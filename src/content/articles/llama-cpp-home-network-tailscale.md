---
title: "Serving llama.cpp Across My Home Network and Tailscale"
description: "Building llama.cpp on Fedora with Vulkan, then sharing a 27B model with friends and other machines across my home network and Tailscale."
date: "2026-09-06"
category: "AI Engineering"
tags: ["llama.cpp", "local-llm", "tailscale", "inference", "self-hosting"]
slug: "llama-cpp-home-network-tailscale"
draft: false
featured: false
readTime: "12 min read"
---

I recently set up [llama.cpp](https://github.com/ggml-org/llama.cpp) on an NVIDIA
GeForce RTX 5090, serving a Qwen3.8 27B GGUF on the machine itself, across my home
LAN, and through Tailscale. I’m now sharing inference with friends and using it
from my other machines, including outside my home network. They can point their
scripts and coding tools at the same OpenAI-compatible endpoint while my desktop
does the inference, without needing their own GPU or a local copy of the model.

Getting it built on Fedora took a detour through compiler compatibility first.
Once it was running, I worked through sharing one GPU, keeping client
configuration stable, and checking access from the machines that would use it.

## Compile for the Fedora toolchain you actually have

My first plan was to build llama.cpp with CUDA. That was also what the old
automation I brought to this machine expected. The new host was Fedora 44,
though, and its default compiler was GCC 16.2.1. CUDA 12.9 found the toolkit and
then stopped during compiler identification because that release supports host
GCC only through version 14. NVIDIA documents the supported compiler range in
its [CUDA 12.9 Linux guide](https://docs.nvidia.com/cuda/archive/12.9.2/cuda-installation-guide-linux/index.html).

I tried the shorter escape routes before changing backends. Allowing an
unsupported compiler still did not give me a working build. Using Clang 18 as
the CUDA host compiler got farther, then failed on incompatible math-function
declarations between the CUDA headers and Fedora's glibc 2.43 headers. I could
have introduced and maintained another supported compiler environment. I chose
Vulkan instead. The performance tradeoff was acceptable to me compared with
maintaining a separate compiler setup alongside Fedora’s defaults. This is my maintenance
decision for this machine, not a CUDA-versus-Vulkan benchmark.

### Build and check the Vulkan backend

This recipe assumes the NVIDIA driver is already installed and working. Start
with `nvidia-smi`; if it cannot see the card, fix the driver before compiling
llama.cpp. Install the build dependencies and `vulkan-tools` for a separate
Vulkan device check:

```bash
sudo dnf install -y \
  git cmake make gcc-c++ \
  vulkan-loader-devel vulkan-headers glslc spirv-headers-devel \
  vulkan-tools
```

I pin the source revision here because a build from a moving `master` branch is
hard to reproduce. The `/srv/` paths below are examples. Use a new source
directory so an older CMake cache does not carry settings into this build:

```bash
sudo install -d -o "$(id -un)" -g "$(id -gn)" /srv/llama.cpp
git clone https://github.com/ggml-org/llama.cpp.git /srv/llama.cpp
git -C /srv/llama.cpp checkout 95ef7fc16054e63b427a3ef00188e055ef7586d8

cd /srv/llama.cpp
vulkaninfo --summary
cmake -S . -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_VULKAN=ON \
  -DGGML_CUDA=OFF
cmake --build build -j"$(nproc)"

./build/bin/llama-server --version
./build/bin/llama-server --list-devices
```

The last command matters on this desktop because Vulkan sees both the RTX 5090
and the integrated AMD GPU. A successful build proves that the backend exists;
the device list and startup log show which hardware the server can actually use.
The upstream [Vulkan build instructions](https://github.com/ggml-org/llama.cpp/blob/95ef7fc16054e63b427a3ef00188e055ef7586d8/docs/build.md#vulkan)
describe the same CMake backend and the SPIR-V header requirement.

### Run locally before sharing it

Download a GGUF from the model repository linked in the next section, then
replace the example model path below with that file. Pick the device ID that
`--list-devices` reports for your intended GPU. On my machine, that is `Vulkan0`.
For a first run, bind to loopback with a small context:

```bash
./build/bin/llama-server \
  --model /srv/models/active-model.gguf \
  --alias home-model \
  --host 127.0.0.1 \
  --port 8080 \
  --device Vulkan0 \
  --n-gpu-layers 99 \
  --ctx-size 4096
```

From another terminal, `curl --fail http://127.0.0.1:8080/health` checks that
the model finished loading and the HTTP server is ready. Check the startup log
for GPU offload as well as the selected device. Stop the foreground process with Ctrl+C when finished. This first run has no API key and
only accepts local connections. Before changing the bind address for sharing,
add the key-file configuration and network controls described below.

A missing `glslc` or SPIR-V header error is a build dependency problem. A server
that starts but selects the wrong GPU is a device-selection problem. Checking
those here makes the later service and network setup easier to diagnose.

### For those braver than me

There is still some compiler wizardry to try if you want CUDA on this Fedora
setup. Start by matching the toolkit’s supported compiler and OS versions:

- Keep a compatible GCC alongside Fedora’s default, or build in an isolated
  environment with a matching toolchain and headers. Point CMake’s
  `CMAKE_CUDA_HOST_COMPILER` at the supported compiler, using a fresh build
  directory so the old compiler choice is not cached.
- Try a supported Clang version, then resolve any CUDA/glibc header conflicts.
  My Clang attempt reached those conflicts; a different compiler alone was not
  enough. Header patches or compatibility shims would become another thing to
  maintain when packages update.
- Move to a host/toolkit combination that already agrees on the compiler.
  Downgrading the system GCC itself has a much wider impact than selecting a
  compiler just for this build.

Bypassing NVCC’s version gate with `-allow-unsupported-compiler` is also possible,
but that attempt failed here. It removes a check, not the incompatibility. I have
not validated a working CUDA workaround for this installation.

For me, that was too much wizardry to carry on a personal gaming PC. Vulkan let
me get on with running the model and sharing tokens with friends.

## Fit the context and concurrency to one GPU

The active model is a Qwen3.8 27B `UD-Q4_K_M` GGUF of about 16.5 GB. The official
[Qwen3.8-27B model card](https://huggingface.co/Qwen/Qwen3.8-27B) describes a 27B
model with a native 262,144-token context, while the selected quantized variant is
distributed for llama.cpp in the
[Unsloth GGUF repository](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF).
Quantization makes the weights a practical fit on a 32 GB card, but the model file
is only part of the memory budget. The KV cache, runtime buffers, and concurrent
sequences need room too.

My current service configuration asks for a 262,144-token server context, two
parallel slots, a unified KV buffer, and Q8_0 K and V caches. It also enables flash
attention and GPU offload through Vulkan. This is an adapted version of the
relevant command. The paths, alias, and credentials are examples rather than my
real values:

```bash
/srv/llama.cpp/build/bin/llama-server \
  --model /srv/models/active-model.gguf \
  --alias home-model \
  --host 0.0.0.0 \
  --port 8080 \
  --api-key-file /srv/llama-server/api-keys \
  --n-gpu-layers 99 \
  --ctx-size 262144 \
  --parallel 2 \
  --kv-unified \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --flash-attn on \
  --metrics
```

Those numbers need to be read together. In llama-server, `--parallel 2` creates
two slots for parallel inference sequences. The unified KV option gives those
sequences one shared cache allocation. It does not create two independent
262,144-token promises. A very long request can consume capacity that a second
request would otherwise use. The llama.cpp
[server documentation](https://github.com/ggml-org/llama.cpp/blob/95ef7fc16054e63b427a3ef00188e055ef7586d8/tools/server/README.md)
defines the flags, and its
[server design notes](https://github.com/ggml-org/llama.cpp/blob/95ef7fc16054e63b427a3ef00188e055ef7586d8/tools/server/README-dev.md)
describe slots as parallel sequences contributing work to a shared batch.

Q8 KV caches reduce cache memory compared with full-precision caches, at the cost
of some precision. Two slots accept limited overlap between clients, but they do
not promise twice the throughput. A native context limit also does not promise
uniform answer quality at every prompt length. I treat the context size as a
capacity ceiling and the slot count as an admission decision, not as a benchmark.

## Give clients a stable name, and keep the real identity somewhere else

llama-server's OpenAI-compatible API let me reuse clients that already know how
to call Chat Completions. Its `--alias` option gives the loaded model a stable ID,
so the client-side shape stays small:

```text
base URL: http://<MODEL_HOST>:8080/v1
API key:  <API_KEY>
model:    home-model
```

Only `<MODEL_HOST>` changes between loopback, a LAN address, and a Tailscale
address. The model ID can stay the same when an active-model symlink selects a
different GGUF and the service restarts. That keeps scripts, editor extensions,
and terminal agents from embedding model filenames in every configuration file.

There is a cost. The same abstraction that prevents configuration churn also
hides the concrete artifact. With an alias configured, `/v1/models` reports the
alias and model metadata rather than the selected GGUF path. That is convenient
for daily interactive use and insufficient for a repeatable evaluation. A test
harness should record a versioned alias, artifact digest, or separate deployment
manifest if the exact weights and quantization matter. My current endpoint proves
which API identity answered; it does not provide that stronger provenance by
itself.

Compatibility also needs testing at the behavior level. llama.cpp describes its
server as OpenAI-compatible, but its documentation does not claim complete
equivalence with every OpenAI API feature. A client that can list a model may
still disagree about chat templates, reasoning fields, streaming events, or tool
calls.

## Use three routes without confusing their protections

The server listens on all interfaces so one process can accept local, LAN, and
Tailscale traffic. A reachable non-loopback bind is necessary for remote clients;
the wildcard bind is one way to cover both the physical and overlay interfaces.
It is not an access policy.

On my home network, firewalld admits the serving port through the active
workstation zone. Away from home, a Tailscale client reaches the same port through
the host's tailnet address. This path uses neither Tailscale Serve nor Funnel and
does not require router port forwarding. Funnel is specifically for exposing a
local resource to the broader internet, according to the
[Tailscale documentation](https://tailscale.com/docs/features/tailscale-funnel),
which is a different exposure decision from private tailnet access.

The layers answer different questions:

| Layer | Question it answers |
| --- | --- |
| llama-server bind | Which host interfaces can deliver a request to the process? |
| Host firewall or tailnet policy | Which network sources can reach TCP port 8080? |
| Tailscale | How do approved devices route and encrypt traffic across networks? |
| llama-server API key | May this HTTP request use the model API? |

The API key does not make the port private. Tailscale membership does not make an
HTTP request valid. Tailscale encrypts its device-to-device traffic end to end
with WireGuard, for both direct and relayed connections, as its
[encryption documentation](https://tailscale.com/docs/concepts/tailscale-encryption)
explains. A direct `http://` request over the ordinary home LAN does not gain that
overlay encryption. That distinction matters if the LAN contains devices I do
not fully trust: I should route through Tailscale or add TLS rather than assuming
an API key protects prompts or the credential itself in transit.

For sharing with friends, I restrict Tailscale access to the inference server's
TCP port, 8080. That lets them use the model API without opening access to other
services on the machine. Tailscale's
[grants](https://tailscale.com/docs/features/access-control/grants) support this
port-level restriction, while
[machine sharing](https://tailscale.com/docs/features/sharing) makes an individual
machine available without exposing the rest of the owner's tailnet. The model
API still requires its own key.

## Make “off” part of the service contract

This inference host is also a desktop with other uses for the GPU. I run
llama-server through systemd, enabled at boot with `Restart=on-failure`. A crash
triggers a retry after a short delay. A deliberate stop stays stopped.

A small desktop toggle uses that distinction to switch between inference and
gaming: it stops llama-server to release GPU capacity, then starts it again when
the model should be available. A model-switch command updates the active-model
symlink and restarts the service only if it was already running.

The practical consequence is that unavailability is sometimes intentional.
Clients should report connection refusal or a temporarily unavailable server as
a service state, not silently fall back to a different model. After a model switch,
health may return only after the new weights and context are loaded. A stable
alias removes client reconfiguration, but it should not erase the fact that the
backend changed.

## Verify the path in the order it can fail

The verification sequence follows the request from the service process through
the client workflow:

1. `systemctl is-active llama-server` proves the service manager sees a running
   process.
2. `GET /health` proves the HTTP server is ready. In my current build, this route
   returns 200 without an API key, which makes it suitable for a narrow health
   probe.
3. `GET /v1/models` without a key should fail. My endpoint returned 401. The same
   request with a key should return the configured alias and model metadata.
4. A small Chat Completions request proves that inference finishes, rather than
   only that metadata loaded.
5. From a remote client, `tailscale ping <MODEL_HOST>` checks peer reachability.
   It does not prove that the serving port is admitted, so an authenticated HTTP
   request must follow.
6. For an agent client, require one harmless tool-call round trip. A normal text
   response can succeed even when the model's chat template and the harness
   disagree about tool-call syntax.

The local checks passed on September 6, 2026: the service was healthy,
unauthenticated model discovery was rejected, authenticated discovery succeeded,
and a short inference returned the requested marker. A separate client validation
record from the previous day captured authenticated discovery, a streamed response,
and a complete Pi tool call over Tailscale. I did not repeat that remote test or
run a load test while preparing this article, so these results say nothing about
latency, throughput, or behavior under two long concurrent prompts.

The setup now has a modest, useful contract. Clients know one API shape and one
stable model name. The host can deliberately give the GPU back to other work.
Local and remote routes reuse the same inference process while applying different
network protections. The checks stop at the boundary they actually prove. That
makes a workstation-hosted model easier to use without
mistaking it for an always-on managed service.
