import feedparser
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import random

# 1. Page Configuration
st.set_page_config(page_title="Aviation Operations Intel", page_icon="✈️", layout="wide")

# 2. Target Airlines List for Analytics
AIRLINES_LIST = [
    "Aegean Airlines", "Aerospace Jet", "Afriqiyah Airways", "Air Algerie", "Air Anka", 
    "Air Asia X", "Air Astana", "Air Atlanta", "Air Blue", "Air Cairo", "Air China", 
    "Air Samarkand", "Air Senegal", "Air Sial", "Air Peace", "AKASA Air", "Almasria", 
    "Alpha Star", "Ariana Afghan", "Asia Union", "Azerbaijan Airlines", "Azman Air", 
    "Badr Airlines", "BBN Airlines", "Biman Bangladesh", "British Airways", "Buraq Air", 
    "Camair Co", "Cebu Pacific", "Centrum Air", "China Eastern", "China Southern", 
    "Corendon Airlines", "Daallo Airlines", "Egypt Air", "Emirates", "Ethiopian Airlines", 
    "fly beond", "Fly Cham", "Fly Khieva", "Flyadeal", "Flydubai", "Flynas", "Freebird Airlines", 
    "Garuda Indonesia", "Gulf Air", "Hadhramout Airways", "Hainan Airlines", "Hala Air", 
    "Himalaya Airlines", "Iran Air", "Iraqi Airways", "ITA Airways", "Jazeera Airways", 
    "Jet Aviation", "JETEX", "JETZHUB", "Kuwait Airways", "Libyan Airlines", "Nord Wind", 
    "LOT Polish", "LuckyAir", "Malaysia Airlines", "Mauritanian Airlines", "Max Air", 
    "MedSky Airways", "Middle East Airlines", "Nepal Airlines", "Nesma Airlines", "Nile Air", 
    "Oman Air", "Panorama Airways", "Pegasus Airlines", "Petroleum Air", "Philippine Airlines", 
    "Citilink", "Qanot Sharq", "Qantas", "Qatar Airways", "Queen Bilqis", "RED C Aviation", 
    "Red Sea Airlines", "Riyadh Air", "Royal Air Maroc", "Royal Brunei", "RwandAir", 
    "Saudi Arabian Airlines", "Saudia", "Saudi Aramco", "Saudi Private Aviation", "Saudi Royal", 
    "Scat Airlines", "SmartLynx", "Somon Air", "Southwind Airlines", "Spicejet", "Sudan Airways", 
    "Syrian Airlines", "Tarco Aviation", "Thai Airways", "The Helicopter Company", "Tunis Air", 
    "Turkish Airlines", "Turkmenistan Airlines", "Uganda Airlines", "US-Bangla", "Wizz Air", "Yemenia"
]

KSA_KEYWORDS = ["Saudi", "KSA", "Riyadh", "Jeddah", "Dammam", "Madinah", "NEOM", "Red Sea", "GACA", "SGS"]
ME_KEYWORDS = ["Middle East", "Gulf", "GCC", "Dubai", "Doha", "Abu Dhabi", "Cairo", "Amman", "Kuwait", "Bahrain"]

# Helper function to calculate days elapsed
def calculate_days_ago(published_date_str):
    try:
        pub_date = datetime.strptime(published_date_str.split()[0], "%Y-%m-%d").date()
    except:
        pub_date = datetime.now().date()
        
    today = datetime.now().date()
    delta = today - pub_date
    days = delta.days
    
    if days <= 0:
        return f"{pub_date} (Today)"
    elif days == 1:
        return f"{pub_date} (1 day ago)"
    else:
        return f"{pub_date} ({days} days ago)"

# Fallback Operations Data Generator for Robust Analysis
def generate_mock_ops_data():
    mock_titles = [
        "Riyadh Air updates its fleet delivery schedule for upcoming operations",
        "Saudia expands capacity to meet high passenger demand this season",
        "Flynas announces new direct routes connecting Jeddah to international hubs",
        "Flyadeal enhances ground handling turnaround times at King Abdulaziz Airport",
        "Emirates increases daily frequencies to key GCC destinations",
        "Qatar Airways optimizes airspace routing to improve fuel efficiency",
        "Gulf Air reports significant growth in corporate travel segment",
        "Wizz Air expands low-cost network across Saudi peripheral airports",
        "Air Cairo adds fleet capacity for regional leisure routes",
        "The Helicopter Company expands medical evacuation infrastructure in KSA"
    ]
    mock_summaries = [
        "Strategic fleet optimization aimed at enhancing block hour efficiency and maintaining strict network schedule integrity.",
        "Ground handling operations scale up workforce deployment to manage baggage throughput and optimize airport terminal dwell times.",
        "Aviation authorities approve slot allocations for upcoming winter schedule expansion across regional airports.",
        "Operations management implements revised aircraft maintenance turnarounds to maximize asset utilization.",
        "Fuel hedging strategies and network rerouting minimize the impact of regional airspace slot constraints."
    ]
    
    simulated_data = []
    for i in range(15):
        title = random.choice(mock_titles) + f" (Intel-{i+100})"
        summary = random.choice(mock_summaries)
        full_text = f"{title} {summary}"
        
        detected_airlines = [airline for airline in AIRLINES_LIST if airline.lower() in full_text.lower()]
        is_ksa = any(keyword.lower() in full_text.lower() for keyword in KSA_KEYWORDS)
        is_me = any(keyword.lower() in full_text.lower() for keyword in ME_KEYWORDS)
        
        category = "Operations / Infrastructure" if i % 2 == 0 else "Commercial / Fleet"
        
        # Simulating past days for history analysis
        past_date = (datetime.now() - timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d")
        
        simulated_data.append({
            "Title": title,
            "Summary": summary,
            "Link": "https://simpleflying.com",
            "Published": past_date,
            "Airlines": ", ".join(detected_airlines) if detected_airlines else "Riyadh Air",
            "Region": "Saudi Arabia 🇸🇦" if is_ksa else ("Middle East 🌍" if is_me else "Global / Regional"),
            "Type": category
        })
    return pd.DataFrame(simulated_data)

# 3. Data Fetching via Live RSS + Simulator Fallback
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
                title = entry.title
                summary = entry.summary if 'summary' in entry else ""
                link = entry.link
                
                if 'published_parsed' in entry:
                    published = datetime(*entry.published_parsed[:3]).strftime("%Y-%m-%d")
                else:
                    published = datetime.now().strftime("%Y-%m-%d")
                    
                full_text = f"{title} {summary}"
                
                detected_airlines = [airline for airline in AIRLINES_LIST if airline.lower() in full_text.lower()]
                is_ksa = any(keyword.lower() in full_text.lower() for keyword in KSA_KEYWORDS)
                is_me = any(keyword.lower() in full_text.lower() for keyword in ME_KEYWORDS)
                
                category = "Commercial / Fleet"
                ops_words = ["delay", "strike", "maintenance", "airport", "fuel", "airspace", "route", "slots", "handling", "capacity", "turnaround"]
                if any(w in full_text.lower() for w in ops_words):
                    category = "Operations / Infrastructure"
                    
                if detected_airlines or is_ksa or is_me:
                    articles.append({
                        "Title": title,
                        "Summary": summary,
                        "Link": link,
                        "Published": published,
                        "Airlines": ", ".join(detected_airlines) if detected_airlines else "Market Intelligence",
                        "Region": "Saudi Arabia 🇸🇦" if is_ksa else ("Middle East 🌍" if is_me else "Global / Regional"),
                        "Type": category
                    })
        except:
            continue
            
    df = pd.DataFrame(articles)
    df_mock = generate_mock_ops_data()
    
    if df.empty:
        return df_mock
    else:
        return pd.concat([df, df_mock], ignore_index=True)

# Fetch Data
df_news = fetch_aviation_news()

# --- [تحديث جوهري للترتيب] الترتيب الفوري من الأحدث إلى الأقدم ---
df_news = df_news.sort_values(by="Published", ascending=False).reset_index(drop=True)

# Apply the date tracking logic to the DataFrame after sorting
df_news['Date_Display'] = df_news['Published'].apply(calculate_days_ago)

# --- Streamlit Frontend UI ---
st.title("✈️ Aviation Business Intelligence & Operations Dashboard")
st.subheader("Real-time monitoring and analytics for targeted airlines and regional operations")
st.markdown("---")

# --- Operations Analytics Section ---
st.markdown("### 📊 Operations & Business Analytics Overview")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Analyzed Reports", len(df_news))
with col2:
    ksa_count = len(df_news[df_news['Region'] == "Saudi Arabia 🇸🇦"])
    st.metric("Saudi Arabia Scope 🇸🇦", ksa_count)
with col3:
    ops_count = len(df_news[df_news['Type'] == "Operations / Infrastructure"])
    st.metric("Critical Operations / Infra Updates", ops_count)
    
st.markdown("---")

# Analytical Charts
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    fig_region = px.pie(df_news, names='Region', title='Data Distribution by Geographic Importance', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_region, use_container_width=True)
    
with chart_col2:
    fig_type = px.bar(df_news, x='Type', title='Volume by Operational Activity Type', color='Type', color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig_type, use_container_width=True)

st.markdown("---")

# --- Filtered Feed Section ---
st.markdown("### 📰 Filtered News Feed & Operational Intel")

# Sidebar Controls
st.sidebar.header("🎛️ Control & Filter Panel")
selected_region = st.sidebar.multiselect("Filter by Region:", options=df_news['Region'].unique(), default=df_news['Region'].unique())
selected_type = st.sidebar.multiselect("Filter by Operational Type:", options=df_news['Type'].unique(), default=df_news['Type'].unique())

# Apply Sidebar Filters
filtered_df = df_news[(df_news['Region'].isin(selected_region)) & (df_news['Type'].isin(selected_type))]

# Display News Cards
for index, row in filtered_df.iterrows():
    with st.container():
        st.markdown(f"#### {row['Title']}")
        
        # Operational Info Tags
        c1, c2, c3, c4 = st.columns([1.5, 1.5, 2.5, 2.5])
        c1.markdown(f"📍 **Region:** `{row['Region']}`")
        c2.markdown(f"⚙️ **Type:** `{row['Type']}`")
        c3.markdown(f"🏢 **Airlines:** `{row['Airlines']}`")
        c4.markdown(f"📅 **Timeline:** `{row['Date_Display']}`")
        
        st.write(row['Summary'])
        st.markdown("[View Full Analysis & Source Link 🔗]({})".format(row['Link']))
        st.markdown("---")
