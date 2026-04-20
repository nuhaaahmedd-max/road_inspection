import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import base64
import os
import random

# 1. إعداد الصفحة مع منع السكرول في الـ CSS
st.set_page_config(layout="wide", page_title="Road Inspection AI")

gold_theme = "#FFD700"
color_map = {'Clear': '#FFD700', 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}

# 2. CSS احترافي لضغط العناصر (Compacting)
st.markdown(f"""
<style>
    /* تقليل المسافات في الصفحة كلها */
    .main .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }}
    .stApp {{ background-color: #0B0E14; color: {gold_theme}; overflow: hidden; }}
    
    /* تصغير الكروت العلوية */
    .kpi-card {{
        background-color: #161B22;
        border-top: 2px solid {gold_theme};
        padding: 5px;
        border-radius: 5px;
        text-align: center;
    }}
    .kpi-value {{ font-size: 20px !important; font-weight: bold; }}
    .kpi-label {{ font-size: 10px !important; opacity: 0.8; }}

    /* تصغير المربعات (Containers) */
    .chart-container {{
        background-color: #161B22;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 5px;
    }}
    h4 {{ margin-bottom: 5px !important; font-size: 14px !important; color: {gold_theme}; }}

    /* تصغير السايد بار */
    section[data-testid="stSidebar"] {{ width: 250px !important; }}
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
# تقليل المسافة تحت العنوان الرئيسي
st.markdown(f"<h3 style='text-align:center; color:{gold_theme}; margin:0; padding-bottom:10px;'>ROAD INSPECTION INTELLIGENCE</h3>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>TOTAL ASSETS</div><div class='kpi-value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>CRACKS</div><div class='kpi-value' style='color:#FF0000;'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>POTHOLES</div><div class='kpi-value' style='color:#00FF00;'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>MANHOLES</div><div class='kpi-value' style='color:#0070FF;'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

# ---------------- MAIN LAYOUT ----------------
# تقسيم المساحة بنسب تجعل الخريطة مسيطرة بدون سكرول
m_col1, m_col2, m_col3 = st.columns([0.9, 2.2, 0.9])

with m_col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Ratio")
    fig_pie = px.pie(df_plot, names='Object', hole=0.5, color='Object', color_discrete_map=color_map)
    fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color=gold_theme, height=220, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Confidence")
    fig_hist = px.histogram(df_plot, x='Confidence', nbins=10, color_discrete_sequence=[gold_theme])
    fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=gold_theme, height=180, margin=dict(t=10, b=0, l=0, r=0))
    fig_hist.update_yaxes(visible=False) # إخفاء المحور الرأسي لتوفير مساحة
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with m_col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    # ارتفاع الخريطة هو اللي بيتحكم في السكرول، خليته 450 عشان يناسب معظم الشاشات
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        for _, row in df_plot.iterrows():
            folium.CircleMarker(location=[row['Longitude'], row['Latitude']], radius=5, color=color_map.get(row['Object'], "#FFF"), fill=True).add_to(m)
        st_folium(m, width="100%", height=440)
    st.markdown("</div>", unsafe_allow_html=True)

with m_col3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Counts")
    fig_bar = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map)
    fig_bar.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=gold_theme, height=220, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Status")
    critical_count = len(df_plot[df_plot['Confidence'] > 90])
    if critical_count > 0:
        st.error(f"⚠️ {critical_count} Urgent")
    else:
        st.success("✅ Stable")
    st.markdown("</div>", unsafe_allow_html=True)
