"use client";

import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Typography,
} from "@mui/material";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import { getDashboardSummary, isAuthenticated } from "@/lib/api";

function formatNumber(n: unknown, suffix = ""): string {
  if (typeof n !== "number") return "–";
  return n.toLocaleString("de-DE") + (suffix ? " " + suffix : "");
}

export default function HomePage() {
  const router = useRouter();
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    getDashboardSummary()
      .then(setSummary)
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  const re = (summary?.real_estate_overview as Record<string, number> | undefined) ?? {};
  const wp = (summary?.windpark_overview as Record<string, number> | undefined) ?? {};
  const fi = (summary?.finance as Record<string, number> | undefined) ?? {};

  const cards = [
    { title: "Immobilien", value: formatNumber(re.objects) },
    { title: "Mieteinnahmen", value: formatNumber(re.rent_income, "€") },
    { title: "Windparks", value: formatNumber(wp.parks) },
    { title: "Energieproduktion", value: formatNumber(wp.energy_production_kwh, "kWh") },
    { title: "Einnahmen", value: formatNumber(fi.income, "€") },
    { title: "Ausgaben", value: formatNumber(fi.expenses, "€") },
    { title: "Gewinn", value: formatNumber(fi.profit, "€") },
    { title: "Offene Aufgaben", value: formatNumber(summary?.tasks as number) },
    { title: "Dokumente", value: formatNumber(summary?.documents as number) },
    { title: "Verträge", value: formatNumber(summary?.contracts as number) },
  ];

  return (
    <AppShell>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Z1 – Löwenherz Dashboard
      </Typography>

      {loading ? (
        <CircularProgress />
      ) : (
        <Grid container spacing={2}>
          {cards.map((card) => (
            <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={card.title}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">
                    {card.title}
                  </Typography>
                  <Typography variant="h5" fontWeight={600}>
                    {card.value}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </AppShell>
  );
}

