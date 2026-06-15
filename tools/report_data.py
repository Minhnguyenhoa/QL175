"""
report_data.py — Lớp dữ liệu dùng chung cho các trình sinh báo cáo (PDF / Slide).
Tách từ generate_report_pdf.py để 1 nguồn dữ liệu duy nhất.
Import: from report_data import *
"""
import sys, argparse
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
from datetime import date as dt_date
import mysql.connector

# ── ARGS (parse_known_args để không xung đột với args riêng của script gọi) ──────
_p = argparse.ArgumentParser(add_help=False)
_p.add_argument('--date',    default=dt_date.today().strftime('%d/%m/%Y'))
_p.add_argument('--host',    default='localhost')
_p.add_argument('--port',    default=3306, type=int)
_p.add_argument('--db',      default='project_mgmt')
_p.add_argument('--user',    default='root')
_p.add_argument('--pwd',     default='123456')
_p.add_argument('--project', default=None)
args, _ = _p.parse_known_args()

REPORT_DATE = args.date

# ── PROJECT LOOKUP ──────────────────────────────────────────────────────────────
_cnx = mysql.connector.connect(host=args.host, port=args.port, database=args.db,
                               user=args.user, password=args.pwd, charset='utf8mb4')
_cur = _cnx.cursor(dictionary=True)
_cur.execute("SELECT id, code, name FROM project_groups ORDER BY id")
_all_pgs = _cur.fetchall()
_req = (args.project or '').strip().upper()

if not _req or _req == 'ALL':
    PROJ_IDS  = []
    PROJ_CODE = 'ALL'
    PROJ_NAME = 'Tất cả dự án'
    PROJ_LIST = [pg['code'] for pg in _all_pgs]
else:
    codes_req = [c.strip() for c in _req.split(',') if c.strip()]
    matched = [pg for pg in _all_pgs if pg['code'].upper() in codes_req]
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
        PROJ_IDS  = []
        PROJ_CODE = 'ALL'
        PROJ_NAME = 'Tất cả dự án'
        PROJ_LIST = [pg['code'] for pg in _all_pgs]
_cur.close(); _cnx.close()

# ── SQL FILTER HELPERS ──────────────────────────────────────────────────────────
if PROJ_IDS:
    _ids = ','.join(str(i) for i in PROJ_IDS)
    MS_WHERE  = f" WHERE product_id IN (SELECT id FROM products WHERE project_group_id IN ({_ids}))"
    MS_AND    = f" AND product_id IN (SELECT id FROM products WHERE project_group_id IN ({_ids}))"
    PROD_WHER = f" WHERE p.project_group_id IN ({_ids})"
    PROD_AND  = f" AND p.project_group_id IN ({_ids})"
    EMP_WHERE = (f" WHERE id IN (SELECT DISTINCT employee_id FROM resource_allocations ra"
                 f" JOIN products p ON ra.product_id=p.id WHERE p.project_group_id IN ({_ids}))")
    EMP_AND   = (f" AND id IN (SELECT DISTINCT employee_id FROM resource_allocations ra"
                 f" JOIN products p ON ra.product_id=p.id WHERE p.project_group_id IN ({_ids}))")
    EMP_E_AND = (f" AND e.id IN (SELECT DISTINCT employee_id FROM resource_allocations ra"
                 f" JOIN products p ON ra.product_id=p.id WHERE p.project_group_id IN ({_ids}))")
    RA_WHER   = f" WHERE p.project_group_id IN ({_ids})"
    OS_AND    = f" AND ra.product_id IN (SELECT id FROM products WHERE project_group_id IN ({_ids}))"
else:
    MS_WHERE = MS_AND = PROD_WHER = PROD_AND = ""
    EMP_WHERE = EMP_AND = EMP_E_AND = RA_WHER = OS_AND = ""

# ── DB HELPERS ──────────────────────────────────────────────────────────────────
def get_conn():
    return mysql.connector.connect(host=args.host, port=args.port, database=args.db,
                                   user=args.user, password=args.pwd, charset='utf8mb4')
def Q(sql, params=None):
    c = get_conn(); cur = c.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    cur.close(); c.close(); return rows
def Q1(sql, params=None):
    r = Q(sql, params); return r[0] if r else {}
def iv(x, d=0):
    try: return int(x or d)
    except: return d
def fv(x, d=0.0):
    try: return float(x or d)
    except: return d
def pct(a, b):
    return round(a/b*100, 2) if b else 0
def fpct(a, b):
    return f'{pct(a,b):.1f}%'

# ── CONVERSION RATES ────────────────────────────────────────────────────────────
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
    total = sum(iv(r['cnt']) for r in rows)
    breakdown = {}
    for r in rows:
        cp  = r.get('current_phase'); dn = 1 if iv(r.get('is_done')) else 0
        cnt = iv(r['cnt']); key = (cp, dn)
        rate, label = CONV.get(key, (0.00, f'{cp} — {"Đã HT" if dn else "Đang TH"}'))
        if label not in breakdown: breakdown[label] = {'cnt': 0, 'rate': rate}
        breakdown[label]['cnt'] += cnt
    items = []; total_pts = 0.0
    for label, v in sorted(breakdown.items(), key=lambda x: -x[1]['rate']):
        pts = v['cnt'] * v['rate']; total_pts += pts
        items.append({'label': label, 'cnt': v['cnt'], 'rate': v['rate'],
                      'pts': pts, 'w_pct': pct(v['cnt'], total)})
    return pct(total_pts, total), total_pts, total, items

# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
# Overall
ov = Q1(f"""SELECT COUNT(*) total, SUM(actual_end_date IS NOT NULL) done,
      SUM(actual_end_date IS NULL AND current_phase IS NOT NULL) in_prog,
      SUM(remind='Quá hạn') overdue FROM milestones{MS_WHERE}""")
TOT   = iv(ov['total']); DONE = iv(ov['done']); INPROG = iv(ov['in_prog'])
OVERD = iv(ov['overdue']); NOSTART = max(0, TOT - DONE - INPROG)

# Phase breakdown
phase_stats = Q(f"""SELECT phase, COUNT(*) total, SUM(actual_end_date IS NOT NULL) done,
      SUM(actual_end_date IS NULL AND current_phase IS NOT NULL) in_prog,
      SUM(remind='Quá hạn') overdue FROM milestones WHERE phase IS NOT NULL{MS_AND}
      GROUP BY phase ORDER BY phase""")

# Conversion-point breakdown
conv_rows = Q(f"""SELECT current_phase, (actual_end_date IS NOT NULL) is_done, COUNT(*) cnt
      FROM milestones{MS_WHERE} GROUP BY current_phase, (actual_end_date IS NOT NULL)
      ORDER BY current_phase, is_done DESC""")
FC_PCT_TOTAL, FC_PTS_TOTAL, _, FC_ITEMS = calc_forecast(conv_rows)

# By product
by_prod = Q(f"""SELECT p.code, p.name, p.status, p.current_phase AS cur_phase,
      COUNT(m.id) total, SUM(m.actual_end_date IS NOT NULL) done,
      SUM(m.actual_end_date IS NULL AND m.current_phase IS NOT NULL) in_prog,
      SUM(m.remind='Quá hạn') overdue
      FROM products p LEFT JOIN milestones m ON m.product_id=p.id{PROD_WHER}
      GROUP BY p.id,p.code,p.name,p.status,p.current_phase ORDER BY p.code""")

# GĐ1 detail by product+status
gd1_by_prod_phase = Q(f"""SELECT p.code,
      SUM(m.current_phase='Coding' AND m.actual_end_date IS NULL)    coding_prog,
      SUM(m.current_phase='Coding' AND m.actual_end_date IS NOT NULL) coding_done,
      SUM(m.current_phase='Kiểm thử nội bộ' AND m.actual_end_date IS NULL)    ktnb_prog,
      SUM(m.current_phase='Kiểm thử nội bộ' AND m.actual_end_date IS NOT NULL) ktnb_done,
      SUM(m.current_phase='Pilot' AND m.actual_end_date IS NULL)    pilot_prog,
      SUM(m.current_phase='Pilot' AND m.actual_end_date IS NOT NULL) pilot_done,
      COUNT(m.id) total, SUM(m.actual_end_date IS NOT NULL) done
      FROM products p LEFT JOIN milestones m ON m.product_id=p.id
      WHERE m.phase='Giai đoạn 1'{PROD_AND} GROUP BY p.code ORDER BY p.code""")

# Milestone components GĐ1
gd1_comps = Q(f"""SELECT p.code prod_code, m.component_milestone comp, COUNT(*) total,
      SUM(m.actual_end_date IS NOT NULL) done,
      SUM(m.current_phase='Coding' AND m.actual_end_date IS NULL) coding_prog,
      SUM(m.current_phase='Coding' AND m.actual_end_date IS NOT NULL) coding_done,
      SUM(m.current_phase='Kiểm thử nội bộ' AND m.actual_end_date IS NULL) ktnb_prog,
      SUM(m.current_phase='Kiểm thử nội bộ' AND m.actual_end_date IS NOT NULL) ktnb_done,
      SUM(m.current_phase='Pilot' AND m.actual_end_date IS NULL) pilot_prog,
      SUM(m.current_phase='Pilot' AND m.actual_end_date IS NOT NULL) pilot_done
      FROM milestones m JOIN products p ON m.product_id=p.id
      WHERE m.phase='Giai đoạn 1' AND m.component_milestone IS NOT NULL{PROD_AND}
      GROUP BY p.code, m.component_milestone ORDER BY p.code, m.component_milestone""")

# Employees
emp_ov = Q1(f"SELECT COUNT(*) total, SUM(company='GTEL ICT') gtel FROM employees{EMP_WHERE}")
EMP_TOT = iv(emp_ov['total']); EMP_GTEL = iv(emp_ov['gtel']); EMP_OUT = EMP_TOT - EMP_GTEL

by_company = Q(f"""SELECT company, COUNT(*) hc FROM employees
      WHERE company IS NOT NULL{EMP_AND} GROUP BY company ORDER BY hc DESC""")
by_role = Q(f"""SELECT role, COUNT(*) hc FROM employees
      WHERE role IS NOT NULL{EMP_AND} GROUP BY role ORDER BY hc DESC LIMIT 12""")

# Allocation by product
alloc_prod = Q(f"""SELECT p.code, p.name, COUNT(DISTINCT ra.employee_id) hc,
      ROUND(SUM(ra.allocation_percent),2) mm
      FROM resource_allocations ra JOIN products p ON ra.product_id=p.id{RA_WHER}
      GROUP BY p.id,p.code,p.name ORDER BY mm DESC""")

# GTEL vs OS per product
alloc_detail = Q(f"""SELECT p.code, e.company, COUNT(DISTINCT e.id) hc,
      ROUND(SUM(ra.allocation_percent),2) mm
      FROM resource_allocations ra JOIN products p ON ra.product_id=p.id
      JOIN employees e ON e.id=ra.employee_id{RA_WHER}
      GROUP BY p.code,e.company ORDER BY p.code,e.company""")
companies_all = sorted(set(r['company'] for r in by_company))
alloc_pivot = {}
for r in alloc_detail:
    alloc_pivot.setdefault(r['code'], {})[r['company']] = {'hc': iv(r['hc']), 'mm': fv(r['mm'])}

os_vendors = Q(f"""SELECT e.company, COUNT(DISTINCT e.id) hc, ROUND(SUM(ra.allocation_percent),2) mm
      FROM resource_allocations ra JOIN employees e ON e.id=ra.employee_id
      WHERE e.company != 'GTEL ICT'{OS_AND} GROUP BY e.company ORDER BY mm DESC""")

# Per-product forecast
prod_forecast = {}
for pr in by_prod:
    r2 = Q("""SELECT m.current_phase, (m.actual_end_date IS NOT NULL) is_done, COUNT(*) cnt
        FROM milestones m JOIN products p ON m.product_id=p.id WHERE p.code=%s
        GROUP BY m.current_phase,(m.actual_end_date IS NOT NULL)""", (pr['code'],))
    prod_forecast[pr['code']] = calc_forecast(r2)

# Personnel list grouped by role (for detailed slide)
emp_list = Q(f"""SELECT e.name, e.role, e.company,
      ROUND(COALESCE(SUM(ra.allocation_percent),0),2) mm
      FROM employees e LEFT JOIN resource_allocations ra ON ra.employee_id=e.id
      WHERE e.name IS NOT NULL{EMP_E_AND}
      GROUP BY e.id,e.name,e.role,e.company ORDER BY e.role, mm DESC""")

if __name__ == '__main__':
    print(f'Project: {PROJ_CODE} | Milestones: {TOT} done {DONE} fc {FC_PCT_TOTAL:.1f}% | Emp {EMP_TOT}')
