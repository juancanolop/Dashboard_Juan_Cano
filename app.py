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

# URL base de Cloudinary
CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dmf2pbdlq/image/upload/"

# User-Agent para requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Paleta de colores para skills (¡sin grises!)
SKILL_COLORS = {
    "GIS": "#4285F4",               # Azul Google
    "Survey": "#FBBC05",            # Amarillo Google
    "Network Analysis": "#EA4335",  # Rojo Google
    "CAD Drafting": "#34A853",      # Verde Google
    "Dashboard": "#FF6D01",         # Naranja profundo
    "Python": "#3776AB",            # Azul Python
    "Excel": "#217346",             # Verde Excel
    "AutoCAD": "#0A97D9",           # Azul AutoCAD
    "Revit": "#C51152",             # Rosa rojo Revit
    "Rhino": "#7D66DD",             # Púrpura
    "Grasshopper": "#1A1A1A",      # Negro elegante
    "ArcGIS": "#228B22",            # Verde bosque
    "QGIS": "#377EB8",              # Azul QGIS
    "Power BI": "#F2C811",          # Amarillo Power BI
    "Civil 3D": "#00A9CE",          # Cian industrial
    "PMI": "#5855B8",               # Púrpura oscuro
    "LinkedIn": "#0077B5",          # Azul LinkedIn
    "Remote Sensing": "#005F5D",    # Verde oscuro
    "Data Analysis": "#8E24AA",     # Púrpura fuerte
    "Machine Learning": "#D81B60",  # Rosa brillante
    "BIM": "#FFB300",               # Amarillo dorado
    "Urban Planning": "#6D4C41",    # Marrón tierra
    "Geodesign": "#00897B",         # Turquesa oscuro
    "3D Modeling": "#5E35B1",       # Índigo
    "Lidar": "#5D4037",             # Marrón chocolate
    "Hydrology": "#0277BD",         # Azul cielo
    "Infrastructure": "#757575",    # Gris industrial → vamos a cambiarlo
    "Project Management": "#E65100",# Naranja oscuro
    "Consulting": "#311B92",        # Púrpura profundo
    "Feasibility Study": "#C0CA33", # Verde lima
    "Environmental Impact": "#2E7D32", # Verde bosque
    "Transportation": "#D84315",    # Rojo terracota
    "Land Use": "#827717",          # Verde oliva
    "Geospatial": "#006064",        # Verde azulado
    "Topography": "#4E342E",        # Marrón oscuro
    "Photogrammetry": "#BF360C",    # Rojo cobre
    "Design": "#AD1457",            # Rosa vino
    "Visualization": "#283593",     # Azul noche
    "Planning": "#1B5E20",          # Verde oscuro
    "Modeling": "#01579B",          # Azul acero
    "Analysis": "#C62828",          # Rojo sangre
    "Mapping": "#4A148C",           # Púrpura real
    "Simulation": "#EF6C00",        # Naranja quemado
    "Optimization": "#2E7D32",      # Verde profundo
    "Reporting": "#455A64",         # Gris azulado → vamos a cambiarlo
    "Stakeholder Engagement": "#B71C1C", # Rojo intenso
    "Field Work": "#33691E",        # Verde oscuro
    "Data Collection": "#E64A19",   # Naranja vivo
    "Risk Assessment": "#C2185B",   # Rosa fuerte
}

# Asegurarnos de que ningún skill se quede en gris
fallback_colors = [
    "#D81B60", "#1E88E5", "#43A047", "#FB8C00", "#7CB342",
    "#8E24AA", "#039BE5", "#66BB6A", "#FFA726", "#26A69A"
]
used_colors = set(SKILL_COLORS.values())
available_fallbacks = [c for c in fallback_colors if c not in used_colors]
color_index = 0

# Asignar colores únicos a skills no definidos
for skill in filtered_df["Skills"].dropna().str.split(", ").explode().str.strip().unique():
    skill_clean = skill.strip()
    if skill_clean not in SKILL_COLORS:
        # Evitar colores ya usados
        while color_index < len(available_fallbacks) - 1 and available_fallbacks[color_index] in used_colors:
            color_index += 1
        SKILL_COLORS[skill_clean] = available_fallbacks[color_index % len(available_fallbacks)]
        used_colors.add(SKILL_COLORS[skill_clean])
        color_index += 1

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
                color = SKILL_COLORS.get(skill, "#1976D2")  # Azul por defecto si no está
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

        # Ajustar zoom según cantidad de proyectos
        zoom_start = 12 if len(filtered_df) == 1 else 5

        map_ = folium.Map(
            location=[lat_center, lon_center],
            zoom_start=zoom_start,
            tiles="CartoDB positron",
            control_scale=True
        )

        # Añadir todos los marcadores
        for _, row in filtered_df.iterrows():
            folium.Marker(
                [row["Latitud"], row["Longitud"]],
                tooltip=row["Project_Name"],
                icon=folium.Icon(color="darkblue", icon="map-marker")
            ).add_to(map_)

        # Ajustar vista si hay más de un proyecto
        if len(filtered_df) > 1:
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
