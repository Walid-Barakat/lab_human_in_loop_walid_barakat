# Requirements and completion checklist

| Lab step | Implemented material | Current evidence status |
| --- | --- | --- |
| 1 Space setup | Official-template instructions in space_setup.md | Real deployment and URL pending |
| 2 Programmatic connection | connect(), environment settings and private-Space header | Live connection pending; mocked SDK test only |
| 3 Evaluation data |20 synthetic responses /10 paired energy prompts; optional real generator | Actual provider outputs pending |
| 4 Guidelines | Root annotator_guidelines.md, full cumulative0-7 rubric | Real colleague clarity review and pilot pending |
| 5 Dataset config | Settings/fields/questions/metadata/distribution code and dataset_config.md | Offline SDK configuration tested; remote/UI pending |
| 6 Upload | Stable-ID records, pilot limit, repeated-upload safety and ID verification | Real upload pending |
| 7 Annotation | Evidence-oriented rubric, pilot and UI instructions | Genuine human submissions pending |
| 8 Download | Attributed raw JSON plus normalized CSV; submitted-status filter | Demo fixture export completed; actual Argilla export pending |
| 9 Analyze | Mean/median/min/max, distributions, paired stats, comments, root paragraph | Executed synthetic demo; actual findings pending |

Before actual submission:

- [ ] Use genuine LLM responses and retain original provider/run provenance.
- [ ] Have a colleague review guidelines, record feedback and resolve pilot disagreements.
- [ ] Deploy Space, record actual URL and persistence settings, connect successfully.
- [ ] Create/configure dataset and verify fields/questions/guidelines in the UI.
- [ ] Upload1-2 pilot records, annotate and export, then full dataset.
- [ ] Collect genuine complete submitted human ratings for all records or a declared representative sample.
- [ ] Export actual responses, retain annotator identity/status/comments and document all filters/exclusions.
- [ ] Review scores, matched-prompt comparisons, uncertain cases and comments; avoid a broad model-ranking claim from a tiny sample.
- [ ] Rewrite the root one-paragraph summary around actual metrics, actual failure themes, and next improvement.
- [ ] Ensure root annotated_dataset.csv/JSON are live exports and provenance remains honest.
- [ ] Save permitted UI screenshots under docs/evidence and complete live_evidence.md.
- [ ] Put all required deliverables in a dedicated lab-only GitHub repository and submit its real URL.

## Required files

`annotator_guidelines.md`; `dataset_config.md` or actual configuration screenshot; `annotated_dataset.csv` or `.json`; root `lab_summary.md`; README with overview, dataset structure, annotation approach, file map and public Space URL if appropriate. Optional `reflection.md` included. Folder is `lab_human_in_loop_walid_barakat`.

A downloadable package is not the GitHub submission itself. No Space, reviewer, human ratings, screenshot, or repository URL is invented here.
