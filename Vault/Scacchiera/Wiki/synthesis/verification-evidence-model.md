---
type: synthesis
date_updated: 2026-07-25
tags:
  - wiki/synthesis
---

# Verification evidence model

[question::How does the project prevent requirements and acceptance limits from drifting away from
tests?] [result::A source-hash guarded requirement manifest and a bidirectionally linked numeric
criteria catalog make traceability executable]

The release workflow now separates three concerns. The functional specification remains the product
authority. `docs/verification/traceability.yaml` assigns each current statement a stable requirement
ID and one or more test IDs. `docs/hardware/criteria.yaml` owns numeric acceptance limits, including
units, conditions, evidence source, and deliberate margin. Automated V0 tests validate all links and
pin the reviewed functional files by SHA-256, so a specification edit cannot silently leave the
verification map stale.

This structure does not treat a planned test ID as passing evidence. Later gates implement and run
those tests. V1 owns the generated fitted-part inventory and absolute-maximum records, V2 through V7
own design and system evidence, V8 owns measurements and model calibration, and V9 owns independent
review and immutable release hashes. See
[[../../../docs/simulation-workflow.md|the simulation and verification workflow]] and
[[../../../docs/verification/README.md|the traceability documentation]].

The first V0 inventory contains 71 atomic functional requirements and 37 numeric criteria. It also
removed a stale 17-pixel WS2812 criterion left behind when the design changed to fourteen
low-current pixels, illustrating why cross-document checks are release evidence rather than
housekeeping.

## Related

- [[overview]]
- [[v1-component-proof]]
- [[tps2553-current-limit-error]]
