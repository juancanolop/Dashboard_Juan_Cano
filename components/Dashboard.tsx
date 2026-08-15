"use client";

import { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import type { Project, FilterMode } from "@/lib/types";
import Sidebar from "./Sidebar";
import FiltersBar from "./FiltersBar";
import SkillBadges from "./SkillBadges";
import SoftwareLogos from "./SoftwareLogos";
import ProjectGallery from "./ProjectGallery";
import ProjectsTable from "./ProjectsTable";

const ProjectMap = dynamic(() => import("./ProjectMap"), {
  ssr: false,
  loading: () => <div className="h-[640px] animate-pulse rounded-lg bg-panel" />,
});

export default function Dashboard({ projects }: { projects: Project[] }) {
  const years = useMemo(
    () => Array.from(new Set(projects.map((p) => p.Year))).sort((a, b) => a - b),
    [projects]
  );
  const minYear = years[0] ?? 0;
  const maxYear = years[years.length - 1] ?? 0;

  const industries = useMemo(
    () => Array.from(new Set(projects.map((p) => p.Industry).filter(Boolean))).sort(),
    [projects]
  );
  const categories = useMemo(
    () => Array.from(new Set(projects.map((p) => p.Category).filter(Boolean))).sort(),
    [projects]
  );
  const roles = useMemo(
    () => Array.from(new Set(projects.map((p) => p.RoleClean))).sort(),
    [projects]
  );

  const [selectedYear, setSelectedYear] = useState(maxYear);
  const [filterMode, setFilterMode] = useState<FilterMode>("include");
  const [selectedYearsSidebar, setSelectedYearsSidebar] = useState<string[]>(["All"]);
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);

  const finalYears = useMemo(() => {
    const sidebarYearList = selectedYearsSidebar.includes("All")
      ? years
      : selectedYearsSidebar.filter((y) => /^\d+$/.test(y)).map(Number);
    if (filterMode === "include") {
      return Array.from(new Set([...sidebarYearList, selectedYear])).sort((a, b) => a - b);
    }
    return [...sidebarYearList].sort((a, b) => a - b);
  }, [selectedYearsSidebar, selectedYear, filterMode, years]);

  const filtered = useMemo(() => {
    return projects.filter((p) => {
      if (!finalYears.includes(p.Year)) return false;
      if (selectedIndustries.length && !selectedIndustries.includes(p.Industry)) return false;
      if (selectedCategories.length && !selectedCategories.includes(p.Category)) return false;
      if (selectedRoles.length && !selectedRoles.includes(p.RoleClean)) return false;
      return true;
    });
  }, [projects, finalYears, selectedIndustries, selectedCategories, selectedRoles]);

  const skills = useMemo(() => {
    const set = new Set<string>();
    filtered.forEach((p) => p.Skills.forEach((s) => set.add(s)));
    return Array.from(set).sort();
  }, [filtered]);

  const software = useMemo(() => {
    const set = new Set<string>();
    filtered.forEach((p) => p.Software.forEach((s) => set.add(s)));
    return Array.from(set).sort();
  }, [filtered]);

  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      <Sidebar
        years={years}
        selectedYearsSidebar={selectedYearsSidebar}
        onYearsChange={setSelectedYearsSidebar}
        industries={industries}
        selectedIndustries={selectedIndustries}
        onIndustriesChange={setSelectedIndustries}
        categories={categories}
        selectedCategories={selectedCategories}
        onCategoriesChange={setSelectedCategories}
        roles={roles}
        selectedRoles={selectedRoles}
        onRolesChange={setSelectedRoles}
      />

      <main className="flex-1 p-4 sm:p-6">
        <h1 className="mb-4 text-3xl font-bold text-white">Projects Dashboard</h1>

        <FiltersBar
          minYear={minYear}
          maxYear={maxYear}
          selectedYear={selectedYear}
          onYearChange={setSelectedYear}
          filterMode={filterMode}
          onFilterModeChange={setFilterMode}
          finalYears={finalYears}
          projectCount={filtered.length}
        />

        <div className="mb-8 grid gap-8 lg:grid-cols-2">
          <div>
            <h3 className="section-header">Project Locations</h3>
            <ProjectMap projects={filtered} highlightYear={selectedYear} />
          </div>
          <ProjectGallery projects={filtered} highlightYear={selectedYear} />
        </div>

        <div className="mb-8 grid gap-8 lg:grid-cols-2">
          <SkillBadges skills={skills} />
          <SoftwareLogos software={software} />
        </div>

        <ProjectsTable projects={filtered} highlightYear={selectedYear} />
      </main>
    </div>
  );
}
