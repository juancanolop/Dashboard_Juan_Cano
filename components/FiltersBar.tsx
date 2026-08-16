"use client";

import type { FilterMode } from "@/lib/types";

interface Props {
  minYear: number;
  maxYear: number;
  selectedYear: number;
  onYearChange: (year: number) => void;
  filterMode: FilterMode;
  onFilterModeChange: (mode: FilterMode) => void;
  finalYears: number[];
  projectCount: number;
  showAllProjects: boolean;
  onShowAllProjects: () => void;
}

export default function FiltersBar({
  minYear,
  maxYear,
  selectedYear,
  onYearChange,
  filterMode,
  onFilterModeChange,
  finalYears,
  projectCount,
  showAllProjects,
  onShowAllProjects,
}: Props) {
  const yearsPreview = finalYears.slice(0, 5).join(", ") + (finalYears.length > 5 ? "…" : "");

  return (
    <div className="mb-4">
      <div className="mb-4 grid gap-6 md:grid-cols-[2fr_1fr]">
        <div>
          <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
            <label className="text-sm text-gray-300">Timeline: view projects active in a year</label>
            <button
              onClick={onShowAllProjects}
              disabled={showAllProjects}
              className="rounded-md border border-[#1557b0] bg-[#2d3436] px-3 py-1 text-xs font-medium text-white transition hover:bg-[#1557b0] disabled:cursor-default disabled:border-accent disabled:bg-accent/20 disabled:text-accent"
            >
              {showAllProjects ? "✓ Showing all projects" : "Show all projects"}
            </button>
          </div>
          <input
            type="range"
            min={minYear}
            max={maxYear}
            value={selectedYear}
            onChange={(e) => onYearChange(Number(e.target.value))}
            className="w-full accent-accent"
          />
          <div className="mt-1 flex justify-between text-xs text-muted">
            <span>{minYear}</span>
            <span className="font-semibold text-accent">{selectedYear}</span>
            <span>{maxYear}</span>
          </div>
        </div>
        <div>
          <p className="mb-1 text-sm text-gray-300">Advanced filters</p>
          <div className="space-y-1">
            {(
              [
                ["include", "Include timeline year"],
                ["sidebar-only", "Only sidebar selection"],
              ] as [FilterMode, string][]
            ).map(([value, text]) => (
              <label key={value} className="flex cursor-pointer items-center gap-2 text-sm text-gray-300">
                <input
                  type="radio"
                  name="filter-mode"
                  checked={filterMode === value}
                  onChange={() => onFilterModeChange(value)}
                  className="accent-accent"
                />
                {text}
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="mb-3 rounded-md border-l-4 border-accent bg-panel p-3">
        <strong className="text-sm text-white">🔍 Active Filter:</strong>{" "}
        {showAllProjects ? (
          <span className="text-sm text-gray-300">All {finalYears.length} years — every project</span>
        ) : (
          <span className="text-sm text-gray-300">
            Showing {finalYears.length} year(s): {yearsPreview}
          </span>
        )}
        <br />
        <small className="text-muted">
          Timeline: {selectedYear} | Mode: {filterMode === "include" ? "Include timeline year" : "Only sidebar selection"}
        </small>
      </div>

      {projectCount > 0 ? (
        <p className="mb-2 rounded-md bg-emerald-900/30 px-3 py-2 text-sm text-emerald-300">
          📊 Found <strong>{projectCount} projects</strong> matching your criteria
        </p>
      ) : (
        <p className="mb-2 rounded-md bg-amber-900/30 px-3 py-2 text-sm text-amber-300">
          ❌ No projects found with current filters. Try adjusting your selection.
        </p>
      )}
    </div>
  );
}
