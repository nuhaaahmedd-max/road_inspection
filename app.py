import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import base64
import os
import random

# 1. Configuration
st.set_page_config(layout="wide", page_title="Road Inspection AI", initial_sidebar_state="expanded")

# 2. Color Map (الألوان المطلوبة: الأصفر والبينك هما الأساس)
color_map = {
    'Crack': '#FF69B4',      # بينك فاقع (Hot Pink) - هيظهر كتير
    'Manhole': '#FACC15',    # أصفر زاهي - هيظهر كتير
    'Pothole': '#60A5FA',    # أزرق (Sky Blue) - هيظهر قليل
    'Clear': '#34D399',      # أخضر هادي - هيظهر قليل
}

# 3. CSS Customization
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap');
    .stApp { background-color: #0B0E14; color: #FACC15; }
    .main-title { 
        color: #FACC15; font-family: 'Montserrat', sans-serif;
        font-size: 34px; font-weight: 900; text-align: left; 
        padding: 10px 0px 10px 15px; border-bottom: 2px solid #1F2937; 
        margin-bottom: 15px; letter-spacing: 2px;
        text-transform: uppercase; -webkit-text-stroke: 1.5px #000000;
        text-shadow: 3px 3px 0px #000000;
    }
    iframe { border: 2px solid #FACC15 !important; border-radius: 10px !important; }
    .card { background: #161B22; padding: 10px; border-radius: 12px; border: 1px solid #FACC15; text-align: center; }
    .value { font-size: 24px; font-weight: bold; color: #FACC15; }
    .label { font-size: 12px; color: #9CA3AF; text-transform: uppercase; }
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
    if obj_type == 'Clear':
        return "CLEAR_MODE"
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
    except:
        return None
    return None

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("<h2 style='text-align:center;'>🛠️ FILTERS</h2>", unsafe_allow_html=True)
if not df.empty:
    selected_types = st.sidebar.multiselect("SELECT DEFECT:", options=df["Object"].unique(), default=list(df["Object"].unique()))
    df_plot = df[df["Object"].isin(selected_types)]
else:
    df_plot = df

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">Road Inspection Intelligence</div>', unsafe_allow_html=True)

# ---------------- KPI ROW ----------------
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"<div class='card'><div class='label'>TOTAL POINTS</div><div class='value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='label'>CRACKS</div><div class='value' style='color:#FF69B4;'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='label'>RELIABILITY</div><div class='value'>{df_plot['Confidence'].mean() if not df_plot.empty else 0:.1f}%</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='label'>MANHOLES</div><div class='value' style='color:#FACC15;'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

# ---------------- MAIN CONTENT ----------------
col1, col2, col3 = st.columns([1, 1.8, 1])

with col1:
    st.markdown("### Defect Distribution")
    if not df_plot.empty:
        # شارت الدونات بالألوان الجديدة
        fig1 = px.pie(df_plot, names='Object', hole=0.6, color='Object', color_discrete_map=color_map, height=320)
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15", showlegend=True, 
                          legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### Spatial Analysis Map")
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        for index, row in df_plot.iterrows():
            img_b64 = get_random_image_by_type(row['Object'])
            obj_id = row.get('OBJECTID', row.get('FID', index))
            
            if img_b64 == "CLEAR_MODE":
                html_content = f'<div style="text-align:center;color:black;padding:10px;"><b>✅ ROAD IS CLEAR</b><br>ID: {obj_id}</div>'
            elif img_b64:
                html_content = f'''
                <div style="text-align:center; font-family: Montserrat; color:black;">
                    <h6 style="margin:2px; color:gray;">ID: {obj_id}</h6>
                    <h5 style="margin:5px; color:{color_map.get(row['Object'])};">{row['Object']}</h5>
                    <img src="data:image/jpeg;base64,{img_b64}" style="width:150px; border-radius:5px; border:2px solid {color_map.get(row['Object'])};">
                    <p style="margin:5px;"><b>Confidence: {row['Confidence']}%</b></p>
                </div>'''
            else:
                html_content = f'<div style="color:black;padding:10px;">ID: {obj_id}<br>Type: {row["Object"]}<br><b>Check Folder: assets/{row["Object"]}</b></div>'

            folium.CircleMarker(
                location=[row['Longitude'], row['Latitude']],
                radius=8, color=color_map.get(row['Object'], "#FFF"), fill=True, fill_opacity=0.9,
                popup=folium.Popup(folium.IFrame(html_content, width=180, height=220))
            ).add_to(m)
        st_folium(m, height=320, width="100%", key="main_map")

with col3:
    st.markdown("### Priority Alerts")
    critical = df_plot[(df_plot['Object'] != 'Clear') & (df_plot['Confidence'] > 90)]
    if not critical.empty:
        for r in critical.head(5).itertuples():
            st.error(f"⚠️ HIGH CONFIDENCE: {r.Object}")
    else:
        st.success("✅ Area Analysis Stable")

# ---------------- BOTTOM ROW ----------------
st.markdown("---")
c_low1, c_low2 = st.columns(2)
with c_low1:
    if not df_plot.empty:
        # الهيستوجرام بالألوان الجديدة
        fig2 = px.histogram(df_plot, x='Confidence', color='Object', color_discrete_map=color_map, 
                           nbins=20, barmode='group', height=300)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15", plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
with c_low2:
    if not df_plot.empty:
        # البار شارت بالألوان الجديدة
        fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map, height=300)
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15", plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
