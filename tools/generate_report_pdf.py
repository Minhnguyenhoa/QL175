"""
generate_report_pdf.py — Báo cáo tiến độ dự án H05YTS
Cấu trúc đầy đủ theo mẫu: Tổng thể + Điểm quy đổi + GĐ1 + Nhân sự + GTEL/OS
Thêm: báo cáo riêng cho từng hệ thống (HIS, LIS, EMR, ...)
"""
import sys, argparse, os, math
sys.stdout.reconfigure(encoding='utf-8')

from datetime import date as dt_date
import mysql.connector
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── ARGS ──────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument('--out',     default=r'D:/QT_175/database/bao_cao_tien_do.pdf')
parser.add_argument('--date',    default=dt_date.today().strftime('%d/%m/%Y'))
parser.add_argument('--host',    default='localhost')
parser.add_argument('--port',    default=3306, type=int)
parser.add_argument('--db',      default='project_mgmt')
parser.add_argument('--user',    default='root')
parser.add_argument('--pwd',     default='123456')
parser.add_argument('--project', default=None,
                    help='Mã dự án, có thể truyền nhiều cách:\n'
                         '  Một dự án:   --project H05YTS\n'
                         '  Nhiều dự án: --project H05YTS,H06ABC\n'
                         '  Tất cả:      --project ALL  (hoặc bỏ trống)')
args = parser.parse_args()

REPORT_DATE = args.date
OUT_PATH    = args.out

# ── PROJECT LOOKUP ─────────────────────────────────────────────────────────────
import mysql.connector as _mc
_cnx = _mc.connect(host=args.host, port=args.port, database=args.db,
                   user=args.user, password=args.pwd, charset='utf8mb4')
_cur = _cnx.cursor(dictionary=True)

# Load all project groups first
_cur.execute("SELECT id, code, name FROM project_groups ORDER BY id")
_all_pgs = _cur.fetchall()

_req = (args.project or '').strip().upper()

if not _req or _req == 'ALL':
    # Tất cả dự án — không filter
    PROJ_IDS  = []                        # rỗng = không filter
    PROJ_CODE = 'ALL'
    PROJ_NAME = 'Tất cả dự án'
    PROJ_LIST = [pg['code'] for pg in _all_pgs]  # danh sách tên để hiển thị
else:
    # Có thể là "H05YTS" hoặc "H05YTS,H06ABC"
    codes_req = [c.strip() for c in _req.split(',') if c.strip()]
    matched = [pg for pg in _all_pgs if pg['code'].upper() in codes_req]
    not_found = [c for c in codes_req if c not in {pg['code'].upper() for pg in matched}]
    if not_found:
        print(f"WARNING: Project(s) not found: {not_found} — sẽ bị bỏ qua")
    if matched:
        PROJ_IDS  = [pg['id'] for pg in matched]
        PROJ_LIST = [pg['code'] for pg in matched]
        if len(matched) == 1:
            PROJ_CODE = matched[0]['code']
            PROJ_NAME = matched[0]['name'] or matched[0]['code']
        else:
            PROJ_CODE = '+'.join(pg['code'] for pg in matched)
            PROJ_NAME = ', '.join(pg['code'] for pg in matched)
    else:
        print(f"WARNING: Không tìm thấy dự án nào khớp — lấy tất cả dữ liệu")
        PROJ_IDS  = []
        PROJ_CODE = 'ALL'
        PROJ_NAME = 'Tất cả dự án'
        PROJ_LIST = [pg['code'] for pg in _all_pgs]

_cur.close(); _cnx.close()

# ── SQL FILTER HELPERS ─────────────────────────────────────────────────────────
# PROJ_IDS = []  → không filter (tất cả dự án)
# PROJ_IDS = [5] → chỉ H05YTS
# PROJ_IDS = [5,6] → H05YTS + H06ABC
if PROJ_IDS:
    _ids = ','.join(str(i) for i in PROJ_IDS)   # an toàn: từ DB lookup, không phải user input
    MS_WHERE  = f" WHERE product_id IN (SELECT id FROM products WHERE project_group_id IN ({_ids}))"
    MS_AND    = f" AND product_id IN (SELECT id FROM products WHERE project_group_id IN ({_ids}))"
    PROD_WHER = f" WHERE p.project_group_id IN ({_ids})"
    PROD_AND  = f" AND p.project_group_id IN ({_ids})"
    EMP_WHERE = (f" WHERE id IN (SELECT DISTINCT employee_id FROM resource_allocations ra"
                 f" JOIN products p ON ra.product_id=p.id WHERE p.project_group_id IN ({_ids}))")
    EMP_AND   = (f" AND id IN (SELECT DISTINCT employee_id FROM resource_allocations ra"
                 f" JOIN products p ON ra.product_id=p.id WHERE p.project_group_id IN ({_ids}))")
    RA_WHER   = f" WHERE p.project_group_id IN ({_ids})"
    RA_AND    = f" AND p.project_group_id IN ({_ids})"
    OS_AND    = f" AND ra.product_id IN (SELECT id FROM products WHERE project_group_id IN ({_ids}))"
else:
    # Không filter = lấy tất cả
    MS_WHERE = MS_AND = PROD_WHER = PROD_AND = ""
    EMP_WHERE = EMP_AND = RA_WHER = RA_AND = OS_AND = ""

print(f'Project: {PROJ_CODE} (ids={PROJ_IDS}) — {PROJ_NAME[:60]}')

# ── FONT ──────────────────────────────────────────────────────────────────────
FONT_DIRS = [r'C:\Windows\Fonts', r'C:\Users\Mr.Cua\AppData\Local\Microsoft\Windows\Fonts']
def find_font(*names):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p): return p
    return None

reg_path  = find_font('arial.ttf', 'Arial.ttf', 'DejaVuSans.ttf')
bold_path = find_font('arialbd.ttf', 'Arial Bold.ttf', 'DejaVuSans-Bold.ttf')
R  = 'ArialReg';  B = 'ArialBold'
if reg_path:  pdfmetrics.registerFont(TTFont(R, reg_path))
else: R = 'Helvetica'
if bold_path: pdfmetrics.registerFont(TTFont(B, bold_path))
else: B = 'Helvetica-Bold'

# ── COLORS ────────────────────────────────────────────────────────────────────
C_NAVY  = colors.HexColor('#003a8c')
C_BLUE  = colors.HexColor('#1677ff')
C_GREEN = colors.HexColor('#52c41a')
C_ORA   = colors.HexColor('#fa8c16')
C_RED   = colors.HexColor('#ff4d4f')
C_PURP  = colors.HexColor('#531dab')
C_GREY  = colors.HexColor('#8c8c8c')
C_DGREY = colors.HexColor('#333333')
C_LGREY = colors.HexColor('#f5f5f5')
C_LBLUE = colors.HexColor('#e6f4ff')
C_YELL  = colors.HexColor('#fffbe6')
C_WHITE = colors.white
PAGE_W, PAGE_H = A4
MARGIN = 2*cm
CW = PAGE_W - 2*MARGIN   # ~17.15 cm usable width

# ── STYLES ────────────────────────────────────────────────────────────────────
def S(name, font=R, sz=8.5, color=C_DGREY, align=TA_LEFT, lead=None, bold=False):
    return ParagraphStyle(name, fontName=(B if bold else font),
        fontSize=sz, textColor=color, alignment=align,
        leading=lead or sz*1.35, spaceBefore=0, spaceAfter=0)

ST_TH = S('th', B, 8, C_WHITE, TA_CENTER, 10)
ST_TD = S('td', R, 8, C_DGREY, TA_LEFT,   10)
ST_TC = S('tc', R, 8, C_DGREY, TA_CENTER, 10)
ST_TR = S('tr', R, 8, C_DGREY, TA_RIGHT,  10)

# ── DB ────────────────────────────────────────────────────────────────────────
def get_conn():
    return mysql.connector.connect(
        host=args.host, port=args.port, database=args.db,
        user=args.user, password=args.pwd, charset='utf8mb4')

def Q(sql, params=None):
    c = get_conn(); cur = c.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    cur.close(); c.close(); return rows

def Q1(sql, params=None):
    r = Q(sql, params); return r[0] if r else {}

def iv(x, d=0):
    """int value with default"""
    try: return int(x or d)
    except: return d

def fv(x, d=0.0):
    """float value with default"""
    try: return float(x or d)
    except: return d

def pct(a, b):
    return round(a/b*100, 2) if b else 0

def fpct(a, b):
    return f'{pct(a,b):.1f}%'

# ── CONVERSION RATES (điểm quy đổi) ──────────────────────────────────────────
CONV = {
    ('Pilot', 1): (1.00, 'Pilot — Đã hoàn thành'),
    ('Kiểm thử nội bộ', 1): (0.70, 'Kiểm thử nội bộ — Đã hoàn thành'),
    ('Coding', 1): (0.50, 'Coding — Đã hoàn thành'),
    ('Pilot', 0): (0.80, 'Pilot — Đang thực hiện'),
    ('Kiểm thử nội bộ', 0): (0.70, 'Kiểm thử nội bộ — Đang thực hiện'),
    ('Coding', 0): (0.35, 'Coding — Đang thực hiện'),
    ('Phân tích yêu cầu nghiệp vụ', 0): (0.10, 'Phân tích YCNV — Đang thực hiện'),
    (None, 0): (0.00, 'Chưa bắt đầu'),
}

def calc_forecast(rows):
    """rows: list of (current_phase, is_done, count)
    Returns: (forecast_pct, total_points, total_count, breakdown)
    breakdown: [(label, count, rate, points, weight_pct)]"""
    total = sum(iv(r['cnt']) for r in rows)
    breakdown = {}
    for r in rows:
        cp  = r.get('current_phase')
        dn  = 1 if iv(r.get('is_done')) else 0
        cnt = iv(r['cnt'])
        key = (cp, dn)
        rate, label = CONV.get(key, (0.00, f'{cp} — {"Đã HT" if dn else "Đang TH"}'))
        if label not in breakdown:
            breakdown[label] = {'cnt': 0, 'rate': rate}
        breakdown[label]['cnt'] += cnt
    items = []
    total_pts = 0.0
    for label, v in sorted(breakdown.items(), key=lambda x: -x[1]['rate']):
        pts = v['cnt'] * v['rate']
        total_pts += pts
        items.append({
            'label': label,
            'cnt': v['cnt'],
            'rate': v['rate'],
            'pts': pts,
            'w_pct': pct(v['cnt'], total),
        })
    fc_pct = pct(total_pts, total)
    return fc_pct, total_pts, total, items

# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
print('Querying database...')

# ── Overall milestone stats ───────────────────────────────────────────────────
ov = Q1(f"""
    SELECT COUNT(*) total,
      SUM(actual_end_date IS NOT NULL) done,
      SUM(actual_end_date IS NULL AND current_phase IS NOT NULL) in_prog,
      SUM(remind='Quá hạn') overdue
    FROM milestones{MS_WHERE}""")
TOT   = iv(ov['total'])
DONE  = iv(ov['done'])
INPROG= iv(ov['in_prog'])
OVERD = iv(ov['overdue'])
NOSTART = max(0, TOT - DONE - INPROG)

# ── Phase breakdown (GĐ1, GĐ2) ───────────────────────────────────────────────
phase_stats = Q(f"""
    SELECT phase, COUNT(*) total,
      SUM(actual_end_date IS NOT NULL) done,
      SUM(actual_end_date IS NULL AND current_phase IS NOT NULL) in_prog,
      SUM(remind='Quá hạn') overdue
    FROM milestones WHERE phase IS NOT NULL{MS_AND}
    GROUP BY phase ORDER BY phase""")

# ── Conversion-point breakdown (overall) ─────────────────────────────────────
conv_rows = Q(f"""
    SELECT current_phase,
      (actual_end_date IS NOT NULL) is_done,
      COUNT(*) cnt
    FROM milestones{MS_WHERE}
    GROUP BY current_phase, (actual_end_date IS NOT NULL)
    ORDER BY current_phase, is_done DESC""")
FC_PCT_TOTAL, FC_PTS_TOTAL, _, FC_ITEMS = calc_forecast(conv_rows)

# ── By product (all milestones) ───────────────────────────────────────────────
by_prod = Q(f"""
    SELECT p.code, p.name, p.status, p.current_phase AS cur_phase,
      COUNT(m.id) total,
      SUM(m.actual_end_date IS NOT NULL) done,
      SUM(m.actual_end_date IS NULL AND m.current_phase IS NOT NULL) in_prog,
      SUM(m.remind='Quá hạn') overdue
    FROM products p LEFT JOIN milestones m ON m.product_id=p.id{PROD_WHER}
    GROUP BY p.id,p.code,p.name,p.status,p.current_phase
    ORDER BY p.code""")

# ── GĐ1 detail by product+status ─────────────────────────────────────────────
gd1_by_prod_phase = Q(f"""
    SELECT p.code,
      SUM(m.current_phase='Coding' AND m.actual_end_date IS NULL)    coding_prog,
      SUM(m.current_phase='Coding' AND m.actual_end_date IS NOT NULL) coding_done,
      SUM(m.current_phase='Kiểm thử nội bộ' AND m.actual_end_date IS NULL)    ktnb_prog,
      SUM(m.current_phase='Kiểm thử nội bộ' AND m.actual_end_date IS NOT NULL) ktnb_done,
      SUM(m.current_phase='Pilot' AND m.actual_end_date IS NULL)    pilot_prog,
      SUM(m.current_phase='Pilot' AND m.actual_end_date IS NOT NULL) pilot_done,
      COUNT(m.id) total,
      SUM(m.actual_end_date IS NOT NULL) done
    FROM products p LEFT JOIN milestones m ON m.product_id=p.id
    WHERE m.phase='Giai đoạn 1'{PROD_AND}
    GROUP BY p.code ORDER BY p.code""")

# ── Milestone components GĐ1 ─────────────────────────────────────────────────
gd1_comps = Q(f"""
    SELECT p.code prod_code, m.component_milestone comp,
      COUNT(*) total,
      SUM(m.actual_end_date IS NOT NULL) done,
      SUM(m.current_phase='Coding' AND m.actual_end_date IS NULL) coding_prog,
      SUM(m.current_phase='Coding' AND m.actual_end_date IS NOT NULL) coding_done,
      SUM(m.current_phase='Kiểm thử nội bộ' AND m.actual_end_date IS NULL) ktnb_prog,
      SUM(m.current_phase='Kiểm thử nội bộ' AND m.actual_end_date IS NOT NULL) ktnb_done,
      SUM(m.current_phase='Pilot' AND m.actual_end_date IS NULL) pilot_prog,
      SUM(m.current_phase='Pilot' AND m.actual_end_date IS NOT NULL) pilot_done
    FROM milestones m JOIN products p ON m.product_id=p.id
    WHERE m.phase='Giai đoạn 1' AND m.component_milestone IS NOT NULL{PROD_AND}
    GROUP BY p.code, m.component_milestone
    ORDER BY p.code, m.component_milestone""")

# ── Employee overview ──────────────────────────────────────────────────────────
emp_ov = Q1(f"SELECT COUNT(*) total, SUM(company='GTEL ICT') gtel FROM employees{EMP_WHERE}")
EMP_TOT  = iv(emp_ov['total'])
EMP_GTEL = iv(emp_ov['gtel'])
EMP_OUT  = EMP_TOT - EMP_GTEL

by_company = Q(f"""
    SELECT company, COUNT(*) hc FROM employees
    WHERE company IS NOT NULL{EMP_AND} GROUP BY company ORDER BY hc DESC""")

by_role = Q(f"""
    SELECT role, COUNT(*) hc FROM employees
    WHERE role IS NOT NULL{EMP_AND} GROUP BY role ORDER BY hc DESC LIMIT 12""")

# ── Allocation by product ─────────────────────────────────────────────────────
alloc_prod = Q(f"""
    SELECT p.code, p.name,
      COUNT(DISTINCT ra.employee_id) hc,
      ROUND(SUM(ra.allocation_percent),2) mm
    FROM resource_allocations ra JOIN products p ON ra.product_id=p.id{RA_WHER}
    GROUP BY p.id,p.code,p.name ORDER BY mm DESC""")

# ── GTEL vs Outsourcing per product ──────────────────────────────────────────
alloc_detail = Q(f"""
    SELECT p.code, e.company,
      COUNT(DISTINCT e.id) hc,
      ROUND(SUM(ra.allocation_percent),2) mm
    FROM resource_allocations ra
    JOIN products p ON ra.product_id=p.id
    JOIN employees e ON e.id=ra.employee_id{RA_WHER}
    GROUP BY p.code,e.company ORDER BY p.code,e.company""")

# Build pivot: {prod_code: {company: {hc, mm}}}
companies_all = sorted(set(r['company'] for r in by_company))
alloc_pivot = {}
for r in alloc_detail:
    code = r['code']
    if code not in alloc_pivot: alloc_pivot[code] = {}
    alloc_pivot[code][r['company']] = {'hc': iv(r['hc']), 'mm': fv(r['mm'])}

# Outsourcing vendors
os_vendors = Q(f"""
    SELECT e.company,
      COUNT(DISTINCT e.id) hc,
      ROUND(SUM(ra.allocation_percent),2) mm
    FROM resource_allocations ra JOIN employees e ON e.id=ra.employee_id
    WHERE e.company != 'GTEL ICT'{OS_AND}
    GROUP BY e.company ORDER BY mm DESC""")

# ── Per-product milestone forecast ───────────────────────────────────────────
prod_forecast = {}
for pr in by_prod:
    code = pr['code']
    r2 = Q("""
        SELECT m.current_phase, (m.actual_end_date IS NOT NULL) is_done, COUNT(*) cnt
        FROM milestones m JOIN products p ON m.product_id=p.id
        WHERE p.code=%s
        GROUP BY m.current_phase,(m.actual_end_date IS NOT NULL)""", (code,))
    prod_forecast[code] = calc_forecast(r2)

print(f'  Milestones: {TOT} | Done: {DONE} | Forecast: {FC_PCT_TOTAL:.1f}%')
print(f'  Employees: {EMP_TOT} (GTEL: {EMP_GTEL}, OS: {EMP_OUT})')
print(f'  Products: {len(by_prod)} | GD1 comps: {len(gd1_comps)}')

# ══════════════════════════════════════════════════════════════════════════════
# HELPER BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def hdr_bar(num, title, subtitle='', bg=C_NAVY):
    """Section header bar (blue strip with number + title)."""
    cells = [[
        Paragraph(str(num), S('sn',B,24,C_WHITE,TA_CENTER,28)),
        Paragraph(title,    S('sh',B,13,C_WHITE,TA_LEFT,17)),
        Paragraph(subtitle or f'Ngày báo cáo: {REPORT_DATE}',
                  S('sd',R,8.5,colors.HexColor('#91caff'),TA_RIGHT,12)),
    ]]
    return Table(cells, colWidths=[40, CW-120, 80],
        style=TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),bg),
            ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
            ('LEFTPADDING',(0,0),(0,-1),12),('LEFTPADDING',(1,0),(1,-1),10),
            ('RIGHTPADDING',(0,0),(-1,-1),12),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ROUNDEDCORNERS',[4]),
        ]))

def sec_bar(title, color=C_BLUE):
    """Sub-section bar."""
    return Table([[Paragraph(title, S('sb',B,10,C_DGREY,TA_LEFT,13))]],
        colWidths=[CW],
        style=TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),C_LGREY),
            ('LINEBEFORE',(0,0),(0,-1),4,color),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ]))

def kpi_row(items):
    """items = [(value, label, color, suffix)]"""
    n = len(items)
    w = CW/n
    cells = [[
        Table([[Paragraph(f'{v}{(" "+sfx) if sfx else ""}',
                      S(f'kv{i}',B,15,c,TA_CENTER,18))],
               [Paragraph(lbl, S(f'kl{i}',R,7.5,C_GREY,TA_CENTER,10))]],
        colWidths=[w-8],
        style=TableStyle([
            ('LINEABOVE',(0,0),(-1,0),3,c),
            ('BOX',(0,0),(-1,-1),0.4,colors.HexColor('#d9d9d9')),
            ('BACKGROUND',(0,0),(-1,-1),C_WHITE),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ]))
        for i,(v,lbl,c,sfx) in enumerate(items)
    ]]
    return Table(cells, colWidths=[w]*n,
        style=TableStyle([
            ('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2),
            ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
        ]))

def data_table(header, rows, widths, row_extras=None):
    """Standard table with dark blue header."""
    all_rows = [header]+rows
    n = len(rows)
    ts = TableStyle([
        ('BACKGROUND',(0,0),(-1,0),C_NAVY),
        ('TEXTCOLOR',(0,0),(-1,0),C_WHITE),
        ('FONTNAME',(0,0),(-1,0),B),
        ('FONTNAME',(0,1),(-1,-1),R),
        ('FONTSIZE',(0,0),(-1,-1),8),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[C_WHITE,C_LGREY]),
        ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#e0e0e0')),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ])
    if row_extras:
        for ri,bg in row_extras:
            ts.add('BACKGROUND',(0,ri+1),(-1,ri+1),bg)
    return Table(all_rows, colWidths=widths, repeatRows=1, style=ts, hAlign='LEFT')

def insight_box(lines, bg=C_LBLUE, border=C_BLUE):
    data = [[Paragraph(l, S('ins',R,8.5,C_DGREY,TA_LEFT,12))] for l in lines]
    return Table(data, colWidths=[CW],
        style=TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),bg),
            ('BOX',(0,0),(-1,-1),0.5,border),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),
        ]))

def color_pct(p):
    return C_GREEN if p>=70 else C_ORA if p>=30 else C_RED

def p_done(v,t):
    p=pct(iv(v),iv(t)); return Paragraph(f'{p:.1f}%',S('pd',B,8,color_pct(p),TA_CENTER))
def p_green(v): return Paragraph(str(iv(v)), S('pg',B,8,C_GREEN,TA_CENTER))
def p_red(v):   return Paragraph(str(iv(v)), S('pr',B,8,C_RED,TA_CENTER))
def p_ora(v):   return Paragraph(str(iv(v)), S('po',B,8,C_ORA,TA_CENTER))
def p_c(v,bold=False): return Paragraph(str(v), S('pc1',B if bold else R,8,C_DGREY,TA_CENTER))
def p_r(v): return Paragraph(str(v), S('pr2',R,8,C_DGREY,TA_RIGHT))
def p_l(v): return Paragraph(str(v), S('pl2',R,8,C_DGREY,TA_LEFT))
def p_blue(v):  return Paragraph(str(v), S('pb',B,8,C_BLUE,TA_CENTER))

PROD_COLOR = {
    'HIS':'#096dd9','LIS':'#08979c','EMR':'#531dab',
    'KSK':'#d46b08','QLTTDL':'#389e0d','THDB':'#cf1322',
}
PROD_LABEL = {
    'HIS':'HIS — Hệ thống thông tin bệnh viện',
    'LIS':'LIS — Quản lý xét nghiệm',
    'EMR':'EMR — Bệnh án điện tử',
    'KSK':'KSK — Sức khỏe CBCS',
    'QLTTDL':'QLTTDL — Trung tâm dữ liệu',
    'THDB':'THDB — Tích hợp đồng bộ',
}

# ══════════════════════════════════════════════════════════════════════════════
# BUILD STORY
# ══════════════════════════════════════════════════════════════════════════════
story = []
SP4  = Spacer(1, 4)
SP8  = Spacer(1, 8)
SP12 = Spacer(1, 12)
SP16 = Spacer(1, 16)

# ─────────────────────────────────────────────────────────────────────────────
# TRANG BÌA
# ─────────────────────────────────────────────────────────────────────────────
story.append(Table(
    [[Paragraph(f'{PROJ_CODE}{"" if PROJ_CODE=="ALL" else " — "}{("" if PROJ_CODE=="ALL" else (PROJ_NAME[:55]+"..." if len(PROJ_NAME)>55 else PROJ_NAME))}',
                S('cs',R,11,colors.HexColor('#91caff'),TA_LEFT,14))],
     [Paragraph('BÁO CÁO TIẾN ĐỘ DỰ ÁN',
                S('ct',B,26,C_WHITE,TA_LEFT,32))],
     [Paragraph(f'Ngày báo cáo: {REPORT_DATE}  ·  Phạm vi: Giai đoạn 1',
                S('cd',R,10,colors.HexColor('#bae0ff'),TA_LEFT,13))],
     [SP8],
     [Table([[
         Table([[Paragraph(str(TOT),S('cv1',B,34,C_WHITE,TA_CENTER,40))],
                [Paragraph('TỔNG MILESTONE',S('cl1',R,8,colors.HexColor('#91caff'),TA_CENTER,11))]],
               colWidths=[120], style=TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)])),
         Table([[Paragraph(f'{FC_PCT_TOTAL:.2f}%',
                            S('cv2',B,34,colors.HexColor('#95f204') if FC_PCT_TOTAL>=50 else colors.HexColor('#ffc53d'),TA_CENTER,40))],
                [Paragraph('DỰ BÁO HOÀN THÀNH',S('cl2',R,8,colors.HexColor('#91caff'),TA_CENTER,11))]],
               colWidths=[140], style=TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)])),
         Table([[Paragraph(str(DONE),S('cv3',B,34,C_GREEN,TA_CENTER,40))],
                [Paragraph(f'ĐÃ HOÀN THÀNH ({fpct(DONE,TOT)})',S('cl3',R,8,colors.HexColor('#91caff'),TA_CENTER,11))]],
               colWidths=[120], style=TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)])),
     ]], colWidths=[120,140,120],
     style=TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                       ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))],
     [SP8],
     [Paragraph('Báo cáo tổng hợp tiến độ, nguồn lực và khối lượng công việc',
                S('cs2',R,9,colors.HexColor('#bae0ff'),TA_LEFT,12))],
     [Paragraph('Tài liệu này chứa thông tin nội bộ — không phát hành ra bên ngoài',
                S('cs3',R,8,colors.HexColor('#69b1ff'),TA_LEFT,11))],
    ], colWidths=[CW],
    style=TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),C_NAVY),
        ('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),22),('RIGHTPADDING',(0,0),(-1,-1),16),
        ('ROUNDEDCORNERS',[8]),
    ])))
story.append(SP12)

# ─────────────────────────────────────────────────────────────────────────────
# MỤC LỤC
# ─────────────────────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(Paragraph('NỘI DUNG BÁO CÁO', S('toc_h',B,14,C_NAVY,TA_LEFT,18)))
story.append(Paragraph(f'Ngày báo cáo: {REPORT_DATE}', S('toc_d',R,9,C_GREY,TA_LEFT,12)))
story.append(SP12)

toc = [
    ('1','Tổng thể tiến độ dự án',
     'Tổng quan tiến độ, cơ cấu khối lượng và điểm quy đổi hoàn thành toàn dự án','3'),
    ('2','Tiến độ Giai đoạn 1',
     'Tổng quan cơ cấu khối lượng, hiệu quả thực hiện và tỷ lệ hoàn thành theo hệ thống','5'),
    ('3','Nhân sự dự án',
     'Tổng quan headcount, cơ cấu nhân sự theo dự án, vai trò và phân bổ nguồn lực','8'),
    ('4','Báo cáo từng hệ thống',
     'Chi tiết tiến độ và nhân sự riêng cho từng hệ thống: HIS, LIS, EMR, KSK, QLTTDL, THDB','11'),
]
for num,title,desc,pg in toc:
    story.append(Table([[
        Paragraph(num, S('tn',B,16,C_BLUE,TA_CENTER,20)),
        Table([[Paragraph(title, S('tt',B,10,C_NAVY,TA_LEFT,14))],
               [Paragraph(desc,  S('td2',R,8.5,C_GREY,TA_LEFT,12))]],
              colWidths=[CW-80],
              style=TableStyle([('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),('LEFTPADDING',(0,0),(-1,-1),0)])),
        Paragraph(f'Tr. {pg}', S('tp',B,10,C_BLUE,TA_RIGHT,14)),
    ]], colWidths=[36, CW-80, 44],
    style=TableStyle([
        ('BOX',(0,0),(-1,-1),0.5,colors.HexColor('#d9d9d9')),
        ('LINEBEFORE',(0,0),(0,-1),4,C_BLUE),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(0,0),(0,-1),10),('LEFTPADDING',(1,0),(1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('BACKGROUND',(0,0),(-1,-1),C_WHITE),
    ])))
    story.append(SP6:=Spacer(1,6))

story.append(SP8)
story.append(insight_box([
    '<b>Ghi chú phương pháp tính Dự báo Hoàn thành:</b>',
    'Pilot/Staging đã hoàn thành = 100%  |  Kiểm thử nội bộ đã/đang HT = 70%',
    'Pilot/Staging đang thực hiện = 80%  |  Coding đang thực hiện = 35%  |  Coding đã HT = 50%',
    'Phân tích YCNV đang TH = 10%  |  Chưa bắt đầu = 0%',
    'Công thức: Dự báo HT = Σ(Số lượng × Tỷ lệ quy đổi) / Tổng số milestone',
], bg=C_YELL, border=colors.HexColor('#ffe58f')))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — TỔNG THỂ TIẾN ĐỘ DỰ ÁN
# ─────────────────────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(hdr_bar('1','TỔNG THỂ TIẾN ĐỘ DỰ ÁN'))
story.append(SP12)

story.append(kpi_row([
    (TOT,      'TỔNG MILESTONE',    C_BLUE, ''),
    (DONE,     f'ĐÃ HOÀN THÀNH',   C_GREEN, fpct(DONE,TOT)),
    (INPROG,   'ĐANG THỰC HIỆN',   C_ORA,  fpct(INPROG,TOT)),
    (NOSTART,  'CHƯA BẮT ĐẦU',     C_GREY, fpct(NOSTART,TOT)),
    (OVERD,    'QUÁ HẠN',          C_RED,  ''),
]))
story.append(SP12)

# Dự báo HT theo giai đoạn
story.append(sec_bar('Dự báo Hoàn thành theo Giai đoạn'))
story.append(SP8)

phase_fc_rows = []
for ps in phase_stats:
    ph = ps['phase'] or ''
    t = iv(ps['total']); d = iv(ps['done']); ip = iv(ps['in_prog']); ov2 = iv(ps['overdue'])
    r3 = Q(f"""SELECT current_phase,(actual_end_date IS NOT NULL) is_done,COUNT(*) cnt
              FROM milestones WHERE phase=%s{MS_AND} GROUP BY current_phase,(actual_end_date IS NOT NULL)""", (ph,))
    fc, pts, _, _ = calc_forecast(r3)
    ns = max(0, t - d - ip)
    phase_fc_rows.append([
        Paragraph(ph, ST_TD),
        p_c(t),
        p_green(d), p_ora(ip), p_c(ns), p_red(ov2),
        Paragraph(f'{pts:.1f} / {t}', ST_TC),
        Paragraph(f'{fc:.1f}%', S('fc',B,8,color_pct(fc),TA_CENTER)),
    ])

story.append(data_table(
    [Paragraph(h,ST_TH) for h in ['Giai đoạn','Tổng','Đã HT','Đang TH','Chưa BĐ','Quá hạn','Điểm / Tổng','Dự báo HT']],
    phase_fc_rows,
    [CW*0.25, CW*0.07, CW*0.09, CW*0.1, CW*0.1, CW*0.09, CW*0.15, CW*0.15]))
story.append(SP12)

# Cơ cấu khối lượng
story.append(sec_bar('Cơ cấu Khối lượng Công việc'))
story.append(SP8)
story.append(data_table(
    [Paragraph(h,ST_TH) for h in ['Giai đoạn','Chưa BĐ','Đang TH','Đã HT','Tổng','Dự báo HT']],
    [[Paragraph(str(ps['phase'] or ''),ST_TD),
      p_c(iv(ps['total'])-iv(ps['done'])-iv(ps['in_prog'])),
      p_ora(ps['in_prog']), p_green(ps['done']), p_c(ps['total']),
      Paragraph(f'{calc_forecast(Q(f"SELECT current_phase,(actual_end_date IS NOT NULL) is_done,COUNT(*) cnt FROM milestones WHERE phase=%s{MS_AND} GROUP BY current_phase,(actual_end_date IS NOT NULL)",(ps["phase"],)))[0]:.1f}%',
                S("fc2",B,8,color_pct(calc_forecast(Q(f"SELECT current_phase,(actual_end_date IS NOT NULL) is_done,COUNT(*) cnt FROM milestones WHERE phase=%s{MS_AND} GROUP BY current_phase,(actual_end_date IS NOT NULL)",(ps["phase"],)))[0]),TA_CENTER))]
     for ps in phase_stats]+
    [[Paragraph('TỔNG CỘNG',S('tot',B,8,C_WHITE,TA_LEFT)),
      p_c(NOSTART), p_ora(INPROG), p_green(DONE), p_c(TOT),
      Paragraph(f'{FC_PCT_TOTAL:.1f}%',S('tot2',B,8,C_WHITE,TA_CENTER))]],
    [CW*0.3, CW*0.14, CW*0.14, CW*0.14, CW*0.14, CW*0.14],
    row_extras=[(len(phase_stats), C_NAVY)]))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1b — CƠ CẤU ĐIỂM QUY ĐỔI
# ─────────────────────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(sec_bar('Cơ cấu Điểm Quy đổi — Toàn dự án'))
story.append(SP8)

conv_data_rows = []
for item in FC_ITEMS:
    conv_data_rows.append([
        Paragraph(item['label'], ST_TD),
        p_c(item['cnt']),
        Paragraph(f"{item['rate']*100:.0f}%", ST_TC),
        Paragraph(f"{item['pts']:.2f}", ST_TC),
        Paragraph(f"{item['w_pct']:.1f}%", ST_TC),
    ])
conv_data_rows.append([
    Paragraph('TỔNG CỘNG', S('ct',B,8,C_WHITE,TA_LEFT)),
    Paragraph(str(TOT), S('ct2',B,8,C_WHITE,TA_CENTER)),
    Paragraph('—', S('ct3',B,8,C_WHITE,TA_CENTER)),
    Paragraph(f'{FC_PTS_TOTAL:.2f}', S('ct4',B,8,C_WHITE,TA_CENTER)),
    Paragraph(f'{FC_PCT_TOTAL:.2f}%', S('ct5',B,8,C_WHITE,TA_CENTER)),
])
story.append(data_table(
    [Paragraph(h,ST_TH) for h in ['Trạng thái','Số lượng','Tỷ lệ quy đổi','Điểm','Tỷ trọng']],
    conv_data_rows, [CW*0.42,CW*0.13,CW*0.15,CW*0.15,CW*0.15],
    row_extras=[(len(FC_ITEMS), C_NAVY)]))
story.append(SP8)

done_ct  = sum(item['cnt'] for item in FC_ITEMS if '100%' in item['label'] or 'Pilot — Đã' in item['label'])
inprog_ct= sum(item['cnt'] for item in FC_ITEMS if 'Đang' in item['label'])
story.append(insight_box([
    f'<b>Nhận định:</b>',
    f'• Dự báo hoàn thành toàn dự án: <b>{FC_PCT_TOTAL:.2f}%</b> ({FC_PTS_TOTAL:.1f} điểm / {TOT} milestone).',
    f'• Giai đoạn 1 đóng góp chính vào tiến độ với {iv(next((p["done"] for p in phase_stats if "1" in str(p["phase"])),0))} milestone đã hoàn thành.',
    f'• {NOSTART} milestone ({fpct(NOSTART,TOT)}) chưa bắt đầu — cần phân bổ nguồn lực trong giai đoạn tiếp theo.',
]))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — TIẾN ĐỘ GIAI ĐOẠN 1
# ─────────────────────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(hdr_bar('2','TIẾN ĐỘ GIAI ĐOẠN 1'))
story.append(SP12)

# ── GĐ1: compute stats + per-system forecast rates ────────────────────────────
gd1_total = sum(iv(r['total']) for r in gd1_by_prod_phase) if gd1_by_prod_phase else 0
gd1_done  = sum(iv(r['done'])  for r in gd1_by_prod_phase) if gd1_by_prod_phase else 0
gd1_fc, gd1_pts, _, _ = calc_forecast(
    Q(f"SELECT current_phase,(actual_end_date IS NOT NULL) is_done,COUNT(*) cnt "
      f"FROM milestones WHERE phase='Giai đoạn 1'{MS_AND} "
      f"GROUP BY current_phase,(actual_end_date IS NOT NULL)"))
gd1_coding_tot = sum(iv(r['coding_prog'])+iv(r['coding_done']) for r in gd1_by_prod_phase)
gd1_ktnb_tot   = sum(iv(r['ktnb_prog'])+iv(r['ktnb_done'])     for r in gd1_by_prod_phase)
gd1_pilot_tot  = sum(iv(r['pilot_prog'])+iv(r['pilot_done'])   for r in gd1_by_prod_phase)

gd1_prod_fc = []
for r in gd1_by_prod_phase:
    _r3 = Q("SELECT m.current_phase,(m.actual_end_date IS NOT NULL) is_done,COUNT(*) cnt "
            "FROM milestones m JOIN products p ON m.product_id=p.id "
            "WHERE m.phase='Giai đoạn 1' AND p.code=%s "
            "GROUP BY m.current_phase,(m.actual_end_date IS NOT NULL)", (r['code'],))
    _fc3,_,_,_ = calc_forecast(_r3)
    gd1_prod_fc.append({'code':r['code'],'fc':_fc3,'total':iv(r['total']),'done':iv(r['done'])})

# ── 2-column overview: GĐ1 stats (left) + per-system completion rates (right) ──
_hw = (CW - 8) / 2

# Left: GĐ1 overview box with mini KPI cards
_kpi_w = (_hw - 28) / 2
_left_data = [
    [Paragraph('TỔNG QUAN GĐ1', S('gdL0',B,11,C_NAVY,TA_LEFT,14))],
    [Spacer(1,6)],
    [Table([[
        Table([[Paragraph(str(gd1_total),S('gd1v1',B,22,C_NAVY,TA_CENTER,26)),
                Paragraph('TỔNG\nMILESTONE',S('gd1l1',R,7.5,C_GREY,TA_CENTER,10))]],
              colWidths=[_kpi_w],style=TableStyle([
                  ('LINEABOVE',(0,0),(-1,0),3,C_NAVY),('BOX',(0,0),(-1,-1),0.4,colors.HexColor('#d9d9d9')),
                  ('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                  ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
                  ('BACKGROUND',(0,0),(-1,-1),C_WHITE)])),
        Table([[Paragraph(f'{gd1_fc:.1f}%',S('gd1v2',B,22,color_pct(gd1_fc),TA_CENTER,26)),
                Paragraph('DỰ BÁO\nHOÀN THÀNH',S('gd1l2',R,7.5,C_GREY,TA_CENTER,10))]],
              colWidths=[_kpi_w],style=TableStyle([
                  ('LINEABOVE',(0,0),(-1,0),3,color_pct(gd1_fc)),('BOX',(0,0),(-1,-1),0.4,colors.HexColor('#d9d9d9')),
                  ('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                  ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
                  ('BACKGROUND',(0,0),(-1,-1),C_WHITE)])),
    ]],colWidths=[_kpi_w+4, _kpi_w+4],style=TableStyle([
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),4),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))],
    [Spacer(1,6)],
    [Paragraph(f'Coding: <b>{gd1_coding_tot}</b>  ·  KTNB: <b>{gd1_ktnb_tot}</b>  ·  Staging/Pilot: <b>{gd1_pilot_tot}</b>',
               S('gdLph',R,8,C_GREY,TA_LEFT,11))],
]
_left_tbl = Table(_left_data, colWidths=[_hw-12],
    style=TableStyle([
        ('BACKGROUND',(0,0),(0,0),C_LBLUE),
        ('BOX',(0,0),(-1,-1),0.8,C_NAVY),
        ('LINEBELOW',(0,0),(0,0),1.5,C_NAVY),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
    ]))

# Right: per-system completion rates with colored code tags
_right_data = [
    [Paragraph('TỶ LỆ HOÀN THÀNH THEO HỆ THỐNG', S('gdR0',B,11,C_NAVY,TA_LEFT,14))],
    [Spacer(1,5)],
]
for _g in gd1_prod_fc:
    _pc = colors.HexColor(PROD_COLOR.get(_g['code'],'#1677ff'))
    _right_data.append([Table([[
        Paragraph(_g['code'], S(f'gsc_{_g["code"]}',B,8.5,C_WHITE,TA_CENTER)),
        Paragraph(f'{_g["fc"]:.2f}%', S(f'gsfc_{_g["code"]}',B,13,color_pct(_g['fc']),TA_RIGHT,17)),
    ]],colWidths=[40, _hw-68],
    style=TableStyle([
        ('BACKGROUND',(0,0),(0,0),_pc),
        ('LEFTPADDING',(0,0),(0,0),4),('RIGHTPADDING',(0,0),(0,0),4),
        ('LEFTPADDING',(1,0),(1,0),8),('RIGHTPADDING',(1,0),(1,0),6),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LINEBELOW',(0,0),(-1,-1),0.3,colors.HexColor('#e0e0e0')),
    ]))])
# Total row
_tot_w = max(50, len(PROJ_CODE)*7+6)
_right_data.append([Table([[
    Paragraph(PROJ_CODE, S('gstot',B,8.5,C_WHITE,TA_CENTER)),
    Paragraph(f'{gd1_fc:.2f}%', S('gstotfc',B,13,color_pct(gd1_fc),TA_RIGHT,17)),
]],colWidths=[_tot_w, _hw-_tot_w-28],
style=TableStyle([
    ('BACKGROUND',(0,0),(0,0),C_NAVY),
    ('LEFTPADDING',(0,0),(0,0),4),('RIGHTPADDING',(0,0),(0,0),4),
    ('LEFTPADDING',(1,0),(1,0),8),
    ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
]))])
_right_tbl = Table(_right_data, colWidths=[_hw-12],
    style=TableStyle([
        ('BACKGROUND',(0,0),(0,0),C_LBLUE),
        ('BOX',(0,0),(-1,-1),0.8,C_NAVY),
        ('LINEBELOW',(0,0),(0,0),1.5,C_NAVY),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
    ]))

story.append(Table([[_left_tbl, _right_tbl]], colWidths=[_hw, _hw],
    style=TableStyle([
        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ])))
story.append(SP12)

# ── GĐ1 breakdown table: grouped by system with Đã HT / Đang TH sub-rows ──────
story.append(sec_bar('Số lượng Hiện trạng GĐ1 theo Hệ thống'))
story.append(SP4)

_grp_hdr = [Paragraph(h,ST_TH) for h in ['Hệ thống','Trạng thái','Coding','Kiểm thử nội bộ','Pilot/Staging','Tổng']]
_grp_rows = []; _grp_ext = []; _ri = 0

for r in gd1_by_prod_phase:
    code = r['code']
    _pn = PROD_LABEL.get(code, code)
    _pc2 = colors.HexColor(PROD_COLOR.get(code,'#1677ff'))
    cd = iv(r['coding_done']); cp = iv(r['coding_prog'])
    kd = iv(r['ktnb_done']);   kp = iv(r['ktnb_prog'])
    pd2 = iv(r['pilot_done']); pp = iv(r['pilot_prog'])
    t = iv(r['total'])
    # System header row (spans all columns)
    _grp_rows.append([Paragraph(_pn,S(f'grh_{code}',B,8.5,C_WHITE,TA_LEFT)),
                      Paragraph('',ST_TC),Paragraph('',ST_TC),Paragraph('',ST_TC),Paragraph('',ST_TC),Paragraph('',ST_TC)])
    _grp_ext += [('BACKGROUND',(0,_ri),(-1,_ri),_pc2),('SPAN',(0,_ri),(-1,_ri)),
                 ('TOPPADDING',(0,_ri),(-1,_ri),5),('BOTTOMPADDING',(0,_ri),(-1,_ri),5),
                 ('LEFTPADDING',(0,_ri),(0,_ri),8)]
    _ri += 1
    # Đã hoàn thành row
    _done_tot = cd + kd + pd2
    _grp_rows.append([
        Paragraph(code,S(f'gcd_{code}',B,8,C_WHITE,TA_CENTER)),
        Paragraph('Đã hoàn thành',S('gd_ht',R,8,colors.HexColor('#237804'),TA_LEFT)),
        p_c(cd) if cd else Paragraph('—',ST_TC),
        p_c(kd) if kd else Paragraph('—',ST_TC),
        p_c(pd2) if pd2 else Paragraph('—',ST_TC),
        Paragraph(str(_done_tot),S('gdtt',B,8,C_DGREY,TA_CENTER)) if _done_tot else Paragraph('—',ST_TC),
    ])
    _grp_ext += [('BACKGROUND',(0,_ri),(0,_ri),_pc2),('TEXTCOLOR',(0,_ri),(0,_ri),C_WHITE)]
    _ri += 1
    # Đang thực hiện row
    _prog_tot = cp + kp + pp
    _grp_rows.append([
        Paragraph(code,S(f'gcp_{code}',B,8,C_WHITE,TA_CENTER)),
        Paragraph('Đang thực hiện',S('gi_ht',R,8,C_ORA,TA_LEFT)),
        p_c(cp) if cp else Paragraph('—',ST_TC),
        p_c(kp) if kp else Paragraph('—',ST_TC),
        p_c(pp) if pp else Paragraph('—',ST_TC),
        Paragraph(str(_prog_tot),S('gitt',B,8,C_DGREY,TA_CENTER)) if _prog_tot else Paragraph('—',ST_TC),
    ])
    _grp_ext += [('BACKGROUND',(0,_ri),(0,_ri),_pc2),('TEXTCOLOR',(0,_ri),(0,_ri),C_WHITE)]
    _ri += 1
    # Subtotal row
    _grp_rows.append([
        Paragraph(f'Tổng {code}',S(f'gst_{code}',B,8.5,C_DGREY,TA_LEFT)),
        Paragraph('',ST_TC),
        Paragraph(str(cd+cp),S('gstc_v',B,8.5,C_DGREY,TA_CENTER)) if (cd+cp) else Paragraph('—',ST_TC),
        Paragraph(str(kd+kp),S('gstk_v',B,8.5,C_DGREY,TA_CENTER)) if (kd+kp) else Paragraph('—',ST_TC),
        Paragraph(str(pd2+pp),S('gstp_v',B,8.5,C_DGREY,TA_CENTER)) if (pd2+pp) else Paragraph('—',ST_TC),
        Paragraph(str(t),S('gsto_v',B,8.5,C_BLUE,TA_CENTER)),
    ])
    _grp_ext += [('BACKGROUND',(0,_ri),(-1,_ri),colors.HexColor('#f0f5ff')),
                 ('LINEABOVE',(0,_ri),(-1,_ri),0.5,colors.HexColor('#adc6ff')),
                 ('LINEBELOW',(0,_ri),(-1,_ri),1.0,colors.HexColor('#adc6ff')),
                 ('SPAN',(1,_ri),(1,_ri))]
    _ri += 1

# Grand total
gd1_c_tot = sum(iv(r['coding_done'])+iv(r['coding_prog']) for r in gd1_by_prod_phase)
gd1_k_tot = sum(iv(r['ktnb_done'])+iv(r['ktnb_prog'])     for r in gd1_by_prod_phase)
gd1_p_tot = sum(iv(r['pilot_done'])+iv(r['pilot_prog'])   for r in gd1_by_prod_phase)
_grp_rows.append([
    Paragraph(f'{PROJ_CODE} — TỔNG GĐ1',S('gFtot',B,9,C_WHITE,TA_LEFT)),
    Paragraph('',ST_TC),
    Paragraph(str(gd1_c_tot),S('gFc',B,9,C_WHITE,TA_CENTER)),
    Paragraph(str(gd1_k_tot),S('gFk',B,9,C_WHITE,TA_CENTER)),
    Paragraph(str(gd1_p_tot),S('gFp',B,9,C_WHITE,TA_CENTER)),
    Paragraph(str(gd1_total),S('gFt',B,9,C_WHITE,TA_CENTER)),
])
_grp_ext += [('BACKGROUND',(0,_ri),(-1,_ri),C_NAVY),('TEXTCOLOR',(0,_ri),(-1,_ri),C_WHITE)]

story.append(Table(
    [_grp_hdr] + _grp_rows,
    colWidths=[CW*0.22,CW*0.18,CW*0.13,CW*0.18,CW*0.17,CW*0.12],
    repeatRows=1, hAlign='LEFT',
    style=TableStyle([
        ('BACKGROUND',(0,0),(-1,0),C_NAVY),('TEXTCOLOR',(0,0),(-1,0),C_WHITE),
        ('FONTNAME',(0,0),(-1,-1),B),('FONTSIZE',(0,0),(-1,-1),8),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[C_WHITE,C_LGREY]),
        ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#e0e0e0')),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ] + _grp_ext)))
story.append(SP12)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2b — CHI TIẾT MILESTONE THÀNH PHẦN GĐ1
# ─────────────────────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(sec_bar('Chi tiết Milestone Thành phần — Giai đoạn 1'))
story.append(SP8)

gd1c_rows = []
rc_colors = []
for ri,r in enumerate(gd1_comps):
    t=iv(r['total']); d=iv(r['done'])
    cp=iv(r['coding_prog']); cd=iv(r['coding_done'])
    kp=iv(r['ktnb_prog']);   kd=iv(r['ktnb_done'])
    pp=iv(r['pilot_prog']);  pd2=iv(r['pilot_done'])
    fc_r = calc_forecast(Q(
        "SELECT m.current_phase,(m.actual_end_date IS NOT NULL) is_done,COUNT(*) cnt FROM milestones m JOIN products p ON m.product_id=p.id WHERE m.phase='Giai đoạn 1' AND p.code=%s AND m.component_milestone=%s GROUP BY m.current_phase,(m.actual_end_date IS NOT NULL)",
        (r['prod_code'],r['comp'])))[0]
    if fc_r==100: rc_colors.append((ri, colors.HexColor('#f6ffed')))
    elif fc_r<50: rc_colors.append((ri, colors.HexColor('#fff2e8')))
    gd1c_rows.append([
        p_c(ri+1), p_blue(r['prod_code'] or ''),
        Paragraph(str(r['comp'] or ''), ST_TD),
        p_c(cd) if cd else Paragraph('—',ST_TC),
        p_c(cp) if cp else Paragraph('—',ST_TC),
        p_c(kd) if kd else Paragraph('—',ST_TC),
        p_c(kp) if kp else Paragraph('—',ST_TC),
        p_c(pd2) if pd2 else Paragraph('—',ST_TC),
        p_c(pp) if pp else Paragraph('—',ST_TC),
        p_c(t),
        Paragraph(f'{fc_r:.1f}%',S('gfc',B,8,color_pct(fc_r),TA_CENTER)),
    ])
story.append(data_table(
    [Paragraph(h,ST_TH) for h in ['#','Hệ thống','Thành phần Milestone',
      'Cod HT','Cod ĐTH','KTNB HT','KTNB ĐTH','Pilot HT','Pilot ĐTH','Tổng','Dự báo HT']],
    gd1c_rows,
    [CW*0.055,CW*0.08,CW*0.213,CW*0.072,CW*0.072,CW*0.072,CW*0.072,CW*0.072,CW*0.072,CW*0.073,CW*0.082],
    row_extras=rc_colors))
story.append(SP8)
done_comps = sum(1 for r in gd1_comps if calc_forecast(
    Q("SELECT m.current_phase,(m.actual_end_date IS NOT NULL) is_done,COUNT(*) cnt FROM milestones m JOIN products p ON m.product_id=p.id WHERE m.phase='Giai đoạn 1' AND p.code=%s AND m.component_milestone=%s GROUP BY m.current_phase,(m.actual_end_date IS NOT NULL)",
      (r['prod_code'],r['comp'])))[0]==100)
story.append(insight_box([
    f'Hoàn thành 100%: <b>{done_comps}</b> thành phần  ·  Cần theo dõi: <b>{len(gd1_comps)-done_comps}</b> thành phần  ·  Tổng GĐ1: <b>{gd1_fc:.1f}%</b> dự báo hoàn thành'
]))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — NHÂN SỰ DỰ ÁN
# ─────────────────────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(hdr_bar('3', f'NHÂN SỰ DỰ ÁN — {REPORT_DATE}', bg=C_PURP))
story.append(SP12)

total_mm = sum(fv(r['mm']) for r in alloc_prod)
story.append(kpi_row([
    (EMP_TOT, 'TỔNG HEADCOUNT',    C_PURP, ''),
    (EMP_GTEL,f'GTEL ICT',         C_BLUE, fpct(EMP_GTEL,EMP_TOT)),
    (EMP_OUT, f'OUTSOURCING',      C_ORA,  fpct(EMP_OUT,EMP_TOT)),
    (f'{total_mm:.1f}', 'TỔNG MM', colors.HexColor('#08979c'), ''),
]))
story.append(SP12)

# Cơ cấu theo dự án
story.append(sec_bar('Cơ cấu theo Dự án'))
story.append(SP4)
alloc_rows = []
for r in alloc_prod:
    hc=iv(r['hc']); mm=fv(r['mm'])
    alloc_rows.append([
        p_blue(r['code'] or ''),
        Paragraph(str(r['name'] or ''), ST_TD),
        p_c(hc), Paragraph(f'{mm:.2f}', ST_TC),
        Paragraph(fpct(mm,total_mm), S('ap',R,8,C_GREY,TA_RIGHT)),
    ])
alloc_rows.append([
    Paragraph('TỔNG',S('ta',B,8,C_WHITE)),
    Paragraph('CỘNG',S('ta2',B,8,C_WHITE)),
    Paragraph(str(sum(iv(r['hc']) for r in alloc_prod)),S('ta3',B,8,C_WHITE,TA_CENTER)),
    Paragraph(f'{total_mm:.2f}',S('ta4',B,8,C_WHITE,TA_CENTER)),
    Paragraph('100%',S('ta5',B,8,C_WHITE,TA_RIGHT)),
])
story.append(data_table(
    [Paragraph(h,ST_TH) for h in ['Hệ thống','Tên dự án','HC','MM','Tỷ trọng']],
    alloc_rows, [CW*0.1,CW*0.45,CW*0.12,CW*0.15,CW*0.18],
    row_extras=[(len(alloc_rows)-1, C_NAVY)]))
story.append(SP12)

# Cơ cấu theo vai trò (2 cột)
half = (CW-8)/2
story.append(sec_bar('Cơ cấu theo Vai trò & Đơn vị'))
story.append(SP4)

comp_tbl = data_table(
    [Paragraph(h,ST_TH) for h in ['Đơn vị','HC','MM','Tỷ trọng']],
    [[Paragraph(str(r['company'] or ''),ST_TD),
      p_c(r['hc']),
      Paragraph(f"{fv(alloc_pivot.get(list(alloc_pivot.keys())[0] if alloc_pivot else '',{}).get(r['company'],{}).get('mm',0)):.0f}—",ST_TC),
      Paragraph(fpct(iv(r['hc']),EMP_TOT),ST_TR)]
     for r in by_company],
    [half*0.45, half*0.2, half*0.15, half*0.2])

role_tbl = data_table(
    [Paragraph(h,ST_TH) for h in ['Vai trò','HC','Tỷ trọng']],
    [[Paragraph(str(r['role'] or ''),ST_TD),
      p_c(r['hc']),
      Paragraph(fpct(iv(r['hc']),EMP_TOT),ST_TR)]
     for r in by_role],
    [half*0.5, half*0.2, half*0.3])

# Better version: just separate company by HC
comp_tbl2 = data_table(
    [Paragraph(h,ST_TH) for h in ['Đơn vị','HC','Tỷ trọng']],
    [[Paragraph(str(r['company'] or ''),ST_TD),
      p_c(r['hc']),
      Paragraph(fpct(iv(r['hc']),EMP_TOT),ST_TR)]
     for r in by_company],
    [half*0.55, half*0.2, half*0.25])

story.append(Table([[comp_tbl2, role_tbl]], colWidths=[half,half],
    style=TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),4),
                       ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
                       ('VALIGN',(0,0),(-1,-1),'TOP')])))
story.append(SP8)
_his_hc = iv(next((r["hc"] for r in alloc_prod if r["code"]=="HIS"), None) or 0)
_his_ms = next((iv(r["total"]) for r in by_prod if r["code"]=="HIS"), 0)
_tot_hc = sum(iv(r["hc"]) for r in alloc_prod)
story.append(insight_box([
    '<b>Insight nhân sự:</b>',
    f'• HIS chiếm {fpct(_his_hc, _tot_hc)} nhân sự phân bổ — phù hợp với khối lượng công việc lớn nhất ({_his_ms} milestone).',
    f'• GTEL ICT ({EMP_GTEL} HC / {fpct(EMP_GTEL,EMP_TOT)}) và Outsourcing ({EMP_OUT} HC / {fpct(EMP_OUT,EMP_TOT)}).',
]))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3b — PHÂN BỔ GTEL ICT vs OUTSOURCING
# ─────────────────────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(sec_bar('Phân bổ GTEL ICT vs Outsourcing theo Dự án'))
story.append(SP8)

gtel_mm = sum(fv(alloc_pivot.get(pr['code'],{}).get('GTEL ICT',{}).get('mm',0)) for pr in by_prod)
os_mm   = sum(fv(alloc_pivot.get(pr['code'],{}).get(comp,{}).get('mm',0))
              for pr in by_prod for comp in companies_all if comp != 'GTEL ICT')

story.append(kpi_row([
    (EMP_GTEL,f'GTEL ICT\n{fpct(EMP_GTEL,EMP_TOT)}', C_BLUE, f'{gtel_mm:.1f} MM'),
    (EMP_OUT, f'OUTSOURCING\n{fpct(EMP_OUT,EMP_TOT)}',C_ORA,  f'{os_mm:.1f} MM'),
]))
story.append(SP12)

# Table: product × company (HC)
prod_codes = [pr['code'] for pr in by_prod]
all_comps  = [c['company'] for c in by_company]
n_comps = len(all_comps)
# Determine widths
col_w_code = CW*0.1
col_w_c    = (CW - col_w_code) / max(n_comps, 1)
col_w_c    = max(col_w_c, CW*0.07)
col_w_code = CW - col_w_c * n_comps

hdr_pivot = [Paragraph('Dự án',ST_TH)] + [Paragraph(c,S('ch',B,7,C_WHITE,TA_CENTER,9)) for c in all_comps]
pivot_rows = []
for code in prod_codes:
    row = [p_blue(code)]
    for comp in all_comps:
        hc = iv(alloc_pivot.get(code,{}).get(comp,{}).get('hc',0))
        row.append(Paragraph(str(hc) if hc else '—', ST_TC))
    pivot_rows.append(row)
# Total row
total_row = [Paragraph('Tổng cộng',S('tr',B,8,C_WHITE))]
for comp in all_comps:
    total_row.append(Paragraph(str(sum(iv(alloc_pivot.get(c,{}).get(comp,{}).get('hc',0)) for c in prod_codes)),
                                S('tc2',B,8,C_WHITE,TA_CENTER)))
pivot_rows.append(total_row)

story.append(data_table(hdr_pivot, pivot_rows,
    [col_w_code] + [col_w_c]*n_comps,
    row_extras=[(len(pivot_rows)-1, C_NAVY)]))
story.append(SP12)

# Outsourcing vendors
story.append(sec_bar('Phân bổ Outsourcing theo Vendor'))
story.append(SP4)
os_rows = [[
    Paragraph(str(r['company'] or ''), ST_TD),
    p_c(r['hc']),
    Paragraph(f"{fv(r['mm']):.2f}", ST_TC),
    Paragraph(fpct(iv(r['hc']),EMP_OUT), ST_TR),
] for r in os_vendors]
os_rows.append([
    Paragraph('Tổng Outsourcing',S('to',B,8,C_WHITE)),
    Paragraph(str(EMP_OUT),S('to2',B,8,C_WHITE,TA_CENTER)),
    Paragraph(f'{os_mm:.2f}',S('to3',B,8,C_WHITE,TA_CENTER)),
    Paragraph('100%',S('to4',B,8,C_WHITE,TA_RIGHT)),
])
story.append(data_table(
    [Paragraph(h,ST_TH) for h in ['Vendor','HC','MM','Tỷ trọng']],
    os_rows, [CW*0.4,CW*0.15,CW*0.2,CW*0.25],
    row_extras=[(len(os_rows)-1, C_NAVY)]))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — BÁO CÁO TỪNG HỆ THỐNG
# ══════════════════════════════════════════════════════════════════════════════
for pr in by_prod:
    code = pr['code']
    pname = pr['name'] or code
    p_col = colors.HexColor(PROD_COLOR.get(code,'#1677ff'))
    p_label = PROD_LABEL.get(code, pname)

    t_ms = iv(pr['total']); d_ms = iv(pr['done'])
    ip_ms = iv(pr['in_prog']); ov_ms = iv(pr['overdue'])
    ns_ms = max(0, t_ms - d_ms - ip_ms)

    fc_this, pts_this, _, fc_items_this = prod_forecast[code]

    # Allocation for this product
    p_alloc = alloc_pivot.get(code, {})
    p_total_mm  = sum(fv(v.get('mm',0)) for v in p_alloc.values())
    p_gtel_hc   = iv(p_alloc.get('GTEL ICT',{}).get('hc',0))
    p_gtel_mm   = fv(p_alloc.get('GTEL ICT',{}).get('mm',0))
    p_os_hc     = sum(iv(v.get('hc',0)) for k,v in p_alloc.items() if k != 'GTEL ICT')
    p_os_mm     = sum(fv(v.get('mm',0)) for k,v in p_alloc.items() if k != 'GTEL ICT')
    p_total_hc  = p_gtel_hc + p_os_hc

    story.append(PageBreak())

    # ── Product header
    _csz = 22 if len(code) <= 3 else (15 if len(code) == 4 else 11)
    story.append(Table([[
        Paragraph(code, S(f'ph_{code}',B,_csz,C_WHITE,TA_CENTER,_csz+4)),
        Table([[Paragraph(p_label, S(f'pn_{code}',B,13,C_WHITE,TA_LEFT,17))],
               [Paragraph(f'Báo cáo riêng  ·  Ngày: {REPORT_DATE}',
                          S(f'pd_{code}',R,8.5,colors.HexColor('#d6e4ff'),TA_LEFT,12))]],
              colWidths=[CW-116],
              style=TableStyle([('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
                                 ('LEFTPADDING',(0,0),(-1,-1),0)])),
    ]], colWidths=[76, CW-76],
    style=TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),p_col),
        ('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12),
        ('LEFTPADDING',(0,0),(0,-1),10),('LEFTPADDING',(1,0),(1,-1),10),
        ('RIGHTPADDING',(0,0),(0,-1),8),('RIGHTPADDING',(1,0),(1,-1),12),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ROUNDEDCORNERS',[4]),
    ])))
    story.append(SP12)

    # ── A: Tổng quan milestone
    story.append(sec_bar(f'A · Tổng quan Milestone — {code}', p_col))
    story.append(SP8)
    story.append(kpi_row([
        (t_ms,  'TỔNG MILESTONE', p_col, ''),
        (d_ms,  'ĐÃ HOÀN THÀNH', C_GREEN, fpct(d_ms,t_ms)),
        (ip_ms, 'ĐANG THỰC HIỆN',C_ORA,  fpct(ip_ms,t_ms)),
        (ns_ms, 'CHƯA BẮT ĐẦU',  C_GREY, fpct(ns_ms,t_ms)),
        (ov_ms, 'QUÁ HẠN',       C_RED,  ''),
    ] if t_ms>0 else [
        (0,'TỔNG MILESTONE',p_col,''),
        (0,'ĐÃ HOÀN THÀNH',C_GREEN,''),
        (0,'ĐANG THỰC HIỆN',C_ORA,''),
        (0,'CHƯA BẮT ĐẦU',C_GREY,''),
        (0,'QUÁ HẠN',C_RED,''),
    ]))
    story.append(SP8)

    # Phase breakdown for this product
    p_phases = Q("""
        SELECT m.phase, COUNT(*) total,
          SUM(m.actual_end_date IS NOT NULL) done,
          SUM(m.actual_end_date IS NULL AND m.current_phase IS NOT NULL) in_prog,
          SUM(m.remind='Quá hạn') overdue
        FROM milestones m JOIN products p ON m.product_id=p.id
        WHERE p.code=%s AND m.phase IS NOT NULL
        GROUP BY m.phase ORDER BY m.phase""", (code,))

    if p_phases:
        ph_rows2 = []
        for ps2 in p_phases:
            t2=iv(ps2['total']); d2=iv(ps2['done']); ip2=iv(ps2['in_prog']); ov2=iv(ps2['overdue'])
            r5 = Q("SELECT m.current_phase,(m.actual_end_date IS NOT NULL) is_done,COUNT(*) cnt FROM milestones m JOIN products p ON m.product_id=p.id WHERE p.code=%s AND m.phase=%s GROUP BY m.current_phase,(m.actual_end_date IS NOT NULL)",(code,ps2['phase']))
            fc5,_,_,_ = calc_forecast(r5)
            ph_rows2.append([
                Paragraph(str(ps2['phase'] or ''),ST_TD),
                p_c(t2), p_green(d2), p_ora(ip2), p_c(max(0,t2-d2-ip2)), p_red(ov2),
                Paragraph(f'{fc5:.1f}%',S('phfc',B,8,color_pct(fc5),TA_CENTER)),
            ])
        story.append(data_table(
            [Paragraph(h,ST_TH) for h in ['Giai đoạn','Tổng','Đã HT','Đang TH','Chưa BĐ','Quá hạn','Dự báo HT']],
            ph_rows2,
            [CW*0.3,CW*0.1,CW*0.1,CW*0.1,CW*0.1,CW*0.1,CW*0.2]))
    story.append(SP12)

    # ── B: Điểm quy đổi cho product này
    story.append(sec_bar(f'B · Điểm Quy đổi — {code}', p_col))
    story.append(SP4)
    if fc_items_this:
        p_conv_rows = []
        for item in fc_items_this:
            p_conv_rows.append([
                Paragraph(item['label'], ST_TD),
                p_c(item['cnt']),
                Paragraph(f"{item['rate']*100:.0f}%", ST_TC),
                Paragraph(f"{item['pts']:.2f}", ST_TC),
                Paragraph(f"{item['w_pct']:.1f}%", ST_TC),
            ])
        p_conv_rows.append([
            Paragraph('TỔNG CỘNG',S('ptot',B,8,C_WHITE)),
            Paragraph(str(t_ms),S('ptot2',B,8,C_WHITE,TA_CENTER)),
            Paragraph('—',S('ptot3',B,8,C_WHITE,TA_CENTER)),
            Paragraph(f'{pts_this:.2f}',S('ptot4',B,8,C_WHITE,TA_CENTER)),
            Paragraph(f'{fc_this:.2f}%',S('ptot5',B,8,C_WHITE,TA_CENTER)),
        ])
        story.append(data_table(
            [Paragraph(h,ST_TH) for h in ['Trạng thái','Số lượng','Tỷ lệ quy đổi','Điểm','Tỷ trọng']],
            p_conv_rows,
            [CW*0.42,CW*0.13,CW*0.15,CW*0.15,CW*0.15],
            row_extras=[(len(p_conv_rows)-1, C_NAVY)]))
    story.append(SP12)

    # ── C: Milestone thành phần GĐ1 cho product này
    p_comps = [r for r in gd1_comps if r['prod_code']==code]
    if p_comps:
        story.append(sec_bar(f'C · Chi tiết Milestone Thành phần GĐ1 — {code}', p_col))
        story.append(SP4)
        pc_rows = []
        pc_colors = []
        for ri2,r in enumerate(p_comps):
            t2=iv(r['total']); d2=iv(r['done'])
            cp=iv(r['coding_prog']); cd=iv(r['coding_done'])
            kp=iv(r['ktnb_prog']);   kd=iv(r['ktnb_done'])
            pp=iv(r['pilot_prog']);  pd3=iv(r['pilot_done'])
            fc_c = calc_forecast(Q(
                "SELECT m.current_phase,(m.actual_end_date IS NOT NULL) is_done,COUNT(*) cnt FROM milestones m JOIN products p ON m.product_id=p.id WHERE p.code=%s AND m.component_milestone=%s AND m.phase='Giai đoạn 1' GROUP BY m.current_phase,(m.actual_end_date IS NOT NULL)",
                (code,r['comp'])))[0]
            if fc_c==100: pc_colors.append((ri2, colors.HexColor('#f6ffed')))
            elif fc_c<50: pc_colors.append((ri2, colors.HexColor('#fff2e8')))
            pc_rows.append([
                p_c(ri2+1),
                Paragraph(str(r['comp'] or ''), ST_TD),
                p_c(cd) if cd else Paragraph('—',ST_TC),
                p_c(cp) if cp else Paragraph('—',ST_TC),
                p_c(kd) if kd else Paragraph('—',ST_TC),
                p_c(kp) if kp else Paragraph('—',ST_TC),
                p_c(pd3) if pd3 else Paragraph('—',ST_TC),
                p_c(pp) if pp else Paragraph('—',ST_TC),
                p_c(t2),
                Paragraph(f'{fc_c:.1f}%',S('pcf',B,8,color_pct(fc_c),TA_CENTER)),
            ])
        story.append(data_table(
            [Paragraph(h,ST_TH) for h in ['#','Thành phần Milestone',
              'Cod HT','Cod ĐTH','KTNB HT','KTNB ĐTH','Pilot HT','Pilot ĐTH','Tổng','Dự báo HT']],
            pc_rows,
            [CW*0.06,CW*0.28,CW*0.07,CW*0.07,CW*0.08,CW*0.08,CW*0.08,CW*0.08,CW*0.07,CW*0.13],
            row_extras=pc_colors))
        story.append(SP12)

    # ── D: Nhân sự & Phân bổ cho product này
    story.append(sec_bar(f'D · Nhân sự & Phân bổ Nguồn lực — {code}', p_col))
    story.append(SP8)

    if p_total_hc > 0:
        story.append(kpi_row([
            (p_total_hc, 'TỔNG HEADCOUNT', p_col, ''),
            (p_gtel_hc,  f'GTEL ICT',       C_BLUE, f'{p_gtel_mm:.1f} MM'),
            (p_os_hc,    'OUTSOURCING',     C_ORA,  f'{p_os_mm:.1f} MM'),
            (f'{p_total_mm:.1f}', 'TỔNG MM', colors.HexColor('#08979c'), ''),
        ]))
        story.append(SP8)

        # By company table for this product
        p_comp_rows = []
        for comp, vals in sorted(p_alloc.items(), key=lambda x: -fv(x[1].get('mm',0))):
            hc_v = iv(vals.get('hc',0)); mm_v = fv(vals.get('mm',0))
            p_comp_rows.append([
                Paragraph(comp, ST_TD),
                p_c(hc_v),
                Paragraph(f'{mm_v:.2f}', ST_TC),
                Paragraph(fpct(mm_v, p_total_mm), ST_TR),
                Paragraph('GTEL ICT' if comp=='GTEL ICT' else 'Outsourcing',
                          S('ct',R,7.5,C_BLUE if comp=='GTEL ICT' else C_ORA,TA_CENTER,9)),
            ])
        p_comp_rows.append([
            Paragraph('Tổng', S('ttl',B,8,C_WHITE)),
            Paragraph(str(p_total_hc), S('ttl2',B,8,C_WHITE,TA_CENTER)),
            Paragraph(f'{p_total_mm:.2f}', S('ttl3',B,8,C_WHITE,TA_CENTER)),
            Paragraph('100%', S('ttl4',B,8,C_WHITE,TA_RIGHT)),
            Paragraph('', ST_TC),
        ])
        story.append(data_table(
            [Paragraph(h,ST_TH) for h in ['Đơn vị','HC','MM','Tỷ trọng MM','Phân loại']],
            p_comp_rows,
            [CW*0.30,CW*0.12,CW*0.15,CW*0.2,CW*0.23],
            row_extras=[(len(p_comp_rows)-1, C_NAVY)]))
    else:
        story.append(insight_box([f'Chưa có dữ liệu phân bổ nhân sự cho {code}.'], bg=C_LGREY, border=C_GREY))
    story.append(SP4)

# ─────────────────────────────────────────────────────────────────────────────
# TRANG CẢM ƠN
# ─────────────────────────────────────────────────────────────────────────────
story.append(PageBreak())
story.append(Spacer(1, 60))
story.append(Table(
    [[Paragraph('XIN CẢM ƠN', S('ty1',B,28,C_NAVY,TA_CENTER,34))],
     [Paragraph('Trân trọng cảm ơn Quý Anh/Chị đã theo dõi báo cáo.',
                S('ty2',R,11,C_GREY,TA_CENTER,15))],
     [Spacer(1,18)],
     [Paragraph(f'{PROJ_CODE}{" — " + PROJ_NAME[:55] if PROJ_CODE != "ALL" else " — Tổng hợp tất cả dự án"}',
                S('ty3',B,10,C_NAVY,TA_CENTER))],
     [Paragraph(f'Báo cáo ngày {REPORT_DATE}',
                S('ty4',R,9,C_GREY,TA_CENTER))],
    ], colWidths=[CW],
    style=TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                       ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)])))

# ── BUILD ──────────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(os.path.abspath(OUT_PATH)), exist_ok=True)

def footer(canvas, doc):
    if doc.page == 1: return
    canvas.saveState()
    canvas.setFont(R, 7.5)
    canvas.setFillColor(C_GREY)
    canvas.drawString(MARGIN, 1.2*cm, f'{PROJ_CODE} — Báo cáo tiến độ dự án · {REPORT_DATE}')
    canvas.drawRightString(PAGE_W-MARGIN, 1.2*cm, f'Trang {doc.page}')
    canvas.line(MARGIN, 1.5*cm, PAGE_W-MARGIN, 1.5*cm)
    canvas.restoreState()

doc = SimpleDocTemplate(OUT_PATH, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=MARGIN,
    title=f'Báo cáo tiến độ {PROJ_CODE} — {REPORT_DATE}',
    author=f'{PROJ_CODE} Project Management')

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f'PDF generated: {OUT_PATH}')
print(f'Milestones={TOT} | Forecast={FC_PCT_TOTAL:.2f}% | Employees={EMP_TOT} | Products={len(by_prod)}')
