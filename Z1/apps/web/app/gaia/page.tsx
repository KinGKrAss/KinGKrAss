"use client";

import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
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
  MenuItem,
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
import { gaia, isAuthenticated, type GaiaSummary, type Property } from "@/lib/api";

export default function GaiaPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<GaiaSummary | null>(null);
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    name: "",
    address: "",
    city: "",
    property_type: "apartment",
    area_sqm: "",
    purchase_price: "",
    monthly_rent: "",
  });

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    Promise.all([gaia.summary(), gaia.listProperties()])
      .then(([s, p]) => { setSummary(s); setProperties(p); })
      .finally(() => setLoading(false));
  }, [router]);

  async function handleCreate() {
    const prop = await gaia.createProperty({
      name: form.name,
      address: form.address,
      city: form.city,
      property_type: form.property_type,
      area_sqm: parseFloat(form.area_sqm),
      purchase_price: form.purchase_price ? parseFloat(form.purchase_price) : undefined,
      monthly_rent: form.monthly_rent ? parseFloat(form.monthly_rent) : undefined,
    });
    setProperties((prev) => [...prev, prop]);
    const s = await gaia.summary();
    setSummary(s);
    setOpen(false);
    setForm({ name: "", address: "", city: "", property_type: "apartment", area_sqm: "", purchase_price: "", monthly_rent: "" });
  }

  async function handleDelete(id: number) {
    await gaia.deleteProperty(id);
    setProperties((prev) => prev.filter((p) => p.id !== id));
    const s = await gaia.summary();
    setSummary(s);
  }

  return (
    <AppShell>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        🏢 Gaia – Immobilienverwaltung
      </Typography>

      {loading ? <CircularProgress /> : (
        <>
          {summary && (
            <Grid container spacing={2} sx={{ mb: 3 }}>
              {[
                { label: "Objekte gesamt", value: summary.total_properties },
                { label: "Vermietet", value: summary.rented_properties },
                { label: "Verfügbar", value: summary.available_properties },
                { label: "Mieteinnahmen", value: summary.total_rent_income.toLocaleString("de-DE") + " €" },
                { label: "Offene Wartungen", value: summary.open_maintenance_requests },
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
            <Typography variant="h6">Immobilien</Typography>
            <Button startIcon={<AddIcon />} variant="contained" onClick={() => setOpen(true)}>
              Neue Immobilie
            </Button>
          </Box>

          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Adresse</TableCell>
                <TableCell>Stadt</TableCell>
                <TableCell>Typ</TableCell>
                <TableCell>Fläche (m²)</TableCell>
                <TableCell>Miete (€)</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Aktionen</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {properties.map((p) => (
                <TableRow key={p.id}>
                  <TableCell>{p.name}</TableCell>
                  <TableCell>{p.address}</TableCell>
                  <TableCell>{p.city}</TableCell>
                  <TableCell>{p.property_type}</TableCell>
                  <TableCell>{p.area_sqm.toLocaleString("de-DE")}</TableCell>
                  <TableCell>{p.monthly_rent?.toLocaleString("de-DE") ?? "–"}</TableCell>
                  <TableCell>
                    <Chip
                      label={p.status === "rented" ? "Vermietet" : p.status === "maintenance" ? "Wartung" : "Verfügbar"}
                      color={p.status === "rented" ? "success" : p.status === "maintenance" ? "warning" : "default"}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" color="error" onClick={() => handleDelete(p.id)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {properties.length === 0 && (
                <TableRow><TableCell colSpan={8} align="center">Keine Immobilien vorhanden</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Neue Immobilie</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "16px !important" }}>
          <TextField label="Name" value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} fullWidth />
          <TextField label="Adresse" value={form.address} onChange={(e) => setForm((p) => ({ ...p, address: e.target.value }))} fullWidth />
          <TextField label="Stadt" value={form.city} onChange={(e) => setForm((p) => ({ ...p, city: e.target.value }))} fullWidth />
          <TextField select label="Typ" value={form.property_type} onChange={(e) => setForm((p) => ({ ...p, property_type: e.target.value }))} fullWidth>
            {["apartment", "house", "commercial", "land"].map((t) => (
              <MenuItem key={t} value={t}>{t}</MenuItem>
            ))}
          </TextField>
          <TextField label="Fläche (m²)" type="number" value={form.area_sqm} onChange={(e) => setForm((p) => ({ ...p, area_sqm: e.target.value }))} fullWidth />
          <TextField label="Kaufpreis (€)" type="number" value={form.purchase_price} onChange={(e) => setForm((p) => ({ ...p, purchase_price: e.target.value }))} fullWidth />
          <TextField label="Monatsmiete (€)" type="number" value={form.monthly_rent} onChange={(e) => setForm((p) => ({ ...p, monthly_rent: e.target.value }))} fullWidth />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Abbrechen</Button>
          <Button variant="contained" onClick={handleCreate}>Erstellen</Button>
        </DialogActions>
      </Dialog>
    </AppShell>
  );
}
