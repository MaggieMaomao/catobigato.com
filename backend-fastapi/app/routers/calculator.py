"""Calculator API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.models.calculator import CustomFunction, CalculationHistory
from app.services.calculator_engine import engine
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/calculator", tags=["Calculator"])


class EvaluateRequest(BaseModel):
    expression: str
    mode: str = "basic"


class EvaluateResponse(BaseModel):
    success: bool
    result: str | None = None
    error: str | None = None
    latex: str | None = None


class FunctionCreate(BaseModel):
    name: str
    description: str = ""
    definition: dict  # {"params": [{"name": "x", "type": "number"}], "body": "x^2"}
    is_public: bool = False


class FunctionResponse(BaseModel):
    id: str
    name: str
    description: str
    definition: dict
    is_public: bool
    creator_id: str


class HistoryResponse(BaseModel):
    id: str
    mode: str
    expression: str
    result: str
    created_at: str


@router.post("/evaluate/", response_model=EvaluateResponse)
async def evaluate(req: EvaluateRequest, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    mode = req.mode or "basic"

    try:
        if mode == "algebra":
            result = engine.simplify(req.expression)
        elif mode == "calculus":
            result = engine.derivative(req.expression)
        elif mode == "graph":
            result = engine.plot_function(req.expression)
            if result.get("success"):
                hist = CalculationHistory(
                    user_id=uuid.UUID(user.sub),  # keycloak sub as uuid
                    expression=req.expression,
                    result=f"plotted: {req.expression}",
                    mode=mode,
                    inputs={},
                    calc_metadata={"svg": result.get("svg", "")},
                )
                db.add(hist)
                await db.commit()
                return EvaluateResponse(success=True, result="plotted", latex=result.get("latex"))
        else:
            result = engine.evaluate(req.expression)

        if result.get("success"):
            hist = CalculationHistory(
                user_id=uuid.UUID(user.sub),
                expression=req.expression,
                result=str(result.get("result", result.get("simplified", ""))),
                mode=mode,
                inputs={},
                calc_metadata={},
            )
            db.add(hist)
            await db.commit()

        return EvaluateResponse(
            success=result.get("success", False),
            result=str(result.get("result", result.get("simplified", result.get("derivative", "")))),
            error=result.get("error"),
            latex=result.get("simplified_latex", result.get("derivative_latex")),
        )
    except Exception as e:
        return EvaluateResponse(success=False, error=str(e))


@router.get("/history/", response_model=list[HistoryResponse])
async def get_history(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = (
        select(CalculationHistory)
        .where(CalculationHistory.user_id == uuid.UUID(user.sub))
        .order_by(CalculationHistory.created_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [
        HistoryResponse(
            id=str(r.id),
            mode=r.mode,
            expression=r.expression,
            result=r.result,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]


@router.delete("/history/")
async def clear_history(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = delete(CalculationHistory).where(CalculationHistory.user_id == uuid.UUID(user.sub))
    await db.execute(stmt)
    await db.commit()
    return {"message": "History cleared"}


@router.get("/functions/", response_model=list[FunctionResponse])
async def list_functions(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    uid = uuid.UUID(user.sub)
    stmt = select(CustomFunction).where(
        (CustomFunction.creator_id == uid) | (CustomFunction.is_public == True)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [
        FunctionResponse(
            id=str(r.id),
            name=r.name,
            description=r.description,
            definition=r.definition,
            is_public=r.is_public,
            creator_id=str(r.creator_id),
        )
        for r in rows
    ]


@router.post("/functions/", response_model=FunctionResponse)
async def create_function(data: FunctionCreate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    func = CustomFunction(
        name=data.name,
        description=data.description,
        definition=data.definition,
        is_public=data.is_public,
        creator_id=uuid.UUID(user.sub),
    )
    db.add(func)
    await db.commit()
    await db.refresh(func)
    return FunctionResponse(
        id=str(func.id),
        name=func.name,
        description=func.description,
        definition=func.definition,
        is_public=func.is_public,
        creator_id=str(func.creator_id),
    )


@router.delete("/functions/{func_id}")
async def delete_function(func_id: str, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(CustomFunction).where(CustomFunction.id == func_id)
    result = await db.execute(stmt)
    func = result.scalar_one_or_none()
    if not func:
        raise HTTPException(status_code=404, detail="Function not found")
    if str(func.creator_id) != user.sub:
        raise HTTPException(status_code=403, detail="Not your function")
    await db.delete(func)
    await db.commit()
    return {"message": "Deleted"}
