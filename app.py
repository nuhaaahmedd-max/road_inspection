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

# 2. Color Map (الألوان المطلوبة: أصفر، بينك، جرين، أورنج)
color_map = {
    'Crack': '#FF69B4',      # بينك (Hot Pink)
    'Pothole': '#FB923C',    # أورنج
    'Manhole': '#FACC15',    # أصفر
    'Clear': '#34D399',      # جرين
}

# 3. CSS Customization
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap');
    html, body, [class*="css"]  { height: 100vh; overflow: hidden !important; }
    .stApp { background-color: #0B0E14; color: #FACC15; }
    header[data-testid="stHeader"] { background: rgba(0,0,0,0) !important; }
    #MainMenu, footer, .stDeployButton { visibility: hidden; }
    .main .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; }
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
    .value { font-size: 22px; font-weight: bold; color: #FACC15; }
    .label { font-size: 12px; color: #9CA3AF; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADING ----------------
@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv("road_data.csv")
        # بنفلتر الداتا على الـ 4 أنواع المطلوبة بس
        valid_objects = ['Crack', 'Pothole', 'Manhole', 'Clear']
        df = df[df['Object'].isin(valid_objects)]
        df = df.dropna(subset=['Latitude', 'Longitude'])
        return df
    except:
        return pd.DataFrame()

# ✅ الدالة الجديدة: اختيار صورة عشوائية بناءً على النوع (مع استثناء Clear)
def get_random_image_by_type(obj_type):
    if obj_type == 'Clear':
        return "CLEAR_MODE" # علامة عشان الكود يفهم إن مفيش صورة هنا
    
    try:
        # المسار للفولدر (assets/Crack أو assets/Pothole إلخ)
        folder_path = os.path.join("assets", str(obj_type))
        if os.path.exists(folder_path):
            images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                selected = random.choice(images)
                with open(os.path.join(folder_path, selected), "rb") as f:
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

# ---------------- HEADER & KPIs ----------------
st.markdown('<div class="main-title">Road Inspection Intelligence</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
def card_html(t, v): return f"<div class='card'><div class='label'>{t}</div><div class='value'>{v}</div></div>" 
c1.markdown(card_html("TOTAL POINTS", len(df_plot)), unsafe_allow_html=True)
cracks_count = len(df_plot[df_plot['Object'] == 'Crack'])
c2.markdown(card_html("CRACKS DETECTED", cracks_count), unsafe_allow_html=True)
avg_conf = df_plot['Confidence'].mean() if not df_plot.empty else 0
c3.markdown(card_html("AVG CONFIDENCE", f"{avg_conf:.1f}%"), unsafe_allow_html=True)
c4.markdown(card_html("SYSTEM STATUS", "ACTIVE"), unsafe_allow_html=True)

# ---------------- MAIN CONTENT ----------------
col1, col2, col3 = st.columns([1, 1.8, 1])

with col1:
    st.markdown("### Defect Ratio")
    if not df_plot.empty:
        fig1 = px.pie(df_plot, names='Object', hole=0.6, color='Object', color_discrete_map=color_map, height=320)
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15", showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### Spatial View")
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        
        for index, row in df_plot.iterrows():
            img_b64 = get_random_image_by_type(row['Object'])
            obj_id = row.get('FID', row.get('ObjectID', index))
            
            if img_b64 == "CLEAR_MODE":
                # شكل الـ Popup في حالة الـ Clear (بدون صورة)
                html_content = f'''
                <div style="text-align:center; font-family: Montserrat; color:black; padding:10px;">
                    <b style="color:green; font-size:16px;">✅ ROAD IS CLEAR</b><br>
                    <span>Point ID: {obj_id}</span>
                </div>'''
            elif img_b64:
                # شكل الـ Popup العادي بالصور العشوائية
                html_content = f'''
                <div style="text-align:center; font-family: Montserrat; color:black;">
                    <h6 style="margin:2px; color:gray;">ID: {obj_id}</h6>
                    <h5 style="margin:5px;">{row['Object']}</h5>
                    <img src="data:image/jpeg;base64,{img_b64}" style="width:150px; border-radius:5px; border:2px solid #FACC15;">
                    <p style="margin:5px;"><b>Confidence: {row['Confidence']}%</b></p>
                </div>'''
            else:
                html_content = f'<div style="color:black; padding:10px;">ID: {obj_id}<br>Type: {row["Object"]}<br>Sample Missing</div>'

            folium.CircleMarker(
                location=[row['Longitude'], row['Latitude']],
                radius=7, color=color_map.get(row['Object'], "#FFF"), fill=True,
                fill_opacity=0.8,
                tooltip=f"ID: {obj_id} | {row['Object']}",
                popup=folium.Popup(folium.IFrame(html_content, width=180, height=220))
            ).add_to(m)
            
        st_folium(m, height=320, width="100%", key="main_map")

with col3:
    st.markdown("### Priority Alerts")
    critical = df_plot[(df_plot['Object'] != 'Clear') & (df_plot['Confidence'] > 90)]
    if not critical.empty:
        for r in critical.head(5).itertuples():
            st.error(f"⚠️ HIGH SEVERITY: {r.Object}")
    else:
        st.success("✅ No Critical Issues")

# ---------------- BOTTOM ROW ----------------
st.markdown("---")
c_low1, c_low2 = st.columns(2)
with c_low1:
    if not df_plot.empty:
        fig2 = px.histogram(df_plot, x='Confidence', color='Object', color_discrete_map=color_map, height=300)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
with c_low2:
    if not df_plot.empty:
        fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map, height=300)
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)
