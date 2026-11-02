---
name: saas-sidebar-redesign
description: Redesign a Vue 3 app's UI into a modern SaaS-style interface with a vertical left sidebar instead of a top nav bar, a consistent spacing scale and design tokens, and polished cards, tables, badges and buttons. Use this skill whenever the user wants to modernize, restyle, or "make professional" a Vue 3 frontend, move navigation from a top bar to a sidebar, add a collapsible side menu, introduce design tokens or a spacing system, or make a dashboard/admin UI look like a SaaS product, even if they never say "sidebar" or "redesign" explicitly.
---

# SaaS sidebar redesign for Vue 3

Turn a Vue 3 app with a top navigation bar into a SaaS-style layout: a left sidebar for navigation, a slim top bar for page-level actions, a content area on a consistent spacing scale, and shared components (cards, tables, badges, buttons) that all draw from one set of design tokens.

The goal is a coherent system, not a pile of restyled pages. A sidebar alone looks bolted on if spacing, radius and color still vary from view to view. That is why tokens come before component restyling, and why the skill stops short of rewriting each view.

## Scope

In scope: the app shell (`App.vue` or equivalent layout), a sidebar component, a sidebar state composable, global design tokens, and the shared/global styles for cards, tables, badges, buttons, form controls and page headers.

Out of scope unless the user asks: view-level logic, data fetching, routing structure, per-view layout rewrites, new dependencies. Preserve behavior. Every existing route, modal trigger, filter and event wiring must work after the redesign, because a redesign that breaks the app is worse than no redesign.

## Workflow

### 1. Discover before changing anything

Read, do not guess:

- The shell: where the top nav lives (usually `App.vue`), which router-links it holds, and what else is in the bar (language switcher, profile menu, search, notifications).
- Global styles: where they live and whether they are scoped or global. Note every hex color, `px`/`rem` spacing value, radius and shadow in use. Existing values are the raw material for tokens, so extract them rather than inventing a new palette. Keep the project's established palette unless the user asks for a new one.
- Project rules: read `CLAUDE.md` (root and client) for conventions that constrain the work, such as API style (Options vs Composition), "no emojis in UI", i18n usage, required subagents for `.vue` files, comment requirements. Follow them. If the project says `.vue` changes must be delegated to a specific subagent, delegate the component work to it with the specs from this skill.
- Router: list routes so every nav item maps to a real path, and check for i18n keys on labels so new labels reuse them.
- Anything that assumes a top bar: `position: sticky; top: 70px` filter bars, hard-coded header heights, `100vh` calculations, z-index layers. These break silently when the shell changes.

Summarize what you found in a short plan (current structure, what moves where) before editing, so the user can catch a wrong assumption cheaply.

### 2. Establish design tokens first

Copy `assets/tokens.css` into the project's global style entry (or import it from there) and adapt the values to the palette you extracted in step 1. Tokens cover color, a 4px-based spacing scale, radius, shadow, type scale, layout dimensions (sidebar widths, top bar height) and motion.

Why first: every later step references `var(--space-4)` rather than `1rem`, so spacing consistency is enforced by construction. Then replace one-off values in the shared styles with tokens. Map to the nearest token; if a value fits none, that is usually a sign of inconsistency, so snap it to the scale instead of adding a token.

See `references/design-system.md` for the scale rationale and the rules for choosing values.

### 3. Build the sidebar

Use `assets/AppSidebar.vue` and `assets/useSidebar.js` as starting points. Adapt them to the project's component style (match the existing API style, naming, and file layout) rather than pasting verbatim.

Required behavior:

- **Structure**: brand/logo at top, nav list in the middle, user area (profile menu, language switcher) pinned at the bottom. Group items under small section labels if there are more than about six.
- **Items**: driven by an array of `{ to, label, icon }`, with labels coming from the project's i18n if it has one. Use `router-link` with exact-active handling so `/` is not highlighted on every page.
- **Icons**: inline SVG (stroke style, 20px, `currentColor`). No icon library dependency and no emojis.
- **Active state**: tinted background plus an accent-colored icon/text; hover state subtler. Keep a visible keyboard focus ring.
- **Collapsible**: expanded around 240px, collapsed to a roughly 72px icon rail with labels hidden and a `title`/tooltip on each item. Persist the choice in `localStorage` (guard against it being unavailable).
- **Mobile**: below the tablet breakpoint the sidebar becomes an off-canvas drawer with a backdrop, opened by a hamburger button in the top bar, closed on route change, backdrop click and Escape.
- **Accessibility**: `<nav aria-label>`, `aria-current="page"` on the active link, `aria-expanded` on the toggle, labelled icon-only buttons.

### 4. Restructure the shell

Replace the top nav with a layout of sidebar plus main column. The main column gets a slim top bar (hamburger on mobile, page title or breadcrumb, global actions such as filters or search) and a scrollable content area with a max width and token-based padding.

Move things that lived in the old top bar to where they now belong: profile and language to the sidebar footer, global filter bars to the top of the content area (not sticky under a header that no longer exists). Keep modals mounted at the shell level exactly as before.

### 5. Restyle the shared components

Apply tokens to the global/shared styles so every view inherits the polish without edits:

- **Cards**: surface background, 1px border, radius token, subtle shadow, consistent header with a bottom divider.
- **Stat tiles**: consistent label/value hierarchy; semantic color only on the value or a small indicator, not whole tiles.
- **Tables**: sticky-feeling header on a muted background, small uppercase column labels, comfortable row height, row hover, right-aligned numeric columns where easy.
- **Badges**: soft tinted background with a darker text of the same hue; one shape across the app.
- **Buttons and inputs**: one height scale, one radius, a visible focus ring, clear disabled state.
- **Page headers**: one pattern for title plus description plus actions.
- **Loading/error/empty states**: consistent treatment.

Prefer changing the shared stylesheet. Only touch a view when it hard-codes a value that fights the system (for example a fixed pixel width that overflows next to the sidebar). Keep those edits minimal and mention them in the summary.

### 6. Verify in the browser

Static reading is not enough for layout work. Run the app and check, at desktop, tablet and mobile widths:

- Every nav item routes correctly and highlights only on its own page.
- Collapse and expand work and persist across reload; the drawer opens and closes on mobile.
- No horizontal page scroll; wide tables scroll inside their own container.
- Sticky/overlay elements (filter bars, modals, dropdowns) sit at the right height and z-index.
- Contrast on active, hover and badge states is readable.
- Nothing from the old top bar is orphaned, and the browser console is clean.

If the project provides browser tooling (for example Playwright MCP) use it to take screenshots. Fix what you find, then report.

## Quality bar

- Every spacing value is a token. Every color is a token. If you reach for a raw value, add or reuse a token.
- Whitespace does the grouping: related things close together, sections clearly separated. Avoid adding borders where spacing already separates.
- Restraint reads as professional: one accent color, neutral surfaces, soft shadows, short transitions (150-200ms) that respect `prefers-reduced-motion`.
- Match the project's conventions on top of this skill. Where project rules and this skill disagree (for example no emojis, a required subagent, a comment requirement), the project wins.
- Comment non-obvious logic (collapse persistence, drawer breakpoint handling, route-change closing) briefly, explaining why.

## Final report

Finish with a short summary: files created and changed, tokens introduced, what moved where from the old top bar, any view-level edits and why, what you verified and at which widths, and anything you deliberately left alone. Be honest about anything you could not verify.
