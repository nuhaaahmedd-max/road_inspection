import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import plotly.express as px
import base64
import os

# 1. Configuration
st.set_page_config(layout="wide", page_title="Road Inspection AI", initial_sidebar_state="expanded")

# 2. Color Map
color_map = {
    'Crack': '#F87171',      
    'Clear': '#34D399',      
    'Pothole': '#FB923C',    
    'Manhole': '#A78BFA',    
    'speed bump': '#60A5FA', 
    'Lamp_Post': '#FACC15'   
}

# 3. CSS Customization
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap');

    html, body, [class*="css"]  {
        height: 100vh;
        overflow: hidden !important;
    }

    .stApp { background-color: #0B0E14; color: #FACC15; }
    header[data-testid="stHeader"] { background: rgba(0,0,0,0) !important; color: #FACC15 !important; }
    #MainMenu, footer, .stDeployButton { visibility: hidden; }

    .main .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 0rem !important; 
        height: 100vh;
        overflow: hidden;
    }

    section.main > div {
        height: 100vh;
        overflow: hidden;
    }

    .element-container {
        margin-bottom: 0.4rem !important;
    }

    [data-testid="column"] {
        height: 100%;
    }

    .main-title { 
        color: #FACC15; 
        font-family: 'Montserrat', sans-serif;
        font-size: 34px; 
        font-weight: 900; 
        text-align: left; 
        padding: 10px 0px 10px 15px; 
        border-bottom: 2px solid #1F2937; 
        margin-bottom: 15px; 
        letter-spacing: 2px;
        text-transform: uppercase;
        -webkit-text-stroke: 1.5px #000000;
        text-shadow: 3px 3px 0px #000000;
    }

    iframe {
        border: 2px solid #FACC15 !important;
        border-radius: 10px !important;
        height: 320px !important;
    }

    [data-testid="stSidebar"] label p, 
    [data-testid="stSidebar"] span p,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p { 
        color: #FACC15 !important; 
    }

    div[data-baseweb="radio"] div { border-color: #FACC15 !important; }
    div[data-baseweb="radio"] div::after { background-color: #FACC15 !important; }
    div[data-baseweb="slider"] > div > div > div { background-color: #FACC15 !important; }
    div[data-baseweb="slider"] > div > div { background-color: #FACC15 !important; }

    span[data-baseweb="tag"] { 
        background-color: transparent !important; 
        border: 1.5px solid #FACC15 !important; 
        color: #FACC15 !important; 
        font-weight: bold;
    }

    div[data-baseweb="select"] > div { 
        background-color: #161B22 !important; 
        border: 1px solid #FACC15 !important; 
        color: #FACC15 !important; 
    }

    [data-testid="stSidebar"] { 
        background-color: #05070A !important; 
        border-right: 2px solid #FACC15; 
    }

    .card { 
        background: #161B22; 
        padding: 10px; 
        border-radius: 12px; 
        border: 1px solid #FACC15; 
        text-align: center; 
    }

    .value { font-size: 22px; font-weight: bold; color: #FACC15; }
    .label { font-size: 12px; color: #9CA3AF; text-transform: uppercase; }

    .stAlert { 
        background-color: #161B22 !important; 
        border: 1px solid #FACC15 !important; 
        color: #FACC15 !important; 
    }
</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADING ----------------

@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv("road_data.csv")
        df = df.dropna(subset=['Latitude','Longitude'])
        return df
    except:
        data = {
            'Latitude': [30.0444, 30.0450, 30.0460, 30.0470],
            'Longitude': [31.2357, 31.2360, 31.2370, 31.2380],
            'Object': ['Crack', 'Clear', 'Crack', 'Pothole'],
            'Confidence': [95, 88, 92, 85]
        }
        return pd.DataFrame(data)

# قراءة الصورة
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

df = load_data()
df_plot = df.copy()

# ---------------- SIDEBAR ----------------

st.sidebar.markdown("<h2 style='text-align:center;'>🛠️ FILTERS</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---") 
view = st.sidebar.radio("MAP DISPLAY MODE:", ["Points", "Heatmap"], index=0)
selected_types = st.sidebar.multiselect("SELECT DEFECT CATEGORY:", options=df_plot["Object"].unique(), default=list(df_plot["Object"].unique()))
confidence_min = st.sidebar.slider("MIN CONFIDENCE %:", 0, 100, 0)

df_plot = df_plot[df_plot["Object"].isin(selected_types)]
df_plot = df_plot[df_plot["Confidence"] >= confidence_min]
cracks = df_plot[df_plot['Object'] == "Crack"]

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">Road Inspection Intelligence</div>', unsafe_allow_html=True)

# ---------------- KPI ROW ----------------
c1, c2, c3, c4 = st.columns(4)
def card_html(t, v): return f"<div class='card'><div class='label'>{t}</div><div class='value'>{v}</div></div>" 
c1.markdown(card_html("TOTAL ASSETS", len(df_plot)), unsafe_allow_html=True)
c2.markdown(card_html("CRACKS FOUND", len(cracks)), unsafe_allow_html=True)
avg_conf = df_plot['Confidence'].mean() if not df_plot.empty else 0
c3.markdown(card_html("AVG RELIABILITY", f"{avg_conf:.1f}%"), unsafe_allow_html=True)
c4.markdown(card_html("SEVERITY STATUS", "HIGH" if len(cracks) > 10 else "NORMAL"), unsafe_allow_html=True)

# ---------------- MAIN CONTENT ----------------
col1, col2, col3 = st.columns([1, 1.8, 1])

with col1:
    st.markdown("### Defect Ratio")
    fig1 = px.pie(df_plot, names='Object', hole=0.6, color='Object', color_discrete_map=color_map, height=320)
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown(f"### Spatial View ({view})")
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        
        if view == "Points":
            for r in df_plot.itertuples():
                p_color = color_map.get(r.Object, "#FFFFFF") 

                img_base64 = None
                for file in os.listdir("assets"):
                    if str(r.Image).replace(".jpg","") in file:
                        img_path = os.path.join("assets", file)
                        img_base64 = get_base64_image(img_path)
                        break

                if img_base64:
                    img_html = f"""
                    <div style="text-align:center;">
                        <h4 style="color:black;">{r.Object}</h4>
                        <img src="data:image/jpeg;base64,{img_base64}" style="width:180px;border-radius:10px;">
                        <p style="color:black;">Confidence: {r.Confidence}%</p>
                    </div>
                    """
                else:
                    img_html = "<p style='color:black;'>No Image</p>"

                iframe = folium.IFrame(html=img_html, width=200, height=220)
                popup = folium.Popup(iframe, max_width=250)

                folium.CircleMarker(
                    location=[r.Longitude, r.Latitude],
                    radius=6,
                    color=p_color,
                    fill=True,
                    fill_opacity=0.8,
                    popup=popup
                ).add_to(m)

        else:
            heat_data = [[r.Longitude, r.Latitude, r.Confidence] for r in df_plot.itertuples()]
            HeatMap(heat_data, radius=18, blur=12).add_to(m)
        
        st_folium(m, height=320, width="100%", key=f"map_{view}")
    else:
        st.warning("No data available.")

with col3:
    st.markdown("### Priority Alerts")
    critical = cracks[cracks["Confidence"] > 90]
    if not critical.empty:
        for r in critical.head(5).itertuples():
            st.warning(f"⚠️ CRITICAL | {r.Confidence}% Confidence")
    else:
        st.success("✅ System Clear")

st.markdown("---")

# ---------------- BOTTOM ----------------
c_low1, c_low2 = st.columns(2)

with c_low1:
    st.markdown("### Confidence Distribution")
    fig2 = px.histogram(df_plot, x='Confidence', height=320)
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15")
    st.plotly_chart(fig2, use_container_width=True)

with c_low2:
    st.markdown("### Asset Analysis by Type")
    fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map, height=320)
    fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15")
    st.plotly_chart(fig3, use_container_width=True)
