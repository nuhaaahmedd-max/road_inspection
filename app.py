import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import base64
import os
import random
from PIL import Image
import io

# 1. الإعدادات الأساسية
st.set_page_config(layout="wide", page_title="Fusion Road AI")

# 2. الألوان (نفس درجات الصورة)
color_map = {'Clear': '#FFD700', 'Crack': '#E91E63', 'Manhole': '#01B9D1', 'Pothole': '#05CD99'}

# 3. CSS لتصغير الأحجام وجعلها "Compact" مثل الصورة
st.markdown("""
<style>
    .stApp { background-color: #F4F7FE; }
    
    /* تصغير المسافات بين العناصر */
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    
    /* ستايل الكروت العلوية (صغيرة ومضغوطة) */
    .fusion-metric {
        background: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 10px 10px 20px rgba(112, 144, 176, 0.05);
        border: 1px solid #F0F0F0;
    }
    .fusion-label { font-size: 12px; color: #A3AED0; font-weight: 600; margin-bottom: 2px; }
    .fusion-value { font-size: 20px; color: #2B3674; font-weight: 700; }

    /* حاوية المحتوى الرئيسي */
    .content-box {
        background: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 10px 10px 20px rgba(112, 144, 176, 0.05);
        height: 380px; /* ارتفاع ثابت لمنع الضخامة */
        overflow: hidden;
    }
    
    .box-title { color: #2B3674; font-size: 16px; font-weight: 700; margin-bottom: 10px; }
    
    /* تصغير حجم الخريطة */
    iframe { height: 300px !important; border-radius: 10px !important; }
    
    /* إخفاء الهوامش الزائدة في Plotly */
    .js-plotly-plot { margin-bottom: -20px; }
</style>
""", unsafe_allow_html=True)

# --- دالة تحميل البيانات (بفرض وجود ملف csv) ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("road_data.csv")
        return df
    except:
        return pd.DataFrame(columns=['Object', 'Latitude', 'Longitude', 'Confidence'])

df = load_data()

# ---------------- HEADER ----------------
st.markdown("<h4 style='color: #2B3674; margin-bottom:15px;'>Road Inspection Dashboard</h4>", unsafe_allow_html=True)

# ---------------- ROW 1: METRICS (4 Columns) ----------------
# هذه الكروت تمثل الصف العلوي في الصورة (Revenue, Page View, etc)
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"<div class='fusion-metric'><div class='fusion-label'>Total Assets</div><div class='fusion-value'>{len(df)}</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='fusion-metric'><div class='fusion-label'>Cracks Found</div><div class='fusion-value' style='color:#E91E63;'>{len(df[df['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='fusion-metric'><div class='fusion-label'>Active Potholes</div><div class='fusion-value' style='color:#05CD99;'>{len(df[df['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
with m4:
    st.markdown(f"<div class='fusion-metric'><div class='fusion-label'>System Status</div><div class='fusion-value' style='color:#01B9D1;'>Optimal</div></div>", unsafe_allow_html=True)

st.write("") # Spacer

# ---------------- ROW 2: MAIN CONTENT (Middle Row) ----------------
# هنا وضعنا الخريطة في الوسط كأنها الشارت الرئيسي الكبير
col_main, col_side = st.columns([2, 1])

with col_main:
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    st.markdown("<div class='box-title'>Spatial Intelligence Map</div>", unsafe_allow_html=True)
    # خريطة مصغرة
    m = folium.Map(location=[24.7136, 46.6753], zoom_start=12, tiles="CartoDB Positron")
    st_folium(m, height=300, width="100%")
    st.markdown("</div>", unsafe_allow_html=True)

with col_side:
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    st.markdown("<div class='box-title'>Traffic & Defects Ratio</div>", unsafe_allow_html=True)
    # شارت دائري صغير (مثل الـ Donut في الصورة)
    if not df.empty:
        fig = px.pie(df, names='Object', hole=0.7, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(showlegend=False, height=250, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ROW 3: RECENT ACTIVITIES & STATUS ----------------
# الصف السفلي الصغير
c_low1, c_low2 = st.columns([1, 2])

with c_low1:
    st.markdown("<div class='content-box' style='height:250px;'>", unsafe_allow_html=True)
    st.markdown("<div class='box-title'>Recent Alerts</div>", unsafe_allow_html=True)
    st.caption("⚠️ Pothole detected at Zone A")
    st.caption("✅ Maintenance complete - Site 4")
    st.markdown("</div>", unsafe_allow_html=True)

with c_low2:
    st.markdown("<div class='content-box' style='height:250px;'>", unsafe_allow_html=True)
    st.markdown("<div class='box-title'>Inspection Trends</div>", unsafe_allow_html=True)
    # شارت خطي صغير جداً
    trend_data = pd.DataFrame({'Day': range(10), 'Count': [2, 5, 4, 8, 3, 6, 9, 4, 7, 5]})
    fig2 = px.line(trend_data, x='Day', y='Count')
    fig2.update_layout(height=180, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
