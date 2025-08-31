import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# =========================
# 1. Configuración inicial
# =========================
st.set_page_config(layout="wide")

# =========================
# 2. CSS Personalizado
# =========================
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
    /* Botones de navegación */
    .nav-button {
        display: block;
        padding: 10px 15px;
        margin: 6px 0;
        background-color: #1a73e8;
        color: white !important;
        text-decoration: none;
        font-size: 0.95rem;
        font-weight: 500;
        border-radius: 8px;
        text-align: left;
        transition: background-color 0.3s ease, transform 0.1s ease;
        border: 1px solid #1557b0;
    }
    .nav-button:hover {
        background-color: #1557b0;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .nav-button:active {
        background-color: #0d47a1;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .logo-container img {
        transition: transform 0.3s ease;
    }
    .logo-container img:hover {
        transform: scale(1.03);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 3. Sidebar de Navegación Kronos GMT
# =========================
def create_navigation_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="logo-container">
            <a href="https://kronosgmt.com" target="_blank">
                <img src="https://res.cloudinary.com/dmbgxvfo0/image/upload/v1754540320/Logos_Kronos_PNG-04_nxdbz3.png" 
                     alt="Kronos GMT Logo"
                     style="width: 280px; height: auto; border-radius: 10px; cursor: pointer;">
            </a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='text-align: center; color: #07b9d1;'>Servicios</h3>", unsafe_allow_html=True)

        with st.expander("🔍 Ver servicios", expanded=True):
            st.markdown("""
            <a href="https://www.kronosgmt.com/3D-rendering" target="_blank" class="nav-button">
                🖼️ 3D Rendering
            </a>
            """, unsafe_allow_html=True)

            st.markdown("""
            <a href="https://www.kronosgmt.com/CAD-drafting" target="_blank" class="nav-button">
                📐 CAD Drafting
            </a>
            """, unsafe_allow_html=True)

            st.markdown("""
            <a href="https://www.kronosgmt.com/takeoffs-schedules" target="_blank" class="nav-button">
                📊 Takeoffs & Schedules
            </a>
            """, unsafe_allow_html=True)

            st.markdown("""
            <a href="https://www.kronosgmt.com/GIS-mapping" target="_blank" class="nav-button">
                🌍 GIS Mapping
            </a>
            """, unsafe_allow_html=True)

            st.markdown("""
            <a href="https://www.kronosgmt.com/automation-workflow-optimization" target="_blank" class="nav-button">
                ⚙️ Automation & Workflow Optimization
            </a>
            """, unsafe_allow_html=True)

        st.markdown("""
        <a href="https://news.kronosgmt.com/" target="_blank" class="nav-button">
            📰 Noticias
        </a>
        """, unsafe_allow_html=True)

        st.markdown("""
        <a href="https://www.kronosgmt.com/#contact" target="_blank" class="nav-button">
            📞 Contacto
        </a>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border: 1px solid #34495e;'>", unsafe_allow_html=True)

# Llamar al sidebar
create_navigation_sidebar()

# =========================
# 4. Cargar los datos
# =========================
@st.cache_data
def load_data():
    data_url = "https://raw.githubusercontent.com/juancanolop/Dashboard_Juan_Cano/main/data.csv"
    try:
        df = pd.read_csv(data_url)
        df.columns = df.columns.str.strip()
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
# 5. Filtros
# =========================
# Año
years = sorted(df["Year"].dropna().unique())
year_options = ["All"] + list(years)

selected_years_sidebar = st.sidebar.multiselect(
    "Filtrar años",
    options=year_options,
    default=["All"]
)

# Timeline
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

# Filtro categorías
categories = sorted(df["Category"].dropna().unique()) if "Category" in df.columns else []
selected_categories = st.sidebar.multiselect("Categorías", categories)

# =========================
# 6. Filtrar datos
# =========================
filtered_df = df[df["Year"].isin(years_to_use)]

if selected_industries:
    filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industries)]

if selected_categories:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]

# =========================
# 7. Fila: Skills + Logos vs Mapa
# =========================
col1, col2 = st.columns([1, 1])

CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dmf2pbdlq/image/upload/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

SKILL_COLORS = {
    "GIS": "#4285F4", "Survey": "#FBBC05", "Network Analysis": "#EA4335",
    "CAD Drafting": "#34A853", "Dashboard": "#FF6D01", "Python": "#3776AB",
    "Excel": "#217346", "AutoCAD": "#0A97D9", "Revit": "#C51152",
    "Rhino": "#7D66DD", "Grasshopper": "#1A1A1A", "ArcGIS": "#228B22",
    "QGIS": "#377EB8", "Power BI": "#F2C811", "Civil 3D": "#00A9CE",
    "PMI": "#5855B8", "LinkedIn": "#0077B5", "Remote Sensing": "#005F5D",
    "Data Analysis": "#8E24AA", "Machine Learning": "#D81B60", "BIM": "#FFB300",
    "Urban Planning": "#6D4C41", "Geodesign": "#00897B", "3D Modeling": "#5E35B1",
    "Lidar": "#5D4037", "Hydrology": "#0277BD", "Infrastructure": "#00897B",
    "Project Management": "#E65100", "Consulting": "#311B92",
    "Feasibility Study": "#C0CA33", "Environmental Impact": "#2E7D32",
    "Transportation": "#D84315", "Land Use": "#827717", "Geospatial": "#006064",
    "Topography": "#4E342E", "Photogrammetry": "#BF360C", "Design": "#AD1457",
    "Visualization": "#283593", "Planning": "#1B5E20", "Modeling": "#01579B",
    "Analysis": "#C62828", "Mapping": "#4A148C", "Simulation": "#EF6C00",
    "Optimization": "#2E7D32", "Reporting": "#8E24AA",
    "Stakeholder Engagement": "#B71C1C", "Field Work": "#33691E",
    "Data Collection": "#E64A19", "Risk Assessment": "#C2185B"
}

# Asignar colores a skills no definidos
fallback_colors = ["#D81B60", "#1E88E5", "#43A047", "#FB8C00", "#7CB342"]
used_colors = set(SKILL_COLORS.values())
available_fallbacks = [c for c in fallback_colors if c not in used_colors]
color_index = 0
for skill in filtered_df["Skills"].dropna().str.split(", ").explode().str.strip().unique():
    skill_clean = skill.strip()
    if skill_clean not in SKILL_COLORS:
        SKILL_COLORS[skill_clean] = available_fallbacks[color_index % len(available_fallbacks)]
        used_colors.add(SKILL_COLORS[skill_clean])
        color_index += 1

with col1:
    # Skills
    st.markdown('<div class="section-header">Skills</div>', unsafe_allow_html=True)
    if not filtered_df.empty and "Skills" in filtered_df.columns:
        all_skills = {s.strip().strip('"\'[] ') for skill_list in filtered_df["Skills"].dropna() for s in str(skill_list).split(",") if s.strip()}
        skills_list = sorted(all_skills)
        if skills_list:
            cols_skills = st.columns(min(len(skills_list), 6))
            for idx, skill in enumerate(skills_list):
                color = SKILL_COLORS.get(skill, "#1976D2")
                with cols_skills[idx % 6]:
                    st.markdown(f"""
                    <div style="background-color: {color}; color: white; padding: 8px 12px; border-radius: 12px; text-align: center; font-size: 0.85rem; font-weight: 600; margin: 4px; min-width: 80px;">
                        {skill}
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("No hay skills disponibles.")
    else:
        st.warning("No hay datos de skills para mostrar.")

    # Logos
    st.markdown('<div class="section-header">Logos</div>', unsafe_allow_html=True)
    if "Software" in filtered_df.columns:
        all_software = {s.strip().replace(" ", "_").replace("-", "_").lower() for s_list in filtered_df["Software"].dropna() for s in str(s_list).split(",") if s.strip()}
        software_list = sorted(all_software)
        if software_list:
            cols_logos = st.columns(min(len(software_list), 6))
            for idx, software in enumerate(software_list):
                urls_to_try = [f"{CLOUDINARY_BASE_URL}logos/{software}.jpg", f"{CLOUDINARY_BASE_URL}logos/{software}.png"]
                success = any(requests.head(url, timeout=5, headers=HEADERS).status_code == 200 for url in urls_to_try)
                with cols_logos[idx % 6]:
                    if success:
                        st.image([url for url in urls_to_try if requests.head(url, timeout=5, headers=HEADERS).status_code == 200][0], width=80, use_container_width=False, clamp=True, channels="RGB")
                    else:
                        st.markdown('<div class="warning-text">⚠️</div>', unsafe_allow_html=True)
        else:
            st.info("No hay software/logos disponibles.")
    else:
        st.warning("No se encontró la columna 'Software' en los datos.")

with col2:
    st.markdown('<div class="section-header">Mapa</div>', unsafe_allow_html=True)
    if not filtered_df.empty and "Latitud" in filtered_df.columns and "Longitud" in filtered_df.columns:
        valid_locations = filtered_df.dropna(subset=["Latitud", "Longitud"])
        if not valid_locations.empty:
            lat_center = valid_locations["Latitud"].mean()
            lon_center = valid_locations["Longitud"].mean()
            zoom_start = 12 if len(valid_locations) == 1 else 5
            map_ = folium.Map(location=[lat_center, lon_center], zoom_start=zoom_start, tiles="CartoDB positron", control_scale=True)
            for _, row in valid_locations.iterrows():
                folium.Marker([row["Latitud"], row["Longitud"]], tooltip=row["Project_Name"], icon=folium.Icon(color="darkblue", icon="map-marker")).add_to(map_)
            if len(valid_locations) > 1:
                bounds = [[row["Latitud"], row["Longitud"]] for _, row in valid_locations.iterrows()]
                map_.fit_bounds(bounds, padding=(0.1, 0.1))
            st_folium(map_, height=600, use_container_width=True)
        else:
            st.warning("No hay coordenadas válidas.")
    else:
        st.warning("No hay datos geográficos.")

# =========================
# 8. Galería con "Cargar más"
# =========================
st.markdown('<div class="section-header">Galería de Proyectos</div>', unsafe_allow_html=True)
if "image_link" in filtered_df.columns and "Project_Name" in filtered_df.columns:
    valid_images = filtered_df[filtered_df["image_link"].apply(lambda x: pd.notna(x) and isinstance(x, str) and x.startswith("http"))].copy()
    if not valid_images.empty:
        shuffled_images = valid_images.sample(frac=1, random_state=None).reset_index(drop=True)
        per_page = 8
        st.write("### Destacados")
        cols1 = st.columns(4)
        for i, (_, row) in enumerate(shuffled_images.head(per_page).iterrows()):
            col = cols1[i % 4]
            with col:
                image_url = row["image_link"].strip()
                try:
                    if requests.head(image_url, timeout=5, headers=HEADERS).status_code == 200:
                        st.image(image_url, caption=f"{row['Project_Name']} ({int(row['Year'])})", use_container_width=True, clamp=True, channels="RGB")
                        if "Blog_Link" in filtered_df.columns and pd.notna(row.get("Blog_Link")):
                            st.markdown(f"[📖 Más Información]({row['Blog_Link']})", unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="image-placeholder">🖼️ No disponible</div>', unsafe_allow_html=True)
                except:
                    st.markdown('<div class="image-placeholder">⚠️ Error</div>', unsafe_allow_html=True)
        if len(shuffled_images) > per_page:
            if st.button("🔍 Cargar más proyectos"):
                st.write("### Más proyectos")
                more_images = shuffled_images.iloc[per_page:per_page*2]
                cols2 = st.columns(4)
                for i, (_, row) in enumerate(more_images.iterrows()):
                    col = cols2[i % 4]
                    with col:
                        image_url = row["image_link"].strip()
                        try:
                            if requests.head(image_url, timeout=5, headers=HEADERS).status_code == 200:
                                st.image(image_url, caption=f"{row['Project_Name']} ({int(row['Year'])})", use_container_width=True, clamp=True, channels="RGB")
                                if "Blog_Link" in filtered_df.columns and pd.notna(row.get("Blog_Link")):
                                    st.markdown(f"[📖 Más Información]({row['Blog_Link']})", unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="image-placeholder">🖼️ No disponible</div>', unsafe_allow_html=True)
                        except:
                            st.markdown('<div class="image-placeholder">⚠️ Error</div>', unsafe_allow_html=True)
    else:
        st.info("No hay enlaces de imágenes válidos disponibles.")
else:
    st.warning("No se encontró la columna 'image_link' o 'Project_Name' en los datos.")

# =========================
# 9. Tabla de datos
# =========================
st.markdown('<div class="section-header">Tabla de datos</div>', unsafe_allow_html=True)
show_cols = [col for col in ["Project_Name", "Industry", "Scope", "Functions", "Client_Company", "Country"] if col in filtered_df.columns]
if not filtered_df.empty and show_cols:
    st.dataframe(filtered_df[show_cols], use_container_width=True)
else:
    st.info("No hay datos para mostrar.")
