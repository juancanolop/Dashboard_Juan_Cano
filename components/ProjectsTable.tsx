"use client";

import { useMemo } from "react";
import type { Project } from "@/lib/types";

interface Props {
  projects: Project[];
  highlightYear: number;
}

function isActiveInTimeline(p: Project, year: number): boolean {
  return p.OriginalYear <= year && year <= p.EndYear;
}

const COLUMNS: { key: keyof Project | "Year"; label: string }[] = [
  { key: "Project_Name", label: "Project" },
  { key: "Year", label: "Year" },
  { key: "RoleClean", label: "Role" },
  { key: "ScopeOfWork", label: "Scope of Work" },
  { key: "DurationDisplay", label: "Duration" },
  { key: "Functions", label: "Functions" },
  { key: "ClientCompany", label: "Client" },
  { key: "Country", label: "Country" },
];

export default function ProjectsTable({ projects, highlightYear }: Props) {
  const uniqueProjects = useMemo(() => {
    const sorted = [...projects].sort((a, b) => a.OriginalYear - b.OriginalYear);
    const seen = new Set<string>();
    return sorted.filter((p) => {
      if (seen.has(p.Project_Name)) return false;
      seen.add(p.Project_Name);
      return true;
    });
  }, [projects]);

  const stats = useMemo(() => {
    const activeCount = uniqueProjects.filter((p) => isActiveInTimeline(p, highlightYear)).length;
    const years = uniqueProjects.map((p) => p.OriginalYear);
    const yearRange = years.length ? `${Math.min(...years)}-${Math.max(...years)}` : "–";
    const multiYear = uniqueProjects.filter((p) => p.ProjectSpan.includes("-")).length;
    return { activeCount, yearRange, multiYear };
  }, [uniqueProjects, highlightYear]);

  if (uniqueProjects.length === 0) {
    return (
      <div>
        <h3 className="section-header">Project Details</h3>
        <p className="text-sm text-muted">No data to display with current filters.</p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="section-header">Project Details</h3>

      <div className="mb-4 overflow-x-auto rounded-md border border-border">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-panel text-white">
            <tr>
              {COLUMNS.map((col) => (
                <th key={col.key} className="whitespace-nowrap border-b border-border px-3 py-2 font-semibold">
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {uniqueProjects.map((p, idx) => (
              <tr key={p.Project_Name} className={idx % 2 === 1 ? "bg-white/[0.03]" : undefined}>
                <td className="border-b border-border/60 px-3 py-2 text-gray-200">{p.Project_Name}</td>
                <td className="border-b border-border/60 px-3 py-2 text-gray-200">
                  {isActiveInTimeline(p, highlightYear) ? "⭐ " : ""}
                  {p.OriginalYear}
                </td>
                <td className="border-b border-border/60 px-3 py-2 text-gray-200">{p.RoleClean}</td>
                <td className="border-b border-border/60 px-3 py-2 text-gray-200">{p.ScopeOfWork}</td>
                <td className="border-b border-border/60 px-3 py-2 text-gray-200">
                  {p.DurationDisplay || p.ProjectSpan}
                </td>
                <td className="max-w-xs whitespace-pre-line border-b border-border/60 px-3 py-2 text-gray-200">
                  {p.Functions}
                </td>
                <td className="border-b border-border/60 px-3 py-2 text-gray-200">{p.ClientCompany}</td>
                <td className="border-b border-border/60 px-3 py-2 text-gray-200">{p.Country}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Unique Projects" value={uniqueProjects.length} />
        <StatCard label={`Active in ${highlightYear}`} value={stats.activeCount} />
        <StatCard label="Project Year Range" value={stats.yearRange} />
        <StatCard label="Multi-Year Projects" value={stats.multiYear} />
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md border border-border bg-panel p-3">
      <p className="text-xs text-muted">{label}</p>
      <p className="text-xl font-bold text-white">{value}</p>
    </div>
  );
}
