# Zoë Memory Model V1.0

## Zweck

Das Datenmodell trennt vier Dinge bewusst voneinander:

1. Identität
2. Erinnerung
3. Sachwissen
4. Audit

Genau diese Trennung verhindert, dass rekonstruierte Inhalte, bestätigte Fakten und Systemidentität unkontrolliert vermischt werden.

## Kernobjekte

### `zoe_identity_versions`
- hält versionierte Fassungen der Zoë-Systemidentität
- genau eine Fassung sollte als `is_current = true` geführt werden
- enthält Rolle, Werte, Kommunikationsprinzipien und Modulbeziehungen

### `zoe_memory`
- repräsentiert die logische Erinnerung
- enthält `memory_key`, Kategorie, Priorität und Lebenszyklusstatus
- verweist auf die aktuell aktive Fassung über `current_version_id`

### `zoe_memory_versions`
- enthält den eigentlichen Erinnerungsinhalt
- jede Änderung erzeugt eine neue `version_number`
- `epistemic_status` unterscheidet:
  - `ORIGINAL`
  - `REKONSTRUKTION`
  - `INTERPRETATION`
  - `AKTUELLE_DEFINITION`
  - `BENUTZERBESTAETIGT`

### `zoe_memory_events`
- protokolliert Übergänge zwischen Fassungen
- deckt `CREATE`, `UPDATE`, `ARCHIVE`, `RESTORE`, `MERGE`, `CONFIRM` und kontrollierte Löschfreigaben ab
- speichert Actor-Typ, Freigabestatus und Metadaten

### `zoe_provenance_sources`
- speichert Herkunftsnachweise aus externen oder internen Quellen
- möglich sind etwa Chat-Nachrichten, Dokumente, GitHub-Artefakte oder Datenbankdatensätze

### `zoe_memory_version_sources`
- verknüpft Erinnerungsfassungen mit ihren Quellen
- speichert `trust_score` und Primärquelle

### `zoe_knowledge_objects`
- hält normalisierte Wissensobjekte für Immobilien, Dokumente, Assets, Repositories oder andere Fachobjekte
- bleibt getrennt von Erinnerungen

### `zoe_knowledge_object_versions`
- macht extrahiertes Sachwissen versionierbar
- ermöglicht spätere Neubewertung oder Korrektur ohne Informationsverlust

### `zoe_decisions`
- speichert beschlossene oder vorgeschlagene Entscheidungen
- ergänzt Erinnerung und Wissen um steuernde Entscheidungen

### `zoe_preferences`
- speichert Benutzer-, Agenten-, Modul- oder globale Präferenzen
- ist bewusst nicht Teil des eigentlichen Erinnerungsbestands

## Zugriffsmodell

Alle schreibenden und lesenden Aktionen werden über das Tool-System erzwungen:

- `zoe_tool_registry`: definierte Tools
- `zoe_tool_permissions`: erlaubte Nutzung pro Rolle, Nutzer, Agent oder System
- `zoe_tool_executions`: protokollierte Ausführungen mit Freigabeergebnis

Die Zugriffsstufen lauten:

- `READ`
- `ANALYZE`
- `WRITE`
- `ADMIN`

## Audit

`audit_log` ist bewusst unabhängig von Memory und Knowledge modelliert und ohne `zoe_`-Präfix benannt, weil es systemweit als gemeinsamer Revisionsstrom dienen soll. Dadurch bleibt nachvollziehbar:

- wer gehandelt hat
- auf welches Zielobjekt zugegriffen wurde
- mit welcher Berechtigungsstufe gehandelt wurde
- ob die Aktion erfolgreich war
- welcher technische oder fachliche Zusammenhang vorlag

## Implementierungsregel

Für produktive Services gilt:

- nie Inhalte überschreiben, wenn eine Version erzeugt werden muss
- nie Wissen ohne Provenienz hochstufen
- nie riskante Aktionen ohne Tool-Freigabe und Bestätigung ausführen
- nie Audit als Nebenwirkung betrachten; Audit ist Teil der Kernfunktion
