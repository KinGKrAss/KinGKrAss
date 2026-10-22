from fastapi import APIRouter, Depends

from auth.deps import get_current_user

router = APIRouter(prefix="/modules", tags=["modules"])

MODULES = {
    "zoe": ["agent_koordination", "aufgabenverwaltung", "workflow_steuerung"],
    "electra": ["windparkverwaltung", "energieproduktion", "strompreisueberwachung"],
    "gaia": ["immobilienverwaltung", "kartenansicht", "wartungsverwaltung"],
    "fortuna": ["einnahmen", "ausgaben", "cashflow"],
    "themis": ["vertragsverwaltung", "dokumentengenerator", "fristen"],
    "diplomatia": ["diplomatische_dokumente", "analysen", "korrespondenz"],
    "astraea": ["sicherheit", "verschluesselung", "audit_logs", "berechtigungen"],
}


@router.get("")
def list_modules(_: str = Depends(get_current_user)) -> dict:
    return MODULES
