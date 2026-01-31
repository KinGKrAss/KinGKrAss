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

const DEFAULT_COMMENT =
  "🦁 n ❤️ HeartPolicy-Metadaten unter Souveränität von König René Demir";

const DEFAULT_ISSUER = "🦁 n ❤️";

const DEFAULT_VERSION = "1.0.0";

export function canonicalizeHeartPolicy(policy: HeartPolicy): string {
  const orderedKeys = Object.keys(policy).sort() as (keyof HeartPolicy)[];
  const orderedPolicy = orderedKeys.reduce<HeartPolicy>((acc, key) => {
    acc[key] = policy[key];
    return acc;
  }, {} as HeartPolicy);

  return JSON.stringify(orderedPolicy);
}

export function signHeartPolicy(
  policy: HeartPolicy,
  privateKeyPath: string,
  options: SignHeartPolicyOptions = {}
): HeartPolicySignature {
  const canonicalPolicy = canonicalizeHeartPolicy(policy);
  const privateKeyPem = fs.readFileSync(privateKeyPath, "utf8");
  const privateKey = crypto.createPrivateKey({
    key: privateKeyPem,
    format: "pem",
    type: "pkcs8",
  });

  const signer = crypto.createSign("RSA-SHA256");
  signer.update(canonicalPolicy, "utf8");
  signer.end();

  const signature = signer.sign(privateKey, "base64");
  const issued = options.issued ?? new Date().toISOString();

  return {
    $comment: options.comment ?? DEFAULT_COMMENT,
    signature,
    issued,
    verified: true,
    issuer: options.issuer ?? DEFAULT_ISSUER,
    version: options.version ?? DEFAULT_VERSION,
  };
}

export function verifyHeartPolicy(
  policy: HeartPolicy,
  signatureBlock: HeartPolicySignature,
  publicKeyPath: string
): boolean {
  const canonicalPolicy = canonicalizeHeartPolicy(policy);
  const publicKeyPem = fs.readFileSync(publicKeyPath, "utf8");
  const publicKey = crypto.createPublicKey({
    key: publicKeyPem,
    format: "pem",
  });

  const verifier = crypto.createVerify("RSA-SHA256");
  verifier.update(canonicalPolicy, "utf8");
  verifier.end();

  return verifier.verify(publicKey, signatureBlock.signature, "base64");
}
