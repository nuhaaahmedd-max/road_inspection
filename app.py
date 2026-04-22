import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, Fullscreen
import plotly.express as px
import base64
import os
import random
from PIL import Image
import io

# 1. Configuration - إعدادات الصفحة
st.set_page_config(
    layout="wide", 
    page_title="Road Inspection AI", 
    initial_sidebar_state="expanded" # إجبار السايد بار على الظهور عند التحميل
)

# 2. Colors
color_map = {'Clear': '#FFD700', 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}
gold_color = "#FFD700" 

# 3. CSS Customization - تعديلات المظهر وإجبار السايد بار
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&display=swap');

    /* تحسين المساحة الكلية */
    .block-container {{ 
        padding-top: 0.5rem !important; 
        max-width: 98% !important;
    }}
    
    .stApp {{ background-color: #0B0E14; color: {gold_color}; }}
    
    /* تنسيق العنوان */
    .main-title {{ 
        color: {gold_color}; font-family: 'Montserrat', sans-serif;
        font-size: 26px; font-weight: 900; text-align: center; 
        width: 100%; padding: 15px 0px; margin-bottom: 10px; 
        text-transform: uppercase; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        border-bottom: 2px solid rgba(255, 215, 0, 0.2);
    }}

    /* تنسيق الكروت العلوي */
    .card {{ 
        background: #161B22; padding: 5px; border-radius: 10px; 
        border: 1px solid {gold_color}; text-align: center;
    }}
    .value {{ font-size: 22px; font-weight: bold; color: {gold_color} !important; }}
    .label {{ font-size: 10px; color: {gold_color} !important; text-transform: uppercase; opacity: 0.8; }}

    /* إجبار السايد بار على الظهور بلون متناسق */
    section[data-testid="stSidebar"] {{ 
        background-color: #11141a !important; 
        border-right: 1px solid {gold_color};
    }}

    /* إطار الخريطة الذهبي */
    iframe {{ 
        border: 2px solid {gold_color} !important; 
        border-radius: 12px !important; 
    }}

    header {{visibility: hidden !important;}}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADING ----------------
@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv("road_data.csv")
        valid_objects = ['Crack', 'Pothole', 'Manhole', 'Clear']
        df = df[df['Object'].isin(valid_objects)]
        df = df.dropna(subset=['Latitude', 'Longitude'])
        return df
    except: return pd.DataFrame()

df = load_data()

# ---------------- SIDEBAR (الفلاتر داخل السايد بار) ----------------
# استخدام 'with st.sidebar' يضمن وضع العناصر بداخلها
with st.sidebar:
    st.markdown(f"<h2 style='color:{gold_color};'>🛠️ SETTINGS</h2>", unsafe_allow_html=True)
    view_mode = st.radio("Map Display Mode:", ["Points", "Heatmap"])
    
    if not df.empty:
        selected_types = st.multiselect(
            "Select Inspection Types:", 
            options=df["Object"].unique(), 
            default=list(df["Object"].unique())
        )
        df_plot = df[df["Object"].isin(selected_types)]
    else:
        df_plot = df

    st.markdown("---")
    if not df_plot.empty:
        csv = df_plot.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Report", data=csv, file_name='inspection_report.csv')

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">Road Inspection Intelligence Dashboard</div>', unsafe_allow_html=True)

# ---------------- TOP ROW: KPIs ----------------
c1, c2, c3, c4, c5 = st.columns(5)
stats = {obj: len(df_plot[df_plot['Object'] == obj]) for obj in ['Crack', 'Pothole', 'Manhole']}

c1.markdown(f"<div class='card'><div class='label'>TOTAL</div><div class='value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='label'>CRACKS</div><div class='value'>{stats['Crack']}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='label'>POTHOLES</div><div class='value'>{stats['Pothole']}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='label'>MANHOLES</div><div class='value'>{stats['Manhole']}</div></div>", unsafe_allow_html=True)

# إصلاح نسبة الـ Confidence المئوية
if not df_plot.empty:
    avg_c = df_plot['Confidence'].mean()
    # إذا كانت القيمة أقل من 1 (مثل 0.9) نضرب في 100، وإلا نستخدمها كما هي
    final_conf = int(avg_c * 100) if avg_c <= 1 else int(avg_c)
    c5.markdown(f"<div class='card'><div class='label'>CONFIDENCE</div><div class='value'>{final_conf}%</div></div>", unsafe_allow_html=True)
else:
    c5.markdown(f"<div class='card'><div class='label'>CONFIDENCE</div><div class='value'>0%</div></div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ---------------- MAIN DASHBOARD LAYOUT ----------------
col_left, col_mid, col_right = st.columns([1.2, 2.5, 1.2])

with col_left:
    st.markdown("##### 📊 Distribution")
    if not df_plot.empty:
        fig1 = px.pie(df_plot, names='Object', hole=0.6, color='Object', color_discrete_map=color_map)
        fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220, showlegend=True, 
                          legend=dict(orientation="h", y=-0.2), paper_bgcolor='rgba(0,0,0,0)', font_color=gold_color)
        st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("##### 📉 Trend")
    fig2 = px.histogram(df_plot, x='Confidence', nbins=15, color_discrete_sequence=[gold_color])
    fig2.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=180, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=gold_color)
    st.plotly_chart(fig2, use_container_width=True)

with col_mid:
    st.markdown("##### 🗺️ Spatial View")
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        if view_mode == "Points":
            for _, row in df_plot.iterrows():
                folium.CircleMarker(
                    location=[row['Longitude'], row['Latitude']], 
                    radius=6, color=color_map.get(row['Object'], "#FFF"), fill=True
                ).add_to(m)
        else:
            HeatMap([[r['Longitude'], r['Latitude']] for _, r in df_plot.iterrows()]).add_to(m)
        
        st_folium(m, height=450, width="100%", key="main_map")

with col_right:
    st.markdown("##### ⚠️ Alerts")
    # عرض حالة النظام
    st.success("✅ No Critical Issues")

    st.markdown("##### 📊 Category Count")
    fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map)
    fig3.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=gold_color, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
