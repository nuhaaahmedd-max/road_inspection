import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import base64
import os
import random

# 1. إعداد الصفحة
st.set_page_config(layout="wide", page_title="Road Inspection Dashboard")

# درجة الذهب الملكي (شيك جداً وهادية)
royal_gold = "#D4AF37" 
color_map = {'Clear': royal_gold, 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}

# 2. CSS متوازن (حجم وسط)
st.markdown(f"""
<style>
    /* خلفية التطبيق */
    .stApp {{ background-color: #0B0E14; color: {royal_gold}; }}
    
    /* ضبط المسافات الجانبية والعلوية */
    .main .block-container {{
        padding: 1rem 2rem 0rem 2rem !important;
    }}
    
    /* الهيدر */
    header[data-testid="stHeader"] {{ background-color: #0B0E14 !important; }}
    
    /* كروت الـ KPI - حجم وسط */
    .kpi-card {{
        background-color: #161B22;
        border-bottom: 3px solid {royal_gold};
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 15px;
    }}
    .kpi-value {{ font-size: 24px !important; font-weight: bold; color: {royal_gold}; }}
    .kpi-label {{ font-size: 11px !important; opacity: 0.9; letter-spacing: 1px; font-weight: 700; }}

    /* الحاويات (Boxes) بحدود ناعمة */
    .chart-container {{
        background-color: #161B22;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }}
    h4 {{ margin: 0px 0px 10px 0px !important; font-size: 15px !important; color: {royal_gold}; font-weight: 800; }}

    /* تعديل السايد بار */
    section[data-testid="stSidebar"] {{ background-color: #0B0E14 !important; border-right: 1px solid #222; }}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("road_data.csv")
        return df[df['Object'].isin(['Clear', 'Crack', 'Manhole', 'Pothole'])].dropna(subset=['Latitude', 'Longitude'])
    except: return pd.DataFrame()

df = load_data()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown(f"<h3 style='color:{royal_gold}'>🛠️ SETTINGS</h3>", unsafe_allow_html=True)
    selected_types = st.multiselect("FILTER FEATURES", ['Clear', 'Crack', 'Manhole', 'Pothole'], default=['Clear', 'Crack', 'Manhole', 'Pothole'])
    df_plot = df[df["Object"].isin(selected_types)] if not df.empty else df

# ---------------- TOP ROW (KPIs) ----------------
st.markdown(f"<h2 style='text-align:center; color:{royal_gold}; font-weight:900; margin-bottom:15px; letter-spacing:2px;'>ROAD INSPECTION INTELLIGENCE</h2>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>TOTAL ASSETS</div><div class='kpi-value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>CRACKS DETECTED</div><div class='kpi-value' style='color:#FF0000;'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>POTHOLES FOUND</div><div class='kpi-value' style='color:#00FF00;'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>MANHOLES IDENTIFIED</div><div class='kpi-value' style='color:#0070FF;'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

# ---------------- MAIN LAYOUT (وسط - مريح للعين) ----------------
m_col1, m_col2, m_col3 = st.columns([1, 2, 1])

with m_col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Feature Ratio")
    fig_pie = px.pie(df_plot, names='Object', hole=0.5, color='Object', color_discrete_map=color_map)
    fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color=royal_gold, height=250, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Confidence Levels")
    fig_hist = px.histogram(df_plot, x='Confidence', nbins=12, color_discrete_sequence=[royal_gold])
    fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=royal_gold, height=200, margin=dict(t=10, b=0, l=0, r=0))
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with m_col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Spatial Intelligence View")
    # ارتفاع الماب 480px هو الارتفاع "الوسط" المثالي
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        for _, row in df_plot.iterrows():
            folium.CircleMarker(location=[row['Longitude'], row['Latitude']], radius=6, color=color_map.get(row['Object'], "#FFF"), fill=True).add_to(m)
        st_folium(m, width="100%", height=480)
    st.markdown("</div>", unsafe_allow_html=True)

with m_col3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Object Counts")
    fig_bar = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map)
    fig_bar.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=royal_gold, height=250, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Priority Notifications")
    crit = len(df_plot[df_plot['Confidence'] > 90])
    if crit > 0: st.error(f"⚠️ {crit} Critical Issues")
    else: st.success("✅ Maintenance Stable")
    st.markdown("</div>", unsafe_allow_html=True)
