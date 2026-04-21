import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import base64
import os
import random

# 1. إعداد الصفحة ومنع السكرول
st.set_page_config(layout="wide", page_title="Road Inspection Intelligence", initial_sidebar_state="expanded")

# اللون النيون اللي اخترناه (Lemon Neon)
neon_yellow = "#CCFF00" 
color_map = {'Clear': neon_yellow, 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}

# 2. CSS متقدم (لمسات جمالية: Glow + Dark Sidebar + No Scroll)
st.markdown(f"""
<style>
    /* خلفية التطبيق ومنع السكرول */
    .stApp {{ background-color: #0B0E14; color: {neon_yellow}; overflow: hidden; }}
    .main .block-container {{ padding: 0.5rem 1.5rem 0rem 1.5rem !important; }}
    
    /* توهج نيون للعناوين */
    h3, h4 {{ 
        color: {neon_yellow} !important; 
        text-shadow: 0 0 10px rgba(204, 255, 0, 0.5);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* كروت الـ KPI مع تأثير التوهج السفلي */
    .kpi-card {{
        background-color: #161B22; 
        border-bottom: 3px solid {neon_yellow};
        box-shadow: 0px 4px 10px rgba(204, 255, 0, 0.1);
        padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 10px;
    }}
    .kpi-value {{ font-size: 24px !important; font-weight: 900; color: {neon_yellow}; }}
    .kpi-label {{ font-size: 10px !important; opacity: 0.8; font-weight: 700; text-transform: uppercase; }}
    
    /* حاويات الشارتات بتصميم قزازي (Glassmorphism) بسيط */
    .chart-container {{
        background-color: #161B22; 
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 10px; margin-bottom: 8px;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.4);
    }}

    /* تصميم السايد بار */
    section[data-testid="stSidebar"] {{ background-color: #0B0E14 !important; border-right: 1px solid #222; }}
</style>
""", unsafe_allow_html=True)

# 3. دالة معالجة الصور (الحل التقني لظهور الصور)
def get_base64_img(obj_type):
    if obj_type == 'Clear': return "CLEAR"
    try:
        folder = os.path.join("assets", str(obj_type))
        if os.path.exists(folder):
            imgs = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if imgs:
                with open(os.path.join(folder, random.choice(imgs)), "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except: return None
    return None

# 4. تحميل البيانات
@st.cache_data(show_spinner=False)
def load_data():
    try:
        df = pd.read_csv("road_data.csv")
        return df[df['Object'].isin(['Clear', 'Crack', 'Manhole', 'Pothole'])].dropna(subset=['Latitude', 'Longitude'])
    except: return pd.DataFrame()

df = load_data()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown(f"<h2 style='color:{neon_yellow}'>🛠️ CONTROL</h2>", unsafe_allow_html=True)
    selected_types = st.multiselect("FILTER FEATURES", ['Clear', 'Crack', 'Manhole', 'Pothole'], default=['Clear', 'Crack', 'Manhole', 'Pothole'])
    df_plot = df[df["Object"].isin(selected_types)] if not df.empty else df

# ---------------- HEADER ----------------
st.markdown(f"<h2 style='text-align:center; margin:0; padding-bottom:10px;'>ROAD INSPECTION INTELLIGENCE</h2>", unsafe_allow_html=True)

# ---------------- KPI ROW ----------------
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>TOTAL DETECTED</div><div class='kpi-value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>CRACKS</div><div class='kpi-value' style='color:#FF0000;'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>POTHOLES</div><div class='kpi-value' style='color:#00FF00;'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>MANHOLES</div><div class='kpi-value' style='color:#0070FF;'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

# ---------------- MAIN LAYOUT ----------------
m_col1, m_col2, m_col3 = st.columns([1, 2.2, 1])

with m_col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    if not df_plot.empty:
        # استخدام CartoDB Dark Matter لخريطة سودة فخمة
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        
        for _, row in df_plot.iterrows():
            img_data = get_base64_img(row['Object'])
            color = color_map.get(row['Object'], "#FFF")
            
            if img_data == "CLEAR":
                html = f'<div style="text-align:center; color:black; font-family:sans-serif;"><b>✅ STATUS: CLEAR</b></div>'
            elif img_data:
                html = f'''
                <div style="text-align:center; color:black; font-family:sans-serif; width:170px;">
                    <b style="color:{color}; font-size:15px;">{row['Object']}</b><br>
                    <img src="data:image/jpeg;base64,{img_data}" width="160" style="border-radius:8px; margin-top:8px; border:2px solid {color};">
                    <p style="margin-top:5px; font-size:12px;">Confidence: <b>{row['Confidence']}%</b></p>
                </div>'''
            else:
                html = f'<div style="color:black; padding:5px;">{row["Object"]} (Point)</div>'
            
            folium.CircleMarker(
                location=[row['Longitude'], row['Latitude']], radius=6, color=color, fill=True, fill_opacity=0.85,
                popup=folium.Popup(folium.IFrame(html, width=190, height=210))
            ).add_to(m)
        st_folium(m, width="100%", height=420)
    st.markdown("</div>", unsafe_allow_html=True)

# --- الأعمدة الجانبية ---
with m_col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Distribution Ratio")
    st.plotly_chart(px.pie(df_plot, names='Object', hole=0.5, color='Object', color_discrete_map=color_map).update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color=neon_yellow, height=200, margin=dict(t=0, b=0, l=0, r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Confidence Analysis")
    st.plotly_chart(px.histogram(df_plot, x='Confidence', nbins=10, color_discrete_sequence=[neon_yellow]).update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=neon_yellow, height=180, margin=dict(t=10, b=0, l=0, r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with m_col3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Defect Counts")
    st.plotly_chart(px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map).update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=neon_yellow, height=200, margin=dict(t=0, b=0, l=0, r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Real-time Alerts")
    if len(df_plot[df_plot['Confidence'] > 90]) > 0: st.error("🚨 HIGH SEVERITY DETECTED")
    else: st.success("✔️ SYSTEM STABLE")
    st.markdown("</div>", unsafe_allow_html=True)
