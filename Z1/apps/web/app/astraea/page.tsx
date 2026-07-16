"use client";

import {
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import { astraea, isAuthenticated, type AuditLog, type AstraeaSummary } from "@/lib/api";

export default function AstraeaPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<AstraeaSummary | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    Promise.all([astraea.summary(), astraea.listAuditLogs()])
      .then(([s, l]) => { setSummary(s); setLogs(l); })
      .finally(() => setLoading(false));
  }, [router]);

  return (
    <AppShell>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        🔒 Astraea – Sicherheit & Audit
      </Typography>

      {loading ? <CircularProgress /> : (
        <>
          {summary && (
            <Grid container spacing={2} sx={{ mb: 3 }}>
              {[
                { label: "Audit-Logs gesamt", value: summary.total_audit_entries },
                { label: "Fehlgeschlagene Aktionen", value: summary.failed_actions },
                { label: "Aktive Berechtigungen", value: summary.active_permissions },
                { label: "Backups gesamt", value: summary.total_backups },
              ].map((s) => (
                <Grid size={{ xs: 6, md: 3 }} key={s.label}>
                  <Card><CardContent>
                    <Typography variant="caption" color="text.secondary">{s.label}</Typography>
                    <Typography variant="h6" fontWeight={600}>{s.value}</Typography>
                  </CardContent></Card>
                </Grid>
              ))}
            </Grid>
          )}

          <Typography variant="h6" sx={{ mb: 1 }}>Audit-Logs (neueste 50)</Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Zeitstempel</TableCell>
                <TableCell>Benutzer</TableCell>
                <TableCell>Aktion</TableCell>
                <TableCell>Ressource</TableCell>
                <TableCell>Ergebnis</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logs.map((l) => (
                <TableRow key={l.id}>
                  <TableCell sx={{ whiteSpace: "nowrap" }}>{new Date(l.timestamp).toLocaleString("de-DE")}</TableCell>
                  <TableCell>{l.user ?? "System"}</TableCell>
                  <TableCell>{l.action}</TableCell>
                  <TableCell>{l.resource ?? "–"}</TableCell>
                  <TableCell>
                    <Chip label={l.success ? "OK" : "Fehler"} color={l.success ? "success" : "error"} size="small" />
                  </TableCell>
                </TableRow>
              ))}
              {logs.length === 0 && (
                <TableRow><TableCell colSpan={5} align="center">Keine Logs vorhanden</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </>
      )}
    </AppShell>
  );
}
