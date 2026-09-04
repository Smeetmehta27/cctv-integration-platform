import io
import csv
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

class EvaluationReportGenerator:
    @staticmethod
    def generate_csv(trajectory_data: dict, target_plate: str) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Timestamp', 'Camera_ID', 'Camera_Name', 'Department', 
            'Latitude', 'Longitude', 'Raw_OCR', 'Normalized_Plate', 
            'Confidence', 'Speed_from_Prev_kmh'
        ])
        
        for wp in trajectory_data.get('waypoints', []):
            writer.writerow([
                wp.get('entry_time'),
                wp.get('camera_id'),
                wp.get('camera_name'),
                wp.get('district'),
                wp.get('latitude'),
                wp.get('longitude'),
                target_plate, # In a real system, we'd fetch the raw OCR from DB
                target_plate,
                wp.get('confidence'),
                wp.get('speed_from_prev')
            ])
            
        return output.getvalue()

    @staticmethod
    def generate_pdf(trajectory_data: dict, target_plate: str) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Header
        header_style = ParagraphStyle('Header', parent=styles['Heading1'], alignment=1, spaceAfter=20)
        elements.append(Paragraph("Government of Gujarat", header_style))
        elements.append(Paragraph("Statewide CCTV Integration Platform - Investigation & Tracking Audit Report", styles['Heading2']))
        elements.append(Spacer(1, 20))
        
        # Details
        elements.append(Paragraph(f"<b>Target Vehicle Registration:</b> {target_plate}", styles['Normal']))
        elements.append(Paragraph(f"<b>Report Generated At:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        
        summary = trajectory_data.get('summary', {})
        elements.append(Paragraph(f"<b>Total Distance:</b> {summary.get('total_distance_km')} km", styles['Normal']))
        elements.append(Paragraph(f"<b>Average Speed:</b> {summary.get('average_speed_kmh')} km/h", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Table
        data = [['Time', 'Camera Name', 'District', 'Speed (km/h)']]
        for wp in trajectory_data.get('waypoints', []):
            try:
                dt_str = wp.get('entry_time')[:19].replace("T", " ")
            except:
                dt_str = wp.get('entry_time')
                
            data.append([
                dt_str,
                wp.get('camera_name', '')[:20],
                wp.get('district', '')[:20],
                str(wp.get('speed_from_prev', 0))
            ])
            
        table = Table(data, colWidths=[120, 150, 120, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        return buffer.getvalue()
