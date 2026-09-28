# AI-Use Transcript

## Tool used

OpenAI Codex desktop agent (GPT-5), used as a drafting and review assistant.

## Important prompt supplied to the tool

> Create the deliverables for Assignment #3: turn the supplied informal stakeholder brief for a LAMBDA browser environment into `MySolution/REQUIREMENTS.md`, including stakeholders/scope, clarification questions and assumptions, approximately 12–20 functional requirements, 3–5 quality requirements, interfaces/dependencies, priorities, acceptance criteria, traceability, and review notes. Also create this AI transcript.

The user also supplied the complete informal brief from the course instructor.

## Significant assistance received

The AI:

- identified students, compiler-modifying students, the instructor, the UI team, and the compiler-interface provider as stakeholders;
- separated the browser environment from the external compiler/interpreter and identified first-version exclusions;
- proposed eight clarification questions and labeled unprovided answers as assumptions or unresolved issues;
- drafted 18 functional requirements and 5 quality requirements with identifiers, priorities, and testable wording;
- proposed acceptance checks including compiler-service failure, non-terminating execution/cancellation, source-version association, and suite continuation after failure;
- created traceability links and reviewed ambiguity around responsiveness, cancellation, test-suite failure handling, artifacts, and persistence.

## How I reviewed and used the output

I reviewed the document against the instructor's brief and assignment checklist. I checked that it does not claim invented stakeholder answers, that it separates compiler work from the UI, that simulated responses are visibly distinct from real compiler results, and that the acceptance criteria describe future checks rather than performed tests. I retained the proposed one-second UI-feedback target only as an explicitly labeled assumption pending stakeholder confirmation. I also verified that the requested files are placed under `MySolution/`.

The author remains responsible for reading the final specification, correcting any interpretation of the brief they disagree with, and disclosing AI use according to course policy.
