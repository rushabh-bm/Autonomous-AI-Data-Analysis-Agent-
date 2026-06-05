import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf_report(summary: dict, chat_history: list) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Autonomous AI Data Analysis Report")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 80, "Dataset Summary:")
    
    c.setFont("Helvetica", 10)
    y_pos = height - 100
    c.drawString(50, y_pos, f"Total Rows: {summary.get('n_rows', 0)}")
    c.drawString(50, y_pos - 15, f"Total Columns: {summary.get('n_cols', 0)}")
    c.drawString(50, y_pos - 30, f"Missing Cells: {summary.get('missing_cells', 0)}")
    
    y_pos -= 60
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_pos, "Key Insights (from chat):")
    
    c.setFont("Helvetica", 10)
    y_pos -= 20
    for msg in chat_history:
        if msg['role'] == 'assistant':
            # very basic wrapping hack for PDF
            text = msg['content'][:110] + ("..." if len(msg['content'])>110 else "")
            c.drawString(50, y_pos, f"- {text}")
            y_pos -= 15
            if y_pos < 50:
                c.showPage()
                y_pos = height - 50
                
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
