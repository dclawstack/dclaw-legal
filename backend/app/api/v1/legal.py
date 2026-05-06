import uuid
from datetime import datetime, timezone
from random import randint

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ContractReviewRequest(BaseModel):
    contract_text: str


class ContractReviewResponse(BaseModel):
    id: str
    title: str
    risk_score: int
    status: str
    created_at: str


@router.post("/contracts/review")
async def review_contract(req: ContractReviewRequest):
    return ContractReviewResponse(
        id=str(uuid.uuid4()),
        title="Contract Review",
        risk_score=randint(1, 100),
        status="completed",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
