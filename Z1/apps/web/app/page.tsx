import { Card, CardContent, Grid, Typography } from "@mui/material";

const cards = [
  { title: "Immobilien", value: "12" },
  { title: "Windparks", value: "3" },
  { title: "Energieproduktion", value: "845 MWh" },
  { title: "Einnahmen", value: "120.000 €" },
  { title: "Ausgaben", value: "54.000 €" },
  { title: "Gewinn", value: "66.000 €" },
  { title: "Aufgaben", value: "8" },
  { title: "Dokumente", value: "126" },
  { title: "Kalender", value: "5 Termine" },
  { title: "Benachrichtigungen", value: "3" }
];

export default function HomePage() {
  return (
    <main style={{ padding: 24 }}>
      <Typography variant="h4" gutterBottom>
        Z1 – Löwenherz Dashboard
      </Typography>
      <Grid container spacing={2}>
        {cards.map((card) => (
          <Grid size={{ xs: 12, md: 6, lg: 3 }} key={card.title}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary">
                  {card.title}
                </Typography>
                <Typography variant="h5">{card.value}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </main>
  );
}
