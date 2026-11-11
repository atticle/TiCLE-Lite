"""
Generate asyncio_structure.png — 1100x500 image illustrating
"Additive vs Transformative concurrency" for the TiCLE Lite textbook.
All text is in English per the textbook rule for embedded diagrams.
"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1100, 520

BG         = (245, 245, 248)
PANEL_L    = (230, 240, 255)   # light blue for additive side
PANEL_R    = (255, 238, 230)   # light orange for asyncio side
CODE_BG    = (30,  34,  40)    # dark code box
CODE_FG    = (200, 210, 220)
KW_COLOR   = (130, 180, 255)   # keyword colour in code
WARN_BG    = (255, 210, 200)
WARN_FG    = (180, 40, 20)
ARROW_COL  = (100, 100, 130)
TITLE_COL  = (40,  40,  60)
LABEL_COL  = (50,  60, 100)
GREEN_NOTE = (30, 130, 60)
DIVIDER    = (180, 180, 200)

img  = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# ── fonts ────────────────────────────────────────────────────────────────────
def try_font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

MONO_PATHS = [
    "C:/Windows/Fonts/consola.ttf",
    "C:/Windows/Fonts/cour.ttf",
    "C:/Windows/Fonts/lucon.ttf",
]
SANS_PATHS = [
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
]
BOLD_PATHS = [
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
]

f_title   = try_font(BOLD_PATHS, 22)
f_label   = try_font(BOLD_PATHS, 17)
f_body    = try_font(SANS_PATHS, 14)
f_code    = try_font(MONO_PATHS, 13)
f_code_sm = try_font(MONO_PATHS, 12)
f_warn    = try_font(BOLD_PATHS, 14)
f_note    = try_font(SANS_PATHS, 13)

# ── title ────────────────────────────────────────────────────────────────────
title = "asyncio Requires a Full Program Restructure"
tw = draw.textlength(title, font=f_title)
draw.text(((W - tw) / 2, 14), title, fill=TITLE_COL, font=f_title)

# ── divider line in the middle ───────────────────────────────────────────────
MID = W // 2
draw.line([(MID, 46), (MID, H - 10)], fill=DIVIDER, width=2)

# ────────────────────────────────────────────────────────────────────────────
# LEFT PANEL  —  IRQ / Timer / _thread  (Additive)
# ────────────────────────────────────────────────────────────────────────────
PAD = 18
lx1, ly1, lx2, ly2 = PAD, 50, MID - PAD, H - PAD
draw.rounded_rectangle([lx1, ly1, lx2, ly2], radius=10, fill=PANEL_L, outline=DIVIDER, width=1)

# panel title
ptitle_l = "IRQ / Timer / _thread"
draw.text((lx1 + 12, ly1 + 10), ptitle_l, fill=LABEL_COL, font=f_label)
draw.text((lx1 + 12, ly1 + 31), "Additive — existing code stays unchanged", fill=(80, 90, 140), font=f_body)

# code box
cx1, cy1, cx2, cy2 = lx1 + 12, ly1 + 60, lx2 - 12, ly2 - 90
draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=6, fill=CODE_BG)

code_lines_l = [
    ("# Original loop — unchanged", CODE_FG),
    ("while True:", KW_COLOR),
    ("    d = sonic.read()", CODE_FG),
    ("    display.update(d)", CODE_FG),
    ("    time.sleep_ms(50)", CODE_FG),
    ("", None),
    ("# Just ADD on top:", (160, 220, 130)),
    ("button.irq(my_handler)", CODE_FG),
    ("timer = Timer(period=500, ...)", CODE_FG),
    ("_thread.start_new_thread(...)", CODE_FG),
]
cy = cy1 + 8
for line, color in code_lines_l:
    if color:
        draw.text((cx1 + 8, cy), line, fill=color, font=f_code)
    cy += 18

# bottom note
note_l = "+ Attach new behaviour without rewriting the program"
draw.text((lx1 + 12, ly2 - 80), note_l, fill=GREEN_NOTE, font=f_body)
draw.text((lx1 + 12, ly2 - 60), "+ Any blocking call only freezes that one thread", fill=GREEN_NOTE, font=f_body)

# ────────────────────────────────────────────────────────────────────────────
# RIGHT PANEL  —  asyncio  (Transformative)
# ────────────────────────────────────────────────────────────────────────────
rx1, ry1, rx2, ry2 = MID + PAD, 50, W - PAD, H - PAD
draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=10, fill=PANEL_R, outline=DIVIDER, width=1)

ptitle_r = "asyncio"
draw.text((rx1 + 12, ry1 + 10), ptitle_r, fill=(140, 60, 20), font=f_label)
draw.text((rx1 + 12, ry1 + 31), "Transformative — entire program must be rewritten", fill=(160, 80, 40), font=f_body)

# code box
dx1, dy1, dx2, dy2 = rx1 + 12, ry1 + 60, rx2 - 12, ry2 - 90
draw.rounded_rectangle([dx1, dy1, dx2, dy2], radius=6, fill=CODE_BG)

code_lines_r = [
    ("# Every long-running task → async def", (160, 220, 130)),
    ("async def task_sensor():", KW_COLOR),
    ("    while True:", KW_COLOR),
    ("        d = await sr04.read()  # ← must be await", CODE_FG),
    ("        await asyncio.sleep_ms(40)", CODE_FG),
    ("", None),
    ("async def task_display():", KW_COLOR),
    ("    while True:", KW_COLOR),
    ("        lcd.update()", CODE_FG),
    ("        await asyncio.sleep_ms(150)", CODE_FG),
    ("", None),
    ("async def main():", KW_COLOR),
    ("    await asyncio.gather(", CODE_FG),
    ("        task_sensor(), task_display())", CODE_FG),
    ("", None),
    ("asyncio.run(main())  # only entry point", (130, 180, 255)),
]
dy = dy1 + 8
for line, color in code_lines_r:
    if color:
        draw.text((dx1 + 8, dy), line, fill=color, font=f_code_sm)
    dy += 17

# warning box
wx1, wy1, wx2, wy2 = rx1 + 12, ry2 - 85, rx2 - 12, ry2 - 55
draw.rounded_rectangle([wx1, wy1, wx2, wy2], radius=5, fill=WARN_BG, outline=(220, 100, 80), width=1)
warn_text = "Any blocking call (time.sleep_ms, sensor.read) freezes ALL tasks"
draw.text((wx1 + 8, wy1 + 6), "⚠  " + warn_text, fill=WARN_FG, font=f_warn)

note_r = "→ Use SR04Async / ServoAsync / AsyncAudio to wrap blocking into await"
draw.text((rx1 + 12, ry2 - 46), note_r, fill=GREEN_NOTE, font=f_body)

# ── save ─────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "asyncio_structure.png")
img.save(out)
print("Saved:", out, f"({W}x{H})")
