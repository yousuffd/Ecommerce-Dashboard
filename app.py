"""
╔══════════════════════════════════════════════════════════════════════╗
║        ELECTRONIC COMMERCE INTELLIGENCE — C-Suite Dashboard           ║
║        Streamlit · Plotly · Pandas · Claude AI / ChatGPT             ║
╠══════════════════════════════════════════════════════════════════════╣
║  Data sources : CSV upload | XLSX upload | PostgreSQL | MySQL | SQLite
║  AI insights  : Claude API / OpenAI GPT-4o + rule-based fallback     ║
╚══════════════════════════════════════════════════════════════════════╝

HOW TO RUN
──────────
1.  pip install -r requirements.txt
2.  Copy .env.example → .env  and fill in your keys / DB credentials
3.  streamlit run app_csuite.py

SECTION MAP
───────────
  §0   Page config
  §1   Global CSS / design system
  §2   Environment / secrets loader
  §3   Data layer  – file loaders + DB connectors + sample generator
  §4   Pandas processing + derived columns
  §5   Metrics computation – KPIs, growth, health scores, cohort proxies
  §6   Plotly chart builders
  §7   AI insights – Claude / OpenAI + rule-based fallback
  §8   Reusable UI components
  §9   Page renderers – Executive Summary | Revenue | Operations | AI Insights | Ask
  §10  Sidebar
  §11  main() entry point
"""

# ── stdlib ──────────────────────────────────────────────────────────
import os
import io
import time
import json
import textwrap
from datetime import datetime, timedelta

# ── third-party ─────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# optional: load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ══════════════════════════════════════════════════════════════════
# §0  PAGE CONFIG  — must be the very first Streamlit call
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Electronic Commerce Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ══════════════════════════════════════════════════════════════════
# §1  GLOBAL CSS / DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════
def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ─────────────────────────────────────────
       DESIGN TOKENS
    ───────────────────────────────────────── */
    :root {
        /* Layout */
        --bg-base:   #eef0f5;   /* page background — noticeably off-white */
        --bg-card:   #ffffff;   /* card surface */
        --bg-raised: #f4f6f9;   /* table rows, inner panels */
        --border:    #dde1ea;   /* standard border */
        --border-strong: #bcc3d0; /* emphasized border */

        /* Brand / accent */
        --blue:      #1d4ed8;
        --blue-light:#eff6ff;
        --blue-mid:  #bfdbfe;
        --gold:      #b45309;
        --gold-light:#fffbeb;
        --green:     #047857;
        --green-light:#ecfdf5;
        --red:       #b91c1c;
        --red-light: #fef2f2;
        --purple:    #6d28d9;

        /* Text — 4-level scale */
        --t-hero:    #0a0f1e;   /* page titles, KPI numbers */
        --t-strong:  #1e2a3a;   /* card headings */
        --t-body:    #374151;   /* body text, table cells */
        --t-muted:   #6b7280;   /* labels, captions */
        --t-faint:   #9ca3af;   /* timestamps, hints */

        /* Typography scale */
        --fs-hero:   1.75rem;
        --fs-h1:     1.15rem;
        --fs-h2:     0.95rem;
        --fs-body:   0.875rem;
        --fs-label:  0.72rem;
        --fs-caption:0.65rem;

        /* Shape */
        --r-sm:  6px;
        --r-md:  10px;
        --r-lg:  14px;

        /* Shadows — real depth on white cards */
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05), 0 2px 6px rgba(0,0,0,0.06);
        --shadow-md: 0 2px 6px rgba(0,0,0,0.07), 0 6px 20px rgba(0,0,0,0.08);
        --shadow-lg: 0 4px 12px rgba(0,0,0,0.09), 0 12px 32px rgba(0,0,0,0.10);
    }
                        
    /* Expander header (the clickable label row) */
    [data-testid="stSidebar"] [data-testid="stExpander"] summary,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary p,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary span,
    [data-testid="stSidebar"] .streamlit-expanderHeader,
    [data-testid="stSidebar"] .streamlit-expanderHeader p {
        color: #ffffff !important;
        font-size: 0.8rem !important;
    }
    /* Expander content (the revealed body) */
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"],
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] div,
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] p,
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] span,
    [data-testid="stSidebar"] .streamlit-expanderContent,
    [data-testid="stSidebar"] .streamlit-expanderContent div,
    [data-testid="stSidebar"] .streamlit-expanderContent p,
    [data-testid="stSidebar"] .streamlit-expanderContent span {
        color: #ffffff !important;
    }
    

    /* ─────────────────────────────────────────
       BASE
    ───────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: var(--bg-base) !important;
        color: var(--t-body) !important;
        font-size: var(--fs-body) !important;
        line-height: 1.5 !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stHeader"] { display: none !important; }
    .block-container {
        padding-top: 0 !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }

    /* ─────────────────────────────────────────
       SIDEBAR — dark panel, high contrast
    ───────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: #111827 !important;
        border-right: 1px solid #374151 !important;
        min-width: 240px !important;
        max-width: 240px !important;
    }
    /* Force all text in sidebar content to be visible */
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f9fafb !important;
        font-size: 0.65rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
    }
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio span,
    [data-testid="stSidebar"] .stRadio p,
    [data-testid="stSidebar"] .stRadio div {
        color: #ffffff !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSelectbox span,
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] div { color: #e5e7eb !important; }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown a,
    [data-testid="stSidebar"] .stMarkdown div { color: #e5e7eb !important; font-size: 0.85rem !important; }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-baseweb="input"] input,
    [data-testid="stSidebar"] [data-baseweb="textarea"] textarea {
        background: #1f2937 !important; color: #f9fafb !important;
        border: 1px solid #374151 !important; border-radius: var(--r-sm) !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stSidebar"] input::placeholder { color: #6b7280 !important; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #1f2937 !important; border: 1px solid #374151 !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        background: #1f2937 !important; border: 1px dashed #3b82f6 !important;
        border-radius: var(--r-sm) !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] button {
        background: #1d4ed8 !important; color: #fff !important;
        font-weight: 600 !important; border: none !important;
        border-radius: var(--r-sm) !important; width: 100% !important;
    }
    [data-testid="stSidebar"] hr { border-color: #374151 !important; }
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] .stCaption { color: #9ca3af !important; }
    /* Hide the collapse/expand toggle button */
    [data-testid="collapsedControl"] { display: none !important; }
    button[title="View fullscreen"] { display: none !important; }

    /* ─────────────────────────────────────────
       TOP HEADER
    ───────────────────────────────────────── */
    .top-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 100%);
        border-bottom: none;
        padding: 16px 28px;
        display: flex; align-items: center; justify-content: space-between;
        position: sticky; top: 0; z-index: 999;
        box-shadow: 0 2px 12px rgba(29,78,216,0.25);
    }
    .logo {
        font-size: var(--fs-h1);
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.3px;
    }
    .logo span { color: #93c5fd; }
    .tagline {
        font-size: var(--fs-caption);
        color: rgba(255,255,255,0.55);
        letter-spacing: 1.8px;
        margin-top: 3px;
        text-transform: uppercase;
        font-weight: 500;
    }
    .header-right { display: flex; align-items: center; gap: 10px; }
    .badge {
        background: rgba(255,255,255,0.15); color: #ffffff;
        border: 1px solid rgba(255,255,255,0.3); border-radius: 20px;
        font-size: var(--fs-caption); font-weight: 700;
        padding: 3px 10px; letter-spacing: 0.8px;
    }
    .ds-badge {
        background: rgba(255,255,255,0.12); color: rgba(255,255,255,0.85);
        border: 1px solid rgba(255,255,255,0.2); border-radius: 20px;
        font-size: var(--fs-caption); padding: 3px 10px;
    }
    /* page context breadcrumb */
    .page-context {
        font-size: var(--fs-caption);
        color: rgba(255,255,255,0.5);
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-weight: 500;
        margin-top: 2px;
    }
    .page-context span { color: rgba(255,255,255,0.9); font-weight: 700; }

    /* ─────────────────────────────────────────
       KPI CARDS
    ───────────────────────────────────────── */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px; margin-bottom: 18px;
    }
    @media (max-width: 1200px) { .kpi-grid { grid-template-columns: repeat(3,1fr); } }
    @media (max-width: 768px)  { .kpi-grid { grid-template-columns: repeat(2,1fr); } }

    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--r-lg);
        padding: 20px 22px 18px;
        position: relative; overflow: hidden;
        box-shadow: var(--shadow-sm);
        transition: box-shadow .18s, transform .18s;
    }
    .kpi-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
    /* color bar top */
    .kpi-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
        background: var(--blue);
    }
    .kpi-card.gold::before   { background: var(--gold); }
    .kpi-card.green::before  { background: var(--green); }
    .kpi-card.red::before    { background: var(--red); }
    .kpi-card.purple::before { background: var(--purple); }

    .kpi-icon {
        position: absolute; top: 14px; right: 14px;
        font-size: 1.4rem; opacity: 0.10;
    }
    /* LABEL — smallest, caps, muted */
    .kpi-label {
        font-size: var(--fs-caption);
        font-weight: 600;
        letter-spacing: 1.1px;
        text-transform: uppercase;
        color: var(--t-muted);
        margin-bottom: 8px;
    }
    /* VALUE — hero number, strong contrast */
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: var(--t-hero) !important;
        line-height: 1;
        margin-bottom: 6px;
        letter-spacing: -1px;
        font-family: 'Inter', sans-serif;
    }
    /* DELTA — body-size, colored */
    .kpi-delta {
        font-size: var(--fs-label);
        font-weight: 600;
    }
    .kpi-delta.pos { color: var(--green); }
    .kpi-delta.neg { color: var(--red); }
    .kpi-delta.neu { color: var(--t-muted); }
    /* SUB — caption below delta */
    .kpi-sub {
        font-size: var(--fs-caption);
        color: var(--t-faint);
        margin-top: 3px;
    }

    /* ─────────────────────────────────────────
       SECTION CARDS
    ───────────────────────────────────────── */
    .section-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--r-lg);
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: var(--shadow-sm);
    }
    /* SECTION TITLE — label-size, spaced caps */
    .section-title {
        font-size: var(--fs-label);
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: var(--t-muted);
        margin-bottom: 16px;
        display: flex; align-items: center; gap: 8px;
    }

    /* color dots */
    .dot       { width:5px; height:5px; background:var(--blue);   border-radius:50%; display:inline-block; flex-shrink:0; }
    .dot-gold  { width:5px; height:5px; background:var(--gold);   border-radius:50%; display:inline-block; flex-shrink:0; }
    .dot-green { width:5px; height:5px; background:var(--green);  border-radius:50%; display:inline-block; flex-shrink:0; }
    .dot-red   { width:5px; height:5px; background:var(--red);    border-radius:50%; display:inline-block; flex-shrink:0; }

    /* ─────────────────────────────────────────
       STREAMLIT CONTAINER BORDER — chart labels
    ───────────────────────────────────────── */
    /* The st.container(border=True) label we inject */
    .chart-label {
        font-size: var(--fs-label);
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: var(--t-muted);
        margin-bottom: 4px;
        display: flex; align-items: center; gap: 6px;
    }

    /* ─────────────────────────────────────────
       EXEC ALERT BANNERS
    ───────────────────────────────────────── */
    .exec-alert {
        border-left: 4px solid var(--red);
        border-radius: 0 var(--r-sm) var(--r-sm) 0;
        padding: 12px 16px; margin-bottom: 10px;
        font-size: var(--fs-body); font-weight: 500;
        color: #7f1d1d; background: var(--red-light);
        line-height: 1.5;
    }
    .exec-alert.warn { border-color: var(--gold); color: #78350f; background: var(--gold-light); }
    .exec-alert.good { border-color: var(--green); color: #064e3b; background: var(--green-light); }
    .exec-alert.info { border-color: var(--blue); color: #1e3a8a; background: var(--blue-light); }

    /* ─────────────────────────────────────────
       AI INSIGHT CARDS
    ───────────────────────────────────────── */
    .insight-card {
        background: #f8faff;
        border: 1px solid #dbeafe;
        border-left: 4px solid var(--blue);
        border-radius: 0 var(--r-md) var(--r-md) 0;
        padding: 14px 18px; margin-bottom: 10px;
    }
    /* insight number — mono, blue, small */
    .insight-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: var(--fs-caption);
        font-weight: 700;
        color: var(--blue);
        margin-right: 8px;
    }
    /* insight text — body size, readable */
    .insight-text {
        font-size: var(--fs-body);
        line-height: 1.7;
        color: var(--t-strong);
    }

    /* ─────────────────────────────────────────
       SCORECARD TABLE
    ───────────────────────────────────────── */
    .styled-table { width:100%; border-collapse:collapse; }
    .styled-table th {
        background: var(--bg-raised);
        color: var(--t-muted);
        font-size: var(--fs-caption);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.9px;
        padding: 10px 14px;
        text-align: left;
        border-bottom: 2px solid var(--border-strong);
    }
    /* TABLE BODY — body-size, readable color */
    .styled-table td {
        font-size: var(--fs-body);
        padding: 11px 14px;
        border-bottom: 1px solid var(--bg-raised);
        color: var(--t-body);
    }
    .styled-table tr:hover td { background: var(--bg-raised); }
    .styled-table tr:last-child td { border-bottom: none; }
    .rank-badge {
        background: var(--blue-light); color: var(--blue);
        border-radius: 4px; padding: 2px 7px;
        font-size: var(--fs-caption); font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ─────────────────────────────────────────
       PILLS
    ───────────────────────────────────────── */
    .pill {
        display: inline-block; border-radius: 20px;
        padding: 2px 10px;
        font-size: var(--fs-caption); font-weight: 600;
    }
    .pill-green  { background: #d1fae5; color: #065f46; }
    .pill-red    { background: #fee2e2; color: #991b1b; }
    .pill-amber  { background: #fef3c7; color: #92400e; }
    .pill-blue   { background: #dbeafe; color: #1e40af; }
    .pill-purple { background: #ede9fe; color: #5b21b6; }

    /* ─────────────────────────────────────────
       ALERT BOXES
    ───────────────────────────────────────── */
    .info-box    { background:var(--blue-light);  border:1px solid var(--blue-mid);  border-radius:var(--r-md); padding:12px 16px; font-size:var(--fs-body); color:#1e40af; line-height:1.6; margin-bottom:12px; }
    .warn-box    { background:var(--gold-light);  border:1px solid #fde68a;          border-radius:var(--r-md); padding:12px 16px; font-size:var(--fs-body); color:#78350f; line-height:1.6; margin-bottom:12px; }
    .error-box   { background:var(--red-light);   border:1px solid #fecaca;          border-radius:var(--r-md); padding:12px 16px; font-size:var(--fs-body); color:#991b1b; line-height:1.6; margin-bottom:12px; }
    .success-box { background:var(--green-light); border:1px solid #a7f3d0;          border-radius:var(--r-md); padding:12px 16px; font-size:var(--fs-body); color:#065f46; line-height:1.6; margin-bottom:12px; }

    /* ─────────────────────────────────────────
       SECONDARY KPI CARDS (ops strip)
    ───────────────────────────────────────── */
    .ops-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--r-lg);
        padding: 16px 20px;
        box-shadow: var(--shadow-sm);
    }
    .ops-card .kpi-label   { font-size: var(--fs-caption); }
    .ops-card .ops-value   {
        font-size: var(--fs-h1);
        font-weight: 800;
        color: var(--t-hero);
        margin: 6px 0 4px;
        font-family: 'Inter', sans-serif;
    }
    .ops-card .ops-status  { font-size: var(--fs-caption); color: var(--t-muted); }

    /* ─────────────────────────────────────────
       CHAT BUBBLES
    ───────────────────────────────────────── */
    .chat-wrap  { display:flex; flex-direction:column; gap:14px; margin-bottom:24px; }
    .bubble-row { display:flex; align-items:flex-end; gap:10px; }
    .bubble-row.user { flex-direction:row-reverse; }
    .avatar {
        width:32px; height:32px; border-radius:50%; flex-shrink:0;
        display:flex; align-items:center; justify-content:center;
        font-size:13px; font-weight:700;
    }
    .avatar.claude { background: var(--blue); color:#fff; }
    .avatar.user   { background: var(--bg-raised); border:1px solid var(--border); color:var(--t-muted); }
    .bubble {
        max-width:72%; padding:12px 16px;
        border-radius:14px; line-height:1.65; color:var(--t-body);
        font-size: var(--fs-body);
    }
    .bubble.claude { background:var(--bg-raised); border:1px solid var(--border); border-bottom-left-radius:4px; }
    .bubble.user   { background:#dbeafe; border:1px solid #bfdbfe; border-bottom-right-radius:4px; color:#1e3a8a; }
    .chat-meta { font-size:var(--fs-caption); color:var(--t-faint); margin-top:3px; padding:0 42px; }
    .chat-meta.user { text-align:right; }
    .suggested-btn button {
        background:var(--bg-raised) !important; color:var(--t-muted) !important;
        border:1px solid var(--border) !important; border-radius:20px !important;
        padding:6px 14px !important; font-size:var(--fs-label) !important;
        font-weight:500 !important; margin:0 4px 6px 0 !important;
        transition:all .18s !important;
    }
    .suggested-btn button:hover {
        border-color:var(--blue) !important; color:var(--blue) !important;
        background:var(--blue-light) !important;
    }

    /* ─────────────────────────────────────────
       BUTTONS
    ───────────────────────────────────────── */
    .stButton > button {
        background: var(--blue) !important; color: #fff !important;
        font-weight: 600 !important; border: none !important;
        border-radius: var(--r-sm) !important; padding: 8px 20px !important;
        font-size: var(--fs-body) !important; transition: opacity .18s !important;
    }
    .stButton > button:hover { opacity: .86 !important; }

    /* ─────────────────────────────────────────
       FOOTER
    ───────────────────────────────────────── */
    .footer {
        text-align:center; padding:20px 0 12px;
        font-size: var(--fs-caption); color: var(--t-faint);
        border-top:1px solid var(--border); margin-top:28px;
    }
    .footer span { color: var(--blue); font-weight:600; }

    /* ─────────────────────────────────────────
       SCROLLBAR
    ───────────────────────────────────────── */
    ::-webkit-scrollbar { width:5px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius:3px; }

    /* ─────────────────────────────────────────
       UPLOAD ZONE
    ───────────────────────────────────────── */
    .upload-zone {
        background: var(--bg-card); border: 2px dashed var(--border);
        border-radius: var(--r-lg); padding: 60px 40px; text-align: center;
    }
    .upload-zone:hover { border-color: var(--blue); }
    .upload-title { font-size: var(--fs-h2); font-weight: 700; color: var(--t-strong); margin-bottom: 8px; }
    .upload-sub   { font-size: var(--fs-body); color: var(--t-muted); }
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# §2  ENVIRONMENT / SECRETS LOADER
# ══════════════════════════════════════════════════════════════════
def load_env_config() -> dict:
    """
    Priority order for secrets:
      1. st.secrets  (Streamlit Cloud deployment)
      2. OS environment variables  (loaded from .env via python-dotenv)
      3. Empty string fallback

    Returns a flat dict so the rest of the app never has to worry
    about where the value came from.
    """
    def _get(key: str) -> str:
        # Streamlit secrets (toml-based)
        try:
            return st.secrets.get(key, "")
        except Exception:
            pass
        # Plain env var
        return os.environ.get(key, "")

    return {
        "ANTHROPIC_API_KEY": _get("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY":    _get("OPENAI_API_KEY"),
        "DB_TYPE":           _get("DB_TYPE"),          # postgres | mysql | sqlite
        "DB_HOST":           _get("DB_HOST"),
        "DB_PORT":           _get("DB_PORT"),
        "DB_NAME":           _get("DB_NAME"),
        "DB_USER":           _get("DB_USER"),
        "DB_PASSWORD":       _get("DB_PASSWORD"),
        "DB_SQLITE_PATH":    _get("DB_SQLITE_PATH"),   # path for SQLite
        "DB_TABLE":          _get("DB_TABLE"),          # table / view to query
    }


# ══════════════════════════════════════════════════════════════════
# §3  DATA LAYER — loaders + DB connectors + sample generator
# ══════════════════════════════════════════════════════════════════
REQUIRED_COLS = {
    "order_id", "order_date", "product_name", "category",
    "quantity", "unit_price", "revenue", "city",
    "order_status", "shipping_days",
}

# ── Sample data constants ──────────────────────────────────────────
_CITIES  = ["Mumbai","Delhi","Bengaluru","Hyderabad","Chennai",
             "Pune","Kolkata","Ahmedabad","Jaipur","Surat"]
_STATES  = ["Maharashtra","Delhi","Karnataka","Telangana","Tamil Nadu",
             "Maharashtra","West Bengal","Gujarat","Rajasthan","Gujarat"]
_CITY_STATE = dict(zip(_CITIES, _STATES))

_PRODUCTS = ["Wireless Earbuds Pro","Fitness Tracker X2","Bamboo Water Bottle",
             "Mechanical Keyboard","USB-C Hub 7-in-1","Yoga Mat Premium",
             "Smart LED Bulb","Portable Charger 20k","Coffee Grinder Mini","Running Shoes V3"]
_SKUS     = ["SKU-EAR-001","SKU-FIT-002","SKU-LIF-003","SKU-KEY-004","SKU-HUB-005",
             "SKU-YOG-006","SKU-LED-007","SKU-CHG-008","SKU-COF-009","SKU-RUN-010"]
_CATS     = ["Electronics","Electronics","Lifestyle","Electronics","Electronics",
             "Fitness","Smart Home","Electronics","Kitchen","Footwear"]

# COGS as % of unit_price per product (realistic margins)
_COGS_PCT = [0.52, 0.48, 0.35, 0.55, 0.50, 0.38, 0.42, 0.53, 0.40, 0.45]

# Realistic INR price ranges per product (base year 2020)
_PRICE_RANGE = [
    (1200, 6000),   # Wireless Earbuds
    (2500, 8000),   # Fitness Tracker
    (300,  900),    # Bamboo Water Bottle
    (3500, 12000),  # Mechanical Keyboard
    (800,  3500),   # USB-C Hub
    (600,  2500),   # Yoga Mat
    (400,  1800),   # Smart LED Bulb
    (1500, 4500),   # Portable Charger
    (1200, 4000),   # Coffee Grinder
    (2000, 9000),   # Running Shoes
]

_STATUSES  = ["Delivered","Delivered","Delivered","Shipped","Processing",
              "Returned","Refunded","Cancelled"]
_STATUS_P  = [0.52, 0.13, 0.09, 0.08, 0.05, 0.05, 0.04, 0.04]

_RETURN_REASONS = [
    "Changed mind","Defective product","Wrong item delivered",
    "Better price elsewhere","Delayed delivery","Size/fit issue",
]

_CARRIERS        = ["BlueDart","Delhivery","Ekart","XpressBees","DTDC"]
_CARRIER_SPEED   = {"BlueDart":(1,4),"Delhivery":(2,6),"Ekart":(2,7),
                    "XpressBees":(2,5),"DTDC":(3,10)}
_CARRIER_PROMISE = {"BlueDart":2,"Delhivery":4,"Ekart":5,"XpressBees":3,"DTDC":6}

_CHANNELS  = ["Direct Website","Google Ads","Organic Search","Email Campaign",
              "Instagram Ads","Amazon Marketplace","Flipkart Marketplace","Referral"]
_CHANNEL_P = [0.20, 0.18, 0.15, 0.10, 0.12, 0.12, 0.08, 0.05]

_PAYMENT   = ["UPI","Credit Card","Debit Card","Net Banking","Cash on Delivery","Wallet"]
_PAYMENT_P = [0.35, 0.22, 0.18, 0.08, 0.12, 0.05]


def generate_sample_data(n: int = 5000) -> pd.DataFrame:
    """
    Realistic 5-year synthetic e-commerce dataset (2020–2024).
    23 fields covering: customer, product, pricing, discounts, margin,
    fulfilment, SLA, logistics, channel, geography.

    Realism features
    ─────────────────
    • YoY order volume growth (10 → 30 pct weight by year)
    • Nov–Dec festive season spike (1.5–1.8×)
    • Realistic INR price ranges per product category
    • 5 % annual price inflation
    • ~3 500 unique customers with weighted repeat-purchase behaviour
    • Loyal customers ordered 3× more than new ones
    • 30 % of orders carry a discount (5–25 %)
    • COGS computed per-product; gross margin derived
    • Carrier-specific ship-day windows
    • COD orders have 12 % extra return probability
    • Promised vs actual delivery dates for SLA breach analysis
    • Metro cities get proportionally more volume
    """
    rng = np.random.default_rng(42)

    # ── Date distribution: YoY growth + seasonal spike ───────────
    all_dates = pd.date_range("2020-01-01", "2024-12-31", freq="D")
    year_w  = {2020:0.10, 2021:0.15, 2022:0.20, 2023:0.25, 2024:0.30}
    month_w = {1:0.70,2:0.70,3:0.80,4:0.80,5:0.90,6:0.90,
               7:1.00,8:1.00,9:1.05,10:1.10,11:1.50,12:1.80}
    w = np.array([year_w[d.year] * month_w[d.month] for d in all_dates], dtype=float)
    w /= w.sum()
    idx    = rng.choice(len(all_dates), size=n, p=w, replace=True)
    chosen = sorted(all_dates[idx])   # list of pd.Timestamp

    # ── Products ─────────────────────────────────────────────────
    pidx = rng.integers(0, len(_PRODUCTS), n)

    # ── Pricing: category-specific INR ranges + 5 %/yr inflation ─
    years_from = np.array([(d.year - 2020) for d in chosen])
    prices = np.array([
        rng.uniform(_PRICE_RANGE[pidx[i]][0], _PRICE_RANGE[pidx[i]][1])
        * (1.05 ** years_from[i])
        for i in range(n)
    ]).round(2)

    qty = rng.integers(1, 4, n)   # 1–3 units per order (realistic)

    # ── Discounts: ~30 % of orders, 5–25 % off ───────────────────
    disc_mask = rng.random(n) < 0.30
    disc_pct  = np.where(disc_mask, rng.uniform(0.05, 0.25, n), 0.0)
    disc_amt  = (prices * disc_pct).round(2)
    revenue   = ((prices - disc_amt) * qty).round(2)

    # ── COGS & gross margin ───────────────────────────────────────
    cogs         = np.array([prices[i] * _COGS_PCT[pidx[i]] * qty[i]
                              for i in range(n)]).round(2)
    gross_margin = (revenue - cogs).round(2)

    # ── Payment method ────────────────────────────────────────────
    payment = rng.choice(_PAYMENT, n, p=_PAYMENT_P)

    # ── Carriers (random) ─────────────────────────────────────────
    carriers = rng.choice(_CARRIERS, n)

    # ── Shipping days: carrier-specific window ────────────────────
    ship_days = np.array([
        rng.integers(_CARRIER_SPEED[carriers[i]][0],
                     _CARRIER_SPEED[carriers[i]][1] + 1)
        for i in range(n)
    ])

    # ── Order status: COD elevates return probability ────────────
    base_st = rng.choice(_STATUSES, n, p=_STATUS_P)
    statuses = []
    for i, st in enumerate(base_st):
        if payment[i] == "Cash on Delivery" and rng.random() < 0.12:
            statuses.append(rng.choice(["Returned","Refunded"], p=[0.6,0.4]))
        else:
            statuses.append(st)
    statuses = np.array(statuses)

    # ── Return reasons (only for returned/refunded orders) ────────
    return_rsn = [
        rng.choice(_RETURN_REASONS) if s in ("Returned","Refunded") else ""
        for s in statuses
    ]

    # ── Delivery dates ────────────────────────────────────────────
    promised_delivery = [
        (pd.Timestamp(chosen[i]) +
         pd.Timedelta(days=int(_CARRIER_PROMISE[carriers[i]]))).strftime("%Y-%m-%d")
        for i in range(n)
    ]
    actual_delivery = [
        (pd.Timestamp(chosen[i]) +
         pd.Timedelta(days=int(ship_days[i]))).strftime("%Y-%m-%d")
        for i in range(n)
    ]

    # ── Customers: 3 500 unique, loyalty-weighted repeat orders ──
    n_cust       = 3500
    cust_ids     = [f"CUST-{10000+i}" for i in range(n_cust)]
    cust_w       = np.ones(n_cust, dtype=float)
    cust_w[:700]       = 3.0   # Loyal   — order 3× more
    cust_w[700:1400]   = 1.8   # Returning
    cust_w[1400:2800]  = 1.0   # New
    cust_w[2800:]      = 0.6   # At-Risk — order less
    cust_w /= cust_w.sum()
    cust_assign = rng.choice(n_cust, size=n, p=cust_w, replace=True)

    def _segment(i: int) -> str:
        if i < 700:    return "Loyal"
        if i < 1400:   return "Returning"
        if i < 2800:   return "New"
        return "At-Risk"

    # ── Cities: metro-weighted volume ─────────────────────────────
    city_w = np.array([0.18,0.18,0.14,0.10,0.10,0.09,0.08,0.06,0.04,0.03])
    cities = rng.choice(_CITIES, n, p=city_w)

    # ── Channels ─────────────────────────────────────────────────
    channels = rng.choice(_CHANNELS, n, p=_CHANNEL_P)

    df = pd.DataFrame({
        "order_id":               [f"ORD-{10000+i}" for i in range(n)],
        "order_date":             [d.strftime("%Y-%m-%d") for d in chosen],
        "customer_id":            [cust_ids[c] for c in cust_assign],
        "customer_segment":       [_segment(c) for c in cust_assign],
        "channel":                channels,
        "product_name":           [_PRODUCTS[i] for i in pidx],
        "sku_id":                 [_SKUS[i]     for i in pidx],
        "category":               [_CATS[i]     for i in pidx],
        "quantity":               qty,
        "unit_price":             prices,
        "discount_amount":        disc_amt,
        "revenue":                revenue,
        "cogs":                   cogs,
        "gross_margin":           gross_margin,
        "city":                   cities,
        "state":                  [_CITY_STATE[c] for c in cities],
        "payment_method":         payment,
        "order_status":           statuses,
        "return_reason":          return_rsn,
        "carrier":                carriers,
        "shipping_days":          ship_days,
        "promised_delivery_date": promised_delivery,
        "actual_delivery_date":   actual_delivery,
    })

    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


# ── File loaders ───────────────────────────────────────────────────
def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace(" ","_").replace("-","_") for c in df.columns]
    return df


def _coerce_types(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Parse dates and numerics; return (df, warnings)."""
    warns = []
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    dropped = df["order_date"].isna().sum()
    if dropped:
        warns.append(f"{dropped} rows dropped — unparseable order_date.")
    df = df.dropna(subset=["order_date"])

    for col in ["quantity","unit_price","revenue","shipping_days"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0
            warns.append(f"Column '{col}' not found — defaulting to 0.")

    if df["revenue"].sum() == 0 and df["unit_price"].sum() > 0:
        df["revenue"] = (df["unit_price"] * df["quantity"]).round(2)
        warns.append("revenue derived from unit_price × quantity.")

    return df, warns


def load_csv(file) -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_csv(file)
    df = _normalise_columns(df)
    return _coerce_types(df)


def load_excel(file) -> tuple[pd.DataFrame, list[str]]:
    """
    Reads the first sheet by default.
    If the workbook has multiple sheets the user can pick one
    (handled in the sidebar).
    """
    xl = pd.ExcelFile(file)
    sheet = xl.sheet_names[0]
    # stash sheet list in session for sheet selector
    st.session_state["_excel_sheets"] = xl.sheet_names
    chosen = st.session_state.get("_chosen_sheet", sheet)
    df = xl.parse(chosen)
    df = _normalise_columns(df)
    return _coerce_types(df)



# ── Column mapper ──────────────────────────────────────────────────
# Maps the 10 required field names to whatever the user's file calls them.
_REQUIRED_FIELDS = [
    ("order_id",      "Order ID"),
    ("order_date",    "Order Date"),
    ("product_name",  "Product Name"),
    ("category",      "Category"),
    ("quantity",      "Quantity"),
    ("unit_price",    "Unit Price"),
    ("revenue",       "Revenue"),
    ("city",          "City"),
    ("order_status",  "Order Status"),
    ("shipping_days", "Shipping Days"),
]

_OPTIONAL_FIELDS = [
    ("customer_id",            "Customer ID"),
    ("customer_segment",       "Customer Segment"),
    ("channel",                "Acquisition Channel"),
    ("sku_id",                 "SKU ID"),
    ("discount_amount",        "Discount Amount"),
    ("cogs",                   "COGS"),
    ("gross_margin",           "Gross Margin"),
    ("state",                  "State / Region"),
    ("payment_method",         "Payment Method"),
    ("return_reason",          "Return Reason"),
    ("carrier",                "Carrier"),
    ("promised_delivery_date", "Promised Delivery Date"),
    ("actual_delivery_date",   "Actual Delivery Date"),
]


@st.dialog("🗂️ Map Your Columns", width="large")
def _column_mapper_dialog(df: pd.DataFrame, file_key: str):
    """
    Modal dialog for column mapping.
    Stores the rename mapping in session_state and closes itself on confirm.
    file_key is a unique identifier (e.g. file name) so the mapping is
    re-shown when a new file is uploaded.
    """
    raw_cols    = list(df.columns)
    none_option = "— skip / not in file —"
    options     = [none_option] + raw_cols

    st.markdown(
        '<p style="color:#a0b0cc;font-size:.85rem;margin-bottom:16px;">'
        'Match each required field to the corresponding column in your file. '
        'Columns that already match are pre-selected.</p>',
        unsafe_allow_html=True,
    )

    mapping = {}
    cols_left, cols_right = st.columns(2)
    half = len(_REQUIRED_FIELDS) // 2

    for i, (required, label) in enumerate(_REQUIRED_FIELDS):
        default = required if required in raw_cols else none_option
        col     = cols_left if i < half else cols_right
        with col:
            chosen = st.selectbox(
                label,
                options,
                index=options.index(default),
                key=f"dlg_colmap_{required}",
            )
            mapping[required] = None if chosen == none_option else chosen

    unmapped = [label for req, label in _REQUIRED_FIELDS
                if mapping.get(req) is None and req not in df.columns]
    if unmapped:
        st.warning(f"⚠️ Unmapped fields: {', '.join(unmapped)}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅ Confirm Mapping", use_container_width=True):
        rename = {v: k for k, v in mapping.items() if v is not None}
        st.session_state[f"colmap_rename_{file_key}"] = rename
        st.session_state[f"colmap_done_{file_key}"]   = True
        st.rerun()


def render_column_mapper(df: pd.DataFrame, file_key: str) -> pd.DataFrame:
    """
    Opens the column-mapper as a modal dialog on first load.
    Returns a renamed copy of df using the stored mapping.

    Call this AFTER reading the raw file and BEFORE process().
    file_key should be a stable identifier (e.g. uploaded file name).
    """
    done_key   = f"colmap_done_{file_key}"
    rename_key = f"colmap_rename_{file_key}"

    if not st.session_state.get(done_key):
        # Open dialog (will rerun once confirmed)
        _column_mapper_dialog(df, file_key)
        # Return unmapped df until user confirms
        return df

    rename = st.session_state.get(rename_key, {})
    if rename:
        st.sidebar.markdown(
            '<div style="font-size:.7rem;color:#22c55e;margin-top:4px;">'
            '✅ Column mapping applied</div>',
            unsafe_allow_html=True,
        )
    return df.rename(columns=rename)


def _pg_connection(cfg: dict):
    """Returns a psycopg2 connection or raises ImportError / OperationalError."""
    import psycopg2
    port = int(cfg["DB_PORT"]) if cfg["DB_PORT"] else 5432
    return psycopg2.connect(
        host=cfg["DB_HOST"], port=port,
        dbname=cfg["DB_NAME"], user=cfg["DB_USER"],
        password=cfg["DB_PASSWORD"], connect_timeout=8,
    )


def _mysql_connection(cfg: dict):
    import pymysql
    port = int(cfg["DB_PORT"]) if cfg["DB_PORT"] else 3306
    return pymysql.connect(
        host=cfg["DB_HOST"], port=port,
        database=cfg["DB_NAME"], user=cfg["DB_USER"],
        password=cfg["DB_PASSWORD"], connect_timeout=8,
    )


def _sqlite_connection(cfg: dict):
    import sqlite3
    path = cfg["DB_SQLITE_PATH"] or ":memory:"
    return sqlite3.connect(path)


def _mssql_connection(cfg: dict):
    """
    SQL Server via pyodbc.
    Requires:  pip install pyodbc
    And the ODBC Driver 17/18 on the OS:
      macOS:  brew install msodbcsql18
      Ubuntu: follow https://learn.microsoft.com/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server
    """
    import pyodbc
    port = int(cfg["DB_PORT"]) if cfg["DB_PORT"] else 1433
    # Try ODBC Driver 18 first, fall back to 17
    for driver in ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"]:
        try:
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={cfg['DB_HOST']},{port};"
                f"DATABASE={cfg['DB_NAME']};"
                f"UID={cfg['DB_USER']};"
                f"PWD={cfg['DB_PASSWORD']};"
                "TrustServerCertificate=yes;"
                "Connection Timeout=8;"
            )
            return pyodbc.connect(conn_str)
        except Exception:
            continue
    raise RuntimeError(
        "No compatible SQL Server ODBC driver found. "
        "Install 'ODBC Driver 17 for SQL Server' or 'ODBC Driver 18 for SQL Server'."
    )


_DB_DRIVERS = {
    "postgres":   _pg_connection,
    "postgresql": _pg_connection,
    "mysql":      _mysql_connection,
    "mssql":      _mssql_connection,
    "sqlserver":  _mssql_connection,
    "sqlite":     _sqlite_connection,
}


@st.cache_data(ttl=300, show_spinner=False)   # cache for 5 minutes
def load_from_db(cfg_tuple: tuple, query: str) -> tuple[pd.DataFrame, list[str]]:
    """
    Executes `query` against the configured database and returns (df, warns).
    cfg_tuple is a hashable tuple of (db_type, host, port, dbname, user, pw, sqlite_path).
    Results are cached for 5 minutes so repeated page switches don't re-query.
    """
    cfg = {
        "DB_TYPE": cfg_tuple[0], "DB_HOST": cfg_tuple[1],
        "DB_PORT": cfg_tuple[2], "DB_NAME": cfg_tuple[3],
        "DB_USER": cfg_tuple[4], "DB_PASSWORD": cfg_tuple[5],
        "DB_SQLITE_PATH": cfg_tuple[6],
    }
    db_type = cfg["DB_TYPE"].lower()
    connector = _DB_DRIVERS.get(db_type)
    if not connector:
        return pd.DataFrame(), [f"Unsupported DB type: {db_type}"]

    try:
        conn = connector(cfg)
        df   = pd.read_sql(query, conn)
        conn.close()
    except Exception as e:
        return pd.DataFrame(), [f"DB error: {e}"]

    df = _normalise_columns(df)
    df, warns = _coerce_types(df)
    return df, warns


def build_db_query(table: str) -> str:
    """Default SELECT * for the configured table — user can override."""
    return f"SELECT * FROM {table} LIMIT 50000"


# ══════════════════════════════════════════════════════════════════
# §4  PANDAS PROCESSING — derived columns
# ══════════════════════════════════════════════════════════════════
def process(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month"]        = df["order_date"].dt.to_period("M").astype(str)
    df["week"]         = df["order_date"].dt.to_period("W").astype(str)
    df["quarter"]      = df["order_date"].dt.to_period("Q").astype(str)
    df["year"]         = df["order_date"].dt.year.astype(str)
    df["is_returned"]  = df["order_status"].str.lower().isin(["returned","refunded"])
    df["is_cancelled"] = df["order_status"].str.lower().isin(["cancelled","canceled"])
    df["is_delivered"] = df["order_status"].str.lower() == "delivered"
    df["is_delayed"]   = df["shipping_days"] > 7
    df["is_express"]   = df["shipping_days"] <= 2
    df["aov"]          = df["revenue"] / df["quantity"].clip(lower=1)
    df["is_perfect"]   = df["is_delivered"] & ~df["is_delayed"] & ~df["is_returned"]

    # ── Enriched fields — computed only when source columns exist ──
    if "promised_delivery_date" in df.columns and "actual_delivery_date" in df.columns:
        df["promised_delivery_date"] = pd.to_datetime(
            df["promised_delivery_date"], errors="coerce")
        df["actual_delivery_date"]   = pd.to_datetime(
            df["actual_delivery_date"], errors="coerce")
        df["sla_breach"] = (
            df["actual_delivery_date"] > df["promised_delivery_date"]
        ).fillna(False)
    else:
        df["sla_breach"] = df["is_delayed"]

    if "gross_margin" in df.columns:
        df["margin_pct"] = (
            df["gross_margin"] / df["revenue"].clip(lower=0.01) * 100
        ).round(2)
    else:
        df["margin_pct"] = np.nan

    if "discount_amount" in df.columns:
        df["discount_pct"]  = (
            df["discount_amount"] / df["unit_price"].clip(lower=0.01) * 100
        ).round(2)
        df["is_discounted"] = df["discount_amount"] > 0
    else:
        df["discount_pct"]  = 0.0
        df["is_discounted"] = False

    return df


# ══════════════════════════════════════════════════════════════════
# §5  METRICS COMPUTATION — executive KPIs
# ══════════════════════════════════════════════════════════════════
def compute_kpis(df: pd.DataFrame) -> dict:
    orders  = df["order_id"].nunique()
    revenue = df["revenue"].sum()
    aov     = revenue / orders if orders else 0

    # ── MoM growth ───────────────────────────────────────────────
    monthly = df.groupby("month")["revenue"].sum().sort_index()
    if len(monthly) >= 2:
        rev_last   = monthly.iloc[-1]
        rev_prev   = monthly.iloc[-2]
        mom_growth = ((rev_last - rev_prev) / rev_prev * 100) if rev_prev else 0.0
    else:
        mom_growth = 0.0

    # ── QoQ growth ───────────────────────────────────────────────
    quarterly = df.groupby("quarter")["revenue"].sum().sort_index()
    if len(quarterly) >= 2:
        qoq_growth = ((quarterly.iloc[-1] - quarterly.iloc[-2])
                      / quarterly.iloc[-2] * 100)
    else:
        qoq_growth = 0.0

    # ── Customer metrics ─────────────────────────────────────────
    if "customer_id" in df.columns:
        cust_orders      = df.groupby("customer_id")["order_id"].nunique()
        repeat_rate      = (cust_orders > 1).mean() * 100
        unique_customers = df["customer_id"].nunique()
        ltv              = revenue / unique_customers if unique_customers else 0
    else:
        repeat_rate = unique_customers = ltv = None

    # ── Revenue concentration (top-3 products) ───────────────────
    top3_rev = (df.groupby("product_name")["revenue"].sum()
                  .sort_values(ascending=False).head(3).sum())
    rev_concentration = (top3_rev / revenue * 100) if revenue else 0

    # ── Fulfilment ───────────────────────────────────────────────
    perfect_order_rate = df["is_perfect"].mean() * 100
    cancel_rate        = df["is_cancelled"].mean() * 100
    refund_r           = df["is_returned"].mean() * 100
    delay_r            = df["is_delayed"].mean() * 100
    sla_breach_rate    = df["sla_breach"].mean() * 100

    # ── Revenue at risk ───────────────────────────────────────────
    at_risk_mask = df["order_status"].str.lower().isin(
        ["processing","shipped","in transit"])
    at_risk = float(df.loc[at_risk_mask, "revenue"].sum())

    # ── Gross margin ─────────────────────────────────────────────
    if "gross_margin" in df.columns:
        total_margin     = df["gross_margin"].sum()
        gross_margin_pct = (total_margin / revenue * 100) if revenue else 0
    else:
        total_margin = gross_margin_pct = None

    # ── Discounts ────────────────────────────────────────────────
    if "discount_amount" in df.columns:
        discount_rate     = df["is_discounted"].mean() * 100
        avg_discount_pct  = (df.loc[df["is_discounted"],"discount_pct"].mean()
                             if df["is_discounted"].any() else 0)
        revenue_lost_disc = float(df["discount_amount"].sum())
    else:
        discount_rate = avg_discount_pct = revenue_lost_disc = None

    # ── Composite health score (0–100) ───────────────────────────
    s_perfect = min(perfect_order_rate / 85 * 100, 100) * 0.30
    s_refund  = max(0, (10 - refund_r) / 10 * 100) * 0.25
    s_cancel  = max(0, (5  - cancel_rate) / 5 * 100) * 0.20
    s_growth  = min(max(mom_growth + 10, 0) / 20 * 100, 100) * 0.15
    s_delay   = max(0, (25 - delay_r) / 25 * 100) * 0.10
    health_score = round(s_perfect + s_refund + s_cancel + s_growth + s_delay, 1)

    return {
        "revenue":            revenue,
        "orders":             orders,
        "aov":                aov,
        "quantity":           int(df["quantity"].sum()),
        "refund_rate":        refund_r,
        "delay_rate":         delay_r,
        "cancel_rate":        cancel_rate,
        "avg_ship_days":      df["shipping_days"].mean(),
        "mom_growth":         mom_growth,
        "qoq_growth":         qoq_growth,
        "perfect_order_rate": perfect_order_rate,
        "rev_concentration":  rev_concentration,
        "at_risk_revenue":    at_risk,
        "health_score":       health_score,
        "sla_breach_rate":    sla_breach_rate,
        # customer (None if no customer_id)
        "repeat_rate":        repeat_rate,
        "unique_customers":   unique_customers,
        "ltv":                ltv,
        # margin (None if no gross_margin col)
        "gross_margin_total": total_margin,
        "gross_margin_pct":   gross_margin_pct,
        # discounts (None if no discount_amount col)
        "discount_rate":      discount_rate,
        "avg_discount_pct":   avg_discount_pct,
        "revenue_lost_disc":  revenue_lost_disc,
    }


def top_products(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    return (
        df.groupby("product_name")
          .agg(revenue=("revenue","sum"), orders=("order_id","nunique"),
               quantity=("quantity","sum"), avg_price=("unit_price","mean"),
               returns=("is_returned","sum"))
          .sort_values("revenue", ascending=False)
          .head(n).reset_index()
    )


def city_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("city")
          .agg(revenue=("revenue","sum"), orders=("order_id","nunique"),
               delay_rate=("is_delayed","mean"))
          .assign(delay_rate=lambda x: (x["delay_rate"]*100).round(1))
          .sort_values("revenue", ascending=False)
          .reset_index()
    )


def revenue_trend(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    col = "month" if freq == "M" else "week"
    return (
        df.groupby(col)
          .agg(revenue=("revenue","sum"), orders=("order_id","nunique"))
          .reset_index().rename(columns={col:"period"})
          .sort_values("period")
    )


def shipping_summary(df: pd.DataFrame) -> pd.DataFrame:
    # Bins start at -1 so shipping_days=0 (same-day) is captured in Express
    # Thresholds reflect real data: 0-2d express, 3-4d standard, 5-6d slow, 7d+ delayed
    bins   = [-1, 2, 4, 6, 9999]
    labels = ["Express (0-2d)", "Standard (3-4d)", "Slow (5-6d)", "Delayed (7d+)"]
    df2    = df.copy()
    df2["band"] = pd.cut(df2["shipping_days"], bins=bins, labels=labels)
    result = df2.groupby("band", observed=True).size().reset_index(name="count")
    # Keep only bands that have at least 1 order so the chart isn't polluted
    return result[result["count"] > 0].reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════
# §6  PLOTLY CHART BUILDERS
# ══════════════════════════════════════════════════════════════════
_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#64748b", size=11),
    margin=dict(l=0, r=8, t=10, b=0), showlegend=False,
)
_GRID = dict(
    xaxis=dict(gridcolor="#f1f5f9", gridwidth=1, zeroline=False),
    yaxis=dict(gridcolor="#f1f5f9", gridwidth=1, zeroline=False),
)
_ACCENT   = "#2563eb"
_GOLD     = "#d97706"
_GREEN    = "#059669"
_RED      = "#dc2626"
_PURPLE   = "#7c3aed"


def chart_revenue_trend(trend: pd.DataFrame, show_orders: bool = False) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["period"], y=trend["revenue"], name="Revenue",
        mode="lines", line=dict(color=_ACCENT, width=2.5, shape="spline"),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.06)",
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
    ))
    if show_orders and "orders" in trend.columns:
        fig.add_trace(go.Scatter(
            x=trend["period"], y=trend["orders"], name="Orders",
            mode="lines", line=dict(color=_GOLD, width=1.8, dash="dot"),
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
        ))
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                        showgrid=False, zeroline=False,
                        tickfont=dict(color=_GOLD, size=10)),
            showlegend=True,
            legend=dict(orientation="h", x=1, xanchor="right", y=1.1,
                        font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)"),
        )
    fig.update_layout(**_LAYOUT, **_GRID, height=260)
    fig.update_xaxes(tickangle=-25, tickfont=dict(size=10))
    return fig


def chart_mom_waterfall(monthly: pd.DataFrame) -> go.Figure:
    """MoM revenue waterfall — shows growth/decline visually."""
    months = monthly["period"].tolist()[-6:]
    values = monthly["revenue"].tolist()[-6:]
    colors = [_GREEN if v >= 0 else _RED for v in values]
    fig = go.Figure(go.Bar(
        x=months, y=values,
        marker_color=colors,
        text=[f"₹{v/1000:.0f}K" for v in values],
        textposition="outside",
        textfont=dict(color="#64748b", size=10),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_LAYOUT, **_GRID, height=220)
    return fig


def chart_city_bar(city_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        y=city_df["city"], x=city_df["revenue"], orientation="h",
        marker=dict(color=city_df["revenue"],
                    colorscale=[[0,"#131b27"],[.5,"#1d4ed8"],[1,_ACCENT]],
                    showscale=False),
        text=city_df["revenue"].apply(lambda v: f"₹{v/1000:.0f}K"),
        textposition="outside", textfont=dict(color="#374151", size=11),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_LAYOUT, height=300,
                      yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
                      xaxis=dict(gridcolor="#f1f5f9"))
    return fig


def chart_shipping_donut(ship: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=ship["band"], values=ship["count"], hole=0.62,
        marker=dict(colors=[_GREEN, _ACCENT, _GOLD, _RED],
                    line=dict(color="#ffffff", width=2)),
        textinfo="percent", textfont=dict(color="#ffffff", size=11),
        hovertemplate="<b>%{label}</b><br>%{value} orders (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11),
        margin=dict(l=0, r=8, t=10, b=45), showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.32,
                    xanchor="center", x=0.5,
                    font=dict(color="#475569", size=11), bgcolor="rgba(0,0,0,0)"),
        height=270,
    )
    return fig


def chart_category_treemap(df: pd.DataFrame) -> go.Figure:
    cat = df.groupby(["category","product_name"])["revenue"].sum().reset_index()
    fig = px.treemap(cat, path=["category","product_name"], values="revenue",
                     color="revenue",
                     color_continuous_scale=["#dbeafe","#3b82f6","#1d4ed8"])
    fig.update_layout(**_LAYOUT, height=300)
    fig.update_traces(textfont=dict(color="#0f172a"),
                      hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>")
    return fig


def chart_status_bar(df: pd.DataFrame) -> go.Figure:
    s = df["order_status"].value_counts().reset_index()
    s.columns = ["Status","Count"]
    status_colors = {
        "Delivered": _GREEN, "Shipped": _ACCENT, "Processing": _GOLD,
        "Returned": _RED, "Refunded": "#ef4444", "Cancelled": "#6b7280",
    }
    colors = [status_colors.get(st, _ACCENT) for st in s["Status"]]
    fig = go.Figure(go.Bar(
        x=s["Status"], y=s["Count"],
        marker_color=colors,
        text=s["Count"], textposition="outside",
        textfont=dict(color="#64748b", size=10),
        hovertemplate="<b>%{x}</b><br>%{y} orders<extra></extra>",
    ))
    fig.update_layout(**_LAYOUT, **_GRID, height=240)
    return fig


def chart_perfect_order_gauge(rate: float) -> go.Figure:
    color = _GREEN if rate >= 75 else (_GOLD if rate >= 50 else _RED)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rate,
        number=dict(suffix="%", font=dict(size=28, color="#0f172a", family="Inter")),
        gauge=dict(
            axis=dict(range=[0,100], tickcolor="#475569",
                      tickfont=dict(color="#475569", size=10)),
            bar=dict(color=color, thickness=0.25),
            bgcolor="#f8fafc",
            bordercolor="#e2e8f0",
            steps=[
                dict(range=[0,50],  color="#fef2f2"),
                dict(range=[50,75], color="#fffbeb"),
                dict(range=[75,100],color="#ecfdf5"),
            ],
            threshold=dict(line=dict(color=color, width=2), thickness=0.75, value=rate),
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#64748b"),
        margin=dict(l=20, r=20, t=20, b=10), height=200,
    )
    return fig


def chart_revenue_by_category(df: pd.DataFrame) -> go.Figure:
    cat = (df.groupby("category")
             .agg(revenue=("revenue","sum"), orders=("order_id","nunique"))
             .sort_values("revenue", ascending=True).reset_index())
    fig = go.Figure(go.Bar(
        y=cat["category"], x=cat["revenue"], orientation="h",
        marker_color=_PURPLE,
        text=cat["revenue"].apply(lambda v: f"₹{v/1000:.0f}K"),
        textposition="outside", textfont=dict(color="#94a3b8", size=10),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_LAYOUT, height=260,
                      yaxis=dict(gridcolor="rgba(0,0,0,0)"),
                      xaxis=dict(gridcolor="#f1f5f9"))
    return fig


def chart_aov_trend(df: pd.DataFrame) -> go.Figure:
    # Avoid pandas 3.x groupby.apply() crash — compute AOV manually
    monthly_rev    = df.groupby("month")["revenue"].sum()
    monthly_orders = df.groupby("month")["order_id"].nunique()
    aov_m = (monthly_rev / monthly_orders.clip(lower=1)).reset_index()
    aov_m.columns = ["month", "aov"]
    aov_m = aov_m.sort_values("month")
    fig = go.Figure(go.Scatter(
        x=aov_m["month"], y=aov_m["aov"],
        mode="lines+markers",
        line=dict(color=_GOLD, width=2.5, shape="spline"),
        marker=dict(color=_GOLD, size=5),
        fill="tozeroy", fillcolor="rgba(245,158,11,0.05)",
        hovertemplate="<b>%{x}</b><br>AOV: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_LAYOUT, **_GRID, height=220)
    fig.update_xaxes(tickangle=-25, tickfont=dict(size=10))
    return fig


def chart_delay_heatmap(df: pd.DataFrame) -> go.Figure:
    """City × Month delay rate heatmap."""
    pivot = (df.groupby(["city","month"])["is_delayed"]
               .mean().reset_index()
               .pivot(index="city", columns="month", values="is_delayed")
               .fillna(0) * 100)
    cols = sorted(pivot.columns)[-6:]   # last 6 months
    pivot = pivot[cols]
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=cols, y=pivot.index,
        colorscale=[[0,_GREEN],[0.5,_GOLD],[1,_RED]],
        text=[[f"{v:.0f}%" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=9, color="#f0f4f8"),
        hovertemplate="<b>%{y}</b> · %{x}<br>Delay rate: %{z:.1f}%<extra></extra>",
        showscale=False,
    ))
    fig.update_layout(**_LAYOUT, height=280,
                      xaxis=dict(tickangle=-25, tickfont=dict(size=9)),
                      yaxis=dict(tickfont=dict(size=10)))
    return fig


# ── Advanced charts (require enriched columns) ─────────────────────
def chart_margin_by_category(df: pd.DataFrame) -> go.Figure:
    if "gross_margin" not in df.columns:
        return go.Figure()
    cat = (df.groupby("category")
             .agg(revenue=("revenue","sum"), margin=("gross_margin","sum"))
             .assign(margin_pct=lambda x: (x["margin"]/x["revenue"].clip(lower=0.01)*100).round(1))
             .sort_values("margin_pct", ascending=True).reset_index())
    colors = [_GREEN if v>=50 else (_GOLD if v>=35 else _RED) for v in cat["margin_pct"]]
    fig = go.Figure(go.Bar(
        y=cat["category"], x=cat["margin_pct"], orientation="h",
        marker_color=colors,
        text=cat["margin_pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside", textfont=dict(color="#374151", size=11),
        hovertemplate="<b>%{y}</b><br>Gross Margin: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(**_LAYOUT, height=260,
                      xaxis=dict(gridcolor="#e5e7eb", title="Gross Margin %"),
                      yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    return fig


def chart_channel_revenue(df: pd.DataFrame) -> go.Figure:
    if "channel" not in df.columns:
        return go.Figure()
    ch = (df.groupby("channel")
            .agg(revenue=("revenue","sum"), orders=("order_id","nunique"))
            .sort_values("revenue", ascending=True).reset_index())
    fig = go.Figure(go.Bar(
        y=ch["channel"], x=ch["revenue"], orientation="h",
        marker_color=_PURPLE,
        text=ch["revenue"].apply(lambda v: f"₹{v/1000:.0f}K"),
        textposition="outside", textfont=dict(color="#374151", size=11),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_LAYOUT, height=300,
                      xaxis=dict(gridcolor="#e5e7eb"),
                      yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    return fig


def chart_new_vs_returning(df: pd.DataFrame) -> go.Figure:
    if "customer_id" not in df.columns:
        return go.Figure()
    first_order = df.groupby("customer_id")["order_date"].min().rename("first_date")
    df2 = df.join(first_order, on="customer_id")
    df2["cust_type"] = np.where(df2["order_date"] == df2["first_date"], "New", "Returning")
    monthly = (df2.groupby(["month","cust_type"])["revenue"]
                  .sum().reset_index()
                  .pivot(index="month", columns="cust_type", values="revenue")
                  .fillna(0).reset_index().sort_values("month"))
    fig = go.Figure()
    for col, color in [("New", _ACCENT), ("Returning", _GREEN)]:
        if col in monthly.columns:
            fig.add_trace(go.Bar(
                x=monthly["month"], y=monthly[col], name=col,
                marker_color=color,
                hovertemplate=f"<b>%{{x}}</b><br>{col}: ₹%{{y:,.0f}}<extra></extra>",
            ))
    fig.update_layout(**_LAYOUT, **_GRID, height=260, barmode="stack",
                      legend=dict(orientation="h", x=1, xanchor="right", y=1.12,
                                  font=dict(color="#374151",size=10), bgcolor="rgba(0,0,0,0)"))
    fig.update_layout(showlegend=True)
    fig.update_xaxes(tickangle=-25, tickfont=dict(size=10))
    return fig

def chart_carrier_sla(df: pd.DataFrame) -> go.Figure:
    if "carrier" not in df.columns:
        return go.Figure()
    carr = (df.groupby("carrier")["sla_breach"]
              .mean().reset_index()
              .rename(columns={"sla_breach":"breach_rate"})
              .assign(breach_rate=lambda x: (x["breach_rate"]*100).round(1))
              .sort_values("breach_rate"))
    colors = [_RED if v>30 else (_GOLD if v>15 else _GREEN) for v in carr["breach_rate"]]
    fig = go.Figure(go.Bar(
        x=carr["carrier"], y=carr["breach_rate"],
        marker_color=colors,
        text=carr["breach_rate"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside", textfont=dict(color="#374151", size=11),
        hovertemplate="<b>%{x}</b><br>SLA Breach: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(**_LAYOUT, **_GRID, height=240)
    return fig


def chart_return_reasons(df: pd.DataFrame) -> go.Figure:
    if "return_reason" not in df.columns:
        return go.Figure()
    reasons = (df[df["return_reason"].str.len() > 0]["return_reason"]
                 .value_counts().reset_index())
    reasons.columns = ["reason","count"]
    if reasons.empty:
        return go.Figure()
    fig = go.Figure(go.Pie(
        labels=reasons["reason"], values=reasons["count"], hole=0.55,
        marker=dict(colors=[_RED,_GOLD,_PURPLE,_ACCENT,_GREEN,"#0891b2"],
                    line=dict(color="#ffffff", width=2)),
        textinfo="percent", textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>%{value} orders (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11),
        margin=dict(l=0,r=8,t=10,b=55), showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.45,
                    xanchor="center", x=0.5,
                    font=dict(color="#374151",size=10), bgcolor="rgba(0,0,0,0)"),
        height=290,
    )
    return fig


def chart_discount_impact(df: pd.DataFrame) -> go.Figure:
    if "discount_amount" not in df.columns:
        return go.Figure()
    monthly = (df.groupby("month")
                 .agg(revenue=("revenue","sum"), discounts=("discount_amount","sum"))
                 .assign(gross=lambda x: x["revenue"] + x["discounts"])
                 .tail(12).reset_index().sort_values("month"))
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["month"], y=monthly["gross"], name="Gross Revenue",
        marker_color=_ACCENT, opacity=0.35,
        hovertemplate="<b>%{x}</b><br>Gross: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=monthly["month"], y=monthly["revenue"], name="Net Revenue",
        marker_color=_ACCENT,
        hovertemplate="<b>%{x}</b><br>Net: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_LAYOUT, **_GRID, height=240, barmode="overlay",
                      legend=dict(orientation="h", x=1, xanchor="right", y=1.12,
                                  font=dict(color="#374151",size=10), bgcolor="rgba(0,0,0,0)"))
    fig.update_layout(showlegend=True)
    fig.update_xaxes(tickangle=-25, tickfont=dict(size=10))
    return fig


def chart_segment_revenue(df: pd.DataFrame) -> go.Figure:
    if "customer_segment" not in df.columns:
        return go.Figure()
    seg = (df.groupby("customer_segment")["revenue"]
             .sum().reset_index()
             .sort_values("revenue", ascending=False))
    seg_colors = {"Loyal":_GREEN,"Returning":_ACCENT,"New":_GOLD,"At-Risk":_RED}
    colors = [seg_colors.get(s, _ACCENT) for s in seg["customer_segment"]]
    fig = go.Figure(go.Bar(
        x=seg["customer_segment"], y=seg["revenue"],
        marker_color=colors,
        text=seg["revenue"].apply(lambda v: f"₹{v/1000:.0f}K"),
        textposition="outside", textfont=dict(color="#374151", size=11),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_LAYOUT, **_GRID, height=240)
    return fig
def _build_context(kpis: dict, prod_df: pd.DataFrame, city_df: pd.DataFrame) -> str:
    top3p    = prod_df.head(3)["product_name"].tolist()
    top3c    = city_df.head(3)["city"].tolist()
    mom_sign = "+" if kpis["mom_growth"] >= 0 else ""

    gm_line   = (f"Gross Margin %       : {kpis['gross_margin_pct']:.1f}%"
                 if kpis.get("gross_margin_pct") is not None else
                 "Gross Margin %       : N/A (no cogs column)")
    rpt_line  = (f"Repeat Purchase Rate : {kpis['repeat_rate']:.1f}%"
                 if kpis.get("repeat_rate") is not None else
                 "Repeat Purchase Rate : N/A (no customer_id column)")
    ltv_line  = (f"Avg Customer LTV     : ₹{kpis['ltv']:,.0f}"
                 if kpis.get("ltv") is not None else
                 "Avg Customer LTV     : N/A")
    disc_line = (f"Revenue Lost (Disc.) : ₹{kpis['revenue_lost_disc']:,.0f}"
                 if kpis.get("revenue_lost_disc") is not None else
                 "Revenue Lost (Disc.) : N/A")

    return textwrap.dedent(f"""
        E-Commerce Executive Dashboard Summary
        ───────────────────────────────────────
        Total Revenue        : ₹{kpis['revenue']:,.2f}
        Total Orders         : {kpis['orders']:,}
        Avg Order Value      : ₹{kpis['aov']:,.2f}
        Units Sold           : {kpis['quantity']:,}
        MoM Revenue Growth   : {mom_sign}{kpis['mom_growth']:.1f}%
        QoQ Revenue Growth   : {kpis['qoq_growth']:+.1f}%
        {gm_line}
        {rpt_line}
        {ltv_line}
        {disc_line}
        Perfect Order Rate   : {kpis['perfect_order_rate']:.1f}%
        Refund Rate          : {kpis['refund_rate']:.1f}%
        Cancellation Rate    : {kpis['cancel_rate']:.1f}%
        Delay Rate           : {kpis['delay_rate']:.1f}%
        SLA Breach Rate      : {kpis['sla_breach_rate']:.1f}%
        Avg Ship Days        : {kpis['avg_ship_days']:.1f}
        Revenue Concentration: {kpis['rev_concentration']:.1f}% (top 3 products)
        Revenue at Risk      : ₹{kpis['at_risk_revenue']:,.0f} (in-flight orders)
        Business Health Score: {kpis['health_score']}/100
        Top 3 Products       : {', '.join(top3p)}
        Top 3 Cities         : {', '.join(top3c)}
    """).strip()


def fallback_insights(kpis: dict, prod_df: pd.DataFrame, city_df: pd.DataFrame) -> list[str]:
    """Rule-based C-suite insights — no API key needed."""
    top_prod = prod_df.iloc[0]["product_name"] if len(prod_df) else "top product"
    top_city = city_df.iloc[0]["city"]          if len(city_df) else "top city"
    low_city = city_df.iloc[-1]["city"]         if len(city_df) else "bottom city"
    mom      = kpis["mom_growth"]

    insights = [
        # Growth signal
        (f"Revenue {'grew' if mom >= 0 else 'declined'} {abs(mom):.1f}% MoM — "
         + (f"momentum is positive; accelerate paid acquisition to compound gains."
            if mom >= 0 else f"immediate attention needed: diagnose demand drop vs. supply issue.")),
        # Perfect order rate
        (f"Perfect Order Rate of {kpis['perfect_order_rate']:.1f}% "
         + ("exceeds industry benchmark — use as a competitive differentiator in marketing."
            if kpis["perfect_order_rate"] >= 75
            else f"is below the 75% benchmark — logistics and QC improvements will directly lift NPS.")),
        # Revenue concentration risk
        (f"Top-3 products drive {kpis['rev_concentration']:.1f}% of revenue — "
         + ("high concentration risk; prioritise SKU diversification to reduce single-product dependency."
            if kpis["rev_concentration"] > 60
            else "healthy diversification; invest in the next tier of products to grow the long tail.")),
        # Geographic opportunity
        (f"{top_city} leads revenue; {low_city} is underperforming — "
         f"replicating {top_city}'s promo and fulfilment model could unlock ₹{kpis['revenue']*0.08:,.0f}+ incremental revenue."),
        # Revenue at risk
        (f"₹{kpis['at_risk_revenue']:,.0f} is in-flight (processing/shipped) — "
         + ("monitor closely given elevated refund rate; proactive comms reduce returns."
            if kpis["refund_rate"] > 5
            else "low refund rate suggests strong fulfilment; safe to accelerate shipping SLAs.")),
    ]
    return insights

def get_ai_insights(context: str, api_key: str) -> list[str]:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    system = (
        "You are a Chief Revenue Officer advising a board of directors.\n"
        "Given this e-commerce performance summary, produce exactly 6 sharp, board-ready insights.\n"
        "Rules:\n"
        "- Return ONLY a valid JSON array of 6 strings. No markdown fences, no preamble.\n"
        "- Each string is one insight (max 40 words). Lead with the metric, then the implication, then the action.\n"
        "- Cover: revenue momentum, operational risk, customer economics, market concentration, "
        "  logistics efficiency, and one forward-looking strategic recommendation.\n"
        "- Quantify every insight — reference the actual numbers.\n"
        "- Tone: direct, data-driven, board-appropriate. No fluff.\n"
        'Example: ["Revenue grew X% MoM driven by Y — sustain by Z.", ...]'
    )
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=800,
        system=system,
        messages=[{"role": "user", "content": context}],
    )
    raw = msg.content[0].text.strip().replace("```json","").replace("```","").strip()
    return json.loads(raw)


def get_ai_insights_openai(context: str, api_key: str) -> list[str]:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    system = (
        "You are a Chief Revenue Officer advising a board of directors.\n"
        "Given this e-commerce performance summary, produce exactly 6 sharp, board-ready insights.\n"
        "Rules:\n"
        "- Return ONLY a valid JSON array of 6 strings. No markdown fences, no preamble.\n"
        "- Each string is one insight (max 40 words). Lead with the metric, then the implication, then the action.\n"
        "- Cover: revenue momentum, operational risk, customer economics, market concentration, "
        "  logistics efficiency, and one forward-looking strategic recommendation.\n"
        "- Quantify every insight — reference the actual numbers.\n"
        "- Tone: direct, data-driven, board-appropriate. No fluff.\n"
        'Example: ["Revenue grew X% MoM driven by Y — sustain by Z.", ...]'
    )
    response = client.chat.completions.create(
        model="gpt-4o", max_tokens=800,
        messages=[{"role": "system", "content": system},
                  {"role": "user",   "content": context}],
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json","").replace("```","").strip()
    return json.loads(raw)


def _chat_with_openai(messages: list, system: str, api_key: str):
    """
    Calls OpenAI ChatGPT with the full conversation history and yields
    text chunks for streaming display.
    """
    from openai import OpenAI

    client   = OpenAI(api_key=api_key)
    oai_msgs = [{"role": "system", "content": system}] + messages

    stream = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=oai_msgs,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# ══════════════════════════════════════════════════════════════════
# §8  REUSABLE UI COMPONENTS
# ══════════════════════════════════════════════════════════════════
def render_header(data_source_label: str = "", page: str = ""):
    ds_html = f'<div class="ds-badge">📡 {data_source_label}</div>' if data_source_label else ""
    # Map page radio label to a short readable name
    page_names = {
        "Summary":    "Executive Summary",
        "Revenue":    "Revenue",
        "Operations": "Operations",
        "Profitability": "Profitability",
        "AI Insights":"AI Insights",
        "Ask":        "Ask the Data",
    }
    page_label = next((v for k, v in page_names.items() if k in page), "")
    # breadcrumb = (
    #     f'<div class="page-context">ECOM Intelligence &nbsp;›&nbsp; <span>{page_label}</span></div>'
    #     if page_label else
    #     '<div class="page-context">ECOM Intelligence</div>'
    # )
    breadcrumb = (
        f'<div class="page-context"><span>{page_label}</span></div>'
        if page_label else ''
    )
    st.markdown(f"""
    <div class="top-header">
        <div>
            <div class="logo">📊 <span>Electronic</span> Commerce Intelligence</div>
            {breadcrumb}
        </div>
        <div class="header-right">
            {ds_html}
            <div class="badge">LIVE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def chart_card(title: str, dot_class: str = "dot"):
    """
    Context manager replacement for the broken HTML-div-wrapping-chart pattern.
    Usage:
        with chart_card("TITLE"):
            st.plotly_chart(fig, use_container_width=True)
    """
    import contextlib

    @contextlib.contextmanager
    def _card():
        st.markdown(f"""
        <div class="section-card" style="padding:18px 20px 4px;">
            <div class="section-title">
                <span class="{dot_class}"></span>{title}
            </div>
        </div>""", unsafe_allow_html=True)
        # Streamlit renders widgets AFTER html — use a container to co-locate
        with st.container():
            yield

    return _card()


def render_kpis(kpis: dict):
    """5-card executive KPI strip with real computed deltas."""
    mom   = kpis["mom_growth"]
    qoq   = kpis["qoq_growth"]
    health = kpis["health_score"]

    mom_cls  = "pos" if mom  >= 0 else "neg"
    qoq_cls  = "pos" if qoq  >= 0 else "neg"
    h_color  = "green" if health >= 75 else ("gold" if health >= 50 else "red")
    h_cls    = "pos" if health >= 75 else ("neu" if health >= 50 else "neg")

    cards = [
        ("blue",   "TOTAL REVENUE",        f"₹{kpis['revenue']/1e6:.2f}M",
         f"{mom:+.1f}% MoM", mom_cls,      "₹" + f"{kpis['revenue']:,.0f}", "💰"),
        ("gold",   "AVG ORDER VALUE",       f"₹{kpis['aov']:,.0f}",
         f"{qoq:+.1f}% QoQ", qoq_cls,     f"{kpis['orders']:,} orders", "🎯"),
        ("green",  "PERFECT ORDER RATE",    f"{kpis['perfect_order_rate']:.1f}%",
         "Delivered on time, no return", "pos" if kpis["perfect_order_rate"]>=75 else "neg",
         "Target: 75%+", "✅"),
        ("red",    "REVENUE AT RISK",       f"₹{kpis['at_risk_revenue']/1000:.0f}K",
         f"{kpis['refund_rate']:.1f}% refund rate",
         "neg" if kpis["refund_rate"]>5 else "pos",
         "In-flight orders", "⚠️"),
        (h_color,  "BUSINESS HEALTH",       f"{health:.0f}",
         "out of 100", h_cls,
         "Composite score", "🏥"),
    ]
    html = '<div class="kpi-grid">'
    for color, label, val, delta, dcls, sub, icon in cards:
        html += f"""
        <div class="kpi-card {color}">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-delta {dcls}">{delta}</div>
            <div class="kpi-sub">{sub}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_exec_alerts(kpis: dict):
    """Surface the top 3 most critical flags for the executive."""
    alerts = []
    if kpis["mom_growth"] < -5:
        alerts.append(("danger", f"⚠️ Revenue declined {kpis['mom_growth']:.1f}% MoM — immediate investigation required."))
    if kpis["refund_rate"] > 8:
        alerts.append(("danger", f"⚠️ Refund rate at {kpis['refund_rate']:.1f}% — exceeds 8% threshold. QC review needed."))
    if kpis["cancel_rate"] > 5:
        alerts.append(("warn", f"🟡 Cancellation rate {kpis['cancel_rate']:.1f}% — review checkout and stock availability."))
    if kpis["perfect_order_rate"] < 60:
        alerts.append(("warn", f"🟡 Perfect Order Rate {kpis['perfect_order_rate']:.1f}% is below 60% — logistics SLA review needed."))
    if kpis["rev_concentration"] > 70:
        alerts.append(("warn", f"🟡 Top-3 SKUs = {kpis['rev_concentration']:.1f}% of revenue — high concentration risk."))
    if kpis["mom_growth"] > 10:
        alerts.append(("good", f"✅ Strong MoM growth of {kpis['mom_growth']:+.1f}% — ensure supply chain can sustain demand."))

    if alerts:
        for kind, msg in alerts[:3]:
            css = {"danger":"exec-alert","warn":"exec-alert warn","good":"exec-alert good"}.get(kind,"exec-alert")
            st.markdown(f'<div class="{css}">{msg}</div>', unsafe_allow_html=True)


def render_secondary_kpis(kpis: dict):
    cols = st.columns(4)
    metrics = [
        ("UNITS SOLD",        f"{kpis['quantity']:,}",
         f"{kpis['quantity']//kpis['orders'] if kpis['orders'] else 0} units/order avg"),
        ("DELAY RATE",        f"{kpis['delay_rate']:.1f}%",
         "🔴 Action needed" if kpis["delay_rate"]>20 else "🟢 On track"),
        ("CANCELLATION RATE", f"{kpis['cancel_rate']:.1f}%",
         "🔴 Elevated" if kpis["cancel_rate"]>5 else "🟢 Normal"),
        ("AVG SHIP DAYS",     f"{kpis['avg_ship_days']:.1f}d",
         "🔴 Slow" if kpis["avg_ship_days"]>8 else "🟢 Fast"),
    ]
    for col, (label, val, status) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="ops-card">
                <div class="kpi-label">{label}</div>
                <div class="ops-value">{val}</div>
                <div class="ops-status">{status}</div>
            </div>""", unsafe_allow_html=True)


def render_top_products_table(prod_df: pd.DataFrame, total_rev: float):
    rows = ""
    for i, row in prod_df.iterrows():
        ret_pct   = (row["returns"] / row["orders"] * 100) if row["orders"] else 0
        rev_share = (row["revenue"] / total_rev * 100) if total_rev else 0
        pcls = "pill-red" if ret_pct > 10 else "pill-green"
        scls = "pill-amber" if rev_share > 20 else "pill-blue"
        rows += f"""<tr>
            <td><span class="rank-badge">#{i+1}</span></td>
            <td><b>{row['product_name']}</b></td>
            <td>₹{row['revenue']/1000:.0f}K</td>
            <td><span class="pill {scls}">{rev_share:.1f}%</span></td>
            <td>{int(row['orders'])}</td>
            <td>{int(row['quantity'])}</td>
            <td>₹{row['avg_price']:.0f}</td>
            <td><span class="pill {pcls}">{ret_pct:.1f}%</span></td>
        </tr>"""
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title"><span class="dot"></span>PRODUCT REVENUE SCORECARD</div>
        <table class="styled-table">
            <thead><tr>
                <th>#</th><th>Product</th><th>Revenue</th><th>Rev Share</th>
                <th>Orders</th><th>Units</th><th>Avg Price</th><th>Return Rate</th>
            </tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>""", unsafe_allow_html=True)


def render_insights(insights: list[str], source_label: str = "AI"):
    st.markdown(f"""
    <div class="section-title" style="margin-bottom:12px;">
        <span class="dot"></span>BOARD-READY INTELLIGENCE
        &nbsp;<span class="pill pill-blue">{source_label}</span>
    </div>""", unsafe_allow_html=True)
    for i, text in enumerate(insights, 1):
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-text">
                <span class="insight-num">0{i}</span>{text}
            </div>
        </div>""", unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <div class="footer">
        Electronic Commerce Intelligence &nbsp;·&nbsp;
        &nbsp;|&nbsp; © 2025
    </div>""", unsafe_allow_html=True)


def alert(msg: str, kind: str = "info"):
    cls = {"info":"info-box","warn":"warn-box","error":"error-box","success":"success-box"}.get(kind,"info-box")
    st.markdown(f'<div class="{cls}">{msg}</div>', unsafe_allow_html=True)


def _section(title: str, dot: str = "dot"):
    """Renders a section-card header. Charts go immediately after via st.container()."""
    st.markdown(f"""
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;
                padding:18px 20px 0 20px;margin-bottom:0;
                box-shadow:0 1px 3px rgba(0,0,0,0.06);">
        <div style="font-size:.6rem;font-weight:700;letter-spacing:1.2px;
                    text-transform:uppercase;color:#64748b;
                    margin-bottom:10px;display:flex;align-items:center;gap:8px;">
            <span class="{dot}"></span>{title}
        </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# §9  PAGE RENDERERS
# ══════════════════════════════════════════════════════════════════
def page_overview(df, kpis, prod_df, city_df):
    """Executive Summary — the one page a CEO looks at every morning."""
    render_exec_alerts(kpis)
    render_kpis(kpis)
    render_secondary_kpis(kpis)

    c1, c2 = st.columns([3, 1], gap="medium")
    with c1:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● REVENUE TREND WITH ORDER VOLUME</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_revenue_trend(revenue_trend(df,"M"), show_orders=True), use_container_width=True)
    with c2:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● PERFECT ORDER RATE</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_perfect_order_gauge(kpis["perfect_order_rate"]), use_container_width=True)
            st.markdown(f'<p style="text-align:center;font-size:.68rem;color:#94a3b8;margin-top:-8px;">Industry benchmark: 75%+</p>', unsafe_allow_html=True)

    c3, c4 = st.columns([1, 1], gap="medium")
    with c3:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● REVENUE BY MARKET</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_city_bar(city_df), use_container_width=True)
    with c4:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● REVENUE BY CATEGORY</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_revenue_by_category(df), use_container_width=True)

    render_top_products_table(prod_df, kpis["revenue"])


def page_revenue(df, kpis, prod_df, city_df):
    """Revenue deep-dive — growth, AOV trends, mix, concentration."""
    render_kpis(kpis)

    c1, c2 = st.columns([1, 1], gap="medium")
    with c1:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● MONTHLY REVENUE (LAST 6 MONTHS)</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_mom_waterfall(revenue_trend(df,"M")), use_container_width=True)
    with c2:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● AVG ORDER VALUE TREND</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_aov_trend(df), use_container_width=True)

    conc = kpis["rev_concentration"]
    conc_cls = "error-box" if conc > 70 else ("warn-box" if conc > 50 else "success-box")
    conc_msg = (f"🔴 <b>High concentration risk:</b> Top-3 SKUs = {conc:.1f}% of revenue — diversification needed"
                if conc > 70 else
                f"🟡 <b>Moderate concentration:</b> Top-3 SKUs = {conc:.1f}% of revenue — monitor closely"
                if conc > 50 else
                f"✅ <b>Well-diversified:</b> Top-3 SKUs = {conc:.1f}% of revenue")
    st.markdown(f'<div class="{conc_cls}">{conc_msg}</div>', unsafe_allow_html=True)

    c3, c4 = st.columns([2, 1], gap="medium")
    with c3:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● REVENUE MIX — CATEGORY & PRODUCT</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_category_treemap(df), use_container_width=True)
    with c4:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● ORDER STATUS SPLIT</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_status_bar(df), use_container_width=True)

    render_top_products_table(prod_df, kpis["revenue"])


def page_operations(df, kpis, city_df):
    """Operations page — logistics health, delays, shipping bands."""
    render_secondary_kpis(kpis)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    metrics = [
        ("PERFECT ORDER RATE", f"{kpis['perfect_order_rate']:.1f}%",
         "🟢 Best-in-class" if kpis["perfect_order_rate"]>=75 else "🔴 Below 75% benchmark"),
        ("ON-TIME DELIVERY",   f"{100-kpis['delay_rate']:.1f}%",
         "Orders delivered within 7-day SLA"),
        ("CANCELLATION RATE",  f"{kpis['cancel_rate']:.1f}%",
         "🟢 Normal (≤5%)" if kpis["cancel_rate"]<=5 else "🔴 Elevated — review checkout"),
    ]
    for col, (lbl, val, sub) in zip([c1,c2,c3], metrics):
        with col:
            st.markdown(f"""
            <div class="ops-card">
                <div class="kpi-label">{lbl}</div>
                <div class="ops-value">{val}</div>
                <div class="ops-status">{sub}</div>
            </div>""", unsafe_allow_html=True)

    c4, c5 = st.columns([2, 1], gap="medium")
    with c4:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● DELAY RATE — CITY × MONTH HEATMAP</p>', unsafe_allow_html=True)
            try:
                st.plotly_chart(chart_delay_heatmap(df), use_container_width=True)
            except Exception:
                st.info("Insufficient monthly data for heatmap.")
    with c5:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● SHIPPING SPEED BANDS</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_shipping_donut(shipping_summary(df)), use_container_width=True)

    with st.container(border=True):
        st.markdown('<p class="chart-label">● DELAY RATE BY MARKET</p>', unsafe_allow_html=True)
        cd = city_df[["city","delay_rate"]].sort_values("delay_rate")
        delay_colors = [_RED if v > 25 else (_GOLD if v > 15 else _GREEN) for v in cd["delay_rate"]]
        fig = go.Figure(go.Bar(
            y=cd["city"], x=cd["delay_rate"], orientation="h",
            marker_color=delay_colors,
            text=cd["delay_rate"].apply(lambda v: f"{v:.1f}%"),
            textposition="outside", textfont=dict(color="#374151", size=11),
            hovertemplate="<b>%{y}</b><br>Delay rate: %{x:.1f}%<extra></extra>",
        ))
        fig.update_layout(**_LAYOUT, height=280,
                          yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
                          xaxis=dict(gridcolor="#f1f5f9"))
        st.plotly_chart(fig, use_container_width=True)


def page_profitability(df, kpis, prod_df, city_df):
    """CFO view — margin, discounts, channel economics, customer retention."""

    # ── Top KPI strip ────────────────────────────────────────────
    cols = st.columns(4)
    margin_val = (f"{kpis['gross_margin_pct']:.1f}%"
                  if kpis.get("gross_margin_pct") is not None else "N/A")
    repeat_val = (f"{kpis['repeat_rate']:.1f}%"
                  if kpis.get("repeat_rate") is not None else "N/A")
    ltv_val    = (f"₹{kpis['ltv']:,.0f}"
                  if kpis.get("ltv") is not None else "N/A")
    disc_val   = (f"₹{kpis['revenue_lost_disc']/1000:.0f}K"
                  if kpis.get("revenue_lost_disc") is not None else "N/A")
    disc_sub   = (f"{kpis.get('discount_rate',0):.1f}% orders discounted"
                  if kpis.get("discount_rate") is not None else "No discount data")

    strip = [
        ("green",  "GROSS MARGIN",         margin_val, "Target: 45%+"),
        ("blue",   "CUSTOMER REPEAT RATE", repeat_val, "% with 2+ orders"),
        ("purple", "AVG CUSTOMER LTV",     ltv_val,    "Revenue / unique customer"),
        ("red",    "REVENUE LOST TO DISC", disc_val,   disc_sub),
    ]
    for col, (color, lbl, val, sub) in zip(cols, strip):
        with col:
            st.markdown(f"""
            <div class="kpi-card {color}" style="margin-bottom:16px;">
                <div class="kpi-label">{lbl}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # ── Row 1: Gross margin by category + Channel revenue ─────────
    c1, c2 = st.columns([1,1], gap="medium")
    with c1:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● GROSS MARGIN % BY CATEGORY</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_margin_by_category(df), use_container_width=True)
    with c2:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● REVENUE BY ACQUISITION CHANNEL</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_channel_revenue(df), use_container_width=True)

    # ── Row 2: New vs Returning + Discount impact ─────────────────
    c3, c4 = st.columns([1,1], gap="medium")
    with c3:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● NEW VS RETURNING CUSTOMER REVENUE</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_new_vs_returning(df), use_container_width=True)
    with c4:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● DISCOUNT IMPACT — GROSS VS NET REVENUE</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_discount_impact(df), use_container_width=True)

    # ── Row 3: Customer segment revenue + Return reasons ──────────
    c5, c6 = st.columns([1,1], gap="medium")
    with c5:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● REVENUE BY CUSTOMER SEGMENT</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_segment_revenue(df), use_container_width=True)
    with c6:
        with st.container(border=True):
            st.markdown('<p class="chart-label">● RETURN REASON BREAKDOWN</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_return_reasons(df), use_container_width=True)

    # ── Row 4: SLA breach by carrier ─────────────────────────────
    with st.container(border=True):
        st.markdown('<p class="chart-label">● SLA BREACH RATE BY CARRIER</p>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_carrier_sla(df), use_container_width=True)


def page_ai_insights(df, kpis, prod_df, city_df, api_key: str, ai_tool: str = "🟠 Claude (Anthropic)"):
    is_claude = "Claude" in ai_tool
    tool_name = "Claude AI" if is_claude else "ChatGPT"
    tool_note = "powered by Claude (Anthropic)" if is_claude else "powered by ChatGPT (OpenAI)"

    # ── API key status banner ─────────────────────────────────────
    if api_key:
        alert(f"🔑 <b>{tool_name} active</b> — Live AI insights are enabled.", "success")
    else:
        key_url  = "https://console.anthropic.com" if is_claude else "https://platform.openai.com/api-keys"
        key_hint = "ANTHROPIC_API_KEY=sk-ant-..." if is_claude else "OPENAI_API_KEY=sk-..."
        alert(
            f"⚠️ <b>No API key configured.</b> "
            f"Enter your key in the sidebar or add <code>{key_hint}</code> "
            f"to your <code>.env</code> file. Rule-based insights are being used as a fallback.",
            "warn",
        )

    st.markdown(f"""
    <div class="section-card" style="background:linear-gradient(135deg,#060e1e,#0d1117);border-color:#1e3a5f;margin-bottom:18px;">
        <div style="font-size:1.05rem;font-weight:700;margin-bottom:6px;color:#f0f4f8;">🤖 Board-Ready AI Analysis</div>
        <div style="color:#64748b;font-size:.85rem;line-height:1.6;">
            AI analyses your full dataset and generates 6 executive-grade insights covering
            revenue momentum, operational risk, market concentration, and strategic priorities — {tool_note}.
        </div>
    </div>""", unsafe_allow_html=True)

    context = _build_context(kpis, prod_df, city_df)

    col_btn, col_ctx = st.columns([1,4])
    with col_btn:
        gen = st.button("⚡ Generate Insights")
    with col_ctx:
        with st.expander("View data context sent to AI"):
            st.code(context, language="text")

    if gen or st.session_state.get("insights_generated"):
        st.session_state["insights_generated"] = True
        with st.spinner(f"Analysing your data with {tool_name}…"):
            if api_key:
                try:
                    if is_claude:
                        insights = get_ai_insights(context, api_key)
                    else:
                        insights = get_ai_insights_openai(context, api_key)
                    source = tool_name
                except Exception as e:
                    alert(f"⚠️ API error: {e} — falling back to rule-based insights.", "warn")
                    insights = fallback_insights(kpis, prod_df, city_df)
                    source   = "Rule-based"
            else:
                time.sleep(0.6)
                insights = fallback_insights(kpis, prod_df, city_df)
                source   = "Rule-based"

        render_insights(insights, source_label=source)

        # Delay analysis
        st.markdown("<br>", unsafe_allow_html=True)
        d1, d2 = st.columns(2, gap="medium")
        with d1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span class="dot"></span>DELAY RATE BY CITY</div>', unsafe_allow_html=True)
            cd = city_df[["city","delay_rate"]].sort_values("delay_rate")
            fig = px.bar(cd, x="delay_rate", y="city", orientation="h",
                         color="delay_rate",
                         color_continuous_scale=[[0,"#22c55e"],[.5,"#f5a623"],[1,"#ef4444"]],
                         text=cd["delay_rate"].apply(lambda v: f"{v:.1f}%"))
            fig.update_layout(**_LAYOUT, height=260)
            fig.update_traces(textposition="outside", textfont=dict(color="#e8edf5"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with d2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span class="dot"></span>SHIPPING BANDS</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_shipping_donut(shipping_summary(df)), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="upload-zone" style="padding:44px 20px;">
            <div style="font-size:2.5rem;margin-bottom:12px">⚡</div>
            <div class="upload-title" style="font-size:1.1rem">Ready to analyse</div>
            <div class="upload-sub">Click "Generate Insights" above to surface intelligence from your data.</div>
        </div>""", unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════════════
# §10b  ASK THE DATA — conversational Q&A against the dataset
# ══════════════════════════════════════════════════════════════════
def _build_data_summary(df: pd.DataFrame, kpis: dict,
                         prod_df: pd.DataFrame, city_df: pd.DataFrame) -> str:
    """
    Builds a rich text snapshot of the dataset that is injected as
    context into every chat message so Claude can answer accurately
    without needing direct dataframe access.
    """
    top_prods  = prod_df.head(5)[["product_name","revenue","orders"]].to_string(index=False)
    top_cities = city_df.head(5)[["city","revenue","orders","delay_rate"]].to_string(index=False)
    cat_rev    = (df.groupby("category")["revenue"]
                    .sum().sort_values(ascending=False)
                    .head(6).to_string())
    status_cnt = df["order_status"].value_counts().to_string()
    date_min   = df["order_date"].min().date()
    date_max   = df["order_date"].max().date()
    monthly    = (df.groupby("month")["revenue"]
                    .sum().tail(6).to_string())

    return f"""
You are a Chief Revenue Officer and data analytics advisor to C-suite executives.
Answer the user's question using ONLY the dataset summary below.
Be concise, quantitative, and board-appropriate. Lead with the number, then the implication.
If something cannot be determined from the data, say so clearly.

━━━━ DATASET SNAPSHOT ━━━━
Period          : {date_min} → {date_max}
Total rows      : {len(df):,}
Cities          : {df['city'].nunique()}
Products        : {df['product_name'].nunique()}
Categories      : {df['category'].nunique()}

━━━━ EXECUTIVE KPIs ━━━━
Total Revenue        : ₹{kpis['revenue']:,.2f}
Total Orders         : {kpis['orders']:,}
Avg Order Value      : ₹{kpis['aov']:,.2f}
Units Sold           : {kpis['quantity']:,}
MoM Revenue Growth   : {kpis['mom_growth']:+.1f}%
QoQ Revenue Growth   : {kpis['qoq_growth']:+.1f}%
Perfect Order Rate   : {kpis['perfect_order_rate']:.1f}%
Refund Rate          : {kpis['refund_rate']:.1f}%
Cancellation Rate    : {kpis['cancel_rate']:.1f}%
Delay Rate           : {kpis['delay_rate']:.1f}%
Avg Ship Days        : {kpis['avg_ship_days']:.1f}
Revenue Concentration: {kpis['rev_concentration']:.1f}% (top 3 SKUs)
Revenue at Risk      : ₹{kpis['at_risk_revenue']:,.0f}
Health Score         : {kpis['health_score']}/100

━━━━ TOP 5 PRODUCTS ━━━━
{top_prods}

━━━━ TOP 5 MARKETS ━━━━
{top_cities}

━━━━ REVENUE BY CATEGORY ━━━━
{cat_rev}

━━━━ ORDER STATUS BREAKDOWN ━━━━
{status_cnt}

━━━━ LAST 6 MONTHS REVENUE ━━━━
{monthly}
""".strip()


def _chat_with_claude(messages: list, system: str, api_key: str):
    """
    Calls Claude with the full conversation history and yields
    text chunks for streaming display.
    Raises on auth / API errors so the caller can surface them.
    """
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    with client.messages.stream(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=system,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


def page_ask_data(df: pd.DataFrame, kpis: dict,
                  prod_df: pd.DataFrame, city_df: pd.DataFrame,
                  api_key: str, ai_tool: str = "🟠 Claude (Anthropic)"):
    """Conversational Q&A — requires an API key."""
    is_claude = "Claude" in ai_tool
    tool_name = "Claude AI" if is_claude else "ChatGPT"
    avatar    = "⚡" if is_claude else "🤖"

    # ── No-API state: show static data summary instead of broken chat ──
    if not api_key:
        st.markdown("""
        <div class="section-card" style="background:#fffbeb;border-color:#fde68a;">
            <div style="font-size:1rem;font-weight:700;color:#92400e;margin-bottom:6px;">
                💬 Ask the Data — API Key Required
            </div>
            <div style="color:#78350f;font-size:.85rem;line-height:1.7;">
                This feature uses an AI model to answer plain-English questions about your data.
                Add your <b>Anthropic</b> or <b>OpenAI</b> API key in the sidebar to enable it.<br><br>
                <b>Without a key</b>, the AI Insights tab still works — it uses rule-based analysis
                to surface the most important findings automatically.
            </div>
        </div>""", unsafe_allow_html=True)

        # Show a useful static summary instead
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"><span class="dot"></span>DATA SNAPSHOT — KEY FACTS AT A GLANCE</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **Revenue & Orders**
            - Total revenue: ₹{kpis['revenue']:,.0f}
            - Total orders: {kpis['orders']:,}
            - Avg order value: ₹{kpis['aov']:,.0f}
            - MoM growth: {kpis['mom_growth']:+.1f}%

            **Top 3 Products**
            """)
            for i, row in prod_df.head(3).iterrows():
                st.markdown(f"- **{row['product_name']}** — ₹{row['revenue']/1000:.0f}K")
        with col2:
            st.markdown(f"""
            **Operations**
            - Perfect order rate: {kpis['perfect_order_rate']:.1f}%
            - Delay rate: {kpis['delay_rate']:.1f}%
            - Refund rate: {kpis['refund_rate']:.1f}%
            - Avg ship days: {kpis['avg_ship_days']:.1f}

            **Top 3 Markets**
            """)
            for i, row in city_df.head(3).iterrows():
                st.markdown(f"- **{row['city']}** — ₹{row['revenue']/1000:.0f}K")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── Page header ──────────────────────────────────────────────
    st.markdown(f"""
    <div class="section-card" style="background:#eff6ff;border-color:#bfdbfe;margin-bottom:20px;">
        <div style="font-size:1rem;font-weight:700;color:#1e40af;margin-bottom:6px;">
            💬 Ask the Data
        </div>
        <div style="color:#1e3a8a;font-size:.85rem;line-height:1.6;">
            Ask any question about your dataset in plain English.
            {tool_name} has full context of your metrics, products, cities, and order history.
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Session state init ───────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    system_prompt = _build_data_summary(df, kpis, prod_df, city_df)

    # ── Top controls ─────────────────────────────────────────────
    col_title, col_clear = st.columns([5, 1])
    with col_clear:
        if st.button("🗑️ Clear", key="clear_chat"):
            st.session_state["chat_history"] = []
            st.rerun()

    # ── Suggested questions (shown when chat is empty) ────────────
    if not st.session_state["chat_history"]:
        st.markdown(
            '<div style="font-size:.78rem;color:#4f617a;margin-bottom:8px;">'
            'Try asking:</div>',
            unsafe_allow_html=True,
        )
        suggestions = [
            "What is driving our MoM revenue change?",
            "Which market has the worst perfect order rate?",
            "What is our revenue concentration risk?",
            "Where are we losing the most revenue to refunds?",
            "Which category should we double down on?",
            "What is our revenue at risk this month?",
        ]
        cols = st.columns(3)
        for i, s in enumerate(suggestions):
            with cols[i % 3]:
                st.markdown('<div class="suggested-btn">', unsafe_allow_html=True)
                if st.button(s, key=f"sug_{i}"):
                    st.session_state["chat_history"].append(
                        {"role": "user", "content": s}
                    )
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # ── Chat history display ──────────────────────────────────────
    if st.session_state["chat_history"]:
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        for msg in st.session_state["chat_history"]:
            role    = msg["role"]
            content = msg["content"]
            is_user = role == "user"

            avatar_cls  = "user" if is_user else "claude"
            bubble_cls  = "user" if is_user else "claude"
            row_cls     = "user" if is_user else ""
            avatar_icon = "U" if is_user else avatar
            meta_cls    = "user" if is_user else ""
            meta_label  = "You" if is_user else f" AI ({tool_name})"

            st.markdown(f"""
            <div class="bubble-row {row_cls}">
                <div class="avatar {avatar_cls}">{avatar_icon}</div>
                <div class="bubble {bubble_cls}">{content}</div>
            </div>
            <div class="chat-meta {meta_cls}">{meta_label}</div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Handle pending user message (stream response) ─────────────
    history = st.session_state["chat_history"]
    last    = history[-1] if history else None

    if last and last["role"] == "user":
        # Stream the reply from the selected AI tool
        with st.chat_message("assistant", avatar=avatar):
            response_placeholder = st.empty()
            full_response = ""
            try:
                stream_fn = (
                    _chat_with_claude if is_claude else _chat_with_openai
                )
                for chunk in stream_fn(history, system_prompt, api_key):
                    full_response += chunk
                    response_placeholder.markdown(
                        f'<div class="bubble claude" style="max-width:100%">'
                        f'{full_response}▌</div>',
                        unsafe_allow_html=True,
                    )
                # Final render without cursor
                response_placeholder.markdown(
                    f'<div class="bubble claude" style="max-width:100%">'
                    f'{full_response}</div>',
                    unsafe_allow_html=True,
                )
                st.session_state["chat_history"].append(
                    {"role": "assistant", "content": full_response}
                )
            except Exception as e:
                err = f"⚠️ API error: {e}"
                response_placeholder.markdown(
                    f'<div class="bubble claude" style="max-width:100%;'
                    f'border-color:#ef4444;">{err}</div>',
                    unsafe_allow_html=True,
                )
                st.session_state["chat_history"].append(
                    {"role": "assistant", "content": err}
                )

    # ── Input box ────────────────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    user_input = st.chat_input(
        "Ask anything about your data… e.g. 'Which city has the lowest AOV?'",
    )
    if user_input and user_input.strip():
        st.session_state["chat_history"].append(
            {"role": "user", "content": user_input.strip()}
        )
        st.rerun()


# ══════════════════════════════════════════════════════════════════
# §11 SIDEBAR — nav + data source selector
# ══════════════════════════════════════════════════════════════════

# Maps display label → internal db_type string and default port
_DB_OPTIONS = {
    "🐘 PostgreSQL":  ("postgres",  "5432"),
    "🐬 MySQL":       ("mysql",     "3306"),
    "🖥️ SQL Server":  ("mssql",     "1433"),
    "🗄️ SQLite":      ("sqlite",    ""),
}

_SOURCE_OPTIONS = [
    "🎲 Sample Data",
    "📄 CSV Upload",
    "📊 Excel Upload",
    "─── Database ───",          # visual separator (non-selectable handled below)
    "🐘 PostgreSQL",
    "🐬 MySQL",
    "🖥️ SQL Server",
    "🗄️ SQLite",
]


def _db_form(env: dict, db_type: str, default_port: str):
    """
    Renders the database connection form fields.
    Returns (cfg_tuple, db_table, custom_sql).
    cfg_tuple is a hashable (db_type, host, port, name, user, pw, sqlite_path).
    """
    if db_type == "sqlite":
        db_path  = st.text_input("SQLite file path",
                                  value=env.get("DB_SQLITE_PATH",""),
                                  placeholder="/data/orders.db")
        db_table = st.text_input("Table / View",
                                  value=env.get("DB_TABLE","orders"),
                                  placeholder="orders")
        cfg_tuple = (db_type, "", "", "", "", "", db_path)
    else:
        col_h, col_p = st.columns([3, 1])
        db_host = col_h.text_input("Host",
                                    value=env.get("DB_HOST",""),
                                    placeholder="localhost")
        db_port = col_p.text_input("Port",
                                    value=env.get("DB_PORT", default_port))
        db_name = st.text_input("Database",
                                 value=env.get("DB_NAME",""),
                                 placeholder="ecommerce")
        db_user = st.text_input("Username",
                                 value=env.get("DB_USER",""),
                                 placeholder="sa" if db_type=="mssql" else "admin")
        db_pass = st.text_input("Password", type="password",
                                 value=env.get("DB_PASSWORD",""))
        db_table= st.text_input("Table / View",
                                 value=env.get("DB_TABLE","orders"),
                                 placeholder="dbo.orders" if db_type=="mssql" else "orders")
        cfg_tuple = (db_type, db_host, db_port, db_name, db_user, db_pass, "")

    custom_sql = st.text_area(
        "Custom SQL (optional)",
        value="",
        placeholder=f"SELECT * FROM {db_table} LIMIT 50000",
        height=70,
    )
    return cfg_tuple, db_table, custom_sql


def render_sidebar(env: dict) -> tuple:
    """
    Renders the full sidebar.
    Returns (page, df, data_source_label, api_key, warns, source).

    Changes vs previous version:
      • SQL Server added as a database option
      • API key is read ONLY from .env / st.secrets — no input box
      • Sidebar text forced to bright colours so it's always visible
    """
    with st.sidebar:
        # ── Branding ────────────────────────────────────────────
        st.markdown(
            '<div style="padding:4px 0 12px;">'
            '<span style="font-size:1.1rem;font-weight:700;color:#e8edf5;"> </span>'
            '<span style="font-size:.7rem;color:#4f617a;margin-left:6px;letter-spacing:.5px;"> </span>'
            '</div>',
            unsafe_allow_html=True,
        )

        # ── Navigation ─────────────────────────────────────────
        st.markdown("### Navigation")
        page = st.radio(
            "nav",
            ["📊  Executive Summary", "💰  Revenue", "🚚  Operations",
             "📈  Profitability", "🤖  AI Insights", "💬  Ask the Data"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # ── Data source selector ────────────────────────────────
        st.markdown("### Data Source")

        # Filter out the separator from actual options so Streamlit
        # doesn't error — we re-insert it as display-only text.
        real_options = [o for o in _SOURCE_OPTIONS if not o.startswith("─")]
        source = st.selectbox(
            "source",
            real_options,
            label_visibility="collapsed",
        )

        df       = pd.DataFrame()
        warns    = []
        data_lbl = ""

        # ── File uploads ─────────────────────────────────────────
        if source == "📄 CSV Upload":
            f = st.file_uploader("Upload CSV", type=["csv"],
                                  label_visibility="collapsed")
            if f:
                with st.spinner("Loading CSV…"):
                    df, warns = load_csv(f)
                data_lbl = f"CSV · {f.name}"
                # Clear mapping state when a new file is uploaded
                if st.session_state.get("_last_csv") != f.name:
                    st.session_state.pop(f"colmap_done_{f.name}", None)
                    st.session_state.pop(f"colmap_rename_{f.name}", None)
                    st.session_state["_last_csv"] = f.name
                df = render_column_mapper(df, f.name)

        elif source == "📊 Excel Upload":
            f = st.file_uploader("Upload Excel", type=["xlsx", "xls"],
                                  label_visibility="collapsed")
            if f:
                xl_sheets = pd.ExcelFile(f).sheet_names
                chosen    = st.selectbox("Sheet", xl_sheets)
                st.session_state["_chosen_sheet"] = chosen
                with st.spinner("Loading Excel…"):
                    df, warns = load_excel(f)
                data_lbl = f"Excel · {f.name} [{chosen}]"
                # Clear mapping state when a new file is uploaded
                file_key = f"{f.name}_{chosen}"
                if st.session_state.get("_last_excel") != file_key:
                    st.session_state.pop(f"colmap_done_{file_key}", None)
                    st.session_state.pop(f"colmap_rename_{file_key}", None)
                    st.session_state["_last_excel"] = file_key
                df = render_column_mapper(df, file_key)

        # ── Database connections ──────────────────────────────────
        elif source in _DB_OPTIONS:
            db_type, default_port = _DB_OPTIONS[source]

            # SQL Server requires pyodbc — show install hint
            if db_type == "mssql":
                st.markdown(
                    '<div style="font-size:.72rem;color:#f5a623;margin-bottom:8px;">'
                    '⚠️ Requires <code>pyodbc</code> + ODBC Driver 18.<br>'
                    'Run: <code>pip install pyodbc</code></div>',
                    unsafe_allow_html=True,
                )

            cfg_tuple, db_table, custom_sql = _db_form(env, db_type, default_port)

            connect_btn = st.button("🔌 Connect & Load")
            if connect_btn:
                table = db_table or "orders"
                query = custom_sql.strip() or build_db_query(table)
                with st.spinner(f"Connecting to {db_type.upper()}…"):
                    df, warns = load_from_db(cfg_tuple, query)
                if df.empty and warns:
                    st.session_state["db_error"] = warns
                    st.session_state.pop("db_df", None)
                else:
                    st.session_state["db_df"]    = df
                    st.session_state["db_warns"] = warns
                    st.session_state["db_label"] = f"{source} · {table}"
                    st.session_state.pop("db_error", None)

            # Restore cached connection on page switch
            if st.session_state.get("db_df") is not None and df.empty:
                df       = st.session_state["db_df"]
                warns    = st.session_state.get("db_warns", [])
                data_lbl = st.session_state.get("db_label", source)

            if "db_error" in st.session_state:
                for e in st.session_state["db_error"]:
                    st.error(e)

        else:
            # Sample data
            data_lbl = "Sample dataset · 5,000 orders (2020–2024)"

        # ── AI Tool selector ─────────────────────────────────────
        st.markdown("---")
        st.markdown("### AI Tool")
        ai_tool = st.radio(
            "ai_tool",
            ["🟠 Claude (Anthropic)", "🟢 ChatGPT (OpenAI)"],
            label_visibility="collapsed",
            key="ai_tool_selector",
        )

        if ai_tool == "🟠 Claude (Anthropic)":
            st.markdown(
                '<div style="font-size:.72rem;color:#8b9ab8;margin-bottom:4px;">'
                'Anthropic API Key</div>',
                unsafe_allow_html=True,
            )
            sidebar_key = st.text_input(
                "Anthropic API Key",
                type="password",
                value=env.get("ANTHROPIC_API_KEY", ""),
                placeholder="sk-ant-api03-…",
                label_visibility="collapsed",
                help="Used only for AI Insights. Never stored or logged.",
            )
            if env.get("ANTHROPIC_API_KEY"):
                st.markdown(
                    '<div style="font-size:.72rem;color:#22c55e;">✅ Key loaded from .env</div>',
                    unsafe_allow_html=True,
                )
            elif sidebar_key:
                st.markdown(
                    '<div style="font-size:.72rem;color:#f5a623;">🔑 Key set for this session</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="font-size:.72rem;color:#8b9ab8;">'
                    'No key — rule-based insights will be used.<br>'
                    '<a href="https://console.anthropic.com" target="_blank" '
                    'style="color:#60a5fa;text-decoration:none;">→ Get a free API key</a>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            api_key = env.get("ANTHROPIC_API_KEY") or sidebar_key

        else:  # ChatGPT
            st.markdown(
                '<div style="font-size:.72rem;color:#8b9ab8;margin-bottom:4px;">'
                'OpenAI API Key</div>',
                unsafe_allow_html=True,
            )
            sidebar_oai_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=env.get("OPENAI_API_KEY", ""),
                placeholder="sk-…",
                label_visibility="collapsed",
                help="Used only for AI Insights. Never stored or logged.",
            )
            if env.get("OPENAI_API_KEY"):
                st.markdown(
                    '<div style="font-size:.72rem;color:#22c55e;">✅ Key loaded from .env</div>',
                    unsafe_allow_html=True,
                )
            elif sidebar_oai_key:
                st.markdown(
                    '<div style="font-size:.72rem;color:#f5a623;">🔑 Key set for this session</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="font-size:.72rem;color:#8b9ab8;">'
                    'No key — rule-based insights will be used.<br>'
                    '<a href="https://platform.openai.com/api-keys" target="_blank" '
                    'style="color:#60a5fa;text-decoration:none;">→ Get an OpenAI API key</a>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            api_key = env.get("OPENAI_API_KEY") or sidebar_oai_key

        # ── Schema hint ──────────────────────────────────────────
        st.markdown("---")
        with st.expander("📋 Expected schema"):
            st.markdown(
                '<div style="font-size:.72rem;color:#FFFFFF;line-height:2;">'
                '<b style="color:#FFFFFF;">Column</b> · Type<br>'
                'order_id · string<br>'
                'order_date · date<br>'
                'product_name · string<br>'
                'category · string<br>'
                'quantity · int<br>'
                'unit_price · float<br>'
                'revenue · float<br>'
                'city · string<br>'
                'order_status · string<br>'
                'shipping_days · int'
                '</div>',
                unsafe_allow_html=True,
            )

    return page, df, data_lbl, api_key, warns, source, ai_tool


# ══════════════════════════════════════════════════════════════════
# §11 MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════
def main():
    inject_styles()

    # Load env config once per session
    if "env" not in st.session_state:
        st.session_state["env"] = load_env_config()
    env = st.session_state["env"]

    # Sidebar handles source selection + nav
    page, df_raw, data_lbl, api_key, warns, source, ai_tool = render_sidebar(env)

    # ── Resolve data ────────────────────────────────────────────
    if df_raw.empty:
        # Try DB cache (persists across page switches without re-connecting)
        if "db_df" in st.session_state and source not in ("📄 CSV Upload","📊 Excel Upload"):
            df_raw   = st.session_state["db_df"]
            data_lbl = st.session_state.get("db_label","Database")
            warns    = st.session_state.get("db_warns",[])

    if df_raw.empty:
        df_raw   = generate_sample_data()
        data_lbl = "Sample dataset · 5,000 orders (2020–2024)"

    # ── Show warnings ────────────────────────────────────────────
    for w in warns:
        st.warning(w)

    # ── Process & compute ────────────────────────────────────────
    df      = process(df_raw)
    kpis    = compute_kpis(df)
    prod_df = top_products(df)
    city_df = city_performance(df)

    # ── Header (after sidebar so data_lbl is known) ───────────────
    render_header(data_source_label=data_lbl, page=page)

    # ── Meta strip ──────────────────────────────────────────────
    st.markdown(
        f'<div style="padding:10px 2px 14px;font-size:0.75rem;color:#9ca3af;">'
        f'<span style="color:#374151;font-weight:600;">{len(df):,} records</span>'
        f'&nbsp; · &nbsp;{df["order_date"].min().date()} – {df["order_date"].max().date()}'
        f'&nbsp; · &nbsp;{df["city"].nunique()} markets'
        f'&nbsp; · &nbsp;{df["product_name"].nunique()} products'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Route pages ──────────────────────────────────────────────
    if "Summary" in page:
        page_overview(df, kpis, prod_df, city_df)
    elif "Revenue" in page:
        page_revenue(df, kpis, prod_df, city_df)
    elif "Operations" in page:
        page_operations(df, kpis, city_df)
    elif "Profitability" in page:
        page_profitability(df, kpis, prod_df, city_df)
    elif "AI Insights" in page:
        page_ai_insights(df, kpis, prod_df, city_df, api_key, ai_tool)
    elif "Ask the Data" in page:
        page_ask_data(df, kpis, prod_df, city_df, api_key, ai_tool)

    render_footer()


if __name__ == "__main__":
    main()