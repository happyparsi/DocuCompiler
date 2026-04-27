# FRONTEND DOCUMENTATION

This document covers all the frontend files responsible for the UI/UX of DocuCompiler.

## List of Frontend Files
1. `static/index.html` - The structural skeleton and React application logic.
2. `static/style.css` - The visual styling, layout, theme definitions, and animations.

*(Note: `script.js` was removed and its logic migrated to the React app in `index.html`)*

---

## 1. `static/index.html`

### Purpose and UI/UX Role
This file is the single-page application (SPA) entry point built using **React 18** (loaded via CDN). It creates a premium, dark-glassmorphism interface consisting of:
- An **Authentication Overlay** (for Login/Signup) with animated scale-ins.
- A **Sidebar** (for showing chat history/sessions and theme toggling).
- A **Main Chat Area** (for displaying messages and summaries) with **Markdown Rendering** via `marked.js` and a bouncing typing indicator.
- An **Input Area** with drag-and-drop support, format strategies, and a document context badge when a document is active.

### How it Connects to the Backend
The React components in this file fetch data via REST calls to the FastAPI backend (`/api/login`, `/api/summarize`, `/api/sessions`, etc.) and automatically update the UI state dynamically.

---

## 2. `static/style.css`

### Purpose and UI/UX Role
Handles the premium aesthetics of the application.
- Uses CSS custom properties (`--bg`, `--accent`, etc.) defined in `:root`.
- Supports theme toggling (Light, Dark, System) via the `[data-theme="light"]` selector.
- Implements glassmorphism effects (backdrop-filter) and smooth animations/transitions for a polished feel.
