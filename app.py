import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
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
primary_color = "#FACC15"
bg_color = "#161B22"
sidebar_bg = "#05070A"
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
    
    .main-title { 
        color: #FACC15;
        background-color: #0B0E14; /* لون الخلفية دارك نفس السايد بار */
        font-family: 'Montserrat', sans-serif;
        font-size: 26px; 
        font-weight: 900; 
        text-align: left; 
        padding: 15px; 
        border-radius: 10px; /* حواف دائرية خفيفة */
        border: 1px solid #1F2937; /* إطار غامق بسيط */
        margin-bottom: 20px; 
        letter-spacing: 1px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3); /* ظل خفيف عشان يبرز */
    }

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
        border: 1px solid #FFD700 !important; 
        border-radius: 12px !important; 
        box-shadow: 0px 0px 10px rgba(255, 215, 0, 0.3);
    }}
    div[data-testid="stAppViewContainer"] > section > div {{
        background-color: #0B0E14 !important; /* نفس لون السايد بار الغامق */
    }}
/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {{
    background-color: #0B0E14 !important;
    border-right: 2px solid #FFD700;
    padding: 10px;
}}

/* ===== TITLE ===== */
section[data-testid="stSidebar"] h2 {{
    color: #ebecef;
    font-weight: 800;
    text-align: center !important;
    margin-top: -40px !important;
    margin-bottom: 40px !important;
}}

/* ===== LABELS ===== */
section[data-testid="stSidebar"] label {{
    color: #FFD700 !important;
    font-weight: 600;
}}
/* المربع الكبير اللي شايل كل الاختيارات */
    div[data-baseweb="select"] > div:first-child {{
        border: 1px solid #FACC15 !important; /* لون البوردر الذهبي */
        border-radius: 8px !important;        /* حواف دائرية للمربع الكبير */
        background-color: transparent !important;
    }}
span[data-baseweb="tag"] {{
        background-color: transparent !important; /* إلغاء الخلفية الحمراء */
        border: 1.5px solid #FACC15 !important;    /* رسم الإطار الذهبي */
        border-radius: 5px !important;           /* جعل الحواف مربعة قليلاً مثل صورتك */
        padding: 2px 8px !important;
    }}

    /* 2. إجبار النص الداخلي يكون ذهبي وعريض */
    span[data-baseweb="tag"] span {{
        color: #FACC15 !important;               /* لون النص ذهبي */
        font-weight: 600 !important;             /* سمك الخط */
    }}

    /* 3. تنسيق علامة الـ X لتكون ذهبية */
    span[data-baseweb="tag"] svg {{
        fill: #FACC15 !important;
    }}

    /* 4. إلغاء أي تأثير عند الوقوف بالماوس (Hover) عشان اللون ميتغيرش */
    span[data-baseweb="tag"]:hover {{
        background-color: rgba(250, 204, 21, 0.1) !important; /* خلفية ذهبية خفيفة جداً عند اللمس */
    }}
    /* 1. تلوين الدائرة اللي تم اختيارها (الـ Active Radio Button) */
    div[role="radiogroup"] div[data-active="true"] > div {{
        border-color: #FACC15 !important;
    }}

    div[role="radiogroup"] div[data-active="true"] > div::after {{
        background-color: #FACC15 !important;
    }}

    /* 2. تلوين النص (Points & Heatmap) باللون الأصفر */
    div[role="radiogroup"] label p {{
        color: #FACC15 !important;
        font-weight: 400 !important;
    }}

    /* 3. تلوين الدوائر غير المختارة (اختياري لو حابة توحدي اللون) */
    div[role="radiogroup"] div[data-active="false"] > div {{
        border-color: rgba(250, 204, 21, 0.4) !important;
    }}
    .stSlider > div > div > div {{
    background: #444444 !important;
}}

/* الجزء قبل الدايرة */
.stSlider > div > div > div > div {{
   background: linear-gradient(to right, #FFD700, #36454F) !important; 
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

# هنخلي الكاش يعتمد على الـ seed عشان يثبت صورة لكل نقطة وميتقلش الجهاز
def get_random_image_by_type(obj_type, seed):
    @st.cache_data(show_spinner=False)
    def get_cached_image(obj_type, seed):
    # الكود بتاعك اللي بيطلع الـ base64
      return get_random_image_by_type(obj_type, seed)
    if obj_type == 'Clear': return "CLEAR_MODE"
    try:
        random.seed(seed)
        # تأكدي إن المسار ده هو اللي فيه الصور فعلاً
        base_path = "assets" 
        target_folder = str(obj_type).strip()
        full_path = os.path.join(base_path, target_folder)

        # لو مش لاقي الفولدر بالكبير، يدور بالصغير
        if not os.path.exists(full_path):
            full_path = os.path.join(base_path, target_folder.lower())

        if os.path.exists(full_path):
            images = [f for f in os.listdir(full_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                selected = random.choice(images)
                img_path = os.path.join(full_path, selected)
                
                # السطر ده عشان نتأكد إن الصورة بتفتح صح
                with Image.open(img_path) as img:
                    img = img.convert('RGB')
                    img.thumbnail((250, 250))
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG", quality=70)
                    return base64.b64encode(buffered.getvalue()).decode()
        else:
            # لو دخل هنا يبقى مش لاقي الفولدر أصلاً
            print(f"Folder not found: {full_path}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
df = load_data()

# ---------------- SIDEBAR (نفس الفلاتر) ----------------
st.sidebar.markdown("## 🛠️ FILTERS")
view_mode = st.sidebar.radio("MAP MODE", ["Points", "Heatmap"], index=0)
if not df.empty:
    selected_types = st.sidebar.multiselect("DEFECT TYPE", options=df["Object"].unique(), default=list(df["Object"].unique()))
    df_plot = df[df["Object"].isin(selected_types)]
else: df_plot = df
# السلايدر والفلترة (تأكدي إن كلهم على نفس خط البداية)
confidence_min = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.0, 0.05)
df_plot = df_plot[df_plot['Confidence'] >= confidence_min]

# السطر ده كان فيه مسافة زيادة، كدا بقى صح:
csv = df_plot.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Download Report", data=csv, file_name='road_report.csv')

# ---------------- HEADER ----------------
st.markdown("<div style='margin-top:15px'></div>", unsafe_allow_html=True)
st.markdown('<div class="main-title">Road Inspection Intelligence Dashboard</div>', unsafe_allow_html=True)

# حساب كثافة العيوب (Defect Density)
# حساب الفرق بين أقصى وأدنى إحداثيات (تقدير للمسافة)
if not df_plot.empty:
    delta_lat = df_plot['Longitude'].max() - df_plot['Longitude'].min()
    delta_lon = df_plot['Latitude'].max() - df_plot['Latitude'].min()
    # تحويل فرق الدرجات لمسافة تقريبية (كل درجة تقريباً 111 كم)
    road_length_km = ((delta_lat**2 + delta_lon**2)**0.5) * 111
    if road_length_km < 0.1: road_length_km = 0.1 # عشان لو المسافة صغيرة جداً
else:
    road_length_km = 1.0
density_value = len(df_plot) / road_length_km if road_length_km > 0 else 0

# ---------------- TOP ROW: KPIs (تم دمجها في سطر واحد رفيع) ----------------
c1, c2, c3, c4, c5 = st.columns(5)
stats = {obj: len(df_plot[df_plot['Object'] == obj]) for obj in ['Crack', 'Pothole', 'Manhole']}
c1.markdown(f"<div class='card'><div class='label'>TOTAL</div><div class='value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='label'>CRACKS</div><div class='value'>{stats['Crack']}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='label'>POTHOLES</div><div class='value'>{stats['Pothole']}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='label'>MANHOLES</div><div class='value'>{stats['Manhole']}</div></div>", unsafe_allow_html=True)
c5.markdown(f"<div class='card'><div class='label'>DEFECT DENSITY</div><div class='value'>{density_value:.1f} <span style='font-size:12px;'>Defect/Km</span></div></div>", unsafe_allow_html=True)

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
    df_defects_only = df_plot[df_plot['Object'] != 'Clear']
    # 1. بنفلتر الداتا عشان نشيل الـ Clear قبل ما نرسم
    df_defects_only = df_plot[df_plot['Object'] != 'Clear']

    # 2. بنرسم نفس الجراف بأبعاده الأصلية بالظبط
    st.markdown("##### 📉 Confidence Trend")
    fig2 = px.histogram(df_defects_only, x='Confidence', color='Object', color_discrete_map=color_map, nbins=15)
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
                # دوري على السطر ده وغيريه للنسخة دي:
                img_b64 = get_random_image_by_type(row['Object'], index)
                color = color_map.get(row['Object'], "#FFF")
                lat_val = row['Longitude']
                long_val = row['Latitude']
              # إضافة Scroll ومنع خروج المحتوى عن البرواز
                html_content = f"""
                <div style="
                    text-align:center; 
                    width:220px; 
                    max-height:300px; 
                    overflow-y:auto; 
                    overflow-x:hidden; 
                    font-family:sans-serif;
                    padding-right:5px;
                ">
                    <b style="font-size:16px; color:#333;">{row['Object']}</b><br>
                    <img src="data:image/jpeg;base64,{img_b64}" style="width:100%; border-radius:8px; margin-top:5px;">
                    <div style="
                        margin-top:10px; 
                        padding:8px; 
                        border-top:1px solid #ccc; 
                        background-color:#f9f9f9; 
                        border-radius:5px;
                        font-size:12px;
                    ">
                        <p style="margin:0;"><b>Lat (Y):</b> {row['Longitude']:.6f}</p>
                        <p style="margin:0;"><b>Long (X):</b> {row['Latitude']:.6f}</p>
                    </div>
                </div>
                """
                
                folium.CircleMarker(
                    location=[row['Longitude'], row['Latitude']],
                    radius=7, color=color, fill=True, fill_opacity=0.8,
                    # تحديد العرض والارتفاع الأقصى للفقاعة نفسها
                    popup=folium.Popup(html_content, max_width=250) 
                ).add_to(m)
        else:
            HeatMap([[r['Longitude'], r['Latitude']] for _, r in df_plot.iterrows()], radius=15).add_to(m)
            
        # ارتفاع الخريطة لملء المنتصف دون تسبب في Scroll
        folium_static(m, height=450, width=700) # العرض بالبكسل هنا أدق

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
