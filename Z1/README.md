# Z1 – Löwenherz Operating System

Modulare Plattform für Immobilien, Energie, Finanzen, Dokumente und KI-Agenten.

## Stack
- **Frontend:** Android (Kotlin + Jetpack Compose), Next.js (React, Material UI)
- **Backend:** FastAPI, REST, WebSocket, JWT
- **Daten:** PostgreSQL, Redis, SQLAlchemy, Alembic
- **KI:** OpenAI-kompatible APIs, Agenten- und Workflow-Orchestrierung
- **Infra:** Docker, Docker Compose, Nginx, GitHub Actions

## Schnellstart
1. `.env.example` nach `.env` kopieren und bei Bedarf anpassen.
2. Docker starten und dann:
   ```bash
   docker compose -f docker-compose.yml up --build
   ```
3. API öffnen: `http://localhost:8000/docs`
4. Web öffnen: `http://localhost`

## Projektstruktur
Siehe `docs/architecture.md`.
