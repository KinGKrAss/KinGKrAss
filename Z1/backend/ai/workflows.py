from dataclasses import dataclass


@dataclass(slots=True)
class WorkflowResult:
    workflow: str
    status: str
    details: str


def run_workflow(name: str) -> WorkflowResult:
    return WorkflowResult(
        workflow=name,
        status="queued",
        details="Workflow zur Ausführung an Zoë übergeben.",
    )
