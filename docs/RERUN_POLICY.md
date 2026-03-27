## Provenance and rerun policy

| Artifact | Current status | Rerun policy | Rationale |
|---|---|---|---|
| `paper_01.ttl` | subtask decomposition migrated to patch layer | do **not** full-rerun `03` unless patches are retained | JSON was not updated to reproduce this decomposition automatically |
| `paper_07.ttl` | subtask decomposition migrated to patch layer | do **not** full-rerun `03` unless patches are retained | same reason |
| `paper_11.ttl` | subtask decomposition migrated to patch layer | do **not** full-rerun `03` unless patches are retained | same reason |
| `paper_09.json` + `paper_09.ttl` | synchronized correction | selective rerun of `03` is allowed | correction exists in both JSON and TTL |
| `external_links.ttl` + `src/expanded_concept_mappings.py` | hybrid checked state | rerun `04` only where mappings reproduce the links | DOI links were mirrored in mappings, but external linking remains partly heuristic |

## Decision rule for fixes

- If the issue is only in merged output, fix the checked artifact or downstream stage.
- If the issue should survive rerun from extraction outputs, fix JSON and then selectively rerun `03`.
- If the issue is in external-linking logic, fix mappings/code and rerun `04` only if reproducible there.
- Preferred safe validation path: `05 → 10 → 07 → 08`.