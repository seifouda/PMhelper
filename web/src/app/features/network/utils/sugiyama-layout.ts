/**
 * Sugiyama-style layered layout engine for CPM network diagrams.
 * TypeScript port of src/pmhelper/utils/network_layout.py
 *
 * Algorithm:
 * 1. Layer assignment via topological generations (BFS kahn)
 * 2. Virtual (dummy) node insertion for edges spanning > 1 layer
 * 3. Barycenter Y-ordering with configurable passes
 * 4. Final coordinate assignment
 */

import { CPMNode, CPMEdge } from '../../../core/models/cpm-result.model';

export interface EdgePath {
  originalFrom: string;
  originalTo: string;
  isCritical: boolean;
  /** Positions of each waypoint in the path [source → virt… → target] */
  waypoints: Array<{ x: number; y: number }>;
}

export interface LayoutResult {
  nodePositions: Map<string, { x: number; y: number }>;
  edgePaths: EdgePath[];
  bounds: { minX: number; maxX: number; minY: number; maxY: number };
}

export function sugiyamaLayout(
  nodes: CPMNode[],
  edges: CPMEdge[],
  criticalActivities: string[],
  xSpacing = 180,
  ySpacing = 110,
  numPasses = 4,
): LayoutResult {
  if (nodes.length === 0) {
    return {
      nodePositions: new Map(),
      edgePaths: [],
      bounds: { minX: 0, maxX: 0, minY: 0, maxY: 0 },
    };
  }

  const criticalSet = new Set(criticalActivities);
  const nodeIds = nodes.map((n) => n.id);

  // Build adjacency lists
  const successors = new Map<string, string[]>(nodeIds.map((id) => [id, []]));
  const predecessors = new Map<string, string[]>(nodeIds.map((id) => [id, []]));
  for (const edge of edges) {
    if (successors.has(edge.from)) successors.get(edge.from)!.push(edge.to);
    if (predecessors.has(edge.to)) predecessors.get(edge.to)!.push(edge.from);
  }

  // --- Step 1: Layer assignment via topological BFS ---
  const layers = topologicalGenerations(nodeIds, successors, predecessors);
  const nodeLayer = new Map<string, number>();
  for (let i = 0; i < layers.length; i++) {
    for (const id of layers[i]) nodeLayer.set(id, i);
  }

  // --- Step 2: Virtual nodes for long edges ---
  const virtualNodes = new Set<string>();
  const edgePathMap = new Map<string, string[]>();

  // Augmented adjacency (will include virtual nodes)
  const augSucc = new Map<string, string[]>(
    nodeIds.map((id) => [id, [...(successors.get(id) ?? [])]]),
  );
  const augPred = new Map<string, string[]>(
    nodeIds.map((id) => [id, [...(predecessors.get(id) ?? [])]]),
  );

  for (const edge of edges) {
    const fromL = nodeLayer.get(edge.from) ?? 0;
    const toL = nodeLayer.get(edge.to) ?? 0;
    const span = toL - fromL;

    if (span <= 1) {
      edgePathMap.set(edgeKey(edge.from, edge.to), [edge.from, edge.to]);
      continue;
    }

    // Insert virtual nodes at intermediate layers
    const path = [edge.from];
    let prev = edge.from;
    for (let k = 1; k < span; k++) {
      const virtId = `__v_${edge.from}_${edge.to}_${k}`;
      virtualNodes.add(virtId);
      const virtLayer = fromL + k;
      // Ensure layers array is large enough
      while (layers.length <= virtLayer) layers.push([]);
      layers[virtLayer].push(virtId);
      nodeLayer.set(virtId, virtLayer);
      augSucc.set(virtId, []);
      augPred.set(virtId, [prev]);
      augSucc.get(prev)!.push(virtId);
      prev = virtId;
      path.push(virtId);
    }
    augSucc.get(prev)!.push(edge.to);
    augPred.get(edge.to)!.push(prev);

    // Remove the original long edge from augmented adjacency
    const fs = augSucc.get(edge.from);
    if (fs) {
      const idx = fs.indexOf(edge.to);
      if (idx >= 0) fs.splice(idx, 1);
    }
    const tp = augPred.get(edge.to);
    if (tp) {
      const idx = tp.indexOf(edge.from);
      if (idx >= 0) tp.splice(idx, 1);
    }

    path.push(edge.to);
    edgePathMap.set(edgeKey(edge.from, edge.to), path);
  }

  // --- Step 3: Initialize positions ---
  const pos = new Map<string, { x: number; y: number }>();
  for (let i = 0; i < layers.length; i++) {
    const layer = layers[i];
    for (let j = 0; j < layer.length; j++) {
      pos.set(layer[j], {
        x: i * xSpacing,
        y: (j - layer.length / 2 + 0.5) * ySpacing,
      });
    }
  }

  // --- Step 4: Barycenter ordering (iterative passes) ---
  for (let pass = 0; pass < numPasses; pass++) {
    const forward = pass % 2 === 0;
    const indices: number[] = forward
      ? Array.from({ length: layers.length - 1 }, (_, k) => k + 1)
      : Array.from({ length: layers.length - 1 }, (_, k) => layers.length - 2 - k);

    for (const li of indices) {
      const layer = layers[li];
      const bary = new Map<string, number>();
      for (const node of layer) {
        const neighbors = forward ? (augPred.get(node) ?? []) : (augSucc.get(node) ?? []);
        const connected = neighbors.filter((n) => pos.has(n));
        bary.set(
          node,
          connected.length > 0
            ? connected.reduce((s, n) => s + (pos.get(n)?.y ?? 0), 0) / connected.length
            : (pos.get(node)?.y ?? 0),
        );
      }
      layer.sort((a, b) => (bary.get(a) ?? 0) - (bary.get(b) ?? 0));
      for (let j = 0; j < layer.length; j++) {
        pos.set(layer[j], {
          x: li * xSpacing,
          y: (j - layer.length / 2 + 0.5) * ySpacing,
        });
      }
    }
  }

  // --- Build results ---
  const nodePositions = new Map<string, { x: number; y: number }>();
  for (const id of nodeIds) {
    const p = pos.get(id);
    if (p) nodePositions.set(id, p);
  }

  const edgePaths: EdgePath[] = [];
  for (const edge of edges) {
    const key = edgeKey(edge.from, edge.to);
    const path = edgePathMap.get(key) ?? [edge.from, edge.to];
    const waypoints = path
      .map((id) => pos.get(id))
      .filter((p): p is { x: number; y: number } => p !== undefined);
    edgePaths.push({
      originalFrom: edge.from,
      originalTo: edge.to,
      isCritical: criticalSet.has(edge.from) && criticalSet.has(edge.to),
      waypoints,
    });
  }

  // Bounds from real node positions only
  let minX = Infinity,
    maxX = -Infinity,
    minY = Infinity,
    maxY = -Infinity;
  for (const [, p] of nodePositions) {
    if (p.x < minX) minX = p.x;
    if (p.x > maxX) maxX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.y > maxY) maxY = p.y;
  }
  if (!isFinite(minX)) {
    minX = 0;
    maxX = 0;
    minY = 0;
    maxY = 0;
  }

  return { nodePositions, edgePaths, bounds: { minX, maxX, minY, maxY } };
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function edgeKey(from: string, to: string): string {
  return `${from}→${to}`;
}

function topologicalGenerations(
  ids: string[],
  successors: Map<string, string[]>,
  predecessors: Map<string, string[]>,
): string[][] {
  const inDegree = new Map<string, number>(
    ids.map((id) => [id, (predecessors.get(id) ?? []).length]),
  );
  const remaining = new Set(ids);
  const generations: string[][] = [];

  while (remaining.size > 0) {
    const gen = [...remaining].filter((id) => (inDegree.get(id) ?? 0) === 0).sort();
    if (gen.length === 0) break; // guard against cycles
    generations.push(gen);
    for (const id of gen) {
      remaining.delete(id);
      for (const succ of successors.get(id) ?? []) {
        inDegree.set(succ, (inDegree.get(succ) ?? 0) - 1);
      }
    }
  }
  return generations;
}
