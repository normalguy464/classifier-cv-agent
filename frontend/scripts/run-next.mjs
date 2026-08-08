import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { loadRootFrontendEnvironment } from "./load-root-env.mjs";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const nextCli = resolve(scriptDirectory, "..", "node_modules", "next", "dist", "bin", "next");
const child = spawn(process.execPath, [nextCli, ...process.argv.slice(2)], {
  env: loadRootFrontendEnvironment(),
  stdio: "inherit",
});

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.once(signal, () => child.kill(signal));
}

child.once("error", (error) => {
  throw error;
});

const exitCode = await new Promise((resolveExitCode) => {
  child.once("exit", (code) => resolveExitCode(code ?? 1));
});

process.exitCode = exitCode;
