"use client";

interface Props {
  label: string;
  options: string[];
  selected: string[];
  onChange: (next: string[]) => void;
  emptyHint?: string;
}

export default function FilterCheckboxGroup({ label, options, selected, onChange, emptyHint }: Props) {
  if (options.length === 0) {
    return emptyHint ? <p className="text-xs text-muted">{emptyHint}</p> : null;
  }

  function toggle(option: string) {
    if (selected.includes(option)) {
      onChange(selected.filter((o) => o !== option));
    } else {
      onChange([...selected, option]);
    }
  }

  return (
    <div className="mb-4">
      <p className="mb-2 text-sm font-semibold text-white">{label}</p>
      <div className="max-h-40 space-y-1 overflow-y-auto pr-1">
        {options.map((option) => (
          <label
            key={option}
            className="flex cursor-pointer items-center gap-2 rounded px-1 py-0.5 text-sm text-gray-300 hover:bg-white/5"
          >
            <input
              type="checkbox"
              checked={selected.includes(option)}
              onChange={() => toggle(option)}
              className="h-3.5 w-3.5 accent-accent"
            />
            <span className="truncate">{option}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
