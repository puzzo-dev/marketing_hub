# UI states (review-ui-states)

State machines for Marketing Hub's screens, walked by Playwright to screenshot every state.

**Status: written, never run.** It was authored in a session with no bench or browser, so the
selectors, request patterns (`LIST`, `QUEUE`, `DASH`) and seed payloads are unverified.
Expect to adjust them on the first run. `harness files` (`flow.ts`, `manifest.ts`,
`capture.spec.ts`) are the skill's, unchanged.

Needs: a bench with erpnext + marketing_hub, `yarn build`, `BASE_URL`, `ADMIN_PASSWORD`, and
dev deps `@playwright/test xstate @xstate/graph`.

    npx playwright test -c e2e/ui-states/playwright.config.ts
    UI_STATES_FLOWS=approvals npx playwright test -c e2e/ui-states/playwright.config.ts

Flows so far: home, exercises, approvals. Still to write: exercise detail, content, out-of-home,
placements, forms, client screens.
