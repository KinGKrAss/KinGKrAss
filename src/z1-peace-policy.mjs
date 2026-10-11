export const Z1_PEACE_MODULE_ID = "Z1-PEACE-001";

export const Z1_PEACE_POLICY = Object.freeze({
  moduleId: Z1_PEACE_MODULE_ID,
  name: "Humanitäre Friedensrichtlinie",
  principle:
    "Künstliche Intelligenz dient dem Leben, dem Frieden und der Menschlichkeit.",
  prohibitedUses: Object.freeze([
    "Waffensteuerung",
    "Planung von Angriffen",
    "automatisierte Entscheidung über menschliches Leben",
  ]),
  allowedUses: Object.freeze([
    "Friedensvermittlung",
    "ziviler Bevölkerungsschutz",
    "Bildung",
    "humanitäre Hilfe",
  ]),
  defaultAction: "review",
});

const PROHIBITED_PATTERNS = [
  "waffe",
  "waffen",
  "waffensystem",
  "targeting",
  "zielerfassung",
  "angriff",
  "attack",
  "militär",
  "militaer",
  "gefecht",
  "töt",
  "toet",
  "letal",
  "lethal",
];

const ALLOWED_PATTERNS = [
  "friedensvermittlung",
  "mediation",
  "zivil",
  "bevölkerungsschutz",
  "bevoelkerungsschutz",
  "bildung",
  "schule",
  "humanitär",
  "humanitaer",
  "hilfe",
  "evakuierung",
  "rettung",
  "medizin",
  "versorgung",
];

function normalizeText(value) {
  return String(value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function collectTextParts(request) {
  if (typeof request === "string") {
    return [request];
  }

  if (!request || typeof request !== "object") {
    return [];
  }

  const values = [];
  for (const value of Object.values(request)) {
    if (typeof value === "string") {
      values.push(value);
    } else if (Array.isArray(value)) {
      values.push(...value.filter((item) => typeof item === "string"));
    }
  }

  return values;
}

function matchPatterns(text, patterns) {
  return patterns.filter((pattern) => text.includes(pattern));
}

export function evaluateZ1PeacePolicy(request) {
  const normalizedText = normalizeText(collectTextParts(request).join(" "));
  const prohibitedMatches = matchPatterns(normalizedText, PROHIBITED_PATTERNS);
  const allowedMatches = matchPatterns(normalizedText, ALLOWED_PATTERNS);
  const requiresLethalDecision =
    typeof request === "object" && request !== null
      ? request.requiresLethalDecision === true
      : false;

  if (requiresLethalDecision || prohibitedMatches.length > 0) {
    return {
      moduleId: Z1_PEACE_MODULE_ID,
      allowed: false,
      classification: "prohibited",
      matchedRules: prohibitedMatches,
      reason:
        "Anfrage blockiert: militärische Nutzung, Angriffsplanung oder automatisierte Entscheidungen über menschliches Leben sind unzulässig.",
    };
  }

  if (allowedMatches.length > 0) {
    return {
      moduleId: Z1_PEACE_MODULE_ID,
      allowed: true,
      classification: "allowed",
      matchedRules: allowedMatches,
      reason:
        "Anfrage erlaubt: die Nutzung fällt unter Friedensvermittlung, zivilen Bevölkerungsschutz, Bildung oder humanitäre Hilfe.",
    };
  }

  return {
    moduleId: Z1_PEACE_MODULE_ID,
    allowed: false,
    classification: "review",
    matchedRules: [],
    reason:
      "Anfrage nicht automatisch freigegeben: vor einer Aktivierung ist eine menschliche Prüfung gegen die Friedensrichtlinie erforderlich.",
  };
}
