import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import base64
import os
import random

# 1. إعداد الصفحة
st.set_page_config(layout="wide", page_title="Road Inspection AI")

# درجة الأصفر الفوسفوري اللي طلبتيها (Electric Lime)
neon_yellow = "#CCFF00" 
color_map = {'Clear': neon_yellow, 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}

# 2. CSS المتظبط باللون الجديد وضغط المساحات
st.markdown(f"""
<style>
    .main .block-container {{ padding: 1rem 2rem 0rem 2rem !important; }}
    .stApp {{ background-color: #0B0E14; color: {neon_yellow}; overflow: hidden; }}
    
    .kpi-card {{
        background-color: #161B22; border-top: 2px solid {neon_yellow};
        padding: 5px; border-radius: 5px; text-align: center;
    }}
    .kpi-value {{ font-size: 20px !important; font-weight: bold; color: {neon_yellow}; }}
    .kpi-label {{ font-size: 10px !important; opacity: 0.8; }}

    .chart-container {{
        background-color: #161B22; border: 1px solid #333;
        border-radius: 8px; padding: 8px; margin-bottom: 5px;
    }}
    h4 {{ margin-bottom: 5px !important; font-size: 14px !important; color: {neon_yellow}; }}
</style>
""", unsafe_allow_html=True)

# 3. دالة تحويل الصور (المسؤولة عن ظهور الصور)
def get_image_as_base64(obj_type):
    if obj_type == 'Clear': return "CLEAR"
    try:
        # لازم فولدر assets يكون جنبه فولدرات بنفس الأسماء (Crack, Pothole, Manhole)
        path = os.path.join("assets", str(obj_type))
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if files:
                with open(os.path.join(path, random.choice(files)), "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except: return None
    return None

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

# ---------------- HEADER ----------------
st.markdown(f"<h3 style='text-align:center; color:{neon_yellow}; margin:0; padding-bottom:10px;'>ROAD INSPECTION INTELLIGENCE</h3>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>TOTAL ASSETS</div><div class='kpi-value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>CRACKS</div><div class='kpi-value' style='color:#FF0000;'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>POTHOLES</div><div class='kpi-value' style='color:#00FF00;'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>MANHOLES</div><div class='kpi-value' style='color:#0070FF;'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

# ---------------- MAIN LAYOUT ----------------
m_col1, m_col2, m_col3 = st.columns([0.9, 2.2, 0.9])

with m_col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        for _, row in df_plot.iterrows():
            img_b64 = get_image_as_base64(row['Object'])
            color = color_map.get(row['Object'], "#FFF")
            
            if img_b64 == "CLEAR":
                html = f'<div style="color:black; font-family:sans-serif;"><b>✅ Safe Zone</b></div>'
            elif img_b64:
                # الجزء ده هو اللي بيخلي الصورة تظهر جوه الخريطة
                html = f'''
                <div style="text-align:center; color:black; font-family:sans-serif; width:160px;">
                    <b style="color:{color};">{row['Object']}</b><br>
                    <img src="data:image/jpeg;base64,{img_b64}" width="150" style="border-radius:5px; margin-top:5px;">
                    <p style="font-size:12px;">Confidence: {row['Confidence']}%</p>
                </div>'''
            else:
                html = f'<div style="color:black;">{row["Object"]}</div>'

            folium.CircleMarker(
                location=[row['Longitude'], row['Latitude']],
                radius=6, color=color, fill=True, fill_opacity=0.8,
                popup=folium.Popup(folium.IFrame(html, width=180, height=200))
            ).add_to(m)
        st_folium(m, width="100%", height=440)
    st.markdown("</div>", unsafe_allow_html=True)

# --- شاشات البيانات الجانبية ---
with m_col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.plotly_chart(px.pie(df_plot, names='Object', hole=0.5, color='Object', color_discrete_map=color_map).update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color=neon_yellow, height=220, margin=dict(t=0,b=0,l=0,r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.plotly_chart(px.histogram(df_plot, x='Confidence', nbins=10, color_discrete_sequence=[neon_yellow]).update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=neon_yellow, height=180, margin=dict(t=10,b=0,l=0,r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with m_col3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.plotly_chart(px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map).update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=neon_yellow, height=220, margin=dict(t=0,b=0,l=0,r=0)), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    if len(df_plot[df_plot['Confidence'] > 90]) > 0: st.error("⚠️ Urgent Issues")
    else: st.success("✅ Stable")
    st.markdown("</div>", unsafe_allow_html=True)
