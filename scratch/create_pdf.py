from pypdf import PdfWriter
import io

writer = PdfWriter()
page = writer.add_blank_page(width=600, height=800)
# Note: pypdf doesn't support adding text easily without reportlab or similar.
# But for testing, we just need a valid PDF structure.
# If PdfReader finds no text, it will raise my 400 error, which is also a test.
writer.write("scratch/test.pdf")
print("PDF created at scratch/test.pdf")
