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

// Widths sum to 100%. Functions gets the most room since it tends to hold
// the longest text; every other column stays close in size so no single
// row looks lopsided.
const COLUMNS: { key: string; label: string; width: string }[] = [
  { key: "Project_Name", label: "Project", width: "13%" },
  { key: "Year", label: "Year", width: "6%" },
  { key: "RoleClean", label: "Role", width: "9%" },
  { key: "ScopeOfWork", label: "Scope of Work", width: "16%" },
  { key: "DurationDisplay", label: "Duration", width: "9%" },
  { key: "Functions", label: "Functions", width: "28%" },
  { key: "ClientCompany", label: "Client", width: "12%" },
  { key: "Country", label: "Country", width: "7%" },
];

/** Long free-text cells (Scope of Work, Functions) get a capped height with
 *  their own scrollbar, so one wordy project can't blow out every row. */
function ClampCell({ children }: { children: React.ReactNode }) {
  return (
    <td className="border-b border-border/60 px-2.5 py-1.5 align-top text-xs text-gray-200">
      <div className="table-scroll max-h-14 overflow-y-auto whitespace-pre-line pr-1 leading-snug">{children}</div>
    </td>
  );
}

function Cell({ children }: { children: React.ReactNode }) {
  return (
    <td className="border-b border-border/60 px-2.5 py-1.5 align-top text-xs leading-snug text-gray-200">
      {children}
    </td>
  );
}

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
        <table className="w-full min-w-[820px] table-fixed text-left text-xs">
          <colgroup>
            {COLUMNS.map((col) => (
              <col key={col.key} style={{ width: col.width }} />
            ))}
          </colgroup>
          <thead className="bg-panel text-white">
            <tr>
              {COLUMNS.map((col) => (
                <th
                  key={col.key}
                  className="truncate border-b border-border px-2.5 py-1.5 text-xs font-semibold"
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {uniqueProjects.map((p, idx) => (
              <tr key={p.Project_Name} className={idx % 2 === 1 ? "bg-white/[0.03]" : undefined}>
                <Cell>{p.Project_Name}</Cell>
                <Cell>
                  {isActiveInTimeline(p, highlightYear) ? "⭐ " : ""}
                  {p.OriginalYear}
                </Cell>
                <Cell>{p.RoleClean}</Cell>
                <ClampCell>{p.ScopeOfWork}</ClampCell>
                <Cell>{p.DurationDisplay || p.ProjectSpan}</Cell>
                <ClampCell>{p.Functions}</ClampCell>
                <Cell>{p.ClientCompany}</Cell>
                <Cell>{p.Country}</Cell>
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
