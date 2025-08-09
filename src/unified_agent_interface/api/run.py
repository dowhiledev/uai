from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request

from ..components.storage.base import Storage
from ..models.run import (
    CreateRunRequest,
    CreateRunResponse,
    LogEntry,
    RunArtifact,
    RunStatusResponse,
)


router = APIRouter()


def get_storage(req: Request) -> Storage:
    return req.app.state.storage


@router.post("/", response_model=CreateRunResponse)
def create_run(payload: CreateRunRequest | None = None, storage: Storage = Depends(get_storage)):
    task = storage.create_run(initial_input=payload.input if payload else None, params=(payload.params if payload else None) or {})
    return CreateRunResponse(task_id=task.id, estimated_completion_time=task.estimated_completion_time)


@router.get("/{task_id}", response_model=RunStatusResponse)
def get_run_status(task_id: str, storage: Storage = Depends(get_storage)) -> RunStatusResponse:
    task = storage.get_run(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return RunStatusResponse(**task.model_dump())


@router.delete("/{task_id}")
def cancel_run(task_id: str, storage: Storage = Depends(get_storage)):
    ok = storage.delete_run(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}


@router.post("/{task_id}/input")
def provide_input(task_id: str, payload: CreateRunRequest, storage: Storage = Depends(get_storage)):
    task = storage.get_run(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    storage.append_run_input(task_id, payload.input or "")
    return {"ok": True}


@router.get("/{task_id}/artifacts", response_model=List[RunArtifact])
def list_run_artifacts(task_id: str, storage: Storage = Depends(get_storage)) -> List[RunArtifact]:
    arts = storage.get_run_artifacts(task_id)
    if arts is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return arts


@router.get("/{task_id}/artifacts/{artifact_id}", response_model=RunArtifact)
def get_run_artifact(task_id: str, artifact_id: str, storage: Storage = Depends(get_storage)) -> RunArtifact:
    art = storage.get_single_run_artifact(task_id, artifact_id)
    if art is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return art


@router.post("/{task_id}/logs")
def send_logs(task_id: str, payload: LogEntry, storage: Storage = Depends(get_storage)):
    task = storage.get_run(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    storage.append_run_log(task_id, payload)
    return {"ok": True}

