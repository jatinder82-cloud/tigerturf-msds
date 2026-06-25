import streamlit as st
import base64
import os
from datetime import date

MSDS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MSDS")

st.set_page_config(page_title="TigerTurf MSDS Library", page_icon="🧪", layout="wide")

st.markdown("""
<style>
    html, body, [class*="css"] { font-family: "Segoe UI", Arial, sans-serif; }
    .stApp { background-color: #0a0a0a; color: #f0f0f0; }
    .stTextInput input { background: #1a1a1a !important; border: 2px solid #333 !important; border-radius: 10px !important; color: white !important; font-size: 16px !important; }
    .stTextInput input:focus { border-color: #e85d04 !important; }
    div[data-testid="stSelectbox"] > div { background: #1a1a1a !important; border: 2px solid #333 !important; border-radius: 10px !important; color: white !important; }
    .cat-badge { display:inline-block; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:600; text-transform:uppercase; }
    .cat-adhesives { background:#e85d04; color:white; }
    .cat-cleaners { background:#0077b6; color:white; }
    .cat-protectors { background:#2d6a4f; color:white; }
    .cat-technical { background:#6d28d9; color:white; }
    .cat-hardeners { background:#92400e; color:white; }
    .cat-other { background:#374151; color:white; }
    .sds-overdue { display:inline-block; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:700; background:#7f1d1d; color:#fca5a5; text-transform:uppercase; margin-left:8px; }
    .sds-due-soon { display:inline-block; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:700; background:#78350f; color:#fcd34d; text-transform:uppercase; margin-left:8px; }
    .sds-current { display:inline-block; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:600; background:#14532d; color:#86efac; text-transform:uppercase; margin-left:8px; }
    .sds-unknown { display:inline-block; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:600; background:#374151; color:#9ca3af; text-transform:uppercase; margin-left:8px; }
    .alert-box-red { background:#1c0a0a; border:1px solid #7f1d1d; border-left:4px solid #dc2626; border-radius:8px; padding:14px 18px; margin-bottom:10px; }
    .alert-box-amber { background:#1c1000; border:1px solid #78350f; border-left:4px solid #d97706; border-radius:8px; padding:14px 18px; margin-bottom:10px; }
    .supplier-tag { font-size:14px; color:#aaa; margin-top:8px; }
    .supplier-tag a { color:#e85d04; text-decoration:none; font-weight:500; }
    .supplier-tag a:hover { text-decoration:underline; }
    hr { border-color:#222; }
    .stDownloadButton button { background:#e85d04 !important; color:white !important; border:none !important; border-radius:8px !important; font-weight:600 !important; font-size:14px !important; }
    .stDownloadButton button:hover { background:#c94e00 !important; }
    [data-testid="stMetricValue"] { color:#e85d04; font-weight:700; }
    [data-testid="stMetricLabel"] p { color:#aaa !important; }
    [data-testid="stMetric"] { background:#1a1a1a; border:1px solid #2a2a2a; border-radius:10px; padding:12px; }
    details { background:#1a1a1a !important; border:1px solid #2a2a2a !important; border-radius:12px !important; margin-bottom:8px !important; }
    details:hover { border-color:#e85d04 !important; }
    summary { color:#ffffff !important; font-weight:600 !important; font-size:15px !important; }
</style>
""", unsafe_allow_html=True)

# ── SDS DATES ─────────────────────────────────────────────────────────────────
# Key = exact PDF filename (case sensitive, must match file in MSDS folder)
# Value = issue/revision date of that SDS
# To update: change the date when you receive a new SDS from supplier

SDS_DATES = {
    "ADH CRC (NZ) 8002, 8016 F2 Contact Adhesive (ADOS F2)-MSDS.pdf":   date(2023, 3, 10),
    "GG Heavy Duty Cleaner MSDS 2024.pdf":                                date(2024, 1, 1),
    "GG High Stregth Protector MSDS 2025.pdf":                            date(2025, 1, 1),
    "GG Matrix MSDS.pdf":                                                 date(2026, 5, 18),
    "Greengauge MATRIX - B Protector Instructions 2025.pdf":              date(2025, 1, 1),
    "HM 1016 5.12.25 10 16 0R 8 16 TECHNICAL SHEET.pdf":                 date(2025, 12, 5),
    "HM40 5.12.25 ROC 40 TECHNICAL SHEET.pdf":                           date(2025, 12, 5),
    "LDH78_MSDS_英繁中_2024.pdf":                                          date(2024, 2, 7),
    "MSDS - Fullatak Thinner.pdf":                                        date(2022, 8, 1),
    "MSDS - Premiumbond Green.pdf":                                       date(2022, 3, 2),
    "PREMIUMBOND_GREEN.pdf":                                              date(2022, 3, 2),    # same version 1.1 — supplier re-sent same document
    "MSDS - Premiumbond extrud.pdf":                                      date(2022, 12, 14),
    "MSDS Freudenberg - Freudenberg Tape.pdf":                            date(2025, 1, 5),   # non-hazardous, AU format not mandatory — treated as current
    "MSDS Tyrecycle -Crumb Rubber.pdf":                                   date(2023, 12, 15),  # supplier confirmed unchanged
    "MSDS Wetgel - TURF-WELD CA556 ADHESIVE-SDS.pdf":                    date(2026, 4, 20),   # updated v2.0 Apr 2026 (Bondtech CA556)
    "BONDTECH_CA556_ADHESIVE_SDS.pdf":                                    date(2026, 4, 20),   # same product, alternate filename
    "MSDS_PEARLBOND RB-10.pdf":                                           date(2026, 2, 2),
    "Material-Safety-Ultrafix-Flexibond-Adhesive-v7-1.pdf":               date(2022, 9, 15),
    "Material-safety-Hardener-v10.pdf":                                   date(2023, 7, 31),
    "PEARLBOND BR-10_SDS_GHS.pdf":                                        date(2025, 1, 2),
    "SDS - Sodium Silicate Solution MR 2.6-3.2 - EN (1).pdf":            date(2023, 8, 28),
    "SDS - TigerBond.pdf":                                                date(2025, 4, 15),  # supplier confirmed unchanged — treated as current
    "SDS Ultrabond Turf PU 1K.pdf":                                       date(2026, 5, 22),   # updated v6 May 2026
    "ULTRABOND_TURF_PU_1_K.pdf":                                          date(2026, 5, 22),   # same product, new filename
    "SDS-BP308280-en-NZ.pdf":                                             date(2023, 9, 12),
    "Slasher - Organic Weed Killer.pdf":                                  date(2024, 6, 4),    # supplier confirmed unchanged
    "TigerBondDBE - PC Blend HAZ SDS CW 23-3870.pdf":                    date(2023, 3, 10),
    "Ultrabond Turf 2 Stars Pro Pt A.pdf":                                date(2023, 6, 21),
    "Ultrabond Turf 2 Stars Pro Pt B.pdf":                                date(2024, 10, 16),
}

# ── SUPPLIER DETAILS ──────────────────────────────────────────────────────────
# Key = exact PDF filename
# Value = (Contact Name, Email)

SUPPLIER_INFO = {
    "ADH CRC (NZ) 8002, 8016 F2 Contact Adhesive (ADOS F2)-MSDS.pdf":   ("DespatchNZ",              "despatchnz@tigerturf.com"),
    "GG Heavy Duty Cleaner MSDS 2024.pdf":                                ("Peter Bainbridge",        "peter@sportcrete.com.au"),
    "GG High Stregth Protector MSDS 2025.pdf":                            ("Peter Bainbridge",        "peter@sportcrete.com.au"),
    "GG Matrix MSDS.pdf":                                                 ("Peter Bainbridge",        "peter@sportcrete.com.au"),
    "Greengauge MATRIX - B Protector Instructions 2025.pdf":              ("Peter Bainbridge",        "peter@sportcrete.com.au"),
    "MSDS - Fullatak Thinner.pdf":                                        ("Customer Service",        "Customer.Service@hbfuller.com"),
    "MSDS - Premiumbond Green.pdf":                                       ("Customer Service",        "Customer.Service@hbfuller.com"),
    "PREMIUMBOND_GREEN.pdf":                                              ("Customer Service",        "Customer.Service@hbfuller.com"),
    "MSDS - Premiumbond extrud.pdf":                                      ("Customer Service",        "Customer.Service@hbfuller.com"),
    "Material-Safety-Ultrafix-Flexibond-Adhesive-v7-1.pdf":               ("Julie Dean",              "julied@envirostik.com"),
    "Material-safety-Hardener-v10.pdf":                                   ("Julie Dean",              "julied@envirostik.com"),
    "MSDS Freudenberg - Freudenberg Tape.pdf":                            ("DespatchNZ",              "despatchnz@tigerturf.com"),
    "LDH78_MSDS_英繁中_2024.pdf":                                          ("DespatchNZ",              "despatchnz@tigerturf.com"),
    "MSDS Tyrecycle -Crumb Rubber.pdf":                                   ("",                        ""),
    "MSDS Wetgel - TURF-WELD CA556 ADHESIVE-SDS.pdf":                    ("Murray",                  "murray@chemtech.com.au"),
    "BONDTECH_CA556_ADHESIVE_SDS.pdf":                                    ("Murray",                  "murray@chemtech.com.au"),
    "MSDS_PEARLBOND RB-10.pdf":                                           ("",                        ""),
    "PEARLBOND BR-10_SDS_GHS.pdf":                                        ("",                        ""),
    "SDS - Sodium Silicate Solution MR 2.6-3.2 - EN (1).pdf":            ("Janet Dalziel",           "janet.dalziel@pottersindustries.com"),
    "SDS - TigerBond.pdf":                                                ("Manny Samano",            "msamano@bisley.biz"),
    "TigerBondDBE - PC Blend HAZ SDS CW 23-3870.pdf":                    ("Manny Samano",            "msamano@bisley.biz"),
    "SDS Ultrabond Turf PU 1K.pdf":                                       ("Mapei Australia",         "sales@mapei.com.au"),
    "ULTRABOND_TURF_PU_1_K.pdf":                                          ("Mapei Australia",         "sales@mapei.com.au"),
    "Ultrabond Turf 2 Stars Pro Pt A.pdf":                                ("Mapei Australia",         "sales@mapei.com.au"),
    "Ultrabond Turf 2 Stars Pro Pt B.pdf":                                ("Mapei Australia",         "sales@mapei.com.au"),
    "SDS-BP308280-en-NZ.pdf":                                             ("DespatchNZ",              "despatchnz@tigerturf.com"),
    "Slasher - Organic Weed Killer.pdf":                                  ("",                        ""),
    "HM 1016 5.12.25 10 16 0R 8 16 TECHNICAL SHEET.pdf":                 ("DespatchNZ",              "despatchnz@tigerturf.com"),
    "HM40 5.12.25 ROC 40 TECHNICAL SHEET.pdf":                           ("DespatchNZ",              "despatchnz@tigerturf.com"),
}

TODAY = date.today()

def get_sds_status(filename):
    sds_date = SDS_DATES.get(filename)
    if not sds_date:
        return "Unknown", None, "—", "sds-unknown"
    age_years = (TODAY - sds_date).days / 365.25
    issue_str = sds_date.strftime("%d %b %Y")
    if age_years >= 5:
        return "Overdue", round(age_years, 1), issue_str, "sds-overdue"
    elif age_years >= 4:
        return "Due Soon", round(age_years, 1), issue_str, "sds-due-soon"
    else:
        return "Current", round(age_years, 1), issue_str, "sds-current"

def get_supplier(filename):
    return SUPPLIER_INFO.get(filename, ("", ""))

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('''
<div style="display:flex;align-items:center;gap:20px;padding:10px 0 24px 0;">
  <div>
    <div style="font-size:22px;font-weight:800;color:#ffffff;">🧪 MSDS Library</div>
    <div style="font-size:12px;color:#e85d04;font-weight:600;letter-spacing:2px;text-transform:uppercase;">Material Safety Data Sheets — TigerTurf Australia</div>
  </div>
</div><hr>
''', unsafe_allow_html=True)

# ── LOAD PDFs ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_pdfs():
    if not os.path.exists(MSDS_FOLDER):
        return {}
    pdfs = {}
    for f in sorted(os.listdir(MSDS_FOLDER)):
        if f.lower().endswith(".pdf"):
            with open(os.path.join(MSDS_FOLDER, f), "rb") as fp:
                pdfs[f] = base64.b64encode(fp.read()).decode()
    return pdfs

PDF_DATA = load_pdfs()

if not PDF_DATA:
    st.error("MSDS folder not found or no PDFs available.")
    st.stop()

# ── CATEGORIES ────────────────────────────────────────────────────────────────
CATEGORIES = {
    "Adhesives & Bonds": "cat-adhesives",
    "Cleaners":          "cat-cleaners",
    "Protectors & Coatings": "cat-protectors",
    "Technical Sheets":  "cat-technical",
    "Hardeners & Solutions": "cat-hardeners",
    "Other":             "cat-other"
}

def get_category(name):
    n = name.lower()
    if any(k in n for k in ["bond", "adhesive", "ultrafix", "flexibond", "ultrabond", "premiumbond", "pearlbond", "tigerbond", "envirostik", "freudenberg"]):
        return "Adhesives & Bonds"
    if any(k in n for k in ["cleaner", "slasher", "weed", "crumb", "rubber", "tyrecycle"]):
        return "Cleaners"
    if any(k in n for k in ["protector", "matrix", "turfguard"]):
        return "Protectors & Coatings"
    if any(k in n for k in ["technical", "sheet", "hm "]):
        return "Technical Sheets"
    if any(k in n for k in ["hardener", "sodium", "silicate"]):
        return "Hardeners & Solutions"
    return "Other"

def clean_name(filename):
    name = filename.replace(".pdf", "").replace(".PDF", "")
    for r in ["MSDS - ", "MSDS_", "MSDS ", "-MSDS", "SDS - ", "SDS ", " 2024", " 2025"]:
        name = name.replace(r, "")
    return name.strip()

# ── ALERT BANNER ──────────────────────────────────────────────────────────────
all_files = sorted(PDF_DATA.keys())
overdue_list = []
due_soon_list = []

for f in all_files:
    status, age, issue_str, _ = get_sds_status(f)
    if status == "Overdue":
        overdue_list.append((clean_name(f), age, issue_str))
    elif status == "Due Soon":
        due_soon_list.append((clean_name(f), age, issue_str))

if overdue_list or due_soon_list:
    st.markdown("### ⚠️ SDS Status Alerts")

if overdue_list:
    items_html = "".join(
        f'<div style="margin:4px 0;color:#fca5a5;">• <b>{name}</b>&nbsp;<span style="color:#888;font-size:12px;">issued {issue_str} ({age} yrs ago)</span></div>'
        for name, age, issue_str in overdue_list
    )
    st.markdown(
        f'<div class="alert-box-red">'
        f'<div style="color:#f87171;font-weight:700;font-size:14px;margin-bottom:8px;">🔴 &nbsp;Overdue — SDS renewal required ({len(overdue_list)} product{"s" if len(overdue_list)>1 else ""})</div>'
        f'{items_html}</div>',
        unsafe_allow_html=True
    )

if due_soon_list:
    items_html = "".join(
        f'<div style="margin:4px 0;color:#fcd34d;">• <b>{name}</b>&nbsp;<span style="color:#888;font-size:12px;">issued {issue_str} ({age} yrs ago)</span></div>'
        for name, age, issue_str in due_soon_list
    )
    st.markdown(
        f'<div class="alert-box-amber">'
        f'<div style="color:#fbbf24;font-weight:700;font-size:14px;margin-bottom:8px;">🟡 &nbsp;Due for review within 12 months ({len(due_soon_list)} product{"s" if len(due_soon_list)>1 else ""})</div>'
        f'{items_html}</div>',
        unsafe_allow_html=True
    )

if overdue_list or due_soon_list:
    st.markdown("---")

# ── SEARCH & FILTER ───────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    search = st.text_input("Search", placeholder="🔍  Search by product name...", label_visibility="collapsed")
with col2:
    cat_filter = st.selectbox("Category", ["All Categories"] + list(CATEGORIES.keys()))
with col3:
    status_filter = st.selectbox("SDS Status", ["All", "Overdue", "Due Soon", "Current", "Unknown"])

# ── METRICS ───────────────────────────────────────────────────────────────────
cats = [(f, clean_name(f), get_category(f)) for f in all_files]
filtered = [
    (f, clean_name(f), get_category(f)) for f in all_files
    if (not search or search.lower() in clean_name(f).lower() or search.lower() in f.lower())
    and (cat_filter == "All Categories" or get_category(f) == cat_filter)
    and (status_filter == "All" or get_sds_status(f)[0] == status_filter)
]

st.markdown("<br>", unsafe_allow_html=True)
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Total Sheets", len(all_files))
m2.metric("Adhesives", sum(1 for _, _, c in cats if c == "Adhesives & Bonds"))
m3.metric("Cleaners", sum(1 for _, _, c in cats if c == "Cleaners"))
m4.metric("Protectors", sum(1 for _, _, c in cats if c == "Protectors & Coatings"))
m5.metric("Overdue", len(overdue_list))
m6.metric("Showing", len(filtered))
st.markdown("---")

# ── PDF LIST ──────────────────────────────────────────────────────────────────
if not filtered:
    st.info("No MSDS found. Try a different search term or filter.")
else:
    for filename, display_name, category in filtered:
        css_class = CATEGORIES.get(category, "cat-other")
        status_label, age_years, issue_str, status_css = get_sds_status(filename)
        contact_name, contact_email = get_supplier(filename)
        pdf_bytes = base64.b64decode(PDF_DATA[filename])

        expander_title = f"📄  {display_name}"
        if status_label == "Overdue":
            expander_title = f"🔴  {display_name}"
        elif status_label == "Due Soon":
            expander_title = f"🟡  {display_name}"

        with st.expander(expander_title, expanded=False):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f'<span class="cat-badge {css_class}">{category}</span>', unsafe_allow_html=True)
                if contact_name or contact_email:
                    if contact_email:
                        supplier_html = f'<div class="supplier-tag">📧 {contact_name + " — " if contact_name else ""}<a href="mailto:{contact_email}">{contact_email}</a></div>'
                    else:
                        supplier_html = f'<div class="supplier-tag">👤 {contact_name}</div>'
                    st.markdown(supplier_html, unsafe_allow_html=True)
            with col2:
                age_text = f"{age_years} yrs ago" if age_years else ""
                st.markdown(
                    f'<span class="{status_css}">{status_label}</span>'
                    f'<span style="color:#888;font-size:13px;margin-left:10px;">Issued {issue_str} {age_text}</span>',
                    unsafe_allow_html=True
                )
            with col3:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"dl_{filename}"
                )

st.markdown("<br><hr><p style='text-align:center;color:#444;font-size:12px;'>TigerTurf Australia · MSDS Library · SDS review threshold: 5 years</p>", unsafe_allow_html=True)
