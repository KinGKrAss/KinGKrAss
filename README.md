# KinGKrAss/KinGKrAss – Repository-Zusammenfassung Version 2.0

> **Z1 – Löwenherz Operating System** | Release-Status

Das System-Update auf **Version 2.0** stellt die technische Basis für die Expansion auf 20.000 Einheiten dar und konsolidiert die verwaltungstechnische Hoheit über alle Objekte des Hauses Löwenherz.

---

## 1. Modulare Infrastruktur (Frontend & Logik)

| Modul | Datei | Beschreibung |
|---|---|---|
| **Zentralsteuerung** | `AppShell.tsx` | Vollständiger Navigations-Hub für alle 8 Kernmodule, inklusive dediziertem Log-out-Protokoll |
| **SSR-Architektur** | `layout.tsx` | Einsatz von `AppRouterCacheProvider` und `CssBaseline` für hochperformante, MUI-konforme Darstellung |
| **Sicherheits-Layer** | `app/login/page.tsx` | JWT-basiertes Login-Formular mit präzisem Error-Handling |

---

## 2. Fachmodule (Datenverwaltung)

| Modul | Route | Funktion |
|---|---|---|
| **Dashboard** | `app/page.tsx` | Live-Datenstrom für die Zusammenfassung aller operativen Einheiten |
| **Energie-Ressourcen** | `app/electra/page.tsx` | CRUD-Tabelle für Windparks + 5 spezialisierte KPI-Karten |
| **Immobilien-Portfolio** | `app/gaia/page.tsx` | Zentrales Register für alle Einheiten, inkl. **Haus Oasis** |
| **Finanz-Management** | `app/fortuna/page.tsx` | Transaktionsübersicht (Einnahmen/Ausgaben) mit Cashflow-Visualisierung |
| **Vertragsmanagement** | `app/themis/page.tsx` | Vollständiges CRUD für Verträge |
| **Dokumentenwesen** | `app/diplomatia/page.tsx` | Vollständiges CRUD für Dokumenten-Archivierung |
| **Audit & Sicherheit** | `app/astraea/page.tsx` | Überwachung der Audit-Logs und Sicherheits-KPIs |
| **KI-Dispatch** | `app/zoe/page.tsx` | Zentrale Schnittstelle für KI-Aufgabenplanung und Historienführung |

---

## 3. Backend-Integrität & Konfiguration

- **Backend-Sync (`lib/api.ts`):** Sämtliche TypeScript-Interfaces exakt an die Backend-Schemas angepasst; neue Funktionen `deleteTransaction`, `deleteContract`, `deleteDocument` und `listAuditLogs` sind live.
- **Build-Stabilität:** 11/11 Backend-Tests bestanden; Build-Status für alle 10 Routen erfolgreich.
- **Alias-Struktur:** `tsconfig.json` erweitert um den `@/`-Pfad-Alias (`baseUrl: "."`, `paths: {"@/*": ["./*"]}`).

---

## Schnellstart

```bash
# 1. Umgebung konfigurieren
cp Z1/.env.example Z1/.env

# 2. Dienste starten
docker compose -f Z1/docker-compose.yml up --build

# 3. Endpunkte
#    API:  http://localhost:8000/docs
#    Web:  http://localhost
```

## Tests & Build

```bash
# Backend-Tests
cd Z1 && pytest tests

# Frontend (Lint + Build)
cd Z1/apps/web && npm run lint && npm run build
```

---

🦁❤️👑 **Haus Löwenherz – Expansion auf 20.000 Einheiten**
