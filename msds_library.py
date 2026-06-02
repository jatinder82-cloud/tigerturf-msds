import streamlit as st
import base64
import os

MSDS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MSDS")

st.set_page_config(page_title="TigerTurf MSDS Library", page_icon="🧪", layout="wide")

st.markdown("""
<style>
    html, body, [class*="css"] { font-family: "Segoe UI", Arial, sans-serif; }
    .stApp { background-color: #0a0a0a; color: #f0f0f0; }
    .stTextInput input { background: #1a1a1a !important; border: 2px solid #333 !important; border-radius: 10px !important; color: white !important; font-size: 16px !important; }
    .stTextInput input:focus { border-color: #e85d04 !important; }
    div[data-testid="stSelectbox"] > div { background: #1a1a1a !important; border: 2px solid #333 !important; border-radius: 10px !important; color: white !important; }
    .cat-badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
    .cat-adhesives { background: #e85d04; color: white; }
    .cat-cleaners { background: #0077b6; color: white; }
    .cat-protectors { background: #2d6a4f; color: white; }
    .cat-technical { background: #6d28d9; color: white; }
    .cat-hardeners { background: #92400e; color: white; }
    .cat-other { background: #374151; color: white; }
    hr { border-color: #222; }
    .stDownloadButton button { background: #e85d04 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
    .stDownloadButton button:hover { background: #c94e00 !important; }
    [data-testid="stMetricValue"] { color: #e85d04; font-weight: 700; }
    [data-testid="stMetricLabel"] p { color: #aaa !important; }
    [data-testid="stMetric"] { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 12px; }
    details { background: #1a1a1a !important; border: 1px solid #2a2a2a !important; border-radius: 12px !important; margin-bottom: 8px !important; }
    details:hover { border-color: #e85d04 !important; }
    summary { color: #ffffff !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div style="display:flex;align-items:center;gap:20px;padding:10px 0 24px 0;"><div><div style="font-size:22px;font-weight:800;color:#ffffff;">🧪 MSDS Library</div><div style="font-size:12px;color:#e85d04;font-weight:600;letter-spacing:2px;text-transform:uppercase;">Material Safety Data Sheets</div></div></div><hr>', unsafe_allow_html=True)

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

CATEGORIES = {
    "Adhesives & Bonds": "cat-adhesives",
    "Cleaners": "cat-cleaners",
    "Protectors & Coatings": "cat-protectors",
    "Technical Sheets": "cat-technical",
    "Hardeners & Solutions": "cat-hardeners",
    "Other": "cat-other"
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

col1, col2 = st.columns([3, 1])
with col1:
    search = st.text_input("Search", placeholder="🔍  Search by product name...", label_visibility="collapsed")
with col2:
    cat_filter = st.selectbox("Category", ["All Categories"] + list(CATEGORIES.keys()))

all_files = sorted(PDF_DATA.keys())
filtered = [
    (f, clean_name(f), get_category(f)) for f in all_files
    if (not search or search.lower() in clean_name(f).lower() or search.lower() in f.lower())
    and (cat_filter == "All Categories" or get_category(f) == cat_filter)
]

st.markdown("<br>", unsafe_allow_html=True)
cats = [(f, clean_name(f), get_category(f)) for f in all_files]
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Sheets", len(all_files))
m2.metric("Adhesives", sum(1 for _, _, c in cats if c == "Adhesives & Bonds"))
m3.metric("Cleaners", sum(1 for _, _, c in cats if c == "Cleaners"))
m4.metric("Protectors", sum(1 for _, _, c in cats if c == "Protectors & Coatings"))
m5.metric("Showing", len(filtered))
st.markdown("---")

if not filtered:
    st.info("No MSDS found. Try a different search term.")
else:
    for filename, display_name, category in filtered:
        css_class = CATEGORIES.get(category, "cat-other")
        pdf_bytes = base64.b64decode(PDF_DATA[filename])
        with st.expander(f"📄  {display_name}", expanded=False):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f'<span class="cat-badge {css_class}">{category}</span>', unsafe_allow_html=True)
            with col2:
                st.download_button(label="⬇️ Download PDF", data=pdf_bytes, file_name=filename, mime="application/pdf", key=f"dl_{filename}")

st.markdown("<br><hr><p style='text-align:center;color:#444;font-size:12px;'>TigerTurf Australia · MSDS Library</p>", unsafe_allow_html=True)
