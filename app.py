import streamlit as st
import pandas as pd
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
col1, col2 = st.columns([1, 1])  # Mitad y mitad

# URL base de Cloudinary (sin espacios)
CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dmf2pbdlq/image/upload/"

# User-Agent para requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Paleta de colores por skill (opcional)
SKILL_COLORS = {
    "GIS": "#4285F4",
    "Survey": "#FBBC05",
    "Network Analysis": "#EA4335",
    "CAD Drafting": "#34A853",
    "Dashboard": "#FF6D01",
    "Python": "#3776AB",
    "Excel": "#217346",
    "AutoCAD": "#0A97D9",
    "Revit": "#C51152",
    "Rhino": "#7D66DD",
    "Grasshopper": "#1A1A1A",
    "ArcGIS": "#228B22",
    "QGIS": "#377EB8",
    "Power BI": "#F2C811",
    "Civil 3D": "#00A9CE",
    "PMI": "#5855B8",
    "LinkedIn": "#0077B5"
}

with col1:
    # === SKILLS como etiquetas únicas ===
    st.markdown('<div class="section-header">Skills</div>', unsafe_allow_html=True)
    if not filtered_df.empty and "Skills" in filtered_df.columns:
        all_skills = set()
        for skill_list in filtered_df["Skills"].dropna():
            for skill in str(skill_list).split(","):
                skill_clean = skill.strip().strip('"\'[] ')
                if skill_clean:
                    all_skills.add(skill_clean)

        skills_list = sorted(all_skills)

        if skills_list:
            cols_skills = st.columns(min(len(skills_list), 6))
            for idx, skill in enumerate(skills_list):
                color = SKILL_COLORS.get(skill, "#666666")
                with cols_skills[idx % 6]:
                    st.markdown(
                        f"""
                        <div style="
                            background-color: {color};
                            color: white;
                            padding: 8px 12px;
                            border-radius: 12px;
                            text-align: center;
                            font-size: 0.85rem;
                            font-weight: 600;
                            margin: 4px;
                            min-width: 80px;
                        ">
                            {skill}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.info("No hay skills disponibles.")
    else:
        st.warning("No hay datos de skills para mostrar.")

    # === LOGOS ===
    st.markdown('<div class="section-header">Logos</div>', unsafe_allow_html=True)
    if "Software" in filtered_df.columns:
        all_software = set()
        for software_list in filtered_df["Software"].dropna():
            for software in str(software_list).split(","):
                software_clean = software.strip().strip('"\'[] ').replace(" ", "_").replace("-", "_").lower()
                if software_clean:
                    all_software.add(software_clean)

        software_list = sorted(all_software)

        if software_list:
            cols_logos = st.columns(min(len(software_list), 6))
            for idx, software in enumerate(software_list):
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
                    except:
                        continue

                with cols_logos[idx % 6]:
                    if success:
                        try:
                            st.image(img_url, width=60, use_container_width=False, clamp=True, channels="RGB")
                        except:
                            st.markdown('<div class="warning-text">⚠️</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="warning-text">⚠️</div>', unsafe_allow_html=True)
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
            tiles="CartoDB positron",  # Estilo claro, como Google Maps
            control_scale=True
        )

        # Añadir marcadores
        for _, row in filtered_df.iterrows():
            folium.Marker(
                [row["Latitud"], row["Longitud"]],
                tooltip=row["Project_Name"],
                icon=folium.Icon(color="darkblue", icon="map-marker")
            ).add_to(map_)

        # Ajustar zoom automáticamente
        if len(filtered_df) == 1:
            map_.set_view([lat_center, lon_center], zoom=10)
        else:
            bounds = [[row["Latitud"], row["Longitud"]] for _, row in filtered_df.iterrows()]
            map_.fit_bounds(bounds, padding=(0.1, 0.1))

        st_folium(map_, height=600, use_container_width=True)
    else:
        st.warning("No hay datos geográficos.")

# =========================
# 5. Fila: Imágenes (Galería de Proyectos)
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
                    response = requests.head(image_url, timeout=5, headers=HEADERS)
                    if response.status_code == 200:
                        st.image(image_url, caption=row["Project_Name"], use_container_width=True, clamp=True, channels="RGB")
                        if "Blog_Link" in filtered_df.columns and pd.notna(row.get("Blog_Link")):
                            st.markdown(f"[📖 Más Información]({row['Blog_Link']})", unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="image-placeholder">🖼️ No disponible</div>', unsafe_allow_html=True)
                except Exception:
                    st.markdown('<div class="image-placeholder">⚠️ Error</div>', unsafe_allow_html=True)
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
