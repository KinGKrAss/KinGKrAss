"use client";

import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
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
import { diplomatia, isAuthenticated, type DiplomaticDocument } from "@/lib/api";

const EMPTY_FORM = { title: "", document_type: "memo", language: "de", content: "", tags: "" };

export default function DiplomatiaPage() {
  const router = useRouter();
  const [docs, setDocs] = useState<DiplomaticDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [snack, setSnack] = useState<{ msg: string; severity: "success" | "error" } | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    diplomatia.listDocuments()
      .then(setDocs)
      .finally(() => setLoading(false));
  }, [router]);

  async function handleCreate() {
    try {
      const doc = await diplomatia.createDocument({
        title: form.title,
        document_type: form.document_type,
        language: form.language,
        content: form.content,
        tags: form.tags || undefined,
      });
      setDocs((prev) => [...prev, doc]);
      setOpen(false);
      setForm(EMPTY_FORM);
      setSnack({ msg: "Dokument erstellt.", severity: "success" });
    } catch {
      setSnack({ msg: "Fehler beim Erstellen.", severity: "error" });
    }
  }

  async function handleDelete(id: number) {
    try {
      await diplomatia.deleteDocument(id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
      setSnack({ msg: "Dokument gelöscht.", severity: "success" });
    } catch {
      setSnack({ msg: "Fehler beim Löschen.", severity: "error" });
    }
  }

  async function handleArchive(id: number) {
    try {
      const updated = await diplomatia.archiveDocument(id);
      setDocs((prev) => prev.map((d) => (d.id === id ? updated : d)));
      setSnack({ msg: "Dokument archiviert.", severity: "success" });
    } catch {
      setSnack({ msg: "Fehler beim Archivieren.", severity: "error" });
    }
  }

  return (
    <AppShell>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        🌐 Diplomatia – Diplomatische Dokumente
      </Typography>

      {loading ? <CircularProgress /> : (
        <>
          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
            <Typography variant="h6">Dokumente ({docs.length})</Typography>
            <Button startIcon={<AddIcon />} variant="contained" onClick={() => setOpen(true)}>
              Neues Dokument
            </Button>
          </Box>

          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Titel</TableCell>
                <TableCell>Typ</TableCell>
                <TableCell>Sprache</TableCell>
                <TableCell>Tags</TableCell>
                <TableCell>Archiviert</TableCell>
                <TableCell align="right">Aktionen</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {docs.map((d) => (
                <TableRow key={d.id}>
                  <TableCell>{d.title}</TableCell>
                  <TableCell>{d.document_type}</TableCell>
                  <TableCell>{d.language}</TableCell>
                  <TableCell>{d.tags ?? "–"}</TableCell>
                  <TableCell>
                    <Chip label={d.is_archived ? "Ja" : "Nein"} color={d.is_archived ? "warning" : "default"} size="small" />
                  </TableCell>
                  <TableCell align="right">
                    {!d.is_archived && (
                      <Button size="small" onClick={() => handleArchive(d.id)} sx={{ mr: 1 }}>
                        Archivieren
                      </Button>
                    )}
                    <IconButton size="small" color="error" onClick={() => handleDelete(d.id)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {docs.length === 0 && (
                <TableRow><TableCell colSpan={6} align="center">Keine Dokumente vorhanden</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Neues Dokument</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: "16px !important" }}>
          <TextField label="Titel" value={form.title} onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))} fullWidth />
          <TextField select label="Typ" value={form.document_type} onChange={(e) => setForm((p) => ({ ...p, document_type: e.target.value }))} fullWidth>
            {["memo", "treaty", "letter", "report", "note", "directive"].map((t) => (
              <MenuItem key={t} value={t}>{t}</MenuItem>
            ))}
          </TextField>
          <TextField label="Sprache (ISO)" value={form.language} onChange={(e) => setForm((p) => ({ ...p, language: e.target.value }))} fullWidth />
          <TextField label="Tags" value={form.tags} onChange={(e) => setForm((p) => ({ ...p, tags: e.target.value }))} fullWidth />
          <TextField label="Inhalt" multiline rows={3} value={form.content} onChange={(e) => setForm((p) => ({ ...p, content: e.target.value }))} fullWidth />
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
