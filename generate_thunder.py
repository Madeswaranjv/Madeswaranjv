#!/usr/bin/env python3
"""
Pixel-Art Animated Thunder SVG Generator for GitHub Profile README
Author: Senior Pixel-Art & SVG Animation Engineer

Deliverables:
  - assets/hero.svg (1000x380 animated intro banner)
  - assets/bolt.svg (400x520 looping thunder icon for About Me)

Constraints:
  - Pure SVG + CSS @keyframes with steps(1, end).
  - Strict 8px pixel grid, shape-rendering="crispEdges".
  - No blur filters, no gradients. Dithered checkerboard pixel halos.
  - Grouped pixels per frame (<g>), run-length merged <rect>s.
  - File size under 300 KB.
  - GitHub README compatible (runs inside <img> tag).
"""

import os
import random
import subprocess
import sys
import xml.etree.ElementTree as ET

# ==============================================================================
# CONFIGURATION - Tweak seeds, palettes, and speeds here
# ==============================================================================

CONFIG_HERO = {
    "width": 1000,
    "height": 380,
    "pixel_size": 8,
    "grid_cols": 125,
    "grid_rows": 47,
    # 4 distinct bolt shapes (different random seeds):
    "seed_strikes": [115, 230, 345, 460],
    "speed_multiplier": 1.0,  # 1.0 = standard speed; >1.0 = faster; <1.0 = slower
    "palette": {
        "bg": "#07070a",
        "border": "#554400",
        "core": "#FFFBD0",
        "body": "#FFD500",
        "edge": "#FF9F00",
        "halo": "#FFD500",
        "flash": "#FFFBD0",
        "name": "#FFD500",
        "name_shadow": "#FF9F00",
        "sub": "#FFD500",
        "tech": "#E6EDF3",
        "quote": "#8B949E",
        "underline": "#FFD500",
    },
}

CONFIG_BOLT = {
    "width": 400,
    "height": 520,
    "pixel_size": 8,
    "grid_cols": 50,
    "grid_rows": 65,
    "seed": 888,
    "speed_multiplier": 1.0,
    "palette": {
        "bg": "#07070a",
        "border": "#554400",
        "core": "#FFFBD0",
        "body": "#FFD500",
        "edge": "#FF9F00",
        "halo": "#FFD500",
        # Palette cycling states (Core, Body, Edge cycle brighten & dim):
        "cycle_norm":   {"core": "#FFFBD0", "body": "#FFD500", "edge": "#FF9F00"},
        "cycle_bright": {"core": "#FFFFFF", "body": "#FFFBD0", "edge": "#FFD500"},
        "cycle_dim":    {"core": "#FFD500", "body": "#FF9F00", "edge": "#B86800"},
        "caption": "#FFD500",
        "caption_shadow": "#FF9F00",
    },
}

# ==============================================================================
# 5x7 BITMAP FONT
# ==============================================================================

FONT_5X7 = {
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'B': ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
    'C': ['01111', '10000', '10000', '10000', '10000', '10000', '01111'],
    'D': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'F': ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
    'G': ['01111', '10000', '10000', '10111', '10001', '10001', '01110'],
    'H': ['10001', '10001', '10001', '11111', '10001', '10001', '10001'],
    'I': ['11111', '00100', '00100', '00100', '00100', '00100', '11111'],
    'J': ['00111', '00010', '00010', '00010', '00010', '10010', '01100'],
    'K': ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
    'M': ['10001', '11011', '10101', '10001', '10001', '10001', '10001'],
    'N': ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    'P': ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
    'Q': ['01110', '10001', '10001', '10001', '10101', '10010', '01101'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'S': ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    'U': ['10001', '10001', '10001', '10001', '10001', '10001', '01110'],
    'V': ['10001', '10001', '10001', '10001', '10001', '01010', '00100'],
    'W': ['10001', '10001', '10001', '10101', '10101', '11011', '10001'],
    'X': ['10001', '10001', '01010', '00100', '01010', '10001', '10001'],
    'Y': ['10001', '10001', '01010', '00100', '00100', '00100', '00100'],
    'Z': ['11111', '00001', '00010', '00100', '01000', '10000', '11111'],
    'a': ['00000', '00000', '01110', '00001', '01111', '10001', '01111'],
    'b': ['10000', '10000', '10110', '11001', '10001', '10001', '11110'],
    'c': ['00000', '00000', '01110', '10000', '10000', '10001', '01110'],
    'd': ['00001', '00001', '01101', '10011', '10001', '10001', '01111'],
    'e': ['00000', '00000', '01110', '10001', '11111', '10000', '01110'],
    'f': ['00110', '01001', '01000', '11110', '01000', '01000', '01000'],
    'g': ['00000', '00000', '01111', '10001', '01111', '00001', '01110'],
    'h': ['10000', '10000', '10110', '11001', '10001', '10001', '10001'],
    'i': ['00100', '00000', '01100', '00100', '00100', '00100', '01110'],
    'j': ['00010', '00000', '00110', '00010', '00010', '10010', '01100'],
    'k': ['10000', '10000', '10010', '10100', '11000', '10100', '10010'],
    'l': ['01100', '00100', '00100', '00100', '00100', '00100', '00110'],
    'm': ['00000', '00000', '11010', '10101', '10101', '10101', '10101'],
    'n': ['00000', '00000', '10110', '11001', '10001', '10001', '10001'],
    'o': ['00000', '00000', '01110', '10001', '10001', '10001', '01110'],
    'p': ['00000', '00000', '11110', '10001', '11110', '10000', '10000'],
    'q': ['00000', '00000', '01111', '10001', '01111', '00001', '00001'],
    'r': ['00000', '00000', '10110', '11001', '10000', '10000', '10000'],
    's': ['00000', '00000', '01111', '10000', '01110', '00001', '11110'],
    't': ['00100', '00100', '01110', '00100', '00100', '00100', '00010'],
    'u': ['00000', '00000', '10001', '10001', '10001', '10011', '01101'],
    'v': ['00000', '00000', '10001', '10001', '10001', '01010', '00100'],
    'w': ['00000', '00000', '10001', '10001', '10101', '10101', '01010'],
    'x': ['00000', '00000', '10001', '01010', '00100', '01010', '10001'],
    'y': ['00000', '00000', '10001', '10001', '01111', '00001', '01110'],
    'z': ['00000', '00000', '11111', '00010', '00100', '01000', '11111'],
    '0': ['01110', '10001', '10011', '10101', '11001', '10001', '01110'],
    '1': ['00100', '01100', '00100', '00100', '00100', '00100', '01110'],
    '2': ['01110', '10001', '00001', '00010', '00100', '01000', '11111'],
    '3': ['11110', '00001', '00001', '01110', '00001', '00001', '11110'],
    '4': ['00010', '00110', '01010', '10010', '11111', '00010', '00010'],
    '5': ['11111', '10000', '11110', '00001', '00001', '10001', '01110'],
    '6': ['01110', '10000', '11110', '10001', '10001', '10001', '01110'],
    '7': ['11111', '00001', '00010', '00100', '01000', '01000', '01000'],
    '8': ['01110', '10001', '10001', '01110', '10001', '10001', '01110'],
    '9': ['01110', '10001', '10001', '01111', '00001', '00001', '01110'],
    ' ': ['00000', '00000', '00000', '00000', '00000', '00000', '00000'],
    '.': ['00000', '00000', '00000', '00000', '00000', '01100', '01100'],
    '|': ['00100', '00100', '00100', '00100', '00100', '00100', '00100'],
    '-': ['00000', '00000', '00000', '11111', '00000', '00000', '00000'],
    '!': ['00100', '00100', '00100', '00100', '00000', '00100', '00100'],
}

def get_glyph_matrix(ch):
    if ch in FONT_5X7:
        return FONT_5X7[ch]
    ch_up = ch.upper()
    if ch_up in FONT_5X7:
        return FONT_5X7[ch_up]
    return FONT_5X7[' ']

def measure_text_width(text, scale, tracking=1):
    w = 0
    for ch in text:
        if ch == ' ':
            w += (3 + tracking) * scale
        elif ch == '|':
            w += (1 + tracking) * scale
        elif ch == '.':
            w += (2 + tracking) * scale
        else:
            w += (5 + tracking) * scale
    return w

def render_font_rects(text, start_x, start_y, scale, tracking=1):
    curr_x = start_x
    char_rects_list = []
    for ch in text:
        ch_rects = []
        glyph = get_glyph_matrix(ch)
        g_w = 1 if ch == '|' else (2 if ch == '.' else (3 if ch == ' ' else 5))
        for r_idx, row in enumerate(glyph):
            run_start = None
            run_len = 0
            for c_idx, bit in enumerate(row):
                if bit == '1':
                    if run_start is None:
                        run_start = c_idx
                        run_len = 1
                    else:
                        run_len += 1
                else:
                    if run_start is not None:
                        ch_rects.append((curr_x + run_start * scale, start_y + r_idx * scale, run_len * scale, scale))
                        run_start = None
                        run_len = 0
            if run_start is not None:
                ch_rects.append((curr_x + run_start * scale, start_y + r_idx * scale, run_len * scale, scale))
        char_rects_list.append(ch_rects)
        curr_x += (g_w + tracking) * scale
    return char_rects_list

def merge_grid_to_rects(pixel_set, px_size=8, x_offset=0, y_offset=0):
    if not pixel_set:
        return []
    rows = {}
    for c, r in pixel_set:
        rows.setdefault(r, []).append(c)

    rects = []
    for r in sorted(rows.keys()):
        cols = sorted(rows[r])
        start_c = cols[0]
        length = 1
        for i in range(1, len(cols)):
            if cols[i] == cols[i - 1] + 1:
                length += 1
            else:
                rects.append((x_offset + start_c * px_size, y_offset + r * px_size, length * px_size, px_size))
                start_c = cols[i]
                length = 1
        rects.append((x_offset + start_c * px_size, y_offset + r * px_size, length * px_size, px_size))
    return rects

def rects_to_xml(rects):
    return "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>' for x, y, w, h in rects)

# ==============================================================================
# RECURSIVE THUNDER GENERATOR
# ==============================================================================

class BoltGenerator:
    def __init__(self, seed, max_cols=125, max_rows=47, px_size=8):
        self.seed = seed
        self.max_cols = max_cols
        self.max_rows = max_rows
        self.px_size = px_size
        self.rng = random.Random(seed)

    def generate(self, start_col, max_row_reach, num_branches=4, is_major=False):
        """
        Generates realistic branched lightning tree:
        - 1 main trunk drifting 1-3 px per step with sharp 45-deg and 90-deg kinks.
        - 3 to 5 secondary branches splitting at 30-60 deg.
        - Tertiary twigs (2-6 px long).
        - If is_major is True, branches spread widely across both sides of the banner.
        """
        trunk = []
        c = start_col
        r = 0
        trunk.append((c, r))

        fork_rows = sorted(self.rng.sample(
            range(3, max(4, int(max_row_reach * 0.85))),
            min(num_branches, max_row_reach // 3)
        ))
        branches = []

        while r < max_row_reach:
            kink = self.rng.random()
            if kink < 0.22:
                # 90-degree horizontal kink
                direction = self.rng.choice([-1, 1])
                kink_steps = self.rng.randint(2, 3)
                for _ in range(kink_steps):
                    c = max(3, min(self.max_cols - 4, c + direction))
                    trunk.append((c, r))
                r = min(max_row_reach, r + 1)
                trunk.append((c, r))
            elif kink < 0.48:
                # 45-degree diagonal step
                direction = self.rng.choice([-1, 1])
                c = max(3, min(self.max_cols - 4, c + direction))
                r = min(max_row_reach, r + 1)
                trunk.append((c, r))
            else:
                # Vertical step
                step_r = self.rng.choice([1, 1, 2])
                c = max(3, min(self.max_cols - 4, c + self.rng.choice([-1, 0, 1])))
                r = min(max_row_reach, r + step_r)
                trunk.append((c, r))

            # Branch forking
            for f_r in fork_rows:
                if r >= f_r and not any(b['fork_r'] == f_r for b in branches):
                    # For major strike, alternate branches to spread across both left and right
                    if is_major:
                        b_dir = -1 if len(branches) % 2 == 0 else 1
                        b_len = self.rng.randint(32, 48)
                    else:
                        b_dir = self.rng.choice([-1, 1])
                        b_len = self.rng.randint(14, 24)

                    b_path = []
                    bc, br = c, r
                    twigs = []
                    for _ in range(b_len):
                        # Wide horizontal reach for major banner strike
                        if is_major:
                            bc += b_dir * self.rng.choice([1, 2, 2, 3])
                            br += self.rng.choice([0, 1, 1])
                        else:
                            bc += b_dir * self.rng.choice([1, 1, 2])
                            br += self.rng.choice([1, 1, 2])
                        bc = max(2, min(self.max_cols - 3, bc))
                        br = max(1, min(self.max_rows - 2, br))
                        b_path.append((bc, br))

                        # Tertiary twigs (2 to 6 px long)
                        if self.rng.random() < 0.28 and len(b_path) > 3:
                            twig = []
                            tc, tr = bc, br
                            t_len = self.rng.randint(2, 6)
                            tdir = b_dir if self.rng.random() < 0.6 else -b_dir
                            for _ in range(t_len):
                                tc += tdir * self.rng.choice([1, 2])
                                tr += self.rng.choice([0, 1])
                                if 0 <= tc < self.max_cols and 0 <= tr < self.max_rows:
                                    twig.append((tc, tr))
                            if twig:
                                twigs.append(twig)
                    branches.append({'fork_r': f_r, 'path': b_path, 'twigs': twigs})

        return trunk, branches

    def rasterize_layers(self, trunk, branches):
        core_pixels = set()
        body_pixels = set()

        # Trunk: center Core line, flanked by 1px Body on each side (width 3)
        for i, (cc, cr) in enumerate(trunk):
            core_pixels.add((cc, cr))
            body_pixels.add((cc - 1, cr))
            body_pixels.add((cc + 1, cr))

        # Secondary branches: width 2
        for b in branches:
            for i, (bc, br) in enumerate(b['path']):
                if i < 4:
                    core_pixels.add((bc, br))
                else:
                    body_pixels.add((bc, br))
                body_pixels.add((bc + 1, br))
            for twig in b['twigs']:
                for tc, tr in twig:
                    body_pixels.add((tc, tr))

        core_pixels = {(c, r) for c, r in core_pixels if 0 <= c < self.max_cols and 0 <= r < self.max_rows}
        body_pixels = {(c, r) for c, r in body_pixels if 0 <= c < self.max_cols and 0 <= r < self.max_rows and (c, r) not in core_pixels}

        occupied = core_pixels | body_pixels

        # Edge outline: 1-pixel boundary
        edge_pixels = set()
        for oc, or_ in occupied:
            for dc in [-1, 0, 1]:
                for dr in [-1, 0, 1]:
                    nc, nr = oc + dc, or_ + dr
                    if 0 <= nc < self.max_cols and 0 <= nr < self.max_rows:
                        if (nc, nr) not in occupied:
                            edge_pixels.add((nc, nr))

        # Dither halo (checkerboard (c + r) % 2 == 0)
        halo_pixels = set()
        all_bolt = occupied | edge_pixels
        for ec, er in edge_pixels:
            for dc in [-1, 0, 1]:
                for dr in [-1, 0, 1]:
                    hc, hr = ec + dc, er + dr
                    if 0 <= hc < self.max_cols and 0 <= hr < self.max_rows:
                        if (hc, hr) not in all_bolt and (hc + hr) % 2 == 0:
                            halo_pixels.add((hc, hr))

        return core_pixels, body_pixels, edge_pixels, halo_pixels

    def get_segments(self, trunk, branches, num_segments=4):
        max_r = max(r for c, r in trunk)
        segments = []
        for s in range(num_segments):
            r_start = int((s / num_segments) * max_r)
            r_end = int(((s + 1) / num_segments) * max_r)
            sub_trunk = [(c, r) for c, r in trunk if r_start <= r <= r_end]
            sub_branches = []
            for b in branches:
                sub_path = [(c, r) for c, r in b['path'] if r_start <= r <= r_end]
                sub_twigs = [[(c, r) for c, r in tw if r_start <= r <= r_end] for tw in b['twigs']]
                if sub_path or sub_twigs:
                    sub_branches.append({'fork_r': b['fork_r'], 'path': sub_path, 'twigs': sub_twigs})
            segments.append(self.rasterize_layers(sub_trunk, sub_branches))
        return segments

# ==============================================================================
# SVG BUILDERS
# ==============================================================================

def build_hero_svg(config=CONFIG_HERO):
    w = config["width"]
    h = config["height"]
    px = config["pixel_size"]
    cols = config["grid_cols"]
    rows = config["grid_rows"]
    pal = config["palette"]
    seeds = config["seed_strikes"]

    # 1. Generate 4 distinct bolts
    # Bolt 1: Left (reaches row 22, seeds[0])
    gen1 = BoltGenerator(seeds[0], cols, rows, px)
    t1, b1 = gen1.generate(start_col=32, max_row_reach=22, num_branches=3)
    s1_segs = gen1.get_segments(t1, b1, num_segments=4)
    s1_full = gen1.rasterize_layers(t1, b1)

    # Bolt 2: Right (reaches row 22, seeds[1])
    gen2 = BoltGenerator(seeds[1], cols, rows, px)
    t2, b2 = gen2.generate(start_col=92, max_row_reach=22, num_branches=3)
    s2_segs = gen2.get_segments(t2, b2, num_segments=4)
    s2_full = gen2.rasterize_layers(t2, b2)

    # Bolt 3: Mid-Left (reaches row 23, seeds[2])
    gen3 = BoltGenerator(seeds[2], cols, rows, px)
    t3, b3 = gen3.generate(start_col=46, max_row_reach=23, num_branches=4)
    s3_segs = gen3.get_segments(t3, b3, num_segments=4)
    s3_full = gen3.rasterize_layers(t3, b3)

    # Bolt 4: Master Center Strike (reaches row 21, right above name, branches spread wide across banner)
    gen4 = BoltGenerator(seeds[3], cols, rows, px)
    t4, b4 = gen4.generate(start_col=62, max_row_reach=21, num_branches=6, is_major=True)
    s4_segs = gen4.get_segments(t4, b4, num_segments=4)
    s4_full = gen4.rasterize_layers(t4, b4)

    # 2. Typography
    name_str = "MADESWARAN J V"
    name_w = measure_text_width(name_str, scale=8, tracking=1)
    # Dead center on 8px grid
    name_start_x = (((w - name_w) // 2) // px) * px
    name_start_y = 168  # Row 21 (multiple of 8)
    name_char_rects = render_font_rects(name_str, name_start_x, name_start_y, scale=8, tracking=1)

    all_name_rects = [r for cr in name_char_rects for r in cr]
    name_shadow_rects = [(rx + px, ry + px, rw, rh) for rx, ry, rw, rh in all_name_rects]

    # Underline
    uline_rects = [(x, 232, px, px) for x in range(name_start_x, name_start_x + name_w, px)]

    # Subtitles (all perfectly centered)
    dev_str = "FULL STACK DEVELOPER"
    dev_w = measure_text_width(dev_str, scale=4, tracking=1)
    dev_start_x = (w - dev_w) // 2
    dev_start_y = 256
    dev_rects = [r for cr in render_font_rects(dev_str, dev_start_x, dev_start_y, scale=4, tracking=1) for r in cr]

    tech_str = "React | Next.js | Node.js | MongoDB | AWS"
    tech_w = measure_text_width(tech_str, scale=4, tracking=1)
    tech_start_x = (w - tech_w) // 2
    tech_start_y = 292
    tech_rects = [r for cr in render_font_rects(tech_str, tech_start_x, tech_start_y, scale=4, tracking=1) for r in cr]

    quote_str = "Push past the limit. Ship. Repeat."
    quote_w = measure_text_width(quote_str, scale=4, tracking=1)
    quote_start_x = (w - quote_w) // 2
    quote_start_y = 332
    quote_rects = [r for cr in render_font_rects(quote_str, quote_start_x, quote_start_y, scale=4, tracking=1) for r in cr]

    def layers_to_xml(core, body, edge, halo):
        parts = []
        r_h = merge_grid_to_rects(halo, px)
        r_e = merge_grid_to_rects(edge, px)
        r_b = merge_grid_to_rects(body, px)
        r_c = merge_grid_to_rects(core, px)
        if r_h:
            parts.append(f'<g fill="{pal["halo"]}" opacity="0.33">{rects_to_xml(r_h)}</g>')
        if r_e:
            parts.append(f'<g fill="{pal["edge"]}">{rects_to_xml(r_e)}</g>')
        if r_b:
            parts.append(f'<g fill="{pal["body"]}">{rects_to_xml(r_b)}</g>')
        if r_c:
            parts.append(f'<g fill="{pal["core"]}">{rects_to_xml(r_c)}</g>')
        return "".join(parts)

    css = f"""
    .hide {{ opacity: 0; }}

    /* Screen shake: 8px discrete jumps on strike impacts */
    @keyframes shake {{
      0%, 8.2% {{ transform: translate(0, 0); }}
      8.3% {{ transform: translate(8px, 0); }}
      8.8% {{ transform: translate(-8px, 0); }}
      9.3% {{ transform: translate(0, 0); }}
      13.5% {{ transform: translate(-8px, 0); }}
      14.0% {{ transform: translate(8px, 0); }}
      14.5% {{ transform: translate(0, 0); }}
      18.0% {{ transform: translate(8px, 0); }}
      18.5% {{ transform: translate(-8px, 0); }}
      19.0% {{ transform: translate(0, 0); }}
      25.5% {{ transform: translate(8px, 0); }}
      26.0% {{ transform: translate(-8px, 0); }}
      26.5% {{ transform: translate(8px, 0); }}
      27.0%, 100% {{ transform: translate(0, 0); }}
    }}
    .shake-layer {{ animation: shake 6.0s steps(1) 0s forwards; }}

    /* Full-screen strike flash */
    @keyframes screenFlash {{
      0%, 8.2% {{ opacity: 0; }}
      8.3%, 8.8% {{ opacity: 0.85; }}
      8.9%, 13.4% {{ opacity: 0; }}
      13.5%, 14.0% {{ opacity: 0.85; }}
      14.1%, 17.9% {{ opacity: 0; }}
      18.0%, 18.5% {{ opacity: 0.85; }}
      18.6%, 25.4% {{ opacity: 0; }}
      25.5%, 26.2% {{ opacity: 0.95; }}
      26.3%, 100% {{ opacity: 0; }}
    }}
    .screen-flash {{ animation: screenFlash 6.0s steps(1) 0s forwards; }}

    /* Ambient Sparks (0.0s to 0.4s) */
    @keyframes topSparks {{
      0% {{ opacity: 0; }}
      1.5%, 3.0% {{ opacity: 0.8; }}
      3.1%, 4.5% {{ opacity: 0.2; }}
      4.6%, 6.5% {{ opacity: 1.0; }}
      6.6%, 100% {{ opacity: 0; }}
    }}
    .top-sparks {{ animation: topSparks 6.0s steps(1) 0s forwards; }}

    /* Strike 1: Left (0.40s to 0.68s -> 6.7% to 11.3%) */
    @keyframes s1_step0 {{ 6.7%, 10.3% {{ opacity: 1; }} 10.4%, 100% {{ opacity: 0; }} }}
    @keyframes s1_step1 {{ 7.4%, 10.3% {{ opacity: 1; }} 10.4%, 100% {{ opacity: 0; }} }}
    @keyframes s1_step2 {{ 8.1%, 10.3% {{ opacity: 1; }} 10.4%, 100% {{ opacity: 0; }} }}
    @keyframes s1_step3 {{ 8.8%, 9.6% {{ opacity: 1; }} 9.7%, 10.3% {{ opacity: 0.5; }} 10.4%, 100% {{ opacity: 0; }} }}
    @keyframes s1_fade  {{ 10.4%, 11.3% {{ opacity: 0.3; }} 11.4%, 100% {{ opacity: 0; }} }}
    .s1-0 {{ animation: s1_step0 6.0s steps(1) 0s forwards; }}
    .s1-1 {{ animation: s1_step1 6.0s steps(1) 0s forwards; }}
    .s1-2 {{ animation: s1_step2 6.0s steps(1) 0s forwards; }}
    .s1-3 {{ animation: s1_step3 6.0s steps(1) 0s forwards; }}
    .s1-fade {{ animation: s1_fade 6.0s steps(1) 0s forwards; }}

    /* Strike 2: Right (0.70s to 0.98s -> 11.7% to 16.3%) */
    @keyframes s2_step0 {{ 11.7%, 15.3% {{ opacity: 1; }} 15.4%, 100% {{ opacity: 0; }} }}
    @keyframes s2_step1 {{ 12.4%, 15.3% {{ opacity: 1; }} 15.4%, 100% {{ opacity: 0; }} }}
    @keyframes s2_step2 {{ 13.1%, 15.3% {{ opacity: 1; }} 15.4%, 100% {{ opacity: 0; }} }}
    @keyframes s2_step3 {{ 13.8%, 14.6% {{ opacity: 1; }} 14.7%, 15.3% {{ opacity: 0.5; }} 15.4%, 100% {{ opacity: 0; }} }}
    @keyframes s2_fade  {{ 15.4%, 16.3% {{ opacity: 0.3; }} 16.4%, 100% {{ opacity: 0; }} }}
    .s2-0 {{ animation: s2_step0 6.0s steps(1) 0s forwards; }}
    .s2-1 {{ animation: s2_step1 6.0s steps(1) 0s forwards; }}
    .s2-2 {{ animation: s2_step2 6.0s steps(1) 0s forwards; }}
    .s2-3 {{ animation: s2_step3 6.0s steps(1) 0s forwards; }}
    .s2-fade {{ animation: s2_fade 6.0s steps(1) 0s forwards; }}

    /* Strike 3: Mid-Left (1.00s to 1.28s -> 16.7% to 21.3%) */
    @keyframes s3_step0 {{ 16.7%, 20.3% {{ opacity: 1; }} 20.4%, 100% {{ opacity: 0; }} }}
    @keyframes s3_step1 {{ 17.4%, 20.3% {{ opacity: 1; }} 20.4%, 100% {{ opacity: 0; }} }}
    @keyframes s3_step2 {{ 18.1%, 20.3% {{ opacity: 1; }} 20.4%, 100% {{ opacity: 0; }} }}
    @keyframes s3_step3 {{ 18.8%, 19.6% {{ opacity: 1; }} 19.7%, 20.3% {{ opacity: 0.5; }} 20.4%, 100% {{ opacity: 0; }} }}
    @keyframes s3_fade  {{ 20.4%, 21.3% {{ opacity: 0.3; }} 21.4%, 100% {{ opacity: 0; }} }}
    .s3-0 {{ animation: s3_step0 6.0s steps(1) 0s forwards; }}
    .s3-1 {{ animation: s3_step1 6.0s steps(1) 0s forwards; }}
    .s3-2 {{ animation: s3_step2 6.0s steps(1) 0s forwards; }}
    .s3-3 {{ animation: s3_step3 6.0s steps(1) 0s forwards; }}
    .s3-fade {{ animation: s3_fade 6.0s steps(1) 0s forwards; }}

    /* Strike 4: Master Bolt Center (1.40s to 2.20s -> 23.3% to 36.7%) */
    @keyframes s4_step0 {{ 23.3%, 31.5% {{ opacity: 1; }} 31.6%, 100% {{ opacity: 0; }} }}
    @keyframes s4_step1 {{ 24.0%, 31.5% {{ opacity: 1; }} 31.6%, 100% {{ opacity: 0; }} }}
    @keyframes s4_step2 {{ 24.7%, 31.5% {{ opacity: 1; }} 31.6%, 100% {{ opacity: 0; }} }}
    @keyframes s4_step3 {{ 25.4%, 28.5% {{ opacity: 1; }} 28.6%, 31.5% {{ opacity: 0.6; }} 31.6%, 100% {{ opacity: 0; }} }}
    @keyframes s4_fade  {{ 31.6%, 36.7% {{ opacity: 0.25; }} 36.8%, 100% {{ opacity: 0; }} }}
    .s4-0 {{ animation: s4_step0 6.0s steps(1) 0s forwards; }}
    .s4-1 {{ animation: s4_step1 6.0s steps(1) 0s forwards; }}
    .s4-2 {{ animation: s4_step2 6.0s steps(1) 0s forwards; }}
    .s4-3 {{ animation: s4_step3 6.0s steps(1) 0s forwards; }}
    .s4-fade {{ animation: s4_fade 6.0s steps(1) 0s forwards; }}

    /* Permanent Typography Layer */
    @keyframes nameShadowShow {{ 0%, 48.0% {{ opacity: 0; }} 48.1%, 100% {{ opacity: 1; }} }}
    .name-shadow {{ animation: nameShadowShow 6.0s steps(1) 0s forwards; }}

    @keyframes ulineShow {{ 0%, 50.0% {{ opacity: 0; }} 50.1%, 100% {{ opacity: 1; }} }}
    .uline {{ animation: ulineShow 6.0s steps(1) 0s forwards; }}

    @keyframes devShow {{ 0%, 52.0% {{ opacity: 0; }} 52.1%, 100% {{ opacity: 1; }} }}
    .sub-dev {{ animation: devShow 6.0s steps(1) 0s forwards; }}

    @keyframes techShow {{ 0%, 55.0% {{ opacity: 0; }} 55.1%, 100% {{ opacity: 1; }} }}
    .sub-tech {{ animation: techShow 6.0s steps(1) 0s forwards; }}

    @keyframes quoteShow {{ 0%, 58.0% {{ opacity: 0; }} 58.1%, 100% {{ opacity: 1; }} }}
    .sub-quote {{ animation: quoteShow 6.0s steps(1) 0s forwards; }}

    /* Idle loops after intro (loops forever) */
    @keyframes idleCrawl {{
      0%, 70% {{ opacity: 0; }}
      72%, 76% {{ opacity: 1; transform: translate(0, 0); }}
      77%, 81% {{ opacity: 1; transform: translate(32px, 0); }}
      82%, 86% {{ opacity: 1; transform: translate(80px, 0); }}
      87%, 91% {{ opacity: 1; transform: translate(140px, 0); }}
      92%, 100% {{ opacity: 0; }}
    }}
    .idle-spark {{ animation: idleCrawl 5.5s steps(1) 4.2s infinite; }}

    @keyframes idleEdgeFlash1 {{
      0%, 82% {{ opacity: 0; }}
      83%, 85% {{ opacity: 1; }}
      86%, 88% {{ opacity: 0.4; }}
      89%, 100% {{ opacity: 0; }}
    }}
    .idle-edge1 {{ animation: idleEdgeFlash1 6.5s steps(1) 4.5s infinite; }}

    @keyframes idleEdgeFlash2 {{
      0%, 75% {{ opacity: 0; }}
      76%, 78% {{ opacity: 1; }}
      79%, 81% {{ opacity: 0.3; }}
      82%, 100% {{ opacity: 0; }}
    }}
    .idle-edge2 {{ animation: idleEdgeFlash2 5.0s steps(1) 4.8s infinite; }}
    """

    name_letter_svg_groups = []
    base_t_pct = 36.7
    step_t_pct = 0.83

    for idx, cr in enumerate(name_char_rects):
        flash_start = base_t_pct + (idx * step_t_pct)
        flash_end = flash_start + step_t_pct
        perm_start = flash_end

        kf_flash_name = f"letFlash_{idx}"
        kf_perm_name = f"letPerm_{idx}"

        css += f"""
        @keyframes {kf_flash_name} {{
          0%, {flash_start:.2f}% {{ opacity: 0; }}
          {flash_start + 0.01:.2f}%, {flash_end:.2f}% {{ opacity: 1; }}
          {flash_end + 0.01:.2f}%, 100% {{ opacity: 0; }}
        }}
        @keyframes {kf_perm_name} {{
          0%, {perm_start:.2f}% {{ opacity: 0; }}
          {perm_start + 0.01:.2f}%, 100% {{ opacity: 1; }}
        }}
        .lf-{idx} {{ animation: {kf_flash_name} 6.0s steps(1) 0s forwards; }}
        .lp-{idx} {{ animation: {kf_perm_name} 6.0s steps(1) 0s forwards; }}
        """

        xml_rects = rects_to_xml(cr)
        name_letter_svg_groups.append(f'<g class="hide lf-{idx}" fill="{pal["flash"]}">{xml_rects}</g>')
        name_letter_svg_groups.append(f'<g class="hide lp-{idx}" fill="{pal["name"]}">{xml_rects}</g>')

    top_sparks_xml = rects_to_xml(merge_grid_to_rects({(32, 1), (33, 2), (48, 0), (62, 1), (92, 2)}, px))
    name_shadow_xml = rects_to_xml(name_shadow_rects)
    uline_xml = rects_to_xml(uline_rects)
    dev_xml = rects_to_xml(dev_rects)
    tech_xml = rects_to_xml(tech_rects)
    quote_xml = rects_to_xml(quote_rects)

    idle_spark_xml = rects_to_xml([(name_start_x + 8, name_start_y - 8, 8, 8), (name_start_x + 16, name_start_y - 8, 8, 8)])
    edge1_xml = rects_to_xml(merge_grid_to_rects({(6, 4), (7, 5), (7, 6), (8, 7), (9, 8)}, px))
    edge2_xml = rects_to_xml(merge_grid_to_rects({(116, 5), (117, 6), (116, 7), (118, 8)}, px))

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" shape-rendering="crispEdges" role="img" aria-label="Madeswaran J V - Full Stack Developer">
  <defs>
    <!-- Crisp 16-bit arcade pixel aesthetics -->
  </defs>

  <style>
{css}
  </style>

  <!-- Background Canvas -->
  <rect width="{w}" height="{h}" fill="{pal['bg']}"/>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" fill="none" stroke="{pal['border']}" stroke-width="1"/>

  <!-- Screen Shake Layer -->
  <g class="shake-layer">
    <!-- Ambient Sparks (0.0s - 0.4s) -->
    <g class="hide top-sparks" fill="{pal['core']}">{top_sparks_xml}</g>

    <!-- Strike 1: Left -->
    <g class="hide s1-0">{layers_to_xml(*s1_segs[0])}</g>
    <g class="hide s1-1">{layers_to_xml(*s1_segs[1])}</g>
    <g class="hide s1-2">{layers_to_xml(*s1_segs[2])}</g>
    <g class="hide s1-3">{layers_to_xml(*s1_segs[3])}</g>
    <g class="hide s1-fade">{layers_to_xml(set(), set(), s1_full[2], s1_full[3])}</g>

    <!-- Strike 2: Right -->
    <g class="hide s2-0">{layers_to_xml(*s2_segs[0])}</g>
    <g class="hide s2-1">{layers_to_xml(*s2_segs[1])}</g>
    <g class="hide s2-2">{layers_to_xml(*s2_segs[2])}</g>
    <g class="hide s2-3">{layers_to_xml(*s2_segs[3])}</g>
    <g class="hide s2-fade">{layers_to_xml(set(), set(), s2_full[2], s2_full[3])}</g>

    <!-- Strike 3: Mid-Left -->
    <g class="hide s3-0">{layers_to_xml(*s3_segs[0])}</g>
    <g class="hide s3-1">{layers_to_xml(*s3_segs[1])}</g>
    <g class="hide s3-2">{layers_to_xml(*s3_segs[2])}</g>
    <g class="hide s3-3">{layers_to_xml(*s3_segs[3])}</g>
    <g class="hide s3-fade">{layers_to_xml(set(), set(), s3_full[2], s3_full[3])}</g>

    <!-- Strike 4: Master Bolt Center -->
    <g class="hide s4-0">{layers_to_xml(*s4_segs[0])}</g>
    <g class="hide s4-1">{layers_to_xml(*s4_segs[1])}</g>
    <g class="hide s4-2">{layers_to_xml(*s4_segs[2])}</g>
    <g class="hide s4-3">{layers_to_xml(*s4_segs[3])}</g>
    <g class="hide s4-fade">{layers_to_xml(set(), set(), s4_full[2], s4_full[3])}</g>

    <!-- Permanent Typography Layer -->
    <!-- Name Drop Shadow -->
    <g class="hide name-shadow" fill="{pal['name_shadow']}">{name_shadow_xml}</g>
    <!-- Name Characters (Letter-by-Letter Flash & Lock) -->
    {''.join(name_letter_svg_groups)}
    <!-- Underline -->
    <g class="hide uline" fill="{pal['underline']}">{uline_xml}</g>
    <!-- Developer Subtitle -->
    <g class="hide sub-dev" fill="{pal['sub']}">{dev_xml}</g>
    <!-- Tech Stack Line -->
    <g class="hide sub-tech" fill="{pal['tech']}">{tech_xml}</g>
    <!-- Quote Line -->
    <g class="hide sub-quote" fill="{pal['quote']}">{quote_xml}</g>

    <!-- Idle Animations (Crawling sparks & edge bolts) -->
    <g class="hide idle-spark" fill="{pal['core']}">{idle_spark_xml}</g>
    <g class="hide idle-edge1" fill="{pal['body']}">{edge1_xml}</g>
    <g class="hide idle-edge2" fill="{pal['body']}">{edge2_xml}</g>
  </g>

  <!-- Full-screen Strike Flash -->
  <rect class="screen-flash hide" width="{w}" height="{h}" fill="{pal['flash']}"/>
</svg>"""
    return svg_content

def build_bolt_svg(config=CONFIG_BOLT):
    w = config["width"]
    h = config["height"]
    px = config["pixel_size"]
    cols = config["grid_cols"]
    rows = config["grid_rows"]
    pal = config["palette"]

    # Iconic 16-bit arcade thunderbolt sprite (32x40 footprint centered on 50x65 grid)
    # Start at row 6, col 25
    gen = BoltGenerator(config["seed"], cols, rows, px)
    trunk, branches = gen.generate(start_col=25, max_row_reach=38, num_branches=3)
    core_set, body_set, edge_set, halo_set = gen.rasterize_layers(trunk, branches)

    r_core = merge_grid_to_rects(core_set, px)
    r_body = merge_grid_to_rects(body_set, px)
    r_edge = merge_grid_to_rects(edge_set, px)
    r_halo = merge_grid_to_rects(halo_set, px)

    # Side arcs
    gen_l = BoltGenerator(515, cols, rows, px)
    t_l, b_l = gen_l.generate(start_col=8, max_row_reach=24, num_branches=2)
    _, body_l, edge_l, _ = gen_l.rasterize_layers(t_l, b_l)
    r_arc_l = merge_grid_to_rects(body_l | edge_l, px)

    gen_r = BoltGenerator(525, cols, rows, px)
    t_r, b_r = gen_r.generate(start_col=42, max_row_reach=28, num_branches=2)
    _, body_r, edge_r, _ = gen_r.rasterize_layers(t_r, b_r)
    r_arc_r = merge_grid_to_rects(body_r | edge_r, px)

    cap_str = "PUSH PAST THE LIMIT"
    cap_w = measure_text_width(cap_str, scale=3, tracking=1)
    cap_start_x = (w - cap_w) // 2
    cap_start_y = 480
    cap_rects = [r for cr in render_font_rects(cap_str, cap_start_x, cap_start_y, scale=3, tracking=1) for r in cr]
    cap_shadow_rects = [(rx + 2, ry + 2, rw, rh) for rx, ry, rw, rh in cap_rects]

    cap_xml = rects_to_xml(cap_rects)
    cap_shadow_xml = rects_to_xml(cap_shadow_rects)

    spark_rects = [
        (120, 420, 8, 8),
        (200, 436, 8, 8),
        (280, 424, 8, 8),
        (160, 444, 8, 8),
        (240, 452, 8, 8),
    ]

    css = f"""
    .hide {{ opacity: 0; }}

    /* Palette cycling on the bolt sprite (3-frame infinite loop) */
    @keyframes palCycleCore {{
      0%, 33.3%   {{ fill: {pal['cycle_norm']['core']}; }}
      33.4%, 66.6% {{ fill: {pal['cycle_bright']['core']}; }}
      66.7%, 100%  {{ fill: {pal['cycle_dim']['core']}; }}
    }}
    @keyframes palCycleBody {{
      0%, 33.3%   {{ fill: {pal['cycle_norm']['body']}; }}
      33.4%, 66.6% {{ fill: {pal['cycle_bright']['body']}; }}
      66.7%, 100%  {{ fill: {pal['cycle_dim']['body']}; }}
    }}
    @keyframes palCycleEdge {{
      0%, 33.3%   {{ fill: {pal['cycle_norm']['edge']}; }}
      33.4%, 66.6% {{ fill: {pal['cycle_bright']['edge']}; }}
      66.7%, 100%  {{ fill: {pal['cycle_dim']['edge']}; }}
    }}
    .c-core {{ animation: palCycleCore 0.6s steps(1) infinite; }}
    .c-body {{ animation: palCycleBody 0.6s steps(1) infinite; }}
    .c-edge {{ animation: palCycleEdge 0.6s steps(1) infinite; }}

    /* Dither halo pulse */
    @keyframes haloPulse {{
      0%, 50% {{ opacity: 0.35; }}
      51%, 100% {{ opacity: 0.15; }}
    }}
    .c-halo {{ animation: haloPulse 0.6s steps(1) infinite; }}

    /* Side Arcs Flickering */
    @keyframes arcLeft {{
      0%, 75% {{ opacity: 0; }}
      76%, 79% {{ opacity: 1; }}
      80%, 82% {{ opacity: 0.3; }}
      83%, 100% {{ opacity: 0; }}
    }}
    .arc-left {{ animation: arcLeft 3.2s steps(1) infinite; }}

    @keyframes arcRight {{
      0%, 45% {{ opacity: 0; }}
      46%, 49% {{ opacity: 1; }}
      50%, 52% {{ opacity: 0.4; }}
      53%, 100% {{ opacity: 0; }}
    }}
    .arc-right {{ animation: arcRight 2.8s steps(1) infinite; }}

    /* Rising Sparks (discrete 8px jumps) */
    @keyframes floatSpark1 {{
      0%   {{ transform: translateY(0); opacity: 1; }}
      25%  {{ transform: translateY(-16px); opacity: 1; }}
      50%  {{ transform: translateY(-32px); opacity: 0.8; }}
      75%  {{ transform: translateY(-48px); opacity: 0.4; }}
      100% {{ transform: translateY(-64px); opacity: 0; }}
    }}
    @keyframes floatSpark2 {{
      0%   {{ transform: translateY(0); opacity: 0; }}
      20%  {{ transform: translateY(0); opacity: 1; }}
      40%  {{ transform: translateY(-24px); opacity: 1; }}
      70%  {{ transform: translateY(-48px); opacity: 0.7; }}
      100% {{ transform: translateY(-72px); opacity: 0; }}
    }}
    .sp1 {{ animation: floatSpark1 2.2s steps(1) infinite; }}
    .sp2 {{ animation: floatSpark2 2.7s steps(1) 0.5s infinite; }}
    .sp3 {{ animation: floatSpark1 2.5s steps(1) 1.1s infinite; }}
    .sp4 {{ animation: floatSpark2 3.0s steps(1) 1.7s infinite; }}
    """

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" shape-rendering="crispEdges" role="img" aria-label="Animated Pixel-Art Thunderbolt">
  <defs>
    <!-- 16-bit arcade pixel bolt icon -->
  </defs>

  <style>
{css}
  </style>

  <!-- Background Card -->
  <rect width="{w}" height="{h}" fill="{pal['bg']}"/>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" fill="none" stroke="{pal['border']}" stroke-width="1"/>

  <!-- Halo Layer (Dithered Checkerboard) -->
  <g class="c-halo" fill="{pal['halo']}">
    {rects_to_xml(r_halo)}
  </g>

  <!-- Electric Side Arcs -->
  <g class="hide arc-left" fill="{pal['body']}">
    {rects_to_xml(r_arc_l)}
  </g>
  <g class="hide arc-right" fill="{pal['body']}">
    {rects_to_xml(r_arc_r)}
  </g>

  <!-- Main Bolt Sprite with Palette Cycling -->
  <g class="c-edge" fill="{pal['cycle_norm']['edge']}">
    {rects_to_xml(r_edge)}
  </g>
  <g class="c-body" fill="{pal['cycle_norm']['body']}">
    {rects_to_xml(r_body)}
  </g>
  <g class="c-core" fill="{pal['cycle_norm']['core']}">
    {rects_to_xml(r_core)}
  </g>

  <!-- Rising Sparks -->
  <g fill="{pal['core']}">
    <rect class="sp1" x="{spark_rects[0][0]}" y="{spark_rects[0][1]}" width="8" height="8"/>
    <rect class="sp2" x="{spark_rects[1][0]}" y="{spark_rects[1][1]}" width="8" height="8"/>
    <rect class="sp3" x="{spark_rects[2][0]}" y="{spark_rects[2][1]}" width="8" height="8"/>
    <rect class="sp4" x="{spark_rects[3][0]}" y="{spark_rects[3][1]}" width="8" height="8"/>
    <rect class="sp1" x="{spark_rects[4][0]}" y="{spark_rects[4][1]}" width="8" height="8"/>
  </g>

  <!-- Caption -->
  <g fill="{pal['caption_shadow']}">{cap_shadow_xml}</g>
  <g fill="{pal['caption']}">{cap_xml}</g>
</svg>"""
    return svg_content

# ==============================================================================
# MAIN & VERIFICATION
# ==============================================================================

def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(repo_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # 1. Generate hero.svg
    hero_svg = build_hero_svg(CONFIG_HERO)
    hero_path = os.path.join(assets_dir, "hero.svg")
    with open(hero_path, "w", encoding="utf-8") as f:
        f.write(hero_svg)
    hero_size_kb = os.path.getsize(hero_path) / 1024
    print(f"Generated {hero_path} ({hero_size_kb:.1f} KB)")

    # 2. Generate bolt.svg
    bolt_svg = build_bolt_svg(CONFIG_BOLT)
    bolt_path = os.path.join(assets_dir, "bolt.svg")
    with open(bolt_path, "w", encoding="utf-8") as f:
        f.write(bolt_svg)
    bolt_size_kb = os.path.getsize(bolt_path) / 1024
    print(f"Generated {bolt_path} ({bolt_size_kb:.1f} KB)")

    # 3. XML Validation
    ET.fromstring(hero_svg)
    print("XML Validation [hero.svg]: PASSED (Valid XML)")
    ET.fromstring(bolt_svg)
    print("XML Validation [bolt.svg]: PASSED (Valid XML)")

    # 4. Check File Size Constraint (< 300 KB)
    assert hero_size_kb < 300, f"hero.svg is {hero_size_kb:.1f} KB (exceeds 300 KB)"
    assert bolt_size_kb < 300, f"bolt.svg is {bolt_size_kb:.1f} KB (exceeds 300 KB)"
    print("File Size Constraint (< 300 KB): PASSED for both files!")

if __name__ == "__main__":
    main()
