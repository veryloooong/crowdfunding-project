# Project Style Guide: Crowdfunding Platform

**Status:** School Project (Optimization/Scaling is NOT a priority; Code clarity and simplicity ARE).

## 1. Technology Stack

- **Language:** Python 3.12+
- **Backend Framework:** Django 5.x
- **Database:** SQLite (`db.sqlite3` - Single file, no external server)
- **Package Manager:** `uv`
- **Frontend CSS:** Tailwind CSS v4 (configured via `settings.py`)
- **Component Library:** DaisyUI (via Tailwind plugin)
- **Interactivity:** HTMX (for dynamic behavior without writing JS)
- **Icons:** Heroicons (via `django-heroicons`)

---

## 2. Architecture & Deployment

- **Pattern:** Monolithic MVC (Django MVT).
  - **NO** Microservices.
  - **NO** separate API Gateway.
  - **NO** React/Vue/Angular SPAs.
- **Deployment Model:** Single Node.
  - The Web Server (Gunicorn/Django), Static Files, and Database (SQLite) all reside on the same machine.
- **Folder Structure:** Standard Django app structure.
  - `core/` (Project settings)
  - `theme/` (Tailwind app)
  - `campaigns/` (Main logic)

---

## 3. UI/UX Design Language

We use a **Component-First** approach using DaisyUI.

### A. Core Rules

1.  **No "Magic Numbers":** Avoid arbitrary values like `w-[13px]` or `bg-[#123456]`. Always use semantic utility classes.
2.  **Use DaisyUI Components:** Don't build a button from scratch. Use `.btn`. Don't build a card from scratch. Use `.card`.
3.  **Dark Mode:** The app should support the `light` and `dark` themes defined in `settings.py`.

### B. Semantic Colors (Use these classes)

Do not use `bg-blue-500` or `text-green-600`. Use the semantic role:

- **Primary (`primary`):** Main actions (Donate, Create Campaign).
- **Secondary (`secondary`):** Secondary actions (Edit, Settings).
- **Accent (`accent`):** Highlights, badges, progress bars.
- **Neutral (`neutral`):** Card backgrounds, sidebars.
- **Base-100/200/300:** Page backgrounds.
- **Info/Success/Warning/Error:** Contextual alerts.

### C. Typography

- **Font:** System sans-serif or Inter.
- **Headings:**
  - Page Title: `text-3xl font-bold mb-6`
  - Section Title: `text-xl font-semibold mb-4`
- **Body:** `text-base text-base-content`

### D. Icons

- Use **Heroicons** Outline or Solid.
- Implementation: `{% heroicon_outline "icon-name" class="w-5 h-5" %}`

---

## 4. Backend Conventions (Django)

### A. Code Style

- Follow **PEP 8**.
- Use **Function-Based Views (FBVs)** for better readability and easier integration with HTMX.
- **Type Hinting:** Use Python type hints where helpful (e.g., `def get_campaign(request: HttpRequest) -> HttpResponse:`).

### B. Models

- Use `PascalCase` for model names (`Campaign`, `Donation`).
- Use `snake_case` for field names.
- **Money:** Always use `DecimalField` for currency (never `FloatField`).

### C. Views & HTMX

- **Pattern:** Views should be able to detect HTMX requests.
- **HTMX Logic:**
  - If `request.htmx`: Return a **partial template** (HTML snippet).
  - If standard request: Return the **full template** (extends `base.html`).
- **Attributes:** Use `hx-get`, `hx-post`, `hx-target`, and `hx-swap` to handle interactions.
  - _Example:_ `<button hx-post="/donate/1" hx-target="#donation-count" hx-swap="outerHTML">Donate</button>`

---

## 5. Coding Workflow (AI Instructions)

When generating code:

1.  **Simplicity first:** Do not over-engineer.
2.  **No React/Next.js:** If I ask for frontend code, give me Django Templates + Tailwind.
3.  **Config:** If Tailwind config is needed, remember it is done in `settings.py` (Tailwind v4), not `tailwind.config.js`.
