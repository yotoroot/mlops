# arch-drawio — Draw.io Architecture Diagram Generator

## Purpose
YAML-driven generator for Cloud & AI Platform software block diagrams (GCP/AWS/On-Prem style).
No swimlane containers — all layers rendered as plain background bands with colored left accent bars.

## Files
| File | Description |
|------|-------------|
| `generate_drawio.py` | Python script: YAML → .drawio XML |
| `diagram.yaml` | Example diagram definition (Cloud AI Platform, 4 layers) |
| `diagram-generated.drawio` | Output from last generator run |
| `variant-modern.drawio` | Manually crafted reference diagram (preferred style) |

## Usage
```bash
python3 generate_drawio.py diagram.yaml [output.drawio]
```

## YAML Format
```yaml
title: "My Diagram"
subtitle: "optional subtitle"
layers:
  - name: "Layer Title"
    color: "#e65100"       # optional, overrides auto palette
    blocks:
      - text: "Block Name"
        subtext: "detail text"
```

## Layout Constants (generate_drawio.py)
| Constant | Value | Notes |
|----------|-------|-------|
| BLOCK_W | 170 | block width (px) |
| BLOCK_H | 80 | block height (px) |
| BLOCK_GAP | 20 | horizontal gap between blocks |
| LAYER_H | 140 | height of each layer band |
| LAYER_GAP | 0 | vertical gap between bands (no arrows) |

## Style Decisions
- Block fill: `#ffffff` (white), colored border, shadow, rounded corners
- Layer band: light tinted bg + 6px solid left accent bar + bold label
- Auto-palette cycles through 6 colors (orange, green, blue, purple, red, teal)
- No arrows or gaps between layers
