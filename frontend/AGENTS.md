# Repository Guidelines

## Project Structure & Module Organization
This repository is a Vite + React 19 + TypeScript app. Main application code lives in `src/`. Use `src/components/` for UI components such as `AIChat.tsx` and `ServerComponents.tsx`, `src/lib/` for shared helpers like `cn()` and `generateId()`, and `src/constants.ts` and `src/types.ts` for static data and shared types. Global styles are in `src/index.css`. Root-level config is in `vite.config.ts`, `tsconfig.json`, and `package.json`.

## Build, Test, and Development Commands
- `npm install`: install dependencies.
- `npm run dev`: start the Vite dev server on port `3000`.
- `npm run build`: produce a production bundle in `dist/`.
- `npm run preview`: serve the built bundle locally for a final check.
- `npm run lint`: run TypeScript type-checking with `tsc --noEmit`.
- `npm run clean`: remove the `dist/` directory.

## Coding Style & Naming Conventions
Follow the existing TypeScript React style:
- Use 2-space indentation and semicolons.
- Name React components and types in `PascalCase`.
- Name helpers, variables, and functions in `camelCase`.
- Keep component files in `src/components/`; keep reusable utilities in `src/lib/`.
- Prefer explicit shared types from `src/types.ts` over inline object shapes when reused.

No dedicated formatter config is present, so match the surrounding file style exactly and run `npm run lint` before submitting changes.

## Testing Guidelines
There is no automated test framework configured yet. For now, treat `npm run lint` and a manual `npm run preview` smoke test as the minimum validation for UI or state changes. When adding tests later, place them beside the source file as `*.test.ts` or `*.test.tsx`.

## Commit & Pull Request Guidelines
Local Git history is not available in this workspace, so use clear, imperative commit messages such as `feat: add server detail filters` or `fix: guard empty AI prompt`. Keep commits focused. PRs should include:
- a short description of the change,
- manual verification steps,
- linked issue or task when applicable,
- screenshots or screen recordings for UI changes.

## Security & Configuration Tips
Keep secrets in `.env.local`, especially `GEMINI_API_KEY`. Do not commit API keys, passwords, or real infrastructure data. If using sample server records, sanitize sensitive fields before sharing screenshots or logs.
