#!/usr/bin/env python3
"""Draw entry.png for make.fun news-image-20261125 (news-20261125-mosaic).

Compact mosaic: masthead + 2x4 grid of story cards, 1024x1024 PNG.
Provenance script: run it to regenerate entry.png byte-for-byte.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
F_REG = FONT_DIR + "DejaVuSans.ttf"

# (kicker, accent colour, headline, summary)
STORIES = [
    ("DIPLOMACY | UNITED NATIONS", "#1D4ED8",
     "UN Clash Over Black Sea",
     "Russia and Ukraine trade accusations over Black Sea shipping and energy attacks."),
    ("DIPLOMACY | USA-QATAR", "#0E7490",
     "US-Qatar Strategic Talks",
     "Eighth strategic dialogue in Washington reviews cooperation and regional developments."),
    ("JUSTICE | SOUTH AFRICA", "#9D174D",
     "Convicted for Ukraine Trip",
     "A Zimbabwean gets a five-year suspended sentence for planning to fight in Ukraine."),
    ("SPORT | CRICKET", "#15803D",
     "Record Double Ton",
     "Sooryavanshi, 15, hits 204 off 53 balls - the fastest List A double hundred ever."),
    ("SPACE | CHINA-PAKISTAN", "#6D28D9",
     "First Pakistani in Orbit",
     "Shenzhou-24 carries Zeeshan Ali, the first foreign astronaut aboard Tiangong station."),
    ("MIDDLE EAST | ISRAEL-USA", "#B45309",
     "Israel Aid Doubt Cast",
     "Envoy Huckabee doubts military aid to Israel will end this year as Trump promised."),
    ("JUSTICE | USA", "#9D174D",
     "Execution Stay Sought",
     "Nidal Hasan asks a US court to halt his firing-squad execution set for next week."),
    ("TRANSPORT | USA", "#C2410C",
     "O'Hare Radar Chaos",
     "Ground-radar outage delays O'Hare flights by 47 minutes on the busiest travel day."),
]

BG = "#F4F1EA"        # warm paper
INK = "#111827"       # near-black
MUTED = "#4B5563"
NAVY = "#0F2440"      # masthead band
CARD_BG = "#FFFFFF"
CARD_EDGE = "#D8D2C4"
FOOTER = "#6B7280"

MARGIN = 24
GAP = 14
MAST_H = 148
FOOT_H = 34


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap text, shrinking font until it fits in max_lines; returns (lines, font)."""
    size = fnt.size
    while size > 12:
        f = font(fnt.path, size)
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines:
            return lines, f
        size -= 1
    return wrap(draw, text, font(fnt.path, size), max_w), font(fnt.path, size)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.rectangle([0, 0, W, MAST_H], fill=NAVY)
    d.rectangle([0, MAST_H - 4, W, MAST_H], fill="#C9A227")  # gold rule
    title_f = font(F_BOLD, 76)
    title = "25 NOVEMBER 2026"
    tw = d.textlength(title, font=title_f)
    d.text(((W - tw) / 2, 22), title, font=title_f, fill="#FFFFFF")
    sub_f = font(F_BOLD, 25)
    sub = "WEDNESDAY  \u2022  EIGHT STORIES FROM AROUND THE GLOBE"
    sw = d.textlength(sub, font=sub_f)
    d.text(((W - sw) / 2, 106), sub, font=sub_f, fill="#E5C76B")

    # ---- Grid ----
    grid_top = MAST_H + 16
    grid_bot = H - FOOT_H - 10
    cols, rows = 2, 4
    cw = (W - 2 * MARGIN - (cols - 1) * GAP) // cols
    ch = (grid_bot - grid_top - (rows - 1) * GAP) // rows

    kick_f = font(F_BOLD, 19)
    head_f = font(F_BOLD, 30)
    sum_f = font(F_REG, 21)

    for i, (kicker, accent, headline, summary) in enumerate(STORIES):
        r, c = divmod(i, cols)
        x0 = MARGIN + c * (cw + GAP)
        y0 = grid_top + r * (ch + GAP)
        x1, y1 = x0 + cw, y0 + ch
        d.rounded_rectangle([x0, y0, x1, y1], radius=10,
                            fill=CARD_BG, outline=CARD_EDGE, width=1)
        d.rounded_rectangle([x0, y0, x1, y0 + 8], radius=4, fill=accent)
        d.rectangle([x0, y0 + 4, x1, y0 + 8], fill=accent)  # square off bar bottom
        pad = 16
        tx = x0 + pad
        max_w = cw - 2 * pad
        # kicker (shrink if needed)
        kf = kick_f
        while d.textlength(kicker, font=kf) > max_w and kf.size > 13:
            kf = font(F_BOLD, kf.size - 1)
        d.text((tx, y0 + 20), kicker, font=kf, fill=accent)
        # headline, up to 2 lines
        hlines, hf = fit_lines(d, headline, head_f, max_w, 2)
        hy = y0 + 48
        for ln in hlines:
            d.text((tx, hy), ln, font=hf, fill=INK)
            hy += hf.size + 4
        # summary, up to 2 lines (hard cap: overflow fails loudly)
        slines, sf = fit_lines(d, summary, sum_f, max_w, 2)
        sy = hy + 6
        for ln in slines:
            d.text((tx, sy), ln, font=sf, fill=MUTED)
            sy += sf.size + 6
        assert sy <= y1 - 8, f"card {i} text overflows card bottom (ends {sy}, card ends {y1})"
        assert len(hlines) == 1, f"card {i} headline wrapped to {len(hlines)} lines"

    # ---- Footer ----
    foot_f = font(F_REG, 19)
    foot = "Sources: Reuters, AP, Bloomberg  \u2022  All events of 25 November 2026"
    fw = d.textlength(foot, font=foot_f)
    d.text(((W - fw) / 2, H - FOOT_H + 4), foot, font=foot_f, fill=FOOTER)

    img.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
