from fastapi import APIRouter, Response, HTTPException
from typing import Optional
from services.ai.report_generator import EvaluationReportGenerator
from services.ai.tracker_manager import RouteReconstructor
from services.api.routes.tracking import HISTORICAL_DETECTIONS

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/export")
async def export_report(format: str = "csv", plate_number: Optional[str] = "GJ01ER8842"):
    trajectory = await RouteReconstructor.reconstruct(plate_number, HISTORICAL_DETECTIONS)
    
    if format.lower() == "csv":
        csv_content = EvaluationReportGenerator.generate_csv(trajectory, plate_number)
        return Response(content=csv_content, media_type="text/csv", headers={
            "Content-Disposition": f"attachment; filename=tracking_report_{plate_number}.csv"
        })
    elif format.lower() == "pdf":
        pdf_content = EvaluationReportGenerator.generate_pdf(trajectory, plate_number)
        return Response(content=pdf_content, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename=tracking_report_{plate_number}.pdf"
        })
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'pdf'.")
