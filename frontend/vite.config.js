import path from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import Icons from "unplugin-icons/vite";
import fs from "fs";

// Copy frappe-ui Inter font files so Frappe can serve them at /assets/
function copyFontsPlugin() {
  return {
    name: "copy-frappe-ui-fonts",
    writeBundle() {
      const publicDir = path.resolve(__dirname, `../${path.basename(path.resolve(".."))}/public`);
      const fontsDir = path.resolve(__dirname, "node_modules/frappe-ui/src/fonts/Inter");
      const fontMap = {
        "Inter.var.woff2": "Inter.var.C9xDBOS3.woff2",
        "Inter-Italic.var.woff2": "Inter-Italic.var.BGHziHgI.woff2",
      };
      for (const [src, dest] of Object.entries(fontMap)) {
        const srcPath = path.join(fontsDir, src);
        const destPath = path.join(publicDir, dest);
        if (fs.existsSync(srcPath)) {
          fs.copyFileSync(srcPath, destPath);
        }
      }
    },
  };
}

export default defineConfig({
  base: "/assets/marketing_hub/frontend/",
  plugins: [
    vue(),
    Icons({
      compiler: "vue3",
    }),
    copyFontsPlugin(),
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
