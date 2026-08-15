# Z1 System-Erweiterung – Haus Oasis V2.0

> **Modul:** Gaia · Fortuna · Astraea  
> **Status:** Implementierungs-Grundlage  
> **Ziel:** Nahtlose Integration des Hauses Oasis in den Z1-Kern

---

## 1. TypeScript Interface (`lib/types/property.ts`)

Strikte Typensicherheit für die Datenverarbeitung im Z1-Kern.

```typescript
export interface Property {
  property_id: string;
  name: string;
  status: 'active' | 'inactive' | 'maintenance';
  meta: {
    classification: string;
    security_level: string;
    version: string;
  };
  modules: {
    gaia: { type: string; units: number; energy_management: boolean };
    fortuna: { managed: boolean; currency_tag: string };
    astraea: { audit_enabled: boolean };
  };
  guardian_ref: { name: string; role: string };
  timestamp: string;
}
```

> **Hinweis:** Das laufende Gaia-Modul verwendet aktuell das Interface in `apps/web/lib/api.ts`
> (`id: number`, `address`, `city`, `area_sqm` usw.). Diese erweiterte Typ-Definition ist für
> die V2.0-Skalierungsstufe vorgesehen und muss mit dem Backend-Schema synchronisiert werden.

---

## 2. PostgreSQL Schema (`schema.sql`)

Datenintegrität in der Backend-Datenbank für das Haus-Oasis-Objekt.

```sql
CREATE TABLE properties (
    property_id VARCHAR(50) PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    status      VARCHAR(20),
    guardian_name VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE property_modules (
    id          SERIAL PRIMARY KEY,
    property_id VARCHAR(50) REFERENCES properties(property_id),
    module_name VARCHAR(50),
    config      JSONB
);
```

---

## 3. API Route Logic (`app/api/v2/gaia/properties/route.ts`)

Endpunkt für die Aufnahme des Hauses Oasis in den Z1-Kern.

```typescript
export async function POST(req: Request) {
  const data = await req.json();
  // Validierung gegen Schema
  // Datenbank-Commit für Gaia, Fortuna & Astraea
  console.log("Integrations-Protokoll für:", data.name);
  return Response.json({ status: "Success", property_id: data.property_id });
}
```

---

## Integrations-Checkliste

- [ ] TypeScript-Interface in `lib/api.ts` auf V2.0-Schema migrieren
- [ ] PostgreSQL-Migrationsskript erstellen und gegen bestehende `properties`-Tabelle prüfen
- [ ] API-Route `/api/v2/gaia/properties` implementieren und testen
- [ ] Fortuna-Modul: Cashflow-Anbindung für Haus Oasis aktivieren
- [ ] Astraea-Modul: Audit-Logging für neues Objekt einschalten
- [ ] Backend-Tests (`pytest tests`) nach Migration ausführen
- [ ] Frontend-Build (`npm run lint && npm run build`) validieren

---

🦁❤️👑 **Haus Löwenherz – Expansion auf 20.000 Einheiten**
