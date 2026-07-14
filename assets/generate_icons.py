#!/usr/bin/env python3
"""Generate 14 simple PNG threat icons for malware education lab."""
import os, math, textwrap
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "modulos")
os.makedirs(OUT, exist_ok=True)

S = 100  # size
BG = (30, 30, 40, 0)  # transparent bg
FG = (220, 60, 60)    # main red
FG2 = (200, 200, 220) # white-ish
FG3 = (100, 150, 220) # blue


def new():
    return Image.new("RGBA", (S, S), BG)


def save(name, img):
    fp = os.path.join(OUT, f"{name}.png")
    img.save(fp, "PNG")
    print(f"  ✓ {name}.png")


# ─── helpers ───
def center_poly(draw, pts, fill=FG, width=0):
    draw.polygon(pts, fill=fill, outline=None)


# ─── 1. ransomware — lock ───
def icon_ransomware():
    im = new()
    d = ImageDraw.Draw(im)
    # shackle (arc + straight sides)
    d.arc([30, 15, 70, 55], 180, 0, fill=FG, width=6)
    d.line([30, 35, 30, 48], fill=FG, width=6)
    d.line([70, 35, 70, 48], fill=FG, width=6)
    # body
    d.rounded_rectangle([24, 45, 76, 85], radius=6, fill=FG)
    # keyhole
    d.ellipse([42, 55, 58, 71], fill=BG)
    d.rectangle([47, 67, 53, 80], fill=BG)
    return im


# ─── 2. wiper — trash / data destruction ───
def icon_wiper():
    im = new()
    d = ImageDraw.Draw(im)
    # bin body
    d.polygon([25, 30, 75, 30, 70, 88, 30, 88], fill=FG)
    # lid
    d.rectangle([18, 20, 82, 30], fill=FG)
    # handle
    d.rectangle([38, 12, 62, 20], fill=FG)
    # lines (data being wiped)
    d.line([38, 42, 62, 42], fill=BG, width=3)
    d.line([36, 56, 64, 56], fill=BG, width=3)
    d.line([38, 70, 62, 70], fill=BG, width=3)
    return im


# ─── 3. keylogger — keyboard ───
def icon_keylogger():
    im = new()
    d = ImageDraw.Draw(im)
    # base
    d.rounded_rectangle([10, 35, 90, 88], radius=5, fill=FG)
    # keys (grid of small squares)
    for row in range(4):
        for col in range(5):
            x = 16 + col * 15
            y = 40 + row * 12
            d.rounded_rectangle([x, y, x + 11, y + 9], radius=2, fill=BG)
    return im


# ─── 4. worm — wavy worm ───
def icon_worm():
    im = new()
    d = ImageDraw.Draw(im)
    pts = []
    for i in range(20):
        t = i / 19
        x = 15 + t * 70
        y = 40 + 20 * math.sin(t * 4 * math.pi)
        pts.append((x, y))
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=FG)
    # head
    d.ellipse([80, 36, 92, 48], fill=FG)
    # eye
    d.ellipse([84, 38, 88, 42], fill=(255, 255, 255))
    return im


# ─── 5. trojan — horse silhouette ───
def icon_trojan():
    im = new()
    d = ImageDraw.Draw(im)
    # body
    d.ellipse([25, 45, 75, 78], fill=FG)
    # neck
    d.polygon([35, 45, 45, 12, 55, 12, 55, 45], fill=FG)
    # head
    d.ellipse([42, 5, 58, 22], fill=FG)
    # ear
    d.polygon([44, 5, 48, 0, 52, 5], fill=FG)
    # legs
    d.rectangle([30, 75, 40, 92], fill=FG)
    d.rectangle([55, 75, 65, 92], fill=FG)
    # tail
    d.line([75, 50, 90, 40], fill=FG, width=4)
    d.line([90, 40, 92, 35], fill=FG, width=3)
    return im


# ─── 6. backdoor — open door ───
def icon_backdoor():
    im = new()
    d = ImageDraw.Draw(im)
    # door frame
    d.rectangle([20, 10, 80, 92], fill=None, outline=FG, width=5)
    # door (slightly open)
    d.polygon([20, 10, 55, 15, 55, 87, 20, 92], fill=FG)
    # handle
    d.ellipse([45, 45, 52, 52], fill=BG)
    # arrow (entering)
    d.line([78, 50, 88, 50], fill=FG2, width=3)
    d.polygon([85, 44, 92, 50, 85, 56], fill=FG2)
    return im


# ─── 7. rootkit — shield ───
def icon_rootkit():
    im = new()
    d = ImageDraw.Draw(im)
    # shield shape
    d.polygon([50, 5, 90, 25, 90, 55, 50, 90, 10, 55, 10, 25], fill=FG)
    # checkmark
    d.line([32, 50, 46, 68], fill=BG, width=5)
    d.line([46, 68, 72, 36], fill=BG, width=5)
    return im


# ─── 8. botnet — network nodes ───
def icon_botnet():
    im = new()
    d = ImageDraw.Draw(im)
    nodes = [(50, 15), (18, 55), (82, 55), (50, 85)]
    # connections
    for i, (x1, y1) in enumerate(nodes):
        for x2, y2 in nodes[i+1:]:
            d.line([x1, y1, x2, y2], fill=FG3, width=2)
    # nodes
    for x, y in nodes:
        d.ellipse([x-9, y-9, x+9, y+9], fill=FG)
    # inner dot
    for x, y in nodes:
        d.ellipse([x-4, y-4, x+4, y+4], fill=BG)
    return im


# ─── 9. steganography — eye inside image ───
def icon_steganography():
    im = new()
    d = ImageDraw.Draw(im)
    # image frame
    d.rectangle([8, 8, 92, 92], fill=None, outline=FG, width=4)
    # landscape inside
    d.rectangle([8, 60, 92, 92], fill=FG3)
    d.polygon([8, 60, 30, 35, 50, 60], fill=FG3)
    d.polygon([40, 60, 65, 30, 80, 60], fill=FG3)
    # eye
    d.ellipse([35, 35, 65, 65], fill=(255, 255, 255))
    d.ellipse([42, 42, 58, 58], fill=FG)
    d.ellipse([46, 46, 54, 54], fill=(0, 0, 0))
    return im


# ─── 10. fileless — ghost ───
def icon_fileless():
    im = new()
    d = ImageDraw.Draw(im)
    # ghost body
    pts = [(50, 8), (18, 25), (18, 65), (25, 72), (32, 65),
           (39, 72), (46, 65), (53, 72), (60, 65), (67, 72),
           (74, 65), (82, 72), (82, 25)]
    d.polygon(pts, fill=FG)
    # eyes
    d.ellipse([33, 30, 42, 42], fill=(255, 255, 255))
    d.ellipse([58, 30, 67, 42], fill=(255, 255, 255))
    # mouth
    d.ellipse([43, 48, 57, 55], fill=(255, 255, 255))
    return im


# ─── 11. logic_bomb — bomb with timer ───
def icon_logic_bomb():
    im = new()
    d = ImageDraw.Draw(im)
    # bomb sphere
    d.ellipse([18, 25, 82, 89], fill=FG)
    # fuse
    d.arc([45, 15, 65, 35], 180, 0, fill=FG, width=4)
    # flame
    d.polygon([60, 12, 56, 0, 64, 0], fill=(255, 200, 0))
    # timer display
    d.rectangle([35, 45, 65, 65], fill=BG)
    d.text((38, 47), "10", fill=FG, font=None)
    # X shape (danger)
    d.line([30, 72, 70, 72], fill=BG, width=3)
    d.line([35, 78, 65, 78], fill=BG, width=3)
    return im


# ─── 12. cryptominer — bitcoin / pickaxe ───
def icon_cryptominer():
    im = new()
    d = ImageDraw.Draw(im)
    # circle (coin)
    d.ellipse([12, 20, 88, 96], fill=None, outline=FG, width=5)
    # B letter simplified
    d.arc([30, 35, 55, 60], 270, 90, fill=FG, width=5)
    d.arc([30, 55, 55, 80], 270, 90, fill=FG, width=5)
    d.line([40, 35, 40, 80], fill=FG, width=5)
    d.line([40, 35, 50, 35], fill=FG, width=5)
    d.line([40, 58, 52, 58], fill=FG, width=5)
    # pickaxe at top
    d.line([50, 8, 75, 25], fill=FG2, width=3)
    d.polygon([68, 18, 82, 10, 80, 25], fill=(200, 180, 140))
    return im


# ─── 13. supply_chain — chain links ───
def icon_supply_chain():
    im = new()
    d = ImageDraw.Draw(im)
    # three chain links
    def link(cx, cy, r, thick):
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=None, outline=FG, width=thick)
    link(30, 35, 22, 5)
    link(50, 55, 22, 5)
    link(70, 75, 22, 5)
    # connection lines
    d.line([45, 48, 38, 42], fill=FG, width=5)
    d.line([62, 68, 55, 62], fill=FG, width=5)
    return im


# ─── 14. dns_tunneling — satellite / dish ───
def icon_dns_tunneling():
    im = new()
    d = ImageDraw.Draw(im)
    # dish base
    d.arc([15, 30, 85, 100], 200, 340, fill=FG, width=5)
    # stand
    d.line([50, 65, 50, 92], fill=FG, width=4)
    d.line([50, 92, 30, 98], fill=FG, width=4)
    d.line([50, 92, 70, 98], fill=FG, width=4)
    # signal waves
    d.arc([55, 5, 75, 35], 270, 40, fill=FG3, width=2)
    d.arc([65, -5, 95, 35], 270, 40, fill=FG3, width=2)
    d.arc([80, -15, 110, 40], 270, 40, fill=FG3, width=2)
    # focus point
    d.ellipse([48, 22, 56, 30], fill=FG)
    return im


# ─── run all ───
icons = [
    ("ransomware",    icon_ransomware),
    ("wiper",         icon_wiper),
    ("keylogger",     icon_keylogger),
    ("worm",          icon_worm),
    ("trojan",        icon_trojan),
    ("backdoor",      icon_backdoor),
    ("rootkit",       icon_rootkit),
    ("botnet",        icon_botnet),
    ("steganography", icon_steganography),
    ("fileless",      icon_fileless),
    ("logic_bomb",    icon_logic_bomb),
    ("cryptominer",   icon_cryptominer),
    ("supply_chain",  icon_supply_chain),
    ("dns_tunneling", icon_dns_tunneling),
]

print("Generating 14 threat icons...")
for name, fn in icons:
    save(name, fn())
print(f"\nDone → {OUT}")
