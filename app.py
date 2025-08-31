import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# =========================
# 1. Initial Configuration
# =========================
st.set_page_config(layout="wide")

# =========================
# 2. Custom CSS
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
    /* Navigation buttons */
    .nav-button {
        display: block;
        padding: 10px 15px;
        margin: 6px 0;
        background-color: #2d3436;
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
# 3. Navigation Sidebar - Juan David Cano
# =========================
def create_navigation_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="logo-container">
            <a href="https://www.juandavidcano.com/" target="_blank">
                <img src="https://res.cloudinary.com/dmf2pbdlq/image/upload/v1756601724/Profile_zwgeyn.png" 
                     alt="Juan David Cano"
                     style="width: 280px; height: auto; border-radius: 30px; cursor: pointer;">
            </a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <a href="https://www.linkedin.com/in/juan-david-cano/" target="_blank" class="nav-button">
            LinkedIn
        </a>
        """, unsafe_allow_html=True)

        st.markdown("""
        <a href="https://news.kronosgmt.com/" target="_blank" class="nav-button">
            Blog
        </a>
        """, unsafe_allow_html=True)

        st.markdown("""
        <a href="https://calendly.com/juancano-kronosgmt/introduction-meeting" target="_blank" class="nav-button">
            Contact Me
        </a>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border: 1px solid #34495e;'>", unsafe_allow_html=True)

# Call the sidebar function
create_navigation_sidebar()

# =========================
# 4. Load Data
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
        st.error(f"Error loading CSV file: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.error("Failed to load data. Please check the CSV URL.")
    st.stop()

# =========================
# 5. Filters
# =========================
# Year
years = sorted(df["Year"].dropna().unique())
year_options = ["All"] + list(years)

selected_years_sidebar = st.sidebar.multiselect(
    "Filter years",
    options=year_options,
    default=["All"]
)

# Timeline slider
st.title("Projects Dashboard")
selected_year_slider = st.slider(
    "Select a year (slider)",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=int(max(years)),
    key="timeline-slider"
)

# === LÓGICA DE FILTRADO: Intersección entre sidebar y slider ===
if "All" in selected_years_sidebar:
    years_from_sidebar = years
else:
    years_from_sidebar = [y for y in selected_years_sidebar if isinstance(y, int)]

# Solo incluir el año del slider si está en los seleccionados del sidebar
years_to_use = [selected_year_slider] if selected_year_slider in years_from_sidebar else []

# Si no hay años comunes, mostrar advertencia y detener
if not years_to_use:
    st.warning("⚠️ No data matches the selected years. Adjust your filters.")
    st.stop()

# --- Industry Filter (safe) ---
if "Industry" in df.columns:
    industries = sorted(df["Industry"].dropna().unique())
    selected_industries = st.sidebar.multiselect("Industries", industries)
else:
    selected_industries = []  # Definir vacío si no existe la columna
    st.sidebar.info("No 'Industry' column in data.")

# --- Category Filter (safe) ---
if "Category" in df.columns:
    categories = sorted(df["Category"].dropna().unique())
    selected_categories = st.sidebar.multiselect("Categories", categories)
else:
    selected_categories = []  # Definir vacío si no existe
    st.sidebar.info("No 'Category' column in data.")

# =========================
# 6. Apply Filters
# =========================
filtered_df = df[df["Year"].isin(years_to_use)]

if selected_industries:
    filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industries)]

if selected_categories:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]

# =========================
# 7. Row: Skills + Logos vs Map
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

# Assign fallback colors for undefined skills
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
    # Skills Section
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
            st.info("No skills available.")
    else:
        st.warning("No skill data to display.")

    # Software Logos Section
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
                    f"{CLOUDINARY_BASE_URL}logos/{software}.png",
                    f"{CLOUDINARY_BASE_URL}logos/{software}.jpg",
                    f"{CLOUDINARY_BASE_URL}{software}.png",
                    f"{CLOUDINARY_BASE_URL}{software}.jpg"
                ]

                img_url = None
                success = False

                for url in urls_to_try:
                    try:
                        response = requests.head(url.strip(), timeout=5, headers=HEADERS)
                        if response.status_code == 200:
                            img_url = url.strip()
                            success = True
                            break
                    except Exception:
                        continue

                with cols_logos[idx % 6]:
                    if success and img_url:
                        try:
                            st.image(img_url, width=80, use_container_width=False, clamp=True, channels="RGB")
                        except Exception:
                            st.markdown('<div class="warning-text">⚠️</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f'<div style="font-size: 0.7rem; color: #b0b0b0; text-align: center;">{software}</div>',
                            unsafe_allow_html=True
                        )
        else:
            st.info("No software available.")
    else:
        st.warning("No 'Software' column found in data.")

with col2:
    # Map Section
    st.markdown('<div class="section-header">Map</div>', unsafe_allow_html=True)
    if not filtered_df.empty and "Latitud" in filtered_df.columns and "Longitud" in filtered_df.columns:
        valid_locations = filtered_df.dropna(subset=["Latitud", "Longitud"])
        if not valid_locations.empty:
            lat_center = valid_locations["Latitud"].mean()
            lon_center = valid_locations["Longitud"].mean()
            zoom_start = 12 if len(valid_locations) == 1 else 5
            map_ = folium.Map(location=[lat_center, lon_center], zoom_start=zoom_start, tiles="CartoDB positron", control_scale=True)
            for _, row in valid_locations.iterrows():
                folium.Marker(
                    [row["Latitud"], row["Longitud"]],
                    tooltip=row["Project_Name"],
                    icon=folium.Icon(color="darkblue", icon="map-marker")
                ).add_to(map_)
            if len(valid_locations) > 1:
                bounds = [[row["Latitud"], row["Longitud"]] for _, row in valid_locations.iterrows()]
                map_.fit_bounds(bounds, padding=(0.1, 0.1))
            st_folium(map_, height=600, use_container_width=True)
        else:
            st.warning("No valid coordinates found.")
    else:
        st.warning("No geographic data available.")

# =========================
# 8. Project Gallery with "Load More"
# =========================
st.markdown('<div class="section-header">Project Gallery</div>', unsafe_allow_html=True)
if "image_link" in filtered_df.columns and "Project_Name" in filtered_df.columns:
    valid_images = filtered_df[filtered_df["image_link"].apply(lambda x: pd.notna(x) and isinstance(x, str) and x.startswith("http"))].copy()
    if not valid_images.empty:
        shuffled_images = valid_images.sample(frac=1, random_state=None).reset_index(drop=True)
        per_page = 8
        st.write("### Featured Projects")
        cols1 = st.columns(4)
        for i, (_, row) in enumerate(shuffled_images.head(per_page).iterrows()):
            col = cols1[i % 4]
            with col:
                image_url = row["image_link"].strip()
                try:
                    if requests.head(image_url, timeout=5, headers=HEADERS).status_code == 200:
                        st.image(
                            image_url,
                            caption=f"{row['Project_Name']} ({int(row['Year'])})",
                            use_container_width=True,
                            clamp=True,
                            channels="RGB"
                        )
                        if "Blog_Link" in filtered_df.columns and pd.notna(row.get("Blog_Link")):
                            st.markdown(f"[📖 More Information]({row['Blog_Link']})", unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="image-placeholder">🖼️ Not Available</div>', unsafe_allow_html=True)
                except Exception:
                    st.markdown('<div class="image-placeholder">⚠️ Error</div>', unsafe_allow_html=True)

        if len(shuffled_images) > per_page:
            if st.button("🔍 Load More Projects"):
                st.write("### More Projects")
                more_images = shuffled_images.iloc[per_page:per_page*2]
                cols2 = st.columns(4)
                for i, (_, row) in enumerate(more_images.iterrows()):
                    col = cols2[i % 4]
                    with col:
                        image_url = row["image_link"].strip()
                        try:
                            if requests.head(image_url, timeout=5, headers=HEADERS).status_code == 200:
                                st.image(
                                    image_url,
                                    caption=f"{row['Project_Name']} ({int(row['Year'])})",
                                    use_container_width=True,
                                    clamp=True,
                                    channels="RGB"
                                )
                                if "Blog_Link" in filtered_df.columns and pd.notna(row.get("Blog_Link")):
                                    st.markdown(f"[📖 More Information]({row['Blog_Link']})", unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="image-placeholder">🖼️ Not Available</div>', unsafe_allow_html=True)
                        except Exception:
                            st.markdown('<div class="image-placeholder">⚠️ Error</div>', unsafe_allow_html=True)
    else:
        st.info("No valid image links available.")
else:
    st.warning("The 'image_link' or 'Project_Name' column was not found in the data.")

# =========================
# 9. Data Table
# =========================
st.markdown('<div class="section-header">Data Table</div>', unsafe_allow_html=True)
show_cols = [col for col in ["Project_Name", "Industry", "Scope", "Functions", "Client_Company", "Country"] if col in filtered_df.columns]
if not filtered_df.empty and show_cols:
    st.dataframe(filtered_df[show_cols], use_container_width=True)
else:
    st.info("No data to display.")
