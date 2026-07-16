# Architectural · Service Layer

## Pattern card

| Field | Value |
|---|---|
| Family | Architectural |
| Status | Cross-link; this page demonstrates only a client and controlled fake |
| Route | Owned by Chapter 28 |
| Prerequisites | Functions, exceptions, application/persistence boundary concepts |
| Time | 20–30 minutes here, then the owner chapter |

You will recognize a use-case boundary without recreating the professional
capstone's Service Layer.

## Start with the pressure

A caller wants to complete a job, but it starts loading records, applying
domain rules, saving changes, and deciding transaction order itself. Another
caller repeats those steps differently. The use case has no single owner.

The pressure is duplicated application orchestration. A **Service Layer** can
offer task-oriented operations such as `complete(job_id)` while keeping
transport and interface code outside the use case.

## The pattern in plain language

A Service Layer is an application boundary that coordinates one use case. It
is not a bag of unrelated utilities and it is not the same as a web service.
The companion calls a controlled fake only; Chapter 28 owns domain rules,
persistence coordination, and the full implementation.

The simpler option is one well-named function in the application module.
Prefer it until several entry points or growing orchestration justify a
long-lived service object.

### Use it, avoid it, count its cost

- Consider it when command-line, web, or batch entry points must share the same
  use-case order and failure contract.
- Avoid a class whose methods merely forward every Repository operation.
- Its cost is another application API, transaction ownership, and tests across
  domain plus persistence boundaries.
- Remove it when one short function clearly owns the only use case.

## Predict, run, observe

Predict whether the client should know how the job is stored, and whether
`ServiceBusy` may be reported as completed.

Run the verified, deliberately small cross-link companion:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B "zz_Appendix C Software Design Patterns/architectural - Service Layer/example.py"
```

Expected output:

```text illustrative
job-1:completed
calls:['job-1']
boundary:job_id must be non-empty text
malformed:invalid_service_result
recoverable:try later
recovered:job-2:completed
```

The [Service Layer client source](example.py) proves only that the caller can
use a narrow task-oriented operation, validate its `CompletionResult`, and
preserve its failures. A wrong type, identity, or status becomes the stable
`invalid_service_result` error instead of leaking `KeyError` or partial data.
The fake is not evidence for domain correctness or persistence behavior.

## Normal, boundary, and recoverable behavior

- **Normal:** the caller requests one use case and receives a validated result.
- **Boundary:** an empty identifier fails before the service call; a malformed
  service result or non-`completed` status is rejected with one stable error.
- **Recoverable:** `ServiceBusy` remains distinct. Once the service is healthy,
  the caller starts a new operation rather than inventing success. This fake
  defines busy before completion; a real unknown outcome is not automatically
  permission to retry.

Common mistakes are placing presentation formatting in the Service Layer,
letting callers coordinate repositories anyway, or treating every exception as
a retry instruction.

## Guided cross-link exercise

In Chapter 28, trace one entry point into its application use case and then to
the persistence boundary. Record which layer owns validation, domain policy,
storage, and user-facing formatting. Do not duplicate the capstone here.

**Hint:** responsibilities should have one owner. If the same rule appears in
the entry point and service, mark the duplication for review.

**Success criterion:** your trace names the use-case operation, its normal and
failure results, the Repository boundary it uses, and one simpler-function
alternative.

## Explained solution and decision record

The entry point translates input and output. The Service Layer coordinates the
application use case. Domain objects own domain rules, and a Repository owns
persistence access. A module function is enough until multiple entry points or
resource ownership make a service object clearer.

```text illustrative
problem → callers duplicate one use-case orchestration
forces → one ordering, policy, and failure contract across entry points
simplest option → one application function
chosen pattern → Service Layer when several entry points need that boundary
cost → another API and transaction/integration verification
expected failure → callers bypass or reorder domain and persistence work
verification → owner-chapter normal, boundary, failure, and integration checks
when to remove it → one short function owns the only use case
```

## Checkpoint and navigation

You pass this cross-link when you can distinguish a Service Layer from a web
service, a Repository, and a utility class, and can identify Chapter 28 as the
implementation owner.

[Return to the Appendix C family catalogue](../README.md#family-index) ·
[Study the Service Layer owner in Chapter 28](../../chapter-28-professional-capstone/README.md) ·
[Review the Repository cross-link](<../architectural - Repository/README.md>)
