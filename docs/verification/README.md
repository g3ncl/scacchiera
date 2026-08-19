# Verification traceability

This directory maps the stable functional specification to executable verification. It covers
requirement identity and test ownership only. Numeric limits and evidence live in
[`../hardware/criteria.yaml`](../hardware/criteria.yaml), while recorded gate status remains in
[`../planning.md`](../planning.md).

`traceability.yaml` contains one atomic entry per current product requirement. Its source hashes
make edits to `docs/functional/` fail the verification test until the mapping is reviewed. Test IDs
name the checks that later V-gates must implement. A mapped ID is not evidence that its test already
exists or passes.

Hashes are taken over line-ending-normalised text, so a digest identifies the reviewed wording
rather than the checkout that produced it. After an approved change to a functional source, update
its digest in the same commit as the requirement review.

V0 maps every fitted component's applicable absolute maximum through
`TEST-V1-ABSOLUTE-MAXIMUM-COVERAGE`. V1 materializes that rule as one evidence record per fitted
part and fails if a BOM item or applicable limit is absent. This keeps V0 responsible for complete
test ownership and V1 responsible for the component proof itself.
