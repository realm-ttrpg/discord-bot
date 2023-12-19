import { resolve } from "path";
import { defineConfig } from "vite";

export default defineConfig({
	build: {
		emptyOutDir: true,
		outDir: resolve(__dirname, "..", "..", "html"),
		rollupOptions: {
			input: {
				index: resolve(__dirname, "index.html"),
			},
		},
		target: "esnext",
	},
});
