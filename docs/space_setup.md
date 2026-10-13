# Set up the real Argilla Space

No Hugging Face Space has been deployed by this package. Follow the official deployment template linked from [Argilla quickstart](https://docs.argilla.io/latest/getting_started/quickstart/), rather than guessing a Dockerfile, port, server image, default password or Space URL.

1. Sign in to your Hugging Face account. Use the Argilla deploy button/template; choose your owner, Space name and visibility. Retain the supported Docker/OAuth configuration supplied by that template.
2. Wait for the build and verify the running UI. If it fails, inspect build logs and confirm server/client compatibility. This package tests the Argilla2.8 Python SDK offline; it does not verify your remote server version.
3. Sign in to Argilla, confirm owner/admin access and the available workspace. Retrieve the API key from **My Settings**. Use the actual direct `https://...hf.space` endpoint, not merely the Hub's `huggingface.co/spaces/...` page.
4. Put endpoint/key into local `.env`. Private Space requests also need an HF token in an Authorization header, as documented by Argilla. Scripts read it locally and do not print it.
5. Verify persistence before important annotations. The lab and older Argilla guidance mention “Small” persistent storage; current Hugging Face documentation describes attached Storage Bucket volumes. Use the persistence option supported by your actual template/account and ensure the database/data paths are on durable storage. These names should not be assumed interchangeable. If using ephemeral storage for a short trial, export immediately and keep local backups before restarts or settings changes. Private visibility alone does not make storage durable. Do not purchase a storage tier automatically.
6. Run `python -m src.workflow connect`, create the dataset, upload2 records and inspect the UI. Confirm guidelines, fields, questions, metadata, required answers and completion behavior.
7. Submit a genuine pilot annotation, export it and reconcile score values, comment, user ID and status before scaling to all records.
8. Record actual URL, deployment state, persistence configuration, tested server/SDK versions and evidence in `docs/live_evidence.md`. Add the public URL to README only if sharing it is appropriate.

Sources checked10 October2026: [Argilla quickstart](https://docs.argilla.io/latest/getting_started/quickstart/), [Spaces configuration](https://docs.argilla.io/latest/getting_started/how-to-configure-argilla-on-huggingface/), [Hugging Face storage](https://huggingface.co/docs/hub/spaces-storage).
