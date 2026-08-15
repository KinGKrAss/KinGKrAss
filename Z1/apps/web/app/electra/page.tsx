"use client";

import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
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
import { electra, isAuthenticated, type ElectraSummary, type WindFarm } from "@/lib/api";

const STATUS_COLOR: Record<string, "success" | "warning" | "error"> = {
  active: "success",
  maintenance: "warning",
  offline: "error",
};

const EMPTY_FORM = { name: "", location: "", capacity_kw: "", status: "active" };

export default function ElectraPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<ElectraSummary | null>(null);
  const [farms, setFarms] = useState<WindFarm[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<WindFarm | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [snack, setSnack] = useState<{ msg: string; severity: "success" | "error" } | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    Promise.all([electra.summary(), electra.listFarms()])
      .then(([s, f]) => { setSummary(s); setFarms(f); })
      .finally(() => setLoading(false));
  }, [router]);

  function openCreate() {
    setEditTarget(null);
    setForm(EMPTY_FORM);
    setOpen(true);
  }

  function openEdit(farm: WindFarm) {
    setEditTarget(farm);
    setForm({ name: farm.name, location: farm.location, capacity_kw: String(farm.capacity_kw), status: farm.status });
    setOpen(true);
  }

  async function handleSave() {
    try {
      if (editTarget) {
        const updated = await electra.updateFarm(editTarget.id, {
          name: form.name,
          location: form.location,
          capacity_kw: parseFloat(form.capacity_kw),
          status: form.status,
        });
        setFarms((prev) => prev.map((f) => (f.id === editTarget.id ? updated : f)));
        setSnack({ msg: "Windpark aktualisiert.", severity: "success" });
      } else {
        const farm = await electra.createFarm({ name: form.name, location: form.location, capacity_kw: parseFloat(form.capacity_kw) });
        setFarms((prev) => [...prev, farm]);
        setSnack({ msg: "Windpark erstellt.", severity: "success" });
      }
      const s = await electra.summary();
      setSummary(s);
      setOpen(false);
      setForm(EMPTY_FORM);
    } catch {
      setSnack({ msg: "Fehler beim Speichern.", severity: "error" });
    }
  }

  async function handleDelete(id: number) {
    try {
      await electra.deleteFarm(id);
      setFarms((prev) => prev.filter((f) => f.id !== id));
      const s = await electra.summary();
      setSummary(s);
      setSnack({ msg: "Windpark gelöscht.", severity: "success" });
    } catch {
      setSnack({ msg: "Fehler beim Löschen.", severity: "error" });
    }
  }

  return (
    <AppShell>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        ⚡ Electra – Energiemanagement
      </Typography>

      {loading ? <CircularProgress /> : (
        <>
          {summary && (
            <Grid container spacing={2} sx={{ mb: 3 }}>
              {[
                { label: "Windparks gesamt", value: summary.total_farms },
                { label: "Aktive Windparks", value: summary.active_farms },
                { label: "Kapazität (kW)", value: summary.total_capacity_kw.toLocaleString("de-DE") },
                { label: "Produktion (kWh)", value: summary.total_production_kwh.toLocaleString("de-DE") },
                { label: "Aktive Verträge", value: summary.active_contracts },
                { label: "Geschätzter Umsatz", value: summary.estimated_revenue_eur.toLocaleString("de-DE") + " €" },
              ].map((s) => (
                <Grid size={{ xs: 6, md: 4, lg: 2 }} key={s.label}>
                  <Card><CardContent>
                    <Typography variant="caption" color="text.secondary">{s.label}</Typography>
                    <Typography variant="h6" fontWeight={600}>{s.value}</Typography>
                  </CardContent></Card>
                </Grid>
              ))}
            </Grid>
          )}

          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
            <Typography variant="h6">Windparks</Typography>
            <Button startIcon={<AddIcon />} variant="contained" onClick={openCreate}>
              Neuer Windpark
            </Button>
          </Box>

          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Standort</TableCell>
                <TableCell>Kapazität (kW)</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Aktionen</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {farms.map((f) => (
                <TableRow key={f.id}>
                  <TableCell>{f.name}</TableCell>
                  <TableCell>{f.location}</TableCell>
                  <TableCell>{f.capacity_kw.toLocaleString("de-DE")}</TableCell>
                  <TableCell>
                    <Chip label={f.status} color={STATUS_COLOR[f.status] ?? "default"} size="small" />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" color="primary" onClick={() => openEdit(f)}>
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(f.id)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {farms.length === 0 && (
                <TableRow><TableCell colSpan={5} align="center">Keine Windparks vorhanden</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editTarget ? "Windpark bearbeiten" : "Neuer Windpark"}</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "16px !important" }}>
          <TextField label="Name" value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} fullWidth />
          <TextField label="Standort" value={form.location} onChange={(e) => setForm((p) => ({ ...p, location: e.target.value }))} fullWidth />
          <TextField label="Kapazität (kW)" type="number" value={form.capacity_kw} onChange={(e) => setForm((p) => ({ ...p, capacity_kw: e.target.value }))} fullWidth />
          {editTarget && (
            <TextField select label="Status" value={form.status} onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))} fullWidth>
              {["active", "maintenance", "offline"].map((s) => (
                <MenuItem key={s} value={s}>{s}</MenuItem>
              ))}
            </TextField>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Abbrechen</Button>
          <Button variant="contained" onClick={handleSave}>{editTarget ? "Speichern" : "Erstellen"}</Button>
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
