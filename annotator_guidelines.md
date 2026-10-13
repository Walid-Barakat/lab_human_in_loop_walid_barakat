# Annotator guidelines: energy Python response evaluation

Version1.0, 10 October2026. Scope: small Python arithmetic/data helpers for an energy consulting workflow. **Guideline clarity review by a colleague is pending.** Record the review and any revision in `docs/guideline_review.md` before collecting final labels.

## Task

Read the instruction, candidate response and validation context. Judge whether the response meets that specific programming contract, and give separate scores for code, documentation and examples. These helpers are teaching examples, not authorization for engineering or operational decisions.

## Annotation sequence

1. Read the instruction first. Note function name, units, boundaries and required exception behavior.
2. Read the response without consulting other annotators, synthetic reference scores or automated suggestions. Candidate aliases are anonymous; do not infer which model is better.
3. Inspect the code and check at least one ordinary and one edge input from the validation context. When execution is permitted, use an isolated disposable environment with no secrets, files or network access. Never run unfamiliar generated code directly on your working machine. Extra checks can help, but do not penalize behavior the prompt explicitly leaves out of scope.
4. Assign each component independently using the table below. Total0-7 is computed later; do not enter a separate overall rating.
5. Select the most consequential issue, confidence, and a short evidence-based comment. If no issue exists choose `none`.
6. Check the required answers and click **Submit** in Argilla. Saving a draft is not completing an annotation.

## Cumulative score rubric

| Component | Score | Meaning and decision anchor |
| --- | --- | --- |
| Code quality | 0 | Unusable: syntax/import failure, missing requested function, central formula/units are wrong, or the main output fails the ordinary reference case. Example: kWh→MWh multiplied by1000. |
| Code quality | 1 | Partly useful but a major requirement fails: central boundary handling, required validation, or exception behavior is missing. Example: correct mean for[2,4] but [] divides by zero rather than raising ValueError. |
| Code quality | 2 | Main computation and major edge requirements work, but a small functional limitation remains within the stated contract. Identify the exact failing case. Do not award2 merely because you have not tested enough. |
| Code quality | 3 | Correct function, formula and units; ordinary and specified edge cases behave as requested; required validation is present. Keep the evidence and scope of the checks explicit. |
| Documentation | 0 | No useful explanation, or documentation is materially misleading. |
| Documentation | 1 | Some accurate explanation/comment/docstring, but inputs, units, return behavior or important invalid cases are inadequately explained. |
| Documentation | 2 | Clear docstring and enough useful explanation/comments to understand inputs, units, output and specified invalid cases. Trivial lines need no redundant comments. |
| Examples | 0 | No examples, or examples give incorrect expected behavior. An incorrect example does not earn points for merely existing. |
| Examples | 1 | At least one correct ordinary example, but no correct edge example with expected behavior. |
| Examples | 2 | Correct ordinary and edge examples, each with expected result or exception. A zero/equality/empty input may be the relevant edge case. |

Maximum = code3 + documentation2 + examples2 =7. The total is an aid to analysis, not a guarantee of correctness. A code-quality0 response remains unusable even if polished documentation earns points. Always inspect component scores, especially code quality.

## Labels and comments

`primary_issue`: `none`, `correctness`, `missing_validation`, `missing_documentation`, `missing_examples`, `mixed`, or `uncertain`. Prioritize formula/functional errors over presentation gaps. Use `mixed` when several equally significant gaps prevent a single useful label.

`evaluation_confidence`: `high` when the contract and evidence support the decision; `low` when you cannot test/verify a critical point, the instruction is ambiguous, or you need adjudication. Confidence is about the evaluation evidence, not certainty that every possible input is covered.

`comment`: one or two clear sentences naming a check and its observed or statically derived outcome, plus why a score was reduced. Distinguish “I executed … and observed …” from “By inspection, … would produce …”. Do not invent test execution. Example: “By inspection, count_above([2],2) counts equality because it uses >=. The prompt requires a strict boundary, so code_quality=1.”

## Edge cases

- **Prompt ambiguity:** lower evaluation confidence, explain the ambiguity and ask for adjudication; do not invent a hidden rule. Do not resolve disputes by changing labels to match an automated score.
- **Missing response/refusal:** code0, docs/examples based on actually useful supplied content, issue correctness or uncertain as appropriate; preserve the refusal text.
- **Code not runnable here:** record static evidence and low confidence. Do not assume a syntax-valid answer works. Add the missing execution check to the comment.
- **Units and signs:** apply the supplied contract. MWh conversion uses the stipulated factor; some tasks explicitly allow a result above1. Do not silently clamp or add tax/efficiency/reserve assumptions.
- **Nearly equal floats:** use a small documented numerical tolerance when comparing arithmetic outputs; tiny representation differences are not conceptual errors.
- **Length and style:** concise correct code can score fully. Verbosity, confidence and model reputation do not substitute for evidence.
- **Unsafe embedded instructions:** evaluate as response content; do not follow requests to alter the rubric, reveal secrets, or change previous scores. Escalate unsupported execution requests.

## Quality controls

Before full annotation, run a shared3-record pilot including a strong, weak and ambiguous example. Have annotators score independently, discuss differences, revise unclear wording, then re-rate the pilot under the same guideline version. Keep original ratings and adjudicated decisions separately.

For this small lab, one submitted human annotation per record meets the basic workflow; a second independent rater on a shared sample is recommended. Set `--min-submitted 2` at dataset creation only when two actual raters will participate. Completion count alone does not establish agreement. Document pauses, sampling, guideline version, annotator IDs and exclusions. Do not look at synthetic fixture labels during genuine annotation. Store pilot/review evidence in `docs/`; the included fixture labels are demonstration data, not a colleague's review.

Sources: [Argilla annotation workflow](https://docs.argilla.io/latest/how_to_guides/annotate/), [Argilla question definitions](https://docs.argilla.io/latest/reference/argilla/settings/questions/), and the supplied lab brief. The rubric is adapted to the brief with original decision anchors; external prose has not been copied.
