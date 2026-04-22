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

# 1. Configuration - تهيئة الصفحة لتشمل كامل العرض
st.set_page_config(layout="wide", page_title="Road Inspection AI", initial_sidebar_state="collapsed")

# 2. Colors
color_map = {'Clear': '#FFD700', 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}
gold_color = "#FFD700" 

# 3. CSS Customization - تقليل المسافات البيضاء والتحكم في الارتفاع
st.markdown(f"""
<style>
    /* تقليل المسافات في أعلى الصفحة */
    .block-container {{ padding-top: 1rem; padding-bottom: 0rem; }}
    
    .stApp {{ background-color: #0B0E14; color: {gold_color}; }}
    
    .main-title {{ 
        color: {gold_color}; font-family: 'Montserrat', sans-serif;
        font-size: 24px; font-weight: 800; text-align: center; 
        margin-bottom: 10px; text-transform: uppercase;
        text-shadow: 1px 1px 0px #000000;
    }}

    /* تصميم الكروت بحجم أصغر لتوفر مساحة */
    .card {{ 
        background: #161B22; padding: 8px; border-radius: 8px; 
        border: 1px solid {gold_color}; text-align: center;
    }}
    .value {{ font-size: 20px; font-weight: bold; color: {gold_color} !important; }}
    .label {{ font-size: 10px; color: {gold_color}; font-weight: 700; }}

    /* إخفاء شريط القوائم العلوي لتوفير مساحة */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADING ----------------
@st.cache_data
def load_data():
    try:
        # تأكد من وجود ملف road_data.csv أو استبدله ببيانات تجريبية هنا
        df = pd.read_csv("road_data.csv")
        return df.dropna(subset=['Latitude', 'Longitude'])
    except:
        return pd.DataFrame(columns=['Object', 'Latitude', 'Longitude', 'Confidence'])

@st.cache_data(show_spinner=False)
def get_random_image_by_type(obj_type):
    # (نفس دالتك السابقة للمعالجة)
    return "CLEAR_MODE" if obj_type == 'Clear' else None

df = load_data()

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">Road Inspection Intelligence Dashboard</div>', unsafe_allow_html=True)

# ---------------- TOP ROW (KPIs) ----------------
# جعلنا الـ KPIs في سطر واحد رفيع جداً
df_plot = df # تبسيط للمثال
c1, c2, c3, c4, c5 = st.columns(5)
stats = {obj: len(df_plot[df_plot['Object'] == obj]) for obj in ['Crack', 'Pothole', 'Manhole']}
c1.markdown(f"<div class='card'><div class='label'>TOTAL</div><div class='value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='label'>CRACKS</div><div class='value'>{stats['Crack']}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='label'>POTHOLES</div><div class='value'>{stats['Pothole']}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='label'>MANHOLES</div><div class='value'>{stats['Manhole']}</div></div>", unsafe_allow_html=True)
c5.markdown(f"<div class='card'><div class='label'>AVG CONFIDENCE</div><div class='value'>{int(df_plot['Confidence'].mean()) if not df_plot.empty else 0}%</div></div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ---------------- MAIN CONTENT (GRID SYSTEM) ----------------
# تقسيم الصفحة إلى 3 أعمدة رئيسية: يسار (رسوم)، منتصف (خريطة)، يمين (تنبيهات ورسوم)
col_left, col_mid, col_right = st.columns([1, 2, 1])

with col_left:
    st.markdown("##### 📊 Defect Distribution")
    if not df_plot.empty:
        fig1 = px.pie(df_plot, names='Object', hole=0.5, color='Object', color_discrete_map=color_map)
        fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200, showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("##### 📈 Confidence Levels")
    fig2 = px.histogram(df_plot, x='Confidence', nbins=10, color_discrete_sequence=[gold_color])
    fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=180, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)

with col_mid:
    # الخريطة هي العنصر الأكبر في المنتصف
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        # إضافة النقاط (نفس منطق الكود الخاص بك)
        for _, row in df_plot.iterrows():
            folium.CircleMarker(
                location=[row['Longitude'], row['Latitude']],
                radius=6, color=color_map.get(row['Object'], "#FFF"), fill=True
            ).add_to(m)
        
        # التحكم في ارتفاع الخريطة ليتناسب مع الشاشة
        st_folium(m, height=420, width="100%", key="main_map")

with col_right:
    st.markdown("##### ⚠️ Priority Alerts")
    # عرض التنبيهات في مساحة صغيرة مع تمرير داخلي إذا كثرت
    st.markdown('<div style="height: 180px; overflow-y: auto;">', unsafe_allow_html=True)
    critical = df_plot[df_plot['Confidence'] > 90].head(4)
    if not critical.empty:
        for _, r in critical.iterrows():
            st.caption(f"🚨 {r.Object}: {r.Confidence}% Confidence")
    else:
        st.success("All systems clear")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("##### 📊 Object Count")
    fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map)
    fig3.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig3, use_container_width=True)

# ---------------- FOOTER / FILTERS ----------------
# وضع الفلاتر في الأسفل بشكل أفقي لتوفير مساحة جانبية
st.markdown("---")
f1, f2, f3 = st.columns([2, 2, 1])
with f1:
    selected_types = st.multiselect("Filter Objects:", df["Object"].unique(), default=list(df["Object"].unique()))
with f2:
    view_mode = st.radio("Display:", ["Points", "Heatmap"], horizontal=True)
with f3:
    st.download_button("📩 Export CSV", data=df_plot.to_csv().encode('utf-8'), file_name='report.csv')
