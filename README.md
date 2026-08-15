# Juan David Cano — Projects Dashboard

This repo hosts the **interactive Projects Dashboard** shown at `dashboard.juandavidcano.com`, plus the
profile below. It used to be a Streamlit app (still kept in [`streamlit-legacy/`](streamlit-legacy/) for
reference); it's now a **Next.js / React app** so it can be deployed on Vercel while staying dynamic.

## 📊 Dashboard architecture

- **Stack**: Next.js 16 (App Router) + TypeScript + Tailwind CSS + react-leaflet.
- **Data source**: [`data.csv`](data.csv) in this repo — same file the old Streamlit app read. The app
  fetches it straight from GitHub's raw URL on the server, revalidating every 5 minutes, so **editing
  data.csv (e.g. from the GitHub web UI) updates the live dashboard within minutes — no redeploy needed.**
  If that fetch ever fails, it falls back to the copy of `data.csv` bundled in the deployment.
- **Images / logos**: unchanged — still served from Cloudinary via the `image_link` / `Software` columns.
- **Legacy Streamlit app**: moved to [`streamlit-legacy/`](streamlit-legacy/), kept only for reference. It's
  no longer deployed.

### Run it locally

```bash
npm install
npm run dev
```

### Deploy

Import this repo in [Vercel](https://vercel.com/new) (framework preset: Next.js, no extra config needed) and
point the `dashboard` subdomain at it. See the PR/commit description or ask Claude for the exact DNS steps.

---

🎯 **Civil Engineer | Project Manager | CAD/BIM Developer | Data Enthusiast**  

I'm a passionate **Civil Engineer** with a strong background in **land development, infrastructure design, and project management**.  
With over **10 years of experience** in **construction and project coordination**, I combine **technical expertise** with **innovative solutions** to deliver efficient and high-quality results.  

---

## 🧩 About Me  
- 🎓 **Bachelor’s in Civil Engineering** – Focused on structural design, geotechnics, and hydraulics.  
- 🎓 **Specialization in Transportation & Highway Engineering** – Expertise in roadway design and traffic analysis.  
- 🎓 **Specialization in Construction & Infrastructure Project Management** *(PMI PMBOK® 6 methodology)*.  
- 🎓 **Diploma in Project Management and Construction Works** *(80 hours)*.  
- 💻 Passionate about **CAD automation**, **BIM modeling**, and **Python-based tools** for engineering workflows.  

---

## 🛠️ Tech Stack  

### **Programming & Data**
- Python 🐍 (Pandas, NumPy, Matplotlib, Streamlit)
- CAD Automation (Pyautocad, Dynamo, Grasshopper)
- Data visualization & dashboards

### **CAD & BIM**
- AutoCAD LT | Civil 3D | Revit  
- CAD automation and scripting  
- BIM modeling and coordination  

### **GIS & Land Development**
- QGIS | ArcGIS  
- GeoJSON, shapefiles, and spatial data visualization  
- Land subdivision, utilities, and topographic analysis  

---

## 📂 Featured Projects  
Here are some of the engineering and software projects I'm currently working on:

- 🏗 **Pool Hydraulic Simulation App** *(Python)*  
  Calculates **Total Dynamic Head (TDH)** and verifies compliance with **2023 Florida Building Code (FBC)**.  

- 🌎 **QGIS App for Plumbing Systems** *(Python + QGIS)*  
  Automates pressure and velocity calculations for gravity, suction, and pressurized networks.  

- 📊 **Dynamic Project Dashboard** *(Next.js + React)*  
  Visualizes project timelines, schedules, and geospatial data for **construction planning** — this repo.  

---

## 📫 Connect with Me  

- 💼 [LinkedIn](https:///www.linkedin.com/in/juan-david-cano/)  
- 📧 Email: juancano@kronosgmt.com.com
- 📧 Email: juadcanolop@gmail.com
- 🌐 [Website](https://www.juandavidcano.com)
- 🌐 [Portfolio](https://[juan-cano-dashboard.streamlit.app/)

---

*“Transforming ideas into efficient engineering solutions.”*  
