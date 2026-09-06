---
title: "How to Trace an Agent That Can Crash or Be Killed"
description: "The supervisor must own trace identity, timeouts, and final status because the agent may never get a chance to report how it stopped."
date: "2026-09-06"
category: "AI Engineering"
tags: ["observability", "opentelemetry", "agents", "reliability"]
slug: "reconstructing-agent-traces"
draft: false
featured: false
readTime: "6 min read"
---

The trace operators need most is often the one the agent cannot finish. A process can time out, ignore cancellation, exhaust memory, lose its collector, or be killed before its exporter flushes. If the agent owns the only account of its lifecycle, the failure also destroys the information needed to explain it.

That failure mode determines the design. The supervisor creates the run, starts the child, watches its process, and remains alive when the child stops responding. It must own the outer span and final status. The child fills in the interesting work inside that boundary when it can.

I maintain the public [agentic-ci](https://github.com/opendatahub-io/agentic-ci) project, where this model has a concrete implementation. The architectural argument is broader than that codebase: start with the failure modes, assign ownership to the longest-lived observer, and make every inferred fact distinguishable from every observed one.

## Start with the record you need after failure

Before choosing spans or exporters, define the minimum record for every attempted run:

```text
attempt identity
requested operation and sanitized inputs
supervisor start and stop observations
termination reason
child telemetry received, if any
telemetry completion state
```

While it survives, the supervisor can guarantee the first four because it creates and monitors the process. The child may supply model calls, tool executions, token counts, and intermediate decisions. Those details are valuable, but they cannot be required for the attempt record to exist.

This gives the supervisor ownership of the outer lifecycle. Before launch, it creates an attempt ID and tracing context. The W3C [Trace Context specification](https://www.w3.org/TR/trace-context/) defines the portable `traceparent` fields used to carry a trace ID and parent ID across process boundaries. A cooperating child can join that trace. If the child emits nothing, the supervisor still has an identity under which to record the attempt.

One public example is [agentic-ci #235](https://github.com/opendatahub-io/agentic-ci/pull/235), which places root-span creation and finalization in the orchestrator and passes trace context into the agent environment. That implementation is evidence that the ownership model can be applied. It is not evidence that all agents, exporters, and termination paths will behave the same way, so the design still needs explicit handling for disagreement and loss.

## Use two clocks for two questions

Tracing backends want wall-clock timestamps so events from different systems can be correlated. Supervisors need monotonic time so a clock correction does not produce a negative or implausible process duration.

Record both at launch:

```text
started_at_wall = UTC timestamp for correlation
started_at_mono = monotonic counter for duration
```

At termination, calculate duration from the monotonic counter. Record the observed wall-clock stop separately. If the two disagree because the system clock moved, preserve the discrepancy instead of adjusting the evidence until it looks tidy.

Child event timestamps introduce another boundary. They may come from a container, virtual machine, or remote sandbox with a different clock. Their order within one emitter can be useful, but the supervisor should not claim a precise global order that the clocks cannot establish. Causal identifiers and local sequence numbers are stronger evidence than close wall-clock values.

## Define completion as a protocol

Several events can look like completion:

- the child emits a final answer
- the child process exits
- the child exporter reports a flush
- the collector receives its last local record
- the backend makes the trace queryable

They are not interchangeable. A final answer can precede tool cleanup. Process exit can precede collector forwarding. Export success can precede backend indexing.

The supervisor therefore needs a completion protocol, not a sleep. A practical sequence is:

```text
1. Observe the child reach a terminal process state.
2. Stop accepting new work for that attempt.
3. Allow a bounded drain period for local telemetry.
4. Snapshot the evidence received by the deadline.
5. Finalize the supervisor-owned lifecycle record.
6. Report backend export separately.
```

The drain has a deadline because telemetry is secondary to the requested work. Waiting forever for a missing span turns an observability defect into a stuck job. Closing at the deadline does not mean the trace is complete. It means the supervisor has completed its record and classified the remaining gap.

## Treat cancellation as an observable state machine

“Timed out” is too vague for a system that can escalate termination. A cancellation path can contain at least three distinct facts:

```text
cancel requested -> graceful deadline reached -> forced termination observed
```

The child might stop after the request, during the grace period, or only after a hard kill. Record which transition occurred and which actor initiated it. Preserve the last exit status or signal the supervisor actually observed. Do not translate every nonzero outcome into the same generic error.

This matters for both diagnosis and policy. A tool blocked in I/O, an agent that rejected cancellation, and a collector that delayed shutdown may all appear as a timeout from outside. Their remediation is different. The state transitions retain that distinction without requiring the dead process to explain itself.

## Reconstruct identity conservatively

Preallocating context handles cooperative children. It does not prove that every span received by the collector belongs under the expected root. A harness may start its own root, reuse stale environment state, or emit children that refer to a parent the supervisor never saw.

Reconstruction should follow a strict evidence order:

1. Accept valid trace and parent identifiers carried through the launch context.
2. Preserve valid identifiers present in received records.
3. If several records point to one missing parent, report that dangling reference as observed evidence.
4. If identities conflict, keep the groups separate or link them to the attempt rather than rewriting them into a plausible tree.
5. If no child telemetry exists, create only the supervisor lifecycle record.

A synthetic root can say, “this attempt existed and ended this way.” It cannot say that an unobserved model call occurred, that a tool completed, or that the task succeeded. A neat tree is less valuable than an honest partial trace.

## Keep raw evidence and derived views separate

If recovery depends on querying the final backend, a network failure removes both the telemetry and the means of repair. A local append-only spool gives the supervisor a smaller trust boundary. It can retain valid OTLP records, rejected lines, receipt time, and export acknowledgements until retention policy permits cleanup.

The reconstructed trace is then a derived view over that evidence. It should carry provenance such as `observed`, `supervisor_generated`, or `inferred_missing_parent`. Malformed records should be quarantined rather than allowed to abort finalization. Export retries should be idempotent so recovery does not create duplicate attempt records.

Most of all, keep the primary and telemetry outcomes on separate axes:

```text
task:       succeeded | failed | timed_out | cancelled
telemetry:  complete | reconstructed | partial | export_failed
```

A successful task with partial telemetry remains successful. A failed task with a complete reconstructed envelope remains failed. Cleanup and export errors belong beside the primary result, never in place of it.

This architecture does not promise a perfect trace after arbitrary failure. It aims to preserve an attempt identity and an outer lifecycle while the supervisor survives, measure durations with the right clock, record cancellation transitions, and expose the boundary between received evidence and reconstruction. Stronger durability would require a defined persistence and recovery protocol. That gives operators a useful record even when the child cannot report its own outcome.
