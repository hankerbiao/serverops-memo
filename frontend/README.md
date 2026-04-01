<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run the frontend

The frontend now loads infrastructure data from the FastAPI backend instead of local mock data.

## Local development

1. Install dependencies:
   `npm install`
2. Set the API base URL in `.env.local`:
   `VITE_API_BASE_URL=http://127.0.0.1:8000`
3. Start the frontend:
   `npm run dev`

Run the backend separately before opening the UI, otherwise the frontend will show a load error banner.
