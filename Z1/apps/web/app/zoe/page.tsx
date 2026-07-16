"use client";

import SendIcon from "@mui/icons-material/Send";
import {
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  IconButton,
  InputAdornment,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import { zoe, isAuthenticated, type AgentTask, type ZoeDispatchResponse } from "@/lib/api";

const STATUS_COLOR: Record<string, "default" | "info" | "success" | "error" | "warning"> = {
  todo: "default",
  in_progress: "info",
  done: "success",
  cancelled: "warning",
};

export default function ZoePage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<AgentTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [prompt, setPrompt] = useState("");
  const [dispatching, setDispatching] = useState(false);
  const [lastDispatch, setLastDispatch] = useState<ZoeDispatchResponse | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    zoe.listTasks()
      .then(setTasks)
      .finally(() => setLoading(false));
  }, [router]);

  async function handleDispatch() {
    if (!prompt.trim()) return;
    setDispatching(true);
    try {
      const result = await zoe.dispatch(prompt);
      setLastDispatch(result);
      setPrompt("");
      const updated = await zoe.listTasks();
      setTasks(updated);
    } finally {
      setDispatching(false);
    }
  }

  return (
    <AppShell>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        🧠 Zoë – KI-Orchestrierung
      </Typography>

      {loading ? <CircularProgress /> : (
        <>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Aufgabe an Zoë senden
              </Typography>
              <TextField
                inputRef={inputRef}
                fullWidth
                placeholder='z.B. „Zeige mir alle aktiven Windparks" oder „Erstelle einen Bericht über Ausgaben"'
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleDispatch(); } }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={handleDispatch} disabled={dispatching || !prompt.trim()}>
                        {dispatching ? <CircularProgress size={20} /> : <SendIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              {lastDispatch && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Modul erkannt: <strong>{lastDispatch.routed_to ?? "unbekannt"}</strong>
                  </Typography>
                  <Typography variant="body2">{lastDispatch.response}</Typography>
                </Box>
              )}
            </CardContent>
          </Card>

          <Grid container spacing={2} sx={{ mb: 3 }}>
            {[
              { label: "Aufgaben gesamt", value: tasks.length },
              { label: "Abgeschlossen", value: tasks.filter((t) => t.status === "done").length },
              { label: "Offen", value: tasks.filter((t) => t.status === "todo").length },
            ].map((s) => (
              <Grid size={{ xs: 6, md: 4 }} key={s.label}>
                <Card><CardContent>
                  <Typography variant="caption" color="text.secondary">{s.label}</Typography>
                  <Typography variant="h6" fontWeight={600}>{s.value}</Typography>
                </CardContent></Card>
              </Grid>
            ))}
          </Grid>

          <Typography variant="h6" sx={{ mb: 1 }}>Aufgabenverlauf</Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Aufgabe</TableCell>
                <TableCell>Modul</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Priorität</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tasks.map((t) => (
                <TableRow key={t.id}>
                  <TableCell>{t.title}</TableCell>
                  <TableCell>{t.assigned_module ?? "–"}</TableCell>
                  <TableCell>
                    <Chip label={t.status} color={STATUS_COLOR[t.status] ?? "default"} size="small" />
                  </TableCell>
                  <TableCell>{t.priority}</TableCell>
                </TableRow>
              ))}
              {tasks.length === 0 && (
                <TableRow><TableCell colSpan={4} align="center">Keine Aufgaben vorhanden</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </>
      )}
    </AppShell>
  );
}
