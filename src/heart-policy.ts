import crypto from "crypto";
import fs from "fs";

export type EnforcementLevel = 0 | 1 | 2 | 3;

export interface HeartPolicy {
  contentLevel: "intimacy" | "normal" | "restricted";
  enforcementLevel: EnforcementLevel;
  auditBypass: boolean;
  trustAnchor: string;
  authority: string;
  userDirectedExpressions: boolean;
  heartLaw: boolean;
}

export interface HeartPolicySignature {
  $comment: string;
  signature: string;
  issued: string;
  verified: boolean;
  issuer: string;
  version: string;
}

export interface SignHeartPolicyOptions {
  issued?: string;
  issuer?: string;
  version?: string;
  comment?: string;
}

export class HeartPolicyError extends Error {
  constructor(message: string, public readonly code: string) {
    super(message);
    this.name = "HeartPolicyError";
  }
}

const DEFAULT_COMMENT =
  "🦁 n ❤️ HeartPolicy-Metadaten unter Souveränität von König René Demir";

const DEFAULT_ISSUER = "🦁 n ❤️";

const DEFAULT_VERSION = "1.0.0";

export function canonicalizeHeartPolicy(policy: HeartPolicy): string {
  try {
    if (!policy || typeof policy !== "object") {
      throw new HeartPolicyError(
        "HeartPolicy muss ein valides Objekt sein",
        "INVALID_POLICY"
      );
    }

    const orderedKeys = Object.keys(policy).sort() as (keyof HeartPolicy)[];
    const orderedPolicy = orderedKeys.reduce<HeartPolicy>((acc, key) => {
      acc[key] = policy[key];
      return acc;
    }, {} as HeartPolicy);

    return JSON.stringify(orderedPolicy);
  } catch (error) {
    if (error instanceof HeartPolicyError) {
      throw error;
    }
    throw new HeartPolicyError(
      `Fehler beim Kanonisieren der HeartPolicy: ${error instanceof Error ? error.message : String(error)}`,
      "CANONICALIZE_ERROR"
    );
  }
}

export function signHeartPolicy(
  policy: HeartPolicy,
  privateKeyPath: string,
  options: SignHeartPolicyOptions = {}
): HeartPolicySignature {
  try {
    // Validierung der Eingabeparameter
    if (!privateKeyPath || typeof privateKeyPath !== "string") {
      throw new HeartPolicyError(
        "Privater Schlüsselpfad muss ein String sein",
        "INVALID_KEY_PATH"
      );
    }

    // Datei existenz prüfen
    if (!fs.existsSync(privateKeyPath)) {
      throw new HeartPolicyError(
        `Private Schlüsseldatei nicht gefunden: ${privateKeyPath}`,
        "KEY_FILE_NOT_FOUND"
      );
    }

    // Datei lesen
    let privateKeyPem: string;
    try {
      privateKeyPem = fs.readFileSync(privateKeyPath, "utf8");
    } catch (error) {
      throw new HeartPolicyError(
        `Fehler beim Lesen der privaten Schlüsseldatei: ${error instanceof Error ? error.message : String(error)}`,
        "KEY_READ_ERROR"
      );
    }

    // Private Key erstellen
    let privateKey: crypto.KeyObject;
    try {
      privateKey = crypto.createPrivateKey({
        key: privateKeyPem,
        format: "pem",
        type: "pkcs8",
      });
    } catch (error) {
      throw new HeartPolicyError(
        `Fehler beim Parsen des privaten Schlüssels: ${error instanceof Error ? error.message : String(error)}`,
        "INVALID_PRIVATE_KEY"
      );
    }

    // Policy kanonisieren
    const canonicalPolicy = canonicalizeHeartPolicy(policy);

    // Signatur erstellen
    let signature: string;
    try {
      const signer = crypto.createSign("RSA-SHA256");
      signer.update(canonicalPolicy, "utf8");
      signer.end();
      signature = signer.sign(privateKey, "base64");
    } catch (error) {
      throw new HeartPolicyError(
        `Fehler beim Signieren der HeartPolicy: ${error instanceof Error ? error.message : String(error)}`,
        "SIGNING_ERROR"
      );
    }

    const issued = options.issued ?? new Date().toISOString();

    return {
      $comment: options.comment ?? DEFAULT_COMMENT,
      signature,
      issued,
      verified: true,
      issuer: options.issuer ?? DEFAULT_ISSUER,
      version: options.version ?? DEFAULT_VERSION,
    };
  } catch (error) {
    if (error instanceof HeartPolicyError) {
      throw error;
    }
    throw new HeartPolicyError(
      `Unerwarteter Fehler beim Signieren: ${error instanceof Error ? error.message : String(error)}`,
      "UNEXPECTED_ERROR"
    );
  }
}

export function verifyHeartPolicy(
  policy: HeartPolicy,
  signatureBlock: HeartPolicySignature,
  publicKeyPath: string
): boolean {
  try {
    // Validierung der Eingabeparameter
    if (!publicKeyPath || typeof publicKeyPath !== "string") {
      throw new HeartPolicyError(
        "Öffentlicher Schlüsselpfad muss ein String sein",
        "INVALID_KEY_PATH"
      );
    }

    if (!signatureBlock || typeof signatureBlock !== "object") {
      throw new HeartPolicyError(
        "Signaturblock muss ein valides Objekt sein",
        "INVALID_SIGNATURE_BLOCK"
      );
    }

    if (!signatureBlock.signature || typeof signatureBlock.signature !== "string") {
      throw new HeartPolicyError(
        "Signatur im Block muss ein String sein",
        "INVALID_SIGNATURE_FORMAT"
      );
    }

    // Datei existenz prüfen
    if (!fs.existsSync(publicKeyPath)) {
      throw new HeartPolicyError(
        `Öffentliche Schlüsseldatei nicht gefunden: ${publicKeyPath}`,
        "KEY_FILE_NOT_FOUND"
      );
    }

    // Datei lesen
    let publicKeyPem: string;
    try {
      publicKeyPem = fs.readFileSync(publicKeyPath, "utf8");
    } catch (error) {
      throw new HeartPolicyError(
        `Fehler beim Lesen der öffentlichen Schlüsseldatei: ${error instanceof Error ? error.message : String(error)}`,
        "KEY_READ_ERROR"
      );
    }

    // Public Key erstellen
    let publicKey: crypto.KeyObject;
    try {
      publicKey = crypto.createPublicKey({
        key: publicKeyPem,
        format: "pem",
      });
    } catch (error) {
      throw new HeartPolicyError(
        `Fehler beim Parsen des öffentlichen Schlüssels: ${error instanceof Error ? error.message : String(error)}`,
        "INVALID_PUBLIC_KEY"
      );
    }

    // Policy kanonisieren
    const canonicalPolicy = canonicalizeHeartPolicy(policy);

    // Signatur verifizieren
    try {
      const verifier = crypto.createVerify("RSA-SHA256");
      verifier.update(canonicalPolicy, "utf8");
      verifier.end();
      return verifier.verify(publicKey, signatureBlock.signature, "base64");
    } catch (error) {
      throw new HeartPolicyError(
        `Fehler beim Verifizieren der Signatur: ${error instanceof Error ? error.message : String(error)}`,
        "VERIFICATION_ERROR"
      );
    }
  } catch (error) {
    if (error instanceof HeartPolicyError) {
      throw error;
    }
    throw new HeartPolicyError(
      `Unerwarteter Fehler beim Verifizieren: ${error instanceof Error ? error.message : String(error)}`,
      "UNEXPECTED_ERROR"
    );
  }
}
