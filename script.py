# VERSION: v3-correct-diagram-compact-index
# Purpose: Generate the Crop Yield Prediction project report PDF from Title Page to Section 1.5.
# Includes: full Table of Contents from index.txt (compacted to 2 pages), page numbers, and fixed Figure 1.2 layout.
# Run: python make_report.py
# Output: Crop_Yield_Prediction_Project_Report_v3.pdf

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
TEMP_PDF = os.path.join(OUT_DIR, "_project_report_pass1.pdf")
FINAL_PDF = os.path.join(OUT_DIR, "Crop_Yield_Prediction_Project_Report_v3.pdf")

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
        index_path = os.path.join(OUT_DIR, 'index.txt')
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
        title="Crop Yield Prediction using Machine Learning - Project Report"
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
