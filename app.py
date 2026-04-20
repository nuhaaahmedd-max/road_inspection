import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import base64
import os
import random

# 1. إعداد الصفحة لملء الشاشة بالكامل
st.set_page_config(layout="wide", page_title="Road Inspection Pro")

# الألوان والدرجة الذهبية
gold_theme = "#FFD700"
color_map = {'Clear': '#FFD700', 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}

# 2. CSS متقدم للتقسيم لمربعات (Containers)
st.markdown(f"""
<style>
    .stApp {{ background-color: #0B0E14; color: {gold_theme}; }}
    
    /* ستايل الحاوية (المربع) لكل شارت */
    .chart-container {{
        background-color: #161B22;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        height: 100%;
    }}
    
    /* الهيدر */
    header[data-testid="stHeader"] {{ background-color: #0B0E14 !important; }}
    
    /* الكروت العلوية */
    .kpi-card {{
        background-color: #161B22;
        border-top: 3px solid {gold_theme};
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }}
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
    st.markdown(f"## 🛠️ DASHBOARD SETTINGS")
    selected_types = st.multiselect("FEATURES", ['Clear', 'Crack', 'Manhole', 'Pothole'], default=['Clear', 'Crack', 'Manhole', 'Pothole'])
    df_plot = df[df["Object"].isin(selected_types)] if not df.empty else df

# ---------------- TOP ROW (KPIs) ----------------
st.markdown(f"<h2 style='text-align:center; color:{gold_theme}; margin-bottom:20px;'>ROAD INSPECTION INTELLIGENCE</h2>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><div style='font-size:12px;'>TOTAL ASSETS</div><div style='font-size:24px; font-weight:bold;'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card'><div style='font-size:12px;'>CRACKS</div><div style='font-size:24px; font-weight:bold; color:#FF0000;'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card'><div style='font-size:12px;'>POTHOLES</div><div style='font-size:24px; font-weight:bold; color:#00FF00;'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div style='font-size:12px;'>MANHOLES</div><div style='font-size:24px; font-weight:bold; color:#0070FF;'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- MAIN DASHBOARD LAYOUT (المربعات جنب بعض) ----------------
# تقسيم الصفحة لـ 3 أعمدة زي الصورة اللي بعتيها
main_col1, main_col2, main_col3 = st.columns([1, 2, 1])

# العمود الأول (يسار)
with main_col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Distribution")
    fig_pie = px.pie(df_plot, names='Object', hole=0.4, color='Object', color_discrete_map=color_map)
    fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color=gold_theme, height=300, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Confidence Levels")
    fig_hist = px.histogram(df_plot, x='Confidence', nbins=10, color_discrete_sequence=[gold_theme])
    fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=gold_theme, height=250, margin=dict(t=20, b=0))
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# العمود الثاني (المنتصف - الخريطة)
with main_col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Spatial Analysis View")
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        for _, row in df_plot.iterrows():
            folium.CircleMarker(
                location=[row['Longitude'], row['Latitude']],
                radius=6, color=color_map.get(row['Object'], "#FFF"), fill=True
            ).add_to(m)
        st_folium(m, width="100%", height=580)
    st.markdown("</div>", unsafe_allow_html=True)

# العمود الثالث (يمين)
with main_col3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Counts by Category")
    fig_bar = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map)
    fig_bar.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=gold_theme, height=300)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Priority Notifications")
    critical_count = len(df_plot[df_plot['Confidence'] > 90])
    if critical_count > 0:
        st.error(f"⚠️ {critical_count} High Confidence Defects")
    else:
        st.success("✅ No Urgent Issues Found")
    st.markdown("</div>", unsafe_allow_html=True)
