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

# 2. Color Map (الألوان النهائية المعتمدة)
color_map = {
    'Clear': '#FACC15',      # أصفر
    'Crack': '#FF0000',      # أحمر
    'Manhole': '#0000FF',    # أزرق
    'Pothole': '#00FF00',    # أخضر
}

# 3. CSS Customization (Header Dark + Yellow Cards + Black Sidebar)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap');
    
    /* Dark Theme & Header */
    .stApp { background-color: #0B0E14; color: #FACC15; }
    header[data-testid="stHeader"] { background-color: #0B0E14 !important; }
    
    /* Main Title Style */
    .main-title { 
        color: #FACC15; font-family: 'Montserrat', sans-serif;
        font-size: 34px; font-weight: 900; text-align: left; 
        padding: 10px 0px 10px 15px; border-bottom: 2px solid #1F2937; 
        margin-bottom: 15px; letter-spacing: 2px;
        text-transform: uppercase; -webkit-text-stroke: 1.5px #000000;
        text-shadow: 3px 3px 0px #000000;
    }

    /* Cards - All Yellow */
    .card { background: #161B22; padding: 10px; border-radius: 12px; border: 1px solid #FACC15; text-align: center; }
    .value { font-size: 26px; font-weight: bold; color: #FACC15 !important; }
    .label { font-size: 13px; color: #FACC15 !important; text-transform: uppercase; font-weight: 800; }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #0B0E14 !important; border-right: 1px solid #1F2937; }
    section[data-testid="stSidebar"] .stMarkdown h2 { color: #FACC15; }
    .stRadio > label { color: #FACC15 !important; font-weight: bold; }
    
    /* Map Iframe */
    iframe { border: 2px solid #FACC15 !important; border-radius: 10px !important; }
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

# ---------------- SIDEBAR (تعديل الـ Sidebar بالكامل) ----------------
st.sidebar.markdown("<h2 style='text-align:center;'>🛠️ CONTROL PANEL</h2>", unsafe_allow_html=True)
view_mode = st.sidebar.radio("MAP DISPLAY MODE:", ["Points Map", "Heatmap Overlay"], index=0)

if not df.empty:
    st.sidebar.markdown("---")
    selected_types = st.sidebar.multiselect("SELECT FEATURES:", options=df["Object"].unique(), default=list(df["Object"].unique()))
    df_plot = df[df["Object"].isin(selected_types)]
else:
    df_plot = df

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">Road Inspection Intelligence</div>', unsafe_allow_html=True)

# ---------------- KPI ROW (تعديلات الألوان والكروت) ----------------
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"<div class='card'><div class='label'>TOTAL ASSETS</div><div class='value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='label'>CRACKS</div><div class='value'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='label'>POTHOLES</div><div class='value'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='label'>MANHOLES</div><div class='value'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

# ---------------- MAIN CONTENT ----------------
col1, col2, col3 = st.columns([1, 1.8, 1])

with col1:
    st.markdown("### Defect Ratio")
    if not df_plot.empty:
        fig1 = px.pie(df_plot, names='Object', hole=0.6, color='Object', color_discrete_map=color_map, height=320)
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15", showlegend=True, 
                          legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### Spatial Analysis Map")
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        
        if view_mode == "Points Map":
            for index, row in df_plot.iterrows():
                img_b64 = get_random_image_by_type(row['Object'])
                obj_id = row.get('OBJECTID', row.get('FID', index))
                color = color_map.get(row['Object'], "#FFF")
                
                if img_b64 == "CLEAR_MODE":
                    html_content = f'<div style="text-align:center;color:black;padding:10px;">ID: {obj_id}<br><b style="color:#FACC15; font-size:16px;">✅ ROAD IS CLEAR</b></div>'
                elif img_b64:
                    html_content = f'''
                    <div style="text-align:center; font-family: Montserrat; color:black;">
                        <h6 style="margin:2px; color:gray;">ID: {obj_id}</h6>
                        <h5 style="margin:5px; color:{color};">{row['Object']}</h5>
                        <img src="data:image/jpeg;base64,{img_b64}" style="width:150px; border-radius:5px; border:2px solid {color};">
                        <p style="margin:5px;"><b>Confidence: {row['Confidence']}%</b></p>
                    </div>'''
                else:
                    html_content = f'<div style="color:black;padding:10px;">ID: {obj_id}<br>Type: {row["Object"]}<br><b>Asset Missing</b></div>'

                folium.CircleMarker(
                    location=[row['Longitude'], row['Latitude']],
                    radius=8, color=color, fill=True, fill_opacity=0.9,
                    popup=folium.Popup(folium.IFrame(html_content, width=180, height=220))
                ).add_to(m)
        else:
            # Heatmap Mode
            heat_data = [[row['Longitude'], row['Latitude']] for index, row in df_plot.iterrows()]
            HeatMap(heat_data, radius=15, blur=10).add_to(m)
            
        st_folium(m, height=320, width="100%", key="main_map")

with col3:
    st.markdown("### Priority Alerts")
    critical = df_plot[(df_plot['Object'] != 'Clear') & (df_plot['Confidence'] > 90)]
    if not critical.empty:
        for r in critical.head(5).itertuples():
            st.error(f"⚠️ HIGH SEVERITY: {r.Object}")
    else:
        st.success("✅ Analysis Stable")

# ---------------- BOTTOM ROW ----------------
st.markdown("---")
c_low1, c_low2 = st.columns(2)
with c_low1:
    st.markdown("### Confidence Metrics")
    if not df_plot.empty:
        fig2 = px.histogram(df_plot, x='Confidence', color='Object', color_discrete_map=color_map, 
                           nbins=15, height=300)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15", plot_bgcolor='rgba(0,0,0,0)', 
                          showlegend=False, yaxis_title="Point Count", xaxis_title="Confidence %")
        st.plotly_chart(fig2, use_container_width=True)
with c_low2:
    st.markdown("### Defect Summary")
    if not df_plot.empty:
        fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map, height=300)
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15", plot_bgcolor='rgba(0,0,0,0)', 
                          showlegend=False, yaxis_title="Total Count")
        st.plotly_chart(fig3, use_container_width=True)
