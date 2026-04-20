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

# درجة اللون الـ Neon اللي في الصورة بالظبط
neon_color = "#CCFF00" 
color_map = {'Clear': neon_color, 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}

# 2. CSS مضغوط واحترافي
st.markdown(f"""
<style>
    .stApp {{ background-color: #0B0E14; color: {neon_color}; overflow: hidden; }}
    .main .block-container {{ padding: 1rem 2rem 0rem 2rem !important; }}
    header[data-testid="stHeader"] {{ background-color: #0B0E14 !important; }}
    
    .kpi-card {{
        background-color: #161B22; border-top: 2px solid {neon_color};
        padding: 5px; border-radius: 5px; text-align: center;
    }}
    .kpi-value {{ font-size: 22px !important; font-weight: bold; color: {neon_color}; }}
    .kpi-label {{ font-size: 10px !important; opacity: 0.8; font-weight: 800; }}

    .chart-container {{
        background-color: #161B22; border: 1px solid #333;
        border-radius: 8px; padding: 10px; margin-bottom: 5px;
    }}
</style>
""", unsafe_allow_html=True)

# 3. دالة الصور (معدلة لضمان القراءة)
def get_b64(obj_type):
    if obj_type == 'Clear': return "CLEAR"
    try:
        # تأكدي إن المجلدات أسماؤها مطابقة تماماً (Crack, Pothole, Manhole)
        folder = os.path.join("assets", str(obj_type))
        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if files:
                img_path = os.path.join(folder, random.choice(files))
                with open(img_path, "rb") as f:
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
    st.markdown(f"### 🛠️ SETTINGS")
    selected = st.multiselect("FILTER", ['Clear', 'Crack', 'Manhole', 'Pothole'], default=['Clear', 'Crack', 'Manhole', 'Pothole'])
    df_plot = df[df["Object"].isin(selected)] if not df.empty else df

# ---------------- TOP ROW ----------------
st.markdown(f"<h3 style='text-align:center; color:{neon_color}; margin:0; padding-bottom:10px;'>ROAD INSPECTION INTELLIGENCE</h3>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>TOTAL</div><div class='kpi-value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>CRACKS</div><div class='kpi-value' style='color:#FF0000;'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>POTHOLES</div><div class='kpi-value' style='color:#00FF00;'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>MANHOLES</div><div class='kpi-value' style='color:#0070FF;'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

# ---------------- LAYOUT ----------------
c_left, c_mid, c_right = st.columns([1, 2.2, 1])

with c_mid:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        for _, row in df_plot.iterrows():
            img_code = get_b64(row['Object'])
            color = color_map.get(row['Object'], "#FFF")
            
            if img_code == "CLEAR":
                html = '<div style="color:black; padding:5px;"><b>✅ Clear Road</b></div>'
            elif img_code:
                # حل مشكلة المساحة البيضاء: وضع الصورة داخل ديف وتحديد الارتفاع
                html = f'''
                <div style="text-align:center; color:black; font-family:sans-serif; width:160px; min-height:150px;">
                    <b style="color:{color};">{row['Object']}</b><br>
                    <img src="data:image/jpeg;base64,{img_code}" style="width:100%; border-radius:5px; margin-top:5px; display:block;">
                </div>'''
            else:
                html = f'<div style="color:black;">{row["Object"]}</div>'

            folium.CircleMarker(
                location=[row['Longitude'], row['Latitude']], radius=6, color=color, fill=True, fill_opacity=0.8,
                popup=folium.Popup(folium.IFrame(html, width=180, height=200))
            ).add_to(m)
        st_folium(m, width="100%", height=420)
    st.markdown("</div>", unsafe_allow_html=True)

# (الشارتات الجانبية)
with c_left:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.plotly_chart(px.pie(df_plot, names='Object', hole=0.5, color='Object', color_discrete_map=color_map).update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color=neon_color, height=200), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.plotly_chart(px.histogram(df_plot, x='Confidence', nbins=10, color_discrete_sequence=[neon_color]).update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=neon_color, height=180), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c_right:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.plotly_chart(px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map).update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=neon_color, height=200), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    if len(df_plot[df_plot['Confidence'] > 90]) > 0: st.error("🚨 CRITICAL")
    else: st.success("✔️ STABLE")
    st.markdown("</div>", unsafe_allow_html=True)
