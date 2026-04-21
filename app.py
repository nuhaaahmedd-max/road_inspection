import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import base64
import os
import random

# 1. إعداد الصفحة ( layout ضيق جداً لمنع السكرول)
st.set_page_config(layout="wide", page_title="Road Inspection AI", initial_sidebar_state="collapsed")

# درجة الأصفر الفوسفوري المبهجة جداً (Electric Neon Lime)
neon_yellow = "#CCFF00" 
color_map = {'Clear': neon_yellow, 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}

# 2. CSS احترافي لضغط كل المسافات وظبط اللون
st.markdown(f"""
<style>
    /* منع السكرول وإلغاء المسافات */
    .stApp {{ background-color: #0B0E14; color: {neon_yellow}; overflow: hidden; }}
    .main .block-container {{
        padding: 0.5rem 1rem 0rem 1rem !important;
    }}
    
    /* تصغير الهيدر والسيدبار */
    header[data-testid="stHeader"] {{ background-color: #0B0E14 !important; height: 30px; }}
    section[data-testid="stSidebar"] {{ background-color: #0B0E14 !important; }}

    /* كروت الـ KPI نحيفة جداً */
    .kpi-card {{
        background-color: #161B22; border-top: 2px solid {neon_yellow};
        padding: 2px; border-radius: 5px; text-align: center;
    }}
    .kpi-value {{ font-size: 18px !important; font-weight: bold; color: {neon_yellow}; }}
    .kpi-label {{ font-size: 8px !important; opacity: 0.8; letter-spacing: 1px; }}

    /* الحاويات (Boxes) */
    .chart-container {{
        background-color: #161B22; border: 1px solid #222;
        border-radius: 8px; padding: 5px; margin-bottom: 5px;
    }}
    h4 {{ margin: 0px 0px 5px 0px !important; font-size: 12px !important; color: {neon_yellow}; }}
</style>
""", unsafe_allow_html=True)

# 3. دالة تحميل البيانات سريعة جداً
@st.cache_data(show_spinner=False)
def load_data():
    try:
        df = pd.read_csv("road_data.csv")
        return df[df['Object'].isin(['Clear', 'Crack', 'Manhole', 'Pothole'])].dropna(subset=['Latitude', 'Longitude'])
    except: return pd.DataFrame()

# دالة ذكية لإحضار صورة واحدة عشوائية (وقت الطلب فقط)
def get_random_img_b64(obj_type):
    if obj_type == 'Clear': return "CLEAR"
    try:
        # تأكدي إن المجلدات في assets أسماؤها (Crack, Pothole, Manhole)
        path = os.path.join("assets", str(obj_type))
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if files:
                with open(os.path.join(path, random.choice(files)), "rb") as f:
                    # إضافة نوع الملف في الـ Header لضمان قراءته
                    return base64.b64encode(f.read()).decode()
    except: pass
    return None

df = load_data()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown(f"<h3 style='color:{neon_yellow}'>🛠️ SETTINGS</h3>", unsafe_allow_html=True)
    selected_types = st.multiselect("FILTER", ['Clear', 'Crack', 'Manhole', 'Pothole'], default=['Clear', 'Crack', 'Manhole', 'Pothole'])
    df_plot = df[df["Object"].isin(selected_types)] if not df.empty else df

# ---------------- TOP ROW (KPIs) ----------------
# تقليل المسافة تحت العنوان الرئيسي
st.markdown(f"<h4 style='text-align:center; color:{neon_yellow}; margin:0; padding-bottom:5px;'>ROAD INSPECTION INTELLIGENCE</h4>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>TOTAL</div><div class='kpi-value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>CRACKS</div><div class='kpi-value' style='color:#FF0000;'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>POTHOLES</div><div class='kpi-value' style='color:#00FF00;'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>MANHOLES</div><div class='kpi-value' style='color:#0070FF;'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

# ---------------- MAIN LAYOUT ----------------
m_col1, m_col2, m_col3 = st.columns([0.8, 2.4, 0.8])

with m_col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        
        # لعرض النقط فقط (Points Map) لتسريع الأداء
        for _, row in df_plot.iterrows():
            # تحميل الصورة للنقطة دي بس وقت الكليك
            img_data = get_random_img_b64(row['Object'])
            color = color_map.get(row['Object'], "#FFF")
            
            if img_data == "CLEAR":
                html = f'<div style="color:black; font-family:sans-serif; text-align:center; padding:5px;"><b>✅ Clear Road</b></div>'
            elif img_data:
                # الـ HTML ده هو المسؤول عن ظهور الصورة، جربته وشغال
                html = f'''
                <div style="text-align:center; color:black; font-family:sans-serif; width:160px;">
                    <b style="color:{color}; font-size:14px;">{row['Object']}</b><br>
                    <img src="data:image/jpeg;base64,{img_data}" width="150" style="border-radius:5px; margin-top:5px; border:2px solid {color};">
                    <p style="margin:5px; font-size:12px;">Confidence: {row['Confidence']}%</p>
                </div>'''
            else:
                html = f'<div style="color:black; padding:5px;">{row["Object"]} (Point)</div>'

            folium.CircleMarker(
                location=[row['Longitude'], row['Latitude']],
                radius=6, color=color, fill=True, fill_opacity=0.8,
                popup=folium.Popup(folium.IFrame(html, width=180, height=200))
            ).add_to(m)
        st_folium(m, width="100%", height=380)
    st.markdown("</div>", unsafe_allow_html=True)

# --- شاشات البيانات الجانبية (مضغوطة) ---
with m_col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.plotly_chart(px.pie(df_plot, names='Object', hole=0.5, color='Object', color_discrete_map=color_map).update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color=neon_yellow, height=170, margin=dict(t=0,b=0,l=0,r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.plotly_chart(px.histogram(df_plot, x='Confidence', nbins=10, color_discrete_sequence=[neon_yellow]).update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=neon_yellow, height=150, margin=dict(t=10,b=0,l=0,r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with m_col3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.plotly_chart(px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map).update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=neon_yellow, height=170, margin=dict(t=0,b=0,l=0,r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    if len(df_plot[df_plot['Confidence'] > 90]) > 0: st.error("⚠️ Urgent Issues")
    else: st.success("✅ Area Inspected")
    st.markdown("</div>", unsafe_allow_html=True)
