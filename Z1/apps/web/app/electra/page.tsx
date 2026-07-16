"use client";

import AddIcon from "@mui/icons-material/Add";
import {
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import { electra, isAuthenticated, type ElectraSummary, type WindFarm } from "@/lib/api";

const STATUS_COLOR: Record<string, "success" | "warning" | "error"> = {
  active: "success",
  maintenance: "warning",
  offline: "error",
};

export default function ElectraPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<ElectraSummary | null>(null);
  const [farms, setFarms] = useState<WindFarm[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", location: "", capacity_kw: "" });

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    Promise.all([electra.summary(), electra.listFarms()])
      .then(([s, f]) => { setSummary(s); setFarms(f); })
      .finally(() => setLoading(false));
  }, [router]);

  async function handleCreate() {
    const farm = await electra.createFarm({
      name: form.name,
      location: form.location,
      capacity_kw: parseFloat(form.capacity_kw),
    });
    setFarms((prev) => [...prev, farm]);
    const s = await electra.summary();
    setSummary(s);
    setOpen(false);
    setForm({ name: "", location: "", capacity_kw: "" });
  }

  async function handleDelete(id: number) {
    await electra.deleteFarm(id);
    setFarms((prev) => prev.filter((f) => f.id !== id));
    const s = await electra.summary();
    setSummary(s);
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
            <Button startIcon={<AddIcon />} variant="contained" onClick={() => setOpen(true)}>
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
        <DialogTitle>Neuer Windpark</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "16px !important" }}>
          <TextField label="Name" value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} fullWidth />
          <TextField label="Standort" value={form.location} onChange={(e) => setForm((p) => ({ ...p, location: e.target.value }))} fullWidth />
          <TextField label="Kapazität (kW)" type="number" value={form.capacity_kw} onChange={(e) => setForm((p) => ({ ...p, capacity_kw: e.target.value }))} fullWidth />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Abbrechen</Button>
          <Button variant="contained" onClick={handleCreate}>Erstellen</Button>
        </DialogActions>
      </Dialog>
    </AppShell>
  );
}
