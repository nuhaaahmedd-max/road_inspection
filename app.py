import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import plotly.express as px
import base64
import os
import random

# 1. Configuration
st.set_page_config(layout="wide", page_title="Road Inspection AI", initial_sidebar_state="expanded")

# 2. Final Color Map (المعتمد)
color_map = {
    'Clear': '#FFD700',      # ذهبي
    'Crack': '#FF0000',      # أحمر
    'Manhole': '#0070FF',    # أزرق
    'Pothole': '#00FF00',    # أخضر
}

# الدرجة الذهبية الشيك المطلوبة
gold_theme = "#FFD700"

# 3. CSS Customization (المطابق للصور 100%)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap');
    
    /* خلفية التطبيق والهيدر */
    .stApp {{ background-color: #0B0E14; color: {gold_theme}; }}
    header[data-testid="stHeader"] {{ background-color: #0B0E14 !important; visibility: visible !important; }}
    
    /* تصميم السايد بار الأسود بالكامل */
    section[data-testid="stSidebar"] {{ 
        background-color: #0B0E14 !important; 
        border-right: 1px solid #333;
        width: 300px !important;
    }}

    /* عناوين السايد بار بالذهبي والخط العريض */
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] label p {{ 
        color: {gold_theme} !important; 
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        font-size: 14px !important;
        letter-spacing: 1px;
    }}

    /* تصميم مربعات الاختيار (Multiselect) بالحدود الذهبية كما في الصورة */
    div[data-baseweb="select"] > div {{
        background-color: #161B22 !important;
        border: 1.5px solid {gold_theme} !important;
        border-radius: 8px !important;
    }}
    
    /* تصميم الـ Tags جوه المربع (Clear, Crack etc) */
    span[data-baseweb="tag"] {{
        background-color: transparent !important;
        border: 1px solid {gold_theme} !important;
        border-radius: 5px !important;
        color: {gold_theme} !important;
    }}

    /* تصميم الـ Radio Buttons كمربعات اختيار */
    div[data-testid="stRadio"] div[role="radiogroup"] {{
        flex-direction: column;
        gap: 10px;
    }}
    div[data-testid="stRadio"] label {{
        background: #0B0E14 !important;
        border: 1px solid #333 !important;
        padding: 8px 15px !important;
        border-radius: 5px !important;
        transition: 0.3s;
    }}
    div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child {{
        background-color: #FF0000 !important; /* اللون الأحمر للدايرة المختارة كما في صورتك */
    }}

    /* تصميم الكروت الذهبية */
    .card {{ background: #161B22; padding: 12px; border-radius: 12px; border: 1px solid {gold_theme}; text-align: center; }}
    .value {{ font-size: 28px; font-weight: bold; color: {gold_theme} !important; }}
    .label {{ font-size: 12px; color: {gold_theme} !important; text-transform: uppercase; font-weight: 900; }}

    /* الهيدر الرئيسي */
    .main-title {{ 
        color: {gold_theme}; font-family: 'Montserrat', sans-serif;
        font-size: 32px; font-weight: 900; padding: 10px 15px;
        border-bottom: 2px solid #1F2937; margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADING ----------------
@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv("road_data.csv")
        valid = ['Crack', 'Pothole', 'Manhole', 'Clear']
        df = df[df['Object'].isin(valid)].dropna(subset=['Latitude', 'Longitude'])
        return df
    except: return pd.DataFrame()

df = load_data()

# ---------------- SIDEBAR (مطابق للصور) ----------------
st.sidebar.markdown(f"## 🛠️ CONTROL PANEL")
st.sidebar.write("MAP DISPLAY MODE:")
view_mode = st.sidebar.radio("", ["Points Map", "Heatmap Overlay"], label_visibility="collapsed")

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.write("SELECT FEATURES:")
if not df.empty:
    selected_types = st.sidebar.multiselect("", options=df["Object"].unique(), default=list(df["Object"].unique()), label_visibility="collapsed")
    df_plot = df[df["Object"].isin(selected_types)]
else:
    df_plot = df

# ---------------- MAIN CONTENT ----------------
st.markdown('<div class="main-title">ROAD INSPECTION INTELLIGENCE</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"<div class='card'><div class='label'>TOTAL ASSETS</div><div class='value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='label'>CRACKS</div><div class='value'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='label'>POTHOLES</div><div class='value'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='label'>MANHOLES</div><div class='value'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.8, 1])

with col2:
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        if view_mode == "Points Map":
            for _, row in df_plot.iterrows():
                folium.CircleMarker(
                    location=[row['Longitude'], row['Latitude']],
                    radius=8, color=color_map.get(row['Object'], "#FFF"), fill=True, fill_opacity=0.9
                ).add_to(m)
        else:
            HeatMap([[row['Longitude'], row['Latitude']] for _, row in df_plot.iterrows()], radius=15).add_to(m)
        st_folium(m, height=400, width="100%")

# باقي الشارتات بنفس الألوان
with col1:
    fig1 = px.pie(df_plot, names='Object', hole=0.6, color='Object', color_discrete_map=color_map)
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color=gold_theme, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col3:
    fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map)
    fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color=gold_theme, plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
