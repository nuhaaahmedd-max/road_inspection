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

# 1. Configuration - جعل العرض واسع جداً
st.set_page_config(layout="wide", page_title="Road Inspection AI", initial_sidebar_state="expanded")

# 2. Colors
color_map = {'Clear': '#FFD700', 'Crack': '#FF0000', 'Manhole': '#0070FF', 'Pothole': '#00FF00'}
gold_color = "#FFD700" 

# 3. CSS Customization - ضغط المسافات (Padding) لضمان عدم وجود Scroll
st.markdown(f"""
<style>
    /* تقليل المسافات العلوية والجانبية */
    .block-container {{ 
        padding-top: 1rem !important; 
        padding-bottom: 0rem !important; 
        max-width: 98% !important;
    }}
    
    .stApp {{ background-color: #0B0E14; color: {gold_color}; }}
    
    .main-title {{ 
        color: {gold_color}; font-family: 'Montserrat', sans-serif;
        font-size: 26px; font-weight: 900; text-align: left; 
        padding: 5px 0px 5px 15px; border-bottom: 1px solid #1F2937; 
        margin-bottom: 10px; letter-spacing: 1px;
    }}

    /* تصغير الكروت لتناسب سطر واحد */
    .card {{ 
        background: #161B22; padding: 5px; border-radius: 10px; 
        border: 1px solid {gold_color}; text-align: center;
    }}
    .value {{ font-size: 22px; font-weight: bold; color: {gold_color} !important; }}
    .label {{ font-size: 10px; color: {gold_color} !important; text-transform: uppercase; opacity: 0.8; }}

    /* إخفاء الهوامش غير الضرورية في الرسوم */
    .css-1kyx738 {{ margin-bottom: -1rem !important; }}
    iframe {{ 
        border: 3px solid #FFD700 !important; 
        border-radius: 12px !important; 
        box-shadow: 0px 0px 10px rgba(255, 215, 0, 0.3);
    }}
/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {{
    background-color: #0B0E14 !important;
    border-right: 2px solid #FFD700;
    padding: 10px;
}}

/* ===== TITLE ===== */
section[data-testid="stSidebar"] h2 {{
    color: #FFD700;
    font-weight: 800;
}}

/* ===== LABELS ===== */
section[data-testid="stSidebar"] label {{
    color: #FFD700 !important;
    font-weight: 600;
}}

/* ===== MULTISELECT BOX ===== */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background-color: #0B0E14 !important;
    border: 2px solid #FFD700 !important;
    border-radius: 14px !important;
    padding: 8px !important;
}}

/* ===== CHIPS ===== */
section[data-testid="stSidebar"] div[data-baseweb="tag"] {{
    background-color: transparent !important;
    border: 1.5px solid #FFD700 !important;
    color: #FFD700 !important;
    border-radius: 10px !important;
    padding: 4px 10px !important;
    margin: 3px !important;
}}

/* ===== X ICON ===== */
section[data-testid="stSidebar"] div[data-baseweb="tag"] svg {{
    fill: #FFD700 !important;
}}

/* ===== RADIO ===== */
section[data-testid="stSidebar"] input[type="radio"] {{
    accent-color: #FF4B4B;
}}

/* ===== SLIDER ===== */
section[data-testid="stSidebar"] div[data-testid="stSlider"] .st-bd {{
    background: linear-gradient(90deg, #FF4B4B, #FFD700) !important;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADING (نفس منطقك بدون تغيير) ----------------
@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv("road_data.csv")
        valid_objects = ['Crack', 'Pothole', 'Manhole', 'Clear']
        df = df[df['Object'].isin(valid_objects)]
        df = df.dropna(subset=['Latitude', 'Longitude'])
        return df
    except: return pd.DataFrame()

@st.cache_data(show_spinner=False)
def get_random_image_by_type(obj_type):
    if obj_type == 'Clear': return "CLEAR_MODE"
    try:
        base_path = "assets"
        target_folder = str(obj_type).strip()
        full_path = os.path.join(base_path, target_folder)
        if not os.path.exists(full_path): full_path = os.path.join(base_path, target_folder.lower())
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

# ---------------- SIDEBAR (نفس الفلاتر) ----------------
st.sidebar.markdown("## 🛠️ FILTERS")
view_mode = st.sidebar.radio("MAP MODE", ["Points", "Heatmap"], index=0)
if not df.empty:
    selected_types = st.sidebar.multiselect("DEFECT TYPE", options=df["Object"].unique(), default=list(df["Object"].unique()))
    df_plot = df[df["Object"].isin(selected_types)]
else: df_plot = df

if not df_plot.empty:
    csv = df_plot.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Download Report", data=csv, file_name='road_report.csv')

# ---------------- HEADER ----------------
st.markdown("<div style='margin-top:15px'></div>", unsafe_allow_html=True)
st.markdown('<div class="main-title">Road Inspection Intelligence Dashboard</div>', unsafe_allow_html=True)

# ---------------- TOP ROW: KPIs (تم دمجها في سطر واحد رفيع) ----------------
c1, c2, c3, c4, c5 = st.columns(5)
stats = {obj: len(df_plot[df_plot['Object'] == obj]) for obj in ['Crack', 'Pothole', 'Manhole']}
c1.markdown(f"<div class='card'><div class='label'>TOTAL</div><div class='value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='label'>CRACKS</div><div class='value'>{stats['Crack']}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='label'>POTHOLES</div><div class='value'>{stats['Pothole']}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='label'>MANHOLES</div><div class='value'>{stats['Manhole']}</div></div>", unsafe_allow_html=True)
c5.markdown(f"<div class='card'><div class='label'>CONFIDENCE</div><div class='value'>{int(df_plot['Confidence'].mean()) if not df_plot.empty else 0}%</div></div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ---------------- MAIN DASHBOARD LAYOUT ----------------
# تقسيم الصفحة لـ 3 أعمدة: يسار (تحليلات)، منتصف (خريطة)، يمين (تنبيهات ورسوم)
col_left, col_mid, col_right = st.columns([1.2, 2.5, 1.2])

with col_left:
    st.markdown("##### 📊 Object Distribution")
    if not df_plot.empty:
        fig1 = px.pie(df_plot, names='Object', hole=0.6, color='Object', color_discrete_map=color_map)
        fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220, showlegend=True, 
                          legend=dict(orientation="h", y=-0.1), paper_bgcolor='rgba(0,0,0,0)', font_color=gold_color)
        st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("##### 📉 Confidence Trend")
    fig2 = px.histogram(df_plot, x='Confidence', color='Object', color_discrete_map=color_map, nbins=15)
    fig2.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=180, paper_bgcolor='rgba(0,0,0,0)', 
                      plot_bgcolor='rgba(0,0,0,0)', font_color=gold_color, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

with col_mid:
    st.markdown("##### 🗺️ Spatial Inspection View")
    if not df_plot.empty:
        m = folium.Map(location=[df_plot['Longitude'].mean(), df_plot['Latitude'].mean()], zoom_start=15, tiles="CartoDB dark_matter")
        Fullscreen().add_to(m)
        
        if view_mode == "Points":
            for index, row in df_plot.iterrows():
                img_b64 = get_random_image_by_type(row['Object'])
                color = color_map.get(row['Object'], "#FFF")
                html_content = f'<div style="text-align:center; width:150px;"><b>{row["Object"]}</b><br><img src="data:image/jpeg;base64,{img_b64}" style="width:100%">' if img_b64 else "Loading..."
                folium.CircleMarker(
                    location=[row['Longitude'], row['Latitude']],
                    radius=7, color=color, fill=True, fill_opacity=0.8,
                    popup=folium.Popup(html_content, max_width=160)
                ).add_to(m)
        else:
            HeatMap([[r['Longitude'], r['Latitude']] for _, r in df_plot.iterrows()], radius=15).add_to(m)
            
        # ارتفاع الخريطة لملء المنتصف دون تسبب في Scroll
        st_folium(m, height=450, width="100%", key="main_map")

with col_right:
    st.markdown("##### ⚠️ Critical Alerts")
    critical = df_plot[df_plot['Confidence'] > 90].head(5)
    if not critical.empty:
        for r in critical.itertuples():
            st.warning(f"*{r.Object}* - {r.Confidence}%")
    else:
        st.success("No Critical Issues")

    st.markdown("##### 📊 Count by Category")
    fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map)
    fig3.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=200, paper_bgcolor='rgba(0,0,0,0)', 
                      plot_bgcolor='rgba(0,0,0,0)', font_color=gold_color, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
