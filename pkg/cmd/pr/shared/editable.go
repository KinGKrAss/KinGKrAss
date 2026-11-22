package shared

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

// Editable bildet die bearbeitbaren Metadaten eines Pull Requests in System-Z1 ab.
type Editable struct {
	Title     EditableString
	Body      EditableString
	Base      EditableString
	Reviewers EditableSlice
	Assignees EditableSlice
	Labels    EditableSlice
	Projects  EditableSlice
	Milestone EditableString
	Metadata  map[string]string
}

type EditableString struct {
	Value  string
	Edited bool
}

type EditableSlice struct {
	Value   []string
	Add     []string
	Remove  []string
	Default []string
	Edited  bool
}

// Dirty prüft, ob mindestens ein Feld geändert wurde.
func (e *Editable) Dirty() bool {
	return e.Title.Edited ||
		e.Body.Edited ||
		e.Base.Edited ||
		e.Reviewers.Edited ||
		e.Assignees.Edited ||
		e.Labels.Edited ||
		e.Projects.Edited ||
		e.Milestone.Edited
}

type geminiBridgeRequest struct {
	Title       string   `json:"title"`
	Body        string   `json:"body"`
	Labels      []string `json:"labels"`
	Instruction string   `json:"instruction,omitempty"`
}

type geminiBridgeResponse struct {
	Status   string `json:"status"`
	Error    string `json:"error,omitempty"`
	Editable struct {
		Title  string   `json:"title"`
		Body   string   `json:"body"`
		Labels []string `json:"labels"`
	} `json:"editable"`
}

// EnrichWithGemini sendet die aktuellen PR-Daten an die lokale @ai-sdk/google Bridge
// und aktualisiert Titel, Beschreibung und Labels automatisch.
func (e *Editable) EnrichWithGemini(ctx context.Context, instruction string) error {
	endpoint := os.Getenv("Z1_GEMINI_ENDPOINT")
	if endpoint == "" {
		endpoint = "http://127.0.0.1:8787/api/z1/pr/editable"
	}

	rawBody, err := json.Marshal(geminiBridgeRequest{
		Title:       e.Title.Value,
		Body:        e.Body.Value,
		Labels:      e.Labels.Value,
		Instruction: instruction,
	})
	if err != nil {
		return fmt.Errorf("json marshal fehlgeschlagen: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, bytes.NewReader(rawBody))
	if err != nil {
		return fmt.Errorf("request erstellung fehlgeschlagen: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("gemini bridge nicht erreichbar (%s): %w", endpoint, err)
	}
	defer resp.Body.Close()

	var decoded geminiBridgeResponse
	if err := json.NewDecoder(resp.Body).Decode(&decoded); err != nil {
		return fmt.Errorf("ungültige antwort von gemini bridge: %w", err)
	}

	if resp.StatusCode >= 400 || decoded.Status == "error" {
		return fmt.Errorf("gemini bridge fehler (%d): %s", resp.StatusCode, decoded.Error)
	}

	if decoded.Editable.Title != "" && decoded.Editable.Title != e.Title.Value {
		e.Title.Value = decoded.Editable.Title
		e.Title.Edited = true
	}
	if decoded.Editable.Body != "" && decoded.Editable.Body != e.Body.Value {
		e.Body.Value = decoded.Editable.Body
		e.Body.Edited = true
	}
	if len(decoded.Editable.Labels) > 0 {
		e.Labels.Value = decoded.Editable.Labels
		e.Labels.Edited = true
	}

	return nil
}
