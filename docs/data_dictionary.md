# Dataset and export definitions

Input is one JSON object per candidate response, not one object per entire model conversation. Keep20 records for10 paired prompts when using both candidate aliases. Required input fields are defined in README and dataset_config.md.

| Export column | Meaning |
| --- | --- |
| record_id | Stable external response-record ID |
| annotator_id | Argilla user ID; synthetic_reference_fixture in demo is not a real person |
| prompt_id | Key joining answers to the same instruction |
| candidate_alias | Anonymous A/B identity; not evidence of a real model |
| topic | Energy coding task category |
| data_origin | synthetic_authored_demo, openai_generated, or accurately documented source |
| instruction | Complete original task |
| response | Unedited candidate answer |
| validation_context | Supplied expected behavior/cases; not a claim that someone ran tests |
| code_quality | Integer0-3 for functionality/robustness |
| documentation | Integer0-2 for explanation/docstring |
| examples | Integer0-2 for correct ordinary/edge examples |
| primary_issue | Categorical principal issue under the guideline |
| evaluation_confidence | high/low confidence in annotation evidence |
| comment | Rationale; distinguish executed checks from static inspection |
| total_score | Deterministic sum of the three components0-7 |
| annotation_source | synthetic_reference_not_human or argilla_user_response |
| response_status | submitted; only complete submitted groups enter normalized CSV |
| exported_at | Timestamp of raw snapshot; synthetic fixtures use an explicitly fixed demo date |

The raw JSON retains question names, values, per-response status and user IDs. The normalized CSV has one row per record/annotator. Two raters on one record produce two rows; do not mistake annotation rows for independent candidate answers. Excluded responses are in `excluded_responses.csv`.

Record scores average component values across raters on that record. Global/candidate statistics weight those record means equally. Paired comparison joins candidate A/B by prompt ID and includes only complete pairs. Annotation score/issue distributions count annotation rows. Null agreement means no shared multi-rater records, not perfect agreement.
