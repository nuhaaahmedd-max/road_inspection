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

# 3. CSS Customization (تم تعديل الـ main-title هنا بناءً على طلبك)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap');
    
    .block-container {{ 
        padding-top: 1rem !important; 
        padding-bottom: 0rem !important; 
        max-width: 98% !important;
    }}

    .stApp {{ background-color: #0B0E14; color: {gold_color}; }}
    header[data-testid="stHeader"] {{ background-color: #0B0E14 !important; visibility: hidden !important; }}
    
    .main-title {{ 
        color: #FFD700; 
        font-family: 'Montserrat', sans-serif;
        font-size: 22px; 
        font-weight: 800; 
        text-align: center; 
        padding: 5px 0px; 
        margin-bottom: 5px; 
        letter-spacing: 1px;
        text-transform: uppercase;
        text-shadow: 1px 1px 2px #000000;
        width: 100%;
    }}

    section[data-testid="stSidebar"] {{ background-color: #0B0E14 !important; border-right: 1px solid #1F2937; }}
    
    .card {{ 
        background: #161B22; padding: 5px; border-radius: 10px; 
        border: 1px solid {gold_color}; text-align: center;
    }}
    
    .value {{ font-size: 22px; font-weight: bold; color: {gold_color} !important; }}
    .label {{ font-size: 10px; color: {gold_color} !important; text-transform: uppercase; opacity: 0.8; }}

    iframe {{ border: 1px solid {gold_color} !important; border-radius: 8px !important; }}
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

@st.cache_data(show_spinner=False)
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

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🛠️ FILTERS")
view_mode = st.sidebar.radio("MAP DISPLAY MODE", ["Points", "Heatmap"], index=0)

if not df.empty:
    selected_types = st.sidebar.multiselect(
        "SELECT DEFECT CATEGORY", options=df["Object"].unique(), 
        default=list(df["Object"].unique())
    )
    df_plot = df[df["Object"].isin(selected_types)]
else:
    df_plot = df

st.sidebar.markdown("---")
if not df_plot.empty:
    csv = df_plot.to_csv(index=False).encode('utf-8')
    st.
