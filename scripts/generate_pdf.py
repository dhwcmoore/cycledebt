from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sys

if len(sys.argv) != 3:
    print('Usage: generate_pdf.py input.txt output.pdf')
    sys.exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2]

with open(input_path, 'r') as f:
    lines = f.readlines()

c = canvas.Canvas(output_path, pagesize=letter)
width, height = letter
margin = 72
y = height - margin
c.setFont('Helvetica', 12)

for line in lines:
    line = line.rstrip('\n')
    if y < margin:
        c.showPage()
        c.setFont('Helvetica', 12)
        y = height - margin
    c.drawString(margin, y, line)
    y -= 14

c.save()
print('Wrote', output_path)
