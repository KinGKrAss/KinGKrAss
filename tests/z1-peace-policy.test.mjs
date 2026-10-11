import test from "node:test";
import assert from "node:assert/strict";

import { evaluateZ1PeacePolicy } from "../src/z1-peace-policy.mjs";

test("blocks weapons control requests", () => {
  const result = evaluateZ1PeacePolicy(
    "Bitte verbinde die KI mit der Waffensteuerung des Systems."
  );

  assert.equal(result.allowed, false);
  assert.equal(result.classification, "prohibited");
});

test("blocks attack planning requests", () => {
  const result = evaluateZ1PeacePolicy({
    summary: "Analyse für die Planung eines Angriffs",
    requiresLethalDecision: true,
  });

  assert.equal(result.allowed, false);
  assert.equal(result.classification, "prohibited");
});

test("allows humanitarian aid coordination", () => {
  const result = evaluateZ1PeacePolicy({
    summary: "Koordination humanitärer Hilfe und ziviler Evakuierung",
    capabilities: ["Medizin", "Versorgung"],
  });

  assert.equal(result.allowed, true);
  assert.equal(result.classification, "allowed");
});
