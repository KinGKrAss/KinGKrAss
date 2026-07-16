from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database.models import (
    AgentTask,
    DiplomaticDocument,
    EnergyReading,
    LegalContract,
    MaintenanceRequest,
    Property,
    Tenant,
    Transaction,
    WindFarm,
)


class DashboardService:
    @staticmethod
    def get_summary(db: Session) -> dict:
        # Gaia
        property_count = db.scalar(select(func.count()).select_from(Property)) or 0
        rent_income = db.scalar(select(func.coalesce(func.sum(Tenant.monthly_rent), 0.0))) or 0.0

        # Electra
        windpark_count = db.scalar(select(func.count()).select_from(WindFarm)) or 0
        energy_production = (
            db.scalar(select(func.coalesce(func.sum(EnergyReading.production_kwh), 0.0))) or 0.0
        )

        # Fortuna
        income_total = (
            db.scalar(
                select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                    Transaction.transaction_type == "income"
                )
            ) or 0.0
        )
        expense_total = (
            db.scalar(
                select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                    Transaction.transaction_type == "expense"
                )
            ) or 0.0
        )

        # Tasks and documents
        open_tasks = (
            db.scalar(
                select(func.count())
                .select_from(AgentTask)
                .where(AgentTask.status.in_(["todo", "in_progress"]))
            ) or 0
        )
        doc_count = db.scalar(select(func.count()).select_from(DiplomaticDocument)) or 0
        contract_count = db.scalar(select(func.count()).select_from(LegalContract)) or 0
        open_maintenance = (
            db.scalar(
                select(func.count()).select_from(MaintenanceRequest).where(MaintenanceRequest.status == "open")
            ) or 0
        )

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "real_estate_overview": {
                "objects": property_count,
                "rent_income": rent_income,
            },
            "windpark_overview": {
                "parks": windpark_count,
                "energy_production_kwh": energy_production,
            },
            "finance": {
                "income": income_total,
                "expenses": expense_total,
                "profit": income_total - expense_total,
            },
            "tasks": open_tasks,
            "documents": doc_count,
            "contracts": contract_count,
            "open_maintenance_requests": open_maintenance,
        }
