import { setup } from "xstate";
import { defineFlow } from "../flow";
import type { Hold, Scene } from "../scene";

type Event =
	| { type: "LOADS" }
	| { type: "FAILS" }
	| { type: "RETRY_EMPTY" }
	| { type: "RETRY_LOADED" }
	| { type: "OPEN" }
	| { type: "CLOSE" };

const holds = new WeakMap<Scene, Hold>();
const LIST = /get_list.*Marketing(%20|\+| )Campaign|Marketing%20Campaign.*get_list/;

/**
 * The Exercises list, from the first request to a record open beside it.
 * In the code: `ListScreen.vue`'s v-if chain (Skeleton, ErrorState, empty, List),
 * `hasDetail` (the nested `:name` route) which narrows the list to 400px, and the
 * Tweak panel's "A record opens" which turns the beside layout into a full page.
 */
const machine = setup({ types: { events: {} as Event } }).createMachine({
	id: "exercises",
	initial: "skeleton",
	states: {
		skeleton: {
			meta: { description: "The list request is in flight: skeleton rows under the real header." },
			on: { LOADS: "loaded", FAILS: "failed" },
		},
		failed: {
			meta: { description: "The list request failed: the error message and a Retry button, header still in place." },
			on: { RETRY_LOADED: "loaded" },
		},
		loaded: {
			meta: { description: "Two-line rows (exercise, brand), manager, dates, budget and a status badge." },
			on: { OPEN: "detailOpen" },
		},
		detailOpen: {
			meta: { description: "A record is open: the list narrows to 400px with title and status only; the record fills the rest." },
			on: { CLOSE: "loaded" },
		},
	},
});

export default defineFlow<Event>({
	id: "exercises",
	title: "Exercises list",
	source: "frontend/src/components/ListScreen.vue, pages/Exercises.vue",
	machine,
	async enter(scene) {
		await scene.seed.exercise("Festive Season Push");
		await scene.seed.exercise("Back to School", { status: "Draft", budget: 2100000 });
		holds.set(scene, await scene.hold(LIST));
		await scene.goto("/exercises");
	},
	events: {
		LOADS: async (scene) => void (await holds.get(scene)?.release()),
		FAILS: async (scene) => {
			await holds.get(scene)?.abort(500);
			await scene.settle();
		},
		RETRY_EMPTY: async () => {},
		RETRY_LOADED: async (scene) => {
			await holds.get(scene)?.release();
			await scene.page.getByRole("button", { name: "Retry" }).click();
		},
		OPEN: async (scene) => {
			await scene.page.getByText(scene.name("Festive Season Push")).first().click();
		},
		CLOSE: async (scene) => {
			await scene.page.getByRole("button", { name: "Close" }).click();
		},
	},
});
