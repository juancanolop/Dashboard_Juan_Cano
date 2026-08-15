"use client";

import { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Tooltip, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { Project } from "@/lib/types";
import Lightbox from "./Lightbox";

// react-leaflet's default marker icons reference image paths that bundlers
// don't resolve correctly, so point them at the CDN copies instead.
const redIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const blueIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface Props {
  projects: Project[];
  highlightYear: number;
}

/** Recenters/refits an already-mounted map instead of destroying and
 *  recreating it (which is what react-leaflet needs to avoid remounting the
 *  Leaflet container on every filter change). Zooms to fit whatever set of
 *  markers is currently visible whenever the filtered project list changes. */
function FitToMarkers({ locations }: { locations: Project[] }) {
  const map = useMap();
  useEffect(() => {
    if (locations.length === 0) return;
    if (locations.length === 1) {
      map.setView([locations[0].Latitud as number, locations[0].Longitud as number], 13, {
        animate: true,
      });
      return;
    }
    const bounds = L.latLngBounds(
      locations.map((p) => [p.Latitud as number, p.Longitud as number] as [number, number])
    );
    map.fitBounds(bounds, { padding: [40, 40], animate: true, maxZoom: 14 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [map, locations]);
  return null;
}

function MarkerPreview({ project }: { project: Project }) {
  const [failed, setFailed] = useState(false);
  const hasImage = project.ImageLink && project.ImageLink.startsWith("http") && !failed;

  return (
    <div className="w-40">
      {hasImage && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={project.ImageLink}
          alt={project.Project_Name}
          className="mb-1 h-24 w-full rounded object-cover"
          onError={() => setFailed(true)}
        />
      )}
      <p className="text-xs font-semibold leading-snug text-gray-900">
        {project.Project_Name} ({project.Year})
      </p>
    </div>
  );
}

/** The popup shown after clicking a marker: a bigger photo (click to open
 *  the full-screen lightbox) plus the scope of work, like a little fact
 *  sheet for the project. */
function MarkerPopup({ project, onOpenImage }: { project: Project; onOpenImage: (project: Project) => void }) {
  const [failed, setFailed] = useState(false);
  const hasImage = project.ImageLink && project.ImageLink.startsWith("http") && !failed;
  const whenText =
    project.ProjectSpan && project.ProjectSpan !== String(project.Year) ? project.ProjectSpan : String(project.Year);

  return (
    <div className="w-64">
      {hasImage && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={project.ImageLink}
          alt={project.Project_Name}
          className="mb-2 h-36 w-full cursor-zoom-in rounded object-cover transition hover:opacity-90"
          onError={() => setFailed(true)}
          onClick={() => onOpenImage(project)}
        />
      )}
      <p className="text-sm font-semibold leading-snug text-gray-900">{project.Project_Name}</p>
      <p className="mt-0.5 text-xs text-gray-500">
        {whenText}
        {project.Industry ? ` · ${project.Industry}` : ""}
      </p>
      {project.ScopeOfWork && (
        <p className="mt-1.5 max-h-24 overflow-y-auto text-xs leading-snug text-gray-700">{project.ScopeOfWork}</p>
      )}
      {hasImage && (
        <button
          onClick={() => onOpenImage(project)}
          className="mt-1.5 text-xs font-medium text-blue-600 hover:underline"
        >
          🔍 View larger
        </button>
      )}
    </div>
  );
}

export default function ProjectMap({ projects, highlightYear }: Props) {
  const [lightboxProject, setLightboxProject] = useState<Project | null>(null);

  const locations = useMemo(
    () => projects.filter((p) => p.Latitud !== null && p.Longitud !== null),
    [projects]
  );

  const initialCenter = useMemo((): [number, number] => {
    if (locations.length === 0) return [4.5, -74.3]; // fallback: Colombia
    const lat = locations.reduce((sum, p) => sum + (p.Latitud ?? 0), 0) / locations.length;
    const lon = locations.reduce((sum, p) => sum + (p.Longitud ?? 0), 0) / locations.length;
    return [lat, lon];
  }, [locations]);

  if (locations.length === 0) {
    return <p className="text-sm text-amber-300">No valid coordinates found for selected filters.</p>;
  }

  return (
    <div>
      <MapContainer
        center={initialCenter}
        zoom={locations.length === 1 ? 13 : 5}
        scrollWheelZoom
        style={{ height: "600px", width: "100%", borderRadius: "8px" }}
      >
        <FitToMarkers locations={locations} />
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        {locations.map((p, idx) => (
          <Marker
            key={`${p.Project_Name}-${p.Year}-${idx}`}
            position={[p.Latitud as number, p.Longitud as number]}
            icon={p.Year === highlightYear ? redIcon : blueIcon}
          >
            <Tooltip direction="top" offset={[0, -35]} opacity={1}>
              <MarkerPreview project={p} />
            </Tooltip>
            <Popup minWidth={240} maxWidth={280}>
              <MarkerPopup project={p} onOpenImage={setLightboxProject} />
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      <p className="mt-2 text-xs text-muted">
        🔴 <span className="text-red-400">Timeline Year Projects</span> | 🔵{" "}
        <span className="text-blue-400">Other Years</span>
      </p>

      {lightboxProject && (
        <Lightbox
          imageUrl={lightboxProject.ImageLink}
          caption={`${lightboxProject.Project_Name} — ${
            lightboxProject.DurationDisplay || lightboxProject.ProjectSpan
          }`}
          onClose={() => setLightboxProject(null)}
        />
      )}
    </div>
  );
}
