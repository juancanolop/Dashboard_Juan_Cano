import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import os

# =========================
# 1. Cargar los datos
# =========================
@st.cache_data
def load_data():
    data_path = "C:/Users/juanc/Kronos GMT/JUAN DAVID CANO - Documents/mi_dashboard/app/data/data.xlsx"
    df = pd.read_excel(data_path, engine="openpyxl")
    df.columns = df.columns.str.strip()

    # Convertir columna Year
    if df["Year"].dtype == "object":
        df["Year"] = pd.to_datetime(df["Year"]).dt.year
    elif "datetime" in str(df["Year"].dtype):
        df["Year"] = df["Year"].dt.year

    return df

df = load_data()

# =========================
# 2. Filtros (sidebar)
# =========================
st.sidebar.header("Filtros")

years = sorted(df["Year"].dropna().unique())
selected_year = st.sidebar.slider(
    "Selecciona el año", min_value=int(min(years)), max_value=int(max(years)), value=int(max(years))
)

industries = sorted(df["Industry"].dropna().unique())
selected_industries = st.sidebar.multiselect("Selecciona industrias", industries)

types = sorted(df["Type"].dropna().unique()) if "Type" in df.columns else []
selected_types = st.sidebar.multiselect("Selecciona tipos", types)

# =========================
# 3. Filtrar datos
# =========================
filtered_df = df[df["Year"] == selected_year]

if selected_industries:
    filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industries)]

if selected_types:
    filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]

# =========================
# 4. Layout en dos columnas
# =========================
col1, col2 = st.columns(2)

# -------------------------
# 4.1 Columna izquierda
# -------------------------
with col1:
    st.subheader("Skills (Gráfico de torta)")
    if not filtered_df.empty and "Skills" in filtered_df.columns:
        skills_counts = filtered_df["Skills"].str.split(", ").explode().value_counts()
        if not skills_counts.empty:
            fig = px.pie(names=skills_counts.index, values=skills_counts.values, title="Skills")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de Skills para este filtro.")
    else:
        st.warning("No hay datos para mostrar en el gráfico.")

    # Logos
    st.subheader("Logos")
    if "Logo" in filtered_df.columns:
        logos = [
            logo.strip()
            for logo_list in filtered_df["Logo"].dropna()
            for logo in logo_list.split(",")
        ]
        if logos:
            cols = st.columns(min(len(logos), 5))
            for idx, logo in enumerate(logos):
                logo_path = f"assets/Logos/{logo}"
                if os.path.exists(logo_path):
                    cols[idx % 5].image(logo_path, width=50)
        else:
            st.info("No hay logos disponibles.")

    # Tabla
    st.subheader("Tabla de datos")
    show_cols = [
        col for col in ["Project_Name", "Industry", "Scope", "Functions", "Client_Company", "Country"]
        if col in filtered_df.columns
    ]
    if not filtered_df.empty:
        st.dataframe(filtered_df[show_cols])
    else:
        st.info("No hay datos para mostrar en la tabla.")

# -------------------------
# 4.2 Columna derecha
# -------------------------
with col2:
    # Mapa
    st.subheader("Mapa")
    if not filtered_df.empty and "Latitud" in filtered_df.columns and "Longitud" in filtered_df.columns:
        lat_center = filtered_df["Latitud"].mean()
        lon_center = filtered_df["Longitud"].mean()

        map_ = folium.Map(location=[lat_center, lon_center], zoom_start=5)
        for _, row in filtered_df.iterrows():
            folium.Marker([row["Latitud"], row["Longitud"]], tooltip=row["Project_Name"]).add_to(map_)

        st_folium(map_, height=500, width=600)
    else:
        st.warning("No hay datos para mostrar en el mapa.")

    # Fotos
    st.subheader("Imágenes")
    if "Photo" in filtered_df.columns:
        photos = filtered_df["Photo"].dropna().tolist()
        if photos:
            cols = st.columns(min(len(photos), 3))
            for idx, photo in enumerate(photos):
                photo_path = f"assets/Images/{photo}"
                if os.path.exists(photo_path):
                    cols[idx % 3].image(photo_path, use_container_width=True)
        else:
            st.info("No hay imágenes disponibles.")
