# AGENTS.md

## Purpose
This repository implements a RAG-based chatbot (Julius Caesar persona) with:
- Flask backend (API + orchestration)
- LangChain / LangGraph for agent workflows
- Vector retrieval layer
- Next.js frontend for chat UI

Agents working in this repo should prioritize:
- correctness over cleverness
- minimal, readable diffs
- clear separation of concerns (backend / frontend / orchestration)

---

## Core Rules

- Do not make unrelated refactors.
- Prefer small, targeted changes.
- Ask or stop if requirements are ambiguous.
- Do not silently change API contracts.
- Preserve existing patterns unless explicitly improving them.

Before finishing any task:
- Ensure code is consistent with existing structure
- Add or update tests where appropriate
- Document assumptions and tradeoffs

---

## Project Structure

- `backend/` → Flask API, routes, models
- `orchestration/` → LangChain / LangGraph flows, RAG logic
- `retrieval/` → vector search, embeddings, document handling
- `frontend/` → Next.js React UI
- `tests/` → backend + integration tests

---

## Delegation Strategy (IMPORTANT)

For non-trivial tasks, split work into specialized subagents.

Preferred roles:

### 1. backend-agent
Scope:
- Flask routes
- request/response schemas
- database / persistence

Rules:
- Do NOT modify frontend code
- Do NOT change orchestration logic unless required

---

### 2. orchestration-agent
Scope:
- LangGraph nodes
- prompt templates
- routing / classification logic
- RAG flow

Rules:
- Do NOT modify Flask routes unless necessary
- Keep prompts structured and explicit
- Clearly document any prompt changes

---

### 3. retrieval-agent
Scope:
- embeddings
- chunking
- vector DB interactions
- search ranking

Rules:
- Do NOT change orchestration flow logic
- Focus on retrieval quality and performance

---

### 4. frontend-agent
Scope:
- React components
- UI state
- API integration

Rules:
- Do NOT modify backend logic
- Assume API contracts are correct unless told otherwise

---

### 5. test-agent
Scope:
- unit tests
- integration tests
- regression coverage

Rules:
- Prefer testing behavior over implementation
- Add edge cases (invalid input, empty context, failures)

---

### 6. review-agent
Scope:
- correctness
- edge cases
- performance risks
- hallucination risks (RAG-specific)

---

## Parallel Work Guidelines

- Avoid multiple agents editing the same file.
- If overlap is required, coordinate via a plan first.
- Prefer:
  - backend + frontend in parallel
  - retrieval + orchestration in parallel (if loosely coupled)

---

## Required Output Format (for each agent)

Each agent MUST return:

- Summary of changes
- Files modified
- Assumptions made
- Blockers encountered
- Tests added or run
- Risks or follow-ups

---

## RAG-Specific Guidelines

- Never hallucinate missing context — fall back gracefully.
- Clearly separate:
  - retrieval
  - reasoning
  - response generation
- Prefer simple, inspectable prompts over complex ones.
- Track and expose reasoning when useful for debugging.

---

## Prompt / LLM Guidelines

- Keep prompts deterministic and structured.
- Avoid overly verbose instructions.
- Prefer explicit schemas when possible.
- If classification is required, prefer scoring/weighting over single-label outputs.

---

## Testing Expectations

Backend:
- endpoint correctness
- error handling
- schema validation

RAG:
- relevant document retrieval
- fallback when no context
- classification accuracy (where applicable)

Frontend:
- rendering states
- API interaction
- loading/error UX

---

## When to STOP and Ask

Agents should STOP and report instead of guessing when:

- API contract is unclear
- required files are missing
- multiple valid approaches exist with tradeoffs
- a change would impact multiple layers (backend + frontend + orchestration)

---

## Preferred Workflow

1. Exploration (read relevant files only)
2. Plan (what will change and why)
3. Implementation (scoped to role)
4. Tests
5. Review summary

---

## Guiding Principle

Keep the system understandable.

A slightly less “clever” but more readable solution is preferred over a complex one.