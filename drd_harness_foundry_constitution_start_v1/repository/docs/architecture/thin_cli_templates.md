# Thin CLI And Template Boundary

The DRD Harness CLI is a delegation surface. It may parse command arguments, call repository validators or orchestrator helpers, print concise machine-readable results, and return process exit codes.

The CLI must not define product rules, stage semantics, graph algorithms, compiler conservation logic, review approval decisions, promotion decisions, lock decisions, or rule tables. Those responsibilities remain in locked contracts, rule modules, validators, schemas, orchestrators, and Human Gate decisions.

Runtime templates under `repository/templates/` are repository-local promoted artifacts. Templates may describe required fields for operator-facing records, but they do not approve candidates, promote outputs, seal locks, or expand write scope.

Integration tests enforce the boundary through smoke checks and static checks over `repository/src/drd_harness/cli/`.
