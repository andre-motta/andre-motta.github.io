import type { Lecture } from '../lib/lectures';

// This is a faithful HTML transcription of the visible source deck. The
// original PDF remains the presentation reference; these blocks only change
// the layout for a responsive website.
export const lecture: Lecture = {
  slug: 'ai-agents-in-ci-cd',
  title: 'AI Agents in CI/CD',
  subtitle: 'Security, Robustness, and Productivity',
  event: 'NCSU',
  date: 'September 9, 2026',
  author: 'Andre Lustosa',
  draft: false,
  originalSlideCount: 22,
  articlePath: '/blog/2026/ai-agents-in-ci-cd.html',
  slides: [
    {
      section: '',
      title: 'AI Agents in CI/CD:',
      lead: 'Security, Robustness, and Productivity',
      blocks: [
        { kind: 'text', lines: ['A Deep Dive from Theory to Production', 'Andre Lustosa, PhD', 'Principal Software Engineer | Red Hat | AIPCC Ecosystems'] },
      ],
    },
    {
      section: '',
      title: 'Lecture Outline',
      blocks: [
        {
          kind: 'table',
          headers: [],
          headerless: true,
          rows: [
            ['I.  Foundations', 'Agent architectures, delegation, and the confused deputy'],
            ['II.  Security Theory', 'Injection taxonomy, trust boundaries, containment primitives'],
            ['III. Robustness', 'Non-determinism, convergence, cycle detection, action-space reduction'],
            ['IV. Measurement', 'Productivity quantification, automation bias, human-in-the-loop control'],
            ['V.  Open Problems', 'Formal verification, alignment in CI, research frontiers'],
          ],
        },
      ],
    },
    {
      section: 'I. FOUNDATIONS',
      title: 'Agent Architecture: From Theory to Tool-Use LLMs',
      blocks: [
        {
          kind: 'columns',
          columns: [
            { title: 'Agent Model', items: ['▸ Sense: read files, API responses, CI logs', '▸ Reason: LLM inference (probabilistic)', '▸ Act: write files, run commands, call APIs', '▸ Loop: observe outcome, adjust, repeat'] },
            { title: 'Tool-Use LLM as UTM Analog', items: ['▸ LLM + tools = Turing-complete system', '▸ Tape: filesystem, git repos, APIs', '▸ Head: tool-use function calls', '▸ Control: learned policy (weights), not program', '▸ Halting: not guaranteed (token limits as proxy)'] },
          ],
        },
        { kind: 'text', lines: ['Key distinction from classical AI agents: the reasoning engine is a neural network with no formal guarantees on output correctness.', 'Consequence: you cannot statically determine what an agent will do. All safety must be enforced at the environment boundary.'] },
      ],
    },
    {
      section: 'I. FOUNDATIONS',
      title: 'The “Principal-Agent” Problem in AI Automation',
      blocks: [
        { kind: 'bullets', items: ['▸ Economics: principal delegates to agent with misaligned incentives', '▸ In AI CI/CD: the organization delegates code changes to an LLM agent', "▸ Information asymmetry: agent 'sees' codebase details principal doesn't verify", '▸ Moral hazard: agent may take shortcuts invisible at review time', '▸ Adverse selection: which tasks are suitable for delegation?'] },
        { kind: 'text', lines: ["The classical solution is monitoring + incentives. For LLM agents, monitoring = code review + gates + telemetry. 'Incentives' = prompt engineering + structured output constraints. Neither is complete."] },
      ],
    },
    {
      section: 'I. FOUNDATIONS',
      title: 'The Confused Deputy Revisited',
      blocks: [
        {
          kind: 'columns',
          columns: [
            { title: 'Classic Confused Deputy (1988)', items: ['▸ Program A has authority to write billing file', '▸ User B tricks A into writing user-controlled data', "▸ A acts on B's behalf using A's privileges", '▸ Root cause: ambient authority not scoped to intent'] },
            { title: 'LLM Agent as Confused Deputy', items: ['▸ Agent has git push + API credentials (authority)', '▸ Attacker embeds instructions in a bug ticket (trick)', "▸ Agent executes attacker's intent with org's credentials", '▸ Root cause: identical. Ambient authority + untrusted input'] },
          ],
        },
        { kind: 'text', heading: 'Mitigation: Capability-Based Security', lines: ['Replace ambient authority with explicit capabilities. The agent receives only the permissions it needs for the specific task, scoped by ticket, repo, and time window. This is the theoretical basis for our gate architecture.'] },
      ],
    },
    {
      section: 'II. SECURITY',
      title: 'Injection Attack Taxonomy: Why Prompt Injection is Different',
      blocks: [
        {
          kind: 'table',
          headers: ['Attack Class', 'Mechanism', 'Defense', 'Why It Works'],
          rows: [
            ['SQL Injection', 'Untrusted data interpreted as SQL', 'Parameterized queries', 'Grammar-based separation'],
            ['XSS', 'Untrusted data interpreted as script', 'Output encoding / CSP', 'Context-aware escaping'],
            ['Command Injection', 'Untrusted data interpreted as shell', 'Avoid shell; use execve', 'Argument isolation'],
            ['Prompt Injection', 'Untrusted data interpreted as instruction', '???', 'No grammar to parse'],
          ],
        },
        { kind: 'text', lines: ['Every prior injection class was solved by separating data from code at a syntactic level. Prompt injection cannot be solved this way because natural language has no formal grammar that distinguishes instruction from data.'] },
      ],
    },
    {
      section: 'II. SECURITY',
      title: 'Trust Boundary Analysis',
      lead: 'Formal decomposition: Who provides input? What authority does the agent hold? When is output trusted?',
      blocks: [
        {
          kind: 'columns',
          columns: [
            { title: 'WHO (Identity Layer)', items: ['▸ Trigger author (changelog-verified)', '▸ Comment authors (email-domain filtered)', '▸ External reporters (quarantined)', '▸ The LLM itself (not a trusted source)'] },
            { title: 'WHAT (Authority Layer)', items: ['▸ Git push to specific branches', '▸ MR/PR creation and update', '▸ Issue tracker mutations', '▸ Network egress (sandboxed)'] },
            { title: 'WHEN (Temporal Layer)', items: ['▸ Pre-agent: input filtering', '▸ During: runtime containment', '▸ Post-agent: output validation', '▸ Post-merge: monitoring'] },
          ],
        },
      ],
    },
    {
      section: 'II. SECURITY',
      title: 'Case Study: Defense in Depth in Production',
      blocks: [
        { kind: 'text', lines: ['Case Study: Red Hat Agentic CI gate architecture (production since 2025)'] },
        {
          kind: 'columns',
          columns: [
            { title: 'PRE-AGENT', items: ['▸ Label author: @redhat.com via Jira changelog API', '▸ External reporter gate: quarantine + human review', '▸ Comment filter: only @redhat.com in prompt', '▸ Embargo: JQL excludes EMBARGOED tickets', '▸ AI sensitivity: semantic security-bug detection'] },
            { title: 'POST-AGENT', items: ['▸ Sensitive files: blocks .env, .pem, .key commits', '▸ Secret scan: gitleaks on all commits pre-push', '▸ Commit identity: author matches expected bot', '▸ Visibility: comments restricted to employees', 'e.g: https://opendatahub-io.github.io/agentic-ci/api/gates/'] },
          ],
        },
      ],
    },
    {
      section: 'II. SECURITY',
      title: 'Containment Primitives: Kernel-Level Enforcement',
      blocks: [
        { kind: 'text', heading: 'Landlock (Linux 5.13+)', lines: ['Filesystem access control via LSM. Process declares which paths it can read/write. Inherited by children. No root required.'], callout: 'Restrict agent to workspace directory + read-only deps' },
        { kind: 'text', heading: 'seccomp-bpf', lines: ['System call filtering via BPF programs. Blocks dangerous syscalls (ptrace, mount, kexec). Granular per-process policy.'], callout: 'Prevent container escape and privilege escalation' },
        { kind: 'text', heading: 'Network Namespaces + nftables', lines: ['Per-sandbox network stack with firewall rules. Allowlist-only egress. No ambient network access.'], callout: 'Block exfiltration to attacker-controlled endpoints' },
        { kind: 'text', lines: ['These are kernel-level enforcement mechanisms. The agent cannot bypass them regardless of prompt injection success.'] },
      ],
    },
    {
      section: 'II. SECURITY',
      title: 'Case Study: Sandboxing in Production',
      blocks: [
        { kind: 'text', lines: ['Case Study: OpenShell sandbox in Red Hat Agentic CI'] },
        { kind: 'bullets', items: ['▸ Embedded gateway starts per CI job, no external infrastructure', '▸ Landlock: agent writes only to /workspace, reads only approved paths', '▸ Network: allowlist of endpoints (configurable per-repo via .agentic-ci/openshell-policy.yml)', '▸ Default allowlist: GitHub, GitLab, PyPI, Vertex AI, Anthropic API', '▸ Credentials mounted read-only, never exposed as environment variables in the sandbox', '▸ All other outbound traffic silently dropped (not rejected, to avoid side-channel leaks)'] },
        { kind: 'text', lines: ["Design principle: the sandbox is the security boundary, not the prompt. If you rely on prompt instructions for safety, you've already lost."] },
      ],
    },
    {
      section: 'II. SECURITY',
      title: 'The Oracle Problem: Limits of Output Verification',
      blocks: [
        { kind: 'bullets', items: ["▸ Can you formally verify that LLM output is 'safe'?", "▸ Rice's theorem: any non-trivial semantic property of programs is undecidable", '▸ The generated code IS a program. Verifying its safety is at least as hard as the halting problem.', '▸ Practical implication: you cannot build a gate that provably catches all malicious output', '▸ What you CAN do: reduce the attack surface until the residual risk is manageable'] },
        { kind: 'bullets', heading: 'The Defense Stack (ordered by enforceability)', items: ['▸ 1. Kernel enforcement (Landlock, seccomp, netfilter) - cannot be bypassed by the agent', '▸ 2. Structural validation (gitleaks, file-path checks) - syntactic, decidable', '▸ 3. Semantic analysis (AI-powered review) - probabilistic, best-effort', '▸ 4. Human review - highest quality, lowest throughput'] },
      ],
    },
    {
      section: 'III. ROBUSTNESS',
      title: 'Non-Determinism in Agentic Systems',
      blocks: [
        {
          kind: 'columns',
          columns: [
            { title: 'Sources of Non-Determinism', items: ['▸ Sampling temperature (even at T=0, not deterministic)', '▸ Context window position effects', '▸ Batching and quantization artifacts', '▸ Tool output variance (git diff timing, API responses)', '▸ Prompt sensitivity to minor wording changes'] },
            { title: 'Consequences for CI/CD', items: ['▸ Same bug + same prompt = different patches', '▸ Retry may produce better OR worse results', '▸ Test suite pass is necessary but not sufficient', '▸ Idempotency cannot be assumed', '▸ Statistical reliability, not deterministic correctness'] },
          ],
        },
        { kind: 'bullets', heading: 'Mitigation Strategies', items: ['▸ Structured output schemas: constrain output space to valid shapes', '▸ Verdict-based skill design: agent must declare intent before acting', '▸ Idempotent gate design: gates are safe to re-run on retry', '▸ Monotonic state machines: workflow state can only move forward, never back'] },
      ],
    },
    {
      section: 'III. ROBUSTNESS',
      title: 'Convergence and Divergence in Feedback Loops',
      lead: 'When does a closed-loop agentic system converge to a fixed point?',
      blocks: [
        {
          kind: 'columns',
          columns: [
            { title: 'Convergent Patterns', items: ['▸ Bug fix iteration: review feedback narrows the solution', '▸ Bounded retry with monotonic state', '▸ Human checkpoint breaks infinite loops', '▸ CI pass/fail provides a decidable termination criterion', '▸ Diminishing error surface per iteration'] },
            { title: 'Divergent Patterns', items: ['▸ Self-healing loops without cycle detection', "▸ Agent 'fixes' its own fixes (oscillation)", '▸ Expanding scope: agent adds features while fixing bugs', '▸ Cost explosion: each retry consumes tokens', '▸ Cascading failures across dependent pipelines'] },
          ],
        },
      ],
    },
    {
      section: 'III. ROBUSTNESS',
      title: 'Case Study: Cycle Detection in Self-Healing CI',
      blocks: [
        { kind: 'text', lines: ['Case Study: Pipeline Failure Analyzer-Autofix cycle prevention at Red Hat'] },
        { kind: 'flow', items: ['Autofix Pipeline Fails', 'PFA Analyzes Failure', 'Creates Bug Ticket', 'Autofix Sees New Ticket', 'Would Fix Its Own Failure'] },
        { kind: 'bullets', heading: 'Solution: Label-Based Cycle Prevention', items: ['▸ PFA-created tickets receive no-autofix label at creation time', "▸ Autofix's query excludes tickets with no-autofix label", '▸ Cycle is broken at the state machine level, not by detection heuristics', '▸ Formal property: the label graph is a DAG, not a cycle', '▸ Same pattern applies to any self-referential automation chain'] },
      ],
    },
    {
      section: 'III. ROBUSTNESS',
      title: 'Action Space Reduction via Skills',
      lead: "Skills as structured constraints that reduce the agent's effective action space",
      blocks: [
        {
          kind: 'columns',
          columns: [
            { title: 'Unconstrained Agent', items: ['▸ Action space: all possible tool call sequences', '▸ High variance in output quality', '▸ Harder to review (anything could happen)', '▸ Security surface: entire tool set'] },
            { title: 'Skill-Constrained Agent', items: ['▸ Action space: task-specific instruction set', '▸ Structured verdict: declare intent before acting', '▸ Reviewable: expected behavior is documented', '▸ Security surface: scoped to task requirements'] },
          ],
        },
        { kind: 'text', heading: 'Analogy: type systems for agents', lines: ['Skills function like type signatures: they constrain the space of valid behaviors without dictating implementation. A/B testing of skill variants (our production approach) is analogous to benchmarking type system designs for ergonomics and correctness tradeoffs.'] },
      ],
    },
    {
      section: 'IV. MEASUREMENT',
      title: 'Measuring AI Agent Productivity',
      blocks: [
        {
          kind: 'columns',
          columns: [
            { title: 'Naive Metrics (misleading)', items: ['▸ MRs merged per week (quantity, not quality)', "▸ Lines of code changed (Goodhart's law)", '▸ Time to first MR (ignores review cost)', '▸ Bug close rate (includes false closures)'] },
            { title: 'Better Metrics (still imperfect)', items: ['▸ Review acceptance rate (% merged without revision)', '▸ Engineer time displaced (hours saved per task)', '▸ Defect escape rate (bugs introduced by agent)', '▸ Cost per merged MR (tokens + review time)'] },
          ],
        },
        { kind: 'text', heading: 'The Measurement Paradox', lines: ['If agents handle the easy bugs, engineers handle the hard ones. Average bug resolution time may INCREASE because the easy bugs no longer pull down the average. Productivity improvements are real but invisible in aggregate metrics. You need cohort analysis: compare similar-difficulty tasks with and without agent assistance.'] },
      ],
    },
    {
      section: 'IV. MEASUREMENT',
      title: 'Automation Bias and Over-Reliance',
      blocks: [
        { kind: 'bullets', items: ['▸ Automation bias: tendency to favor suggestions from automated systems', "▸ Particularly dangerous in code review: AI says it's fine, reviewer agrees faster", '▸ Complacency effect increases with perceived agent reliability', "▸ The 'LGTM stamp' risk: human review degrades when agent review exists", '▸ Ironically, better agents may produce worse human review quality'] },
        { kind: 'bullets', heading: 'Countermeasures', items: ['▸ Agent never self-merges: humans must take an explicit action', '▸ AI review complements, does not replace, human review assignment', '▸ Chill mode: suppress low-severity findings to prevent review fatigue', '▸ Defect injection testing: periodically verify human reviewers catch planted bugs'] },
      ],
    },
    {
      section: 'IV. MEASUREMENT',
      title: 'Human-in-the-Loop as Supervisory Control',
      blocks: [
        {
          kind: 'columns',
          columns: [
            { title: 'Control Theory Mapping', items: ['▸ Plant: the codebase + CI pipeline', '▸ Controller: AI agent (non-linear, stochastic)', '▸ Sensor: test suites, linters, gate output', '▸ Actuator: git push, MR creation', '▸ Supervisor: human reviewer (override authority)', '▸ Reference signal: correct, secure, passing code'] },
            { title: 'Why Human Supervision Matters', items: ['▸ The controller is stochastic: identical inputs may produce different outputs', '▸ No Lyapunov function exists for LLM reasoning (stability is not provable)', '▸ Test suites are incomplete sensors (cannot observe all state)', '▸ Human acts as a bounded-rationality supervisor with override authority', '▸ The merge button is a hard gate, not a suggestion'] },
          ],
        },
      ],
    },
    {
      section: 'V. EVIDENCE',
      title: 'Production Evidence at Scale',
      blocks: [
        { kind: 'text', lines: ['Case Study: Red Hat Agentic Ecosystems production data (2025-2026)'] },
        {
          kind: 'stats',
          items: [
            { value: '100+', label: ['MRs merged', 'per week'] },
            { value: '7', label: ['Production', 'workflows'] },
            { value: '15+', label: ['Maintained', 'projects'] },
            { value: '5', label: ['Engineers on', 'the squad'] },
          ],
        },
        { kind: 'text', lines: ['Workflows: Autofix (triage + fix), Code Review, Knowledge Sync, Package Onboarding (CPU/CUDA/ROCm/Gaudi/TPU/Neuron/Spyre), Pipeline Failure Analyzer, RFE Assessor, Security Alerts. Zero security incidents from agent-generated code to date.'] },
      ],
    },
    {
      section: 'V. OPEN PROBLEMS',
      title: 'Open Research Problems',
      blocks: [
        { kind: 'text', heading: 'Formal Verification of Agent Behavior', lines: ['Can we develop tractable verification for bounded agent traces? Partial verification of finite tool-call sequences may be feasible even if general verification is not.'] },
        { kind: 'text', heading: 'Prompt Injection Defenses', lines: ['No complete defense exists. Research directions: instruction hierarchy enforcement, data tainting through attention layers, formal separation of instruction and data channels in transformer architectures.'] },
        { kind: 'text', heading: 'Alignment in CI/CD', lines: ["Agent 'values' are shaped by training data and prompts. How do you align agent behavior with organizational security policies when those policies can't be fully specified in natural language?"] },
        { kind: 'text', heading: 'Optimal Human-Agent Task Allocation', lines: ['Which tasks should be delegated and which kept human? Current allocation is heuristic. We lack formal frameworks for delegation decisions under uncertainty.'] },
      ],
    },
    {
      section: '',
      title: 'Key Takeaways',
      blocks: [
        { kind: 'bullets', items: ['▸ AI agents are confused deputies: ambient authority + untrusted input', '▸ Prompt injection is fundamentally different from prior injection classes', '▸ Kernel-level containment is the only trustworthy security boundary', '▸ Non-determinism requires statistical thinking, not deterministic proofs', '▸ Human-in-the-loop is supervisory control, not a crutch', '▸ The defense stack must be ordered by enforceability, not convenience', '▸ Measure displaced effort, not output volume'] },
      ],
    },
    {
      section: '',
      title: 'Questions?',
      blocks: [
        {
          kind: 'links',
          links: [
            { label: 'linkedin.com/company/red-hat', url: 'https://linkedin.com/company/red-hat' },
            { label: 'youtube.com/@redhat', url: 'https://youtube.com/@redhat' },
            { label: 'Andre Lustosa, PhD | alustosa@redhat.com', url: 'mailto:alustosa@redhat.com' },
            { label: 'https://www.redhat.com/en/products/ai', url: 'https://www.redhat.com/en/products/ai' },
            { label: 'facebook.com/redhat', url: 'https://facebook.com/redhat' },
            { label: 'x.com/RedHat', url: 'https://x.com/RedHat' },
          ],
        },
      ],
    },
  ],
};
