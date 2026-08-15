"use client";

interface Props {
  years: number[];
  selected: string[]; // "All" or stringified years
  onChange: (next: string[]) => void;
}

export default function YearFilter({ years, selected, onChange }: Props) {
  const allSelected = selected.includes("All");

  function toggleAll() {
    onChange(allSelected ? [] : ["All"]);
  }

  function toggleYear(year: number) {
    const yearStr = String(year);
    const withoutAll = selected.filter((s) => s !== "All");
    if (withoutAll.includes(yearStr)) {
      onChange(withoutAll.filter((s) => s !== yearStr));
    } else {
      onChange([...withoutAll, yearStr]);
    }
  }

  return (
    <div className="mb-4">
      <p className="mb-2 text-sm font-semibold text-white">📅 Filter by years</p>
      <div className="max-h-40 space-y-1 overflow-y-auto pr-1">
        <label className="flex cursor-pointer items-center gap-2 rounded px-1 py-0.5 text-sm font-medium text-accent hover:bg-white/5">
          <input type="checkbox" checked={allSelected} onChange={toggleAll} className="h-3.5 w-3.5 accent-accent" />
          All
        </label>
        {years.map((year) => (
          <label
            key={year}
            className="flex cursor-pointer items-center gap-2 rounded px-1 py-0.5 text-sm text-gray-300 hover:bg-white/5"
          >
            <input
              type="checkbox"
              checked={!allSelected && selected.includes(String(year))}
              onChange={() => toggleYear(year)}
              disabled={allSelected}
              className="h-3.5 w-3.5 accent-accent disabled:opacity-40"
            />
            {year}
          </label>
        ))}
      </div>
    </div>
  );
}
