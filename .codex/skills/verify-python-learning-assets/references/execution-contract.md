# Execution and fence contract

## Classification oracle

- `runnable`: complete trusted Python expected to exit zero under the declared interpreter.
- `expected-error`: complete trusted Python expected to exit nonzero with a declared stable diagnostic signal.
- `compile-only`: syntax or compilation evidence; do not execute behavior.
- `source-ref`: an excerpt backed by a repository-relative companion path and stable verifier/plugin check ID.
- `todo`: intentionally incomplete learner work; never execute it as a solution.
- `illustrative`: pseudocode, shell/configuration, partial code, dependency-bearing code, or a concept-only fragment.
- `output`: inert expected output associated with the immediately preceding executable example.

Require exactly one classification and a language token for each changed fence. Treat prose that conflicts with the classification as a defect.

## Generic eligibility

Use generic execution only for trusted standard-library Python that needs no network, package installation, subprocess, multiprocessing, native library, persistent service, credential, or privileged filesystem access. Route every other executable claim to a tested companion source and explicit verifier or plugin check.

Before execution, reject undeclared input, working-directory dependence, unbounded loops/output, destructive paths, public targets, secrets, and personal data. Use the repository validator's configured timeout and output limits rather than inventing a wider local exception.

## Execution record

Capture:

- repository-relative lesson path and fence line;
- classification and companion source/check ID when present;
- interpreter implementation and full version;
- normalized command and declared fixtures;
- timeout and combined-output limit;
- exit status and stable comparison result;
- cleanup/process-group result.

Normalize only documented unstable material such as temporary directory names. Do not hide semantically meaningful ordering, values, exception classes, or missing output.

## Expected-error discipline

Verify all of the following:

1. execution reaches the intended failure rather than an earlier setup error;
2. exit status is nonzero within the bound;
3. exception type or stable diagnostic substring matches the lesson;
4. output does not expose unsafe values;
5. the lesson explains why it failed;
6. the corrected recovery example exits zero.

Do not require a full traceback byte-for-byte across Python maintenance releases.
