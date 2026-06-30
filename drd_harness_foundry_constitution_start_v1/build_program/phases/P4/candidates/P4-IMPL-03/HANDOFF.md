# P4-IMPL-03 Handoff

This candidate implements the P4 release suite runner contract layer.

Review focus:
1. Confirm `suites.py` only builds and validates in-memory suite reports.
2. Confirm suite reports require sha256 report hashes and sha256 input/evidence/output hashes.
3. Confirm golden update requests are blocked for Human Gate and do not rewrite expected outputs.
4. Confirm integration suite coverage includes CLI, adapters, program driver, recovery, Human Gate, lock gate, write scope, and machine-readable command payload shape.
5. Confirm release suite report shape requires evidence hashes but does not publish packages, create release locks, or construct release lock input bundles.
6. Confirm P4-IMPL-04 and P4-IMPL-05 surfaces remain separately gated.

Next action after approval: P4-IMPL-04 packaging, example smoke, and migration coverage implementation requires explicit continuation.
