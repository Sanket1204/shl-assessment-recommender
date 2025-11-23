from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .models import RecommendationResponse, RecommendationRequest


def build_recommendation_pdf(req: RecommendationRequest, resp: RecommendationResponse) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Assessment Recommendation Bundle")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Job Title: {req.job_title}")
    y -= 15
    c.drawString(40, y, f"Job Family: {req.job_family}  |  Level: {req.job_level}")
    y -= 15
    c.drawString(40, y, f"Use Case: {req.use_case}  |  Volume: {req.volume}")
    y -= 25

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, f"Total Duration: {resp.total_duration_min} minutes")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(40, y, "Constructs Covered: " + ", ".join(resp.constructs_covered))
    y -= 25

    for p in resp.products:
        if y < 100:
            c.showPage()
            y = height - 50
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, f"{p.name} ({p.product_id}) - {p.max_duration_min} min")
        y -= 15
        c.setFont("Helvetica", 9)
        for line in _wrap_text(p.reason, 90):
            c.drawString(50, y, line)
            y -= 12
        y -= 10

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def _wrap_text(text: str, width: int):
    words = text.split()
    lines = []
    current = []
    count = 0
    for w in words:
        if count + len(w) + 1 > width:
            lines.append(" ".join(current))
            current = [w]
            count = len(w)
        else:
            current.append(w)
            count += len(w) + 1
    if current:
        lines.append(" ".join(current))
    return lines
