import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import base64
import os
import random

# 1. إعداد الصفحة
st.set_page_config(layout="wide", page_title="Road Inspection Intelligence")

# درجة الأصفر المبهرة (Cyber Yellow)
cyber_yellow = "#FFFB00" 
color_map = {'Clear': cyber_yellow, 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}

# 2. CSS احترافي (اللون المبهر + تقسيم بدون سكرول)
st.markdown(f"""
<style>
    .stApp {{ background-color: #0B0E14; color: {cyber_yellow}; }}
    .main .block-container {{ padding: 1rem 2rem 0rem 2rem !important; }}
    header[data-testid="stHeader"] {{ background-color: #0B0E14 !important; }}
    
    /* الكروت العلوية */
    .kpi-card {{
        background-color: #161B22; border-bottom: 4px solid {cyber_yellow};
        padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 10px;
    }}
    .kpi-value {{ font-size: 26px !important; font-weight: 900; color: {cyber_yellow}; }}
    .kpi-label {{ font-size: 11px !important; color: {cyber_yellow}; font-weight: 700; opacity: 0.8; }}
    
    /* الحاويات (Boxes) */
    .chart-container {{
        background-color: #161B22; border: 1.5px solid #222;
        border-radius: 12px; padding: 10px; margin-bottom: 8px;
    }}
    h4 {{ margin: 0px 0px 8px 0px !important; font-size: 14px !important; color: {cyber_yellow}; font-weight: 800; }}
</style>
""", unsafe_allow_html=True)

# --- دالة إحضار الصور (تأكدي من أسماء الفولدرات بداخل assets) ---
def get_base64_img(obj_type):
    if obj_type == 'Clear': return "CLEAR"
    try:
        # الكود بيبحث عن فولدر بنفس اسم الـ Object (مثل Crack أو Pothole)
        folder_path = os.path.join("assets", str(obj_type))
        if os.path.exists(folder_path):
            images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                selected_img = random.choice(images)
                with open(os.path.join(folder_path, selected_img), "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except: return None
    return None

# ---------------- DATA LOADING ----------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("road_data.csv")
        return df[df['Object'].isin(['Clear', 'Crack', 'Manhole', 'Pothole'])].dropna(subset=['Latitude', 'Longitude'])
    except: return pd.DataFrame()

df = load_data()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown(f"<h3 style='color:{cyber_yellow}'>🛠️ SETTINGS</h3>", unsafe_allow_html=True)
    selected_types = st.multiselect("FILTER FEATURES", ['Clear', 'Crack', 'Manhole', 'Pothole'], default=['Clear', 'Crack', 'Manhole', 'Pothole'])
    df_plot = df[df["Object"].isin(selected_types)] if not df.empty else df

# ---------------- TITLE ----------------
st.markdown(f"<h2 style='text-align:center; color:{cyber_yellow}; font-weight:900; margin-bottom:10px;'>ROAD INSPECTION INTELLIGENCE</h2>", unsafe_allow_html=True)

# ---------------- KPI ROW ----------------
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>TOTAL ASSETS</div><div class='kpi-value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>CRACKS</div><div class='kpi-value' style='color:#FF0000;'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>POTHOLES</div><div class='kpi-value' style='color:#00FF00;'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>MANHOLES</div><div class='kpi-value' style='color:#0070FF;'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

# ---------------- LAYOUT ----------------
m_col1, m_col2, m_col3 = st.columns([1, 2.2, 1])

with m_col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    if not df_plot.empty:
        # مركز الخريطة
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        
        for _, row in df_plot.iterrows():
            img_data = get_base64_img(row['Object'])
            color = color_map.get(row['Object'], "#FFF")
            
            if img_data == "CLEAR":
                html = f'<div style="color:black; text-align:center; padding:5px;"><b>✅ Status: Clear</b></div>'
            elif img_data:
                html = f'''
                <div style="text-align:center; font-family:sans-serif; color:black;">
                    <b style="color:{color};">{row['Object']}</b><br>
                    <img src="data:image/jpeg;base64,{img_data}" width="160" style="border-radius:5px; margin-top:5px;">
                    <p style="margin:5px; font-size:12px;">Confidence: {row['Confidence']}%</p>
                </div>'''
            else:
                html = f'<div style="color:black; padding:5px;">{row["Object"]} (Point)</div>'
            
            folium.CircleMarker(
                location=[row['Longitude'], row['Latitude']],
                radius=6, color=color, fill=True, fill_opacity=0.85,
                popup=folium.Popup(folium.IFrame(html, width=190, height=200))
            ).add_to(m)
        st_folium(m, width="100%", height=420)
    st.markdown("</div>", unsafe_allow_html=True)

with m_col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Ratio")
    st.plotly_chart(px.pie(df_plot, names='Object', hole=0.5, color='Object', color_discrete_map=color_map).update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color=cyber_yellow, height=200, margin=dict(t=0, b=0, l=0, r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Confidence Level")
    st.plotly_chart(px.histogram(df_plot, x='Confidence', nbins=10, color_discrete_sequence=[cyber_yellow]).update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=cyber_yellow, height=180, margin=dict(t=10, b=0, l=0, r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with m_col3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Counts")
    st.plotly_chart(px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map).update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=cyber_yellow, height=200, margin=dict(t=0, b=0, l=0, r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Alerts")
    if len(df_plot[df_plot['Confidence'] > 90]) > 0: st.error("🚨 HIGH SEVERITY", icon="⚠️")
    else: st.success("✔️ AREA STABLE")
    st.markdown("</div>", unsafe_allow_html=True)
