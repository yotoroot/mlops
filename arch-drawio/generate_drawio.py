#!/usr/bin/env python3
"""
generate_drawio.py  —  Generate a draw.io block diagram from a YAML definition.

Usage:
    python generate_drawio.py diagram.yaml [output.drawio]

YAML format:
    title: "My Diagram"
    subtitle: "optional subtitle"   # optional
    layers:
      - name: "Layer Title"
        color: "#e65100"            # optional, overrides palette
        blocks:
          - text: "Block Name"
            subtext: "detail text"
"""

import sys
import uuid
import yaml
from pathlib import Path

# ── Color palette (auto-assigned per layer, cycles if more than 6 layers) ──────
PALETTE = [
    dict(accent="#e65100", bg="#fff8f3", border="#ffccaa", font="#3e2723", label="#bf360c"),
    dict(accent="#2e7d32", bg="#f3fff4", border="#a5d6a7", font="#1b2500", label="#1b5e20"),
    dict(accent="#1565c0", bg="#f3f7ff", border="#90caf9", font="#0a1929", label="#0d47a1"),
    dict(accent="#6a1b9a", bg="#f8f3ff", border="#ce93d8", font="#1a0038", label="#4a148c"),
    dict(accent="#c62828", bg="#fff8f8", border="#ffcdd2", font="#3b0000", label="#b71c1c"),
    dict(accent="#00695c", bg="#f0fffe", border="#a7dcd8", font="#002722", label="#004d40"),
]

# ── Layout constants (match variant-modern.drawio style) ───────────────────────
BLOCK_W     = 170   # block width  (px)
BLOCK_H     = 80    # block height (px)
BLOCK_GAP   = 20    # horizontal gap between blocks
LAYER_H     = 140   # height of each layer band
LAYER_GAP   = 0     # vertical gap between bands
X_BAND      = 50    # band left edge
X_PAD_L     = 18    # padding: band left edge → first block left edge
X_PAD_R     = 108   # padding: last block right edge → band right edge
Y_BAND_TOP  = 88    # y of first band


# ── XML helpers ────────────────────────────────────────────────────────────────

def xesc(s):
    """Escape a plain string for an XML attribute value."""
    return (str(s)
            .replace("&",  "&amp;")
            .replace("<",  "&lt;")
            .replace(">",  "&gt;")
            .replace("'",  "&#39;")
            .replace('"',  "&quot;"))


def block_label(text, subtext, accent):
    """Build the HTML label used inside a block cell (XML-attr-escaped)."""
    t = xesc(text)
    s = xesc(subtext)
    return (
        f"&lt;b&gt;{t}&lt;/b&gt;&lt;br/&gt;"
        f"&lt;font style=&apos;font-size:12px;&apos; "
        f"color=&apos;#555555&apos;&gt;{s}&lt;/font&gt;"
    )


def layer_label(name):
    """Bold layer name label value (XML-attr-escaped)."""
    return f"&lt;b style=&apos;font-size:13px;&apos;&gt;{xesc(name)}&lt;/b&gt;"


# ── Generator ─────────────────────────────────────────────────────────────────

def generate(yaml_path, out_path=None):
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    title    = data.get("title", "Architecture Diagram")
    subtitle = data.get("subtitle", "")
    layers   = data.get("layers", [])

    if not layers:
        sys.exit("Error: no layers defined in YAML.")

    # Band width driven by the layer with the most blocks
    max_blocks = max(len(ly.get("blocks", [])) for ly in layers)
    band_w = X_PAD_L + max_blocks * BLOCK_W + (max_blocks - 1) * BLOCK_GAP + X_PAD_R

    lines = []   # accumulated mxCell strings
    _cid  = [2]  # cell-id counter (0 and 1 are reserved root cells)

    def nid():
        i = str(_cid[0])
        _cid[0] += 1
        return i

    def vcell(cid, value, style, x, y, w, h):
        """Append a plain vertex cell."""
        lines.append(
            f'<mxCell id="{cid}" value="{value}" style="{style}" '
            f'parent="1" vertex="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
            f'</mxCell>'
        )

    # ── Title ──────────────────────────────────────────────────────────────────
    vcell(nid(), xesc(title),
          "text;html=1;strokeColor=none;fillColor=none;align=center;"
          "verticalAlign=middle;fontSize=24;fontStyle=1;fontColor=#212121;",
          X_BAND, 18, band_w, 50)

    if subtitle:
        vcell(nid(), xesc(subtitle),
              "text;html=1;strokeColor=none;fillColor=none;align=center;"
              "verticalAlign=middle;fontSize=12;fontStyle=2;fontColor=#757575;",
              X_BAND, 58, band_w, 20)

    # ── Layers ─────────────────────────────────────────────────────────────────
    y = Y_BAND_TOP
    for idx, layer in enumerate(layers):
        c = dict(PALETTE[idx % len(PALETTE)])   # copy so we can override
        if "color" in layer:
            c["accent"] = layer["color"]         # per-layer accent override

        name   = layer.get("name", f"Layer {idx + 1}")
        blocks = layer.get("blocks", [])

        # Background band
        vcell(nid(), "",
              f"rounded=1;whiteSpace=wrap;html=1;"
              f"fillColor={c['bg']};strokeColor={c['border']};arcSize=2;opacity=80;",
              X_BAND, y, band_w, LAYER_H)

        # Left accent bar
        vcell(nid(), "",
              f"rounded=0;whiteSpace=wrap;html=1;"
              f"fillColor={c['accent']};strokeColor=none;",
              X_BAND, y, 6, LAYER_H)

        # Layer label
        vcell(nid(), layer_label(name),
              f"text;html=1;strokeColor=none;fillColor=none;"
              f"align=left;fontSize=13;fontColor={c['label']};",
              X_BAND + X_PAD_L + 5, y + 5, 400, 24)

        # Blocks (vertically centered in the band)
        block_y = y + (LAYER_H - BLOCK_H) // 2
        for bi, block in enumerate(blocks):
            bx = X_BAND + X_PAD_L + bi * (BLOCK_W + BLOCK_GAP)
            vcell(nid(),
                  block_label(block.get("text", ""), block.get("subtext", ""), c["accent"]),
                  f"rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;"
                  f"strokeColor={c['accent']};shadow=1;fontSize=12;"
                  f"arcSize=8;align=center;fontColor={c['font']};",
                  bx, block_y, BLOCK_W, BLOCK_H)

        y += LAYER_H

    # ── Footer ─────────────────────────────────────────────────────────────────
    vcell(nid(), f"Generated from {Path(yaml_path).name}",
          "text;html=1;strokeColor=none;fillColor=none;"
          "align=left;fontSize=10;fontColor=#bdbdbd;",
          X_BAND, y + 20, 700, 20)

    # ── Assemble XML ───────────────────────────────────────────────────────────
    body = "\n".join(f"                {ln}" for ln in lines)
    xml = (
        f'<mxfile host="app.diagrams.net" agent="generate_drawio.py" version="24.0.0">\n'
        f'    <diagram name="{xesc(title)}" id="gen-{uuid.uuid4().hex[:8]}">\n'
        f'        <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" '
        f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        f'pageWidth="1654" pageHeight="1169" math="0" shadow="0">\n'
        f'            <root>\n'
        f'                <mxCell id="0"/>\n'
        f'                <mxCell id="1" parent="0"/>\n'
        f'{body}\n'
        f'            </root>\n'
        f'        </mxGraphModel>\n'
        f'    </diagram>\n'
        f'</mxfile>\n'
    )

    out = out_path or str(Path(yaml_path).with_suffix(".drawio"))
    Path(out).write_text(xml)

    n_blocks = sum(len(ly.get("blocks", [])) for ly in layers)
    print(f"Generated: {out}")
    print(f"  {len(layers)} layers  |  {n_blocks} blocks  |  band width: {band_w}px")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
