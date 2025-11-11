# Project Style Guide

This guide outlines the coding conventions and design language for our project. All generated code must adhere to these rules.

## 1. Technology Stack

- **Backend:** Django
- **Frontend:** HTML, Tailwind CSS, DaisyUI, HTMX
- **Tooling:** `uv`

---

## 2. UI/UX Design Language

This is the most important part. We use a **component-first** approach with DaisyUI, customized via `settings.py`.

### A. Core Philosophy

- **NEVER** write "magic numbers" for styling (e.g., `text-[13px]`, `bg-[#FF0000]`).
- **ALWAYS** use the pre-defined DaisyUI components or Tailwind's theme-based utilities.
- The goal is a consistent, modern, and configurable design.

### B. Colors (DaisyUI Theme)

Our theme is defined in `settings.py`. The AI must **only** use these semantic colors.

- **Primary (`primary`):** For all main call-to-action buttons (e.g., "Donate Now", "Create Campaign").
- **Secondary (`secondary`):** For less important actions (e.g., "Edit Profile").
- **Accent (`accent`):** For highlights, badges, or special notices.
- **Neutral (`neutral`):** For base backgrounds, card backgrounds, etc.
- **Error/Success/Warning (`error`, `success`, `warning`):** For alerts and form validation.

**Example Instruction:** "Create a success alert" should generate `<div class="alert alert-success">...</div>`, NOT `<div class="bg-green-500 p-4">...</div>`.

### C. Typography (Fonts & Sizes)

- **Font:** [e.g., "Inter, sans-serif" - *Specify your chosen font here*]
- **Font Sizes:** Use Tailwind's built-in type scale (`text-xs`, `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`, etc.).
  - **Body Text:** `text-base`
  - **Page Titles:** `text-3xl font-bold`
  - **Card Titles:** `text-xl font-semibold`
  - **Subheadings:** `text-lg`

### D. Component Usage

- **Buttons:** Always use the DaisyUI `btn` class. (e.g., `btn`, `btn-primary`, `btn-outline`).
- **Cards:** All campaigns must be displayed using the DaisyUI `card` component.
- **Forms:** All form inputs MUST use DaisyUI classes (`input`, `textarea`, `select`, `checkbox`, `toggle`) for a consistent look.

---

## 3. Backend: Django & Python Style

- **PEP 8:** All Python code MUST follow PEP 8 for style and formatting.
  - Follow the `ruff` linting rules in the `pyproject.toml` file.
- **Views:** We prefer **Function-Based Views (FBVs)** for simplicity.
- **Naming:**
  - Variables & Functions: `snake_case` (e.g., `def get_campaign_details(...):`)
  - Classes: `PascalCase` (e.g., `class Campaign(models.Model):`)
- **Templates:**
  - All templates must live in `[app_name]/templates/[app_name]/`.
  - All templates must extend `base.html`.

---

## 4. HTMX Conventions

- **Purpose:** Use HTMX for partial page updates to make the app feel dynamic. (e.g., donation forms, live-updating totals, favoriting a campaign).
- **Views:** Django views that respond to an HTMX request MUST return _only_ the HTML fragment (a "partial"), not the full page.
- **Targeting:** Use specific `id` attributes for `hx-target`.
- **Style:** Do NOT mix styling classes (like `btn`) with HTMX attributes. Keep them separate.
