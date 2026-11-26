"""Build a compact, printable PDF report using only Python's standard library."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'reports'/'FINAL_PROJECT_REPORT.md'
TARGET=ROOT/'reports'/'FINAL_PROJECT_REPORT.pdf'
W,H=612,792

def clean(s):
    s=re.sub(r'`([^`]*)`',r'\1',s)
    s=s.replace('—','-').replace('–','-').replace('’',"'").replace('“','"').replace('”','"').replace('ᵢ','i').replace('−','-').replace('→','->').replace('·','|')
    return s.encode('cp1252','replace').decode('cp1252')

def esc(s): return s.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')

def wrap(text, max_chars):
    words=clean(text).split(); out=[]; line=''
    for word in words:
        if len(line)+len(word)+(1 if line else 0)>max_chars:
            out.append(line); line=word
        else: line+=((' ' if line else '')+word)
    if line: out.append(line)
    return out or ['']

pages=[]; ops=[]; y=H-64; page_no=0
def new_page():
    global ops,y,page_no
    if ops: pages.append(ops)
    page_no+=1; ops=[]; y=H-68
    ops.append('0.08 0.25 0.36 rg 0 750 612 42 re f')
    ops.append('BT /F1 10 Tf 1 1 1 rg 42 766 Td (COURIER PLANNING SYSTEM  |  FINAL PROJECT REPORT) Tj ET')
    ops.append('0.08 0.25 0.36 rg 0 0 612 34 re f')
    ops.append(f'BT /F1 9 Tf 1 1 1 rg 42 13 Td (Design and Analysis of Algorithms) Tj ET BT /F1 9 Tf 1 1 1 rg 545 13 Td ({page_no}) Tj ET')

def line(text,size=10,color=(.13,.19,.25),bold=False,leading=None):
    global y
    leading=leading or size*1.45
    if y<58+leading: new_page()
    r,g,b=color; font='F2' if bold else 'F1'
    ops.append(f'BT /{font} {size} Tf {r:.3f} {g:.3f} {b:.3f} rg 48 {y:.1f} Td ({esc(text)}) Tj ET')
    y-=leading

def paragraph(text, size=10, color=(.13,.19,.25), bold=False):
    max_chars=int(98*10/size)
    for ln in wrap(text,max_chars): line(ln,size,color,bold)
    line('',3)

new_page()
for raw in SOURCE.read_text(encoding='utf-8').splitlines():
    s=raw.strip()
    if not s: y-=4; continue
    if s.startswith('# '):
        if y<H-150: new_page()
        for ln in wrap(s[2:],38): line(ln,22,(.06,.29,.45),True,29)
        line('',6)
    elif s.startswith('## '):
        line('',4)
        for ln in wrap(s[3:],70): line(ln,15,(.05,.42,.48),True,20)
    elif s.startswith('### '): paragraph(s[4:],11,(.05,.42,.48),True)
    elif s.startswith('|'):
        cells=[clean(c.strip()) for c in s.strip('|').split('|')]
        if all(set(c)<=set('-: ') for c in cells): continue
        paragraph('   |   '.join(cells),8,(.20,.28,.35),False)
    elif s.startswith('- '): paragraph('•  '+s[2:],9.5)
    elif s.startswith('```'):
        continue
    else: paragraph(s)
if ops: pages.append(ops)

objects=[]
def obj(s): objects.append(s); return len(objects)
font1=obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
font2=obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>')
page_ids=[]
for content in pages:
    stream='\n'.join(content).encode('cp1252','replace')
    stream_id=obj(f'<< /Length {len(stream)} >>\nstream\n'.encode()+stream+b'\nendstream')
    page_id=obj(f'<< /Type /Page /Parent PAGES 0 R /MediaBox [0 0 {W} {H}] /Resources << /Font << /F1 {font1} 0 R /F2 {font2} 0 R >> >> /Contents {stream_id} 0 R >>')
    page_ids.append(page_id)
pages_id=obj('PAGES_PLACEHOLDER'); catalog_id=obj(f'<< /Type /Catalog /Pages {pages_id} 0 R >>')
objects[pages_id-1]=f'<< /Type /Pages /Kids [{" ".join(f"{i} 0 R" for i in page_ids)}] /Count {len(page_ids)} >>'
for page_id in page_ids:
    objects[page_id-1]=objects[page_id-1].replace('PAGES 0 R',f'{pages_id} 0 R')
data=bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'); offsets=[0]
for i,o in enumerate(objects,1):
    offsets.append(len(data)); data.extend(f'{i} 0 obj\n'.encode()); data.extend(o if isinstance(o,bytes) else o.encode('cp1252','replace')); data.extend(b'\nendobj\n')
xref=len(data); data.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
for off in offsets[1:]: data.extend(f'{off:010d} 00000 n \n'.encode())
data.extend(f'trailer\n<< /Size {len(objects)+1} /Root {catalog_id} 0 R >>\nstartxref\n{xref}\n%%EOF'.encode())
TARGET.write_bytes(data)
print(f'Created {TARGET} ({len(pages)} pages, {len(data)} bytes)')
