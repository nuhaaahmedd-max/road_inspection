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

# درجة الأصفر الهادئة
soft_gold = "#E1B12C" 
color_map = {'Clear': soft_gold, 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}

# 2. CSS مضغوط جداً لمنع السكرول
st.markdown(f"""
<style>
    /* منع السكرول وإلغاء المسافات الزائدة */
    .stApp {{ background-color: #0B0E14; color: {soft_gold}; overflow: hidden; }}
    .main .block-container {{
        padding: 0.5rem 1.5rem 0rem 1.5rem !important;
    }}
    
    /* تصغير الهيدر */
    header[data-testid="stHeader"] {{ background-color: #0B0E14 !important; height: 40px; }}
    
    /* كروت الـ KPI نحيفة جداً */
    .kpi-card {{
        background-color: #161B22;
        border-top: 2px solid {soft_gold};
        padding: 3px;
        border-radius: 5px;
        text-align: center;
    }}
    .kpi-value {{ font-size: 18px !important; font-weight: bold; color: {soft_gold}; }}
    .kpi-label {{ font-size: 9px !important; opacity: 0.8; letter-spacing: 1px; }}

    /* الحاويات (Boxes) */
    .chart-container {{
        background-color: #161B22;
        border: 1px solid #222;
        border-radius: 8px;
        padding: 5px;
        margin-bottom: 5px;
    }}
    h4 {{ margin: 0px 0px 5px 0px !important; font-size: 13px !important; color: {soft_gold}; }}

    /* السايد بار */
    section[data-testid="stSidebar"] {{ width: 230px !important; }}
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
    st.markdown("### 🛠️ SETTINGS")
    selected_types = st.multiselect("FILTER", ['Clear', 'Crack', 'Manhole', 'Pothole'], default=['Clear', 'Crack', 'Manhole', 'Pothole'])
    df_plot = df[df["Object"].isin(selected_types)] if not df.empty else df

# ---------------- TOP ROW (KPIs) ----------------
st.markdown(f"<h4 style='text-align:center; color:{soft_gold}; margin:0; padding-bottom:5px;'>ROAD INSPECTION INTELLIGENCE</h4>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>TOTAL ASSETS</div><div class='kpi-value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>CRACKS</div><div class='kpi-value' style='color:#FF0000;'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>POTHOLES</div><div class='kpi-value' style='color:#00FF00;'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>MANHOLES</div><div class='kpi-value' style='color:#0070FF;'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

# ---------------- MAIN LAYOUT ----------------
m_col1, m_col2, m_col3 = st.columns([0.8, 2.4, 0.8])

with m_col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Ratio")
    fig_pie = px.pie(df_plot, names='Object', hole=0.5, color='Object', color_discrete_map=color_map)
    fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color=soft_gold, height=180, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Confidence")
    fig_hist = px.histogram(df_plot, x='Confidence', nbins=10, color_discrete_sequence=[soft_gold])
    fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=soft_gold, height=160, margin=dict(t=10, b=0, l=0, r=0))
    fig_hist.update_yaxes(visible=False)
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with m_col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    # تصغير الماب لـ 380 لضمان عدم وجود سكرول
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        for _, row in df_plot.iterrows():
            folium.CircleMarker(location=[row['Longitude'], row['Latitude']], radius=4, color=color_map.get(row['Object'], "#FFF"), fill=True).add_to(m)
        st_folium(m, width="100%", height=380)
    st.markdown("</div>", unsafe_allow_html=True)

with m_col3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Counts")
    fig_bar = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map)
    fig_bar.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=soft_gold, height=180, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Status")
    # تصغير جزء التنبيهات
    crit = len(df_plot[df_plot['Confidence'] > 90])
    if crit > 0: st.error(f"⚠️ {crit} Critical", icon="🚨")
    else: st.success("✅ Stable", icon="✔️")
    st.markdown("</div>", unsafe_allow_html=True)
