import { defineConfig, devices } from "@playwright/test";
import { resolve } from "node:path";

/**
 * Captures every Marketing Hub UI state as a screenshot by walking the machines under `flows/`.
 * Not a test suite: one run per flow, no retries, one browser.
 *
 * Needs a bench with erpnext and marketing_hub installed, `yarn build` already run, and
 *   BASE_URL      the site, e.g. http://marketing.localhost:8000
 *   ADMIN_PASSWORD the Administrator password (used only to seed through the REST API)
 */
const baseURL = process.env.BASE_URL ?? "http://marketing.localhost:8000";

export const OUT_DIR = resolve(__dirname, "out");

export default defineConfig({
	testDir: __dirname,
	testMatch: /capture\.spec\.ts/,
	outputDir: resolve(__dirname, ".runs"),
	fullyParallel: false,
	retries: 0,
	workers: 1,
	timeout: 15 * 60_000,
	expect: { timeout: 10_000 },
	reporter: [["list"]],
	use: { baseURL, viewport: { width: 1440, height: 900 }, actionTimeout: 15_000, navigationTimeout: 30_000 },
	projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
