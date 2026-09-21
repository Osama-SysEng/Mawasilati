# Dispatch: operating model

## Responsibility

The Dispatch bounded context owns driver assignment and capacity coordination. Its events are correlation-aware, its commands carry an accountable actor, and external side effects require policy approval.

## Safety rule

Location, payment, driver assignment, and passenger data are not shared or mutated merely because an interface requests it. The policy and ownership checks must pass first.

## Acceptance signal

A feature is accepted only when its domain test, API contract, and operating evidence agree.
