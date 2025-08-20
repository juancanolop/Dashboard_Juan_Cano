import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import requests

# Configuración de layout amplio (must be first Streamlit command)
st.set_page_config(layout="wide")

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #07b9d1;
        margin: 1rem 0;
        border-bottom: 2px solid #07b9d1;
        padding-bottom: 0.5rem;
    }
    .logo-image {
        max-width: 50px;
        height: auto;
        object-fit: contain;
        border-radius: 5px;
        border: 1px solid #34495e;
    }
    .cloudinary-image {
        max-width: 20vw;
        height: auto;
        object-fit: cover;
        border-radius: 5px;
        border: 1px solid #34495e;
        cursor: pointer;
    }
    .warning-text {
        color: #e74c3c;
        font-size: 0.9rem;
    }
    .image-placeholder {
        background-color: #2d3436;
        color: #b2bec3;
        text-align: center;
        padding: 10px;
        border-radius: 5px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 1. Cargar los datos
# =========================
@st.cache_data
def load_data():
    # 🔴 Corregido: Eliminado espacio al final
    data_url = "https://raw.githubusercontent.com/juancanolop/Dashboard_Juan_Cano/main/data.csv"
    try:
        df = pd.read_csv(data_url)
        df.columns = df.columns.str.strip()  # Limpiar nombres de columnas
        # Convertir columna Year
        if df["Year"].dtype == "object":
            df["Year"] = pd.to_datetime(df["Year"], errors='coerce').dt.year
        elif "datetime" in str(df["Year"].dtype):
            df["Year"] = df["Year"].dt.year
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.error("No se pudieron cargar los datos. Verifica la URL del CSV.")
    st.stop()

# =========================
# 2. Filtros (sidebar y arriba)
# =========================
st.sidebar.header("Filtros")

# Año: incluir "All"
years = sorted(df["Year"].dropna().unique())
year_options = ["All"] + list(years)

selected_years_sidebar = st.sidebar.multiselect(
    "Filtrar años",
    options=year_options,
    default=["All"]
)

# 🎯 Timeline (slider horizontal principal)
st.title("Dashboard de Proyectos")
selected_year_slider = st.slider(
    "Selecciona un año",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=int(max(years)),
    key="timeline-slider"
)

# Lógica de sincronización
if "All" in selected_years_sidebar:
    years_to_use = years
else:
    years_to_use = [y for y in selected_years_sidebar if isinstance(y, int)]

if selected_year_slider not in years_to_use:
    years_to_use.append(selected_year_slider)

# Filtro industrias
industries = sorted(df["Industry"].dropna().unique())
selected_industries = st.sidebar.multiselect("Industrias", industries)

# Filtro tipos
types = sorted(df["Type"].dropna().unique()) if "Type" in df.columns else []
selected_types = st.sidebar.multiselect("Tipos", types)

# =========================
# 3. Filtrar datos
# =========================
filtered_df = df[df["Year"].isin(years_to_use)]

if selected_industries:
    filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industries)]

if selected_types:
    filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]

# =========================
# 4. Fila: Skills + Logos vs Mapa
# =========================
col1, col2 = st.columns([2, 1])

# 🔴 Corregido: Eliminado espacio al final
CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dmf2pbdlq/image/upload/"

# Agregar encabezado de User-Agent global
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

with col1:
    st.markdown('<div class="section-header">Skills</div>', unsafe_allow_html=True)
    if not filtered_df.empty and "Skills" in filtered_df.columns:
        skills_data = filtered_df["Skills"].dropna().str.split(", ").explode()
        if len(skills_data) > 0:
            skills_counts = skills_data.value_counts()
            fig = px.pie(
                names=skills_counts.index,
                values=skills_counts.values,
                title="",
                template="plotly_dark"
            )
            fig.update_layout(
                font_color="#FAFAFA",
                paper_bgcolor="#0E1117",
                plot_bgcolor="#0E1117"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de Skills.")
    else:
        st.warning("No hay datos para mostrar en el gráfico.")

    # Logos (mejorado con sanitización y verificación)
st.markdown('<div class="section-header">Logos</div>', unsafe_allow_html=True)
if "Software" in filtered_df.columns:
    all_software = set()
    for software_list in filtered_df["Software"].dropna():
        for software in str(software_list).split(","):
            # Limpieza profunda
            software = software.strip().strip('"\'[] ')
            if not software:
                continue
            # Convertir a minúsculas y reemplazar espacios por guiones bajos
            software_clean = software.replace(" ", "_").replace("-", "_").lower()
            all_software.add(software_clean)

    software_logos = list(all_software)
    if software_logos:
        cols = st.columns(min(len(software_logos), 6))
        for idx, software in enumerate(software_logos):
            # Intentar con .jpg y .png
            urls_to_try = [
                f"{CLOUDINARY_BASE_URL}logos/{software}.jpg",
                f"{CLOUDINARY_BASE_URL}logos/{software}.png"
            ]
            img_url = None
            success = False

            for url in urls_to_try:
                try:
                    response = requests.head(url, timeout=5, headers=HEADERS)
                    if response.status_code == 200:
                        img_url = url
                        success = True
                        break
                except Exception as e:
                    continue

            with cols[idx % 6]:
                if success:
                    try:
                        st.image(img_url, width=50, use_container_width=False, clamp=True, channels="RGB")
                    except Exception as e:
                        st.markdown(f'<div class="warning-text">⚠️ Error: {e}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="warning-text">⚠️ No encontrado: {software}</div>', unsafe_allow_html=True)
    else:
        st.info("No hay software/logos disponibles.")
else:
    st.warning("No se encontró la columna 'Software' en los datos.")

with col2:
    st.markdown('<div class="section-header">Mapa</div>', unsafe_allow_html=True)
    if not filtered_df.empty and "Latitud" in filtered_df.columns and "Longitud" in filtered_df.columns:
        lat_center = filtered_df["Latitud"].mean()
        lon_center = filtered_df["Longitud"].mean()

        map_ = folium.Map(
            location=[lat_center, lon_center],
            zoom_start=5,
            tiles="CartoDB dark_matter"
        )

        bounds = []
        for _, row in filtered_df.iterrows():
            lat, lon = row["Latitud"], row["Longitud"]
            folium.Marker([lat, lon], tooltip=row["Project_Name"]).add_to(map_)
            bounds.append([lat, lon])

        if bounds:
            map_.fit_bounds(bounds)

        st_folium(map_, height=500, width=500)
    else:
        st.warning("No hay datos geográficos.")

# =========================
# 5. Fila: Imágenes (Project Gallery style)
# =========================
st.markdown('<div class="section-header">Galería de Proyectos</div>', unsafe_allow_html=True)
if "image_link" in filtered_df.columns and "Project_Name" in filtered_df.columns:
    valid_images = filtered_df[
        filtered_df["image_link"].apply(
            lambda x: pd.notna(x) and isinstance(x, str) and x.strip().startswith("http")
        )
    ]
    if not valid_images.empty:
        cols = st.columns(4)
        for i, (_, row) in enumerate(valid_images.head(8).iterrows()):
            col = cols[i % 4]
            with col:
                image_url = row["image_link"].strip()
                try:
                    # Verificar si la imagen existe
                    response = requests.head(image_url, timeout=5, headers=HEADERS)
                    if response.status_code != 200:
                        st.markdown('<div class="image-placeholder">🖼️ Imagen no disponible</div>', unsafe_allow_html=True)
                    else:
                        st.image(image_url, caption=row["Project_Name"], use_container_width=True, clamp=True, channels="RGB")
                        if "Blog_Link" in filtered_df.columns and pd.notna(row.get("Blog_Link")):
                            st.markdown(f"[📖 Más Información]({row['Blog_Link']})", unsafe_allow_html=True)
                except Exception:
                    st.markdown('<div class="image-placeholder">⚠️ Error al cargar</div>', unsafe_allow_html=True)
    else:
        st.info("No hay enlaces de imágenes válidos disponibles.")
else:
    st.warning("No se encontró la columna 'image_link' o 'Project_Name' en los datos.")

# =========================
# 6. Tabla de datos
# =========================
st.markdown('<div class="section-header">Tabla de datos</div>', unsafe_allow_html=True)
show_cols = [
    col for col in ["Project_Name", "Industry", "Scope", "Functions", "Client_Company", "Country"]
    if col in filtered_df.columns
]
if not filtered_df.empty and show_cols:
    st.dataframe(filtered_df[show_cols], use_container_width=True)
else:
    st.info("No hay datos para mostrar.")
