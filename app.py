import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import plotly.express as px
import base64
import os
import random

# 1. Configuration
st.set_page_config(layout="wide", page_title="Road Inspection AI", initial_sidebar_state="expanded")

# 2. Final Color Map
color_map = {
    'Clear': '#FFD700',
    'Crack': '#FF0000',
    'Manhole': '#0070FF',
    'Pothole': '#00FF00',
}

gold_color = "#FFD700" 

# 3. CSS Customization
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap');
    
    .stApp {{ background-color: #0B0E14; color: {gold_color}; }}
    header[data-testid="stHeader"] {{ background-color: #0B0E14 !important; visibility: visible !important; }}
    
    .main-title {{ 
        color: {gold_color}; font-family: 'Montserrat', sans-serif;
        font-size: 34px; font-weight: 900; text-align: left; 
        padding: 10px 0px 10px 15px; border-bottom: 2px solid #1F2937; 
        margin-bottom: 15px; letter-spacing: 2px;
        text-transform: uppercase; -webkit-text-stroke: 1.2px #000000;
        text-shadow: 2px 2px 0px #000000;
    }}

    section[data-testid="stSidebar"] {{ background-color: #0B0E14 !important; border-right: 1px solid #1F2937; }}
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] label {{ 
        color: {gold_color} !important; font-weight: 800 !important; 
    }}

    /* NEW SIDEBAR STYLE LIKE IMAGE */
    section[data-testid="stSidebar"] h2 {{
        font-size: 20px;
        margin-bottom: 15px;
    }}

    section[data-testid="stSidebar"] h3 {{
        font-size: 13px;
        letter-spacing: 1px;
        margin-top: 15px;
        margin-bottom: 8px;
        color: {gold_color};
    }}

    div[data-testid="stRadio"] > div {{
        flex-direction: column;
        gap: 8px;
    }}

    div[data-testid="stRadio"] label {{
        background: #161B22;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #333;
        cursor: pointer;
        transition: 0.3s;
    }}

    div[data-testid="stRadio"] label:hover {{
        border-color: {gold_color};
    }}

    div[data-baseweb="select"] span {{
        background-color: #161B22 !important;
        border: 1px solid {gold_color} !important;
        color: {gold_color} !important;
        border-radius: 6px !important;
        padding: 2px 6px !important;
        font-size: 12px !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: #0B0E14 !important;
        border: 1px solid {gold_color} !important;
        border-radius: 6px !important;
    }}

    .card {{ background: #161B22; padding: 12px; border-radius: 12px; border: 1px solid {gold_color}; text-align: center; }}
    .value {{ font-size: 28px; font-weight: bold; color: {gold_color} !important; }}
    .label {{ font-size: 12px; color: {gold_color} !important; text-transform: uppercase; font-weight: 900; margin-bottom: 5px; opacity: 0.9; }}

    iframe {{ border: 2px solid {gold_color} !important; border-radius: 12px !important; }}
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
    except:
        return pd.DataFrame()

def get_random_image_by_type(obj_type):
    if obj_type == 'Clear': return "CLEAR_MODE"
    try:
        base_path = "assets"
        target_folder = str(obj_type).strip()
        full_path = os.path.join(base_path, target_folder)
        if not os.path.exists(full_path):
            full_path = os.path.join(base_path, target_folder.lower())
        if os.path.exists(full_path):
            images = [f for f in os.listdir(full_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                selected = random.choice(images)
                with open(os.path.join(full_path, selected), "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except: return None
    return None

df = load_data()

# ---------------- SIDEBAR (UPDATED ONLY) ----------------
st.sidebar.markdown("## 🛠️ FILTERS")

st.sidebar.markdown("### MAP DISPLAY MODE")
view_mode = st.sidebar.radio(
    "",
    ["Points", "Heatmap"],
    index=0,
    label_visibility="collapsed"
)

st.sidebar.markdown("### SELECT DEFECT CATEGORY")

if not df.empty:
    selected_types = st.sidebar.multiselect(
        "",
        options=df["Object"].unique(),
        default=list(df["Object"].unique()),
        label_visibility="collapsed"
    )
    df_plot = df[df["Object"].isin(selected_types)]
else:
    df_plot = df

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">Road Inspection Intelligence</div>', unsafe_allow_html=True)

# ---------------- KPI ROW ----------------
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"<div class='card'><div class='label'>TOTAL ASSETS</div><div class='value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='label'>CRACKS FOUND</div><div class='value'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='label'>POTHOLES</div><div class='value'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div
