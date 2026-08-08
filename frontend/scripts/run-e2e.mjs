import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { resolve } from "node:path";

import next from "next";

const hostname = "127.0.0.1";
const port = 3000;
const application = next({ dev: false, dir: process.cwd(), hostname, port });
const handler = application.getRequestHandler();

await application.prepare();

const server = createServer((request, response) => handler(request, response));

await new Promise((resolveListening, rejectListening) => {
  server.once("error", rejectListening);
  server.listen(port, hostname, resolveListening);
});

const playwrightCli = resolve("node_modules", "@playwright", "test", "cli.js");
const testProcess = spawn(process.execPath, [playwrightCli, "test"], {
  env: process.env,
  stdio: "inherit",
});

const exitCode = await new Promise((resolveExit, rejectExit) => {
  testProcess.once("error", rejectExit);
  testProcess.once("exit", (code) => resolveExit(code ?? 1));
});

server.closeAllConnections();
await new Promise((resolveClosed) => server.close(resolveClosed));

if (typeof application.close === "function") {
  await application.close();
}

process.exitCode = exitCode;
