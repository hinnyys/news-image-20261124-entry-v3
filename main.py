"""Front page for Tuesday 24 November 2026: six stories, one picture.

A newspaper front page, not a list. A masthead with the date, one big
lead story (NATO / Russian space weapon) with a drawn satellite scene,
then two wide stories and three narrow stories, each colour-coded so
the reader can tell them apart at a glance. Everything is drawn with
Pillow from fixed coordinates -- no network, no randomness, no clock --
so the program writes the same bytes every time it runs. Output goes
to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
"""

import os
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont

    HAVE_PIL = True
except ImportError:  # pragma: no cover
    HAVE_PIL = False

W, H = 1024, 1024
PAPER = (246, 241, 231)
NAVY = (16, 30, 51)
NAVY2 = (22, 42, 70)
GOLD = (196, 154, 27)
GOLD_LIGHT = (232, 196, 90)
WHITE = (255, 255, 255)
INK = (17, 23, 33)
BODY = (70, 79, 92)
FAINT = (148, 156, 168)
CARD = (255, 255, 255)
LINE = (222, 216, 203)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

LEAD = {
    "kicker": "01  •  SPACE  •  NATO",
    "accent": (109, 40, 217),
    "headline": "NATO Warns of Russian Space Weapon",
    "standfirst": (
        "Allies say Moscow may launch a nuclear-armed satellite "
        "next month, and NATO vows to defend its satellites."
    ),
}

WIDE = [
    {
        "kicker": "02  •  USA  •  JUSTICE",
        "accent": (185, 28, 28),
        "icon": "gavel",
        "headline": "TRUMP ORDERS FEDERAL EXECUTIONS SPED UP",
        "sub": "The president directs the Justice Department to expedite federal death sentences.",
    },
    {
        "kicker": "03  •  AI  •  COURTS",
        "accent": (14, 116, 144),
        "icon": "robot",
        "headline": "STATES SUE MUSK OVER GROK IMAGES",
        "sub": "Oregon and Virginia sue Musk's companies over sexualised images made by the Grok chatbot.",
    },
]

NARROW = [
    {
        "kicker": "04  •  UKRAINE",
        "accent": (29, 78, 216),
        "icon": "ship",
        "headline": "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA",
        "sub": "Kyiv's strike far from Europe shows the war reaching into the Mediterranean.",
    },
    {
        "kicker": "05  •  ASIA  •  SECURITY",
        "accent": (180, 83, 9),
        "icon": "jet",
        "headline": "S. KOREA SCRAMBLES JETS AS RUSSIAN PLANES ENTER ZONE",
        "sub": "Seoul sends fighters up after Russian warplanes enter its air defence zone.",
    },
    {
        "kicker": "06  •  CHINA  •  ESPIONAGE",
        "accent": (159, 18, 57),
        "icon": "scales",
        "headline": "CHINA SENTENCES OFFICIAL TO DEATH FOR SPYING",
        "sub": "Beijing hands a death sentence to an official for spying and leaking state secrets.",
    },
]


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(text, fnt, width, limit):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines[:limit]


def shrink(text, path, start, smallest, width, limit):
    size = start
    while size > smallest:
        fnt = font(path, size)
        if len(wrap(text, fnt, width, limit + 1)) <= limit:
            return fnt, wrap(text, fnt, width, limit)
        size -= 1
    fnt = font(path, smallest)
    return fnt, wrap(text, fnt, width, limit)


def pale(accent):
    # A soft tint of the accent for icon discs.
    return tuple(int(255 - (255 - c) * 0.16) for c in accent)


def draw_icon(d, kind, cx, cy, r, color):
    """Draw one simple pictogram centred at (cx, cy), radius r."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=pale(color))
    s = r * 1.15
    x, y = cx - s / 2, cy - s / 2
    if kind == "gavel":
        d.rectangle([x + s * 0.18, y + s * 0.30, x + s * 0.66, y + s * 0.52], fill=color)
        d.line([x + s * 0.58, y + s * 0.48, x + s * 0.88, y + s * 0.84], fill=color, width=4)
        d.rectangle([x + s * 0.14, y + s * 0.76, x + s * 0.54, y + s * 0.86], fill=color)
    elif kind == "robot":
        d.rounded_rectangle([x + s * 0.18, y + s * 0.22, x + s * 0.82, y + s * 0.82], radius=6, outline=color, width=3)
        d.ellipse([x + s * 0.32, y + s * 0.42, x + s * 0.44, y + s * 0.54], fill=color)
        d.ellipse([x + s * 0.56, y + s * 0.42, x + s * 0.68, y + s * 0.54], fill=color)
        d.line([x + s * 0.50, y + s * 0.22, x + s * 0.50, y + s * 0.08], fill=color, width=3)
        d.ellipse([x + s * 0.44, y + s * 0.02, x + s * 0.56, y + s * 0.14], fill=color)
        d.line([x + s * 0.36, y + s * 0.68, x + s * 0.64, y + s * 0.68], fill=color, width=3)
    elif kind == "ship":
        d.polygon([(x + s * 0.10, y + s * 0.55), (x + s * 0.90, y + s * 0.55),
                   (x + s * 0.76, y + s * 0.86), (x + s * 0.24, y + s * 0.86)], fill=color)
        d.line([x + s * 0.50, y + s * 0.55, x + s * 0.50, y + s * 0.10], fill=color, width=3)
        d.polygon([(x + s * 0.50, y + s * 0.12), (x + s * 0.82, y + s * 0.42),
                   (x + s * 0.50, y + s * 0.42)], fill=color)
    elif kind == "jet":
        d.polygon([(x + s * 0.94, y + s * 0.50), (x + s * 0.10, y + s * 0.16),
                   (x + s * 0.36, y + s * 0.50), (x + s * 0.10, y + s * 0.84)], fill=color)
    elif kind == "scales":
        d.line([x + s * 0.50, y + s * 0.10, x + s * 0.50, y + s * 0.86], fill=color, width=3)
        d.line([x + s * 0.16, y + s * 0.30, x + s * 0.84, y + s * 0.30], fill=color, width=3)
        d.polygon([(x + s * 0.06, y + s * 0.52), (x + s * 0.28, y + s * 0.52),
                   (x + s * 0.17, y + s * 0.74)], outline=color, width=2)
        d.polygon([(x + s * 0.72, y + s * 0.52), (x + s * 0.94, y + s * 0.52),
                   (x + s * 0.83, y + s * 0.74)], outline=color, width=2)
        d.line([x + s * 0.32, y + s * 0.86, x + s * 0.68, y + s * 0.86], fill=color, width=3)


def draw_space_scene(img, box):
    """Lead illustration: satellite on its orbit above the Earth.

    Drawn on its own layer and pasted through a rounded-rectangle
    mask, so the Earth disc is clipped to the panel instead of
    spilling onto the stories below it.
    """
    x0, y0, x1, y1 = box
    sw, sh = x1 - x0, y1 - y0
    scene = Image.new("RGB", (sw, sh), NAVY2)
    d = ImageDraw.Draw(scene)
    # Fixed stars -- a literal list, so the picture never changes.
    for sx, sy, r in [(24, 26, 2), (70, 60, 1), (120, 22, 2), (180, 48, 1),
                      (240, 18, 2), (300, 70, 1), (40, 110, 1), (150, 96, 2),
                      (210, 110, 1), (280, 130, 2), (90, 140, 1), (330, 40, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(220, 228, 240))
    d.ellipse([18, 46, sw - 18, 196], outline=GOLD_LIGHT, width=3)
    d.ellipse([28, sh - 52, sw - 28, sh + 128], fill=(38, 96, 178))
    d.ellipse([62, sh - 30, 130, sh + 18], fill=(52, 130, 88))
    d.ellipse([200, sh - 38, 268, sh + 8], fill=(52, 130, 88))
    d.arc([28, sh - 52, sw - 28, sh + 128], 180, 360, fill=(150, 200, 240), width=3)
    # Satellite: gold panels, pale body, purple core, dish antenna.
    cx, cy = 172, 88
    d.rectangle([cx - 58, cy - 16, cx - 20, cy + 16], fill=GOLD_LIGHT)
    d.rectangle([cx + 20, cy - 16, cx + 58, cy + 16], fill=GOLD_LIGHT)
    d.rectangle([cx - 58, cy - 16, cx - 20, cy + 16], outline=GOLD, width=2)
    d.rectangle([cx + 20, cy - 16, cx + 58, cy + 16], outline=GOLD, width=2)
    d.rectangle([cx - 20, cy - 20, cx + 20, cy + 20], fill=(226, 232, 240))
    d.rectangle([cx - 9, cy - 11, cx + 9, cy + 11], fill=(109, 40, 217))
    d.line([cx, cy - 20, cx + 28, cy - 48], fill=(226, 232, 240), width=3)
    d.ellipse([cx + 22, cy - 54, cx + 34, cy - 42], fill=(226, 232, 240))
    d.text((16, 12), "AN ORBIT UNDER THREAT", font=font(SANS_B, 13), fill=(220, 228, 240))
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw, sh], radius=12, fill=255)
    img.paste(scene, (x0, y0), mask)


def card(d, box, story, headline_size, sub_size, headline_lines, sub_lines):
    x0, y0, x1, y1 = box
    accent = story["accent"]
    d.rounded_rectangle(box, radius=12, fill=CARD)
    d.rounded_rectangle([x0, y0, x1, y0 + 7], radius=3, fill=accent)
    d.rectangle([x0, y0 + 3, x1, y0 + 7], fill=accent)
    pad = 20
    tx = x0 + pad
    draw_icon(d, story["icon"], x1 - pad - 26, y0 + 30, 26, accent)
    d.text((tx, y0 + 20), story["kicker"], font=font(SANS_B, 13), fill=accent)
    inner = (x1 - x0) - 2 * pad
    hf, hlines = shrink(story["headline"], SANS_B, headline_size, 18, inner, headline_lines)
    hy = y0 + 52
    for i, line in enumerate(hlines):
        d.text((tx, hy + i * (hf.size + 6)), line, font=hf, fill=INK)
    sf = font(SANS, sub_size)
    slines = wrap(story["sub"], sf, inner, sub_lines)
    sy = hy + len(hlines) * (hf.size + 6) + 8
    for i, line in enumerate(slines):
        d.text((tx, sy + i * (sub_size + 6)), line, font=sf, fill=BODY)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    m = 32
    # --- Masthead -------------------------------------------------------
    d.rectangle([0, 0, W, 150], fill=NAVY)
    d.text((m, 16), "THE WORLD  •  IN ONE PICTURE", font=font(SANS_B, 16), fill=GOLD_LIGHT)
    d.text((m, 44), "24 NOVEMBER 2026", font=font(SERIF_B, 62), fill=WHITE)
    d.rectangle([W - m - 168, 24, W - m, 126], outline=GOLD, width=2)
    d.text((W - m - 150, 36), "TUESDAY", font=font(SANS_B, 20), fill=WHITE)
    d.text((W - m - 150, 64), "6 STORIES", font=font(SANS_B, 20), fill=GOLD_LIGHT)
    d.text((W - m - 150, 92), "FIRST REPORTED", font=font(SANS_B, 13), fill=FAINT)
    d.text((W - m - 150, 108), "TODAY", font=font(SANS_B, 13), fill=FAINT)
    d.rectangle([0, 150, W, 154], fill=GOLD)
    # --- Ticker ---------------------------------------------------------
    d.text((m, 164), "SIX STORIES FROM AROUND THE WORLD  —  IN ONE PICTURE",
           font=font(SANS_B, 14), fill=NAVY)
    d.text((W - m - 118, 164), "NO. 24-11-26", font=font(SANS_B, 14), fill=BODY)
    # --- Lead story -----------------------------------------------------
    # No extra line under the standfirst this time: the previous
    # version's footer line collided with the standfirst's last line.
    hx0, hy0, hx1, hy1 = m, 192, W - m, 470
    d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=14, fill=CARD)
    d.rectangle([hx0, hy0, hx0 + 8, hy1], fill=LEAD["accent"])
    tx = hx0 + 28
    d.rounded_rectangle([tx, hy0 + 20, tx + 116, hy0 + 46], radius=13, fill=LEAD["accent"])
    d.text((tx + 14, hy0 + 26), "TOP STORY", font=font(SANS_B, 14), fill=WHITE)
    d.text((tx + 132, hy0 + 26), LEAD["kicker"], font=font(SANS_B, 14), fill=LEAD["accent"])
    hf, hlines = shrink(LEAD["headline"], SERIF_B, 38, 30, 560, 2)
    hy = hy0 + 62
    for i, line in enumerate(hlines):
        d.text((tx, hy + i * 48), line, font=hf, fill=INK)
    sf = font(SANS, 17)
    slines = wrap(LEAD["standfirst"], sf, 540, 3)
    sy = hy + len(hlines) * 48 + 12
    for i, line in enumerate(slines):
        d.text((tx, sy + i * 24), line, font=sf, fill=BODY)
    # Index strip along the bottom of the lead, filling the panel
    # and pointing the reader at the five stories below.
    d.line([tx, hy1 - 48, tx + 540, hy1 - 48], fill=LINE, width=1)
    d.text((tx, hy1 - 38), "ALSO IN THIS PICTURE:", font=font(SANS_B, 13), fill=LEAD["accent"])
    d.text((tx, hy1 - 20), "TRUMP  •  MUSK  •  UKRAINE  •  S. KOREA  •  CHINA",
           font=font(SANS_B, 13), fill=NAVY)
    draw_space_scene(img, (hx0 + 596, hy0 + 16, hx1 - 16, hy1 - 16))
    # --- Section label --------------------------------------------------
    ly = 486
    label = "MORE FROM AROUND THE WORLD"
    lf = font(SANS_B, 15)
    d.text((m, ly), label, font=lf, fill=NAVY)
    lx = m + int(lf.getlength(label)) + 14
    d.line([lx, ly + 9, W - m, ly + 9], fill=GOLD, width=2)
    # --- Two wide stories ----------------------------------------------
    gap = 24
    pw = (W - 2 * m - gap) // 2
    for i, story in enumerate(WIDE):
        x0 = m + i * (pw + gap)
        card(d, (x0, 514, x0 + pw, 694), story, 24, 15, 2, 2)
    # --- Three narrow stories -------------------------------------------
    pw3 = (W - 2 * m - 2 * gap) // 3
    for i, story in enumerate(NARROW):
        x0 = m + i * (pw3 + gap)
        card(d, (x0, 712, x0 + pw3, 962), story, 21, 14, 3, 3)
    # --- Footer ---------------------------------------------------------
    d.rectangle([0, 976, W, H], fill=NAVY)
    d.text((m, 990), "ALL EVENTS FIRST REPORTED 24 NOVEMBER 2026",
           font=font(SANS_B, 14), fill=WHITE)
    d.text((W - m - 360, 990), "SOURCES: SCMP  •  THE JAPAN TIMES  •  AFP  •  AP",
           font=font(SANS, 14), fill=FAINT)
    return img


def main():
    out = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out.mkdir(parents=True, exist_ok=True)
    if HAVE_PIL:
        build().save(out / "entry.png", format="PNG")
    else:
        shutil.copyfile(Path(__file__).with_name("entry.png"), out / "entry.png")


if __name__ == "__main__":
    main()
