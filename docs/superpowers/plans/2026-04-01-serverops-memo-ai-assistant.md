# ServerOps AI Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add memo-oriented metadata plus a structured AI assistant that retrieves asset records and local knowledge, then renders actionable answers in the frontend.

**Architecture:** Extend the existing server/service schema with tags, aliases, notes, and service category. Replace the free-form `/api/chat` flow with a structured `/api/assistant/query` response that combines asset search and local Markdown knowledge lookup. Update the frontend AI panel and list filtering to consume the richer metadata and assistant response.

**Tech Stack:** FastAPI, SQLModel, SQLite, pytest, React, TypeScript, Vite

---

### Task 1: Expand backend data model and CRUD schema

**Files:**
- Modify: `backend/models.py`
- Modify: `backend/schemas.py`
- Modify: `backend/services.py`
- Test: `backend/tests/test_api.py`

- [ ] Step 1: Write failing API tests for server CRUD with tags, aliases, notes, and service category/notes/aliases.
- [ ] Step 2: Run `pytest backend/tests/test_api.py -v` and verify the new assertions fail for missing fields.
- [ ] Step 3: Implement the minimal model, schema, serialization, and CRUD changes to persist the new fields.
- [ ] Step 4: Re-run `pytest backend/tests/test_api.py -v` and verify the CRUD tests pass.

### Task 2: Add tag APIs and assistant query backend

**Files:**
- Modify: `backend/main.py`
- Modify: `backend/services.py`
- Modify: `backend/schemas.py`
- Create: `docs/knowledge/ai-services/open-webui.md`
- Create: `docs/knowledge/troubleshooting/ollama.md`
- Test: `backend/tests/test_api.py`

- [ ] Step 1: Write failing tests for tag CRUD and `/api/assistant/query` with structured response sections.
- [ ] Step 2: Run `pytest backend/tests/test_api.py -v` and verify the new endpoint tests fail correctly.
- [ ] Step 3: Implement tag CRUD, local knowledge loading, asset search, and structured assistant response generation.
- [ ] Step 4: Re-run `pytest backend/tests/test_api.py -v` and verify all backend endpoint tests pass.

### Task 3: Update frontend types, API client, and assistant panel

**Files:**
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/AIChat.tsx`

- [ ] Step 1: Write the failing TypeScript changes by updating the component usage to the new assistant response shape.
- [ ] Step 2: Run `npm run build` in `frontend` and verify the build fails on missing types/props.
- [ ] Step 3: Implement the new assistant data types, API client, and structured AI panel rendering with records and actions.
- [ ] Step 4: Re-run `npm run build` in `frontend` and verify the frontend compiles.

### Task 4: Extend list/detail/modal UI for memo metadata

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/ServerComponents.tsx`
- Modify: `frontend/src/types.ts`
- Test: `frontend` build

- [ ] Step 1: Update UI code to reference tags, notes, aliases, and category so the build fails until all call sites are handled.
- [ ] Step 2: Run `npm run build` in `frontend` and verify failures reflect missing UI support.
- [ ] Step 3: Implement metadata fields in list/detail/modal views plus richer filtering in the servers page.
- [ ] Step 4: Re-run `npm run build` in `frontend` and verify the UI compiles cleanly.

### Task 5: Verify end-to-end behavior

**Files:**
- Verify only

- [ ] Step 1: Run `pytest backend/tests/test_api.py -v`.
- [ ] Step 2: Run `npm run build` in `frontend`.
- [ ] Step 3: Review the spec checklist against the implemented scope and note any gaps before claiming completion.
