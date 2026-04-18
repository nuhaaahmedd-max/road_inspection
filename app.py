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

# 3. CSS Customization (كودك الأصلي)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap');
    html, body, [class*="css"]  { height: 100vh; overflow: hidden !important; }
    .stApp { background-color: #0B0E14; color: #FACC15; }
    header[data-testid="stHeader"] { background: rgba(0,0,0,0) !important; color: #FACC15 !important; }
    #MainMenu, footer, .stDeployButton { visibility: hidden; }
    .main .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; height: 100vh; overflow: hidden; }
    .main-title { 
        color: #FACC15; font-family: 'Montserrat', sans-serif;
        font-size: 34px; font-weight: 900; text-align: left; 
        padding: 10px 0px 10px 15px; border-bottom: 2px solid #1F2937; 
        margin-bottom: 15px; letter-spacing: 2px;
        text-transform: uppercase; -webkit-text-stroke: 1.5px #000000;
        text-shadow: 3px 3px 0px #000000;
    }
    iframe { border: 2px solid #FACC15 !important; border-radius: 10px !important; height: 320px !important; }
    .card { background: #161B22; padding: 10px; border-radius: 12px; border: 1px solid #FACC15; text-align: center; }
    .value { font-size: 22px; font-weight: bold; color: #FACC15; }
    .label { font-size: 12px; color: #9CA3AF; text-transform: uppercase; }
    .stAlert { background-color: #161B22 !important; border: 1px solid #FACC15 !important; color: #FACC15 !important; }
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
        return pd.DataFrame()

# ✅ الدالة المعدلة: بتبحث باسم الملف المكتوب في عمود Image
def get_base64_image(image_name_from_excel):
    try:
        if not os.path.exists("assets") or pd.isna(image_name_from_excel):
            return None
        
        # بنجيب اسم الملف ونشيل منه أي مسافات زيادة
        target_file = str(image_name_from_excel).strip()
        
        # بنحاول نفتح الملف مباشرة من فولدر assets
        img_path = os.path.join("assets", target_file)
        
        if os.path.exists(img_path):
            with open(img_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        else:
            # لو ملقاش الاسم بالظبط، بيدور على أي ملف جوه الفولدر فيه نفس الاسم (احتياطي)
            all_imgs = os.listdir("assets")
            match = [f for f in all_imgs if target_file in f]
            if match:
                with open(os.path.join("assets", match[0]), "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode()
    except:
        return None
    return None

df = load_data()
df_plot = df.copy()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("<h2 style='text-align:center;'>🛠️ FILTERS</h2>", unsafe_allow_html=True)
view = st.sidebar.radio("MAP DISPLAY MODE:", ["Points", "Heatmap"], index=0)
if not df_plot.empty:
    selected_types = st.sidebar.multiselect("SELECT DEFECT:", options=df_plot["Object"].unique(), default=list(df_plot["Object"].unique()))
    confidence_min = st.sidebar.slider("MIN CONFIDENCE %:", 0, 100, 0)
    df_plot = df_plot[df_plot["Object"].isin(selected_types) & (df_plot["Confidence"] >= confidence_min)]

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">Road Inspection Intelligence</div>', unsafe_allow_html=True)

# ---------------- KPI ROW ----------------
c1, c2, c3, c4 = st.columns(4)
def card_html(t, v): return f"<div class='card'><div class='label'>{t}</div><div class='value'>{v}</div></div>" 
c1.markdown(card_html("TOTAL ASSETS", len(df_plot)), unsafe_allow_html=True)
cracks = df_plot[df_plot['Object'] == "Crack"]
c2.markdown(card_html("CRACKS FOUND", len(cracks)), unsafe_allow_html=True)
avg_conf = df_plot['Confidence'].mean() if not df_plot.empty else 0
c3.markdown(card_html("AVG RELIABILITY", f"{avg_conf:.1f}%"), unsafe_allow_html=True)
c4.markdown(card_html("SEVERITY STATUS", "HIGH" if len(cracks) > 10 else "NORMAL"), unsafe_allow_html=True)

# ---------------- MAIN CONTENT ----------------
col1, col2, col3 = st.columns([1, 1.8, 1])

with col1:
    st.markdown("### Defect Ratio")
    if not df_plot.empty:
        fig1 = px.pie(df_plot, names='Object', hole=0.6, color='Object', color_discrete_map=color_map, height=320)
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15", showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown(f"### Spatial View ({view})")
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        
        for r in df_plot.itertuples():
            # ✅ الربط الصحيح: بنبعت القيمة اللي في عمود Image
            img_base64 = get_base64_image(r.Image)
            
            if img_base64:
                img_html = f'''
                <div style="text-align:center; font-family: 'Montserrat', sans-serif;">
                    <img src="data:image/jpeg;base64,{img_base64}" style="width:150px;border-radius:5px;border:1px solid #FACC15;">
                    <br><b style="color:black;">{r.Object}</b>
                    <br><span style="color:black;">Confidence: {r.Confidence}%</span>
                </div>'''
            else:
                img_html = f'<div style="color:black;text-align:center;">Image Not Found:<br>{r.Image}</div>'
            
            folium.CircleMarker(
                location=[r.Longitude, r.Latitude], radius=6, 
                color=color_map.get(r.Object, "#FFF"), fill=True,
                popup=folium.Popup(folium.IFrame(img_html, width=170, height=200))
            ).add_to(m)
        st_folium(m, height=320, width="100%", key=f"map_{view}")

with col3:
    st.markdown("### Priority Alerts")
    critical = cracks[cracks["Confidence"] > 90]
    if not critical.empty:
        for r in critical.head(5).itertuples():
            st.warning(f"⚠️ CRITICAL | {r.Confidence}% Confidence")
    else:
        st.success("✅ System Clear")

# ---------------- BOTTOM ----------------
st.markdown("---")
c_low1, c_low2 = st.columns(2)
with c_low1:
    fig2 = px.histogram(df_plot, x='Confidence', height=320)
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15")
    st.plotly_chart(fig2, use_container_width=True)
with c_low2:
    fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map, height=320)
    fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="#FACC15")
    st.plotly_chart(fig3, use_container_width=True)
