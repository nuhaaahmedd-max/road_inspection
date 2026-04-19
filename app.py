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

# 2. Color Map
color_map = {
    'Clear': '#FFD700',
    'Crack': '#FF0000',
    'Manhole': '#0070FF',
    'Pothole': '#00FF00',
}
gold_color = "#FFD700"

# 3. CSS
st.markdown(f"""
<style>
    .stApp {{ background-color: #0B0E14; color: {gold_color}; }}
    header[data-testid="stHeader"] {{ background-color: #0B0E14 !important; }}

    .main-title {{ 
        color: {gold_color};
        font-size: 34px; font-weight: 900;
        border-bottom: 2px solid #1F2937;
        margin-bottom: 15px;
    }}

    section[data-testid="stSidebar"] {{ background-color: #0B0E14 !important; }}

    section[data-testid="stSidebar"] h2 {{
        font-size: 20px;
        margin-bottom: 15px;
    }}

    section[data-testid="stSidebar"] h3 {{
        font-size: 13px;
        margin-top: 15px;
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
    }}

    div[data-baseweb="select"] span {{
        background-color: #161B22 !important;
        border: 1px solid {gold_color} !important;
        color: {gold_color} !important;
        border-radius: 6px !important;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- SAFE DATA LOADING ----------------
@st.cache_data(ttl=300)
def load_data():
    try:
        if not os.path.exists("road_data.csv"):
            st.warning("⚠️ road_data.csv not found")
            return pd.DataFrame()

        df = pd.read_csv("road_data.csv")

        required_cols = ['Object', 'Latitude', 'Longitude', 'Confidence']
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Missing column: {col}")
                return pd.DataFrame()

        valid_objects = ['Crack', 'Pothole', 'Manhole', 'Clear']
        df = df[df['Object'].isin(valid_objects)]
        df = df.dropna(subset=['Latitude', 'Longitude'])

        return df

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# ---------------- SAFE IMAGE LOADING ----------------
def get_random_image_by_type(obj_type):
    if obj_type == 'Clear':
        return "CLEAR_MODE"
    try:
        base_path = "assets"
        if not os.path.exists(base_path):
            return None

        folder = os.path.join(base_path, str(obj_type))
        if not os.path.exists(folder):
            folder = os.path.join(base_path, str(obj_type).lower())

        if os.path.exists(folder):
            images = [f for f in os.listdir(folder) if f.endswith(('.jpg', '.png'))]
            if images:
                img = random.choice(images)
                with open(os.path.join(folder, img), "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except:
        return None
    return None

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🛠️ FILTERS")

st.sidebar.markdown("### MAP DISPLAY MODE")
view_mode = st.sidebar.radio("", ["Points", "Heatmap"], label_visibility="collapsed")

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

# ---------------- EMPTY STATE ----------------
if df_plot.empty:
    st.warning("⚠️ No data available to display")
    st.stop()

# ---------------- KPI ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("TOTAL", len(df_plot))
c2.metric("CRACKS", len(df_plot[df_plot['Object']=='Crack']))
c3.metric("POTHOLES", len(df_plot[df_plot['Object']=='Pothole']))
c4.metric("MANHOLES", len(df_plot[df_plot['Object']=='Manhole']))

# ---------------- MAP ----------------
st.markdown("### Spatial View")

m = folium.Map(
    location=[df_plot['Latitude'].mean(), df_plot['Longitude'].mean()],
    zoom_start=15,
    tiles="CartoDB dark_matter"
)

if view_mode == "Points":
    for _, row in df_plot.iterrows():
        color = color_map.get(row['Object'], "#FFF")

        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=7,
            color=color,
            fill=True
        ).add_to(m)
else:
    heat_data = df_plot[['Latitude','Longitude']].values.tolist()
    HeatMap(heat_data).add_to(m)

st_folium(m, height=350, width="100%")
