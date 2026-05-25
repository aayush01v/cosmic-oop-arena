# VERSION: v5-redesigned-figures-to-3-5
# Purpose: Generate the Crop Yield Prediction project report PDF from Title Page to Section 3.5.
# Includes: full Table of Contents from index.txt (compacted to 2 pages), page numbers, and fixed Figure 1.2 layout.
# Run: python make_report.py
# Output: Crop_Yield_Prediction_Project_Report_v5_redesigned_figures.pdf

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable, Flowable
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Circle
from reportlab.graphics import renderPDF
from reportlab.pdfbase.pdfmetrics import stringWidth
import os, math, re
from xml.sax.saxutils import escape as xml_escape

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_PDF = os.path.join(OUT_DIR, "_project_report_pass1_to_3_5.pdf")
FINAL_PDF = os.path.join(OUT_DIR, "Crop_Yield_Prediction_Project_Report_v5_redesigned_figures.pdf")

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT = 2.4*cm
RIGHT = 2.2*cm
TOP = 2.2*cm
BOTTOM = 2.0*cm
NAVY = HexColor("#1F3A5F")
ACCENT = HexColor("#4F6F91")
PALE_BLUE = HexColor("#EAF1F8")
PALE_GREEN = HexColor("#EDF5EF")
PALE_GOLD = HexColor("#F7F1DF")
PALE_GRAY = HexColor("#F4F4F2")
DARK_GRAY = HexColor("#333333")


def roman(num:int)->str:
    if num <= 0:
        return ""
    vals = [(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]
    out = []
    for v, sym in vals:
        while num >= v:
            out.append(sym); num -= v
    return ''.join(out)


def page_label(page_num, chapter1_start):
    if not page_num:
        return ""
    if chapter1_start and page_num >= chapter1_start:
        return str(page_num - chapter1_start + 1)
    if page_num == 1:
        return ""
    return roman(page_num - 1)

class PageMarker(Flowable):
    def __init__(self, key, refs):
        super().__init__()
        self.key = key
        self.refs = refs
    def wrap(self, availWidth, availHeight):
        return (0, 0)
    def draw(self):
        self.refs[self.key] = self.canv.getPageNumber()

class DiagramFlowable(Flowable):
    def __init__(self, drawing, width, height):
        super().__init__()
        self.drawing = drawing
        self.width = width
        self.height = height
    def wrap(self, availWidth, availHeight):
        return (min(self.width, availWidth), self.height)
    def draw(self):
        renderPDF.draw(self.drawing, self.canv, 0, 0)


def make_styles():
    styles = {}
    styles['Title'] = ParagraphStyle(
        'Title', fontName='Times-Bold', fontSize=25, leading=31, textColor=NAVY,
        alignment=TA_CENTER, spaceAfter=10
    )
    styles['Subtitle'] = ParagraphStyle(
        'Subtitle', fontName='Times-Italic', fontSize=14, leading=18, textColor=DARK_GRAY,
        alignment=TA_CENTER, spaceAfter=24
    )
    styles['CoverSmall'] = ParagraphStyle(
        'CoverSmall', fontName='Times-Roman', fontSize=11, leading=15, alignment=TA_CENTER,
        textColor=DARK_GRAY, spaceAfter=8
    )
    styles['H1'] = ParagraphStyle(
        'H1', fontName='Times-Bold', fontSize=18, leading=23, textColor=NAVY,
        alignment=TA_CENTER, spaceBefore=8, spaceAfter=12, keepWithNext=True
    )
    styles['ChapterTitle'] = ParagraphStyle(
        'ChapterTitle', fontName='Times-Bold', fontSize=21, leading=27, textColor=NAVY,
        alignment=TA_CENTER, spaceBefore=6, spaceAfter=16, keepWithNext=True
    )
    styles['H2'] = ParagraphStyle(
        'H2', fontName='Times-Bold', fontSize=13.4, leading=17, textColor=NAVY,
        alignment=TA_LEFT, spaceBefore=12, spaceAfter=7, keepWithNext=True
    )
    styles['Body'] = ParagraphStyle(
        'Body', fontName='Times-Roman', fontSize=11, leading=15.5, alignment=TA_JUSTIFY,
        textColor=colors.black, spaceAfter=7
    )
    styles['BodyNoJust'] = ParagraphStyle(
        'BodyNoJust', fontName='Times-Roman', fontSize=11, leading=15.5, alignment=TA_LEFT,
        textColor=colors.black, spaceAfter=7
    )
    styles['Caption'] = ParagraphStyle(
        'Caption', fontName='Times-Italic', fontSize=9.2, leading=12, alignment=TA_CENTER,
        textColor=DARK_GRAY, spaceBefore=4, spaceAfter=10
    )
    styles['TableText'] = ParagraphStyle(
        'TableText', fontName='Times-Roman', fontSize=9.3, leading=12, alignment=TA_LEFT
    )
    styles['TableHead'] = ParagraphStyle(
        'TableHead', fontName='Times-Bold', fontSize=9.5, leading=12, alignment=TA_CENTER,
        textColor=colors.white
    )
    # Reduced fontSize and leading to make the Table of Contents more compact (fits in 2 pages)
    styles['TOC'] = ParagraphStyle(
        'TOC', fontName='Times-Roman', fontSize=9.5, leading=11.5, alignment=TA_LEFT
    )
    styles['TOCBold'] = ParagraphStyle(
        'TOCBold', fontName='Times-Bold', fontSize=9.5, leading=11.5, alignment=TA_LEFT,
        textColor=NAVY
    )
    styles['ListItem'] = ParagraphStyle(
        'ListItem', fontName='Times-Roman', fontSize=10.5, leading=13.5, leftIndent=12,
        firstLineIndent=-8, spaceAfter=4
    )
    styles['SourceNote'] = ParagraphStyle(
        'SourceNote', fontName='Times-Italic', fontSize=8.5, leading=10.5,
        alignment=TA_CENTER, textColor=HexColor("#555555"), spaceAfter=8
    )
    return styles


def P(text, style):
    return Paragraph(text, style)


def add_section_title(story, key, title, refs, styles):
    story.append(PageMarker(key, refs))
    story.append(P(title, styles['H1']))
    story.append(HRFlowable(width="100%", thickness=0.6, color=ACCENT, spaceBefore=0, spaceAfter=14))


def para_list(texts, style):
    return [P(t, style) for t in texts]


def make_formal_table(data, col_widths=None, header=True, shade_rows=True, padding=5):
    # Added padding parameter to allow for highly compressed tables when necessary (like the Index)
    tbl = Table(data, colWidths=col_widths, hAlign='CENTER', repeatRows=1 if header else 0)
    style = [
        ('GRID', (0,0), (-1,-1), 0.35, HexColor("#B8C0CA")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ('TOPPADDING', (0,0), (-1,-1), padding),
        ('BOTTOMPADDING', (0,0), (-1,-1), padding),
    ]
    if header:
        style += [('BACKGROUND', (0,0), (-1,0), NAVY), ('TEXTCOLOR',(0,0),(-1,0), colors.white)]
    if shade_rows:
        for r in range(1 if header else 0, len(data)):
            if r % 2 == (1 if header else 0):
                style.append(('BACKGROUND', (0,r), (-1,r), HexColor("#F7F9FB")))
    tbl.setStyle(TableStyle(style))
    return tbl


def process_diagram():
    w, h = 450, 135
    d = Drawing(w, h)
    box_w, box_h = 92, 42
    y = 62
    xs = [8, 122, 236, 350]
    labels = ["Agricultural\nData", "ML/DL\nModel", "Yield\nForecast", "Decision\nSupport"]
    fills = [PALE_BLUE, PALE_GREEN, PALE_GOLD, HexColor("#EFEAF7")]
    for x, label, fill in zip(xs, labels, fills):
        d.add(Rect(x, y, box_w, box_h, rx=8, ry=8, strokeColor=ACCENT, strokeWidth=1.1, fillColor=fill))
        lines = label.split('\n')
        for i, line in enumerate(lines):
            d.add(String(x+box_w/2, y+26-12*i, line, fontName='Times-Bold', fontSize=9.5, textAnchor='middle', fillColor=NAVY))
    for x in xs[:-1]:
        ymid = y + box_h/2
        d.add(Line(x+box_w+4, ymid, x+box_w+22, ymid, strokeColor=ACCENT, strokeWidth=1.2))
        d.add(Polygon([x+box_w+22, ymid, x+box_w+15, ymid+4, x+box_w+15, ymid-4], fillColor=ACCENT, strokeColor=ACCENT))
    d.add(String(w/2, 118, "Data-driven crop yield prediction workflow", fontName='Times-Bold', fontSize=11, textAnchor='middle', fillColor=NAVY))
    d.add(String(w/2, 28, "Weather, soil, crop and remote sensing features are converted into localized yield intelligence.", fontName='Times-Roman', fontSize=9, textAnchor='middle', fillColor=DARK_GRAY))
    return DiagramFlowable(d, w, h)


def factors_diagram():
    # Fixed matching the uploaded screenshot: segmented center circle + colored quadrant nodes
    w, h = 450, 200
    d = Drawing(w, h)
    cx, cy = w/2, h/2 - 5
    
    d.add(String(w/2, h - 15, "Interacting factors influencing crop yield", fontName='Times-Bold', fontSize=12, textAnchor='middle', fillColor=NAVY))
    
    box_w, box_h = 92, 34
    
    # Coordinates mapping out top/bottom elements mimicking the screenshot
    nodes = [
        (cx - box_w/2 - 130, cy + 15, "Rainfall", PALE_GREEN),
        (cx - box_w/2, cy + 45, "Temperature", PALE_GOLD),
        (cx + box_w/2 + 40, cy + 15, "Soil Health", HexColor("#F2F0FA")),
        (cx - box_w/2 - 130, cy - 50, "Irrigation", PALE_GREEN),
        (cx - box_w/2, cy - 80, "Crop Variety", PALE_GOLD),
        (cx + box_w/2 + 40, cy - 50, "Pests & Diseases", HexColor("#F2F0FA"))
    ]
    
    # Draw connections to central node first so they lie beneath shapes
    for x, y, label, color in nodes:
        box_cx, box_cy = x + box_w/2, y + box_h/2
        d.add(Line(cx, cy, box_cx, box_cy, strokeColor=HexColor("#94A3B8"), strokeWidth=1.0))
        
    # Draw Segmented Central Circle structure seen in screenshot
    r = 38
    d.add(Circle(cx, cy, r, strokeColor=NAVY, strokeWidth=1.2, fillColor=PALE_BLUE))
    d.add(Line(cx - r, cy, cx + r, cy, strokeColor=NAVY, strokeWidth=0.6))
    d.add(Line(cx, cy - r, cx, cy + r, strokeColor=NAVY, strokeWidth=0.6))
    d.add(Circle(cx, cy, r*0.55, strokeColor=NAVY, strokeWidth=0.6, fillColor=colors.white))
    
    d.add(String(cx, cy + 3, "Crop", fontName='Times-Bold', fontSize=11, textAnchor='middle', fillColor=NAVY))
    d.add(String(cx, cy - 9, "Yield", fontName='Times-Bold', fontSize=11, textAnchor='middle', fillColor=NAVY))
    
    # Draw Sub-Nodes
    for x, y, label, color in nodes:
        d.add(Rect(x, y, box_w, box_h, rx=6, ry=6, strokeColor=NAVY, strokeWidth=0.8, fillColor=color))
        d.add(String(x + box_w/2, y + box_h/2 - 3.5, label, fontName='Times-Bold', fontSize=9.5, textAnchor='middle', fillColor=DARK_GRAY))
        
    return DiagramFlowable(d, w, h)


def clean_index_text(value):
    value = value.strip()
    value = value.replace('**', '')
    value = value.replace('—', '-')
    value = re.sub(r'\s+', ' ', value)
    return value


def load_index_entries(index_path=None):
    if index_path is None:
        candidates = [os.path.join(OUT_DIR, 'index.txt'), os.path.join(OUT_DIR, 'index(1).txt')]
        index_path = next((p for p in candidates if os.path.exists(p)), candidates[0])
    entries = []
    if not os.path.exists(index_path):
        return entries
    with open(index_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('|'):
                continue
            cells = [clean_index_text(c) for c in line.strip('|').split('|')]
            if len(cells) < 2:
                continue
            section, title = cells[0], cells[1]
            if not section or '---' in section or 'Section' in section:
                continue
            if not title or '---' in title or title.lower() == 'topic':
                continue
            entries.append((section, title))
    return entries


def safe_p(text, style):
    return Paragraph(xml_escape(str(text)), style)


def page_for_index_entry(section, title, plabel):
    title_key = title.lower()
    exact_title_pages = {
        'title page': '',
        'acknowledgement': plabel('ack'),
        'abstract': plabel('abstract'),
        'list of figures': plabel('list_figures'),
        'list of tables': plabel('list_tables'),
        'list of abbreviations': plabel('abbrev'),
    }
    if title_key in exact_title_pages:
        return exact_title_pages[title_key]
    completed_section_pages = {
        '1': plabel('chapter1'),
        '1.1': plabel('sec_1_1'),
        '1.2': plabel('sec_1_2'),
        '1.3': plabel('sec_1_3'),
        '1.4': plabel('sec_1_4'),
        '1.5': plabel('sec_1_5'),
        '2': plabel('chapter2'),
        '2.1': plabel('sec_2_1'),
        '2.2': plabel('sec_2_2'),
        '2.3': plabel('sec_2_3'),
        '2.4': plabel('sec_2_4'),
        '3': plabel('chapter3'),
        '3.1': plabel('sec_3_1'),
        '3.2': plabel('sec_3_2'),
        '3.3': plabel('sec_3_3'),
        '3.4': plabel('sec_3_4'),
        '3.5': plabel('sec_3_5'),
    }
    return completed_section_pages.get(section, '-')


def build_full_toc_rows(styles, plabel):
    rows = [[P('Section', styles['TableHead']), P('Title', styles['TableHead']), P('Page', styles['TableHead'])]]
    entries = load_index_entries()
    if not entries:
        entries = [
            ('-', 'Title Page'), ('-', 'Acknowledgement'), ('-', 'Abstract'),
            ('-', 'List of Figures'), ('-', 'List of Tables'), ('-', 'List of Abbreviations'),
            ('1', 'Introduction'), ('1.1', 'Agriculture as the Backbone of Indian Economy'),
            ('1.2', 'Evolution of Indian Agriculture'), ('1.3', 'Modern Challenges in Agriculture'),
            ('1.4', 'Need for Crop Yield Prediction'),
            ('1.5', 'Role of AI and Machine Learning in Precision Agriculture'),
        ]
    for section, title in entries:
        row_style = styles['TOCBold'] if re.fullmatch(r'\d+', section) else styles['TOC']
        if section == '-':
            row_style = styles['TOC']
        page_val = page_for_index_entry(section, title, plabel)
        rows.append([safe_p(section, row_style), safe_p(title, row_style), safe_p(page_val, row_style)])
    return rows

def ai_role_diagram(styles):
    data = [
        [P("Prediction", styles['TableHead']), P("Advisory", styles['TableHead']), P("Monitoring", styles['TableHead'])],
        [P("Forecasts expected yield before harvest using historical and real-time data.", styles['TableText']),
         P("Supports irrigation, fertilizer, sowing and risk-management decisions.", styles['TableText']),
         P("Uses weather records, soil data and satellite indicators to track crop condition.", styles['TableText'])],
        [P("Explainability", styles['TableHead']), P("Planning", styles['TableHead']), P("Sustainability", styles['TableHead'])],
        [P("XAI tools such as SHAP help explain why a model predicts a certain yield.", styles['TableText']),
         P("Helps government agencies, insurers and farmers prepare timely interventions.", styles['TableText']),
         P("Improves resource efficiency by reducing unnecessary water, fertilizer and pesticide use.", styles['TableText'])],
    ]
    tbl = Table(data, colWidths=[5.0*cm, 5.0*cm, 5.0*cm], hAlign='CENTER')
    tbl.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, HexColor("#B8C0CA")),
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('BACKGROUND', (0,2), (-1,2), ACCENT),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('BACKGROUND', (0,1), (-1,1), HexColor("#F7F9FB")),
        ('BACKGROUND', (0,3), (-1,3), HexColor("#FFFFFF")),
    ]))
    return tbl



def note_box(text, styles, title="Report Integration Note"):
    tbl = Table([[P(f"<b>{title}</b><br/>{text}", styles['BodyNoJust'])]], colWidths=[16.0*cm])
    tbl.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.75,ACCENT),
        ('BACKGROUND',(0,0),(-1,-1),HexColor("#F8FAFC")),
        ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
    ]))
    return tbl


def bullet_items(items, styles):
    return [P("- " + item, styles['ListItem']) for item in items]


def problem_context_diagram():
    w, h = 460, 160
    d = Drawing(w, h)
    d.add(String(w/2, h-15, "Problem framing for crop yield prediction", fontName='Times-Bold', fontSize=12, textAnchor='middle', fillColor=NAVY))
    
    # Main flow
    xs = [15, 125, 235, 345]
    labels = ["Uncertain\nField Conditions", "Fragmented\nAgricultural Data", "Prediction\nand Trust Gap", "Research\nObjectives"]
    fills = [PALE_GOLD, PALE_BLUE, HexColor("#F2F0FA"), PALE_GREEN]
    box_w, box_h, y = 95, 44, 70
    
    # Draw arrows first so they sit slightly under the boxes for a clean edge
    for x in xs[:-1]:
        ymid = y + box_h/2
        start_x = x + box_w
        end_x = start_x + 15
        d.add(Line(start_x, ymid, end_x, ymid, strokeColor=ACCENT, strokeWidth=1.2))
        d.add(Polygon([end_x, ymid, end_x-6, ymid+4, end_x-6, ymid-4], fillColor=ACCENT, strokeColor=ACCENT))

    # Draw boxes
    for x, label, fill in zip(xs, labels, fills):
        d.add(Rect(x, y, box_w, box_h, rx=8, ry=8, strokeColor=ACCENT, strokeWidth=1.1, fillColor=fill))
        for i, line in enumerate(label.split('\n')):
            d.add(String(x+box_w/2, y+27-12*i, line, fontName='Times-Bold', fontSize=9.2, textAnchor='middle', fillColor=NAVY))
            
    # Supporting labels neatly centered under boxes and arrows
    notes = ["climate", "soil", "crop stage", "explainability", "deployment"]
    nx = [62.5, 145, 230, 315, 392.5]
    for x, label in zip(nx, notes):
        d.add(Circle(x, 40, 15, strokeColor=HexColor("#94A3B8"), strokeWidth=0.8, fillColor=HexColor("#FFFFFF")))
        d.add(String(x, 37, label, fontName='Times-Roman', fontSize=7.5, textAnchor='middle', fillColor=DARK_GRAY))
        
    d.add(String(w/2, 12, "Chapter 2 converts the broad need for yield forecasting into measurable research objectives.", fontName='Times-Roman', fontSize=8.8, textAnchor='middle', fillColor=DARK_GRAY))
    return DiagramFlowable(d, w, h)


def data_silo_diagram():
    w, h = 460, 270
    d = Drawing(w, h)

    # Title and subtitle
    d.add(String(w/2, h-16, "Data fragmentation and the need for harmonization", fontName='Times-Bold', fontSize=13.5, textAnchor='middle', fillColor=NAVY))
    d.add(String(w/2, h-31, "Heterogeneous agricultural datasets become useful only when linked by shared spatial and crop-season identifiers.", fontName='Times-Roman', fontSize=8.2, textAnchor='middle', fillColor=DARK_GRAY))

    def arrow(x1, y1, x2, y2, color=HexColor("#8FA4C2"), width=1.0):
        d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=width))
        ang = math.atan2(y2-y1, x2-x1)
        ah = 7
        p1 = (x2, y2)
        p2 = (x2-ah*math.cos(ang-math.pi/7), y2-ah*math.sin(ang-math.pi/7))
        p3 = (x2-ah*math.cos(ang+math.pi/7), y2-ah*math.sin(ang+math.pi/7))
        d.add(Polygon([p1[0],p1[1],p2[0],p2[1],p3[0],p3[1]], fillColor=color, strokeColor=color))

    # central hub coords
    cx, cy = w/2, 130
    
    # Define Nodes (Adjusted to sit clear of the center circle)
    nodes = [
        (15, 185, 105, 40, "Weather", "IMD / rainfall / temperature", PALE_GOLD),
        (177, 205, 106, 40, "Soil", "profile / pH / nutrients", HexColor("#F7EFE4")),
        (340, 185, 105, 40, "Yield Records", "production / district series", HexColor("#EEF4F9")),
        (15, 75, 105, 40, "Remote Sensing", "NDVI / imagery / phenology", HexColor("#EEF7EF")),
        (177, 10, 106, 40, "Farmer Registry", "plot / holding / crop data", HexColor("#F6F0FA")),
        (340, 75, 105, 40, "Irrigation & Inputs", "water / seed / fertilizer", HexColor("#FDF4E8")),
    ]

    # Draw Arrows FIRST so they are layered beneath the boxes and the center circle
    for x, y, bw, bh, *_ in nodes:
        nx, ny = x+bw/2, y+bh/2
        dx, dy = cx - nx, cy - ny
        dist = math.hypot(dx, dy)
        # Calculate exactly where the arrow should stop (radius 52)
        end_x = cx - (dx/dist) * 54
        end_y = cy - (dy/dist) * 54
        arrow(nx, ny, end_x, end_y)

    # Draw central hub
    d.add(Circle(cx, cy, 52, strokeColor=NAVY, strokeWidth=1.4, fillColor=HexColor("#F6FAFF")))
    d.add(Circle(cx, cy, 36, strokeColor=ACCENT, strokeWidth=0.9, fillColor=PALE_BLUE))
    d.add(String(cx, cy+14, "Unified", fontName='Times-Bold', fontSize=10.4, textAnchor='middle', fillColor=NAVY))
    d.add(String(cx, cy+2, "Common Geocode", fontName='Times-Bold', fontSize=10.8, textAnchor='middle', fillColor=NAVY))
    d.add(String(cx, cy-11, "district • season • crop", fontName='Times-Roman', fontSize=7.7, textAnchor='middle', fillColor=DARK_GRAY))

    # Supporting key chips (placed cleanly below the center circle)
    chip_specs = [(cx-75, 62, "Geo ID"), (cx-25, 62, "Year"), (cx+25, 62, "Crop"), (cx+75, 62, "Season")]
    for x, y, label in chip_specs:
        d.add(Rect(x-22, y, 44, 16, rx=8, ry=8, strokeColor=HexColor("#9EB0C9"), strokeWidth=0.7, fillColor=HexColor("#FFFFFF")))
        d.add(String(x, y+5, label, fontName='Times-Roman', fontSize=7.2, textAnchor='middle', fillColor=DARK_GRAY))

    # Draw Nodes on top
    for x, y, bw, bh, title, subtitle, fill in nodes:
        d.add(Rect(x, y, bw, bh, rx=8, ry=8, strokeColor=ACCENT, strokeWidth=1.0, fillColor=fill))
        d.add(Rect(x, y+bh-12, bw, 12, rx=8, ry=8, strokeColor=None, fillColor=HexColor("#FFFFFF")))
        d.add(String(x+bw/2, y+bh-10, title, fontName='Times-Bold', fontSize=8.9, textAnchor='middle', fillColor=NAVY))
        d.add(String(x+bw/2, y+10, subtitle, fontName='Times-Roman', fontSize=6.9, textAnchor='middle', fillColor=DARK_GRAY))

    return DiagramFlowable(d, w, h)


def prisma_flow_diagram():
    w, h = 460, 310
    d = Drawing(w, h)
    d.add(String(w/2, h-16, "PRISMA-based article selection process", fontName='Times-Bold', fontSize=13.5, textAnchor='middle', fillColor=NAVY))
    d.add(String(w/2, h-31, "Structured literature screening for crop yield prediction studies", fontName='Times-Roman', fontSize=8.2, textAnchor='middle', fillColor=DARK_GRAY))

    def node(x, y, width, height, title, body_lines, fill, title_color=NAVY):
        d.add(Rect(x, y, width, height, rx=9, ry=9, strokeColor=ACCENT, strokeWidth=1.0, fillColor=fill))
        d.add(Rect(x, y+height-12, width, 12, rx=9, ry=9, strokeColor=None, fillColor=HexColor("#FFFFFF")))
        d.add(String(x+width/2, y+height-18, title, fontName='Times-Bold', fontSize=9.4, textAnchor='middle', fillColor=title_color))
        body_y = y + height - 33
        for i, line in enumerate(body_lines):
            d.add(String(x+width/2, body_y-10*i, line, fontName='Times-Roman', fontSize=8.1, textAnchor='middle', fillColor=DARK_GRAY))

    def arrow(x1, y1, x2, y2, color=ACCENT, width=1.15):
        d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=width))
        ang = math.atan2(y2-y1, x2-x1)
        ah = 7
        p1 = (x2, y2)
        p2 = (x2-ah*math.cos(ang-math.pi/7), y2-ah*math.sin(ang-math.pi/7))
        p3 = (x2-ah*math.cos(ang+math.pi/7), y2-ah*math.sin(ang+math.pi/7))
        d.add(Polygon([p1[0],p1[1],p2[0],p2[1],p3[0],p3[1]], fillColor=color, strokeColor=color))

    # Down Arrows
    arrow(145, 250, 145, 237)
    arrow(145, 195, 145, 182)
    arrow(145, 140, 145, 127)
    arrow(145, 85, 145, 72)
    
    # Right Arrows for Exclusions
    arrow(225, 161, 275, 161)
    arrow(225, 106, 275, 106)

    # Restructured nodes to a clear single-column flow with branching right-side exclusions
    node(65, 250, 160, 42, "Records identified", ["Scopus, Web of Science, IEEE", "n = 828"], PALE_GOLD)
    node(65, 195, 160, 42, "Duplicates removed", ["records after de-duplication", "n = 564"], HexColor("#F8ECEC"))
    node(65, 140, 160, 42, "Records screened", ["title and abstract screening", "n = 564"], PALE_BLUE)
    node(275, 140, 150, 42, "Records excluded", ["title and abstract mismatch", "n = 224"], HexColor("#F8ECEC"))
    node(65, 85, 160, 42, "Full-text assessed", ["for eligibility", "n = 340"], HexColor("#F3F8FD"))
    node(275, 85, 150, 42, "Full-text excluded", ["methodological / scope reasons", "n = 117"], HexColor("#F8ECEC"))
    node(65, 30, 160, 42, "Studies included", ["qualitative synthesis", "n = 223"], PALE_GREEN)

    # Stage tags on left
    stage_data = [(25, 261, "1"), (25, 206, "2"), (25, 151, "3"), (25, 41, "4")]
    for x, y, num in stage_data:
        d.add(Circle(x, y+10, 12, strokeColor=ACCENT, strokeWidth=1.0, fillColor=PALE_BLUE))
        d.add(String(x, y+6, num, fontName='Times-Bold', fontSize=9, textAnchor='middle', fillColor=NAVY))

    # subtle divider under title
    d.add(Line(90, h-39, w-90, h-39, strokeColor=HexColor("#CBD5E3"), strokeWidth=0.8))
    return DiagramFlowable(d, w, h)

def article_distribution_diagram():
    w, h = 450, 190
    d = Drawing(w, h)
    d.add(String(w/2, h-14, "Distribution of selected articles by type", fontName='Times-Bold', fontSize=12, textAnchor='middle', fillColor=NAVY))
    items = [("Journal Articles", 81), ("Conference Papers", 14), ("Robust Websites", 3), ("Book Chapters", 2)]
    x0, y0, maxw = 112, 130, 245
    for idx,(label,val) in enumerate(items):
        y = y0 - idx*29
        d.add(String(24, y+5, label, fontName='Times-Roman', fontSize=9, fillColor=DARK_GRAY))
        d.add(Rect(x0, y, maxw, 14, strokeColor=HexColor("#D0D7DE"), strokeWidth=0.4, fillColor=HexColor("#F5F7FA")))
        d.add(Rect(x0, y, maxw*val/100.0, 14, strokeColor=ACCENT, strokeWidth=0.3, fillColor=ACCENT if idx==0 else HexColor("#9FB5CC")))
        d.add(String(x0+maxw+12, y+3, f"{val}%", fontName='Times-Bold', fontSize=9, fillColor=NAVY))
    d.add(String(w/2, 18, "Journal articles dominate the review base, so the formal report should treat conference papers and web sources as supporting evidence.", fontName='Times-Roman', fontSize=8.2, textAnchor='middle', fillColor=DARK_GRAY))
    return DiagramFlowable(d, w, h)


def year_growth_chart():
    w, h = 450, 210
    d = Drawing(w, h)
    d.add(String(w/2, h-14, "Year-wise growth of ML research in agriculture", fontName='Times-Bold', fontSize=12, textAnchor='middle', fillColor=NAVY))
    labels = [">2015", "2016", "2017", "2018", "2019", "2020", "2021"]
    vals = [50, 15, 16, 32, 51, 48, 6]
    x0, y0 = 56, 42
    plot_w, plot_h = 345, 130
    # axes and grid
    d.add(Line(x0, y0, x0, y0+plot_h, strokeColor=HexColor("#6B7280"), strokeWidth=0.8))
    d.add(Line(x0, y0, x0+plot_w, y0, strokeColor=HexColor("#6B7280"), strokeWidth=0.8))
    for tick in [0,10,20,30,40,50]:
        y = y0 + plot_h*tick/55.0
        d.add(Line(x0-3, y, x0+plot_w, y, strokeColor=HexColor("#E5E7EB"), strokeWidth=0.35))
        d.add(String(x0-25, y-3, str(tick), fontName='Times-Roman', fontSize=7.6, fillColor=DARK_GRAY))
    bar_w = plot_w/len(vals)*0.58
    gap = plot_w/len(vals)
    for i,(lab,val) in enumerate(zip(labels, vals)):
        x = x0 + i*gap + gap*0.22
        bh = plot_h*val/55.0
        d.add(Rect(x, y0, bar_w, bh, strokeColor=ACCENT, strokeWidth=0.4, fillColor=HexColor("#7FA2C5")))
        d.add(String(x+bar_w/2, y0-12, lab, fontName='Times-Roman', fontSize=7.5, textAnchor='middle', fillColor=DARK_GRAY))
        d.add(String(x+bar_w/2, y0+bh+4, str(val), fontName='Times-Roman', fontSize=7.2, textAnchor='middle', fillColor=DARK_GRAY))
    d.add(String(14, y0+plot_h/2, "No. of publications", fontName='Times-Roman', fontSize=8, textAnchor='middle', fillColor=DARK_GRAY, transform=[0,1,-1,0,18,y0+plot_h/2-45]))
    return DiagramFlowable(d, w, h)

def research_gap_diagram():
    w, h = 460, 280
    d = Drawing(w, h)
    d.add(String(w/2, h-16, "From literature gaps to the proposed framework", fontName='Times-Bold', fontSize=13.5, textAnchor='middle', fillColor=NAVY))
    d.add(String(w/2, h-31, "Key weaknesses in existing studies motivate a more integrated and explainable solution.", fontName='Times-Roman', fontSize=8.2, textAnchor='middle', fillColor=DARK_GRAY))

    def box(x, y, width, height, title, lines, fill, title_color=NAVY):
        d.add(Rect(x, y, width, height, rx=9, ry=9, strokeColor=ACCENT, strokeWidth=1.0, fillColor=fill))
        d.add(String(x+width/2, y+height-15, title, fontName='Times-Bold', fontSize=9.7, textAnchor='middle', fillColor=title_color))
        for i, line in enumerate(lines):
            d.add(String(x+width/2, y+height-27-10*i, line, fontName='Times-Roman', fontSize=8.0, textAnchor='middle', fillColor=DARK_GRAY))

    def arrow(x1, y1, x2, y2, color=HexColor("#8FA4C2"), width=1.0):
        d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=width))
        ang = math.atan2(y2-y1, x2-x1)
        ah = 7
        p1 = (x2, y2)
        p2 = (x2-ah*math.cos(ang-math.pi/7), y2-ah*math.sin(ang-math.pi/7))
        p3 = (x2-ah*math.cos(ang+math.pi/7), y2-ah*math.sin(ang+math.pi/7))
        d.add(Polygon([p1[0],p1[1],p2[0],p2[1],p3[0],p3[1]], fillColor=color, strokeColor=color))

    # Changed from 2x2 grid to a clear vertical stack to prevent text overflow
    gap_boxes = [
        (20, 200, 180, 40, "Fragmented data", ["weather, soil & yield poorly linked"], HexColor("#FBF3E1")),
        (20, 150, 180, 40, "Limited features", ["often ignore soil or remote sensing"], HexColor("#F6F0E3")),
        (20, 100, 180, 40, "Black-box models", ["high accuracy, low interpretability"], HexColor("#F6EDF6")),
        (20, 50, 180, 40, "Deployment gap", ["results rarely reach farmers"], HexColor("#EEF5FB")),
    ]
    
    # Draw arrows BEFORE boxes to hide the line origin points
    for x, y, bw, bh, *_ in gap_boxes:
        arrow(x+bw, y+bh/2, 250, 145)

    # Draw Left Stack Boxes
    for x, y, bw, bh, title, lines, fill in gap_boxes:
        box(x, y, bw, bh, title, lines, fill)

    # Central synthesis node on the right
    box(250, 100, 190, 90, "Need for a stronger", ["research framework that is", "integrated, localized, and", "explainable"], HexColor("#EFF7F1"), title_color=NAVY)

    # Framework strip at bottom
    d.add(Rect(30, 12, 400, 26, rx=10, ry=10, strokeColor=NAVY, strokeWidth=1.0, fillColor=HexColor("#F7FAFD")))
    d.add(String(230, 20, "Proposed response: harmonized datasets + ensemble/deep models + XAI + deployment", fontName='Times-Bold', fontSize=8.5, textAnchor='middle', fillColor=NAVY))

    return DiagramFlowable(d, w, h)

def add_chapter_heading(story, key, number, title, refs, styles):
    story.append(PageMarker(key, refs))
    story.append(P(f"CHAPTER {number}", styles['ChapterTitle']))
    story.append(P(title, styles['ChapterTitle']))
    story.append(HRFlowable(width="75%", thickness=1.0, color=ACCENT, spaceBefore=0, spaceAfter=18, hAlign='CENTER'))


def add_chapters_2_3(story, refs, styles):
    # Chapter 2
    add_chapter_heading(story, 'chapter2', 2, "PROBLEM STATEMENT AND OBJECTIVES", refs, styles)
    story += para_list([
        "After establishing the importance of agriculture and the need for crop yield prediction, the next step is to convert the broad project theme into a clear research problem. The central issue is that Indian farmers and agricultural planners operate under high uncertainty. Crop yield depends on weather, soil health, irrigation, crop variety, pest pressure, and crop growth stage, but these variables change across districts and seasons.",
        "The IEEE source paper summarizes the problem as a lack of accessible, localized, and accurate prediction models that combine real-time meteorological data with granular soil and crop characteristics. For the main project report, this chapter expands that short problem statement into four academic sections: limitations of traditional forecasting, fragmentation of agricultural data, black-box nature of AI models, and objectives of the proposed research.",
        "The chapter should act as a bridge between the introduction and the literature review. It should not yet describe the complete methodology in detail. Instead, it should explain why the proposed work is necessary and what the research intends to achieve. Detailed datasets, algorithms, evaluation metrics, and deployment architecture should be expanded in later chapters."
    ], styles['Body'])
    story.append(PageMarker('fig_2_1', refs))
    story.append(problem_context_diagram())
    story.append(P("Figure 2.1: Problem framing for crop yield prediction research", styles['Caption']))

    story.append(PageMarker('sec_2_1', refs))
    story.append(P("2.1 Limitations of Traditional Yield Forecasting", styles['H2']))
    story += para_list([
        "Traditional yield forecasting in India depends on field experience, generalized weather forecasts, historical averages, manual surveys, and crop-cutting experiments. These approaches have practical value, but they are limited when agriculture becomes more climate-sensitive and data-intensive. Manual estimation is usually slow, and official yield statistics often become available only after harvesting. This delay reduces their usefulness for early warning, insurance planning, procurement, storage, and farmer advisory services.",
        "Another limitation is that conventional statistical models often assume simple or linear relationships between variables. In real agricultural conditions, rainfall, temperature, soil moisture, crop stage, and management practices interact in a non-linear way. For example, high rainfall may increase yield during one crop stage but damage yield during another. Similarly, temperature stress during flowering can reduce yield even if rainfall is adequate. Traditional models may miss these interactions because they cannot learn complex patterns from multiple data sources.",
        "For the main report, this section should clearly distinguish between traditional estimation and machine learning based estimation. The purpose is not to reject traditional knowledge, but to show that modern forecasting requires timely, localized, and multi-factor analysis."
    ], styles['Body'])
    story.append(PageMarker('table_2_1', refs))
    story.append(P("Table 2.1: Limitations of traditional crop yield forecasting", styles['Caption']))
    table_2_1 = [
        [P("Limitation", styles['TableHead']), P("Explanation", styles['TableHead']), P("Effect on Decision-Making", styles['TableHead'])],
        [P("Delayed estimates", styles['TableText']), P("Official estimates and crop-cutting based results often become available late in the season or after harvest.", styles['TableText']), P("Limits early planning for procurement, storage, insurance, and relief measures.", styles['TableText'])],
        [P("Generalized forecasts", styles['TableText']), P("Weather advisories are often broad and may not capture district-level or field-level variation.", styles['TableText']), P("Farmers may not receive location-specific yield risk information.", styles['TableText'])],
        [P("Linear assumptions", styles['TableText']), P("Many statistical approaches cannot capture complex non-linear relationships among crop, weather, and soil factors.", styles['TableText']), P("Prediction accuracy may decline under changing climate conditions.", styles['TableText'])],
        [P("Manual workload", styles['TableText']), P("Field surveys require time, labour, coordination, and financial resources.", styles['TableText']), P("Large-scale forecasting becomes costly and slow.", styles['TableText'])],
    ]
    story.append(make_formal_table(table_2_1, col_widths=[3.6*cm, 6.8*cm, 5.6*cm], header=True, shade_rows=True, padding=4))

    story.append(PageMarker('sec_2_2', refs))
    story.append(P("2.2 Data Fragmentation in Indian Agriculture", styles['H2']))
    story += para_list([
        "A strong machine learning model requires data that is accurate, integrated, and aligned across space and time. In Indian agriculture, relevant data is distributed across several sources: meteorological records, soil health information, crop statistics, satellite imagery, irrigation data, farmer registries, and market or input records. These datasets are often collected by different departments and stored in separate formats.",
        "The major challenge is the absence of consistent linking keys. If weather data is stored at grid level, soil data at village level, yield data at district level, and farmer information at plot level, the model cannot directly combine them. A common geographic and temporal reference is therefore necessary. In the final report, this part should explain the need for common geocodes, standardized crop-season labels, and careful data harmonization before model training.",
        "Data fragmentation also affects model fairness and reliability. When some regions have better data quality than others, the model may perform well in data-rich regions but poorly in data-poor areas. This is especially important for smallholder farmers because they are often located in regions where data collection is less consistent."
    ], styles['Body'])
    story.append(PageMarker('fig_2_2', refs))
    story.append(data_silo_diagram())
    story.append(P("Figure 2.2: Fragmented agricultural datasets connected through common geocoding", styles['Caption']))
    story.append(PageMarker('table_2_2', refs))
    story.append(P("Table 2.2: Major agricultural data sources and integration challenges", styles['Caption']))
    table_2_2 = [
        [P("Data Source", styles['TableHead']), P("Useful Information", styles['TableHead']), P("Integration Challenge", styles['TableHead'])],
        [P("Weather records", styles['TableText']), P("Rainfall, temperature, humidity, extreme events, and seasonal trends.", styles['TableText']), P("Different spatial resolution and missing local station coverage.", styles['TableText'])],
        [P("Soil data", styles['TableText']), P("Nutrients, pH, organic matter, moisture, and soil type.", styles['TableText']), P("May be available at field, village, or district scale with inconsistent update frequency.", styles['TableText'])],
        [P("Yield statistics", styles['TableText']), P("Historical crop area, production, and yield by crop and season.", styles['TableText']), P("Often aggregated and released after harvest.", styles['TableText'])],
        [P("Remote sensing", styles['TableText']), P("Vegetation indices, crop growth patterns, and spatial crop monitoring.", styles['TableText']), P("Cloud cover, image resolution, and alignment with crop calendars.", styles['TableText'])],
    ]
    story.append(make_formal_table(table_2_2, col_widths=[3.4*cm, 6.1*cm, 6.5*cm], header=True, shade_rows=True, padding=4))

    story.append(PageMarker('sec_2_3', refs))
    story.append(P("2.3 Black-Box Nature of AI Models", styles['H2']))
    story += para_list([
        "Advanced machine learning and deep learning models can give high accuracy, but they often behave like black boxes. A black-box model produces a prediction without clearly explaining why that prediction was made. This creates a trust problem in agriculture because farmers, extension workers, and policymakers need understandable reasons before changing crop plans, irrigation schedules, fertilizer use, or insurance decisions.",
        "In crop yield prediction, explainability is not only a technical issue; it is also a practical requirement. If a model predicts low yield, users should know whether the risk is caused by rainfall deficit, heat stress, soil condition, crop stage, or data uncertainty. Explainable AI methods such as SHAP can estimate how strongly each feature contributed to a specific prediction. Such interpretation helps users verify whether the model is using agronomically meaningful relationships instead of accidental patterns.",
        "Therefore, the main report should include black-box model limitations before introducing Explainable Artificial Intelligence in later chapters. This creates a logical reason for adding SHAP analysis and feature importance interpretation after the model evaluation chapters."
    ], styles['Body'])
    story.append(PageMarker('sec_2_4', refs))
    story.append(P("2.4 Objectives of the Proposed Research", styles['H2']))
    story += para_list([
        "The objectives of this project are designed to address the limitations identified above. The proposed research should not be presented only as a model-building exercise. It should be presented as a complete decision-support framework that begins with data collection and ends with interpretable yield intelligence for farmers and policymakers.",
        "The objectives below expand the short IEEE paper objectives into a formal project-report structure. They can be used directly in the main report, and later chapters can be mapped back to these objectives."
    ], styles['Body'])
    story.append(PageMarker('table_2_3', refs))
    story.append(P("Table 2.3: Objectives of the proposed research", styles['Caption']))
    table_2_3 = [
        [P("Objective", styles['TableHead']), P("Formal Description", styles['TableHead']), P("Where it will be addressed", styles['TableHead'])],
        [P("Data harmonization", styles['TableText']), P("Collect, clean, align, and pre-process agricultural, weather, soil, and remote sensing data.", styles['TableText']), P("Chapters 4 to 6", styles['TableText'])],
        [P("Model comparison", styles['TableText']), P("Evaluate traditional regression, machine learning, ensemble learning, and hybrid deep learning models.", styles['TableText']), P("Chapters 7 to 8", styles['TableText'])],
        [P("Explainability", styles['TableText']), P("Use XAI methods to identify important agronomic features and explain model predictions.", styles['TableText']), P("Chapter 9", styles['TableText'])],
        [P("Evaluation", styles['TableText']), P("Assess performance using RMSE, R2 score, prediction intervals, and uncertainty analysis.", styles['TableText']), P("Chapter 10 and 11", styles['TableText'])],
        [P("Deployment direction", styles['TableText']), P("Suggest how the system can support national digital agriculture platforms and real-world advisories.", styles['TableText']), P("Chapters 12 to 14", styles['TableText'])],
    ]
    story.append(make_formal_table(table_2_3, col_widths=[3.3*cm, 8.0*cm, 4.7*cm], header=True, shade_rows=True, padding=4))
    story.append(Spacer(1, 0.08*inch))
    story.append(note_box("In the main report PDF, Chapter 2 should be inserted immediately after Section 1.5. Keep it problem-focused: do not overload it with algorithm equations or dataset screenshots. Those details should remain in methodology, dataset, model, and results chapters.", styles))
    story.append(PageBreak())

    # Chapter 3
    add_chapter_heading(story, 'chapter3', 3, "LITERATURE REVIEW", refs, styles)
    story += para_list([
        "A literature review explains how previous researchers have attempted to solve crop yield prediction problems and where the proposed project can contribute. In the IEEE source paper, the literature review is presented in a compact form with a PRISMA flow diagram, article-type distribution, publication-year trend, and a comparative literature table. For the main project report, this compact content should be expanded into a formal chapter with separate subsections from 3.1 to 3.5.",
        "The literature indicates a clear movement from simple statistical models toward ensemble machine learning and deep learning methods. Random Forest, XGBoost, Extra Trees, Artificial Neural Networks, CNN-based models, and CNN-LSTM architectures are frequently used because they can capture non-linear relationships in weather, soil, and crop data. However, recurring limitations remain: fragmented datasets, weak localization, lack of explainability, limited temporal modeling, and difficulty in real-world deployment.",
        "This chapter therefore performs two roles. First, it summarizes relevant studies. Second, it uses those studies to justify the proposed project direction."
    ], styles['Body'])

    story.append(PageMarker('sec_3_1', refs))
    story.append(P("3.1 PRISMA-Based Article Selection", styles['H2']))
    story += para_list([
        "A PRISMA-based selection process is useful when the literature review includes many papers from different databases. PRISMA helps show how articles were identified, screened, excluded, and finally included for qualitative analysis. In the source paper, records were identified from major databases such as Scopus, Web of Science, and IEEE. Duplicate records were removed, titles and abstracts were screened, full texts were assessed, and a final set of articles was selected for synthesis.",
        "For the main report, this subsection should not only display the flow diagram but also explain why articles were selected. The inclusion criteria may include relevance to crop yield prediction, use of machine learning or deep learning, use of agricultural or weather datasets, and availability of performance observations. The exclusion criteria may include duplicate records, weak methodological description, non-agricultural prediction tasks, or articles without model evaluation."
    ], styles['Body'])
    story.append(PageMarker('fig_3_1', refs))
    story.append(prisma_flow_diagram())
    story.append(P("Figure 3.1: PRISMA-based article selection for crop yield prediction literature", styles['Caption']))
    story.append(PageMarker('table_3_1', refs))
    story.append(P("Table 3.1: Suggested PRISMA inclusion and exclusion criteria for the main report", styles['Caption']))
    table_3_1 = [
        [P("Criteria Type", styles['TableHead']), P("Criteria", styles['TableHead']), P("Purpose", styles['TableHead'])],
        [P("Inclusion", styles['TableText']), P("Studies on crop yield prediction, agricultural forecasting, ML, DL, XAI, remote sensing, or climate-based yield estimation.", styles['TableText']), P("Keeps the review focused on the project problem.", styles['TableText'])],
        [P("Inclusion", styles['TableText']), P("Studies reporting datasets, algorithms, evaluation metrics, or limitations.", styles['TableText']), P("Supports comparison and gap identification.", styles['TableText'])],
        [P("Exclusion", styles['TableText']), P("Duplicate articles, unrelated agricultural topics, incomplete records, or articles without enough method details.", styles['TableText']), P("Improves quality and avoids repetition.", styles['TableText'])],
        [P("Exclusion", styles['TableText']), P("Sources that only discuss general agriculture without predictive modeling.", styles['TableText']), P("Prevents the chapter from becoming too broad.", styles['TableText'])],
    ]
    story.append(make_formal_table(table_3_1, col_widths=[3.1*cm, 8.2*cm, 4.7*cm], header=True, shade_rows=True, padding=4))

    story.append(PageMarker('sec_3_2', refs))
    story.append(P("3.2 Distribution of Selected Research Articles", styles['H2']))
    story += para_list([
        "The selected literature can be grouped by source type. The source paper indicates that journal articles form the majority of the reviewed literature, while conference papers, robust websites, and book chapters form smaller supporting categories. This is important because journal articles usually contain detailed methodology and peer-reviewed evaluation, while conference papers often present emerging methods and recent technical experiments.",
        "For the final report, this subsection should be used to demonstrate that the literature review is not random. It should show that the project is grounded mainly in academic studies, but also considers selected technical resources where they are relevant to digital agriculture deployment or recent AI practices."
    ], styles['Body'])
    story.append(PageMarker('fig_3_2', refs))
    story.append(article_distribution_diagram())
    story.append(P("Figure 3.2: Distribution of selected research articles by type", styles['Caption']))

    story.append(PageMarker('sec_3_3', refs))
    story.append(P("3.3 Year-Wise Growth of ML Research in Agriculture", styles['H2']))
    story += para_list([
        "Machine learning research in agriculture has grown sharply in recent years. This rise is linked to the availability of public datasets, improved satellite imagery, better computational resources, and open-source machine learning libraries. Earlier studies often focused on regression or simple classification, while recent work increasingly uses ensemble learning, deep learning, hybrid architectures, and explainability methods.",
        "In the main report, the year-wise chart should be interpreted carefully. The exact counts are less important than the trend: crop yield prediction has become a fast-growing research area because agricultural systems now generate more digital data than before. This supports the relevance of the proposed project."
    ], styles['Body'])
    story.append(PageMarker('fig_3_3', refs))
    story.append(year_growth_chart())
    story.append(P("Figure 3.3: Year-wise growth of reviewed ML agriculture publications", styles['Caption']))

    story.append(PageMarker('sec_3_4', refs))
    story.append(P("3.4 Comparative Study of Existing Research Papers", styles['H2']))
    story += para_list([
        "A comparative study helps identify which algorithms, datasets, and limitations appear repeatedly in previous work. The reviewed studies show that ensemble models such as Random Forest and XGBoost often perform strongly on tabular agricultural datasets. Deep learning models, especially CNN-RNN or CNN-LSTM type architectures, are useful when spatial and temporal patterns need to be captured. However, high accuracy alone is not enough for agricultural decision support unless the model is interpretable, localized, and connected to usable data pipelines.",
        "The following table expands the compact IEEE literature table into a project-report format. It is intentionally written in concise academic language so it can be inserted directly into the main report."
    ], styles['Body'])
    story.append(PageMarker('table_3_2', refs))
    story.append(P("Table 3.2: Comparative literature review of crop yield prediction studies", styles['Caption']))
    small = ParagraphStyle('SmallTableText', parent=styles['TableText'], fontSize=7.4, leading=9.0)
    small_head = ParagraphStyle('SmallTableHead', parent=styles['TableHead'], fontSize=7.6, leading=9.0)
    table_3_2 = [
        [P("Study", small_head), P("Dataset or Scope", small_head), P("Algorithms", small_head), P("Observation", small_head), P("Limitation", small_head)],
        [P("Pallavi et al. (2021)", small), P("Crop, area, yield, temperature, and humidity data", small), P("XGBoost, Logistic Regression, Random Forest, KNN", small), P("Random Forest produced the best reported classification performance.", small), P("Accuracy was moderate and input diversity was limited.", small)],
        [P("Mohsen et al. (2021)", small), P("US corn belt data from 1984 to 2018 with weather, soil, and yield variables", small), P("Linear Regression, LASSO, LightGBM, Random Forest, XGBoost", small), P("Adding crop simulation variables reduced RMSE.", small), P("Study context differs from Indian smallholder conditions.", small)],
        [P("Khaki et al. (2020)", small), P("County-level corn and soybean yield data from 2004 to 2018", small), P("Random Forest, DFNN, CNN, regression tree, LASSO, Ridge", small), P("Deep learning captured spatial-temporal dependencies effectively.", small), P("High computational complexity and lower interpretability.", small)],
        [P("Nishant et al. (2020)", small), P("Indian government dataset with state, district, season, crop, area, and production", small), P("LASSO, ElasticNet, Kernel Ridge, Stacking", small), P("Stacking approach achieved strong error reduction.", small), P("Important weather and soil features were simplified.", small)],
        [P("Tiwari et al. (2019)", small), P("Geospatial data with NDVI, SPI, and vegetation indices", small), P("EBPNN, Spiking Neural Network", small), P("Vegetation indices improved model robustness.", small), P("Region-specific and dependent on remote sensing quality.", small)],
        [P("Shah et al. (2018)", small), P("Dataset with rainfall, temperature, climatic condition, and crop type", small), P("AdaBoost, Decision Tree, Random Forest, KNN", small), P("Tree-based ensemble methods showed high predictive performance.", small), P("Limited feature variety and possible generalization issues.", small)],
        [P("Gandhi et al. (2016)", small), P("Rice yield data with temperature, precipitation, and evapotranspiration", small), P("Artificial Neural Network", small), P("ANN captured non-linear patterns better than regression.", small), P("Limited dataset size and explainability.", small)],
        [P("Paul et al. (2015)", small), P("Soil behaviour data with N, P, K, pH, and micronutrients", small), P("Naive Bayes, KNN", small), P("Useful for classification-type agricultural tasks.", small), P("More suitable for crop recommendation than yield regression.", small)],
        [P("Shastry et al. (2015)", small), P("Biomass, rainfall, radiation, and soil moisture data", small), P("ANFIS", small), P("Combined fuzzy logic with predictive modeling.", small), P("Implementation complexity and limited scalability.", small)],
        [P("Recent ML studies (2025)", small), P("Climatic, soil nutrient, and NDVI-based large datasets", small), P("Deep Learning, Random Forest, SVM", small), P("Large datasets and remote sensing improved accuracy.", small), P("Deployment and farmer-facing interpretation remain open issues.", small)],
    ]
    t = Table(table_3_2, colWidths=[3.1*cm, 4.1*cm, 3.2*cm, 3.1*cm, 2.5*cm], hAlign='CENTER', repeatRows=1)
    t.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.3,HexColor("#B8C0CA")),
        ('BACKGROUND',(0,0),(-1,0),NAVY),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
    ]))
    story.append(t)

    story.append(PageMarker('sec_3_5', refs))
    story.append(P("3.5 Research Gaps Identified", styles['H2']))
    story += para_list([
        "The comparative review shows that many studies achieve good prediction performance, but several gaps remain. These gaps are important because a project report should not only repeat previous models; it should explain why the proposed approach is needed. The main gaps are related to data integration, localized prediction, temporal crop-stage modeling, explainability, uncertainty estimation, and deployment in real farming systems.",
        "The proposed research can be positioned as a response to these gaps. It should combine harmonized agricultural datasets, strong machine learning models, deep learning for temporal patterns, and XAI methods for trust. It should also discuss how the model could later connect with digital agriculture platforms."
    ], styles['Body'])
    story.append(PageMarker('fig_3_4', refs))
    story.append(research_gap_diagram())
    story.append(P("Figure 3.4: Research gaps leading to the proposed framework", styles['Caption']))
    story.append(PageMarker('table_3_3', refs))
    story.append(P("Table 3.3: Research gaps and how the proposed project addresses them", styles['Caption']))
    table_3_3 = [
        [P("Research Gap", styles['TableHead']), P("Why it matters", styles['TableHead']), P("Proposed Direction in Main Report", styles['TableHead'])],
        [P("Fragmented datasets", styles['TableText']), P("Weather, soil, crop, and remote sensing data are often stored separately.", styles['TableText']), P("Use a harmonized pre-processing pipeline with common crop-season and geographic identifiers.", styles['TableText'])],
        [P("Limited localization", styles['TableText']), P("National or state-level averages may not represent district-level yield behaviour.", styles['TableText']), P("Emphasize district-level and crop-specific forecasting where data permits.", styles['TableText'])],
        [P("Weak temporal modeling", styles['TableText']), P("Crop response depends on growth stages, not only annual averages.", styles['TableText']), P("Use temporal features and later discuss CNN-LSTM for sequential weather and crop-stage patterns.", styles['TableText'])],
        [P("Black-box predictions", styles['TableText']), P("Users may not trust unexplained model outputs.", styles['TableText']), P("Add SHAP-based feature importance and prediction explanation in the XAI chapter.", styles['TableText'])],
        [P("Uncertainty not communicated", styles['TableText']), P("A single yield value does not show prediction risk.", styles['TableText']), P("Include prediction intervals or uncertainty quantification in evaluation chapters.", styles['TableText'])],
        [P("Deployment gap", styles['TableText']), P("Academic models often stop at performance metrics.", styles['TableText']), P("Connect the framework to national digital public infrastructure and farmer advisories.", styles['TableText'])],
    ]
    story.append(make_formal_table(table_3_3, col_widths=[3.4*cm, 5.5*cm, 7.1*cm], header=True, shade_rows=True, padding=4))
    story.append(Spacer(1, 0.10*inch))
    insertion_data = [
        [P("Part to add in main report", styles['TableHead']), P("Recommended content", styles['TableHead'])],
        [P("Chapter 2", styles['TableText']), P("Keep as the formal problem foundation. Use it to explain why traditional forecasting, fragmented data, and black-box models create the research need.", styles['TableText'])],
        [P("Chapter 3.1 to 3.3", styles['TableText']), P("Use PRISMA, article-type distribution, and year-wise trend as evidence that the review is systematic and current.", styles['TableText'])],
        [P("Chapter 3.4", styles['TableText']), P("Place the comparative table after the trend discussion. It should be allowed to split across pages because literature tables are naturally long.", styles['TableText'])],
        [P("Chapter 3.5", styles['TableText']), P("End the literature review with research gaps. This gives a smooth transition to Chapter 4 Proposed Methodology.", styles['TableText'])],
    ]
    story.append(P("Speculative Main-Report Insertion Plan", styles['H2']))
    story.append(make_formal_table(insertion_data, col_widths=[5.2*cm, 10.8*cm], header=True, shade_rows=True, padding=4))
    story.append(Spacer(1, 0.1*inch))
    story.append(note_box("The next chapter should begin with Proposed Methodology. It should use the research gaps from Section 3.5 as justification for dataset acquisition, feature engineering, pre-processing, model selection, and evaluation metrics.", styles, title="Transition Note"))

def build_story(refs, page_refs=None):
    styles = make_styles()
    if page_refs is None:
        page_refs = {}
    chap_start = page_refs.get('chapter1')
    def plabel(key):
        return page_label(page_refs.get(key), chap_start)
    story = []

    # Title Page
    story.append(Spacer(1, 1.0*inch))
    story.append(P("CROP YIELD PREDICTION<br/>USING MACHINE LEARNING", styles['Title']))
    story.append(P("Towards Smart Agriculture in India", styles['Subtitle']))
    story.append(Spacer(1, 0.15*inch))
    story.append(HRFlowable(width="68%", thickness=1.0, color=ACCENT, spaceBefore=8, spaceAfter=18, hAlign='CENTER'))
    story.append(P("A Project Report", styles['CoverSmall']))
    story.append(P("Submitted in partial fulfilment of academic project requirements", styles['CoverSmall']))
    story.append(Spacer(1, 0.45*inch))
    title_box = Table([[P("Academic Project Report<br/><br/>Prepared for formal submission and presentation", styles['CoverSmall'])]], colWidths=[11.5*cm])
    title_box.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.8,ACCENT),
        ('BACKGROUND',(0,0),(-1,-1),HexColor("#F8FAFC")),
        ('TOPPADDING',(0,0),(-1,-1),18),('BOTTOMPADDING',(0,0),(-1,-1),18),
    ]))
    story.append(title_box)
    story.append(Spacer(1, 0.65*inch))
    story.append(P("Topic Area: Artificial Intelligence, Machine Learning and Precision Agriculture", styles['CoverSmall']))
    story.append(P("Academic Session: 2025 - 2026", styles['CoverSmall']))
    story.append(Spacer(1, 0.7*inch))
    story.append(P("Note: Student, guide, department and institution details may be inserted on the final title page whenever required.", styles['SourceNote']))
    story.append(PageBreak())

    # Acknowledgement
    add_section_title(story, 'ack', "ACKNOWLEDGEMENT", refs, styles)
    story += para_list([
        "The author expresses sincere gratitude to the faculty members, project guide, department, and institution for providing the academic support, encouragement, and learning environment required for preparing this project report.",
        "The completion of this project would not have been possible without the conceptual guidance received during the study of Artificial Intelligence, Machine Learning, and their applications in agriculture. The support of classmates, friends, and well-wishers is also gratefully acknowledged.",
        "The author is thankful to the researchers and organizations whose academic work and agricultural data resources have helped in understanding the practical importance of crop yield prediction. Their contributions provide a strong foundation for studying how data-driven systems can support farmers, policymakers, and agricultural planners.",
        "Finally, heartfelt thanks are extended to family members for their constant motivation, patience, and moral support throughout the preparation of this project report."
    ], styles['Body'])
    story.append(Spacer(1, 0.25*inch))
    story.append(P("<b>Author</b>", styles['BodyNoJust']))
    story.append(PageBreak())

    # Abstract
    add_section_title(story, 'abstract', "ABSTRACT", refs, styles)
    story += para_list([
        "Agriculture is one of the most significant sectors of the Indian economy and plays a vital role in food security, rural employment, and national development. However, modern Indian agriculture faces increasing uncertainty due to climate change, irregular rainfall, soil degradation, water scarcity, pest attacks, and delays in traditional crop estimation systems. As crop yield depends on several interacting environmental and agronomic factors, conventional forecasting approaches often fail to provide accurate and timely predictions.",
        "This project report presents the concept of crop yield prediction using Machine Learning and Artificial Intelligence. The study focuses on how historical crop data, weather data, soil parameters, rainfall, temperature, remote sensing information, and other agricultural features can be analysed to forecast expected crop production. Machine Learning models such as Random Forest, XGBoost, Extra Trees Regressor, Support Vector Regression, and deep learning models such as CNN-LSTM can identify complex non-linear relationships between crop yield and environmental variables.",
        "The report also emphasizes the importance of Explainable Artificial Intelligence in agriculture. Techniques such as SHAP can help interpret the contribution of factors like temperature, precipitation, soil health, humidity, and crop type in the final prediction. Such explainability is important because farmers and agricultural officers need understandable and trustworthy recommendations before adopting AI-based systems.",
        "By supporting timely, localized, and data-driven decision-making, crop yield prediction can help farmers improve planning, reduce risk, and optimize resources. At the policy level, it can assist in food supply planning, crop insurance, disaster response, and sustainable agricultural development. The project therefore supports the transition from traditional experience-based farming towards AI-enabled precision agriculture."
    ], styles['Body'])
    story.append(PageBreak())

    # Contents
    add_section_title(story, 'contents', "TABLE OF CONTENTS", refs, styles)
    story.append(P("Note: Page numbers are shown for completed sections. Remaining entries are included as the planned full report index and can be filled as the report is expanded.", styles['SourceNote']))
    toc_rows = build_full_toc_rows(styles, plabel)
    # Using padding=2 significantly shrinks the row height, allowing standard indexes to fit within 2 pages.
    story.append(make_formal_table(toc_rows, col_widths=[2.2*cm, 12.2*cm, 2.0*cm], header=True, shade_rows=True, padding=2))
    story.append(PageBreak())

    # Lists
    add_section_title(story, 'list_figures', "LIST OF FIGURES", refs, styles)
    fig_rows = [
        [P("Figure No.", styles['TableHead']), P("Title", styles['TableHead']), P("Page", styles['TableHead'])],
        [P("Figure 1.1", styles['TOC']), P("Conceptual workflow of crop yield prediction using Machine Learning", styles['TOC']), P(plabel('fig_1_1'), styles['TOC'])],
        [P("Figure 1.2", styles['TOC']), P("Major factors influencing crop yield in India", styles['TOC']), P(plabel('fig_1_2'), styles['TOC'])],
        [P("Figure 1.3", styles['TOC']), P("Role of AI and Machine Learning in precision agriculture", styles['TOC']), P(plabel('fig_1_3'), styles['TOC'])],
        [P("Figure 2.1", styles['TOC']), P("Problem framing for crop yield prediction research", styles['TOC']), P(plabel('fig_2_1'), styles['TOC'])],
        [P("Figure 2.2", styles['TOC']), P("Fragmented agricultural datasets connected through common geocoding", styles['TOC']), P(plabel('fig_2_2'), styles['TOC'])],
        [P("Figure 3.1", styles['TOC']), P("PRISMA-based article selection for crop yield prediction literature", styles['TOC']), P(plabel('fig_3_1'), styles['TOC'])],
        [P("Figure 3.2", styles['TOC']), P("Distribution of selected research articles by type", styles['TOC']), P(plabel('fig_3_2'), styles['TOC'])],
        [P("Figure 3.3", styles['TOC']), P("Year-wise growth of reviewed ML agriculture publications", styles['TOC']), P(plabel('fig_3_3'), styles['TOC'])],
        [P("Figure 3.4", styles['TOC']), P("Research gaps leading to the proposed framework", styles['TOC']), P(plabel('fig_3_4'), styles['TOC'])],
    ]
    story.append(make_formal_table(fig_rows, col_widths=[3.0*cm, 11.4*cm, 2.0*cm], header=True, shade_rows=True))
    story.append(Spacer(1, 0.20*inch))

    story.append(PageMarker('list_tables', refs))
    story.append(P("LIST OF TABLES", styles['H1']))
    story.append(HRFlowable(width="100%", thickness=0.6, color=ACCENT, spaceBefore=0, spaceAfter=14))
    tbl_rows = [
        [P("Table No.", styles['TableHead']), P("Title", styles['TableHead']), P("Page", styles['TableHead'])],
        [P("Table 1.1", styles['TOC']), P("Contribution of agriculture to the Indian economy and society", styles['TOC']), P(plabel('table_1_1'), styles['TOC'])],
        [P("Table 1.2", styles['TOC']), P("Major challenges in modern Indian agriculture", styles['TOC']), P(plabel('table_1_2'), styles['TOC'])],
        [P("Table 1.3", styles['TOC']), P("Traditional crop yield prediction vs Machine Learning based prediction", styles['TOC']), P(plabel('table_1_3'), styles['TOC'])],
        [P("Table 2.1", styles['TOC']), P("Limitations of traditional crop yield forecasting", styles['TOC']), P(plabel('table_2_1'), styles['TOC'])],
        [P("Table 2.2", styles['TOC']), P("Major agricultural data sources and integration challenges", styles['TOC']), P(plabel('table_2_2'), styles['TOC'])],
        [P("Table 2.3", styles['TOC']), P("Objectives of the proposed research", styles['TOC']), P(plabel('table_2_3'), styles['TOC'])],
        [P("Table 3.1", styles['TOC']), P("Suggested PRISMA inclusion and exclusion criteria for the main report", styles['TOC']), P(plabel('table_3_1'), styles['TOC'])],
        [P("Table 3.2", styles['TOC']), P("Comparative literature review of crop yield prediction studies", styles['TOC']), P(plabel('table_3_2'), styles['TOC'])],
        [P("Table 3.3", styles['TOC']), P("Research gaps and how the proposed project addresses them", styles['TOC']), P(plabel('table_3_3'), styles['TOC'])],
    ]
    story.append(make_formal_table(tbl_rows, col_widths=[3.0*cm, 11.4*cm, 2.0*cm], header=True, shade_rows=True))
    story.append(PageBreak())

    add_section_title(story, 'abbrev', "LIST OF ABBREVIATIONS", refs, styles)
    abbrev_data = [
        [P("Abbreviation", styles['TableHead']), P("Full Form", styles['TableHead'])],
        [P("AI", styles['TableText']), P("Artificial Intelligence", styles['TableText'])],
        [P("ML", styles['TableText']), P("Machine Learning", styles['TableText'])],
        [P("DL", styles['TableText']), P("Deep Learning", styles['TableText'])],
        [P("CNN", styles['TableText']), P("Convolutional Neural Network", styles['TableText'])],
        [P("LSTM", styles['TableText']), P("Long Short-Term Memory", styles['TableText'])],
        [P("XAI", styles['TableText']), P("Explainable Artificial Intelligence", styles['TableText'])],
        [P("SHAP", styles['TableText']), P("SHapley Additive exPlanations", styles['TableText'])],
        [P("RMSE", styles['TableText']), P("Root Mean Square Error", styles['TableText'])],
        [P("NDVI", styles['TableText']), P("Normalized Difference Vegetation Index", styles['TableText'])],
        [P("SAR", styles['TableText']), P("Synthetic Aperture Radar", styles['TableText'])],
        [P("IMD", styles['TableText']), P("India Meteorological Department", styles['TableText'])],
        [P("ICRISAT", styles['TableText']), P("International Crops Research Institute for the Semi-Arid Tropics", styles['TableText'])],
        [P("DPI", styles['TableText']), P("Digital Public Infrastructure", styles['TableText'])],
    ]
    story.append(make_formal_table(abbrev_data, col_widths=[4.0*cm, 11.8*cm], header=True, shade_rows=True))
    story.append(PageBreak())

    # Chapter 1
    story.append(PageMarker('chapter1', refs))
    story.append(P("CHAPTER 1", styles['ChapterTitle']))
    story.append(P("INTRODUCTION", styles['ChapterTitle']))
    story.append(HRFlowable(width="75%", thickness=1.0, color=ACCENT, spaceBefore=0, spaceAfter=18, hAlign='CENTER'))
    story += para_list([
        "Agriculture has always been a fundamental pillar of India's economy and social structure. It provides livelihood to a large portion of the population, supports rural employment, contributes to national food security, and supplies raw materials to many agro-based industries. In a country where agriculture is closely connected with income, culture, and local development, improvement in agricultural productivity has a direct influence on economic stability and public welfare.",
        "Despite its importance, agriculture remains highly dependent on natural conditions. Crop production is affected by rainfall, temperature, humidity, soil nutrients, irrigation, pest attacks, crop variety, and farming practices. These factors rarely act independently. Instead, they interact in complex and sometimes unpredictable ways. For example, the same amount of rainfall may produce different results depending on soil moisture, crop stage, temperature, and irrigation availability. This makes crop yield prediction a challenging but essential task.",
        "Traditional crop yield estimation generally depends on past experience, manual surveys, generalized weather forecasts, and crop-cutting experiments. Although these methods are useful, they are often time-consuming and may not provide accurate forecasts early enough for planning. In contrast, Machine Learning systems can analyse large datasets and learn patterns that are difficult to identify manually. Such systems can combine weather records, soil data, historical yield data, satellite observations, and crop-specific features to estimate future crop production more effectively.",
        "The project titled <b>Crop Yield Prediction using Machine Learning</b> aims to study how Artificial Intelligence and Machine Learning can support smart agriculture in India. The main idea is to use data-driven models to predict crop yield, reduce uncertainty, support farmers, and improve decision-making for policymakers and agricultural agencies. This chapter introduces the background of Indian agriculture, its evolution, modern challenges, the need for yield prediction, and the role of AI and ML in precision agriculture."
    ], styles['Body'])

    story.append(PageMarker('fig_1_1', refs))
    story.append(process_diagram())
    story.append(P("Figure 1.1: Conceptual workflow of crop yield prediction using Machine Learning", styles['Caption']))

    # 1.1
    story.append(PageMarker('sec_1_1', refs))
    story.append(P("1.1 Agriculture as the Backbone of Indian Economy", styles['H2']))
    story += para_list([
        "Agriculture is known as the backbone of the Indian economy because it supports livelihood, employment, food security, industrial raw material supply, and rural development. A significant portion of India's population depends directly or indirectly on agriculture. Farming activities also create demand for seeds, fertilizers, machinery, storage, transport, food processing, and marketing services, thereby supporting several connected sectors.",
        "The economic importance of agriculture can be understood from its contribution to Gross Domestic Product, employment generation, and allied industries. The agricultural sector supplies raw materials to industries such as textiles, sugar, vegetable oils, jute, food processing, and dairy-based products. As a result, agricultural growth has a multiplier effect on the wider economy.",
        "Agriculture also plays a critical role in national food security. A stable and productive farming system ensures that the country can meet the food requirements of its growing population. When crop production declines due to drought, flood, pest infestation, or poor planning, it can affect food prices, farmer income, rural purchasing power, and public welfare. Therefore, accurate crop planning and yield forecasting are essential for national development.",
        "In India, the majority of small and marginal farmers operate with limited land, limited capital, and high dependence on seasonal rainfall. For such farmers, even a small error in crop planning can create financial risk. Scientific yield prediction can help reduce this uncertainty by providing early information about expected production and possible risks."
    ], styles['Body'])

    story.append(PageMarker('table_1_1', refs))
    story.append(P("Table 1.1: Contribution of agriculture to the Indian economy and society", styles['Caption']))
    table_1_1 = [
        [P("Area of Contribution", styles['TableHead']), P("Explanation", styles['TableHead'])],
        [P("Food Security", styles['TableText']), P("Ensures availability of staple crops such as rice, wheat, pulses, oilseeds and other food products for the population.", styles['TableText'])],
        [P("Employment", styles['TableText']), P("Provides livelihood to farmers, labourers, traders, transporters and workers in allied rural activities.", styles['TableText'])],
        [P("Industrial Support", styles['TableText']), P("Supplies raw materials to textile, sugar, food processing, vegetable oil, jute and dairy industries.", styles['TableText'])],
        [P("Rural Economy", styles['TableText']), P("Influences rural income, local markets, purchasing power, credit demand and social development.", styles['TableText'])],
        [P("National Planning", styles['TableText']), P("Helps government agencies plan procurement, storage, exports, imports, subsidies and crop insurance.", styles['TableText'])],
    ]
    story.append(make_formal_table(table_1_1, col_widths=[4.2*cm, 11.8*cm], header=True, shade_rows=True))
    story.append(Spacer(1, 0.1*inch))

    # 1.2
    story.append(PageMarker('sec_1_2', refs))
    story.append(P("1.2 Evolution of Indian Agriculture", styles['H2']))
    story += para_list([
        "The evolution of Indian agriculture is closely connected with the history of Indian civilization. Ancient farming practices can be traced to the Indus Valley Civilization, where crops such as wheat, barley, rice and cotton were cultivated using early irrigation and settlement-based farming systems. These practices show that agriculture was not only an occupation but also a foundation of social organization and economic exchange.",
        "During the medieval period, agriculture developed further through improved irrigation, crop rotation, and the introduction of new crops. Farming practices were shaped by local climate, river systems, soil fertility, and regional knowledge. Traditional farmers developed practical understanding of sowing seasons, monsoon behaviour, crop suitability, and soil management through experience accumulated over generations.",
        "The colonial period brought major changes to Indian agriculture. Land revenue systems, cash crop pressures, and lack of balanced investment affected agricultural productivity and farmer welfare. After independence, India faced the urgent need to increase food production for a growing population. This led to major policy interventions and the introduction of modern agricultural technologies.",
        "The Green Revolution of the 1960s and 1970s became a turning point. High-yielding varieties of seeds, chemical fertilizers, pesticides, irrigation facilities, and mechanized farming practices significantly increased food grain production. It helped India move towards food self-sufficiency. However, the long-term effects of intensive farming also created new problems such as groundwater depletion, soil fatigue, and excessive dependence on chemical inputs in some regions.",
        "The present stage of Indian agriculture is moving towards digital and data-driven farming. Technologies such as satellite monitoring, remote sensing, soil sensors, mobile advisories, Artificial Intelligence, Machine Learning and Digital Public Infrastructure are gradually becoming part of agricultural planning. This transition represents a movement from input-intensive agriculture to knowledge-intensive and precision-based agriculture."
    ], styles['Body'])

    # 1.3
    story.append(PageMarker('sec_1_3', refs))
    story.append(P("1.3 Modern Challenges in Agriculture", styles['H2']))
    story += para_list([
        "Modern Indian agriculture faces several interconnected challenges. Climate change has increased uncertainty in rainfall, temperature, and seasonal patterns. Irregular monsoons, droughts, floods, heat waves and unexpected weather events can disturb crop growth at critical stages such as sowing, flowering, grain filling and harvesting.",
        "Soil degradation is another important challenge. Continuous cultivation, unbalanced fertilizer use, erosion, declining organic matter and poor soil management can reduce fertility over time. In many regions, water scarcity and groundwater depletion are becoming serious problems. Crops that require intensive irrigation place additional pressure on already stressed water resources.",
        "Pest and disease outbreaks also create uncertainty. Changing weather conditions can alter pest behaviour and increase crop vulnerability. Farmers often respond with chemical pesticides, but excessive pesticide use can raise production cost, harm the environment, and affect crop quality. Therefore, early warning and data-driven advisory systems are needed to reduce such risks.",
        "Another challenge is the fragmentation of agricultural data. Weather data, soil information, land records, crop statistics, irrigation data and satellite observations are often collected by different agencies and stored in separate systems. Without proper integration, it becomes difficult to build accurate and localized prediction models. Modern crop yield prediction requires harmonized and high-quality datasets."
    ], styles['Body'])

    story.append(KeepTogether([
        PageMarker('fig_1_2', refs),
        factors_diagram(),
        P("Figure 1.2: Major factors influencing crop yield in India", styles['Caption'])
    ]))

    story.append(PageMarker('table_1_2', refs))
    story.append(P("Table 1.2: Major challenges in modern Indian agriculture", styles['Caption']))
    table_1_2 = [
        [P("Challenge", styles['TableHead']), P("Description", styles['TableHead']), P("Possible Impact", styles['TableHead'])],
        [P("Climate Variability", styles['TableText']), P("Irregular rainfall, heat waves, floods and droughts disturb crop cycles.", styles['TableText']), P("Yield loss and higher production risk.", styles['TableText'])],
        [P("Soil Degradation", styles['TableText']), P("Declining fertility, erosion and imbalance of nutrients reduce soil productivity.", styles['TableText']), P("Lower crop growth and reduced long-term sustainability.", styles['TableText'])],
        [P("Water Scarcity", styles['TableText']), P("Excessive dependence on groundwater and inefficient irrigation create pressure on water resources.", styles['TableText']), P("Reduced irrigation reliability and higher cultivation cost.", styles['TableText'])],
        [P("Pests and Diseases", styles['TableText']), P("Changing climate can increase pest attacks and disease spread.", styles['TableText']), P("Crop damage and increased pesticide use.", styles['TableText'])],
        [P("Data Fragmentation", styles['TableText']), P("Agricultural information is often stored in separate systems without integration.", styles['TableText']), P("Difficulty in building accurate localized prediction models.", styles['TableText'])],
    ]
    story.append(make_formal_table(table_1_2, col_widths=[3.6*cm, 7.1*cm, 5.3*cm], header=True, shade_rows=True))

    # 1.4
    story.append(PageMarker('sec_1_4', refs))
    story.append(P("1.4 Need for Crop Yield Prediction", styles['H2']))
    story += para_list([
        "Crop yield prediction refers to the estimation of expected crop production before or during the growing season. It is important because agricultural decisions are time-sensitive. Farmers need timely information to decide what to sow, when to irrigate, how much fertilizer to apply, when to protect crops from pests, and how to plan harvesting and marketing. If expected yield is known in advance, risk can be managed more effectively.",
        "For government agencies, crop yield prediction is useful in food supply planning, procurement, storage management, import-export decisions, subsidy allocation, disaster response, and crop insurance. It helps identify regions where production may fall below expected levels so that timely interventions can be planned. For insurance companies, yield prediction supports risk assessment and claim estimation. For researchers, it helps understand the relationship between climate, soil and crop productivity.",
        "Traditional yield estimation methods such as manual field surveys and crop-cutting experiments have practical limitations. They can be expensive, labour-intensive and delayed. In many cases, official estimates become available only after harvest. Such delayed information is useful for record keeping but less useful for early intervention. Modern agriculture requires advance estimates that can support proactive planning.",
        "Machine Learning based yield prediction can reduce this gap by using historical and real-time data. By analysing rainfall, temperature, soil characteristics, vegetation indices, crop type and past yield records, ML models can identify patterns and generate timely forecasts. These forecasts may not eliminate uncertainty completely, but they can provide better guidance than purely intuition-based decisions."
    ], styles['Body'])

    story.append(PageMarker('table_1_3', refs))
    story.append(P("Table 1.3: Traditional crop yield prediction vs Machine Learning based prediction", styles['Caption']))
    table_1_3 = [
        [P("Aspect", styles['TableHead']), P("Traditional Approach", styles['TableHead']), P("Machine Learning Based Approach", styles['TableHead'])],
        [P("Data Used", styles['TableText']), P("Past experience, manual surveys and generalized weather information.", styles['TableText']), P("Historical yield, weather, soil, crop, satellite and sensor-based data.", styles['TableText'])],
        [P("Time of Estimate", styles['TableText']), P("Often available near or after harvest.", styles['TableText']), P("Can generate early-season and mid-season forecasts.", styles['TableText'])],
        [P("Pattern Detection", styles['TableText']), P("Limited ability to capture complex non-linear relationships.", styles['TableText']), P("Can learn hidden and non-linear relationships among multiple variables.", styles['TableText'])],
        [P("Scalability", styles['TableText']), P("Difficult to scale quickly across districts and crop types.", styles['TableText']), P("Can be scaled digitally when reliable data pipelines are available.", styles['TableText'])],
        [P("Decision Support", styles['TableText']), P("Useful but often delayed and broad in nature.", styles['TableText']), P("Supports localized, timely and data-driven advisories.", styles['TableText'])],
    ]
    story.append(make_formal_table(table_1_3, col_widths=[3.2*cm, 6.4*cm, 6.4*cm], header=True, shade_rows=True))

    # 1.5
    story.append(PageMarker('sec_1_5', refs))
    story.append(P("1.5 Role of AI and Machine Learning in Precision Agriculture", styles['H2']))
    story += para_list([
        "Artificial Intelligence and Machine Learning play an important role in the development of precision agriculture. Precision agriculture means using data, technology and scientific analysis to make farming decisions more accurate, localized and efficient. Instead of applying the same agricultural practice everywhere, precision agriculture helps provide location-specific and crop-specific recommendations.",
        "Machine Learning models can process large agricultural datasets and identify relationships between crop yield and different influencing factors. For example, rainfall, maximum and minimum temperature, soil nutrients, humidity, irrigation, crop variety and vegetation indices can be used as input features. The model learns from past records and estimates expected yield for future conditions. This is especially useful because crop yield depends on complex and non-linear interactions among many variables.",
        "Different ML algorithms can be used for crop yield prediction. Multiple Linear Regression provides a simple baseline. Support Vector Regression and K-Nearest Neighbour can model more complex patterns. Ensemble methods such as Random Forest, XGBoost and Extra Trees Regressor are effective for tabular agricultural data because they combine multiple decision trees to improve accuracy and stability. Deep learning models such as CNN-LSTM are useful when spatial and temporal patterns need to be captured from weather sequences, crop stages and remote sensing information.",
        "AI can also support farmers through automated advisories. A prediction system can warn about possible yield reduction, suggest irrigation planning, identify pest risk, and support fertilizer decisions. When connected with mobile applications or digital agriculture platforms, these predictions can reach farmers in a practical form. Policymakers can use the same information for district-level planning, food security monitoring and insurance-related decisions.",
        "A major requirement for AI adoption in agriculture is trust. Farmers and agricultural officers may not accept predictions if the model behaves like a black box. Explainable AI addresses this issue by showing which factors influenced the prediction. For example, SHAP analysis can indicate whether rainfall, temperature, soil health or humidity contributed more strongly to a predicted yield value. This makes the system more transparent and useful for real-world decision-making.",
        "Thus, AI and Machine Learning can transform Indian agriculture from reactive and experience-based farming to proactive and data-driven precision agriculture. The goal is not to replace farmer knowledge, but to strengthen it with timely insights, accurate forecasts and scientific decision support."
    ], styles['Body'])

    story.append(PageMarker('fig_1_3', refs))
    story.append(ai_role_diagram(styles))
    story.append(P("Figure 1.3: Role of AI and Machine Learning in precision agriculture", styles['Caption']))
    story.append(Spacer(1, 0.12*inch))
    conclusion_box_data = [[P("<b>Chapter Summary</b><br/>This chapter explained the importance of agriculture in India, the historical evolution of farming, current agricultural challenges, the need for crop yield prediction, and the role of AI and ML in precision agriculture. The next chapters can build on this foundation by presenting the problem statement, objectives, literature review, methodology, datasets, models, evaluation metrics and results.", styles['BodyNoJust'])]]
    box = Table(conclusion_box_data, colWidths=[16.0*cm])
    box.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.8,ACCENT),
        ('BACKGROUND',(0,0),(-1,-1),HexColor("#F8FAFC")),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
    ]))
    story.append(box)
    story.append(PageBreak())
    add_chapters_2_3(story, refs, styles)
    return story


def on_page_factory(chapter1_start=None):
    def on_page(canvas, doc):
        page = canvas.getPageNumber()
        canvas.saveState()
        # Header except title page
        if page > 1:
            canvas.setFont('Times-Roman', 8.7)
            canvas.setFillColor(HexColor("#555555"))
            canvas.drawString(LEFT, PAGE_HEIGHT - 1.35*cm, "Crop Yield Prediction using Machine Learning")
            canvas.drawRightString(PAGE_WIDTH - RIGHT, PAGE_HEIGHT - 1.35*cm, "Project Report")
            canvas.setStrokeColor(HexColor("#B8C0CA"))
            canvas.setLineWidth(0.4)
            canvas.line(LEFT, PAGE_HEIGHT - 1.48*cm, PAGE_WIDTH - RIGHT, PAGE_HEIGHT - 1.48*cm)
        # Footer page number except title page
        if page > 1:
            if chapter1_start and page >= chapter1_start:
                label = str(page - chapter1_start + 1)
            elif chapter1_start:
                label = roman(page - 1)
            else:
                label = str(page)
            canvas.setFont('Times-Roman', 9)
            canvas.setFillColor(HexColor("#444444"))
            canvas.drawCentredString(PAGE_WIDTH/2, 1.15*cm, label)
        canvas.restoreState()
    return on_page


def build_pdf(path, page_refs=None):
    refs = {}
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=LEFT, rightMargin=RIGHT,
        topMargin=TOP, bottomMargin=BOTTOM,
        title="Crop Yield Prediction using Machine Learning - Project Report to Section 3.5"
    )
    story = build_story(refs, page_refs=page_refs)
    chapter1_start = page_refs.get('chapter1') if page_refs else None
    doc.build(story, onFirstPage=on_page_factory(chapter1_start), onLaterPages=on_page_factory(chapter1_start))
    return refs

if __name__ == "__main__":
    refs1 = build_pdf(TEMP_PDF, page_refs={})
    # Build final using pass 1 refs to fill TOC/list page numbers and reset chapter numbering.
    refs2 = build_pdf(FINAL_PDF, page_refs=refs1)
    # Save page refs for debugging
    with open(os.path.join(OUT_DIR, "_report_page_refs.txt"), "w") as f:
        f.write("PASS1\n")
        for k in sorted(refs1):
            f.write(f"{k}: {refs1[k]}\n")
        f.write("\nPASS2\n")
        for k in sorted(refs2):
            f.write(f"{k}: {refs2[k]}\n")
    print(FINAL_PDF)
