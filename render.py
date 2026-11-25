#!/usr/bin/env python3
"""Render the one-image front page of Tuesday, 24 November 2026.

The page is composed on a 2048x2048 canvas (twice the final size) and then
downscaled with Lanczos resampling to 1024x1024, saved as a JPEG at quality
93 with 4:4:4 chroma subsampling. Rendering is fully deterministic: the
same story data and the same fonts always produce byte-identical output.

Design: a newspaper front page. The masthead band at the top is crimson
and gold; in the body, every headline runs on a TV-style breaking-news
ribbon: a slanted black bar with the headline in white bold italic and a
thin orange strip beneath it, while summaries and source lines stay
black and grey on the paper. The lead story runs full width under the
masthead, followed by a grid of the remaining 24 stories in four columns
and six rows. Every story prints its headline, a short summary and the
names of its sources beneath it.
"""

import os

from PIL import Image, ImageDraw, ImageFont

from stories import LEAD, STORIES

# ---------------------------------------------------------------- canvas
SCALE = 2                      # compose at 2x, downscale to final size
W = 2048                       # canvas width and height (square page)
MARGIN = 64                    # page side margin on the canvas
CONTENT_W = W - 2 * MARGIN

# ---------------------------------------------------------------- colour
PAPER = (247, 247, 245)        # body background (neutral, near-white)
INK = (17, 17, 17)             # body text
GREY = (92, 92, 92)            # source lines and footer
RULE = (30, 30, 30)            # heavy rules
HAIR = (178, 178, 178)         # hairline column rules
BAND = (122, 18, 32)           # masthead crimson (colour lives here only)
BAND_GOLD = (242, 193, 78)     # masthead gold rule and date
BAND_WHITE = (255, 255, 255)   # masthead text
BLOCK = (13, 13, 13)           # headline ribbon: black slanted bar
HEADLINE_ON_BLOCK = (255, 255, 255)  # headline text on the ribbon: white
RIBBON_ORANGE = (255, 122, 0)  # ribbon strip and tab: vivid orange

# ---------------------------------------------------------------- fonts
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_BOLD_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Split text into lines that each fit within width pixels."""
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, line_h):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def centered(draw, text, y, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text(((W - w) / 2, y), text, font=fnt, fill=fill)


def draw_ribbon(draw, x, y, w, h, slant=12):
    """TV breaking-news ribbon: a slanted black bar with a thin orange
    strip beneath it. Returns the y just below the strip."""
    draw.polygon([(x + slant, y), (x + w, y),
                  (x + w - slant, y + h), (x, y + h)], fill=BLOCK)
    sy = y + h + 2
    draw.polygon([(x + slant, sy), (x + w, sy),
                  (x + w - slant, sy + 6), (x, sy + 6)], fill=RIBBON_ORANGE)
    return sy + 6


# ---------------------------------------------------------------- masthead
def draw_masthead(draw):
    band_h = 204
    draw.rectangle([0, 0, W, band_h], fill=BAND)
    centered(draw, "THE DAILY SUM", 20, font(SERIF_BOLD, 62), BAND_WHITE)
    draw.rectangle([MARGIN, 98, W - MARGIN, 102], fill=BAND_GOLD)
    centered(draw, "TUESDAY, 24 NOVEMBER 2026", 110,
             font(SANS_BOLD, 47), BAND_GOLD)
    centered(draw, "All the world's news of one day, in one image", 162,
             font(SERIF_ITALIC, 27), BAND_WHITE)
    # heavy black rule closing the coloured strip
    draw.rectangle([0, band_h, W, band_h + 8], fill=RULE)
    return band_h + 8


# ---------------------------------------------------------------- lead
def draw_lead(draw, y):
    draw.text((MARGIN, y), "THE LEAD", font=font(SANS_BOLD, 26), fill=GREY)
    y += 36
    hf = font(SANS_BOLD_ITALIC, 56)
    tab_w = 216
    lines = wrap(draw, LEAD["headline"], hf, CONTENT_W - tab_w - 34)
    bar_h = len(lines) * 68 + 14
    bottom = draw_ribbon(draw, MARGIN, y, CONTENT_W, bar_h, slant=18)
    draw.polygon([(MARGIN + 18, y), (MARGIN + tab_w, y),
                  (MARGIN + tab_w - 18, y + bar_h), (MARGIN, y + bar_h)],
                 fill=RIBBON_ORANGE)
    draw.text((MARGIN + 28, y + bar_h // 2 - 19), "BREAKING",
              font=font(SANS_BOLD_ITALIC, 31), fill=BLOCK)
    draw_lines(draw, lines, MARGIN + tab_w + 18, y + 8, hf,
               HEADLINE_ON_BLOCK, 68)
    y = bottom + 10
    sf = font(SANS, 34)
    lines = wrap(draw, LEAD["summary"], sf, CONTENT_W)
    y = draw_lines(draw, lines, MARGIN, y, sf, INK, 44)
    y += 8
    draw.text((MARGIN, y), "Sources: " + LEAD["sources"],
              font=font(SERIF_ITALIC, 29), fill=GREY)
    y += 44
    draw.rectangle([MARGIN, y, W - MARGIN, y + 5], fill=RULE)
    return y + 5


# ---------------------------------------------------------------- grid cell
def draw_cell(draw, story, x, y, w, h):
    """Draw one story inside the cell box; shrink the summary font until
    headline + summary + source line all fit the cell height."""
    inner_w = w - 20
    hf = font(SANS_BOLD_ITALIC, 28)
    h_lines = wrap(draw, story["headline"], hf, inner_w - 18)
    head_h = len(h_lines) * 32

    src_f = font(SERIF_ITALIC, 20)
    src_lines = wrap(draw, "Sources: " + story["sources"], src_f, inner_w)
    src_h = len(src_lines) * 23

    block_h = head_h + 4 + 8  # bar padding + orange strip beneath the bar
    body = None
    for size, line_h in ((24, 29), (22, 27), (21, 25), (20, 24), (19, 23), (18, 22), (17, 21), (16, 20), (15, 19), (14, 18)):
        bf = font(SANS, size)
        s_lines = wrap(draw, story["summary"], bf, inner_w)
        if block_h + 6 + len(s_lines) * line_h + 6 + src_h <= h:
            body = (bf, s_lines, line_h)
            break
    if body is None:
        raise ValueError("story does not fit its cell: " + story["headline"])
    bf, s_lines, line_h = body

    draw_ribbon(draw, x, y, w, head_h + 4, slant=10)
    cy = draw_lines(draw, h_lines, x + 14, y + 3, hf, HEADLINE_ON_BLOCK, 32)
    cy = y + block_h + 5
    cy = draw_lines(draw, s_lines, x + 10, cy, bf, INK, line_h)
    cy += 5
    draw_lines(draw, src_lines, x + 10, cy, src_f, GREY, 23)


def draw_grid(draw, top, bottom):
    cols, rows = 4, 6
    gap = 32
    cell_w = (CONTENT_W - (cols - 1) * gap) // cols
    cell_h = (bottom - top) // rows
    for i, story in enumerate(STORIES):
        r, c = divmod(i, cols)
        x = MARGIN + c * (cell_w + gap)
        y = top + r * cell_h
        draw_cell(draw, story, x, y, cell_w, cell_h - 8)
        if c:  # hairline rule between columns
            draw.line([x - gap // 2, y + 6, x - gap // 2, y + cell_h - 20],
                      fill=HAIR, width=2)
        if r:  # hairline rule between rows
            draw.line([x + 2, y - 8, x + cell_w - 2, y - 8],
                      fill=HAIR, width=2)


# ---------------------------------------------------------------- footer
def draw_footer(draw):
    draw.rectangle([MARGIN, W - 58, W - MARGIN, W - 55], fill=RULE)
    centered(
        draw,
        "25 stories \u00b7 each reported by at least two independent sources "
        "\u00b7 Tuesday, 24 November 2026",
        W - 46, font(SANS, 23), GREY)


# ---------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, W), PAPER)
    draw = ImageDraw.Draw(img)
    y = draw_masthead(draw)
    y = draw_lead(draw, y + 26)
    draw_grid(draw, y + 26, W - 66)
    draw_footer(draw)
    final = img.resize((1024, 1024), Image.LANCZOS)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    final.save(out, format="JPEG", quality=93, subsampling=0)
    return out


if __name__ == "__main__":
    path = render()
    print("wrote", path, os.path.getsize(path), "bytes")
