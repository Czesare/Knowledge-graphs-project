# Manual Patch Manifest

Purpose: explicit protected patch layer loaded after generated artifacts.

## Migrated instance patches

- paper_01
  - patch file: output/manual_patches/instances/paper_01_subtasks_patch.ttl
  - migrated from: output/instances/paper_01.ttl
  - kept in base file: parent task node and its own base semantics
  - moved to patch layer: hi:hasSubTask + moved subtask nodes
  - validation after migration: merged graph unchanged (3839), SHACL conforms

- paper_07
  - patch file: output/manual_patches/instances/paper_07_subtasks_patch.ttl
  - migrated from: output/instances/paper_07.ttl
  - kept in base file: parent task node and its own base semantics
  - moved to patch layer: hi:hasSubTask + moved subtask nodes
  - validation after migration: merged graph unchanged (3839), SHACL conforms

- paper_11
  - patch file: output/manual_patches/instances/paper_11_subtasks_patch.ttl
  - migrated from: output/instances/paper_11.ttl
  - kept in base file: parent task node and its own base semantics
  - moved to patch layer: hi:hasSubTask + moved subtask nodes
  - validation after migration: merged graph unchanged (3839), SHACL conforms

## Remaining special cases

- paper_09
  - requiresCapability alignment corrected in both output/json/paper_09.json and output/      instances/paper_09.ttl
  - no patch layer currently needed

- DOI external links
  - originally added directly to output/external_links.ttl
  - README says they were also mirrored into mapping logic for persistence across stage-04 reruns