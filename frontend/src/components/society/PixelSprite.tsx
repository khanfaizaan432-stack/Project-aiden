import { useMemo } from "react";
import type { Modality } from "../../types/society";

interface PixelSpriteProps {
  agentId: number;
  tribe: Modality;
  size?: number;
  isDead?: boolean;
  isEgg?: boolean;
}

const IMAGE_PALETTE = [
  "#2a6642",
  "#3a8a5a",
  "#00ff88",
  "#1a4a30",
  "#4aaa72",
  "#0a2a18",
];
const TEXT_PALETTE = [
  "#7a5a2c",
  "#c08a3a",
  "#f59e0b",
  "#4a3a1a",
  "#a07028",
  "#d4a050",
];
const AUDIO_PALETTE = [
  "#1e4a6e",
  "#2a6a9a",
  "#3b82f6",
  "#0e2a4e",
  "#3a7ab8",
  "#60a0d8",
];
const DEAD_PALETTE = [
  "#1a1a1a",
  "#2a2a2a",
  "#3a3a3a",
  "#0a0a0a",
  "#444",
  "#222",
];

function getPalette(
  tribe: Modality,
  isDead: boolean,
  isEgg: boolean,
): string[] {
  if (isDead) return DEAD_PALETTE;
  if (isEgg) return []; // egg uses its own colors inline
  if (tribe === "image") return IMAGE_PALETTE;
  if (tribe === "text") return TEXT_PALETTE;
  return AUDIO_PALETTE;
}

// Deterministic pseudo-random based on seed
function seededRand(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
}

// Generate an 8x8 pixel pattern based on agent id and tribe
function generatePattern(
  agentId: number,
  tribe: Modality,
  isDead: boolean,
  isEgg: boolean,
): string[] {
  const palette = getPalette(tribe, isDead, isEgg);
  const rand = seededRand(agentId * 137 + 42);
  const GRID = 8;
  const cells: string[] = [];
  const WAVE_CENTER = 4;

  if (isEgg) {
    // Simple deterministic purple oval — no noise, flat fill
    const EGG_FILL = "#6b3fa0";
    const EGG_OUTLINE = "#4a2a6e";
    for (let r = 0; r < GRID; r++) {
      for (let c = 0; c < GRID; c++) {
        const dr = (r - 3.5) / 3.5;
        const dc = (c - 3.5) / 3.5;
        const val = dr * dr * 0.7 + dc * dc;
        if (val < 0.9) {
          cells.push(EGG_FILL);
        } else if (val < 1.1) {
          cells.push(EGG_OUTLINE);
        } else {
          cells.push("transparent");
        }
      }
    }
    return cells;
  }

  if (tribe === "image") {
    // Robot-ish: symmetric head pattern
    const half: string[] = [];
    for (let r = 0; r < GRID; r++) {
      for (let c = 0; c < GRID / 2; c++) {
        const v = rand();
        half.push(
          v > 0.6
            ? palette[2]
            : v > 0.35
              ? palette[1]
              : v > 0.15
                ? palette[0]
                : "transparent",
        );
      }
    }
    for (let r = 0; r < GRID; r++) {
      for (let c = 0; c < GRID / 2; c++) {
        cells.push(half[r * 4 + c]);
      }
      for (let c = GRID / 2 - 1; c >= 0; c--) {
        cells.push(half[r * 4 + c]);
      }
    }
    // Eyes (row 2, cols 1,2 and 5,6)
    cells[2 * 8 + 1] = palette[2];
    cells[2 * 8 + 6] = palette[2];
    cells[2 * 8 + 2] = palette[4];
    cells[2 * 8 + 5] = palette[4];
  } else if (tribe === "text") {
    // Head-ish: rounded head with glyph markings
    for (let r = 0; r < GRID; r++) {
      for (let c = 0; c < GRID; c++) {
        const v = rand();
        const dr = Math.abs(r - 3.5) / 3.5;
        const dc = Math.abs(c - 3.5) / 3.5;
        const inHead = dr * dr + dc * dc < 1.2;
        if (!inHead) {
          cells.push("transparent");
        } else if (r === 2 && (c === 2 || c === 5)) {
          cells.push(palette[2]); // eyes
        } else if (r === 4 && c >= 2 && c <= 5) {
          cells.push(palette[1]); // mouth line
        } else {
          cells.push(
            v > 0.5 ? palette[0] : v > 0.25 ? palette[1] : "transparent",
          );
        }
      }
    }
  } else {
    // Audio: waveform pattern
    const waveHeights = Array.from(
      { length: GRID },
      () => Math.floor(rand() * 5) + 2,
    );
    for (let r = 0; r < GRID; r++) {
      for (let c = 0; c < GRID; c++) {
        const waveH = waveHeights[c];
        const inWave = Math.abs(r - WAVE_CENTER) <= waveH / 2;
        const v = rand();
        if (inWave) {
          cells.push(v > 0.4 ? palette[2] : v > 0.2 ? palette[1] : palette[0]);
        } else {
          cells.push("transparent");
        }
      }
    }
    // Central bright stripe
    for (let c = 0; c < GRID; c++) {
      cells[WAVE_CENTER * GRID + c] = palette[2];
    }
  }

  return cells;
}

export function PixelSprite({
  agentId,
  tribe,
  size = 64,
  isDead = false,
  isEgg = false,
}: PixelSpriteProps) {
  const cells = useMemo(
    () => generatePattern(agentId, tribe, isDead, isEgg),
    [agentId, tribe, isDead, isEgg],
  );
  const cellSize = size / 8;
  const GRID = 8;

  return (
    <div
      style={{
        width: size,
        height: size,
        display: "grid",
        gridTemplateColumns: `repeat(${GRID}, ${cellSize}px)`,
        gridTemplateRows: `repeat(${GRID}, ${cellSize}px)`,
        imageRendering: "pixelated",
        flexShrink: 0,
      }}
    >
      {cells.map((color, i) => {
        const row = Math.floor(i / GRID);
        const col = i % GRID;
        return (
          <div
            key={`cell-r${row}-c${col}`}
            style={{
              width: cellSize,
              height: cellSize,
              backgroundColor: color,
            }}
          />
        );
      })}
    </div>
  );
}
