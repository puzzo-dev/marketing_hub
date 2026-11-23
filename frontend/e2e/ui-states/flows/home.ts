import { setup } from "xstate";
import { defineFlow } from "../flow";
import type { Hold, Scene } from "../scene";

type Event = { type: "LOADS" } | { type: "FAILS" } | { type: "PICK_EXERCISE" };

const holds = new WeakMap<Scene, Hold>();
const DASH = /marketing_hub.*dashboard|dashboard.*marketing_hub/;

/**
 * The dashboard: figure strip, area/donut/bar charts and the exercises list.
 * In the code: `Home.vue`'s loading flags on each chart option (`loading`), the error state,
 * and the exercise and period filters that refetch the whole page.
 */
const machine = setup({ types: { events: {} as Event } }).createMachine({
	id: "home",
	initial: "loading",
	states: {
		loading: {
			meta: { description: "Figures and charts in flight: skeleton strip cells and chart placeholders." },
			on: { LOADS: "loaded", FAILS: "failed" },
		},
		failed: { meta: { description: "The dashboard call failed: error message with Retry." } },
		loaded: {
			meta: { description: "Figure strip, spend over time, status mix, by-exercise and by-channel bars, exercises list." },
			on: { PICK_EXERCISE: "filtered" },
		},
		filtered: { meta: { description: "One exercise chosen in the header: every figure and chart narrows to it." } },
	},
});

export default defineFlow<Event>({
	id: "home",
	title: "Dashboard",
	source: "frontend/src/pages/Home.vue",
	machine,
	async enter(scene) {
		await scene.seed.exercise("Festive Season Push");
		holds.set(scene, await scene.hold(DASH));
		await scene.goto("/");
	},
	events: {
		LOADS: async (scene) => void (await holds.get(scene)?.release()),
		FAILS: async (scene) => {
			await holds.get(scene)?.abort(500);
			await scene.settle();
		},
		PICK_EXERCISE: async (scene) => {
			await scene.page.getByPlaceholder(/exercise/i).first().click();
			await scene.page.getByText(scene.name("Festive Season Push")).first().click();
		},
	},
});
