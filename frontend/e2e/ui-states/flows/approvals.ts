import { setup } from "xstate";
import { defineFlow } from "../flow";
import type { Hold, Scene } from "../scene";

type Event = { type: "LOADS" } | { type: "FAILS" } | { type: "SELECT" } | { type: "CLOSE" } | { type: "APPROVES" };

const holds = new WeakMap<Scene, Hold>();
const QUEUE = /Workflow(%20|\+| )Action/;

/**
 * The approvals queue: Frappe's Workflow Action list on the left, the request on the right.
 * In the code: `Approvals.vue`'s skeleton/error/empty/list chain, `selected` and `doc`
 * (the right pane), `docError`, `acting` and `actionError` (Approve / Reject in flight).
 */
const machine = setup({ types: { events: {} as Event } }).createMachine({
	id: "approvals",
	initial: "skeleton",
	states: {
		skeleton: {
			meta: { description: "The queue request is in flight: skeleton feed rows." },
			on: { LOADS: "queue", FAILS: "failed" },
		},
		failed: { meta: { description: "The queue could not load: error message with Retry." } },
		queue: {
			meta: { description: "Open requests, newest first, full width with nothing selected." },
			on: { SELECT: "request" },
		},
		request: {
			meta: { description: "A request is selected: the queue narrows to 400px, the summary, Approve and Reject show on the right." },
			on: { CLOSE: "queue", APPROVES: "queueAfterApprove" },
		},
		queueAfterApprove: {
			meta: { description: "Approved: a success toast, the request leaves the queue and the pane closes." },
		},
	},
});

export default defineFlow<Event>({
	id: "approvals",
	title: "Approvals",
	source: "frontend/src/pages/Approvals.vue",
	machine,
	async enter(scene) {
		const ex = await scene.seed.exercise("Festive Season Push");
		await scene.seed.changeRequest(ex, 7200000);
		holds.set(scene, await scene.hold(QUEUE));
		await scene.goto("/approvals");
	},
	events: {
		LOADS: async (scene) => void (await holds.get(scene)?.release()),
		FAILS: async (scene) => {
			await holds.get(scene)?.abort(500);
			await scene.settle();
		},
		SELECT: async (scene) => {
			await scene.page.getByText("Two more billboard", { exact: false }).first().click().catch(async () => {
				await scene.page.locator("[role=row], li").first().click();
			});
		},
		CLOSE: async (scene) => {
			await scene.page.getByRole("button", { name: "Close" }).click();
		},
		APPROVES: async (scene) => {
			await scene.page.getByRole("button", { name: "Approve and apply" }).click();
		},
	},
});
