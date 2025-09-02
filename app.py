# =========================
# 1. Initial Configuration
# =========================
st.set_page_config(layout="wide")

# =========================
# 2. Custom CSS (sin cambios)
# =========================
st.markdown("""...""", unsafe_allow_html=True)  # Tu CSS original

# =========================
# 3. Navigation Sidebar (sin cambios)
# =========================
def create_navigation_sidebar(): ...  # Tu código original

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
    """Expande proyectos por duración en años."""
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
                new_row['Project_Span'] = f"{start_year}-{end_year}" if len(years_affected) > 1 else str(start_year)
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
# 4.5 Filter by Visibility
# =========================
if "show dashboard" in df.columns:
    df = df[df["show dashboard"].astype(str).str.strip().str.lower() != "no"]
else:
    st.warning("⚠️ Column 'show dashboard' not found. Showing all projects.")

# =========================
# 5. Filters - SISTEMA MEJORADO
# =========================
years = sorted(df["Year"].dropna().unique())
min_year, max_year = int(min(years)), int(max(years))
st.title("Projects Dashboard")

filter_col1, filter_col2 = st.columns([2, 1])
with filter_col1:
    selected_year_slider = st.slider("Select a specific year to highlight", min_year, max_year, max_year, help="Included in filters")
with filter_col2:
    filter_mode = st.radio("Filter Mode:", ["Include timeline year", "Only sidebar selection"], index=0)

# Sidebar filters
with st.sidebar:
    st.markdown("### 🎯 **Filters**")
    
    year_options = ["All"] + [str(year) for year in years]
    selected_years_sidebar = st.multiselect("📅 Filter by years", options=year_options, default=["All"])

    industries = sorted(df["Industry"].dropna().unique()) if "Industry" in df.columns else []
    selected_industries = st.multiselect("🏢 Industries", industries)

    categories = sorted(df["Category"].dropna().unique()) if "Category" in df.columns else []
    selected_categories = st.multiselect("📂 Categories", categories) if categories else []

    # ✅ Filtro por Role
    roles = sorted(df["Role"].dropna().unique()) if "Role" in df.columns else []
    if roles:
        selected_roles = st.multiselect(
            "👤 Role", 
            roles,
            help="Filter by your role in the project"
        )
    else:
        selected_roles = []

# =========================
# 6. Apply Filters
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
if selected_roles:
    filtered_df = filtered_df[filtered_df["Role"].isin(selected_roles)]

# Mostrar estadísticas
st.markdown(f"""<div class="filter-info">...""", unsafe_allow_html=True)
if not filtered_df.empty:
    st.success(f"📊 Found **{len(filtered_df)} projects** matching your criteria")
else:
    st.warning("❌ No projects found with current filters.")

# =========================
# 7. Skills, Logos & Map
# =========================
col1, col2 = st.columns([1, 1])

# ... (tu código original para Skills y Software)

# Mapa: sin cambios importantes
# ... (tu código original del mapa)

# =========================
# 8. Project Gallery - No Duplicates
# =========================
# ... (tu código original de galería, ya está bien)

# =========================
# 9. Data Table - Clean Role Display
# =========================
st.markdown('<div class="section-header">Project Details</div>', unsafe_allow_html=True)

# Columnas a mostrar
show_cols = [col for col in ["Project_Name", "Year", "Role", "Scope_of_work", "Functions", "Client_Company", "Country"] if col in filtered_df.columns]

if not filtered_df.empty and show_cols:
    # Deduplicar
    if 'Original_Year' in filtered_df.columns:
        unique_df = filtered_df.sort_values('Original_Year').drop_duplicates(subset='Project_Name', keep='first')
        display_df = unique_df[show_cols].copy()
        display_df["Year"] = unique_df["Original_Year"].astype(int)
    else:
        unique_df = filtered_df.drop_duplicates(subset='Project_Name', keep='first')
        display_df = unique_df[show_cols].copy()

    # ✅ Limpieza de la columna Role
    def clean_role(role):
        if pd.isna(role) or not isinstance(role, str):
            return "Other"
        role = role.strip().lower()
        replacements = {
            'civil engineer': 'Civil Engineer',
            'ceo': 'CEO',
            'student': 'Student',
            'teacher': 'Teacher',
            'auxiliar / intern': 'Auxiliar / Intern',
            'project manager': 'Project Manager',
            'designer / consulter': 'Designer / Consulter',
            
        }
        for key, value in replacements.items():
            if key in role:
                return value.title()
        return "Other"

    if "Role" in display_df.columns:
        display_df["Role"] = display_df["Role"].apply(clean_role)

    # Añadir ⭐ para proyectos activos en el año seleccionado
    def is_active_in_timeline(row):
        span = str(row.get("Project_Span", "")).strip()
        if "-" in span:
            try:
                start, end = map(int, span.split("-"))
                return start <= selected_year_slider <= end
            except:
                pass
        return row["Year"] == selected_year_slider

    display_df["Year"] = display_df.apply(
        lambda row: f"⭐ {int(row['Year'])}" if is_active_in_timeline(row) else str(int(row['Year'])), axis=1
    )

    # Renombrar si es necesario
    display_df = display_df.rename(columns={"Scope_of_work": "Scope"} if "Scope_of_work" in display_df.columns else {})

    # Mostrar tabla
    st.dataframe(display_df, use_container_width=True, height=400)

    # Métricas
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    with col_stats1:
        st.metric("Unique Projects", len(unique_df))
    with col_stats2:
        active_count = display_df[display_df["Year"].str.contains("⭐", na=False)].shape[0]
        st.metric(f"Active in {selected_year_slider}", active_count)
    with col_stats3:
        year_range = f"{unique_df['Original_Year'].min():.0f}-{unique_df['Original_Year'].max():.0f}"
        st.metric("Project Year Range", year_range)
    with col_stats4:
        multi_year = unique_df[unique_df['Project_Span'].str.contains('-', na=False)].shape[0]
        st.metric("Multi-Year Projects", multi_year)
else:
    st.info("No data to display with current filters.")
