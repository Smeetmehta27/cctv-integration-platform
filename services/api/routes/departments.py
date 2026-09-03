from fastapi import APIRouter

router = APIRouter(prefix="/departments", tags=["departments"])

@router.get("/")
async def get_departments():
    return [
        {"id": "d1", "name": "Ahmedabad City Police", "region": "Ahmedabad"},
        {"id": "d2", "name": "Surat City Police", "region": "Surat"}
    ]
