# Verification record

Executed10 October2026.

- All16 offline tests passed; captured output in test_results.txt. Includes real SDK settings under mocked HTTP and real SDK Response serialization. No production Argilla endpoint was contacted.
- Offline workflow generated20 authored candidate answers for10 paired prompts and20 synthetic reference score rows. It made zero provider or server calls.
- Component scores reconcile exactly to totals0-7; record/candidate statistics and10 matched prompt pairs reconcile to the same20 records. Mean4.25, median5, range0-7; A wins5, B wins5, mean A-B=-0.30.
- Draft/incomplete/invalid responses, duplicate user-question entries, suggestion separation, stable upload reuse and record weighting are covered by tests.
- All eight notebook code cells executed sequentially in a shared Python process with captured stream/table outputs; nbformat validation passed. A native Jupyter kernel could not run in this session because the environment blocks its required sockets. Native kernel startup is not claimed.
- PDF has six pages; each was rendered and visually reviewed for wrapping, clipping and chart/table readability.
- HTML JavaScript syntax/filter behavior and text escaping checked with a simulated DOM; no native browser visual check was performed.
- No candidate code was executed during guideline/reference-score authoring. Static reference reasoning is distinct from runtime verification.
- Space deployment, genuine provider outputs, colleague review, real human annotation/export and GitHub publication remain pending. No human/model ranking or reliability claim is made.

## Tested versions

Python 3.12.14

- argilla 2.8.0
- pandas 2.2.3
- python-dotenv 1.2.4
- httpx 0.28.1
- openai 3.28.0
- nbformat 5.11.1
- matplotlib 3.10.8
- reportlab 4.4.9
