import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { loadRootFrontendEnvironment } from "./load-root-env.mjs";

const temporaryDirectories = [];

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { force: true, recursive: true });
  }
});

function environmentFile(contents) {
  const directory = mkdtempSync(join(tmpdir(), "classifier-frontend-env-"));
  temporaryDirectories.push(directory);
  const path = join(directory, ".env");
  writeFileSync(path, contents, "utf8");
  return path;
}

describe("loadRootFrontendEnvironment", () => {
  it("loads only frontend server values and excludes the provider secret", () => {
    const path = environmentFile(
      [
        "CLASSIFIER_API_KEY=backend-auth-key",
        "CLASSIFIER_LLM_BACKEND_URL=http://127.0.0.1:8001",
        "CLASSIFIER_LLM_PROVIDER=openai",
        "CLASSIFIER_LLM_MODEL=gpt-test-model",
        "CLASSIFIER_LLM_API_KEY=paid-provider-secret",
      ].join("\n"),
    );
    const target = {};

    loadRootFrontendEnvironment(target, path);

    expect(target.CLASSIFIER_API_KEY).toBe("backend-auth-key");
    expect(target.CLASSIFIER_LLM_BACKEND_URL).toBe("http://127.0.0.1:8001");
    expect(target.CLASSIFIER_LLM_PROVIDER).toBe("openai");
    expect(target.CLASSIFIER_LLM_MODEL).toBe("gpt-test-model");
    expect(target.CLASSIFIER_LLM_API_KEY).toBeUndefined();
  });

  it("keeps an existing process value instead of replacing it from dotenv", () => {
    const path = environmentFile("CLASSIFIER_API_KEY=dotenv-key\n");
    const target = { CLASSIFIER_API_KEY: "process-key" };

    loadRootFrontendEnvironment(target, path);

    expect(target.CLASSIFIER_API_KEY).toBe("process-key");
  });

  it("allows the root dotenv file to be absent", () => {
    const target = { CLASSIFIER_API_KEY: "process-key" };

    expect(loadRootFrontendEnvironment(target, "missing.env")).toBe(target);
  });
});
