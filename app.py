import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, Fullscreen
import plotly.express as px
import base64
import os
import random
from PIL import Image  # المكتبة الجديدة لمعالجة الصور
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

    .card {{ 
        background: #161B22; padding: 12px; border-radius: 12px; 
        border: 1px solid {gold_color}; text-align: center;
        transition: transform 0.3s ease;
    }}
    .card:hover {{ transform: translateY(-5px); box-shadow: 0px 4px 15px rgba(255, 215, 0, 0.2); }}
    
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

# --- الدالة المحدثة لمعالجة الصور بصورة احترافية ---
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
                
                # تصغير حجم الصورة لتحسين أداء الخريطة
                with Image.open(img_path) as img:
                    img = img.convert('RGB')
                    img.thumbnail((250, 250)) # أقصى عرض 250 بكسل
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG", quality=80)
                    return base64.b64encode(buffered.getvalue()).decode()
    except: return None
    return None

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🛠️ FILTERS")

st.sidebar.markdown("### MAP DISPLAY MODE")
view_mode = st.sidebar.radio("", ["Points", "Heatmap"], index=0, label_visibility="collapsed")

st.sidebar.markdown("### SELECT DEFECT CATEGORY")
if not df.empty:
    selected_types = st.sidebar.multiselect(
        "", options=df["Object"].unique(), 
        default=list(df["Object"].unique()), label_visibility="collapsed"
    )
    df_plot = df[df["Object"].isin(selected_types)]
else:
    df_plot = df

# زر تحميل التقرير
st.sidebar.markdown("---")
if not df_plot.empty:
    csv = df_plot.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Download Report", data=csv, file_name='road_report.csv', mime='text/csv')

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">Road Inspection Intelligence</div>', unsafe_allow_html=True)

# ---------------- KPI ROW ----------------
c1, c2, c3, c4 = st.columns(4)
stats = {obj: len(df_plot[df_plot['Object'] == obj]) for obj in ['Crack', 'Pothole', 'Manhole']}
c1.markdown(f"<div class='card'><div class='label'>TOTAL ASSETS</div><div class='value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='label'>CRACKS FOUND</div><div class='value'>{stats['Crack']}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='label'>POTHOLES</div><div class='value'>{stats['Pothole']}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='label'>MANHOLES</div><div class='value'>{stats['Manhole']}</div></div>", unsafe_allow_html=True)

# ---------------- MAIN CONTENT ----------------
col1, col2, col3 = st.columns([1, 1.8, 1])

with col1:
    st.markdown("### Defect Ratio")
    if not df_plot.empty:
        fig1 = px.pie(df_plot, names='Object', hole=0.6, color='Object', color_discrete_map=color_map, height=320)
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color=gold_color, showlegend=True, 
                          legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### Spatial View")
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        Fullscreen().add_to(m) # إضافة وضع ملء الشاشة
        
        if view_mode == "Points":
            for index, row in df_plot.iterrows():
                img_b64 = get_random_image_by_type(row['Object'])
                color = color_map.get(row['Object'], "#FFF")
                
                if img_b64 == "CLEAR_MODE":
                    html_content = f'<div style="text-align:center;color:black;padding:10px;"><b>✅ STATUS: CLEAR</b></div>'
                elif img_b64:
                    html_content = f'''
                    <div style="text-align:center; font-family: Montserrat; color:black; width:160px;">
                        <h5 style="margin:5px; color:{color};">{row['Object']}</h5>
                        <img src="data:image/jpeg;base64,{img_b64}" style="width:100%; border-radius:8px; border:2px solid {color}; box-shadow: 0px 2px 5px rgba(0,0,0,0.2);">
                        <p style="margin:5px; font-size:12px;"><b>Confidence: {row['Confidence']}%</b></p>
                    </div>'''
                else:
                    html_content = f'<div style="color:black;padding:10px;">Loading Image...</div>'

                folium.CircleMarker(
                    location=[row['Longitude'], row['Latitude']],
                    radius=8, color=color, fill=True, fill_opacity=0.9,
                    popup=folium.Popup(folium.IFrame(html_content, width=190, height=230))
                ).add_to(m)
        else:
            heat_data = [[row['Longitude'], row['Latitude']] for index, row in df_plot.iterrows()]
            HeatMap(heat_data, radius=15, blur=10).add_to(m)
            
        st_folium(m, height=320, width="100%", key="main_map")

with col3:
    st.markdown("### Priority Alerts")
    critical = df_plot[(df_plot['Object'] != 'Clear') & (df_plot['Confidence'] > 90)]
    if not critical.empty:
        for r in critical.head(5).itertuples():
            st.error(f"⚠️ CRITICAL: {r.Object} ({r.Confidence}%)")
    else:
        st.success("✅ System Stable")

# ---------------- BOTTOM ROW ----------------
st.markdown("---")
c_low1, c_low2 = st.columns(2)
with c_low1:
    if not df_plot.empty:
        fig2 = px.histogram(df_plot, x='Confidence', color='Object', color_discrete_map=color_map, nbins=15, height=300)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color=gold_color, plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
with c_low2:
    if not df_plot.empty:
        fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map, height=300)
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color=gold_color, plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
