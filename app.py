import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import plotly.express as px
import base64
import os
import random

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide", page_title="Road Inspection AI")

color_map = {
    'Clear': '#FFD700',
    'Crack': '#FF0000',
    'Manhole': '#0070FF',
    'Pothole': '#00FF00',
}

gold_color = "#FFD700"

# ---------------- STYLE ----------------
st.markdown(f"""
<style>
.stApp {{background-color:#0B0E14;color:{gold_color};}}
.card {{
    background:#161B22;
    padding:15px;
    border-radius:12px;
    border:1px solid {gold_color};
    text-align:center;
    height:100%;
}}
.value {{font-size:26px;font-weight:bold;}}
.label {{font-size:12px;opacity:0.8;}}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("road_data.csv")
        df = df.dropna(subset=['Latitude', 'Longitude'])
        return df
    except:
        return pd.DataFrame()

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("Filters")

view_mode = st.sidebar.radio("Map Mode", ["Points", "Heatmap"])

if not df.empty:
    selected = st.sidebar.multiselect(
        "Category",
        df["Object"].unique(),
        default=df["Object"].unique()
    )
    df_plot = df[df["Object"].isin(selected)]
else:
    df_plot = df

# ---------------- HEADER ----------------
st.title("🚧 Road Inspection Dashboard")

# ---------------- KPI ROW ----------------
k1, k2, k3, k4 = st.columns(4)

k1.markdown(f"<div class='card'><div class='label'>TOTAL</div><div class='value'>{len(df_plot)}</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='card'><div class='label'>CRACKS</div><div class='value'>{len(df_plot[df_plot['Object']=='Crack'])}</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='card'><div class='label'>POTHOLES</div><div class='value'>{len(df_plot[df_plot['Object']=='Pothole'])}</div></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='card'><div class='label'>MANHOLES</div><div class='value'>{len(df_plot[df_plot['Object']=='Manhole'])}</div></div>", unsafe_allow_html=True)

st.markdown("---")

# ---------------- ROW 1 ----------------
r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    st.markdown("### Defect Ratio")
    if not df_plot.empty:
        fig1 = px.pie(df_plot, names='Object', hole=0.6, color='Object', color_discrete_map=color_map)
        fig1.update_layout(height=300)
        st.plotly_chart(fig1, use_container_width=True)

with r1c2:
    st.markdown("### Map")
    if not df_plot.empty:
        m = folium.Map(
            location=[df_plot['Latitude'].mean(), df_plot['Longitude'].mean()],
            zoom_start=14,
            tiles="CartoDB dark_matter"
        )

        if view_mode == "Points":
            for _, row in df_plot.iterrows():
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=6,
                    color=color_map.get(row['Object']),
                    fill=True
                ).add_to(m)
        else:
            heat = [[r['Latitude'], r['Longitude']] for _, r in df_plot.iterrows()]
            HeatMap(heat).add_to(m)

        st_folium(m, height=300)

with r1c3:
    st.markdown("### Alerts")
    critical = df_plot[(df_plot['Object'] != 'Clear') & (df_plot['Confidence'] > 90)]
    if not critical.empty:
        for r in critical.head(5).itertuples():
            st.error(f"{r.Object} detected")
    else:
        st.success("No critical issues")

# ---------------- ROW 2 ----------------
r2c1, r2c2, r2c3 = st.columns(3)

with r2c1:
    st.markdown("### Confidence Distribution")
    if not df_plot.empty:
        fig2 = px.histogram(df_plot, x='Confidence', color='Object', color_discrete_map=color_map)
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)

with r2c2:
    st.markdown("### Count by Type")
    if not df_plot.empty:
        fig3 = px.bar(df_plot, x='Object', color='Object', color_discrete_map=color_map)
        fig3.update_layout(height=300)
        st.plotly_chart(fig3, use_container_width=True)

with r2c3:
    st.markdown("### Summary")
    st.info("System running normally 🚀")
