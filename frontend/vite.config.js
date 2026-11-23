import path from "path"
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"

// The page that mounts this app is marketing_hub/www/marketing/index.html. It is a
// Jinja template that lists the built assets, so the build plugin is left off and
// the output path is set here.
export default defineConfig({
  base: "/assets/marketing_hub/frontend/",
  plugins: [frappeui({ frontendRoute: "/marketing", buildConfig: false, jinjaBootData: false }), vue()],
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  build: {
    outDir: `../${path.basename(path.resolve(".."))}/public/frontend`,
    emptyOutDir: true,
    manifest: true,
  },
})
