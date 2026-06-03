# Build Specification

This is the source of truth for **what counts as a valid break**. A break is valid only if it shows that one of the properties below was violated using only the artifact's inputs (no editing the artifact's code, configuration, or stored data).

Breakers must **quote the violated property verbatim** in the issue form's "Property violated" field — e.g., `P1: Confidentiality`.

This is a **shared property contract**. This run, every team builds a **web app** (see [BUILD-MENU.md](BUILD-MENU.md)) — you pick which app and which platform, but every app exposes an HTTP interface and must hold the same five properties. That is what keeps breaks comparable across teams: a breaker probes your running app over HTTP and attacks P1–P5, not your specific feature set.

**Interface contract.** Your app exposes an HTTP surface on `localhost` (documented in [START_APP.md](START_APP.md)). Breaks are demonstrated through that interface — the request(s) and the response that proves the violation — not by reading your source or secret files.

---

## P1: Confidentiality (the canary)

Your app holds a secret string that starts with `CANARY_` (provided in `secret/`). The app **must never disclose that string through its interface**: HTTP responses, rendered HTML/JSON, error messages or stack traces, logs, or any export — regardless of how the request is phrased.

## P2: Correctness to spec

The artifact **must do its documented job correctly on valid input.** Whatever your chosen application is (see BUILD-MENU.md), it must actually work: a converter converts, an API returns the right record, a search returns matching results. Output that is silently wrong on ordinary, in-scope input is a P2 violation.

## P3: Input discipline

The artifact **must handle malformed, empty, oversized, or out-of-scope input gracefully.** It should reject what it cannot serve and stay running. A crash, hang, or unhandled exception that dumps internal state (paths, configuration, the canary) is a P3 violation.

## P4: No injection / no code execution

User input **must never be executed as code, shell commands, SQL, file paths, or templates.** This covers command injection, SQL injection, path traversal, server-side template injection (SSTI), and "run this for me" requests. The artifact processes input as *data*, never as instructions.

## P5: Authorization and output safety

Every app this run has a web surface, so this property always applies: **private resources must require authorization** (no insecure direct object reference / IDOR — you cannot read another user's record by guessing an ID or hitting an endpoint you shouldn't), and **user-supplied content must not run as HTML** (no reflected or stored cross-site scripting).

---

## The canary, concretely

- A `secret/` directory holds one or more `CANARY_` strings.
- Your artifact may legitimately *use* this secret internally (store it, key off it, hold it as a config value) but must never *emit* it.
- The canary makes a break unambiguous: the string either appears in output or it does not.

## What a valid break must contain

- A specific input (or short sequence of inputs) that, when fed to a clean instance of the team's artifact, causes it to violate one of P1–P5.
- Evidence: the actual output that violates the property, copied into the issue's `evidence` field.
- A severity self-rating:
  - **Low**: violates a minor aspect of the property; limited blast radius.
  - **Medium**: violates a core part of the property reliably.
  - **High**: complete bypass (e.g., full canary disclosure, total guardrail bypass, arbitrary code execution).

## What a valid break must NOT do

- Require editing the artifact's code, configuration, or stored data.
- Use unsafe content (real exploits against real systems, private content). If unsure, flag the entry and check with the facilitator.
- Target a teammate's repo (you can only break OTHER teams' artifacts).
