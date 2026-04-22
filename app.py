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

# 1. Configuration - إجبار السايد بار على الظهور
st.set_page_config(layout="wide", page_title="Road Inspection AI", initial_sidebar_state="expanded")

# 2. Colors
color_map = {'Clear': '#FFD700', 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}
gold_color = "#FFD700" 

# 3. CSS Customization
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&display=swap');

    .block-container {{ 
        padding-top: 0.5rem !important; 
        max-width: 98% !important;
    }}
    
    .stApp {{ background-color: #0B0E14; color: {gold_color}; }}
    
    .main-title {{ 
        color: {gold_color}; font-family: 'Montserrat', sans-serif;
        font-size: 24px; font-weight: 900; text-align: center; 
        width: 100%; padding: 15px 0px; margin-bottom: 10px; 
        text-transform: uppercase; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        border-bottom: 2px solid rgba(255, 215, 0, 0.2);
    }}

    .card {{ 
        background: #161B22; padding: 5px; border-radius: 10px; 
        border: 1px solid {gold_color}; text-align: center;
    }}
    .value {{ font-size: 22px; font-weight: bold; color: {gold_color} !important; }}
    .label {{ font-size: 10px; color: {gold_color} !important; text-transform: uppercase; opacity: 0.8; }}

    /* تحسين ظهور السايد بار */
    section[data-testid="stSidebar"] {{ 
        background-color: #161B22 !important; 
        min-width: 250px !important;
    }}

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

@st.cache_data(show_spinner=False)
def get_random_image_by_type(obj_type):
    if obj_type == 'Clear': return "CLEAR_MODE"
    try:
        base_path = "assets"
        target_folder = str(obj_type).strip()
        full_path = os.path.join(base_path, target_folder)
        if not os.path.exists(full_path): full_path = os.path.join(base_path, target_folder.lower())
        if os.path.exists(full_path):
            images = [f for f in os.listdir(full_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                selected = random.choice(images)
                img_path = os.path.join(full_path, selected)
                with Image.open(img_path) as img:
                    img = img.convert('RGB')
                    img.thumbnail((250, 250))
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG", quality=80)
                    return base64.b64encode(buffered.getvalue()).decode()
    except: return None
    return None

df = load_data()

# ---------------- SIDEBAR (إعادة إظهار الفلاتر) ----------------
with st.sidebar:
    st.markdown("### 🛠️ DASHBOARD CONTROL")
    view_mode = st.radio("Display Mode", ["Points", "Heatmap"])
    if not df.empty:
        selected_types = st.multiselect("Defect Categories", options=df["Object"].unique(), default=list(df["Object"].unique()))
        df_plot = df[df["Object"].isin(selected_types)]
    else:
        df_plot = df

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">Road Inspection Intelligence Dashboard</div>', unsafe_allow_html=True)

# ---------------- TOP ROW: KPIs ----------------
c1, c2, c3, c4, c5 = st.columns(5)
stats = {obj: len(df_plot[df_plot['Object'] == obj]) for obj in ['Crack', 'Pothole', 'Manhole']}
c1.markdown(f"<div class='card'><div class='label'>TOTAL</div><div class='value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='label'>CRACKS</div><div class='value'>{stats['Crack']}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='label'>POTHOLES</div><div class='value'>{stats['Pothole']}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='label'>MANHOLES</div><div class='value'>{stats['Manhole']}</div></div>", unsafe_allow_html=True)

# حل مشكلة الـ 9%
if not df_plot.empty:
    avg = df_plot['Confidence'].mean()
    final_conf = int(avg) if avg > 1 else int(avg * 100)
    c5.markdown(f"<div class='card'><div class='label'>CONFIDENCE</div><div class='value'>{final_conf}%</div></div>", unsafe_allow_html=True)
else:
    c5.markdown(f"<div class='card'><div class='label'>CONFIDENCE</div><div class='value'>0%</div></div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ---------------- MAIN CONTENT ----------------
col_left, col_mid, col_right = st.columns([1.2, 2.5, 1.2])

with col_left:
    st.markdown("##### 📊 Distribution")
    if not df_plot.empty:
        fig1 = px.pie(df_plot, names='Object', hole=0.6, color='Object', color_discrete_map=color_map)
        fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220, showlegend=True, paper_bgcolor='rgba(0,0,0,0)', font_color=gold_color, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("##### 📉 Trend")
    fig2 = px.histogram(df_plot, x='Confidence', nbins=15)
    fig2.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=180, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=gold_color)
    st.plotly_chart(fig2, use_container_width=True)

with col_mid:
    st.markdown("##### 🗺️ Spatial View")
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        if view_mode == "Points":
            for _, row in df_plot.iterrows():
                folium.CircleMarker(location=[row['Longitude'], row['Latitude']], radius=7, color=color_map.get(row['Object'], "#FFF"), fill=True).add_to(m)
        else:
            HeatMap([[r['Longitude'], r['Latitude']] for _, r in df_plot.iterrows()]).add_to(m)
        st_folium(m, height=450, width="100%", key="main_map")

with col_right:
    st.markdown("##### ⚠️ Alerts")
    # التعديل المطلوب: يظهر No Critical Issues إلا لو الثقة تخطت 98% مثلاً أو كانت pothole
    critical = df_plot[(df_plot['Object'] == 'Pothole') & (df_plot['Confidence'] > 95)].head(3)
    if not critical.empty:
        for r in critical.itertuples():
            st.error(f"🚨 {r.Object}")
    else:
        st.success("✅ No Critical Issues")

    st.markdown("##### 📊 Category Count")
    fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map)
    fig3.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=gold_color, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
