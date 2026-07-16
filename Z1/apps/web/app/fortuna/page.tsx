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
import { fortuna, isAuthenticated, type Transaction } from "@/lib/api";

export default function FortunaPage() {
  const router = useRouter();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    description: "",
    amount: "",
    transaction_type: "income",
    transaction_date: new Date().toISOString().slice(0, 10),
  });

  const income = transactions.filter((t) => t.transaction_type === "income").reduce((s, t) => s + t.amount, 0);
  const expense = transactions.filter((t) => t.transaction_type === "expense").reduce((s, t) => s + t.amount, 0);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    fortuna.listTransactions()
      .then(setTransactions)
      .finally(() => setLoading(false));
  }, [router]);

  async function handleCreate() {
    const t = await fortuna.createTransaction({
      description: form.description,
      amount: parseFloat(form.amount),
      transaction_type: form.transaction_type as "income" | "expense",
      transaction_date: form.transaction_date,
    });
    setTransactions((prev) => [...prev, t]);
    setOpen(false);
  }

  async function handleDelete(id: number) {
    await fortuna.deleteTransaction(id);
    setTransactions((prev) => prev.filter((t) => t.id !== id));
  }

  return (
    <AppShell>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        💰 Fortuna – Finanzverwaltung
      </Typography>

      {loading ? <CircularProgress /> : (
        <>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {[
              { label: "Einnahmen", value: income.toLocaleString("de-DE") + " €" },
              { label: "Ausgaben", value: expense.toLocaleString("de-DE") + " €" },
              { label: "Cashflow", value: (income - expense).toLocaleString("de-DE") + " €" },
              { label: "Buchungen", value: transactions.length },
            ].map((s) => (
              <Grid size={{ xs: 6, md: 3 }} key={s.label}>
                <Card><CardContent>
                  <Typography variant="caption" color="text.secondary">{s.label}</Typography>
                  <Typography variant="h6" fontWeight={600}>{s.value}</Typography>
                </CardContent></Card>
              </Grid>
            ))}
          </Grid>

          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
            <Typography variant="h6">Buchungen</Typography>
            <Button startIcon={<AddIcon />} variant="contained" onClick={() => setOpen(true)}>
              Neue Buchung
            </Button>
          </Box>

          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Datum</TableCell>
                <TableCell>Beschreibung</TableCell>
                <TableCell>Typ</TableCell>
                <TableCell align="right">Betrag (€)</TableCell>
                <TableCell align="right">Aktionen</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transactions.map((t) => (
                <TableRow key={t.id}>
                  <TableCell>{t.transaction_date}</TableCell>
                  <TableCell>{t.description}</TableCell>
                  <TableCell>
                    <Chip
                      label={t.transaction_type === "income" ? "Einnahme" : "Ausgabe"}
                      color={t.transaction_type === "income" ? "success" : "error"}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">{t.amount.toLocaleString("de-DE")}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" color="error" onClick={() => handleDelete(t.id)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {transactions.length === 0 && (
                <TableRow><TableCell colSpan={5} align="center">Keine Buchungen vorhanden</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Neue Buchung</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "16px !important" }}>
          <TextField label="Beschreibung" value={form.description} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))} fullWidth />
          <TextField label="Betrag (€)" type="number" value={form.amount} onChange={(e) => setForm((p) => ({ ...p, amount: e.target.value }))} fullWidth />
          <TextField
            select label="Typ"
            value={form.transaction_type}
            onChange={(e) => setForm((p) => ({ ...p, transaction_type: e.target.value }))}
            fullWidth
          >
            <MenuItem value="income">Einnahme</MenuItem>
            <MenuItem value="expense">Ausgabe</MenuItem>
          </TextField>
          <TextField label="Datum" type="date" value={form.transaction_date} onChange={(e) => setForm((p) => ({ ...p, transaction_date: e.target.value }))} fullWidth InputLabelProps={{ shrink: true }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Abbrechen</Button>
          <Button variant="contained" onClick={handleCreate}>Erstellen</Button>
        </DialogActions>
      </Dialog>
    </AppShell>
  );
}
