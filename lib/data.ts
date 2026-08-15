import Papa from "papaparse";
import fs from "node:fs";
import path from "node:path";
import type { Project } from "./types";

// The "Projects" tab of the Google Sheet Juan edits directly, fetched as CSV
// via Sheets' gviz endpoint (works by sheet *name*, so it survives tabs being
// reordered). The sheet just needs "Anyone with the link can view" sharing.
// Editing it there updates the live dashboard within minutes — no redeploy.
const DATA_URL =
  "https://docs.google.com/spreadsheets/d/1Z2259jNKj_MtKDzSBX_-pvk5DKupLZ55cYfhEgmqPEI/gviz/tq?tqx=out:csv&sheet=Projects";

const ROLE_MAPPINGS: [string, string][] = [
  ["civil engineer", "Civil Engineer"],
  ["ceo", "CEO"],
  ["student", "Student"],
  ["teacher", "Teacher"],
  ["auxiliar / intern", "Auxiliar / Intern"],
  ["project manager", "Project Manager"],
  ["designer / consulter", "Designer / Consulter"],
];

function stripChars(value: string, chars: string): string {
  const set = new Set(chars.split(""));
  let start = 0;
  let end = value.length;
  while (start < end && set.has(value[start])) start++;
  while (end > start && set.has(value[end - 1])) end--;
  return value.slice(start, end);
}

function cleanRole(role: string | undefined): string {
  if (!role || !role.trim()) return "Other";
  const trimmed = role.trim();
  const lower = trimmed.toLowerCase();
  for (const [key, value] of ROLE_MAPPINGS) {
    if (lower.includes(key)) return value;
  }
  const bare = stripChars(trimmed, `"'[]() `);
  if (!bare) return "Other";
  return bare
    .toLowerCase()
    .replace(/(^|[^a-zA-Z])([a-zA-Z])/g, (_m, p1, p2) => p1 + p2.toUpperCase());
}

/** Splits list-ish cells like `["AutoCAD","ArcGIS"]` or `["GIS"]` into clean tokens. */
function parseListField(raw: string | undefined, extraStripChars = ""): string[] {
  if (!raw) return [];
  return raw
    .split(",")
    .map((piece) => stripChars(piece.trim(), `"'[]()${extraStripChars} `))
    .map((piece) => piece.split('"').join("").split("'").join(""))
    .filter(Boolean);
}

function parseSoftwareField(raw: string | undefined): string[] {
  if (!raw) return [];
  return raw
    .split(",")
    .map((piece) =>
      stripChars(piece.trim(), `"'[] `)
        .replace(/ /g, "_")
        .replace(/-/g, "_")
        .toLowerCase()
    )
    .filter(Boolean);
}

/** Extracts a 4-digit year out of values like "2/2/2014 9:00 PM" or plain "2014". */
function parseYear(raw: string | undefined): number | null {
  if (!raw) return null;
  const trimmed = raw.trim();
  if (/^\d{4}$/.test(trimmed)) return parseInt(trimmed, 10);
  const slashParts = trimmed.split("/");
  if (slashParts.length === 3) {
    const yearPart = slashParts[2].trim().split(" ")[0];
    const year = parseInt(yearPart, 10);
    if (!Number.isNaN(year)) return year;
  }
  const match = trimmed.match(/(\d{4})/);
  return match ? parseInt(match[1], 10) : null;
}

function parseNumber(raw: string | undefined): number | null {
  if (raw === undefined || raw === null || raw.trim() === "") return null;
  let normalized = raw.trim();
  // The Google Sheet's locale renders decimals with a comma (e.g. "-76,046194"
  // instead of "-76.046194") regardless of how the value was typed in.
  if (/^-?\d+,\d+$/.test(normalized)) {
    normalized = normalized.replace(",", ".");
  }
  const n = Number(normalized);
  return Number.isNaN(n) ? null : n;
}

type RawRow = Record<string, string>;

function toBaseProject(row: RawRow): Project | null {
  const year = parseYear(row["Year"]);
  if (year === null) return null;

  const role = row["Role"];
  return {
    Project_Name: (row["Project_Name"] ?? "").trim(),
    ScopeOfWork: row["Scope of work"] ?? "",
    Functions: row["Functions"] ?? "",
    Category: row["Category"] ?? "",
    Role: role ?? "",
    RoleClean: cleanRole(role),
    DurationMonths: parseNumber(row["Duration_Months"]),
    Year: year,
    OriginalYear: year,
    EndYear: year,
    ProjectSpan: String(year),
    DurationDisplay: "",
    ClientCompany: row["Client_Company"] ?? "",
    Location: row["Location"] ?? "",
    Longitud: parseNumber(row["Longitud"]),
    Latitud: parseNumber(row["Latitud"]),
    ImageLink: (row["image_link"] ?? "").trim(),
    BlogLink: row["Blog_Link"] ?? "",
    Skills: parseListField(row["Skills"]),
    Software: parseSoftwareField(row["Software"]),
    Industry: row["Industry"] ?? "",
    Country: row["Country"] ?? "",
    Feature: row["Feature"] ?? "",
  };
}

/** Mirrors the old `expand_projects_by_duration`: a project spanning several
 *  years gets one row per year so it shows up in every year it was active. */
function expandByDuration(projects: Project[]): Project[] {
  const out: Project[] = [];
  for (const project of projects) {
    const months = project.DurationMonths;
    if (months === null || months <= 0) {
      out.push(project);
      continue;
    }
    const startYear = project.Year;
    const endYear = startYear + Math.floor(months / 12);
    const spansMultipleYears = endYear > startYear;
    for (let year = startYear; year <= endYear; year++) {
      out.push({
        ...project,
        Year: year,
        OriginalYear: startYear,
        EndYear: endYear,
        ProjectSpan: spansMultipleYears ? `${startYear}-${endYear}` : String(startYear),
        DurationDisplay: spansMultipleYears
          ? `${months} months (${startYear}-${endYear})`
          : `${months} months`,
      });
    }
  }
  return out;
}

function isVisibleInDashboard(row: RawRow): boolean {
  const flag = row["show dashboard"];
  if (!flag) return true;
  return flag.trim().toLowerCase() !== "no";
}

function parseCsv(csvText: string): Project[] {
  const parsed = Papa.parse<RawRow>(csvText, {
    header: true,
    skipEmptyLines: true,
  });

  const rows = parsed.data.filter(isVisibleInDashboard);
  const projects = rows
    .map(toBaseProject)
    .filter((p): p is Project => p !== null);

  return expandByDuration(projects);
}

async function fetchRemoteCsv(): Promise<string | null> {
  try {
    const res = await fetch(DATA_URL, {
      // Re-checked every 5 minutes so editing data.csv on GitHub shows up
      // here without a redeploy.
      next: { revalidate: 300 },
    });
    if (!res.ok) return null;
    return await res.text();
  } catch {
    return null;
  }
}

function readLocalCsv(): string | null {
  try {
    const localPath = path.join(process.cwd(), "data.csv");
    return fs.readFileSync(localPath, "utf-8");
  } catch {
    return null;
  }
}

export async function getProjects(): Promise<{ projects: Project[]; source: "remote" | "local" | "empty" }> {
  const remote = await fetchRemoteCsv();
  if (remote) {
    return { projects: parseCsv(remote), source: "remote" };
  }
  const local = readLocalCsv();
  if (local) {
    return { projects: parseCsv(local), source: "local" };
  }
  return { projects: [], source: "empty" };
}

