import express, { Request, Response } from "express";
import { google } from "@ai-sdk/google";
import { generateText } from "ai";
import { z } from "zod";

const app = express();
app.use(express.json());

const PORT = Number(process.env.Z1_GEMINI_PORT || 8787);
const MODEL_ID = process.env.GEMINI_MODEL || "gemini-2.5-flash";

const EditableRequestSchema = z.object({
  title: z.string().default(""),
  body: z.string().default(""),
  labels: z.array(z.string()).default([]),
  instruction: z
    .string()
    .default("Optimiere Titel und Beschreibung klar und strukturiert für System-Z1."),
});

app.get("/health", (_req: Request, res: Response) => {
  const hasKey = Boolean(process.env.GOOGLE_GENERATIVE_AI_API_KEY);
  res.status(hasKey ? 200 : 500).json({
    status: hasKey ? "online" : "missing_api_key",
    service: "System-Z1 Gemini Bridge",
    model: MODEL_ID,
  });
});

app.post("/api/z1/pr/editable", async (req: Request, res: Response) => {
  try {
    if (!process.env.GOOGLE_GENERATIVE_AI_API_KEY) {
      res.status(500).json({
        status: "error",
        error: "GOOGLE_GENERATIVE_AI_API_KEY ist nicht gesetzt.",
      });
      return;
    }

    const parsed = EditableRequestSchema.parse(req.body);

    const prompt = [
      `Anweisung: ${parsed.instruction}`,
      `Aktueller Titel: ${parsed.title || "(leer)"}`,
      `Aktueller Inhalt: ${parsed.body || "(leer)"}`,
      `Aktuelle Labels: ${parsed.labels.join(", ") || "(keine)"}`,
      "",
      "Antworte ausschließlich als valides JSON-Objekt mit den Feldern:",
      '{"title": "...", "body": "...", "labels": ["..."]}',
    ].join("\n");

    const { text } = await generateText({
      model: google(MODEL_ID),
      system:
        "Du bist das technische PR- und Code-Modul von System-Z1. Liefere präzises, sauberes JSON ohne Markdown-Codeblöcke.",
      prompt,
    });

    const cleaned = text.replace(/^```(?:json)?\s*|\s*```$/g, "").trim();
    const result = JSON.parse(cleaned);

    res.json({
      status: "ok",
      model: MODEL_ID,
      editable: {
        title: result.title ?? parsed.title,
        body: result.body ?? parsed.body,
        labels: Array.isArray(result.labels) ? result.labels : parsed.labels,
      },
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Unbekannter Fehler";
    res.status(500).json({ status: "error", error: message });
  }
});

app.listen(PORT, "127.0.0.1", () => {
  console.log(`System-Z1 Gemini Bridge aktiv auf http://127.0.0.1:${PORT}`);
});
