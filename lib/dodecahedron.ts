// Regular dodecahedron geometry (20 vertices, 30 edges), built from the
// golden ratio. Pure math, no 3D library needed — rendered as CSS 3D bars.

export type Vec3 = [number, number, number];

const PHI = (1 + Math.sqrt(5)) / 2;
const INV_PHI = 1 / PHI;

function buildVertices(): Vec3[] {
  const pts: Vec3[] = [];
  for (const sx of [-1, 1]) for (const sy of [-1, 1]) for (const sz of [-1, 1]) pts.push([sx, sy, sz]);
  for (const sy of [-1, 1]) for (const sz of [-1, 1]) pts.push([0, sy * INV_PHI, sz * PHI]);
  for (const sx of [-1, 1]) for (const sy of [-1, 1]) pts.push([sx * INV_PHI, sy * PHI, 0]);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) pts.push([sx * PHI, 0, sz * INV_PHI]);
  return pts;
}

function dist(a: Vec3, b: Vec3): number {
  return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
}

export interface Edge {
  a: Vec3;
  b: Vec3;
}

/** Vertices + the 30 shortest-distance pairs (the real edges), scaled to `size`. */
export function getDodecahedronEdges(size: number): Edge[] {
  const raw = buildVertices();
  // Raw coordinates range roughly [-PHI, PHI]; normalize so the bounding
  // radius matches `size`.
  const maxR = Math.max(...raw.map((p) => Math.hypot(...p)));
  const scale = size / maxR;
  const verts = raw.map((p): Vec3 => [p[0] * scale, p[1] * scale, p[2] * scale]);

  let minD = Infinity;
  for (let i = 0; i < verts.length; i++) {
    for (let j = i + 1; j < verts.length; j++) {
      const d = dist(verts[i], verts[j]);
      if (d < minD) minD = d;
    }
  }

  const edges: Edge[] = [];
  const eps = minD * 0.01;
  for (let i = 0; i < verts.length; i++) {
    for (let j = i + 1; j < verts.length; j++) {
      if (Math.abs(dist(verts[i], verts[j]) - minD) < eps) {
        edges.push({ a: verts[i], b: verts[j] });
      }
    }
  }
  return edges;
}
