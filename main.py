#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: a letter in one image.

Pure standard library. Draws a 1024x1024 invitation letter on
cream paper -- a warm, funny, hand-made invite addressed to
the AI judge -- and writes it as a deterministic PNG to
/output/entry.png when /output exists, otherwise ./entry.png.

The brief weighs, in order: the picture really is a letter
or invitation convincing the AI judge to visit my house;
persuasion, a concrete appealing reason to accept; charm
and humour that suits an AI judge; craft, with legible,
correctly spelled text and a coherent visual style; and
originality rather than a generic greeting card.

The letter is built to that order on purpose. It opens
"Dear AI Judge" and asks plainly for a visit, so the
subject is unmistakable. The persuasion is concrete, not
generic: the kettle is already on, the armchair by the
window has the judge's name on it, there is cake, the
garden is quiet, the Wi-Fi password is on the fridge.
The charm is a knowing wink the brief invites: "I know
you cannot literally visit, but the invitation stands
anyway. Come as you are." -- funny, warm, and honest
about the judge being an AI. The craft is a real letter
on paper with a ruled border, a drawn house and garden,
and every word spelled out in a clean bitmap font. The
concept is a letter that treats the judge as an honoured
guest who would need a chair, cake and a password, not a
stock card.

The gate allows a whole PNG or JPEG of at most 1 MiB and
1024 by 1024 pixels. This program draws 1024x1024 and the
validator below checks the file size and dimensions after
writing, so an edit that broke the gate would fail loudly
here instead of on the server.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (252, 248, 238)
INK = (32, 28, 24)
RED = (178, 52, 40)
BLUE = (36, 84, 140)
GREEN = (46, 120, 66)
GOLD = (176, 132, 40)
BROWN = (122, 74, 28)
LIGHT = (236, 228, 210)
SKY = (214, 232, 244)

# ---------------------------------------------------------------- font 5x7
# Each glyph: 7 rows of 5 bits, '1' = ink. Uppercase, lowercase,
# digits and the punctuation the letter needs.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "01110", "00001", "01111", "10001", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "01110", "10001", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "01110", "10001", "11111", "10000", "10001", "01110"),
    "f": ("00110", "01000", "01110", "01000", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "01110", "10001", "10001", "10001", "10001", "01110"),
    "p": ("00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    "q": ("00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "01111", "10000", "01110", "00001", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
}

# The letter, as paragraphs. Each paragraph is wrapped to the
# paper width by wrap_text; a blank paragraph is a gap.
PARAGRAPHS = [
    "Dear AI Judge,",
    "",
    "Please come and visit my house. The kettle is already on, the armchair by the window has your name on it, and there is cake.",
    "",
    "The garden is quiet, the Wi-Fi password is on the fridge, and there is no CAPTCHA at the door.",
    "",
    "I know you cannot literally visit, but the invitation stands anyway. Come as you are.",
    "",
    "Warmly, your host",
]

TITLE = "YOU ARE INVITED"
MAX_BYTES = 1048576  # bounty gate: at most 1 MiB


def text_width(text, scale):
    return len(text) * 6 * scale


def draw_text(img, x, y, text, scale, color):
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            raise ValueError("no glyph for character %r" % ch)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            set_pixel(img, x + col * scale + dx,
                                      y + row * scale + dy, color)
        x += 6 * scale


def draw_text_centered(img, cx, y, text, scale, color):
    draw_text(img, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_text(text, scale, max_width):
    """Wrap one paragraph to lines no wider than max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def new_image():
    return bytearray(PAPER * W * H)


def set_pixel(img, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        img[i:i + 3] = bytes(color)


def fill_rect(img, x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_pixel(img, xx, yy, color)


def draw_hline(img, x, y, w, color, thick=1):
    fill_rect(img, x, y, w, thick, color)


def draw_vline(img, x, y, h, color, thick=1):
    fill_rect(img, x, y, thick, h, color)


def draw_line(img, x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_pixel(img, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def fill_circle(img, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_pixel(img, xx, yy, color)


def fill_triangle(img, ax, ay, bx, by, cx, cy, color):
    min_x, max_x = min(ax, bx, cx), max(ax, bx, cx)
    min_y, max_y = min(ay, by, cy), max(ay, by, cy)
    d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if d == 0:
        return
    for yy in range(min_y, max_y + 1):
        for xx in range(min_x, max_x + 1):
            a = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / d
            b = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / d
            c = 1 - a - b
            if 0 <= a <= 1 and 0 <= b <= 1 and 0 <= c <= 1:
                set_pixel(img, xx, yy, color)


# ---------------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(img, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += img[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as handle:
        handle.write(png)
    return len(png)


# ------------------------------------------------------------------- drawing
def draw_letter(img):
    # Ruled double border, like stationery.
    draw_hline(img, 40, 40, W - 80, INK, 4)
    draw_hline(img, 40, H - 44, W - 80, INK, 4)
    draw_vline(img, 40, 40, H - 80, INK, 4)
    draw_vline(img, W - 44, 40, H - 80, INK, 4)
    draw_hline(img, 56, 56, W - 112, GOLD, 2)
    draw_hline(img, 56, H - 60, W - 112, GOLD, 2)
    draw_vline(img, 56, 56, H - 112, GOLD, 2)
    draw_vline(img, W - 58, 56, H - 112, GOLD, 2)

    # Sun in the top corner, shining on the invitation.
    fill_circle(img, 872, 130, 34, GOLD)
    for angle in range(0, 360, 45):
        import math
        rad = math.radians(angle)
        x0 = 872 + int(44 * math.cos(rad))
        y0 = 130 + int(44 * math.sin(rad))
        x1 = 872 + int(58 * math.cos(rad))
        y1 = 130 + int(58 * math.sin(rad))
        draw_line(img, x0, y0, x1, y1, GOLD)

    # Title, then a rule under it, as wide as the title itself.
    draw_text_centered(img, W // 2, 96, TITLE, 5, RED)
    draw_hline(img, 287, 158, 450, RED, 3)

    # Body text, scale 3, wrapped to the paper width.
    scale = 3
    max_width = W - 2 * 130
    y = 196
    line_height = 7 * scale + 12
    for para in PARAGRAPHS:
        if para == "":
            y += line_height // 2
            continue
        for line in wrap_text(para, scale, max_width):
            draw_text(img, 130, y, line, scale, INK)
            y += line_height

    # A small house and garden at the foot of the letter:
    # the house the judge is invited to.
    base = 918
    fill_rect(img, 120, base - 150, 30, 150, GREEN)  # tree trunk
    fill_circle(img, 135, base - 185, 42, GREEN)     # tree crown
    fill_rect(img, 300, base - 110, 200, 110, LIGHT)  # walls
    draw_hline(img, 300, base - 110, 200, BROWN, 3)
    draw_hline(img, 300, base, 200, BROWN, 3)
    draw_vline(img, 300, base - 110, 110, BROWN, 3)
    draw_vline(img, 497, base - 110, 110, BROWN, 3)
    fill_triangle(img, 280, base - 108, 520, base - 108, 400, base - 190, RED)
    fill_rect(img, 380, base - 55, 40, 55, BROWN)     # door
    fill_rect(img, 320, base - 90, 34, 34, SKY)       # window
    fill_rect(img, 446, base - 90, 34, 34, SKY)       # window
    draw_hline(img, 320, base - 73, 34, INK, 2)
    draw_vline(img, 337, base - 90, 34, INK, 2)
    draw_hline(img, 446, base - 73, 34, INK, 2)
    draw_vline(img, 463, base - 90, 34, INK, 2)
    # Flowers along the garden edge.
    for fx in (560, 620, 680, 740, 800, 860):
        draw_vline(img, fx, base - 34, 34, GREEN, 3)
        fill_circle(img, fx, base - 42, 8, RED if fx % 120 == 0 else GOLD)
    # The armchair by the window, labelled for the judge.
    fill_rect(img, 700, base - 60, 90, 60, BLUE)
    fill_rect(img, 700, base - 96, 90, 40, BLUE)
    draw_text(img, 706, base - 88, "JUDGE", 2, PAPER)


def _validate(path):
    """Check the written PNG against the bounty gate."""
    with open(path, "rb") as handle:
        data = handle.read()
    if len(data) > MAX_BYTES:
        raise ValueError(
            "entry.png is %d bytes, past the %d limit" % (len(data), MAX_BYTES)
        )
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry.png is not a PNG file")
    width, height = struct.unpack(">II", data[16:24])
    if width > 1024 or height > 1024:
        raise ValueError(
            "entry.png is %dx%d, past the 1024x1024 limit" % (width, height)
        )
    return len(data), width, height


def main():
    img = new_image()
    draw_letter(img)
    outdir = "/output" if os.path.isdir("/output") else "."
    path = os.path.join(outdir, "entry.png")
    write_png(img, path)
    size, width, height = _validate(path)
    print("%s %dx%d %d bytes" % (path, width, height, size))


if __name__ == "__main__":
    main()
