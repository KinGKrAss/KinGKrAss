# Zoë AI Platform Blueprint V1.0

Codename: `ZOE-CORE`  
Systemkontext: `Z1 Real Estate Command Center`

## Zielbild

Dieses Repository erhält damit ein verbindliches Fundament, auf dem Backend, Datenbank, Integrationen und spätere GitHub-Projektarbeit aufgebaut werden können. Die erste Ausbaustufe trennt Identität, Erinnerung, Wissensobjekte, Werkzeuge, Integrationen und Audit explizit voneinander.

## Bausteine

### 1. ZOE-CORE
- Verantwortlich für Intent-Erkennung, Kontextaufbereitung, Planung, Antwortsynthese und Orchestrierung
- Nutzt ausschließlich registrierte Tools und freigegebene Integrationen
- Darf keine Rohzugriffe auf Datenbank, GitHub oder Terra Box ausführen

### 2. ZOE-MEMORY
- Verwaltet versionierte Identität, Langzeitwissen, Provenienz und Kontextpakete
- Hält Rekonstruktion, bestätigte Fakten und Interpretation getrennt
- Liefert den strukturierten Kontext für ZOE-CORE

### 3. ZOE-TOOLS
- Registriert erlaubte Aktionen als kontrollierte Tool-Schnittstellen
- Erzwingt Permission-Checks, Bestätigungen und Audit-Einträge
- Trennt Lese-, Analyse-, Schreib- und Administrationsaktionen

### 4. Integrationslayer
- Kapselt externe Systeme: PostgreSQL, GitHub und Terra Box
- Definiert je System freigegebene Lese-, Analyse- und Schreibpfade
- Stellt sicher, dass Berechtigungen unabhängig vom Modell erzwungen werden

### 5. Report Engine
- Erzeugt Berichte aus freigegebenen Datenströmen
- Zielausgaben: Dashboard, JSON, PDF
- Nutzt Audit und Versionierung als Nachweisgrundlage

## Rollenmodell

Die Plattform verwendet vier Zugriffsstufen:

- `READ`: anzeigen und abrufen
- `ANALYZE`: berechnen, korrelieren, zusammenfassen
- `WRITE`: schreiben oder aktualisieren
- `ADMIN`: Richtlinien, Tools, Integrationen und Freigaben verwalten

Jede Operation durchläuft:

1. Tool-Auswahl
2. Permission Check
3. optionale Bestätigung
4. Ausführung im Zielsystem
5. Audit-Eintrag

## Datenverantwortung

- `zoe_identity_versions`: versionierte Systemidentität
- `zoe_memory` und `zoe_memory_versions`: Langzeiterinnerungen und ihre Fassungen
- `zoe_memory_events`: Lebenszyklusereignisse wie Create, Update, Archive, Restore und Merge
- `zoe_knowledge_objects` und Versionen: extrahiertes Sachwissen
- `zoe_provenance_sources`: Herkunftsnachweise aus Chat, Dokumenten, Datenbank oder GitHub
- `zoe_tool_*`: definierte Werkzeuge, Rechte und Ausführungen
- `audit_log`: revisionssichere Nachvollziehbarkeit

## Repo-Zuschnitt für die nächste Ausbaustufe

```text
Z1/
├── apps/
├── services/
│   ├── z1-api/
│   ├── zoe-core/
│   ├── zoe-memory/
│   ├── zoe-agents/
│   ├── zoe-connectors/
│   └── zoe-reports/
├── database/
│   ├── migrations/
│   ├── schema/
│   ├── seeds/
│   └── imports/
├── integrations/
│   ├── github/
│   └── terrabox/
├── docs/
│   ├── architecture/
│   ├── zoe/
│   └── database/
└── infrastructure/
```

Die Struktur ist absichtlich modular, aber noch nicht vollständig angelegt. Diese Ausbaustufe liefert zuerst das verbindliche Architektur- und Datenfundament.

## Phasen

### Phase 1
- Datenmodell
- Memory Core
- Audit
- Rollenmodell

### Phase 2
- Tool Router
- PostgreSQL-Integration

### Phase 3
- Report Engine
- erste Analyse-Workflows

### Phase 4
- GitHub-Connector
- Terra-Box-Connector

### Phase 5
- Agent-Orchestrierung
- Command-Center-Anbindung

## Ergebnis dieser Ausbaustufe

Dieses Repository enthält jetzt die verbindliche Blueprint-Dokumentation und ein konkretes PostgreSQL-Schema als Startpunkt für Backend-, Migrations- und API-Arbeit.
