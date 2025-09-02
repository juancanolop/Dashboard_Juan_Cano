import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import random
import hashlib

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
    .filter-info {
        background-color: #1e2329;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #07b9d1;
    }
    .filter-info small {
        color: #b0b0b0;
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

create_navigation_sidebar()

# =========================
# 4. Load Data with Project Duration Logic
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

def expand_projects_by_duration(df):
    if df.empty: return df

    duration_col = next((col for col in ['Duration_Months', 'Duration', 'Months', 'Project_Duration'] if col in df.columns), None)
    if not duration_col: return df

    expanded_rows = []
    for _, row in df.iterrows():
        try:
            duration_months = row[duration_col]
            if pd.isna(duration_months) or duration_months <= 0:
                expanded_rows.append(row.copy())
                continue
            duration_months = int(float(duration_months))
            start_year = int(row['Year'])
            end_year = start_year + (duration_months // 12)
            years_affected = list(range(start_year, end_year + 1))

            for year in years_affected:
                new_row = row.copy()
                new_row['Year'] = year
                new_row['Original_Year'] = start_year
                new_row['End_Year'] = end_year
                new_row['Project_Span'] = f"{start_year}-{end_year}" if len(years_affected) > 1 else str(start_year)
                new_row['Duration_Display'] = f"{duration_months} months ({start_year}-{end_year})" if len(years_affected) > 1 else f"{duration_months} months"
                expanded_rows.append(new_row)
        except:
            expanded_rows.append(row.copy())
    return pd.DataFrame(expanded_rows)

df = load_data()
if df.empty:
    st.error("Failed to load data. Please check the CSV URL.")
    st.stop()

df = expand_projects_by_duration(df)

# =========================
# 4.5 Filter by Visibility in Dashboard
# =========================
if "show dashboard" in df.columns:
    df = df[df["show dashboard"].astype(str).str.strip().str.lower() != "no"]
else:
    st.warning("⚠️ Column 'show dashboard' not found in data. Showing all projects.")

# =========================
# 5. Filters - SISTEMA MEJORADO
# =========================
years = sorted(df["Year"].dropna().unique())
min_year, max_year = int(min(years)), int(max(years))
st.title("Projects Dashboard")

filter_col1, filter_col2 = st.columns([2, 1])
with filter_col1:
    selected_year_slider = st.slider(
        "Select a specific year to highlight",
        min_value=min_year,
        max_value=max_year,
        value=max_year,
        key="timeline-slider",
        help="This will be included in the filter along with sidebar selections"
    )

with filter_col2:
    filter_mode = st.radio(
        "Filter Mode:",
        options=["Include timeline year", "Only sidebar selection"],
        index=0,
        help="Choose how to combine timeline and sidebar filters"
    )

# Sidebar filters
with st.sidebar:
    st.markdown("### 🎯 **Filters**")
    
    year_options = ["All"] + [str(year) for year in years]
    selected_years_sidebar = st.multiselect(
        "📅 Filter by years",
        options=year_options,
        default=["All"],
        help="Select specific years or 'All' for all years"
    )
    
    industries = sorted(df["Industry"].dropna().unique()) if "Industry" in df.columns else []
    selected_industries = st.multiselect("🏢 Industries", industries, help="Filter by industry type")

    categories = sorted(df["Category"].dropna().unique()) if "Category" in df.columns else []
    selected_categories = st.multiselect("📂 Categories", categories, help="Filter by project category") if categories else []

    # ✅ ARREGLADO: Filtro por Role con valores únicos
    if "Role" in df.columns:
        # Función para limpiar roles
        def clean_role_value(role):
            if pd.isna(role) or not isinstance(role, str):
                return "Other"
            role = role.strip()
            role_mappings = {
                'civil engineer': 'Civil Engineer',
                'ceo': 'CEO',
                'student': 'Student',
                'teacher': 'Teacher',
                'auxiliar / intern': 'Auxiliar / Intern',
                'project manager': 'Project Manager',
                'designer / consulter': 'Designer / Consulter',
            }
            role_lower = role.lower()
            for key, value in role_mappings.items():
                if key in role_lower:
                    return value
            return role.title() if role else "Other"
        
        # Obtener roles únicos y limpios
        unique_roles = sorted(set(df["Role"].dropna().apply(clean_role_value)))
        selected_roles = st.multiselect(
            "👤 Role", 
            unique_roles,
            help="Filter by your role in the project"
        )
    else:
        selected_roles = []

# =========================
# 6. Apply Filters - LÓGICA MEJORADA
# =========================
def get_filtered_years(sidebar_years, timeline_year, mode):
    sidebar_year_list = years if "All" in sidebar_years else [int(y) for y in sidebar_years if y.isdigit()]
    return sorted(set(sidebar_year_list + [timeline_year])) if mode == "Include timeline year" else sidebar_year_list

final_years = get_filtered_years(selected_years_sidebar, selected_year_slider, filter_mode)

filtered_df = df[df["Year"].isin(final_years)].copy()
if selected_industries:
    filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industries)]
if selected_categories:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]
if selected_roles and "Role" in filtered_df.columns:
    # Aplicar limpieza de roles al filtro
    def clean_role_value(role):
        if pd.isna(role) or not isinstance(role, str):
            return "Other"
        role = role.strip()
        role_mappings = {
            'civil engineer': 'Civil Engineer',
            'ceo': 'CEO',
            'student': 'Student',
            'teacher': 'Teacher',
            'auxiliar / intern': 'Auxiliar / Intern',
            'project manager': 'Project Manager',
            'designer / consulter': 'Designer / Consulter',
        }
        role_lower = role.lower()
        for key, value in role_mappings.items():
            if key in role_lower:
                return value
        return role.title() if role else "Other"
    
    filtered_df['Role_Clean'] = filtered_df["Role"].apply(clean_role_value)
    filtered_df = filtered_df[filtered_df["Role_Clean"].isin(selected_roles)]

# Mostrar información del filtro activo
st.markdown(f"""
<div class="filter-info">
    <strong>🔍 Active Filter:</strong> Showing {len(final_years)} year(s): {', '.join(map(str, final_years[:5]))}{'...' if len(final_years) > 5 else ''}
    <br><small>Timeline: {selected_year_slider} | Mode: {filter_mode}</small>
</div>
""", unsafe_allow_html=True)

if not filtered_df.empty:
    st.success(f"📊 Found **{len(filtered_df)} projects** matching your criteria")
else:
    st.warning("❌ No projects found with current filters. Try adjusting your selection.")

# =========================
# 7. Row: Skills + Logos vs Map
# =========================
col1, col2 = st.columns([1, 1])

CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dmf2pbdlq/image/upload/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ✅ ARREGLADO: Máximo 5 colores aleatorios para skills
def get_skill_color(skill_name):
    """Genera un color consistente en RGBA con opacidad basado en el hash del nombre del skill"""
    colors_palette_rgba = [
        "rgba(191, 144, 0, 0.5)",    # amarillo semitransparente
        "rgba(153, 0, 0, 0.5)",     # rojo semitransparente
        "rgba(11, 83, 148, 0.5)",   # azul semitransparente
        "rgba(56, 118, 29, 0.5)",   # verde semitransparente
        "rgba(53, 28, 117, 0.5)"    # violeta semitransparente
    ]
    hash_value = int(hashlib.md5(skill_name.encode()).hexdigest(), 16)
    return colors_palette_rgba[hash_value % len(colors_palette_rgba)]


# Sección Skills
with col1:
    st.markdown('<div class="section-header">Skills</div>', unsafe_allow_html=True)
    if not filtered_df.empty and "Skills" in filtered_df.columns:
        all_skills = set()
        for skill_list in filtered_df["Skills"].dropna():
            for skill in str(skill_list).split(","):
                # ✅ ARREGLADO: Quitar comillas y limpiar skills
                skill_clean = skill.strip().strip('"\'[]() ').replace('"', '').replace("'", "")
                if skill_clean:
                    all_skills.add(skill_clean)
        
        skills_list = sorted(all_skills)
        if skills_list:
            cols_skills = st.columns(min(len(skills_list), 6))
            for idx, skill in enumerate(skills_list):
                color = get_skill_color(skill)  # ✅ Color aleatorio consistente
                with cols_skills[idx % 6]:
                    st.markdown(f"""
                    <div style="background-color: {color}; color: white; padding: 8px 12px; border-radius: 12px; text-align: center; font-size: 0.85rem; font-weight: 600; margin: 4px; min-width: 80px;">
                        {skill}
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("No skills available for selected filters.")
    else:
        st.warning("No skill data to display.")

    # Software Logos
    st.markdown('<div class="section-header">Software</div>', unsafe_allow_html=True)
    if not filtered_df.empty and "Software" in filtered_df.columns:
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
                        st.image(img_url, width=80, use_container_width=False, clamp=True, channels="RGB")
                    else:
                        st.markdown(f'<div style="font-size: 0.7rem; color: #b0b0b0; text-align: center;">{software}</div>', unsafe_allow_html=True)
        else:
            st.info("No software available for selected filters.")
    else:
        st.warning("No 'Software' column found in data.")

# Mapa
with col2:
    st.markdown('<div class="section-header">Project Locations</div>', unsafe_allow_html=True)
    if not filtered_df.empty and "Latitud" in filtered_df.columns and "Longitud" in filtered_df.columns:
        valid_locations = filtered_df.dropna(subset=["Latitud", "Longitud"])
        if not valid_locations.empty:
            lat_center = valid_locations["Latitud"].mean()
            lon_center = valid_locations["Longitud"].mean()
            zoom_start = 12 if len(valid_locations) == 1 else 5
            map_ = folium.Map(location=[lat_center, lon_center], zoom_start=zoom_start, tiles="CartoDB positron", control_scale=True)
            for _, row in valid_locations.iterrows():
                color = "red" if row["Year"] == selected_year_slider else "darkblue"
                popup_text = f"<b>{row['Project_Name']}</b><br>Year: {int(row['Year'])}"
                if 'Project_Span' in row and pd.notna(row['Project_Span']):
                    popup_text += f"<br>Duration: {row['Project_Span']}"
                if 'Industry' in row:
                    popup_text += f"<br>Industry: {row.get('Industry', 'N/A')}"
                folium.Marker(
                    [row["Latitud"], row["Longitud"]],
                    popup=folium.Popup(popup_text, max_width=200),
                    tooltip=f"{row['Project_Name']} ({int(row['Year'])})",
                    icon=folium.Icon(color=color, icon="map-marker")
                ).add_to(map_)
            if len(valid_locations) > 1:
                bounds = [[row["Latitud"], row["Longitud"]] for _, row in valid_locations.iterrows()]
                map_.fit_bounds(bounds, padding=(0.1, 0.1))
            st_folium(map_, height=600, use_container_width=True)
            st.markdown("""<small>🔴 <span style="color: red;">Timeline Year Projects</span> | 🔵 <span style="color: blue;">Other Years</span></small>""", unsafe_allow_html=True)
        else:
            st.warning("No valid coordinates found for selected filters.")
    else:
        st.warning("No geographic data available.")

# =========================
# 8. Project Gallery - ARREGLADO: Una imagen única por proyecto considerando duración
# =========================
st.markdown('<div class="section-header">Project Gallery</div>', unsafe_allow_html=True)
if not filtered_df.empty and "image_link" in filtered_df.columns and "Project_Name" in filtered_df.columns:
    valid_images = filtered_df[filtered_df["image_link"].apply(lambda x: pd.notna(x) and isinstance(x, str) and x.startswith("http"))].copy()
    if not valid_images.empty:
        # ✅ ARREGLADO: Considerar proyectos activos en el año seleccionado
        def is_project_active_in_year(row, target_year):
            """Verifica si un proyecto está activo en el año objetivo"""
            if 'Original_Year' in row and 'End_Year' in row:
                original_year = int(row['Original_Year']) if pd.notna(row['Original_Year']) else int(row['Year'])
                end_year = int(row['End_Year']) if pd.notna(row['End_Year']) else original_year
                return original_year <= target_year <= end_year
            return int(row['Year']) == target_year
        
        # Obtener proyectos únicos
        unique_images = valid_images.drop_duplicates(subset='Project_Name', keep='first')
        
        # ✅ Clasificar proyectos según si están activos en el año del timeline
        timeline_projects = unique_images[unique_images.apply(lambda row: is_project_active_in_year(row, selected_year_slider), axis=1)]
        other_projects = unique_images[~unique_images.apply(lambda row: is_project_active_in_year(row, selected_year_slider), axis=1)]
        
        shuffled_others = other_projects.sample(frac=1, random_state=42).reset_index(drop=True)

        if not timeline_projects.empty:
            st.markdown(f"### 🎯 Projects Active in {selected_year_slider}")
            cols_timeline = st.columns(4)
            for i, (_, row) in enumerate(timeline_projects.head(8).iterrows()):
                col = cols_timeline[i % 4]
                with col:
                    image_url = row["image_link"].strip()
                    try:
                        if requests.head(image_url, timeout=5, headers=HEADERS).status_code == 200:
                            caption_text = f"⭐ {row['Project_Name']}"
                            if 'Duration_Display' in row and pd.notna(row['Duration_Display']):
                                caption_text += f" [{row['Duration_Display']}]"
                            elif 'Project_Span' in row and pd.notna(row['Project_Span']):
                                caption_text += f" [{row['Project_Span']}]"
                            else:
                                caption_text += f" ({int(row['Year'])})"
                            
                            st.image(image_url, caption=caption_text, use_container_width=True, clamp=True, channels="RGB")
                            if "Blog_Link" in row and pd.notna(row["Blog_Link"]):
                                st.markdown(f"[📖 More Information]({row['Blog_Link']})", unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="image-placeholder">🖼️ Not Available</div>', unsafe_allow_html=True)
                    except Exception:
                        st.markdown('<div class="image-placeholder">⚠️ Error</div>', unsafe_allow_html=True)

        if not shuffled_others.empty:
            st.markdown("### 📸 Other Projects")
            per_page = 8
            cols1 = st.columns(4)
            for i, (_, row) in enumerate(shuffled_others.head(per_page).iterrows()):
                col = cols1[i % 4]
                with col:
                    image_url = row["image_link"].strip()
                    try:
                        if requests.head(image_url, timeout=5, headers=HEADERS).status_code == 200:
                            caption_text = f"{row['Project_Name']}"
                            if 'Duration_Display' in row and pd.notna(row['Duration_Display']):
                                caption_text += f" [{row['Duration_Display']}]"
                            elif 'Project_Span' in row and pd.notna(row['Project_Span']):
                                caption_text += f" [{row['Project_Span']}]"
                            else:
                                caption_text += f" ({int(row['Year'])})"
                            
                            st.image(image_url, caption=caption_text, use_container_width=True, clamp=True, channels="RGB")
                            if "Blog_Link" in row and pd.notna(row["Blog_Link"]):
                                st.markdown(f"[📖 More Information]({row['Blog_Link']})", unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="image-placeholder">🖼️ Not Available</div>', unsafe_allow_html=True)
                    except Exception:
                        st.markdown('<div class="image-placeholder">⚠️ Error</div>', unsafe_allow_html=True)

            if len(shuffled_others) > per_page and st.button("🔍 Load More Projects"):
                st.markdown("### Additional Projects")
                more_images = shuffled_others.iloc[per_page:per_page*2]
                cols2 = st.columns(4)
                for i, (_, row) in enumerate(more_images.iterrows()):
                    col = cols2[i % 4]
                    with col:
                        image_url = row["image_link"].strip()
                        try:
                            if requests.head(image_url, timeout=5, headers=HEADERS).status_code == 200:
                                caption_text = f"{row['Project_Name']}"
                                if 'Duration_Display' in row and pd.notna(row['Duration_Display']):
                                    caption_text += f" [{row['Duration_Display']}]"
                                elif 'Project_Span' in row and pd.notna(row['Project_Span']):
                                    caption_text += f" [{row['Project_Span']}]"
                                else:
                                    caption_text += f" ({int(row['Year'])})"
                                
                                st.image(image_url, caption=caption_text, use_container_width=True, clamp=True, channels="RGB")
                                if "Blog_Link" in row and pd.notna(row["Blog_Link"]):
                                    st.markdown(f"[📖 More Information]({row['Blog_Link']})", unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="image-placeholder">🖼️ Not Available</div>', unsafe_allow_html=True)
                        except Exception:
                            st.markdown('<div class="image-placeholder">⚠️ Error</div>', unsafe_allow_html=True)
    else:
        st.info("No valid image links available for selected filters.")
else:
    st.warning("No projects found with current filter selection.")

# =========================
# 9. Data Table - ARREGLADO: Incluir Scope of Work y Duration
# =========================
st.markdown('<div class="section-header">Project Details</div>', unsafe_allow_html=True)
# ✅ ARREGLADO: Incluir Scope_of_work y Duration en la tabla
base_cols = ["Project_Name", "Year", "Role"]
optional_cols = ["Scope_of_work", "Duration_Display", "Functions", "Client_Company", "Country"]
show_cols = base_cols + [col for col in optional_cols if col in filtered_df.columns]

if not filtered_df.empty and show_cols:
    if 'Original_Year' in filtered_df.columns:
        unique_df = filtered_df.sort_values('Original_Year').drop_duplicates(subset='Project_Name', keep='first')
    else:
        unique_df = filtered_df.drop_duplicates(subset='Project_Name', keep='first')
    
    display_df = unique_df[show_cols].copy()
    
    # Asegurar que Year sea del año original
    if 'Original_Year' in unique_df.columns:
        display_df["Year"] = unique_df["Original_Year"].astype(int)
    else:
        display_df["Year"] = unique_df["Year"].astype(int)

    # ✅ Limpieza de la columna Role
    def clean_role(role):
        if pd.isna(role) or not isinstance(role, str):
            return "Other"
        role = role.strip()
        role_mappings = {
            'civil engineer': 'Civil Engineer',
            'ceo': 'CEO',
            'student': 'Student',
            'teacher': 'Teacher',
            'auxiliar / intern': 'Auxiliar / Intern',
            'project manager': 'Project Manager',
            'designer / consulter': 'Designer / Consulter',
        }
        role_lower = role.lower()
        for key, value in role_mappings.items():
            if key in role_lower:
                return value
        return role.title() if role else "Other"

    if "Role" in display_df.columns:
        display_df["Role"] = display_df["Role"].apply(clean_role)

    # Añadir ⭐ si está activo en el año seleccionado
    def is_active_in_timeline(row):
        if 'Original_Year' in row and 'End_Year' in row:
            try:
                original_year = int(row['Original_Year']) if pd.notna(row['Original_Year']) else int(row['Year'])
                end_year = int(row['End_Year']) if pd.notna(row['End_Year']) else original_year
                return original_year <= selected_year_slider <= end_year
            except:
                pass
        return int(row["Year"]) == selected_year_slider

    display_df["Year"] = display_df.apply(
        lambda row: f"⭐ {int(row['Year'])}" if is_active_in_timeline(row) else str(int(row['Year'])), axis=1
    )

    # ✅ Renombrar columnas para mejor presentación
    column_renames = {
        "Scope_of_work": "Scope of Work",
        "Duration_Display": "Duration",
        "Client_Company": "Client"
    }
    display_df = display_df.rename(columns={k: v for k, v in column_renames.items() if k in display_df.columns})

    st.dataframe(display_df, use_container_width=True, height=400)

    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    with col_stats1:
        st.metric("Unique Projects", len(unique_df))
    with col_stats2:
        active_count = display_df[display_df["Year"].str.contains("⭐", na=False)].shape[0]
        st.metric(f"Active in {selected_year_slider}", active_count)
    with col_stats3:
        year_range = f"{unique_df['Original_Year'].min():.0f}-{unique_df['Original_Year'].max():.0f}" if 'Original_Year' in unique_df.columns else f"{unique_df['Year'].min():.0f}-{unique_df['Year'].max():.0f}"
        st.metric("Project Year Range", year_range)
    with col_stats4:
        multi_year = unique_df[unique_df['Project_Span'].str.contains('-', na=False)].shape[0] if 'Project_Span' in unique_df.columns else 0
        st.metric("Multi-Year Projects", multi_year)
else:
    st.info("No data to display with current filters.")
