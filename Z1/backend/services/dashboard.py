from datetime import datetime, timezone


class DashboardService:
    @staticmethod
    def get_summary() -> dict:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "real_estate_overview": {"objects": 12, "rent_income": 42000},
            "windpark_overview": {"parks": 3, "energy_production_kwh": 845000},
            "finance": {"income": 120000, "expenses": 54000, "profit": 66000},
            "tasks": 8,
            "documents": 126,
            "calendar_events": 5,
            "notifications": 3,
        }
