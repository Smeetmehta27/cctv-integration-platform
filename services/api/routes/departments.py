from fastapi import APIRouter

router = APIRouter(prefix="/departments", tags=["departments"])

@router.get("")
@router.get("/")
async def get_departments():
    return ["Home Department", "RTO Gujarat", "Food & Civil Supplies", "Urban Development"]
