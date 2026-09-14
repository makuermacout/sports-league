# Build and Ship an AI-Assisted Full-Stack App — Sports-League Scoreboard

## Overview

This project builds a working end-to-end application with AI assistance: a
Sports-League Scoreboard app. It is visual, interactive, and still requires
the main parts of a real system:

* product spec
* frontend
* OpenAPI contract
* backend
* database
* tests

The goal is not to let an AI tool build everything unchecked. The goal is to
practice a controlled workflow where AI helps move faster while each step is
verified by hand.

The project ends with an app that runs on my machine: a frontend and a
backend that talk to each other over a defined contract, with data persisted
in SQLite. Integration tests, containers, CI, deployment, and CI/CD are out
of scope for this stage.

I will:

* Write a small product spec with user stories, acceptance criteria, and
  non-goals before generating any code
* Draft a frontend prototype with an AI tool (Lovable, Bolt, Cursor, Claude
  Code, Codex, ...), then pull it into a normal repo workflow and make it
  maintainable
* Define an OpenAPI contract as the source of truth between frontend and
  backend
* Implement a FastAPI backend against the contract, starting with a mock
  store and tests for the key endpoints
* Swap the mock store for SQLite, keeping the app database-agnostic so
  Postgres can replace it later without a rewrite
* Add unit and frontend tests that cover the behavior described in the spec
  and the contract

## Reference Material

* Reference app: https://github.com/alexeygrigorev/interview-canvas-share
* Recording: [Build and Ship an AI-Assisted Full-Stack App](https://www.youtube.com/watch?v=x9dq5nBpDg8)
* Article: [Build and Ship a Full-Stack App with AI Coding Assistants](https://aishippingblog.com/p/build-and-ship-a-full-stack-app-with)

## Deliverables

At the end of this stage, the repo includes:

```
product-spec.md
AGENTS.md or equivalent
frontend/
backend/
openapi.yaml
tests/
docs/ai-usage-report.md
```

The app runs locally from the README, persists data in SQLite, and passes
its own tests.

## Status

- [x] `product-spec.md` — done (Sports-League Scoreboard)
- [ ] Frontend prototype
- [ ] Pulled into repo workflow
- [ ] `openapi.yaml`
- [ ] FastAPI backend (mock store) + tests
- [ ] SQLite persistence
- [ ] Remaining unit/frontend tests
- [ ] `AGENTS.md`
- [ ] `docs/ai-usage-report.md`
- [ ] README with local run instructions
