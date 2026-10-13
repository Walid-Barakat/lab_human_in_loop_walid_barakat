# Genuine inputs

Add evaluation_records.json with the structure shown in ../demo/evaluation_records.json, but preserve genuine LLM output text and truthful data_origin. The optional `python -m src.generate_responses` command creates this file from real API calls with local credentials. It generates no annotations. Its two candidates use different system instructions; identical model IDs compare prompt variants.

Do not upload the synthetic reference_annotation_fixture.json as human responses. Start with fresh records, have actual people annotate in Argilla, then export. To practise UI mechanics only, you may upload the synthetic candidate texts with their original synthetic provenance, but that does not satisfy the genuine-LLM-response prerequisite.
