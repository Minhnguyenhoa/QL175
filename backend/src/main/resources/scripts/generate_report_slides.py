"""
generate_report_slides.py — Báo cáo tiến độ dạng SLIDE 16:9 (PDF), bám mẫu PowerPoint.
Tái dùng lớp dữ liệu report_data.py. Render bằng reportlab canvas (toạ độ tuyệt đối).
  python generate_report_slides.py --out out.pdf --date 12/06/2026 --project H05YTS
"""
import sys, argparse, os
sys.stdout.reconfigure(encoding='utf-8')

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from report_data import *   # dữ liệu + REPORT_DATE, PROJ_CODE, PROJ_NAME, ...

# Out path (report_data dùng parse_known_args nên --out không xung đột)
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument('--out', default=r'D:/QT_175/database/bao_cao_slide.pdf')
_oa, _ = _ap.parse_known_args()
OUT_PATH = _oa.out

# ── FONT ────────────────────────────────────────────────────────────────────────
FONT_DIRS = [r'C:\Windows\Fonts', r'C:\Users\Mr.Cua\AppData\Local\Microsoft\Windows\Fonts',
             '/usr/share/fonts/truetype/dejavu', '/usr/share/fonts']
def find_font(*names):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p): return p
    return None
R = 'AReg'; B = 'ABold'
_r = find_font('arial.ttf', 'Arial.ttf', 'DejaVuSans.ttf')
_b = find_font('arialbd.ttf', 'Arial Bold.ttf', 'DejaVuSans-Bold.ttf')
if _r: pdfmetrics.registerFont(TTFont(R, _r))
else:  R = 'Helvetica'
if _b: pdfmetrics.registerFont(TTFont(B, _b))
else:  B = 'Helvetica-Bold'

# ── PALETTE ─────────────────────────────────────────────────────────────────────
NAVY   = HexColor('#16357d')
NAVY2  = HexColor('#1e3a8a')
BLUE   = HexColor('#1668dc')
LBLUE  = HexColor('#e8f0fe')
ICEBLUE= HexColor('#cfe0fb')
GREEN  = HexColor('#2e9e3f')
LGREEN = HexColor('#eaf7ec')
TEAL   = HexColor('#0f9b8e')
LTEAL  = HexColor('#e6f6f4')
ORANGE = HexColor('#fa541c')
LORANGE= HexColor('#fff1ea')
RED    = HexColor('#cf1322')
DG     = HexColor('#1f2937')   # dark text
GREY   = HexColor('#6b7280')
LGREY  = HexColor('#9aa3af')
BG     = HexColor('#eef2f7')
CARD   = colors.white
LINE   = HexColor('#e3e8ef')
THBG   = HexColor('#16357d')
ROW_A  = colors.white
ROW_B  = HexColor('#f5f8fc')

PROD_COLOR = {'HIS':'#1668dc','LIS':'#0f9b8e','EMR':'#6d28d9',
              'KSK':'#d97706','KSK-CBCS':'#d97706','QLTTDL':'#2e9e3f','THDB':'#cf1322'}
def pcol(code): return HexColor(PROD_COLOR.get(code, '#1668dc'))

PAGE_W, PAGE_H = 960.0, 540.0
c = canvas.Canvas(OUT_PATH, pagesize=(PAGE_W, PAGE_H))

# ── COORD HELPERS (top-origin) ──────────────────────────────────────────────────
def yb(ty): return PAGE_H - ty
def rrect(x, ty, w, h, fill=None, stroke=None, r=8, sw=0.8, dash=None):
    if fill is not None: c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(sw)
        if dash: c.setDash(dash)
    c.roundRect(x, yb(ty+h), w, h, r, stroke=1 if stroke is not None else 0,
                fill=1 if fill is not None else 0)
    if dash: c.setDash()
def rect(x, ty, w, h, fill=None, stroke=None, sw=0.8):
    if fill is not None: c.setFillColor(fill)
    if stroke is not None: c.setStrokeColor(stroke); c.setLineWidth(sw)
    c.rect(x, yb(ty+h), w, h, stroke=1 if stroke is not None else 0,
           fill=1 if fill is not None else 0)
def circle(cx, ty, rad, fill=None, stroke=None, sw=1):
    if fill is not None: c.setFillColor(fill)
    if stroke is not None: c.setStrokeColor(stroke); c.setLineWidth(sw)
    c.circle(cx, yb(ty), rad, stroke=1 if stroke is not None else 0,
             fill=1 if fill is not None else 0)
def txt(x, ty, s, f=R, sz=10, col=DG, a='l'):
    c.setFont(f, sz); c.setFillColor(col)
    s = str(s)
    if a == 'l':  c.drawString(x, yb(ty), s)
    elif a == 'c':c.drawCentredString(x, yb(ty), s)
    else:         c.drawRightString(x, yb(ty), s)
def tw(s, f, sz): return pdfmetrics.stringWidth(str(s), f, sz)

def bar(x, ty, w, h, frac, color, bgc=HexColor('#e5e9f0'), r=None):
    r = h/2 if r is None else r
    frac = max(0.0, min(1.0, frac))
    rrect(x, ty, w, h, fill=bgc, r=r)
    if frac > 0:
        fw = max(h, w*frac)
        rrect(x, ty, fw, h, fill=color, r=r)
def sbar(x, ty, w, h, segs, bgc=HexColor('#e5e9f0'), r=None):
    """segs = [(frac,color),...] proportions of w"""
    r = h/2 if r is None else r
    rrect(x, ty, w, h, fill=bgc, r=r)
    cx = x
    for frac, col in segs:
        sw_ = w*max(0.0, min(1.0, frac))
        if sw_ <= 0: continue
        rrect(cx, ty, sw_, h, fill=col, r=min(r, sw_/2))
        cx += sw_

def ic(name, cx, ty, s, col=colors.white):
    """Vẽ icon vector trắng (tránh glyph unicode font không có). ty = tâm theo top-origin."""
    Y = yb(ty)
    c.saveState(); c.setStrokeColor(col); c.setFillColor(col)
    c.setLineWidth(max(1.1, s*0.18)); c.setLineCap(1); c.setLineJoin(1)
    if name == 'check':
        c.line(cx-0.42*s, Y-0.02*s, cx-0.08*s, Y-0.34*s)
        c.line(cx-0.08*s, Y-0.34*s, cx+0.46*s, Y+0.36*s)
    elif name == 'flag':
        c.line(cx-0.32*s, Y-0.46*s, cx-0.32*s, Y+0.5*s)
        p = c.beginPath(); p.moveTo(cx-0.32*s, Y+0.48*s); p.lineTo(cx+0.46*s, Y+0.2*s)
        p.lineTo(cx-0.32*s, Y-0.04*s); p.close(); c.drawPath(p, fill=1, stroke=0)
    elif name == 'grid':
        q = 0.36*s
        for ox in (-q-0.04*s, 0.04*s):
            for oy in (-q-0.04*s, 0.04*s):
                c.rect(cx+ox, Y+oy, q, q, fill=1, stroke=0)
    elif name == 'warn':
        p = c.beginPath(); p.moveTo(cx, Y+0.5*s); p.lineTo(cx+0.5*s, Y-0.42*s)
        p.lineTo(cx-0.5*s, Y-0.42*s); p.close(); c.drawPath(p, fill=1, stroke=0)
    elif name == 'sq':
        c.rect(cx-0.38*s, Y-0.38*s, 0.76*s, 0.76*s, fill=1, stroke=0)
    elif name == 'dot':
        c.circle(cx, Y, 0.36*s, fill=1, stroke=0)
    elif name == 'people':
        c.circle(cx, Y+0.22*s, 0.24*s, fill=1, stroke=0)
        p = c.beginPath(); p.moveTo(cx-0.42*s, Y-0.46*s)
        p.curveTo(cx-0.42*s, Y+0.05*s, cx+0.42*s, Y+0.05*s, cx+0.42*s, Y-0.46*s)
        p.close(); c.drawPath(p, fill=1, stroke=0)
    elif name == 'bars':
        for i, hh in enumerate([0.45, 0.72, 1.0]):
            c.rect(cx-0.46*s+i*0.34*s, Y-0.45*s, 0.24*s, 0.9*s*hh, fill=1, stroke=0)
    elif name == 'money':
        c.setFont(B, s*1.1); c.drawCentredString(cx, Y-0.36*s, '$')
    elif name == 'arrow':
        c.line(cx-0.45*s, Y, cx+0.4*s, Y)
        p = c.beginPath(); p.moveTo(cx+0.5*s, Y); p.lineTo(cx+0.1*s, Y+0.28*s)
        p.lineTo(cx+0.1*s, Y-0.28*s); p.close(); c.drawPath(p, fill=1, stroke=0)
    elif name == 'info':
        c.setFont(B, s*1.25); c.drawCentredString(cx, Y-0.42*s, 'i')
    c.restoreState()

# ── platypus table drawn at absolute pos ────────────────────────────────────────
def PS(f=R, sz=8, col=DG, a=TA_LEFT, lead=None):
    return ParagraphStyle('p', fontName=f, fontSize=sz, textColor=col,
                          alignment=a, leading=lead or sz*1.2)
def P(s, f=R, sz=8, col=DG, a=TA_LEFT, lead=None):
    return Paragraph(str(s), PS(f, sz, col, a, lead))
def draw_table(data, col_w, x, ty, style, row_h=None):
    t = Table(data, colWidths=col_w, rowHeights=row_h, style=style)
    w, h = t.wrapOn(c, sum(col_w), PAGE_H)
    t.drawOn(c, x, yb(ty) - h)
    return h

# ── COMMON CHROME ───────────────────────────────────────────────────────────────
def page_bg():
    rect(0, 0, PAGE_W, PAGE_H, fill=BG)
def logo(x, ty):
    rrect(x, ty-15, 26, 26, fill=colors.white, r=6)
    c.setFillColor(NAVY); c.setFont(B, 17); c.drawCentredString(x+13, yb(ty+4.5), '+')
def header(title, scope=True):
    """Navy top bar with logo + title + date box."""
    rect(0, 0, PAGE_W, 64, fill=NAVY)
    rect(0, 64, PAGE_W, 4, fill=BLUE)
    logo(26, 32)
    txt(64, 38, title, B, 17, colors.white, 'l')
    # date box
    bx, bw = 770, 168
    rrect(bx, 14, bw, 38, fill=NAVY2, stroke=HexColor('#3b5bb5'), r=6, sw=0.8)
    txt(bx+16, 28 if scope else 33, f'Ngày báo cáo: {REPORT_DATE}', R, 8.5, colors.white)
    if scope:
        txt(bx+16, 42, f'Phạm vi: {PROJ_CODE}', R, 8.5, ICEBLUE)
def panel_header(x, ty, w, s, color=NAVY, icon='grid'):
    rrect(x, ty, w, 26, fill=color, r=6)
    circle(x+18, ty+13, 8.5, fill=colors.white)
    ic(icon, x+18, ty+13, 9, color)
    txt(x+36, ty+17, s, B, 11, colors.white, 'l')

def kpi_card(x, ty, w, h, label, value, vcol, icon_col, sub='', icon='sq'):
    rrect(x, ty, w, h, fill=CARD, stroke=LINE, r=10, sw=0.8)
    circle(x+26, ty+h/2, 15, fill=icon_col)
    ic(icon, x+26, ty+h/2, 13, colors.white)
    txt(x+50, ty+h/2-6, label, B, 10, DG, 'l')
    txt(x+50, ty+h/2+13, value, B, 19, vcol, 'l')
    if sub:
        txt(x+50, ty+h/2+27, sub, R, 8, GREY, 'l')

# ════════════════════════════════════════════════════════════════════════════════
# DERIVED METRICS
# ════════════════════════════════════════════════════════════════════════════════
def phase_get(name):
    for r in phase_stats:
        if (r.get('phase') or '') == name: return r
    return {}
_g1 = phase_get('Giai đoạn 1'); _g2 = phase_get('Giai đoạn 2')
GD1_TOT = iv(_g1.get('total')); GD2_TOT = iv(_g2.get('total'))

# forecast per phase
phase_fc = {}
for r in phase_stats:
    ph = r.get('phase')
    if not ph: continue
    rows = Q(f"""SELECT current_phase,(actual_end_date IS NOT NULL) is_done,COUNT(*) cnt
        FROM milestones WHERE phase=%s{MS_AND}
        GROUP BY current_phase,(actual_end_date IS NOT NULL)""", (ph,))
    phase_fc[ph] = calc_forecast(rows)

TOTAL_MM = round(sum(fv(r['mm']) for r in alloc_prod), 2)
GTEL_MM  = round(sum(v.get('GTEL ICT', {}).get('mm', 0) for v in alloc_pivot.values()), 2)
OS_MM    = round(TOTAL_MM - GTEL_MM, 2)

# Gom nhóm nhân sự: theo vai trò nếu có dữ liệu, ngược lại theo đơn vị (company)
HAS_ROLE = any((e.get('role') or '').strip() for e in emp_list)
GKEY   = 'role' if HAS_ROLE else 'company'
GLABEL = 'VAI TRÒ' if HAS_ROLE else 'ĐƠN VỊ'
group_mm = {}
for e in emp_list:
    k = (e.get(GKEY) or '—')
    group_mm.setdefault(k, {'hc': 0, 'mm': 0.0})
    group_mm[k]['hc'] += 1
    group_mm[k]['mm'] += fv(e['mm'])

def comp_forecast(r):
    rows = [
        {'current_phase':'Coding','is_done':1,'cnt':iv(r['coding_done'])},
        {'current_phase':'Coding','is_done':0,'cnt':iv(r['coding_prog'])},
        {'current_phase':'Kiểm thử nội bộ','is_done':1,'cnt':iv(r['ktnb_done'])},
        {'current_phase':'Kiểm thử nội bộ','is_done':0,'cnt':iv(r['ktnb_prog'])},
        {'current_phase':'Pilot','is_done':1,'cnt':iv(r['pilot_done'])},
        {'current_phase':'Pilot','is_done':0,'cnt':iv(r['pilot_prog'])},
    ]
    tot = iv(r['total']); used = sum(x['cnt'] for x in rows)
    rows.append({'current_phase':None,'is_done':0,'cnt':max(0, tot-used)})
    return calc_forecast(rows)[0]

def color_pct(p): return GREEN if p>=70 else ORANGE if p>=30 else RED

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# ════════════════════════════════════════════════════════════════════════════════
def deco_dots(x, ty, rows, cols, gap=7, rad=1.6, col=ICEBLUE):
    c.setFillColor(col)
    for i in range(rows):
        for j in range(cols):
            c.circle(x+j*gap, yb(ty+i*gap), rad, stroke=0, fill=1)

def illustration(cx, cy):
    # concentric arcs
    for rad, col in [(150, HexColor('#dbe7fb')), (110, HexColor('#c7d8f7')), (72, HexColor('#1668dc'))]:
        c.setFillColor(col)
        c.setStrokeColor(col)
        c.wedge(cx-rad, yb(cy+rad), cx+rad, yb(cy-rad), 20, 110, stroke=0, fill=1)
    # dashboard card
    rrect(cx-120, cy-50, 200, 120, fill=colors.white, stroke=LINE, r=10)
    rect(cx-120, cy-50, 200, 22, fill=HexColor('#16357d'))
    c.setFillColor(HexColor('#16357d'))
    # donut
    c.setFillColor(TEAL); c.circle(cx-78, yb(cy+18), 20, stroke=0, fill=1)
    c.setFillColor(colors.white); c.circle(cx-78, yb(cy+18), 9, stroke=0, fill=1)
    # bars
    for i, hh in enumerate([14, 24, 34, 20]):
        c.setFillColor(BLUE if i % 2 else TEAL)
        c.rect(cx-30+i*16, yb(cy+38), 10, hh, stroke=0, fill=1)
    # plus marks
    for px, py, s in [(cx+120, cy-70, 12), (cx+150, cy+30, 9), (cx-150, cy+80, 9)]:
        c.setStrokeColor(BLUE); c.setLineWidth(s/4.5)
        c.line(px-s/2, yb(py), px+s/2, yb(py)); c.line(px, yb(py-s/2), px, yb(py+s/2))

def slide_cover():
    page_bg()
    rect(0, 0, PAGE_W, 64, fill=NAVY); rect(0, 64, PAGE_W, 4, fill=BLUE)
    logo(26, 32); txt(64, 38, PROJ_CODE, B, 18, colors.white)
    rrect(770, 14, 168, 38, fill=NAVY2, stroke=HexColor('#3b5bb5'), r=6)
    txt(786, 38, f'Ngày báo cáo: {REPORT_DATE}', R, 8.5, colors.white)
    illustration(720, 300)
    txt(60, 215, PROJ_CODE, B, 30, NAVY2)
    txt(60, 258, 'BÁO CÁO TIẾN ĐỘ DỰ ÁN', B, 30, NAVY2)
    rect(60, 300, 70, 4, fill=BLUE)
    txt(60, 340, 'Báo cáo tổng hợp tiến độ, nguồn lực và khối lượng công việc', R, 11, GREY)
    pills = [('check', 'TỔNG QUAN', 'Tiến độ tổng thể dự án và các giai đoạn', BLUE),
             ('people', 'NGUỒN LỰC', 'Nhân sự, vai trò và phân bổ nguồn lực', BLUE),
             ('bars', 'KHỐI LƯỢNG', 'Khối lượng công việc và tỷ lệ hoàn thành', TEAL)]
    px = 60
    for icon, t1, t2, col in pills:
        circle(px+15, 405, 15, fill=col); ic(icon, px+15, 405, 14, colors.white)
        txt(px+38, 400, t1, B, 10, NAVY2)
        txt(px+38, 414, t2[:48], R, 7.5, GREY)
        px += 250
    rrect(60, 445, 360, 34, fill=colors.white, stroke=LINE, r=8)
    circle(82, 462, 11, fill=NAVY2); txt(82, 466, '+', B, 11, colors.white, 'c')
    txt(102, 466, (PROJ_NAME[:46] if PROJ_CODE != 'ALL' else 'Hệ thống Công nghệ thông tin Y tế'),
        B, 10.5, NAVY2)
    deco_dots(30, 470, 5, 6)
    c.showPage()

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — TOC
# ════════════════════════════════════════════════════════════════════════════════
def slide_toc():
    page_bg(); header(f'{PROJ_CODE} – TỔNG THỂ TIẾN ĐỘ DỰ ÁN')
    txt(60, 130, 'NỘI DUNG BÁO CÁO', B, 26, NAVY2)
    txt(60, 158, 'Tổng quan toàn diện về tiến độ và nguồn lực dự án', R, 12, GREY)
    rect(60, 172, 70, 3, fill=BLUE)
    items = [('01', '1. Tổng thể tiến độ dự án',
              'Tổng quan tiến độ dự án, nguồn lực và khối lượng công việc toàn dự án.', BLUE),
             ('02', '2. Tiến độ dự án Giai đoạn 1',
              'Tổng quan cơ cấu khối lượng và hiệu quả thực hiện Giai đoạn 1.', TEAL),
             ('03', '3. Nhân sự dự án',
              'Tổng quan headcount, cơ cấu nhân sự theo dự án và nguồn lực.', ORANGE)]
    ty = 205
    for num, t1, t2, col in items:
        rrect(90, ty, 560, 78, fill=colors.white, stroke=LINE, r=10)
        rrect(90, ty, 82, 78, fill=col, r=10)
        rect(160, ty, 12, 78, fill=col)
        txt(131, ty+48, num, B, 28, colors.white, 'c')
        circle(205, ty+39, 18, fill=LBLUE)
        ic(['check','flag','people'][min(int(num)-1,2)], 205, ty+39, 15, col)
        txt(240, ty+34, t1, B, 13, col)
        txt(240, ty+56, t2, R, 9.5, GREY)
        circle(632, ty+39, 6, stroke=col, sw=1.5)
        ty += 100
    c.showPage()

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — TỔNG THỂ TIẾN ĐỘ (KPI + 2 tables)
# ════════════════════════════════════════════════════════════════════════════════
def kpi_top(x, ty, w, h, icon_col, icon, label, value, vcol):
    rrect(x, ty, w, h, fill=colors.white, stroke=LINE, r=10)
    circle(x+34, ty+h/2, 20, fill=icon_col)
    ic(icon, x+34, ty+h/2, 17, colors.white)
    txt(x+62, ty+26, label, B, 12, NAVY2)
    txt(x+62, ty+55, value, B, 26, vcol)

def slide_overview1():
    page_bg(); header(f'{PROJ_CODE} – TỔNG THỂ TIẾN ĐỘ DỰ ÁN')
    # KPI row
    cards = [(BLUE, 'check', 'Tổng công việc', TOT, NAVY2),
             (BLUE, 'flag', 'Giai đoạn 1', GD1_TOT, BLUE),
             (TEAL, 'grid', 'Giai đoạn 2', GD2_TOT, TEAL),
             (ORANGE, 'warn', 'Quá hạn', OVERD, ORANGE)]
    x = 24; cw = 222
    for col, icn, lb, vl, vc in cards:
        kpi_top(x, 82, cw, 74, col, icn, lb, vl, vc); x += cw + 8
    # banner
    rrect(150, 172, 660, 30, fill=LORANGE, stroke=HexColor('#ffc7a8'), r=15)
    circle(172, 187, 12, fill=ORANGE); ic('arrow', 172, 187, 11, colors.white)
    txt(192, 191, f'Tổng {TOT} công việc', B, 12, ORANGE)
    txt(330, 191, f'|  Giai đoạn 1: {GD1_TOT}  ·  Giai đoạn 2: {GD2_TOT}  ·  Đã hoàn thành: {DONE}',
        R, 11, DG)
    # Left table
    panel_header(24, 218, 440, '1. TỔNG QUAN THEO GIAI ĐOẠN')
    hdr = [P(h, B, 8, colors.white, TA_CENTER) for h in
           ['Giai đoạn', 'Chưa BĐ', 'Đã HT', 'Đang TH', 'Tổng']]
    rows = [hdr]
    for r in phase_stats:
        t = iv(r['total']); d = iv(r['done']); ip = iv(r['in_prog']); nb = max(0, t-d-ip)
        rows.append([P(r['phase'], R, 8.5), P(nb, R, 8.5, DG, TA_CENTER),
                     P(d, B, 8.5, GREEN, TA_CENTER), P(ip, B, 8.5, ORANGE, TA_CENTER),
                     P(t, B, 8.5, NAVY2, TA_CENTER)])
    nb = max(0, TOT-DONE-INPROG)
    rows.append([P('Tổng cộng', B, 8.5), P(nb, B, 8.5, DG, TA_CENTER),
                 P(DONE, B, 8.5, GREEN, TA_CENTER), P(INPROG, B, 8.5, ORANGE, TA_CENTER),
                 P(TOT, B, 8.5, NAVY2, TA_CENTER)])
    st = TableStyle([('BACKGROUND',(0,0),(-1,0),THBG),
        ('ROWBACKGROUNDS',(0,1),(-1,-2),[ROW_A,ROW_B]),
        ('BACKGROUND',(0,-1),(-1,-1),LGREEN),
        ('GRID',(0,0),(-1,-1),0.4,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)])
    draw_table(rows, [140,75,75,75,75], 24, 250, st)
    # Right table — workload structure (per phase)
    panel_header(490, 218, 446, '2. CƠ CẤU KHỐI LƯỢNG CÔNG VIỆC')
    hdr2 = [P(h, B, 8, colors.white, TA_CENTER) for h in
            ['Giai đoạn', 'Chưa BĐ', 'Đã HT', 'Đang TH', 'Tổng cộng']]
    rows2 = [hdr2]
    for r in phase_stats:
        t = iv(r['total']); d = iv(r['done']); ip = iv(r['in_prog']); nb = max(0, t-d-ip)
        rows2.append([P(r['phase'], R, 8.5), P(nb, R, 8.5, DG, TA_CENTER),
                      P(d, R, 8.5, GREEN, TA_CENTER), P(ip, R, 8.5, ORANGE, TA_CENTER),
                      P(t, B, 8.5, NAVY2, TA_CENTER)])
    rows2.append([P('Tổng cộng', B, 8.5, colors.white), P(nb, B, 8.5, colors.white, TA_CENTER),
                  P(DONE, B, 8.5, colors.white, TA_CENTER), P(INPROG, B, 8.5, colors.white, TA_CENTER),
                  P(TOT, B, 8.5, colors.white, TA_CENTER)])
    st2 = TableStyle([('BACKGROUND',(0,0),(-1,0),THBG),
        ('ROWBACKGROUNDS',(0,1),(-1,-2),[ROW_A,ROW_B]),
        ('BACKGROUND',(0,-1),(-1,-1),NAVY2),
        ('GRID',(0,0),(-1,-1),0.4,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)])
    draw_table(rows2, [120,82,82,82,80], 490, 250, st2)
    c.showPage()

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — DỰ BÁO HOÀN THÀNH
# ════════════════════════════════════════════════════════════════════════════════
def slide_overview2():
    page_bg(); header(f'{PROJ_CODE} – TỔNG THỂ TIẾN ĐỘ DỰ ÁN')
    # top forecast strip
    rrect(24, 82, 912, 78, fill=colors.white, stroke=LINE, r=10)
    circle(70, 121, 24, fill=NAVY2); txt(70, 127, 'Σ', B, 18, colors.white, 'c')
    txt(108, 110, 'Tổng công việc', B, 12, NAVY2)
    txt(108, 138, str(TOT), B, 24, NAVY2); txt(162, 138, 'công việc', R, 9, GREY)
    txt(250, 104, 'Dự báo hoàn thành', B, 12, DG)
    bar(250, 116, 560, 16, FC_PCT_TOTAL/100, ORANGE)
    txt(250, 150, '0%', R, 8, GREY); txt(810, 150, '100%', R, 8, GREY, 'r')
    txt(530, 112, f'{FC_PCT_TOTAL:.2f}%', B, 13, ORANGE, 'c')
    rrect(828, 100, 92, 36, fill=LORANGE, stroke=HexColor('#ffc7a8'), r=6)
    txt(874, 113, 'HIỆN TẠI', B, 8, ORANGE, 'c'); txt(874, 128, f'{FC_PCT_TOTAL:.2f}%', B, 12, ORANGE, 'c')
    # Left panel — forecast by phase
    panel_header(24, 178, 440, '1. DỰ BÁO HOÀN THÀNH THEO GIAI ĐOẠN')
    ty = 214
    pal = [GREEN, ORANGE, BLUE, TEAL]
    for i, r in enumerate(phase_stats):
        ph = r['phase']; fc = phase_fc.get(ph, (0,0,0,[]))[0]; pts = phase_fc.get(ph,(0,0,0,[]))[1]
        col = pal[i % len(pal)]
        rrect(24, ty, 440, 52, fill=colors.white, stroke=LINE, r=8)
        circle(48, ty+26, 12, fill=col); txt(48, ty+30, str(i+1), B, 11, colors.white, 'c')
        txt(70, ty+20, ph, B, 11, DG)
        txt(70, ty+38, f"{iv(r['total'])} việc   ·   {pts:.1f} điểm", R, 8, GREY)
        bar(250, ty+22, 120, 10, fc/100, col)
        txt(450, ty+30, f'{fc:.2f}%', B, 12, col, 'r')
        ty += 60
    rrect(24, ty, 440, 30, fill=LBLUE, r=8)
    txt(40, ty+19, 'Toàn dự án', B, 10, NAVY2)
    txt(300, ty+19, f'{TOT} việc', R, 9, DG, 'r')
    txt(450, ty+19, f'{FC_PCT_TOTAL:.2f}%', B, 11, ORANGE, 'r')
    # Right panel — conversion points
    panel_header(490, 178, 446, '2. CƠ CẤU KHỐI LƯỢNG & ĐIỂM QUY ĐỔI')
    hdr = [P(h, B, 7.5, colors.white, TA_CENTER) for h in
           ['Trạng thái', 'SL', 'Quy đổi', 'Điểm', 'Tỷ trọng']]
    rows = [hdr]
    for it in FC_ITEMS:
        if it['cnt'] == 0: continue
        rows.append([P(it['label'], R, 7.5), P(it['cnt'], R, 7.5, DG, TA_CENTER),
                     P(f"{int(it['rate']*100)}%", B, 7.5, BLUE, TA_CENTER),
                     P(f"{it['pts']:.2f}", B, 7.5, GREEN, TA_CENTER),
                     P(f"{it['w_pct']:.2f}%", R, 7.5, DG, TA_CENTER)])
    rows.append([P('Tổng cộng', B, 7.5), P(TOT, B, 7.5, DG, TA_CENTER), P('', R, 7.5),
                 P(f'{FC_PTS_TOTAL:.2f}', B, 7.5, GREEN, TA_CENTER),
                 P(f'{FC_PCT_TOTAL:.2f}%', B, 7.5, ORANGE, TA_CENTER)])
    st = TableStyle([('BACKGROUND',(0,0),(-1,0),THBG),
        ('ROWBACKGROUNDS',(0,1),(-1,-2),[ROW_A,ROW_B]),('BACKGROUND',(0,-1),(-1,-1),LBLUE),
        ('GRID',(0,0),(-1,-1),0.4,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)])
    draw_table(rows, [196,46,68,68,68], 490, 214, st)
    txt(713, 214+5+len(rows)*22, 'Công thức: Σ(SL × tỷ lệ quy đổi) / Tổng số công việc', R, 7.5, GREY, 'c')
    # Nhận định
    rrect(24, 470, 912, 56, fill=LBLUE, stroke=ICEBLUE, r=8)
    circle(46, 498, 11, fill=BLUE); ic('info', 46, 498, 11, colors.white)
    txt(66, 492, 'Nhận định', B, 12, NAVY2)
    best = max(phase_stats, key=lambda r: phase_fc.get(r['phase'],(0,))[0]) if phase_stats else None
    if best:
        ic('check', 168, 489, 9, GREEN)
        txt(180, 490, f"{best['phase']} đạt {phase_fc[best['phase']][0]:.2f}% dự báo hoàn thành, đóng góp chính vào tiến độ.",
            R, 9.5, DG)
    ic('warn', 168, 509, 9, ORANGE)
    txt(180, 510, f"Còn {NOSTART} công việc ({pct(NOSTART,TOT):.1f}%) chưa bắt đầu — cần phân bổ nguồn lực.",
        R, 9.5, DG)
    c.showPage()

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — GĐ1 theo hệ thống (Coding/KTNB/Staging)
# ════════════════════════════════════════════════════════════════════════════════
def slide_gd1_systems():
    page_bg(); header(f'{PROJ_CODE} – TỔNG THỂ TIẾN ĐỘ GIAI ĐOẠN 1')
    # compute totals
    def cks(r):
        cod = iv(r['coding_prog'])+iv(r['coding_done'])
        ktn = iv(r['ktnb_prog'])+iv(r['ktnb_done'])
        sta = iv(r['pilot_prog'])+iv(r['pilot_done'])
        return cod, ktn, sta
    sys_rows = [r for r in gd1_by_prod_phase if iv(r['total'])>0]
    TC = sum(cks(r)[0] for r in sys_rows); TK = sum(cks(r)[1] for r in sys_rows)
    TS = sum(cks(r)[2] for r in sys_rows); TT = sum(iv(r['total']) for r in sys_rows)
    # top strip
    rrect(24, 82, 912, 58, fill=colors.white, stroke=LINE, r=10)
    circle(60, 111, 20, fill=NAVY2); ic('grid', 60, 111, 16, colors.white)
    txt(92, 104, 'Tổng số', B, 11, DG); txt(92, 128, str(TT), B, 22, NAVY2)
    txt(150, 128, 'tính năng', R, 9, GREY)
    txt(280, 102, 'Cơ cấu Giai đoạn 1 theo trạng thái triển khai (tính năng đã có hoạt động)', B, 10, DG)
    _act = (TC+TK+TS) or 1
    sbar(280, 110, 600, 14, [(TC/_act, BLUE),(TK/_act, ORANGE),(TS/_act, GREEN)])
    # legend dưới thanh
    lx = 280
    for lb, vl, cl in [('Coding', TC, BLUE), ('Kiểm thử nội bộ', TK, ORANGE), ('Staging', TS, GREEN)]:
        ic('sq', lx+4, 135, 6, cl); txt(lx+14, 138, f'{lb}: {vl}', R, 8, DG); lx += tw(f'{lb}: {vl}', R, 8) + 40
    # Single wide table: per system
    panel_header(24, 160, 912, 'SỐ LƯỢNG TÍNH NĂNG GIAI ĐOẠN 1 THEO HỆ THỐNG', NAVY)
    hdr = [P(h, B, 9, colors.white, TA_CENTER) for h in
           ['Hệ thống', 'Coding', 'Kiểm thử nội bộ', 'Staging', 'Đã hoàn thành', 'Tổng cộng']]
    rows = [hdr]
    for r in sys_rows:
        cod, ktn, sta = cks(r)
        rows.append([P(r['code'], B, 9, NAVY2), P(cod, R, 9, DG, TA_CENTER),
                     P(ktn, R, 9, DG, TA_CENTER), P(sta, R, 9, DG, TA_CENTER),
                     P(iv(r['done']), B, 9, GREEN, TA_CENTER), P(iv(r['total']), B, 9, NAVY2, TA_CENTER)])
    rows.append([P('Tổng số', B, 9, colors.white), P(TC, B, 9, colors.white, TA_CENTER),
                 P(TK, B, 9, colors.white, TA_CENTER), P(TS, B, 9, colors.white, TA_CENTER),
                 P(sum(iv(r['done']) for r in sys_rows), B, 9, colors.white, TA_CENTER),
                 P(TT, B, 9, colors.white, TA_CENTER)])
    st = TableStyle([('BACKGROUND',(0,0),(-1,0),THBG),
        ('ROWBACKGROUNDS',(0,1),(-1,-2),[ROW_A,ROW_B]),('BACKGROUND',(0,-1),(-1,-1),GREEN),
        ('GRID',(0,0),(-1,-1),0.4,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10)])
    draw_table(rows, [180,140,160,140,150,142], 24, 192, st)
    # bottom stat row
    base = 430
    stats = [('Tổng tính năng GĐ1', TT, NAVY2), ('Coding', TC, BLUE),
             ('Kiểm thử nội bộ', TK, ORANGE), ('Staging', TS, GREEN)]
    x = 24; w = 222
    for lb, vl, col in stats:
        rrect(x, base, w, 64, fill=colors.white, stroke=LINE, r=10)
        circle(x+28, base+32, 16, fill=col); ic('bars', x+28, base+32, 13, colors.white)
        txt(x+52, base+26, lb, B, 9.5, DG); txt(x+52, base+52, str(vl), B, 20, col)
        x += w + 8
    c.showPage()

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — GĐ1 hiện trạng + tỷ lệ hoàn thành
# ════════════════════════════════════════════════════════════════════════════════
def slide_gd1_status():
    page_bg(); header(f'{PROJ_CODE} – TỔNG THỂ TIẾN ĐỘ GIAI ĐOẠN 1')
    # Left: số lượng hiện trạng
    panel_header(24, 82, 470, 'SỐ LƯỢNG HIỆN TRẠNG GIAI ĐOẠN 1', NAVY)
    hdr = [P(h, B, 8, colors.white, TA_CENTER) for h in
           ['Hệ thống', 'Trạng thái', 'Coding', 'KT nội bộ', 'Staging', 'Tổng']]
    rows = [hdr]
    spans = []
    ri = 1
    for r in gd1_by_prod_phase:
        if iv(r['total']) == 0: continue
        cd_d, cd_p = iv(r['coding_done']), iv(r['coding_prog'])
        kt_d, kt_p = iv(r['ktnb_done']), iv(r['ktnb_prog'])
        st_d, st_p = iv(r['pilot_done']), iv(r['pilot_prog'])
        done_tot = cd_d+kt_d+st_d; prog_tot = cd_p+kt_p+st_p
        rows.append([P(r['code'], B, 8, NAVY2), P('Đã HT', R, 7.5, GREEN, TA_CENTER),
                     P(cd_d, R, 8, DG, TA_CENTER), P(kt_d, R, 8, DG, TA_CENTER),
                     P(st_d, R, 8, DG, TA_CENTER), P(done_tot, B, 8, DG, TA_CENTER)])
        rows.append([P('', R, 8), P('Đang TH', R, 7.5, ORANGE, TA_CENTER),
                     P(cd_p, R, 8, DG, TA_CENTER), P(kt_p, R, 8, DG, TA_CENTER),
                     P(st_p, R, 8, DG, TA_CENTER), P(prog_tot, B, 8, DG, TA_CENTER)])
        spans.append(('SPAN', (0, ri), (0, ri+1)))
        ri += 2
    st = TableStyle([('BACKGROUND',(0,0),(-1,0),THBG),
        ('GRID',(0,0),(-1,-1),0.4,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),3.5),('BOTTOMPADDING',(0,0),(-1,-1),3.5),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)] + spans)
    draw_table(rows, [70,80,75,80,80,55], 24, 114, st)
    # Right: tỷ lệ hoàn thành per system
    panel_header(514, 82, 422, 'TỶ LỆ HOÀN THÀNH THEO HỆ THỐNG', BLUE)
    ty = 120
    for pr in by_prod:
        if iv(pr['total']) == 0: continue
        code = pr['code']; fc = prod_forecast[code][0]
        rrect(514, ty, 422, 40, fill=colors.white, stroke=LINE, r=8)
        circle(536, ty+20, 12, fill=pcol(code)); ic('dot', 536, ty+20, 11, colors.white)
        txt(558, ty+18, code, B, 11, pcol(code))
        bar(558, ty+26, 250, 9, fc/100, pcol(code))
        txt(924, ty+25, f'{fc:.2f}%', B, 12, color_pct(fc), 'r')
        ty += 46
    # H05YTS total
    rrect(514, ty, 422, 36, fill=LBLUE, r=8)
    txt(534, ty+22, f'{PROJ_CODE} (Tổng dự án)', B, 11, NAVY2)
    txt(924, ty+22, f'{FC_PCT_TOTAL:.2f}%', B, 13, ORANGE, 'r')
    # bottom note
    rrect(24, 502, 912, 26, fill=NAVY2, r=6)
    txt(480, 519, 'Tiến độ dự báo = Tổng điểm quy đổi / Tổng số lượng   ·   '
        'Coding 35–50% · Kiểm thử 60–70% · Staging 80–100%', R, 9, colors.white, 'c')
    c.showPage()

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Chi tiết thành phần GĐ1
# ════════════════════════════════════════════════════════════════════════════════
def slide_gd1_components():
    page_bg(); header(f'{PROJ_CODE} – TỔNG THỂ TIẾN ĐỘ GIAI ĐOẠN 1')
    panel_header(24, 82, 912, 'TỶ LỆ HOÀN THÀNH DỰ BÁO THEO THÀNH PHẦN MILESTONE', NAVY)
    comps = [r for r in gd1_comps if iv(r['total'])>0]
    # split into two columns
    half = (len(comps)+1)//2
    cols = [comps[:half], comps[half:]]
    colx = [24, 490]
    for ci, group in enumerate(cols):
        x = colx[ci]
        hdr = [P(h, B, 7.5, colors.white, TA_CENTER) for h in ['#','Hệ thống','Thành phần','Tổng','Dự báo HT']]
        rows = [hdr]
        for i, r in enumerate(group):
            fc = comp_forecast(r)
            idx = ci*half + i + 1
            rows.append([P(idx, R, 7.5, DG, TA_CENTER), P(r['prod_code'], B, 7.5, pcol(r['prod_code']), TA_CENTER),
                         P((r['comp'] or '')[:40], R, 7), P(iv(r['total']), R, 7.5, DG, TA_CENTER),
                         P(f'{fc:.1f}%', B, 7.5, color_pct(fc), TA_CENTER)])
        st = TableStyle([('BACKGROUND',(0,0),(-1,0),THBG),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[ROW_A,ROW_B]),
            ('GRID',(0,0),(-1,-1),0.3,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
            ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)])
        draw_table(rows, [26,52,210,55,80], x, 116, st)
    gd1_total = sum(iv(r['total']) for r in comps)
    done_c = sum(1 for r in comps if comp_forecast(r) >= 100)
    rrect(24, 500, 912, 28, fill=LBLUE, stroke=ICEBLUE, r=6)
    txt(480, 518, f'Hoàn thành 100%: {done_c} thành phần  ·  Cần theo dõi: {len(comps)-done_c} thành phần  '
        f'·  Tổng GĐ1 dự báo: {phase_fc.get("Giai đoạn 1",(0,))[0]:.2f}%', B, 9.5, NAVY2, 'c')
    c.showPage()

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Nhân sự: cơ cấu theo dự án / vai trò
# ════════════════════════════════════════════════════════════════════════════════
def slide_hr1():
    page_bg(); header(f'{PROJ_CODE} – TỔNG QUAN NHÂN SỰ')
    kpi_top(160, 82, 300, 60, BLUE, 'people', 'Tổng nhân sự', f'{EMP_TOT}  nhân sự', NAVY2)
    kpi_top(490, 82, 300, 60, TEAL, 'grid', f'Tổng MM', f'{TOTAL_MM:.2f}  MM', TEAL)
    # Left: theo dự án
    panel_header(24, 160, 456, 'CƠ CẤU THEO DỰ ÁN', NAVY)
    txt(330, 200, 'Nhân sự', B, 7.5, DG, 'c'); txt(390, 200, 'MM', B, 7.5, DG, 'c'); txt(448, 200, 'Tỷ trọng', B, 7.5, DG, 'c')
    mm_max = max((fv(r['mm']) for r in alloc_prod), default=1)
    ty = 208
    for r in alloc_prod:
        code = r['code']; mm = fv(r['mm']); hc = iv(r['hc'])
        ic('dot', 40, ty+11, 6, pcol(code)); txt(52, ty+14, code, B, 9, DG)
        bar(110, ty+9, 180, 8, mm/mm_max if mm_max else 0, pcol(code))
        txt(330, ty+14, str(hc), R, 8.5, DG, 'c')
        txt(390, ty+14, f'{mm:.2f}', R, 8.5, DG, 'c')
        txt(460, ty+14, f'{pct(mm,TOTAL_MM):.0f}%', B, 8.5, NAVY2, 'c')
        ty += 26
    rrect(24, ty, 456, 24, fill=LBLUE, r=6)
    txt(34, ty+16, 'Tổng cộng', B, 9, NAVY2); txt(330, ty+16, str(EMP_TOT), B, 9, NAVY2, 'c')
    txt(390, ty+16, f'{TOTAL_MM:.2f}', B, 9, NAVY2, 'c'); txt(460, ty+16, '100%', B, 9, NAVY2, 'c')
    # Right: theo đơn vị / vai trò
    panel_header(498, 160, 438, f'CƠ CẤU THEO {GLABEL}', TEAL)
    txt(800, 200, 'Nhân sự', B, 7.5, DG, 'c'); txt(858, 200, 'MM', B, 7.5, DG, 'c'); txt(912, 200, 'Tỷ trọng', B, 7.5, DG, 'c')
    roles = sorted(group_mm.items(), key=lambda x: -x[1]['mm'])[:9]
    rmax = max((v['mm'] for _, v in roles), default=1)
    ty = 208
    for role, v in roles:
        ic('dot', 514, ty+11, 6, TEAL); txt(526, ty+14, role[:16], R, 8.5, DG)
        bar(610, ty+9, 170, 8, v['mm']/rmax if rmax else 0, TEAL)
        txt(800, ty+14, str(v['hc']), R, 8.5, DG, 'c')
        txt(858, ty+14, f"{v['mm']:.2f}", R, 8.5, DG, 'c')
        txt(922, ty+14, f"{pct(v['mm'],TOTAL_MM):.0f}%", B, 8.5, TEAL, 'c')
        ty += 26
    # Insight
    rrect(24, 500, 912, 28, fill=LBLUE, stroke=ICEBLUE, r=6)
    circle(44, 514, 9, fill=BLUE); ic('info', 44, 514, 9, colors.white)
    top_prod = max(alloc_prod, key=lambda r: fv(r['mm'])) if alloc_prod else None
    if top_prod:
        txt(60, 517, f"INSIGHT  ·  Nhân sự tập trung chủ yếu ở {top_prod['code']} "
            f"({pct(fv(top_prod['mm']),TOTAL_MM):.0f}% MM)  ·  "
            f"Tổng {EMP_TOT} nhân sự / {TOTAL_MM:.2f} MM.", R, 9.5, DG)
    c.showPage()

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Phân bổ nguồn lực theo nhân sự (theo vai trò)
# ════════════════════════════════════════════════════════════════════════════════
def slide_hr_people():
    page_bg(); header(f'{PROJ_CODE} – TỔNG QUAN NHÂN SỰ')
    panel_header(24, 82, 912, f'PHÂN BỔ NGUỒN LỰC THEO NHÂN SỰ (NHÓM THEO {GLABEL})', NAVY)
    # group emp_list theo vai trò nếu có, ngược lại theo đơn vị
    groups = {}
    for e in emp_list:
        groups.setdefault(e.get(GKEY) or '—', []).append(e)
    order = sorted(groups.items(), key=lambda x: -sum(fv(p['mm']) for p in x[1]))[:6]
    n = len(order) or 1
    gap = 8; x0 = 24; total_w = 912
    cw = (total_w - gap*(n-1)) / n
    role_col = [BLUE, TEAL, GREEN, ORANGE, HexColor('#6d28d9'), HexColor('#0891b2')]
    for ci, (role, people) in enumerate(order):
        x = x0 + ci*(cw+gap)
        gmm = sum(fv(p['mm']) for p in people)
        col = role_col[ci % len(role_col)]
        rrect(x, 116, cw, 30, fill=col, r=6)
        txt(x+10, 130, role[:14], B, 9.5, colors.white)
        txt(x+cw-10, 130, f'{len(people)} · {gmm:.1f}MM', R, 7.5, colors.white, 'r')
        ty = 154
        for p in people[:17]:
            nm = (p['name'] or '')[:20]
            txt(x+8, ty, nm, R, 7, DG)
            txt(x+cw-8, ty, f"{fv(p['mm']):.1f}", R, 7, GREY, 'r')
            ty += 12.5
        if len(people) > 17:
            txt(x+8, ty, f'... +{len(people)-17} người', R, 6.5, LGREY)
    c.showPage()

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — GTEL vs OS theo dự án
# ════════════════════════════════════════════════════════════════════════════════
def slide_hr_gtel():
    page_bg(); header(f'{PROJ_CODE} – TỔNG QUAN NHÂN SỰ')
    cards = [('Headcount\nGTEL ICT', f'{EMP_GTEL} HC', BLUE, f'{pct(EMP_GTEL,EMP_TOT):.2f}%'),
             ('Headcount\nOutsourcing', f'{EMP_OUT} HC', TEAL, f'{pct(EMP_OUT,EMP_TOT):.2f}%'),
             ('Tổng\nHeadcount', f'{EMP_TOT} HC', NAVY2, '100%'),
             ('MM\nGTEL ICT', f'{GTEL_MM:.2f}', BLUE, f'{pct(GTEL_MM,TOTAL_MM):.2f}%'),
             ('MM\nOutsourcing', f'{OS_MM:.2f}', TEAL, f'{pct(OS_MM,TOTAL_MM):.2f}%'),
             ('Tổng MM', f'{TOTAL_MM:.2f}', NAVY2, '100%')]
    x = 24; w = 148
    for lb, vl, col, sub in cards:
        rrect(x, 82, w, 62, fill=colors.white, stroke=LINE, r=8)
        circle(x+22, 113, 13, fill=col); txt(x+22, 117, 'HC' if 'Head' in lb or 'Tổng\nH' in lb else 'MM', B, 7, colors.white, 'c')
        l1 = lb.split('\n')
        txt(x+42, 100, l1[0], B, 8, DG); txt(x+42, 111, l1[1] if len(l1)>1 else '', B, 8, DG)
        txt(x+42, 128, vl, B, 13, col); txt(x+42, 140, sub, R, 7, GREY)
        x += w + 5.6
    # Left: HC theo dự án (stacked)
    panel_header(24, 158, 456, 'HEADCOUNT THEO DỰ ÁN', NAVY)
    ic('sq', 50, 196, 6, BLUE); txt(60, 199, 'GTEL ICT', R, 7.5, DG)
    ic('sq', 140, 196, 6, TEAL); txt(150, 199, 'Outsourcing', R, 7.5, DG)
    txt(412, 199, 'Tổng', B, 7.5, DG, 'c'); txt(455, 199, '%', B, 7.5, DG, 'c')
    hc_max = max((iv(r['hc']) for r in alloc_prod), default=1)
    ty = 208
    for r in alloc_prod:
        code = r['code']; g = alloc_pivot.get(code, {}).get('GTEL ICT', {}).get('hc', 0)
        tot = iv(r['hc']); o = tot - g
        txt(34, ty+12, code, B, 8, DG)
        sbar(100, ty+6, 280*(tot/hc_max if hc_max else 0)+1, 12,
             [(g/tot if tot else 0, BLUE),(o/tot if tot else 0, TEAL)])
        txt(412, ty+12, str(tot), B, 8, DG, 'c'); txt(455, ty+12, f'{pct(tot,EMP_TOT):.1f}%', R, 8, GREY, 'c')
        ty += 22
    rrect(24, ty, 456, 22, fill=LBLUE, r=6)
    txt(34, ty+15, 'Tổng cộng', B, 8, NAVY2); txt(412, ty+15, str(EMP_TOT), B, 8, NAVY2, 'c')
    # Right: MM theo dự án
    panel_header(498, 158, 438, 'MM THEO DỰ ÁN', TEAL)
    ic('sq', 522, 196, 6, BLUE); txt(532, 199, 'GTEL ICT', R, 7.5, DG)
    ic('sq', 612, 196, 6, TEAL); txt(622, 199, 'Outsourcing', R, 7.5, DG)
    txt(882, 199, 'Tổng', B, 7.5, DG, 'c'); txt(922, 199, '%', B, 7.5, DG, 'c')
    mm_max2 = max((fv(r['mm']) for r in alloc_prod), default=1)
    ty = 208
    for r in alloc_prod:
        code = r['code']; gm = alloc_pivot.get(code, {}).get('GTEL ICT', {}).get('mm', 0.0)
        tm = fv(r['mm']); om = tm - gm
        txt(508, ty+12, code, B, 8, DG)
        sbar(570, ty+6, 270*(tm/mm_max2 if mm_max2 else 0)+1, 12,
             [(gm/tm if tm else 0, BLUE),(om/tm if tm else 0, TEAL)])
        txt(882, ty+12, f'{tm:.2f}', B, 8, DG, 'c'); txt(922, ty+12, f'{pct(tm,TOTAL_MM):.1f}%', R, 8, GREY, 'c')
        ty += 22
    rrect(498, ty, 438, 22, fill=LTEAL, r=6)
    txt(508, ty+15, 'Tổng cộng', B, 8, TEAL); txt(882, ty+15, f'{TOTAL_MM:.2f}', B, 8, TEAL, 'c')
    # Vendor row
    rrect(24, 446, 912, 80, fill=colors.white, stroke=LINE, r=8)
    txt(38, 466, 'PHÂN BỔ NGUỒN LỰC OUTSOURCING THEO VENDOR', B, 9.5, NAVY2)
    vx = 40
    for v in os_vendors[:9]:
        rrect(vx, 478, 96, 40, fill=LBLUE, r=6)
        txt(vx+48, 492, (v['company'] or '')[:9], B, 7.5, NAVY2, 'c')
        txt(vx+48, 508, f"{iv(v['hc'])} HC · {fv(v['mm']):.1f}", R, 7.5, DG, 'c')
        vx += 100
    c.showPage()

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Ma trận dự án × đơn vị
# ════════════════════════════════════════════════════════════════════════════════
def slide_hr_matrix():
    page_bg(); header(f'{PROJ_CODE} – TỔNG QUAN NHÂN SỰ')
    vendors = [c for c in companies_all if c != 'GTEL ICT']
    def matrix(x, ty, w, title, color, key):
        panel_header(x, ty, w, title, color)
        cols = ['Dự án', 'GTEL ICT'] + list(vendors) + ['Tổng']
        hdr = [P(h, B, 5.5, colors.white, TA_CENTER, 6) for h in cols]
        rows = [hdr]
        coltot = [0.0]*(len(vendors)+1)
        for r in alloc_prod:
            code = r['code']; piv = alloc_pivot.get(code, {})
            g = piv.get('GTEL ICT', {}).get(key, 0)
            line = [P(code, B, 6.5, NAVY2)]
            line.append(P(f'{g:.2f}' if key=='mm' else g, R, 6.5, DG, TA_CENTER))
            coltot[0] += g
            for vi, v in enumerate(vendors):
                val = piv.get(v, {}).get(key, 0)
                coltot[vi+1] += val
                line.append(P((f'{val:.2f}' if key=='mm' else val) if val else '', R, 6.5, DG, TA_CENTER))
            rowtot = (fv(r['mm']) if key=='mm' else iv(r['hc']))
            line.append(P(f'{rowtot:.2f}' if key=='mm' else rowtot, B, 6.5, NAVY2, TA_CENTER))
            rows.append(line)
        foot = [P('Tổng cộng', B, 6.5, colors.white)]
        for tv in coltot:
            foot.append(P(f'{tv:.2f}' if key=='mm' else int(tv), B, 6.5, colors.white, TA_CENTER))
        grand = TOTAL_MM if key=='mm' else EMP_TOT
        foot.append(P(f'{grand:.2f}' if key=='mm' else grand, B, 6.5, colors.white, TA_CENTER))
        rows.append(foot)
        ncol = len(cols)
        c0 = 38; ctot = 34; rest = (w - c0 - ctot) / (ncol-2)
        cw = [c0] + [rest]*(ncol-2) + [ctot]
        st = TableStyle([('BACKGROUND',(0,0),(-1,0),THBG),
            ('ROWBACKGROUNDS',(0,1),(-1,-2),[ROW_A,ROW_B]),
            ('BACKGROUND',(0,-1),(-1,-1),(NAVY2 if key=='hc' else TEAL)),
            ('GRID',(0,0),(-1,-1),0.3,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)])
        draw_table(rows, cw, x, ty+30, st)
    matrix(24, 92, 456, 'HEADCOUNT THEO DỰ ÁN & ĐƠN VỊ', NAVY, 'hc')
    matrix(498, 92, 438, 'MM THEO DỰ ÁN & ĐƠN VỊ', TEAL, 'mm')
    c.showPage()

# ════════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — THANKS
# ════════════════════════════════════════════════════════════════════════════════
def slide_thanks():
    page_bg()
    rect(0, 0, PAGE_W, 64, fill=NAVY); rect(0, 64, PAGE_W, 4, fill=BLUE)
    logo(26, 32); txt(64, 38, PROJ_CODE, B, 18, colors.white)
    rrect(770, 14, 168, 38, fill=NAVY2, stroke=HexColor('#3b5bb5'), r=6)
    txt(786, 28, f'Ngày báo cáo: {REPORT_DATE}', R, 8.5, colors.white)
    txt(786, 42, f'Phạm vi: {PROJ_CODE}', R, 8.5, ICEBLUE)
    illustration(720, 300)
    txt(60, 230, 'XIN CẢM ƠN', B, 46, NAVY2)
    rect(60, 258, 90, 4, fill=BLUE)
    txt(60, 295, 'Trân trọng cảm ơn Quý Anh/Chị', B, 14, NAVY2)
    txt(60, 318, 'đã theo dõi báo cáo.', B, 14, NAVY2)
    txt(60, 360, (PROJ_NAME if PROJ_CODE!='ALL' else 'Tổng hợp tất cả dự án'), R, 11, GREY)
    deco_dots(30, 430, 5, 6)
    c.showPage()

# ── BUILD ────────────────────────────────────────────────────────────────────────
slide_cover()
slide_toc()
slide_overview1()
slide_overview2()
slide_gd1_systems()
slide_gd1_status()
slide_gd1_components()
slide_hr1()
slide_hr_people()
slide_hr_gtel()
slide_hr_matrix()
slide_thanks()
c.save()
print(f'Slide PDF generated: {OUT_PATH} | {PROJ_CODE} | {TOT} milestones | {EMP_TOT} emp')
