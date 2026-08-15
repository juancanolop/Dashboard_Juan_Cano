// Kept in its own module (no Node built-ins) so client components can import
// it without pulling the server-only CSV-fetching code from lib/data.ts into
// the browser bundle.
const SKILL_PALETTE = [
  "#6C5CE7",
  "#FD79A8",
  "#00B894",
  "#FDCB6E",
  "#E17055",
  "#00CEC9",
  "#A29BFE",
  "#FF7675",
  "#55A3FF",
  "#26DE81",
  "#FC5C65",
  "#45AAF2",
  "#74B9FF",
  "#00B8D4",
  "#7B68EE",
  "#FF6B6B",
];

export function skillColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) >>> 0;
  }
  return SKILL_PALETTE[hash % SKILL_PALETTE.length];
}
