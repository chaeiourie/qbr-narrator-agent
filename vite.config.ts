import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

// Portable dev config — works on any machine (macOS, Windows, Linux).
// `npm run dev` starts the app on http://localhost:5173/ by default.
// Change `server.port` below if 5173 is already taken on your computer.
export default defineConfig({
  server: { host: true, port: 5173 },
  optimizeDeps: { include: ["react", "react-dom", "react-dom/client", "react-router", "framer-motion", "lucide-react", "react-icons", "clsx", "date-fns", "zod", "@supabase/supabase-js"] },
  plugins: [tailwindcss(), reactRouter()],
  resolve: {
    dedupe: ["react", "react-dom"],
    tsconfigPaths: true,
  },
});
