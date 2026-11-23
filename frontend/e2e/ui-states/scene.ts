import type { APIRequestContext, Browser, BrowserContext, Page, Route } from "@playwright/test";

const VIEWPORT = { width: 1440, height: 900 };
/** Long enough for frappe-ui transitions and the list skeleton to finish. */
const SETTLE_MS = 450;
const MANAGER = { email: "ui.states.manager@example.com", first_name: "Ngozi Okoye" };
const PASSWORD = "ui-states-Passw0rd!";

export interface Hold {
	release(): Promise<void>;
	abort(status?: number): Promise<void>;
}

/** What a flow can put on the site before it opens the page. Every name is unique to the path. */
export interface Seed {
	/** An exercise assigned to the signed-in Brand Manager. */
	exercise(label: string, extra?: Record<string, unknown>): Promise<string>;
	/** A budget change request on that exercise, waiting for the Brand Manager. */
	changeRequest(exercise: string, newBudget: number): Promise<string>;
}

export interface Scene {
	page: Page;
	context: BrowserContext;
	api: APIRequestContext;
	baseURL: string;
	/** Readable name shown in lists, unique to this path. */
	name(label: string): string;
	/** The brand every seeded record belongs to. */
	brand: string;
	seed: Seed;
	goto(path: string): Promise<void>;
	/** Holds requests whose URL matches until released or aborted. */
	hold(url: string | RegExp): Promise<Hold>;
	settle(ms?: number): Promise<void>;
	close(): Promise<void>;
}

let counter = 0;
let ready: Promise<void> | null = null;

async function admin(baseURL: string, browser: Browser): Promise<APIRequestContext> {
	const ctx = await browser.newContext({ baseURL });
	const res = await ctx.request.post("/api/method/login", {
		form: { usr: "Administrator", pwd: process.env.ADMIN_PASSWORD ?? "admin" },
	});
	if (!res.ok()) throw new Error(`Administrator login failed: ${res.status()}`);
	return ctx.request;
}

/** One Brand Manager, created once per run and reused by every path. */
function ensureManager(api: APIRequestContext): Promise<void> {
	ready ??= (async () => {
		const exists = await api.get(`/api/resource/User/${MANAGER.email}`);
		if (exists.ok()) return;
		const res = await api.post("/api/resource/User", {
			data: {
				email: MANAGER.email,
				first_name: MANAGER.first_name,
				send_welcome_email: 0,
				new_password: PASSWORD,
				roles: [{ role: "Brand Manager" }, { role: "Projects User" }],
			},
		});
		if (!res.ok()) throw new Error(`Could not create the Brand Manager: ${await res.text()}`);
	})();
	return ready;
}

export async function openScene(browser: Browser, baseURL: string, label: string): Promise<Scene> {
	const adminApi = await admin(baseURL, browser);
	await ensureManager(adminApi);
	const n = ++counter;
	const brand = `Zuri Snacks ${n}`;
	const company = (await (await adminApi.get("/api/resource/Company?limit=1")).json()).data[0].name;
	await adminApi.post("/api/resource/Brand", {
		data: { brand_name: brand, company, team: [{ user: MANAGER.email, brand_role: "Brand Manager" }] },
	});

	const context = await browser.newContext({ baseURL, viewport: VIEWPORT });
	const login = await context.request.post("/api/method/login", { form: { usr: MANAGER.email, pwd: PASSWORD } });
	if (!login.ok()) throw new Error(`Brand Manager login failed: ${login.status()}`);
	const page = await context.newPage();
	const holds: Array<() => Promise<void>> = [];

	const create = async (doctype: string, data: Record<string, unknown>): Promise<string> => {
		const res = await adminApi.post(`/api/resource/${doctype}`, { data });
		if (!res.ok()) throw new Error(`Could not create ${doctype}: ${await res.text()}`);
		return (await res.json()).data.name;
	};

	const seed: Seed = {
		exercise: (title, extra = {}) =>
			create("Marketing Campaign", {
				campaign_name: `${title} ${n}`,
				status: "Active",
				company,
				brand,
				brand_manager: MANAGER.email,
				start_date: "2026-11-01",
				end_date: "2027-01-31",
				budget: 6400000,
				objective: "Move 20,000 cases through the 14 partner stores during the season.",
				...extra,
			}),
		changeRequest: (exercise, newBudget) =>
			create("Campaign Change Request", {
				brand,
				campaign: exercise,
				reason: "Two more billboard sites on the Lekki corridor.",
				items: [{ fieldname: "budget", old_value: "6400000", new_value: String(newBudget) }],
			}),
	};

	return {
		page,
		context,
		api: adminApi,
		baseURL,
		brand,
		seed,
		name: (l) => `${l} ${n}`,
		goto: async (path) => {
			await page.goto(`/marketing${path}`);
		},
		hold: async (url) => {
			let mode: "hold" | "abort" | "pass" = "hold";
			const waiting: Array<() => void> = [];
			const handler = async (route: Route) => {
				if (mode === "abort") return route.fulfill({ status: 500, body: JSON.stringify({ exc_type: "ValidationError", _server_messages: "[]" }) });
				if (mode === "hold") await new Promise<void>((resolve) => waiting.push(resolve));
				return route.continue();
			};
			await page.route(url, handler);
			const release = async () => {
				mode = "pass";
				waiting.splice(0).forEach((r) => r());
			};
			holds.push(async () => {
				await release();
				await page.unroute(url, handler);
			});
			return {
				release,
				abort: async (status = 500) => {
					void status;
					mode = "abort";
					waiting.splice(0).forEach((r) => r());
				},
			};
		},
		settle: (ms = SETTLE_MS) => page.waitForTimeout(ms),
		close: async () => {
			for (const undo of holds) await undo().catch(() => undefined);
			await context.close();
			await adminApi.delete(`/api/resource/Brand/${encodeURIComponent(brand)}`).catch(() => undefined);
		},
	};
}
