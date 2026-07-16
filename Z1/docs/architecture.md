# Architekturübersicht

## Schichten
- **Frontend:** Android und Next.js Web-Oberfläche
- **Backend API:** FastAPI, JWT, WebSocket
- **Domain-Module:** Zoë, Electra, Gaia, Fortuna, Themis, Diplomatia, Astraea
- **Persistenz:** PostgreSQL (primär), Redis (Cache)
- **AI-Layer:** OpenAI-kompatibler Client, Agenten-Koordination, Workflows

## Module
Jedes Modul besitzt einen eigenen Verzeichnisplatzhalter unter `modules/` und wird schrittweise als eigenständige Domain erweitert.

## Sicherheit
- JWT für API-Zugriff
- Rollen und Rechte (Basis im User-Modell)
- Redis-/DB-Healthchecks
