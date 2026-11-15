"""
MaisMap — 7-slide NASA Space Apps 2026 presentation generator.
Run: python docs/demo/build_presentation.py
Outputs: docs/demo/MaisMap_NASA_Space_Apps_2026.pptx
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

OUT = os.path.join(os.path.dirname(__file__), "MaisMap_NASA_Space_Apps_2026.pptx")

# Brand colours
GREEN  = RGBColor(0x27, 0xAE, 0x60)
DARK   = RGBColor(0x1A, 0x1A, 0x2E)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE = RGBColor(0xF3, 0x9C, 0x12)
RED    = RGBColor(0xE7, 0x4C, 0x3C)
LGREY  = RGBColor(0xF4, 0xF6, 0xF7)
BLUE   = RGBColor(0x21, 0x8C, 0xBE)

W = Inches(13.33)
H = Inches(7.5)


def prs() -> Presentation:
    p = Presentation()
    p.slide_width  = W
    p.slide_height = H
    return p


def blank(p: Presentation):
    return p.slides.add_slide(p.slide_layouts[6])


def bg(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def txb(slide, text, x, y, w, h, size=18, bold=False,
        color=WHITE, align=PP_ALIGN.LEFT, wrap=True):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return tb


def rect(slide, x, y, w, h, fill: RGBColor, line=None):
    from pptx.util import Pt as Pt2
    shp = slide.shapes.add_shape(1, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line:
        shp.line.color.rgb = line
    else:
        shp.line.fill.background()
    return shp


def hline(slide, y, color=GREEN):
    r = rect(slide, Inches(0.5), y, Inches(12.33), Inches(0.04), color)
    return r


# ── SLIDE 1 — TITLE ──────────────────────────────────────────────────────────
def slide1(p):
    s = blank(p)
    bg(s, DARK)
    rect(s, 0, 0, W, Inches(0.08), GREEN)
    rect(s, 0, H - Inches(0.08), W, Inches(0.08), GREEN)

    txb(s, "🌽", Inches(0.6), Inches(0.5), Inches(1.2), Inches(1.2), size=54)
    txb(s, "MaïsMap", Inches(1.9), Inches(0.45), Inches(10), Inches(1.4),
        size=60, bold=True, color=GREEN)
    txb(s, "Climate & Soil Intelligence for Smarter Agriculture",
        Inches(1.9), Inches(1.75), Inches(10), Inches(0.8),
        size=24, color=WHITE)

    hline(s, Inches(2.7))

    txb(s, "NASA Space Apps Challenge 2026",
        Inches(0.6), Inches(2.9), Inches(12), Inches(0.6),
        size=20, bold=True, color=ORANGE)
    txb(s, "Challenge: Field Shift — Adapting Farms with NASA Data",
        Inches(0.6), Inches(3.5), Inches(12), Inches(0.55),
        size=17, color=WHITE)
    txb(s, "Team GeoWorks  |  Yaoundé Local Event, Cameroon",
        Inches(0.6), Inches(4.1), Inches(12), Inches(0.55),
        size=17, color=WHITE)
    txb(s, "github.com/princeraoulenix/MaisMap",
        Inches(0.6), Inches(4.7), Inches(12), Inches(0.55),
        size=15, color=BLUE)

    rect(s, Inches(0.6), Inches(5.5), Inches(12.13), Inches(1.5),
         RGBColor(0x0D, 0x0D, 0x1E), RGBColor(0x27, 0xAE, 0x60))
    txb(s, "Northern Cameroon  |  60 grid cells  |  NASA POWER + ISRIC SoilGrids  |  2020–2023",
        Inches(0.7), Inches(5.65), Inches(12), Inches(0.5),
        size=13, color=LGREY, align=PP_ALIGN.CENTER)
    txb(s, "Python · Streamlit · Folium · GeoJSON · QGIS",
        Inches(0.7), Inches(6.15), Inches(12), Inches(0.5),
        size=13, color=LGREY, align=PP_ALIGN.CENTER)


# ── SLIDE 2 — THE TEAM ───────────────────────────────────────────────────────
def slide2(p):
    s = blank(p)
    bg(s, DARK)
    rect(s, 0, 0, W, Inches(0.08), GREEN)

    txb(s, "Team GeoWorks", Inches(0.6), Inches(0.2), Inches(12), Inches(0.7),
        size=36, bold=True, color=GREEN)
    txb(s, "NASA Space Apps Challenge 2026 — Yaoundé, Cameroon",
        Inches(0.6), Inches(0.9), Inches(12), Inches(0.45),
        size=16, color=ORANGE)
    hline(s, Inches(1.45))

    members = [
        ("KAM FOTSO Gislain",        "Team Lead / Project Coordinator"),
        ("Souleymanou Daouda",        "GIS & Cartographic Validation"),
        ("JATSA GUÉDIA Amaël",        "Agronomic Methodology"),
        ("KWENYUI NDEIH JOSEPH",      "Agricultural Research & Data Support"),
        ("Djouda Douanla Anaël",      "Communication & Presentation"),
        ("NDINGA PRINCE RAOUL",       "Technical Lead & Software Engineer"),
    ]

    cols = [(Inches(0.5), Inches(4.0)), (Inches(6.8), Inches(4.0))]
    for i, (name, role) in enumerate(members):
        col_x, col_w = cols[i % 2]
        row = i // 2
        y = Inches(1.65) + row * Inches(1.7)
        rect(s, col_x, y, col_w, Inches(1.5),
             RGBColor(0x0D, 0x0D, 0x1E), RGBColor(0x27, 0xAE, 0x60))
        txb(s, name, col_x + Inches(0.15), y + Inches(0.12),
            col_w - Inches(0.3), Inches(0.55),
            size=15, bold=True, color=WHITE)
        txb(s, role, col_x + Inches(0.15), y + Inches(0.65),
            col_w - Inches(0.3), Inches(0.6),
            size=13, color=ORANGE)

    rect(s, 0, H - Inches(0.08), W, Inches(0.08), GREEN)


# ── SLIDE 3 — THE PROBLEM ────────────────────────────────────────────────────
def slide3(p):
    s = blank(p)
    bg(s, DARK)
    rect(s, 0, 0, W, Inches(0.08), RED)

    txb(s, "The Problem", Inches(0.6), Inches(0.2), Inches(12), Inches(0.7),
        size=36, bold=True, color=RED)
    txb(s, "Agricultural challenges in Northern Cameroon",
        Inches(0.6), Inches(0.9), Inches(12), Inches(0.45),
        size=16, color=WHITE)
    hline(s, Inches(1.45), RED)

    problems = [
        ("🌧️", "Rainfall Variability",
         "Unimodal rainy season (May–Oct) with high inter-annual variability.\n"
         "False starts — early rains followed by dry spells — cause crop failure\n"
         "when farmers sow too early."),
        ("🌡️", "Heat Stress",
         "Maximum temperatures regularly exceed 35°C during the growing season,\n"
         "reducing maize pollen viability at a critical growth stage."),
        ("🌱", "Soil Information Gaps",
         "Smallholders lack access to soil data. ISRIC SoilGrids v2.0 provides\n"
         "modelled estimates but returned null values for this region —\n"
         "a documented gap in global soil models."),
        ("📅", "Sowing Decision Uncertainty",
         "Without reliable climate intelligence, farmers cannot distinguish\n"
         "a true rainy-season onset from a false start. Crop rotation planning\n"
         "requires multi-year climate context that is rarely accessible locally."),
    ]

    for i, (icon, title, body) in enumerate(problems):
        col = i % 2
        row = i // 2
        x = Inches(0.5) + col * Inches(6.4)
        y = Inches(1.65) + row * Inches(2.5)
        rect(s, x, y, Inches(6.1), Inches(2.3),
             RGBColor(0x1E, 0x1E, 0x3A), RGBColor(0xE7, 0x4C, 0x3C))
        txb(s, f"{icon}  {title}", x + Inches(0.15), y + Inches(0.1),
            Inches(5.8), Inches(0.5), size=15, bold=True, color=RED)
        txb(s, body, x + Inches(0.15), y + Inches(0.6),
            Inches(5.8), Inches(1.5), size=12, color=WHITE)

    rect(s, 0, H - Inches(0.08), W, Inches(0.08), RED)


# ── SLIDE 4 — OUR SOLUTION ───────────────────────────────────────────────────
def slide4(p):
    s = blank(p)
    bg(s, DARK)
    rect(s, 0, 0, W, Inches(0.08), GREEN)

    txb(s, "Our Solution — MaïsMap", Inches(0.6), Inches(0.2),
        Inches(12), Inches(0.7), size=36, bold=True, color=GREEN)
    txb(s, "Two analytical engines. One decision-support platform.",
        Inches(0.6), Inches(0.9), Inches(12), Inches(0.45),
        size=16, color=WHITE)
    hline(s, Inches(1.45))

    # Engine A
    rect(s, Inches(0.5), Inches(1.6), Inches(5.9), Inches(5.5),
         RGBColor(0x0D, 0x1A, 0x0D), RGBColor(0x27, 0xAE, 0x60))
    txb(s, "Engine A — Climate Intelligence",
        Inches(0.65), Inches(1.7), Inches(5.6), Inches(0.5),
        size=15, bold=True, color=GREEN)
    features_a = [
        "Rainy-season onset (Sivakumar 1988 / AGRHYMET)",
        "False-start detection",
        "Dry-spell analysis (max consecutive dry days)",
        "Heat-stress days (Tmax > 35°C, CIMMYT threshold)",
        "Composite risk score: LOW / MEDIUM / HIGH",
        "Sowing advice in plain French",
        "Interactive Folium map — 60 grid cells",
        "5 historical trend charts (2020–2023)",
        "Scenario sensitivity simulator",
    ]
    for j, feat in enumerate(features_a):
        txb(s, f"✓  {feat}", Inches(0.65),
            Inches(2.25) + j * Inches(0.47),
            Inches(5.6), Inches(0.45), size=11, color=WHITE)

    # Engine B
    rect(s, Inches(6.9), Inches(1.6), Inches(5.9), Inches(5.5),
         RGBColor(0x0D, 0x0D, 0x1E), RGBColor(0xF3, 0x9C, 0x12))
    txb(s, "Engine B — Crop Rotation Lab",
        Inches(7.05), Inches(1.7), Inches(5.6), Inches(0.5),
        size=15, bold=True, color=ORANGE)
    features_b = [
        "3 rotation strategies compared",
        "  A: Maize monoculture (baseline)",
        "  B: Maize–Cowpea rotation",
        "  C: Diversified cereal–legume",
        "6 farmer priority dimensions",
        "Interactive priority sliders",
        "Climate-fit scoring per strategy",
        "Crop calendar reference table",
        "Transparent assumptions & data gaps",
    ]
    for j, feat in enumerate(features_b):
        txb(s, f"✓  {feat}", Inches(7.05),
            Inches(2.25) + j * Inches(0.47),
            Inches(5.6), Inches(0.45), size=11, color=WHITE)

    rect(s, 0, H - Inches(0.08), W, Inches(0.08), GREEN)


# ── SLIDE 5 — DATA & TECHNOLOGY ──────────────────────────────────────────────
def slide5(p):
    s = blank(p)
    bg(s, DARK)
    rect(s, 0, 0, W, Inches(0.08), BLUE)

    txb(s, "Data & Technology", Inches(0.6), Inches(0.2),
        Inches(12), Inches(0.7), size=36, bold=True, color=BLUE)
    txb(s, "Real NASA data + ISRIC soil estimates + open-source stack",
        Inches(0.6), Inches(0.9), Inches(12), Inches(0.45),
        size=16, color=WHITE)
    hline(s, Inches(1.45), BLUE)

    # Data sources
    rect(s, Inches(0.5), Inches(1.6), Inches(5.9), Inches(3.5),
         RGBColor(0x0A, 0x0A, 0x20), RGBColor(0x21, 0x8C, 0xBE))
    txb(s, "Data Sources", Inches(0.65), Inches(1.7),
        Inches(5.6), Inches(0.45), size=15, bold=True, color=BLUE)
    data_rows = [
        ("NASA POWER v9",      "PRECTOTCORR, T2M_MAX, T2M_MIN",  "0.5°", "2020–2023", "Primary"),
        ("NASA GIBS",          "MODIS True Color",                "Var.", "Daily",     "Overlay"),
        ("ISRIC SoilGrids v2", "pH, SOC, clay (null — documented)","250m","2023",     "Attempted"),
    ]
    hdrs = ["Source", "Variables", "Res.", "Period", "Role"]
    col_xs = [Inches(0.65), Inches(2.3), Inches(3.6), Inches(4.3), Inches(5.1)]
    col_ws = [Inches(1.6), Inches(1.25), Inches(0.65), Inches(0.75), Inches(1.2)]
    for ci, hdr in enumerate(hdrs):
        txb(s, hdr, col_xs[ci], Inches(2.2), col_ws[ci], Inches(0.35),
            size=10, bold=True, color=BLUE)
    for ri, row in enumerate(data_rows):
        y = Inches(2.6) + ri * Inches(0.45)
        for ci, val in enumerate(row):
            txb(s, val, col_xs[ci], y, col_ws[ci], Inches(0.42),
                size=9, color=WHITE)

    # Tech stack
    rect(s, Inches(6.9), Inches(1.6), Inches(5.9), Inches(3.5),
         RGBColor(0x0A, 0x0A, 0x20), RGBColor(0x21, 0x8C, 0xBE))
    txb(s, "Technology Stack", Inches(7.05), Inches(1.7),
        Inches(5.6), Inches(0.45), size=15, bold=True, color=BLUE)
    tech = [
        ("Python 3.13",    "Data processing, analysis pipeline"),
        ("Streamlit",      "Interactive web application"),
        ("Folium",         "Geographic map visualization"),
        ("GeoJSON",        "Spatial data exchange format"),
        ("QGIS",           "Cartographic validation"),
        ("Plotly",         "Historical trend charts"),
        ("pytest",         "46 automated tests"),
    ]
    for j, (name, desc) in enumerate(tech):
        y = Inches(2.2) + j * Inches(0.42)
        txb(s, name, Inches(7.05), y, Inches(1.6), Inches(0.4),
            size=11, bold=True, color=ORANGE)
        txb(s, desc, Inches(8.75), y, Inches(3.9), Inches(0.4),
            size=11, color=WHITE)

    # Data flow diagram
    rect(s, Inches(0.5), Inches(5.3), Inches(12.33), Inches(1.8),
         RGBColor(0x0A, 0x14, 0x0A), RGBColor(0x27, 0xAE, 0x60))
    txb(s, "Data Flow", Inches(0.65), Inches(5.38),
        Inches(3), Inches(0.4), size=12, bold=True, color=GREEN)
    flow = [
        "NASA POWER API", "→", "Python Pipeline", "→",
        "GeoJSON (60 cells)", "→", "Streamlit + Folium", "→", "Agricultural Decision Support"
    ]
    flow_colors = [BLUE, WHITE, ORANGE, WHITE, GREEN, WHITE, ORANGE, WHITE, GREEN]
    flow_xs = [0.65, 2.55, 2.75, 4.55, 4.75, 6.85, 7.05, 9.15, 9.35]
    for fi, (txt, col) in enumerate(zip(flow, flow_colors)):
        txb(s, txt, Inches(flow_xs[fi]), Inches(5.85),
            Inches(1.85), Inches(0.5), size=11, bold=(txt != "→"), color=col)

    rect(s, 0, H - Inches(0.08), W, Inches(0.08), BLUE)


# ── SLIDE 6 — IMPACT & VISION ────────────────────────────────────────────────
def slide6(p):
    s = blank(p)
    bg(s, DARK)
    rect(s, 0, 0, W, Inches(0.08), ORANGE)

    txb(s, "Impact & Vision", Inches(0.6), Inches(0.2),
        Inches(12), Inches(0.7), size=36, bold=True, color=ORANGE)
    txb(s, "Accessible climate intelligence for smallholder farmers",
        Inches(0.6), Inches(0.9), Inches(12), Inches(0.45),
        size=16, color=WHITE)
    hline(s, Inches(1.45), ORANGE)

    impacts = [
        ("🗺️", "Accessible Intelligence",
         "Farmers and extension agents can explore 4 years of real NASA climate\n"
         "data for 60 grid cells across Northern Cameroon — no GIS expertise needed."),
        ("🌾", "Better Sowing Decisions",
         "False-start detection and risk scoring help identify years and zones\n"
         "where early sowing carries high risk of crop failure."),
        ("🔄", "Crop Rotation Awareness",
         "The Crop Rotation Lab compares three evidence-based strategies,\n"
         "helping farmers understand trade-offs between maize monoculture\n"
         "and diversified systems."),
        ("🌍", "Climate Adaptation",
         "Historical trend analysis reveals patterns in onset dates, dry spells\n"
         "and heat stress — building climate literacy at the community level."),
        ("🔬", "Future Development",
         "Seasonal forecasts · Higher-resolution data · Validated soil properties\n"
         "· Variety-specific guidance · Mobile-first interface · Local language support"),
        ("⚠️", "Honest Limitations",
         "This is a prototype. Risk weights are provisional. SoilGrids returned\n"
         "null values for this region. Recommendations require local confirmation."),
    ]

    for i, (icon, title, body) in enumerate(impacts):
        col = i % 2
        row = i // 2
        x = Inches(0.5) + col * Inches(6.4)
        y = Inches(1.65) + row * Inches(1.85)
        fill = RGBColor(0x1A, 0x0D, 0x00) if i < 4 else RGBColor(0x1A, 0x1A, 0x1A)
        border = ORANGE if i < 4 else RGBColor(0x88, 0x88, 0x88)
        rect(s, x, y, Inches(6.1), Inches(1.7), fill, border)
        txb(s, f"{icon}  {title}", x + Inches(0.15), y + Inches(0.1),
            Inches(5.8), Inches(0.45), size=14, bold=True,
            color=ORANGE if i < 4 else RGBColor(0xAA, 0xAA, 0xAA))
        txb(s, body, x + Inches(0.15), y + Inches(0.55),
            Inches(5.8), Inches(1.05), size=11, color=WHITE)

    rect(s, 0, H - Inches(0.08), W, Inches(0.08), ORANGE)


# ── SLIDE 7 — LIVE PRODUCT & CLOSING ─────────────────────────────────────────
def slide7(p):
    s = blank(p)
    bg(s, DARK)
    rect(s, 0, 0, W, Inches(0.08), GREEN)

    txb(s, "Live Product", Inches(0.6), Inches(0.2),
        Inches(12), Inches(0.7), size=36, bold=True, color=GREEN)
    txb(s, "Working application — real NASA POWER data — 46 automated tests passing",
        Inches(0.6), Inches(0.9), Inches(12), Inches(0.45),
        size=15, color=WHITE)
    hline(s, Inches(1.45))

    # Feature summary boxes
    features = [
        ("Map", "Interactive Folium map\n60 color-coded cells\nClick popups with all indicators"),
        ("Climate", "5 historical charts\nOnset · False starts\nDry spells · Heat days"),
        ("Rotation", "3 strategies compared\nPriority sliders\nClimate-fit scoring"),
        ("Scenario", "Sensitivity simulator\nRain ±30% · Temp ±4°C\nRisk redistribution map"),
        ("Data", "CSV export\nGeoJSON validation\nReal vs demo labels"),
        ("Tests", "46/46 passing\nOnset · Risk · Grid\nLoader · Validator"),
    ]
    for i, (title, body) in enumerate(features):
        col = i % 3
        row = i // 3
        x = Inches(0.5) + col * Inches(4.25)
        y = Inches(1.65) + row * Inches(2.0)
        rect(s, x, y, Inches(4.0), Inches(1.8),
             RGBColor(0x0D, 0x1A, 0x0D), RGBColor(0x27, 0xAE, 0x60))
        txb(s, title, x + Inches(0.15), y + Inches(0.1),
            Inches(3.7), Inches(0.45), size=14, bold=True, color=GREEN)
        txb(s, body, x + Inches(0.15), y + Inches(0.55),
            Inches(3.7), Inches(1.1), size=11, color=WHITE)

    # Closing bar
    rect(s, Inches(0.5), Inches(5.85), Inches(12.33), Inches(1.3),
         RGBColor(0x0A, 0x1A, 0x0A), RGBColor(0x27, 0xAE, 0x60))
    txb(s, "github.com/princeraoulenix/MaisMap",
        Inches(0.65), Inches(5.95), Inches(8), Inches(0.45),
        size=14, bold=True, color=GREEN)
    txb(s, "Team GeoWorks  |  NASA Space Apps Challenge 2026  |  Yaoundé, Cameroon",
        Inches(0.65), Inches(6.45), Inches(12), Inches(0.45),
        size=12, color=WHITE)

    rect(s, 0, H - Inches(0.08), W, Inches(0.08), GREEN)


def main():
    p = prs()
    slide1(p)
    slide2(p)
    slide3(p)
    slide4(p)
    slide5(p)
    slide6(p)
    slide7(p)
    assert len(p.slides) == 7, f"Expected 7 slides, got {len(p.slides)}"
    p.save(OUT)
    print(f"Saved {len(p.slides)}-slide presentation: {OUT}")


if __name__ == "__main__":
    main()
