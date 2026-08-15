export interface Project {
  Project_Name: string;
  ScopeOfWork: string;
  Functions: string;
  Category: string;
  Role: string;
  RoleClean: string;
  DurationMonths: number | null;
  /** Year this row represents after duration expansion (one row per year a multi-year project spans). */
  Year: number;
  /** The project's real start year, constant across all of its expanded rows. */
  OriginalYear: number;
  /** The project's real end year (OriginalYear + duration in years), constant across all of its expanded rows. */
  EndYear: number;
  ProjectSpan: string;
  DurationDisplay: string;
  ClientCompany: string;
  Location: string;
  Longitud: number | null;
  Latitud: number | null;
  ImageLink: string;
  BlogLink: string;
  Skills: string[];
  Software: string[];
  Industry: string;
  Country: string;
  Feature: string;
}

export type FilterMode = "include" | "sidebar-only";
