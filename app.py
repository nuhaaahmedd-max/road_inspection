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
st.set_page_config(layout="wide", page_title="Fusion Road AI", initial_sidebar_state="expanded")

# 2. Colors based on the Image
color_map = {
    'Clear': '#FFD700',
    'Crack': '#E91E63', # Pinkish Red
    'Manhole': '#2196F3', # Blue
    'Pothole': '#4CAF50', # Green
}

# 3. CSS for "Fusion" Style (Light Mode Dashboard)
st.markdown("""
<style>
    /* Global Styles */
    .stApp { background-color: #F4F7FE; color: #2B3674; }
    header[data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
        border-right: 1px solid #E0E5F2; 
    }
    section[data-testid="stSidebar"] .stMarkdown h2 { color: #2B3674; font-weight: 800; }
    
    /* Top Metric Cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 14px 17px 40px 4px rgba(112, 144, 176, 0.08);
        text-align: left;
    }
    .metric-label { font-size: 14px; color: #A3AED0; font-weight: 500; margin-bottom: 5px; }
    .metric-value { font-size: 24px; color: #2B3674; font-weight: 700; }
    
    /* Main Content Containers */
    .content-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 14px 17px 40px 4px rgba(112, 144, 176, 0.08);
        margin-bottom: 20px;
    }
    
    h3 { color: #2B3674; font-weight: 700 !important; font-size: 20px !important; }
    
    /* Custom Map Border */
    iframe { border-radius: 15px !important; border: none !important; }
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
with st.sidebar:
    st.markdown("## ⚙️ Navigation")
    view_mode = st.radio("Display Mode", ["Points View", "Heatmap View"])
    
    st.markdown("### Asset Filters")
    if not df.empty:
        selected_types = st.multiselect(
            "Select Categories", 
            options=df["Object"].unique(), 
            default=list(df["Object"].unique())
        )
        df_plot = df[df["Object"].isin(selected_types)]
    else:
        df_plot = df

# ---------------- TOP KPI ROW ----------------
st.markdown("<h2 style='color: #2B3674; margin-bottom:20px;'>Main Dashboard</h2>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
stats = {obj: len(df_plot[df_plot['Object'] == obj]) for obj in ['Crack', 'Pothole', 'Manhole']}

c1.markdown(f"<div class='metric-card'><div class='metric-label'>Total Assets</div><div class='metric-value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card'><div class='metric-label'>Cracks</div><div class='metric-value' style='color:#E91E63;'>{stats['Crack']}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card'><div class='metric-label'>Potholes</div><div class='metric-value' style='color:#4CAF50;'>{stats['Pothole']}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='metric-card'><div class='metric-label'>Manholes</div><div class='metric-value' style='color:#2196F3;'>{stats['Manhole']}</div></div>", unsafe_allow_html=True)

st.write("") # Spacer

# ---------------- MIDDLE ROW (THE BIG CHART AREA -> MAP) ----------------
# هنا استبدلنا الشارت الكبير بالخريطة كما في صورة Fusion
st.markdown("<div class='content-card'>", unsafe_allow_html=True)
st.markdown("### 🗺️ Live Road Map Intelligence")

if not df_plot.empty:
    m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB Positron")
    Fullscreen().add_to(m)
    
    if "Points" in view_mode:
        for index, row in df_plot.iterrows():
            img_b64 = get_random_image_by_type(row['Object'])
            color = color_map.get(row['Object'], "#2B3674")
            
            html_content = f'''
            <div style="text-align:center; font-family: 'Helvetica'; width:160px;">
                <h5 style="margin:5px; color:{color};">{row['Object']}</h5>
                <img src="data:image/jpeg;base64,{img_b64}" style="width:100%; border-radius:10px;">
                <p style="margin:5px; font-size:12px; color:#A3AED0;">Confidence: <b>{row['Confidence']}%</b></p>
            </div>''' if img_b64 and img_b64 != "CLEAR_MODE" else f"<b>{row['Object']}</b>"

            folium.CircleMarker(
                location=[row['Longitude'], row['Latitude']],
                radius=10, color=color, fill=True, fill_opacity=0.7,
                popup=folium.Popup(folium.IFrame(html_content, width=190, height=230))
            ).add_to(m)
    else:
        heat_data = [[row['Longitude'], row['Latitude']] for index, row in df_plot.iterrows()]
        HeatMap(heat_data, radius=15).add_to(m)
        
    st_folium(m, height=450, width="100%", key="fusion_map")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- BOTTOM ROW (2 COLUMNS) ----------------
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### 📊 Distribution Analysis")
    if not df_plot.empty:
        fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map, barmode='group')
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          margin=dict(l=0, r=0, t=20, b=0), height=300, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### 🔔 Priority Alerts")
    critical = df_plot[(df_plot['Object'] != 'Clear') & (df_plot['Confidence'] > 90)]
    if not critical.empty:
        for r in critical.head(4).itertuples():
            st.warning(f"**High Confidence {r.Object}** - Loc: {r.Longitude:.2f}")
    else:
        st.success("All systems clear")
    st.markdown("</div>", unsafe_allow_html=True)
