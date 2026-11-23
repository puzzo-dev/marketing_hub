import type { AnyFlow } from "../flow";
import approvals from "./approvals";
import exercises from "./exercises";
import home from "./home";

/** Canvas order. Add a flow here once its machine and browser steps are written. */
export const flows: AnyFlow[] = [home, exercises, approvals];
