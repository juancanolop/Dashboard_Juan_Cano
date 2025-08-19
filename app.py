import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import requests
from PIL import Image
import io

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
    .success-text {
        color: #2ecc71;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Funciones auxiliares para imágenes
# =========================
def validate_url(url):
    """Valida si una URL es accesible"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def load_image_from_url(url, max_retries=3):
    """Carga una imagen desde una URL con reintentos"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10, stream=True)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                return image
        except Exception as e:
            if attempt == max_retries - 1:
                st.error(f"Error cargando imagen después de {max_retries} intentos: {e}")
            continue
    return None

def get_cloudinary_url(public_id, cloud_name="dmf2pbdlq", format_ext="jpg", transformations=""):
    """Genera URL de Cloudinary con formato correcto"""
    base_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/"
    if transformations:
        return f"{base_url}{transformations}/{public_id}.{format_ext}"
    return f"{base_url}{public_id}.{format_ext}"

# =========================
# 1. Cargar los datos
# =========================
@st.cache_data
def load_data():
    data_url = "https://raw.githubusercontent.com/juancanolop/Dashboard_Juan_Cano/main/data.csv"
    try:
        df = pd.read_csv(data_url)
        df.columns = df.columns.str.strip()
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

# Debugging: Mostrar información sobre las columnas
with st.expander("🔍 Debug Info - Columnas disponibles"):
    st.write("Columnas en el DataFrame:", list(df.columns))
    if "Software" in df.columns:
        st.write("Ejemplos de Software:", df["Software"].dropna().head().tolist())
    if "image_link" in df.columns:
        st.write("Ejemplos de image_link:", df["image_link"].dropna().head().tolist())

# =========================
# 2. Filtros (sidebar y arriba)
# =========================
st.sidebar.header("Filtros")

# Año: incluir "All"
years = sorted(df["Year"].dropna().unique())
year_options = ["All"] + years

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

# Unir lógica de selección
if selected_year_slider not in selected_years_sidebar:
    selected_years_sidebar.append(selected_year_slider)

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

with col1:
    st.markdown('<div class="section-header">Skills</div>', unsafe_allow_html=True)
    if not filtered_df.empty and "Skills" in filtered_df.columns:
        skills_counts = filtered_df["Skills"].str.split(", ").explode().value_counts()
        if not skills_counts.empty:
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

    # Logos mejorados con validación
    st.markdown('<div class="section-header">Logos</div>', unsafe_allow_html=True)
    if "Software" in filtered_df.columns:
        # Extract all software names, strip whitespace, and get unique values
        all_software = set()
        for software_list in filtered_df["Software"].dropna():
            if pd.notna(software_list) and isinstance(software_list, str):
                for software in software_list.split(","):
                    software_clean = software.strip()
                    if software_clean:  # Only add non-empty strings
                        all_software.add(software_clean)
        
        software_logos = sorted(list(all_software))
        if software_logos:
            st.write(f"Encontrados {len(software_logos)} logos únicos")
            
            # Crear múltiples filas de columnas si hay muchos logos
            logos_per_row = 6
            for i in range(0, len(software_logos), logos_per_row):
                row_logos = software_logos[i:i+logos_per_row]
                cols = st.columns(len(row_logos))
                
                for idx, software in enumerate(row_logos):
                    with cols[idx]:
                        # Intentar diferentes formatos de imagen
                        success = False
                        for ext in ['jpg', 'png', 'jpeg', 'webp']:
                            logo_url = get_cloudinary_url(f"logos/{software}", format_ext=ext)
                            
                            if validate_url(logo_url):
                                try:
                                    image = load_image_from_url(logo_url)
                                    if image:
                                        st.image(image, caption=software, width=60)
                                        st.markdown(f'<div class="success-text">✅ {software}</div>', unsafe_allow_html=True)
                                        success = True
                                        break
                                except Exception as e:
                                    continue
                        
                        if not success:
                            # Mostrar placeholder o error
                            st.markdown(f'<div class="warning-text">❌ No se pudo cargar: {software}</div>', unsafe_allow_html=True)
                            # Opcional: mostrar URLs intentadas para debugging
                            if st.checkbox(f"Debug URLs para {software}", key=f"debug_{software}"):
                                for ext in ['jpg', 'png', 'jpeg', 'webp']:
                                    test_url = get_cloudinary_url(f"logos/{software}", format_ext=ext)
                                    st.text(f"{ext.upper()}: {test_url}")
        else:
            st.info("No hay software/logos disponibles en los datos filtrados.")
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
# 5. Fila: Imágenes mejoradas (Project Gallery style)
# =========================
st.markdown('<div class="section-header">Galería de Proyectos</div>', unsafe_allow_html=True)
if "image_link" in filtered_df.columns and "Project_Name" in filtered_df.columns:
    valid_images = filtered_df[
        (filtered_df["image_link"].notna()) & 
        (filtered_df["image_link"] != "") &
        (filtered_df["image_link"].str.startswith(('http', 'https'), na=False))
    ]
    
    if not valid_images.empty:
        st.write(f"Mostrando {len(valid_images)} imágenes de proyectos")
        
        # Crear galería con mejor manejo de errores
        images_per_row = 4
        for i in range(0, min(len(valid_images), 12), images_per_row):  # Limitar a 12 imágenes
            row_images = valid_images.iloc[i:i+images_per_row]
            cols = st.columns(len(row_images))
            
            for idx, (_, row) in enumerate(row_images.iterrows()):
                with cols[idx]:
                    image_url = row["image_link"]
                    project_name = row["Project_Name"]
                    
                    # Validar URL antes de intentar cargar
                    if validate_url(image_url):
                        try:
                            image = load_image_from_url(image_url)
                            if image:
                                st.image(image, caption=project_name, use_column_width=True)
                                st.markdown(f'<div class="success-text">✅ Cargado correctamente</div>', unsafe_allow_html=True)
                                
                                # Optional: Add a "Más Información" link if a column like 'Blog_Link' exists
                                if "Blog_Link" in filtered_df.columns and pd.notna(row.get("Blog_Link")):
                                    st.markdown(f"[📖 Más Información]({row['Blog_Link']})")
                            else:
                                st.markdown(f'<div class="warning-text">❌ Error al procesar imagen para {project_name}</div>', unsafe_allow_html=True)
                                st.text(f"URL: {image_url}")
                        except Exception as e:
                            st.markdown(f'<div class="warning-text">❌ Error cargando {project_name}: {str(e)[:50]}...</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="warning-text">❌ URL no accesible: {project_name}</div>', unsafe_allow_html=True)
                        st.text(f"URL: {image_url}")
    else:
        st.info("No hay enlaces de imágenes válidos disponibles en los datos filtrados.")
        
        # Mostrar información de debugging
        if st.checkbox("Mostrar URLs de imágenes para debugging"):
            st.write("URLs encontradas:")
            for idx, row in filtered_df.iterrows():
                if "image_link" in row and pd.notna(row["image_link"]):
                    st.text(f"{row['Project_Name']}: {row['image_link']}")
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
if not filtered_df.empty:
    st.dataframe(filtered_df[show_cols])
else:
    st.info("No hay datos para mostrar.")

# =========================
# 7. Información de debugging adicional
# =========================
with st.expander("🔧 Información de debugging avanzada"):
    st.write("**Total de filas en datos originales:**", len(df))
    st.write("**Total de filas después del filtrado:**", len(filtered_df))
    
    if "image_link" in df.columns:
        st.write("**Análisis de image_link:**")
        total_images = df["image_link"].notna().sum()
        valid_http_images = df["image_link"].str.startswith(('http', 'https'), na=False).sum()
        st.write(f"- Total de imágenes no nulas: {total_images}")
        st.write(f"- URLs válidas (http/https): {valid_http_images}")
    
    if "Software" in df.columns:
        st.write("**Análisis de Software:**")
        software_entries = df["Software"].notna().sum()
        st.write(f"- Entradas de software no nulas: {software_entries}")
        if software_entries > 0:
            # Mostrar algunos ejemplos
            st.write("- Ejemplos de software:")
            for software_list in df["Software"].dropna().head(3):
                st.text(f"  {software_list}")
