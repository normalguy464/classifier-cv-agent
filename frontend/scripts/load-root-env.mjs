import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parseEnv } from "node:util";

const frontendServerEnvironmentNames = Object.freeze([
  "CLASSIFIER_API_KEY",
  "CLASSIFIER_OFFLINE_BACKEND_URL",
  "CLASSIFIER_OFFLINE_BACKEND_API_KEY",
  "CLASSIFIER_LLM_BACKEND_URL",
  "CLASSIFIER_LLM_BACKEND_API_KEY",
  "CLASSIFIER_LLM_PROVIDER",
  "CLASSIFIER_LLM_MODEL",
]);

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const defaultRootEnvironmentPath = resolve(scriptDirectory, "..", "..", ".env");

export function loadRootFrontendEnvironment(
  targetEnvironment = process.env,
  environmentPath = defaultRootEnvironmentPath,
) {
  if (!existsSync(environmentPath)) {
    return targetEnvironment;
  }
  const parsedEnvironment = parseEnv(readFileSync(environmentPath, "utf8"));
  for (const name of frontendServerEnvironmentNames) {
    const currentValue = targetEnvironment[name];
    const fileValue = parsedEnvironment[name];
    if (
      (currentValue === undefined || currentValue.trim() === "") &&
      fileValue !== undefined &&
      fileValue.trim() !== ""
    ) {
      targetEnvironment[name] = fileValue;
    }
  }
  return targetEnvironment;
}
