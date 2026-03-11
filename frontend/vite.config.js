import path from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import Icons from "unplugin-icons/vite";

export default defineConfig({
  base: "/assets/marketing_hub/frontend/",
  plugins: [
    vue(),
    Icons({
      compiler: "vue3",
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  build: {
    outDir: `../${path.basename(path.resolve(".."))}/public/frontend`,
    emptyOutDir: true,
    target: "es2015",
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          if (id.includes("node_modules")) {
            if (id.includes("frappe-ui")) {
              return "frappe-ui";
            }
            return "vendor";
          }
        },
      },
    },
  },
  optimizeDeps: {
    include: ["feather-icons", "showdown", "engine.io-client"],
  },
});
