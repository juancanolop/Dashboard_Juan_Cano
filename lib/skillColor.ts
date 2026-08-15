// Kept in its own module (no Node built-ins) so client components can import
// it without pulling the server-only CSV-fetching code from lib/data.ts into
// the browser bundle.
//
// A muted, low-saturation palette (rather than candy-bright solid fills) so
// skill chips read as professional tags instead of party confetti. Each hue
// is used as a tinted background + border with the hue itself as the text
// color, similar to tag styling in Linear/GitHub.
const SKILL_PALETTE = [
  "#5B8DEF", // blue
  "#07B9D1", // teal (matches the site accent)
  "#8B7FD6", // violet
  "#4CAF7D", // green
  "#D9A441", // amber
  "#D9738C", // rose
  "#8896AB", // slate
  "#6C7FD8", // indigo
  "#4FB8C4", // cyan
  "#D97D5C", // coral
];

export interface SkillStyle {
  color: string;
  background: string;
  border: string;
}

export function skillColor(name: string): SkillStyle {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) >>> 0;
  }
  const color = SKILL_PALETTE[hash % SKILL_PALETTE.length];
  return {
    color,
    background: `${color}1f`, // ~12% alpha fill
    border: `${color}4d`, // ~30% alpha border
  };
}
