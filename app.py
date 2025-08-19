import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Configuración de layout amplio
st.set_page_config(layout="wide")

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

CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dmf2pbdlq/image/upload/"

with col1:
    st.subheader("Skills")
    if not filtered_df.empty and "Skills" in filtered_df.columns:
        skills_counts = filtered_df["Skills"].str.split(", ").explode().value_counts()
        if not skills_counts.empty:
            fig = px.pie(
                names=skills_counts.index,
                values=skills_counts.values,
                title="Skills",
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

    # Logos (display only unique logos)
    st.subheader("Logos")
    if "Logo" in filtered_df.columns:
        # Extract all logos, split by comma, strip whitespace, and get unique values
        all_logos = set()
        for logo_list in filtered_df["Logo"].dropna():
            for logo in logo_list.split(","):
                all_logos.add(logo.strip())
        logos = list(all_logos)
        if logos:
            cols = st.columns(min(len(logos), 6))
            for idx, logo in enumerate(logos):
                logo_url = f"{CLOUDINARY_BASE_URL}logos/{logo}"
                st.write(f"Attempting to load logo: {logo_url}")  # Debugging output
                try:
                    cols[idx % 6].image(logo_url, width=50)
                except Exception as e:
                    cols[idx % 6].warning(f"No se pudo cargar el logo: {logo} (Error: {e})")
        else:
            st.info("No hay logos disponibles.")

with col2:
    st.subheader("Mapa")
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
# 5. Fila: Imágenes (1 fila horizontal)
# =========================
st.subheader("Imágenes")
if "image_link" in filtered_df.columns:
    image_links = filtered_df["image_link"].dropna().tolist()
    if image_links:
        cols = st.columns(min(len(image_links), 6))
        for idx, image_url in enumerate(image_links):
            st.write(f"Attempting to load image: {image_url}")  # Debugging output
            try:
                cols[idx % 6].image(image_url, use_column_width=True)  # Changed to use_column_width
            except Exception as e:
                cols[idx % 6].warning(f"No se pudo cargar la imagen desde {image_url} (Error: {e})")
    else:
        st.info("No hay enlaces de imágenes disponibles.")
else:
    st.warning("No se encontró la columna 'image_link' en los datos.")

# =========================
# 6. Tabla de datos
# =========================
st.subheader("Tabla de datos")
show_cols = [
    col for col in ["Project_Name", "Industry", "Scope", "Functions", "Client_Company", "Country"]
    if col in filtered_df.columns
]
if not filtered_df.empty:
    st.dataframe(filtered_df[show_cols])
else:
    st.info("No hay datos para mostrar.")
