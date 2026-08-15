"use client";

import { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, Tooltip, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { Project } from "@/lib/types";

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

/** Recenters an already-mounted map instead of destroying/recreating it,
 *  which is what react-leaflet needs to avoid remounting the Leaflet
 *  container on every filter change. */
function RecenterMap({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [map, center, zoom]);
  return null;
}

export default function ProjectMap({ projects, highlightYear }: Props) {
  const locations = useMemo(
    () => projects.filter((p) => p.Latitud !== null && p.Longitud !== null),
    [projects]
  );

  const center = useMemo((): [number, number] => {
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
        center={center}
        zoom={locations.length === 1 ? 12 : 5}
        scrollWheelZoom={false}
        style={{ height: "600px", width: "100%", borderRadius: "8px" }}
      >
        <RecenterMap center={center} zoom={locations.length === 1 ? 12 : 5} />
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
            <Tooltip>
              {p.Project_Name} ({p.Year})
            </Tooltip>
            <Popup>
              <strong>{p.Project_Name}</strong>
              <br />
              Year: {p.Year}
              {p.ProjectSpan && p.ProjectSpan !== String(p.Year) ? (
                <>
                  <br />
                  Duration: {p.ProjectSpan}
                </>
              ) : null}
              {p.Industry ? (
                <>
                  <br />
                  Industry: {p.Industry}
                </>
              ) : null}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      <p className="mt-2 text-xs text-muted">
        🔴 <span className="text-red-400">Timeline Year Projects</span> | 🔵{" "}
        <span className="text-blue-400">Other Years</span>
      </p>
    </div>
  );
}
