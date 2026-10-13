# Argilla dataset configuration

**Prepared configuration, not a screenshot of a deployed Space.** No Space URL or remote dataset is verified in this package. This description is the Step5 configuration deliverable; the live dataset must still be created and checked in the UI.

- Dataset: `energy-code-human-evaluation`
- Workspace: `argilla` (change `.env` if your account uses another existing workspace)
- Task: rate energy-themed Python responses using cumulative code/documentation/examples scores.
- Record shape: **20 separate response records across10 paired prompts** in the demo. Each record contains one response. The prompt ID joins candidate A/B for comparison after export.
- Fields: required Markdown-enabled `instruction`, `response`, `validation_context`.
- Questions: all six below required. Guidelines appear in the UI from root `annotator_guidelines.md`.
- Metadata: categorical `prompt_id`, `candidate_alias`, `topic`, `data_origin` for filtering. Real model/provider/run metadata can be retained separately in a private audit file; do not expose model reputation before rating.
- Task distribution: `min_submitted=1` by default; use2 at creation for two real annotators/record. No suggestions are uploaded by default.

| Question | Type | Values |
| --- | --- | --- |
| `code_quality` | RatingQuestion | 0,1,2,3 |
| `documentation` | RatingQuestion | 0,1,2 |
| `examples` | RatingQuestion | 0,1,2 |
| `primary_issue` | LabelQuestion | none, correctness, missing_validation, missing_documentation, missing_examples, mixed, uncertain |
| `evaluation_confidence` | LabelQuestion | high, low |
| `comment` | TextQuestion | Required evidence and rationale |

Total0-7 is computed after export, avoiding disagreement between component scores and an independently entered total. Per-question responses are joined by **record ID and annotator ID**, never by row order. Only complete `submitted` responses enter analysis; drafts, invalid scores and incomplete annotations are audited separately. Model suggestions remain separate from human responses and are never counted as human labels.

`dataset_settings.json` is a reviewable offline description. `src/workflow.py::make_settings` builds real `rg.Settings`, fields, questions, categorical metadata and task distribution using the tested Argilla2.8 SDK. The upload creates `rg.Record` values with stable external IDs through the SDK `id=` parameter, logs them with `dataset.records.log()`, and verifies IDs. Existing records with changed content are rejected rather than overwriting annotations.

UI acceptance: dataset name/workspace visible; all three fields render readable code; all six questions and guideline text present; test1-2 uploads; submit one pilot response; export it and check component values, comment, annotator attribution and `submitted` status before the full dataset.

Sources: [Argilla dataset settings](https://docs.argilla.io/latest/reference/argilla/settings/settings/), [questions](https://docs.argilla.io/latest/reference/argilla/settings/questions/), [records](https://docs.argilla.io/latest/how_to_guides/record/).
