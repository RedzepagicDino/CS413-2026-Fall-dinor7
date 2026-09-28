# LAMBDA Browser Environment — Requirements Specification

## 1. Purpose, stakeholders, and scope

### Purpose

The LAMBDA Browser Environment (LBE) is a locally run, browser-based environment for entering LAMBDA source programs, obtaining compilation or execution results through a separately supplied compiler service, and retaining example programs and repeatable tests. It is intended to make ordinary course experimentation and compiler-regression checking more convenient than invoking language tools directly.

### Stakeholders and goals

| Stakeholder | Main goals |
|---|---|
| Course students learning LAMBDA | Start quickly; write or import programs; compile/run them; understand results and errors; preserve work. |
| Students modifying the LAMBDA compiler | Re-run a named suite of expected-result and expected-rejection tests after a compiler change. |
| Course instructor/lecturer | Open prepared examples quickly, alter a copy during a lecture, run it, and explain selected compiler artifacts. |
| LBE development team | Build the interface before the compiler is complete and replace simulated results with the real compiler interface later. |
| Compiler-interface provider | Supply a stable interface and documented response/error formats; compiler development remains its responsibility. |

### System boundary

LBE includes the local browser interface, editable source documents and test collections, browser-local persistence, import of local source files, execution/compilation requests, cancellation requests, and presentation of compiler responses. LBE may use an adapter that converts a compiler-interface response into its own display model.

The LAMBDA compiler/interpreter is an external dependency. It parses, type-checks, compiles, executes, and optionally produces artifacts such as an AST or generated code. Developing the compiler, defining final LAMBDA source notation, and determining language semantics are outside LBE's scope.

### First-version scope and exclusions

The first version includes single-program compile/run, starter examples, local saved work, named tests and suite execution, understandable status/error display, optional inspection of supplied artifacts, and a simulated compiler mode while no real compiler is available. It runs on the user's own computer in a normally used browser.

The following are explicitly outside the first version: public hosting, user accounts, authentication, cloud synchronization, collaborative editing, multi-user simultaneous editing, compiler implementation, a full integrated development environment, and required sharing/import-export of collections. Sharing a collection is a deferred feature because the brief identifies it as useful but not necessary initially.

## 2. Clarification questions, answers, assumptions, and unresolved items

No stakeholder answers beyond the informal brief were available when this specification was written. The assumptions below are working decisions, not stakeholder decisions.

| ID | Clarification question and why it matters | Status / working assumption |
|---|---|---|
| CQ-01 | What concrete protocol, operations, response schema, artifact names, and source-location format will the compiler interface provide? This determines the adapter and what can be displayed. | **Unresolved.** Assume an adapter-facing contract will distinguish compile, run, compiler error, runtime failure, infrastructure failure, cancellation, and optional artifacts. |
| CQ-02 | What is the final LAMBDA source syntax and how should a source file's encoding/extension be handled? This affects editor defaults, examples, and import validation. | **Unresolved.** Accept text files without claiming syntax validation beyond compiler feedback; use UTF-8 when the browser can read it. |
| CQ-03 | Where and for how long should documents/tests persist, and what should happen if browser storage is unavailable or full? This affects the promise that refreshes and later sessions retain work. | **Unresolved.** Use browser-local persistent storage on the same browser/device; notify the user when saving fails. Cross-device persistence is excluded. |
| CQ-04 | Which browsers and versions count as “normally use,” and must the local compiler work without network access? This makes compatibility and setup testable. | **Unresolved.** Support the current stable versions of Chrome, Firefox, Edge, and Safari at release; compiler connectivity may be local or networked as its provider specifies. |
| CQ-05 | What outcomes and equality rules are supported for tests (exact text, integer, Boolean, structured output, output streams)? This determines repeatable comparison. | **Unresolved.** Version 1 supports exact normalized textual comparison for answer tests and compiler rejection for rejection tests; other outcome types await agreement. |
| CQ-06 | What run-time/resource limit should protect against non-terminating programs, and does “stop” guarantee termination? This affects safe cancellation behavior. | **Unresolved.** Users can request cancellation; the UI reports cancellation requested/completed. No automatic timeout or hard-termination guarantee is assumed until the compiler interface supports one. |
| CQ-07 | Which compiler artifacts are useful in teaching, and are they available after compile, run, or both? This prevents a misleading artifact UI. | **Unresolved.** Show only artifacts supplied in a successful response and label each by provider-supplied name. |
| CQ-08 | Does “keep a program” require naming, multiple documents, explicit save, export, or recovery after a crash? This affects the document model. | **Assumption.** A user may create and rename multiple locally persisted documents; edits are automatically persisted after a short debounce. Export/recovery beyond browser persistence is deferred. |

## 3. Functional requirements

Priority: **Must** is required for the first usable version; **Should** is planned if it does not endanger Must work; **Could** is deferred/optional. “Current document version” means the exact source text in the editor when the user starts an operation.

| ID | Priority | Requirement |
|---|---|---|
| FR-01 | Must | The system shall present an editable source area in which a user can enter, paste, and revise LAMBDA source text. |
| FR-02 | Must | The system shall provide a selectable collection of starter examples and shall load a selected example into an editable document without modifying the stored starter example. |
| FR-03 | Must | The system shall allow a user to create, name, reopen, and rename locally stored source documents. |
| FR-04 | Must | The system shall persist changes to a locally stored document in browser-local persistent storage and restore the document after a page refresh or a later session in the same browser/device. If persistence fails, it shall tell the user that work may not be retained. |
| FR-05 | Must | The system shall allow a user to import the text of a user-selected local source file into an editable document and shall not overwrite an existing document without an explicit user action. |
| FR-06 | Must | For the current document version, the system shall provide a **Compile** operation that requests compilation without requesting program execution. |
| FR-07 | Must | For the current document version, the system shall provide a **Run** operation that requests the compiler/interpreter to compile and execute the program. |
| FR-08 | Must | The system shall label every operation result with the document name and the source-version identifier captured when that operation began; later editor changes shall not relabel an earlier result. |
| FR-09 | Must | The system shall distinguish in its displayed status and wording among successful compilation, successful execution, compiler-reported source errors, runtime failures, cancellation, and inability to contact/use the compiler service. |
| FR-10 | Must | When a compiler-reported source error includes a source position in the agreed interface format, the system shall provide a user action that moves focus/selection to the corresponding position in the captured source version; when no usable position is supplied, it shall display the explanation without a false location. |
| FR-11 | Should | The system shall keep optional compiler artifacts (for example AST or generated code) hidden by default and let a user reveal each artifact only when it was supplied by the compiler response. |
| FR-12 | Must | While a compile/run request is outstanding, the system shall show that operation's in-progress state, keep source editing and navigation usable, and offer a Stop action for a running request. |
| FR-13 | Must | When Stop is invoked, the system shall send a cancellation request where the compiler interface supports it, display that cancellation was requested, and later display the terminal cancellation/termination status received. |
| FR-14 | Must | The system shall let a user create, name, revise, and locally persist a collection of named tests, each containing a program and exactly one expected outcome type: expected answer or expected compiler rejection. |
| FR-15 | Must | The system shall run all tests in a selected collection independently and shall continue attempting later tests after an individual test has an unexpected result, compiler-service failure, runtime failure, or cancellation. |
| FR-16 | Must | After a suite run, the system shall display a summary count of passed, failed, and not-completed tests and, for each non-passing test, its name, outcome category, expected outcome, and observed result/diagnostic when available. |
| FR-17 | Must | The system shall provide a clearly identified simulated-compiler mode that returns configured sample responses for demonstrations before a real compiler is connected; every simulated result shall visibly state that it is simulated. |
| FR-18 | Should | The system shall provide setup instructions identifying prerequisites, how to start the local environment, how to select/configure the compiler interface or simulated mode, and how to verify that it is available. |

## 4. Quality requirements

| ID | Priority | Requirement |
|---|---|---|
| QR-01 | Must | Main commands (new/open example, edit, Compile, Run, Stop, create/run collection) shall be operable by keyboard with a visible keyboard-focus indicator. |
| QR-02 | Must | Statuses, pass/fail outcomes, and error categories shall be conveyed by text or an accessible programmatic label in addition to any color. |
| QR-03 | Must | For ordinary local UI actions that do not wait for the compiler—opening an already saved document/example, editing text, switching views, and starting an operation—the interface shall provide visible feedback within 1 second on the stated supported browsers. This is a proposed measurable target, pending stakeholder confirmation. |
| QR-04 | Must | A compiler request that remains outstanding shall not prevent editing the source area, opening documents/examples, or viewing a previous result. |
| QR-05 | Should | The setup instructions shall allow a course student or instructor with the stated prerequisites to start the environment and reach either simulated mode or a configured compiler-status check without developer intervention. The exact prerequisites remain to be agreed. |

## 5. External interfaces and dependencies

| Interface/dependency | Required interaction / constraint |
|---|---|
| Web browser | Hosts the local LBE user interface; compatibility target is the CQ-04 assumption. |
| Local persistence facility | Stores documents and test collections on the current browser/device; it is not a cloud account or shared repository. |
| Local file-selection interface | Lets the user choose a source file for import; the browser's permission model governs access. |
| Compiler interface (external) | Must eventually accept compile/run requests and return a correlation identifier or otherwise allow LBE to associate responses with a source-version identifier. Its final protocol is unresolved (CQ-01). |
| Compiler/interpreter (external) | Performs language processing/execution and supplies diagnostics, locations, optional artifacts, and cancellation support where available. It is developed and versioned separately from LBE. |
| Simulated compiler adapter | During interface development, returns deliberately marked sample responses with the same display categories expected from the real integration. It is not evidence that the real compiler compiled anything. |

## 6. Acceptance criteria

These are future acceptance checks; they are not results from an implementation.

| Check | Requirement(s) | Starting conditions | Action/input | Observable expected result |
|---|---|---|---|---|
| AC-01: Example remains available | FR-02 | Starter collection includes “factorial”; no user document is open. | Select factorial, change its input, then select factorial again. | The edited document is editable and differs as changed; selecting the starter example again supplies its original content. |
| AC-02: Persistence across refresh | FR-03, FR-04 | A named local document is open. | Enter distinctive source text, allow save feedback, refresh the page, and reopen the document. | The name and entered text reappear. If persistent storage is deliberately made unavailable, a clear retention warning appears rather than a false saved indication. |
| AC-03: Source diagnostic navigation | FR-09, FR-10 | Compiler adapter returns a compiler error with a valid agreed line/column for the submitted source. | Compile that source and activate the error-location control. | The result is labeled a compiler/source error, not runtime failure; editor focus/selection moves to the indicated submitted-source location. |
| AC-04: Infrastructure failure | FR-04, FR-09 | An edited persisted document exists; compiler endpoint is unreachable. | Start Compile. | The result says the compiler service could not be reached/used, does not say the source is invalid, and the edited document remains available to save/retry. |
| AC-05: Versioned overlapping work | FR-08, FR-12, QR-04 | Program version A starts a deliberately slow Run. | Change source to version B while A is outstanding, then let A finish. | Editing remains possible; A's result identifies version A rather than B, so the displayed result cannot be mistaken for B's result. |
| AC-06: Stop a non-terminating run | FR-12, FR-13 | Compiler adapter supports cancellation; a run is in progress indefinitely. | Activate Stop. | UI first shows cancellation requested and later displays the adapter's cancellation/termination status; editing/navigation remain usable. |
| AC-07: Suite continues after failure | FR-14–FR-16 | A collection has: T1 expected integer answer but will mismatch; T2 expected compiler rejection and is rejected; T3 expected answer and succeeds. | Run the collection. | T1 is failed with expected/observed detail; T2 and T3 are still attempted; summary reports 2 passed, 1 failed, 0 not completed. |
| AC-08: Simulated results are not confused with real results | FR-17 | Real compiler is unconfigured; simulated mode is selected. | Run a starter example. | Result is returned in the normal display categories but visibly says “simulated”; no UI text claims real compilation/execution occurred. |

## 7. Traceability

Sources use **B** for a passage/paragraph in the informal brief, **A** for an assumption above, and **CQ** for an unresolved clarification question.

| Requirement | Source(s) |
|---|---|
| FR-01 | B: “typing or pasting a short program” |
| FR-02 | B: “few examples… modify an example without losing access to the original” |
| FR-03 | B: “keep a program… return to it later”; A/CQ-08 |
| FR-04 | B: “refreshing the page [not] losing… come back… another session”; A/CQ-03 |
| FR-05 | B: “programs saved in files… not have to retype them” |
| FR-06–FR-07 | B: “check whether… compiles”; “run it and see the answer” |
| FR-08 | B: “know which version produced the result” |
| FR-09–FR-10 | B: error explanation/location; compilation vs running failure; compiler unreachable |
| FR-11 | B: inspect AST/generated code when available; detail should not get in the way |
| FR-12–FR-13 | B: long/non-finishing runs; stop; page usable while work progresses; CQ-06 |
| FR-14–FR-16 | B: named test collection, expected answer/rejection, summary, continue after troublesome test; CQ-05 |
| FR-17 | B: sample compiler responses permitted but must not be mistaken for actual results |
| FR-18 | B: local setup straightforward; coordinate compiler interface |
| QR-01–QR-02 | B: main tasks keyboard; messages not dependent only on colors |
| QR-03–QR-04 | B: “respond promptly” and page usable during work; A proposed 1-second target |
| QR-05 | B: another person can follow instructions and get it running; CQ-04 |

## 8. Review notes

| Draft issue found | Resolution |
|---|---|
| “Promptly” and “easy to get started” were not verifiable. | Replaced the former with proposed QR-03 one-second feedback target and made setup outcome measurable in QR-05; both are labeled as pending confirmation. |
| The brief asks to stop long runs but does not establish that a compiler can forcibly terminate them. | FR-13 specifies cancellation request and reported terminal status only, avoiding an unsupported termination guarantee. |
| “Run all tests” could imply aborting a suite on the first failure. | FR-15 expressly requires later independent attempts and FR-16 separates failed from not-completed outcomes. |
| Artifact display could overwhelm a beginner and might be unavailable. | FR-11 makes artifact panes hidden by default and conditional on supplied artifacts. |
| Saved work could be confused with cloud-backed sharing. | The scope and FR-04 define browser-local persistence; accounts/cloud/collaboration are excluded and collection sharing is deferred. |
