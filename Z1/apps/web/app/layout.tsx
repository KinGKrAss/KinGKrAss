import type { Metadata } from "next";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";

export const metadata: Metadata = {
  title: "Z1 Löwenherz OS",
  description: "Dashboard für Immobilien, Energie, Finanzen und Dokumente",
};

const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#6b4eff" },
    secondary: { main: "#0ea5e9" },
  },
});

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="de">
      <body>
        <AppRouterCacheProvider>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            {children}
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
