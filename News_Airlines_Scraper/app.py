import feedparser
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import streamlit.components.v1 as components

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(page_title="OPPM | Aviation Intel", page_icon="✈️", layout="wide")

# ============================================================
# 2. REMOVE STREAMLIT CHROME (footer / header / menu)
# ============================================================
components.html(
    """
    <script>
    function removeElements() {
        var selectors = [
            "footer", "header",
            '[data-testid="stHeader"]',
            '[data-testid="stFooter"]',
            '#MainMenu'
        ];
        selectors.forEach(function(s) {
            var el = window.parent.document.querySelector(s);
            if (el) { el.style.display = 'none'; el.innerHTML = ''; }
        });
    }
    removeElements();
    setInterval(removeElements, 500);
    </script>
    """,
    height=0, width=0,
)

# ============================================================
# 3. GLOBAL THEME — DARK PROFESSIONAL
# ============================================================
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Palette ──
   Background   #0D1117  (near-black)
   Surface      #161B22  (card bg)
   Border       #21262D  (hairline)
   Accent-Blue  #1F6FEB  (primary action / highlight)
   Accent-Teal  #00B4B4  (secondary / KSA tag)
   Accent-Amber #E3A000  (warning / ops tag)
   Text-Primary #E6EDF3
   Text-Muted   #8B949E
*/

/* ── Reset ── */
[data-testid="stHeader"], header,
[data-testid="stFooter"], footer,
#MainMenu { display:none !important; }

/* ── App root ── */
.stApp {
    background: #0D1117 !important;
    font-family: 'Inter', 'IBM Plex Sans Arabic', sans-serif;
    color: #E6EDF3;
}

/* ── Main content padding ── */
.main .block-container {
    padding: 2rem 2.5rem 4rem 2.5rem !important;
    max-width: 1400px;
}

/* ── Page header banner ── */
.oppm-hero {
    background: linear-gradient(135deg, #161B22 0%, #0D1117 60%, #0a1628 100%);
    border: 1px solid #21262D;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.oppm-hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #1F6FEB, #00B4B4);
    border-radius: 12px 0 0 12px;
}
.oppm-hero-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #E6EDF3;
    letter-spacing: -0.3px;
    margin: 0 0 0.25rem 0;
}
.oppm-hero-sub {
    font-size: 0.875rem;
    color: #8B949E;
    margin: 0;
    font-weight: 400;
}
.oppm-hero-badge {
    display: inline-block;
    background: rgba(31,111,235,0.15);
    border: 1px solid rgba(31,111,235,0.4);
    color: #58A6FF;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 0.75rem;
}

/* ── KPI metric cards ── */
.kpi-grid { display:flex; gap:1rem; margin-bottom:2rem; flex-wrap:wrap; }
.kpi-card {
    flex: 1;
    min-width: 180px;
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #30363D; }
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-card.blue::after  { background: #1F6FEB; }
.kpi-card.teal::after  { background: #00B4B4; }
.kpi-card.amber::after { background: #E3A000; }
.kpi-label { font-size:0.75rem; font-weight:600; letter-spacing:0.6px; text-transform:uppercase; color:#8B949E; margin-bottom:0.5rem; }
.kpi-value { font-size:2rem; font-weight:700; line-height:1; color:#E6EDF3; }
.kpi-icon  { position:absolute; right:1.25rem; top:1.25rem; font-size:1.25rem; opacity:0.35; }

/* ── Section headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 1rem;
    font-weight: 600;
    color: #E6EDF3;
    letter-spacing: -0.1px;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #21262D;
}
.section-header span.dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}

/* ── News card ── */
.news-card {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s, transform 0.15s;
    position: relative;
}
.news-card:hover {
    border-color: #30363D;
    transform: translateY(-1px);
}
.news-card-title {
    font-size: 0.975rem;
    font-weight: 600;
    color: #E6EDF3;
    margin: 0 0 0.75rem 0;
    line-height: 1.45;
}
.news-card-summary {
    font-size: 0.83rem;
    color: #8B949E;
    line-height: 1.6;
    margin-bottom: 1rem;
}
.news-card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
}
.tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 6px;
    letter-spacing: 0.2px;
    white-space: nowrap;
}
.tag-region-ksa  { background:rgba(0,180,180,0.12); color:#00B4B4; border:1px solid rgba(0,180,180,0.3); }
.tag-region-me   { background:rgba(31,111,235,0.12); color:#58A6FF; border:1px solid rgba(31,111,235,0.3); }
.tag-region-glob { background:rgba(139,148,158,0.12); color:#8B949E; border:1px solid rgba(139,148,158,0.3); }
.tag-ops  { background:rgba(227,160,0,0.12); color:#E3A000; border:1px solid rgba(227,160,0,0.3); }
.tag-comm { background:rgba(63,185,80,0.12); color:#3FB950; border:1px solid rgba(63,185,80,0.3); }
.tag-airline  { background:rgba(139,148,158,0.08); color:#8B949E; border:1px solid #21262D; }
.tag-date { background:transparent; color:#6E7681; border:none; margin-left:auto; }

.news-card-link {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.78rem;
    color: #58A6FF;
    text-decoration: none;
    font-weight: 500;
    margin-top: 0.75rem;
    padding: 4px 0;
    border-bottom: 1px solid transparent;
    transition: border-color 0.15s;
}
.news-card-link:hover { border-bottom-color: #58A6FF; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0D1117 !important;
    border-right: 1px solid #21262D !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}
.sidebar-logo {
    font-size: 1.1rem;
    font-weight: 700;
    color: #E6EDF3;
    letter-spacing: -0.2px;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #21262D;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.sidebar-section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #6E7681;
    margin: 1.25rem 0 0.5rem 0;
}

/* ── Streamlit widget overrides ── */
.stMultiSelect [data-baseweb="select"] {
    background: #161B22 !important;
    border-color: #30363D !important;
    border-radius: 8px !important;
}
.stMultiSelect span {
    background: rgba(31,111,235,0.2) !important;
    color: #58A6FF !important;
    border-radius: 4px !important;
}
[data-testid="stMetricValue"] {
    color: #E6EDF3 !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: #8B949E !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
}
.stMarkdown h3 { color: #E6EDF3 !important; }

/* ── Plotly chart backgrounds ── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── Divider ── */
hr { border-color: #21262D !important; margin: 1.5rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0D1117; }
::-webkit-scrollbar-thumb { background: #30363D; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #484F58; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 4. DATA & CONSTANTS
# ============================================================
AIRLINES_LIST = [
    "Aegean Airlines","Aerospace Jet","Afriqiyah Airways","Air Algerie","Air Anka",
    "Air Asia X","Air Astana","Air Atlanta","Air Blue","Air Cairo","Air China",
    "Air Samarkand","Air Senegal","Air Sial","Air Peace","AKASA Air","Almasria",
    "Alpha Star","Ariana Afghan","Asia Union","Azerbaijan Airlines","Azman Air",
    "Badr Airlines","BBN Airlines","Biman Bangladesh","British Airways","Buraq Air",
    "Camair Co","Cebu Pacific","Centrum Air","China Eastern","China Southern",
    "Corendon Airlines","Daallo Airlines","Egypt Air","Emirates","Ethiopian Airlines",
    "fly beond","Fly Cham","Fly Khieva","Flyadeal","Flydubai","Flynas","Freebird Airlines",
    "Garuda Indonesia","Gulf Air","Hadhramout Airways","Hainan Airlines","Hala Air",
    "Himalaya Airlines","Iran Air","Iraqi Airways","ITA Airways","Jazeera Airways",
    "Jet Aviation","JETEX","JETZHUB","Kuwait Airways","Libyan Airlines","Nord Wind",
    "LOT Polish","LuckyAir","Malaysia Airlines","Mauritanian Airlines","Max Air",
    "MedSky Airways","Middle East Airlines","Nepal Airlines","Nesma Airlines","Nile Air",
    "Oman Air","Panorama Airways","Pegasus Airlines","Petroleum Air","Philippine Airlines",
    "Citilink","Qanot Sharq","Qantas","Qatar Airways","Queen Bilqis","RED C Aviation",
    "Red Sea Airlines","Riyadh Air","Royal Air Maroc","Royal Brunei","RwandAir",
    "Saudi Arabian Airlines","Saudia","Saudi Aramco","Saudi Private Aviation","Saudi Royal",
    "Scat Airlines","SmartLynx","Somon Air","Southwind Airlines","Spicejet","Sudan Airways",
    "Syrian Airlines","Tarco Aviation","Thai Airways","The Helicopter Company","Tunis Air",
    "Turkish Airlines","Turkmenistan Airlines","Uganda Airlines","US-Bangla","Wizz Air","Yemenia"
]
KSA_KEYWORDS = ["Saudi","KSA","Riyadh","Jeddah","Dammam","Madinah","NEOM","Red Sea","GACA","SGS"]
ME_KEYWORDS  = ["Middle East","Gulf","GCC","Dubai","Doha","Abu Dhabi","Cairo","Amman","Kuwait","Bahrain"]


def calculate_days_ago(published_date_str):
    try:
        pub_date = datetime.strptime(published_date_str.split()[0], "%Y-%m-%d").date()
    except:
        pub_date = datetime.now().date()
    delta = (datetime.now().date() - pub_date).days
    if delta <= 0: return "Today"
    if delta == 1: return "1 day ago"
    return f"{delta} days ago"


def generate_mock_ops_data():
    mock_titles = [
        "Riyadh Air updates its fleet delivery schedule for upcoming operations",
        "Saudia expands capacity to meet high passenger demand this season",
        "Flynas announces new direct routes connecting Jeddah to international hubs",
        "Flyadeal enhances ground handling turnaround times at King Abdulaziz Airport",
        "Emirates increases daily frequencies to key GCC destinations",
        "Qatar Airways optimises airspace routing to improve fuel efficiency",
        "Gulf Air reports significant growth in corporate travel segment",
        "Wizz Air expands low-cost network across Saudi peripheral airports",
        "Air Cairo adds fleet capacity for regional leisure routes",
        "The Helicopter Company expands medical evacuation infrastructure in KSA"
    ]
    mock_summaries = [
        "Strategic fleet optimisation aimed at enhancing block-hour efficiency and maintaining strict network schedule integrity.",
        "Ground handling operations scale up workforce deployment to manage baggage throughput and optimise airport terminal dwell times.",
        "Aviation authorities approve slot allocations for upcoming winter schedule expansion across regional airports.",
        "Operations management implements revised aircraft maintenance turnarounds to maximise asset utilisation.",
        "Fuel hedging strategies and network rerouting minimise the impact of regional airspace slot constraints."
    ]
    simulated = []
    for i in range(15):
        title   = random.choice(mock_titles) + f" (Intel-{i+100})"
        summary = random.choice(mock_summaries)
        full    = f"{title} {summary}"
        airlines = [a for a in AIRLINES_LIST if a.lower() in full.lower()]
        is_ksa  = any(k.lower() in full.lower() for k in KSA_KEYWORDS)
        is_me   = any(k.lower() in full.lower() for k in ME_KEYWORDS)
        cat     = "Operations / Infrastructure" if i % 2 == 0 else "Commercial / Fleet"
        past    = (datetime.now() - timedelta(days=random.randint(0,5))).strftime("%Y-%m-%d")
        simulated.append({
            "Title":    title,
            "Summary":  summary,
            "Link":     "https://simpleflying.com",
            "Published":past,
            "Airlines": ", ".join(airlines) if airlines else "Riyadh Air",
            "Region":   "Saudi Arabia 🇸🇦" if is_ksa else ("Middle East 🌍" if is_me else "Global / Regional"),
            "Type":     cat
        })
    return pd.DataFrame(simulated)


@st.cache_data(ttl=900)
def fetch_aviation_news():
    urls = [
        "https://simpleflying.com/feed/",
        "https://www.flightglobal.com/135.rss"
    ]
    articles = []
    for rss_url in urls:
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                title   = entry.title
                summary = entry.summary if 'summary' in entry else ""
                link    = entry.link
                published = (datetime(*entry.published_parsed[:3]).strftime("%Y-%m-%d")
                             if 'published_parsed' in entry else datetime.now().strftime("%Y-%m-%d"))
                full = f"{title} {summary}"
                airlines = [a for a in AIRLINES_LIST if a.lower() in full.lower()]
                is_ksa = any(k.lower() in full.lower() for k in KSA_KEYWORDS)
                is_me  = any(k.lower() in full.lower() for k in ME_KEYWORDS)
                ops_words = ["delay","strike","maintenance","airport","fuel","airspace","route",
                             "slots","handling","capacity","turnaround"]
                cat = ("Operations / Infrastructure"
                       if any(w in full.lower() for w in ops_words) else "Commercial / Fleet")
                if airlines or is_ksa or is_me:
                    articles.append({
                        "Title":    title,
                        "Summary":  summary,
                        "Link":     link,
                        "Published":published,
                        "Airlines": ", ".join(airlines) if airlines else "Market Intelligence",
                        "Region":   "Saudi Arabia 🇸🇦" if is_ksa else ("Middle East 🌍" if is_me else "Global / Regional"),
                        "Type":     cat
                    })
        except:
            continue

    df      = pd.DataFrame(articles)
    df_mock = generate_mock_ops_data()
    return df_mock if df.empty else pd.concat([df, df_mock], ignore_index=True)


# ============================================================
# 5. LOAD & PREPARE DATA
# ============================================================
df_news = fetch_aviation_news()
df_news = df_news.sort_values("Published", ascending=False).reset_index(drop=True)
df_news['Date_Display'] = df_news['Published'].apply(calculate_days_ago)


# ============================================================
# 6. SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">✈️ OPPM</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-label">Region Filter</div>', unsafe_allow_html=True)
    selected_region = st.multiselect(
        "", options=df_news['Region'].unique(),
        default=list(df_news['Region'].unique()),
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-section-label">Activity Type</div>', unsafe_allow_html=True)
    selected_type = st.multiselect(
        "", options=df_news['Type'].unique(),
        default=list(df_news['Type'].unique()),
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(f'<div style="font-size:0.72rem;color:#6E7681;">Last refreshed<br>{datetime.now().strftime("%d %b %Y, %H:%M")}</div>',
                unsafe_allow_html=True)


# ============================================================
# 7. HERO HEADER
# ============================================================
st.markdown("""
<div class="oppm-hero">
  <div class="oppm-hero-badge">Live Intelligence Feed</div>
  <div class="oppm-hero-title">Aviation Intelligence Brief</div>
  <div class="oppm-hero-sub">Real-time monitoring and analytics for targeted airlines and regional ground operations</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# 8. KPI CARDS (custom HTML, not st.metric)
# ============================================================
ksa_count = len(df_news[df_news['Region'] == "Saudi Arabia 🇸🇦"])
ops_count = len(df_news[df_news['Type'] == "Operations / Infrastructure"])

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card blue">
    <div class="kpi-icon">📋</div>
    <div class="kpi-label">Total Reports</div>
    <div class="kpi-value">{len(df_news)}</div>
  </div>
  <div class="kpi-card teal">
    <div class="kpi-icon">🇸🇦</div>
    <div class="kpi-label">Saudi Arabia Scope</div>
    <div class="kpi-value">{ksa_count}</div>
  </div>
  <div class="kpi-card amber">
    <div class="kpi-icon">⚙️</div>
    <div class="kpi-label">Ops / Infra Updates</div>
    <div class="kpi-value">{ops_count}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# 9. ANALYTICS CHARTS
# ============================================================
st.markdown('<div class="section-header"><span class="dot" style="background:#1F6FEB"></span>Operations & Business Analytics</div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

DARK_BG   = "#161B22"
GRID_COL  = "#21262D"
TEXT_COL  = "#8B949E"
COLORS    = ["#1F6FEB", "#00B4B4", "#E3A000", "#3FB950", "#DA3633"]

with chart_col1:
    fig_region = px.pie(
        df_news, names='Region',
        title='Geographic Distribution',
        hole=0.55,
        color_discrete_sequence=COLORS
    )
    fig_region.update_layout(
        paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
        font=dict(color=TEXT_COL, family="Inter, sans-serif", size=12),
        title_font=dict(color="#E6EDF3", size=14, family="Inter, sans-serif"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_COL)),
        margin=dict(t=40, b=20, l=20, r=20)
    )
    fig_region.update_traces(textfont_color="#E6EDF3")
    st.plotly_chart(fig_region, use_container_width=True)

with chart_col2:
    type_counts = df_news['Type'].value_counts().reset_index()
    type_counts.columns = ['Type','Count']
    fig_type = px.bar(
        type_counts, x='Type', y='Count',
        title='Activity Type Volume',
        color='Type',
        color_discrete_sequence=COLORS
    )
    fig_type.update_layout(
        paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
        font=dict(color=TEXT_COL, family="Inter, sans-serif", size=12),
        title_font=dict(color="#E6EDF3", size=14, family="Inter, sans-serif"),
        xaxis=dict(gridcolor=GRID_COL, tickfont=dict(color=TEXT_COL)),
        yaxis=dict(gridcolor=GRID_COL, tickfont=dict(color=TEXT_COL)),
        showlegend=False,
        margin=dict(t=40, b=20, l=20, r=20),
        bargap=0.35
    )
    fig_type.update_traces(marker_line_width=0)
    st.plotly_chart(fig_type, use_container_width=True)


# ============================================================
# 10. NEWS FEED
# ============================================================
filtered_df = df_news[
    (df_news['Region'].isin(selected_region)) &
    (df_news['Type'].isin(selected_type))
]

count_label = f"{len(filtered_df)} reports"
st.markdown(f'<div class="section-header"><span class="dot" style="background:#00B4B4"></span>Filtered News Feed &amp; Operational Intel <span style="margin-left:auto;font-size:0.78rem;color:#6E7681;font-weight:400">{count_label}</span></div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.markdown('<div style="background:#161B22;border:1px solid #21262D;border-radius:10px;padding:2rem;text-align:center;color:#6E7681;font-size:0.875rem;">No reports match the current filters.</div>', unsafe_allow_html=True)
else:
    for _, row in filtered_df.iterrows():
        # Region tag class
        region_class = "tag-region-ksa" if "Saudi" in row['Region'] else \
                       ("tag-region-me" if "Middle" in row['Region'] else "tag-region-glob")
        type_class   = "tag-ops" if "Operations" in row['Type'] else "tag-comm"

        # Truncate airline string
        airline_str = row['Airlines']
        if len(airline_str) > 40:
            airline_str = airline_str[:40] + "…"

        st.markdown(f"""
        <div class="news-card">
          <div class="news-card-title">{row['Title']}</div>
          <div class="news-card-summary">{row['Summary'][:220]}{'…' if len(row['Summary']) > 220 else ''}</div>
          <div class="news-card-meta">
            <span class="tag {region_class}">{row['Region']}</span>
            <span class="tag {type_class}">{row['Type']}</span>
            <span class="tag tag-airline">✈ {airline_str}</span>
            <span class="tag tag-date">🕐 {row['Date_Display']}</span>
          </div>
          <a class="news-card-link" href="{row['Link']}" target="_blank">
            View full report →
          </a>
        </div>
        """, unsafe_allow_html=True)
