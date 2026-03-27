# Manual Patch Manifest

Purpose: explicit protected patch layer loaded by stage 05 after generated artifacts.

Current status:
- No patch triples moved yet.
- Stage 05 is being prepared to load manual patches safely.

Planned migrations:
- paper_01 hasSubTask additions
- paper_07 hasSubTask additions
- paper_11 hasSubTask additions
- any non-reproducible external link additions, if needed



- paper_01
  - patch file: output/manual_patches/instances/paper_01_subtasks_patch.ttl
  - migrated from: output/instances/paper_01.ttl
  - kept in base file: parent task node (Veracity Prediction) and its own base semantics
  - moved to patch layer: hasSubTask + subtask nodes
  - validation after migration: merged graph unchanged (3839), SHACL conforms


- paper_07
  - patch file: output/manual_patches/instances/paper_07_subtasks_patch.ttl
  - migrated from: output/instances/paper_07.ttl
  - kept in base file: parent task node (RiskAssessment) and its base semantics
  - moved to patch layer: hasSubTask + subtask nodes
  - validation after migration: merged graph unchanged (3839), SHACL conforms