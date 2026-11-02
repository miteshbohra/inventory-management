# Design system rules

Read this when choosing or adapting token values, or when a value in the existing styles does not map cleanly to a token.

## Spacing scale

Everything is a multiple of 4px, which keeps rhythm predictable.

| Token | Value | Typical use |
|---|---|---|
| `--space-1` | 4px | icon-to-label nudges |
| `--space-2` | 8px | tight gaps, badge padding, nav item gaps |
| `--space-3` | 12px | input padding, compact rows |
| `--space-4` | 16px | default gap, card padding on dense screens |
| `--space-5` | 20px | card padding, grid gaps |
| `--space-6` | 24px | section spacing, content padding |
| `--space-8` | 32px | large section breaks, page padding on wide screens |
| `--space-10` | 40px | empty/loading states |

Rules of thumb:
- Padding inside a component is less than or equal to the gap between components. Otherwise grouping looks wrong.
- Grid gap equals card padding or one step below it.
- Do not mix `rem` literals with tokens in the same rule.

## Snapping existing values

Existing apps usually have near-duplicates (`0.625rem`, `0.75rem`, `0.875rem`). Snap each to the nearest token instead of adding tokens. A change of 1-2px is invisible, while the consistency gain is real. Add a new token only when a value recurs in several places and genuinely differs in purpose.

## Color

- Keep the project's existing neutrals and accent. Derive tokens from what is already used.
- Roles: `--color-bg` (app background), `--color-surface` (cards), `--color-border`, `--color-text`, `--color-text-muted`, `--color-accent`, `--color-accent-soft`, plus success/warning/danger/info each with a solid and a soft variant.
- Sidebar may be light (matches the content, border-separated) or dark (slate-900). Default to light unless the existing brand is dark; light is less jarring when converting an existing light app.
- Status colors carry meaning. Do not reuse them decoratively.

## Radius, shadow, type

- Radius: small (6px) for inputs/buttons/badges, medium (10px) for cards, full for pills and avatars.
- Shadow: one subtle card shadow, one raised shadow for dropdowns/drawers. Prefer borders for resting state.
- Type scale: 12 / 13 / 14 (base) / 16 / 18 / 24 / 30. Titles use tight negative letter-spacing; uppercase micro-labels use positive letter-spacing. Base body at 14px suits dense data UIs.

## Layout dimensions

- Sidebar: 240px expanded, 72px collapsed.
- Top bar: 56-64px.
- Content max width: 1440-1600px, centered, with `--space-6` side padding (`--space-8` above 1280px).
- Breakpoints: 1024px (sidebar becomes a drawer below this), 640px (tighter content padding).

## Motion

150-200ms ease for hover, color and width transitions. Wrap non-essential motion in `@media (prefers-reduced-motion: reduce)` to disable it.
