"use client";

import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  MenuItem,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import { themis, isAuthenticated, type LegalContract } from "@/lib/api";

const STATUS_COLOR: Record<string, "success" | "warning" | "error" | "default"> = {
  active: "success",
  expired: "error",
  draft: "default",
  terminated: "warning",
};

const EMPTY_FORM = {
  title: "",
  contract_type: "service",
  counterparty: "",
  start_date: new Date().toISOString().slice(0, 10),
  end_date: "",
  value: "",
};

export default function ThemisPage() {
  const router = useRouter();
  const [contracts, setContracts] = useState<LegalContract[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [snack, setSnack] = useState<{ msg: string; severity: "success" | "error" } | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    themis.listContracts()
      .then(setContracts)
      .finally(() => setLoading(false));
  }, [router]);

  async function handleCreate() {
    try {
      const c = await themis.createContract({
        title: form.title,
        contract_type: form.contract_type,
        counterparty: form.counterparty,
        start_date: form.start_date,
        end_date: form.end_date || undefined,
        value: form.value ? parseFloat(form.value) : undefined,
      });
      setContracts((prev) => [...prev, c]);
      setOpen(false);
      setForm(EMPTY_FORM);
      setSnack({ msg: "Vertrag erstellt.", severity: "success" });
    } catch {
      setSnack({ msg: "Fehler beim Erstellen.", severity: "error" });
    }
  }

  async function handleDelete(id: number) {
    try {
      await themis.deleteContract(id);
      setContracts((prev) => prev.filter((c) => c.id !== id));
      setSnack({ msg: "Vertrag gelöscht.", severity: "success" });
    } catch {
      setSnack({ msg: "Fehler beim Löschen.", severity: "error" });
    }
  }

  const active = contracts.filter((c) => c.status === "active").length;
  const totalValue = contracts.reduce((s, c) => s + (c.value ?? 0), 0);

  return (
    <AppShell>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        ⚖️ Themis – Vertragsmanagement
      </Typography>

      {loading ? <CircularProgress /> : (
        <>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {[
              { label: "Verträge gesamt", value: contracts.length },
              { label: "Aktive Verträge", value: active },
              { label: "Gesamtwert", value: totalValue.toLocaleString("de-DE") + " €" },
            ].map((s) => (
              <Grid size={{ xs: 6, md: 4 }} key={s.label}>
                <Card><CardContent>
                  <Typography variant="caption" color="text.secondary">{s.label}</Typography>
                  <Typography variant="h6" fontWeight={600}>{s.value}</Typography>
                </CardContent></Card>
              </Grid>
            ))}
          </Grid>

          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
            <Typography variant="h6">Verträge</Typography>
            <Button startIcon={<AddIcon />} variant="contained" onClick={() => setOpen(true)}>
              Neuer Vertrag
            </Button>
          </Box>

          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Titel</TableCell>
                <TableCell>Typ</TableCell>
                <TableCell>Vertragspartner</TableCell>
                <TableCell>Beginn</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Wert (€)</TableCell>
                <TableCell align="right">Aktionen</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {contracts.map((c) => (
                <TableRow key={c.id}>
                  <TableCell>{c.title}</TableCell>
                  <TableCell>{c.contract_type}</TableCell>
                  <TableCell>{c.counterparty}</TableCell>
                  <TableCell>{c.start_date ?? "–"}</TableCell>
                  <TableCell>
                    <Chip label={c.status} color={STATUS_COLOR[c.status] ?? "default"} size="small" />
                  </TableCell>
                  <TableCell align="right">{c.value?.toLocaleString("de-DE") ?? "–"}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" color="error" onClick={() => handleDelete(c.id)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {contracts.length === 0 && (
                <TableRow><TableCell colSpan={7} align="center">Keine Verträge vorhanden</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Neuer Vertrag</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "16px !important" }}>
          <TextField label="Titel" value={form.title} onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))} fullWidth />
          <TextField select label="Typ" value={form.contract_type} onChange={(e) => setForm((p) => ({ ...p, contract_type: e.target.value }))} fullWidth>
            {["rental", "energy", "employment", "service", "other"].map((t) => (
              <MenuItem key={t} value={t}>{t}</MenuItem>
            ))}
          </TextField>
          <TextField label="Vertragspartner" value={form.counterparty} onChange={(e) => setForm((p) => ({ ...p, counterparty: e.target.value }))} fullWidth />
          <TextField label="Beginn" type="date" value={form.start_date} onChange={(e) => setForm((p) => ({ ...p, start_date: e.target.value }))} fullWidth InputLabelProps={{ shrink: true }} />
          <TextField label="Ende" type="date" value={form.end_date} onChange={(e) => setForm((p) => ({ ...p, end_date: e.target.value }))} fullWidth InputLabelProps={{ shrink: true }} />
          <TextField label="Wert (€)" type="number" value={form.value} onChange={(e) => setForm((p) => ({ ...p, value: e.target.value }))} fullWidth />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Abbrechen</Button>
          <Button variant="contained" onClick={handleCreate}>Erstellen</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={Boolean(snack)} autoHideDuration={4000} onClose={() => setSnack(null)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}>
        <Alert severity={snack?.severity} onClose={() => setSnack(null)} sx={{ width: "100%" }}>
          {snack?.msg}
        </Alert>
      </Snackbar>
    </AppShell>
  );
}
