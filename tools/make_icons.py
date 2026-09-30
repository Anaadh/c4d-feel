"""Generate the C4D Feel icon set (original artwork, C4D R24-inspired colours).

Run:  python tools/make_icons.py
Writes 128x128 PNGs into c4d_feel/icons/.
"""

import math
import os

from PIL import Image, ImageDraw

S = 512          # supersampled canvas, downscaled to OUT
OUT = 128
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "c4d_feel", "icons")

ORANGE = (243, 149, 49, 255)
ORANGE_D = (176, 96, 20, 255)
BLUE = (96, 170, 235, 255)
BLUE_D = (40, 100, 170, 255)
GREEN = (80, 200, 120, 255)
GREEN_D = (30, 120, 60, 255)
PURPLE = (150, 130, 225, 255)
PURPLE_D = (80, 60, 150, 255)
WHITE = (235, 235, 235, 255)
GREY = (150, 150, 150, 255)
DARK = (40, 40, 40, 255)
W = S // 16      # base stroke width


def canvas():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def save(im, name):
    im.resize((OUT, OUT), Image.LANCZOS).save(os.path.join(OUT_DIR, name + ".png"))


def P(x, y):
    return (x * S, y * S)


def ring(d, cx, cy, r, color, width=W):
    d.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], outline=color, width=width)


def arrow(d, x0, y0, x1, y1, color, width=W, head=0.12):
    d.line([P(x0, y0), P(x1, y1)], fill=color, width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (-1, 1):
        a = ang + math.pi - s * 0.5
        d.line([P(x1, y1), P(x1 + head * math.cos(a), y1 + head * math.sin(a))], fill=color, width=width)


def poly(d, pts, fill=None, outline=None, width=W):
    pts = [P(*p) for p in pts]
    if fill:
        d.polygon(pts, fill=fill)
    if outline:
        d.line(pts + [pts[0]], fill=outline, width=width, joint="curve")


def cube(d, cx=0.5, cy=0.52, r=0.3, top=BLUE, left=BLUE_D, right=(70, 140, 210, 255), edge=None):
    """Isometric cube; returns vertex dict."""
    h = r * 0.58
    t = (cx, cy - r)
    tl, tr = (cx - r, cy - r + h), (cx + r, cy - r + h)
    c = (cx, cy - r + 2 * h)
    bl, br = (cx - r, cy + h), (cx + r, cy + h)
    b = (cx, cy + 2 * h)
    poly(d, [t, tr, c, tl], fill=top)
    poly(d, [tl, c, b, bl], fill=left)
    poly(d, [c, tr, br, b], fill=right)
    if edge:
        for a, z in ((t, tr), (tr, br), (br, b), (b, bl), (bl, tl), (tl, t), (c, tl), (c, tr), (c, b)):
            d.line([P(*a), P(*z)], fill=edge, width=W // 2)
    return dict(t=t, tl=tl, tr=tr, c=c, bl=bl, br=br, b=b)


def cursor(d, x, y, s, color):
    pts = [(x, y), (x, y + s), (x + s * 0.28, y + s * 0.72), (x + s * 0.5, y + s * 1.05),
           (x + s * 0.62, y + s * 0.98), (x + s * 0.42, y + s * 0.66), (x + s * 0.75, y + s * 0.66)]
    poly(d, pts, fill=color)


# ---------------------------------------------------------------------------
def build():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Undo / redo
    for name, flip in (("undo", False), ("redo", True)):
        im, d = canvas()
        d.arc([P(0.22, 0.25), P(0.82, 0.85)], 180, 360 + 60, fill=GREY, width=W)
        arrow(d, 0.34, 0.55, 0.22, 0.55, GREY, head=0.14) if not flip else None
        if flip:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
            d = ImageDraw.Draw(im)
            arrow(d, 0.66, 0.55, 0.78, 0.55, GREY, head=0.14)
        save(im, name)

    # Live selection: cursor in a ring
    im, d = canvas()
    ring(d, 0.5, 0.5, 0.4, ORANGE)
    cursor(d, 0.38, 0.28, 0.42, WHITE)
    save(im, "live_select")

    # Move: four-way arrows
    im, d = canvas()
    for x0, y0, x1, y1 in ((0.5, 0.5, 0.5, 0.1), (0.5, 0.5, 0.5, 0.9), (0.5, 0.5, 0.1, 0.5), (0.5, 0.5, 0.9, 0.5)):
        arrow(d, x0, y0, x1, y1, ORANGE, width=W + 6, head=0.16)
    save(im, "move")

    # Scale: box with growing diagonal
    im, d = canvas()
    d.rectangle([P(0.14, 0.36), P(0.64, 0.86)], fill=ORANGE)
    d.rectangle([P(0.14, 0.14), P(0.86, 0.86)], outline=ORANGE, width=W // 2)
    arrow(d, 0.46, 0.54, 0.84, 0.16, WHITE, width=W, head=0.14)
    save(im, "scale")

    # Rotate: circular arrows
    im, d = canvas()
    d.arc([P(0.14, 0.14), P(0.86, 0.86)], 200, 340, fill=ORANGE, width=W + 6)
    d.arc([P(0.14, 0.14), P(0.86, 0.86)], 20, 160, fill=ORANGE, width=W + 6)
    arrow(d, 0.84, 0.36, 0.86, 0.48, ORANGE, width=W + 6, head=0.14)
    arrow(d, 0.16, 0.64, 0.14, 0.52, ORANGE, width=W + 6, head=0.14)
    save(im, "rotate")

    # Axis locks
    for letter in "XYZ":
        im, d = canvas()
        d.ellipse([P(0.08, 0.08), P(0.92, 0.92)], fill=ORANGE)
        d.ellipse([P(0.2, 0.2), P(0.8, 0.8)], fill=DARK)
        w = W + 4
        if letter == "X":
            d.line([P(0.36, 0.34), P(0.64, 0.66)], fill=WHITE, width=w)
            d.line([P(0.64, 0.34), P(0.36, 0.66)], fill=WHITE, width=w)
        elif letter == "Y":
            d.line([P(0.36, 0.33), P(0.5, 0.5)], fill=WHITE, width=w)
            d.line([P(0.64, 0.33), P(0.5, 0.5)], fill=WHITE, width=w)
            d.line([P(0.5, 0.5), P(0.5, 0.68)], fill=WHITE, width=w)
        else:
            d.line([P(0.36, 0.35), P(0.64, 0.35), P(0.36, 0.65), P(0.64, 0.65)], fill=WHITE, width=w, joint="curve")
        save(im, "axis_" + letter.lower())

    # Coordinate system: world (globe) / object (cube + axes)
    im, d = canvas()
    ring(d, 0.5, 0.5, 0.38, BLUE)
    d.ellipse([P(0.33, 0.12), P(0.67, 0.88)], outline=BLUE, width=W // 2)
    d.line([P(0.12, 0.5), P(0.88, 0.5)], fill=BLUE, width=W // 2)
    save(im, "coord_world")
    im, d = canvas()
    cube(d, 0.55, 0.5, 0.26)
    arrow(d, 0.2, 0.86, 0.2, 0.3, (220, 80, 80, 255), head=0.1)
    arrow(d, 0.2, 0.86, 0.72, 0.86, (90, 200, 90, 255), head=0.1)
    save(im, "coord_object")

    # Render: clapperboard variants
    def clapper(d, badge=None):
        d.rectangle([P(0.1, 0.38), P(0.9, 0.86)], fill=DARK, outline=WHITE, width=W // 2)
        poly(d, [(0.1, 0.24), (0.86, 0.12), (0.9, 0.3), (0.12, 0.38)], fill=WHITE)
        for i in range(4):
            x = 0.2 + i * 0.18
            poly(d, [(x, 0.23), (x + 0.07, 0.22), (x + 0.1, 0.33), (x + 0.03, 0.34)], fill=DARK)
        if badge == "play":
            poly(d, [(0.4, 0.48), (0.4, 0.78), (0.66, 0.63)], fill=WHITE)
        elif badge == "gear":
            ring(d, 0.5, 0.62, 0.14, ORANGE, width=W)
            for k in range(8):
                a = k * math.pi / 4
                d.line([P(0.5 + 0.14 * math.cos(a), 0.62 + 0.14 * math.sin(a)),
                        P(0.5 + 0.21 * math.cos(a), 0.62 + 0.21 * math.sin(a))], fill=ORANGE, width=W)
        else:
            d.rectangle([P(0.24, 0.5), P(0.76, 0.76)], outline=ORANGE, width=W // 2)
    for name, badge in (("render_view", None), ("render_pv", "play"), ("render_settings", "gear")):
        im, d = canvas()
        clapper(d, badge)
        save(im, name)

    # Objects
    im, d = canvas()
    cube(d)
    save(im, "cube")

    im, d = canvas()  # spline pen
    d.arc([P(0.08, 0.3), P(0.7, 0.95)], 200, 330, fill=BLUE, width=W)
    poly(d, [(0.52, 0.62), (0.86, 0.14), (0.95, 0.22), (0.62, 0.7)], fill=ORANGE)
    poly(d, [(0.52, 0.62), (0.62, 0.7), (0.5, 0.76)], fill=WHITE)
    save(im, "spline")

    im, d = canvas()  # subdivision surface: green cage around rounded blob
    cube(d, top=(60, 60, 60, 0), left=(60, 60, 60, 0), right=(60, 60, 60, 0), edge=GREEN)
    d.ellipse([P(0.3, 0.32), P(0.7, 0.72)], fill=GREEN)
    save(im, "generator")

    im, d = canvas()  # array / cloner: three small green cubes
    for cx, cy in ((0.3, 0.64), (0.7, 0.64), (0.5, 0.34)):
        cube(d, cx, cy, 0.17, top=GREEN, left=GREEN_D, right=(55, 160, 90, 255))
    save(im, "array")

    im, d = canvas()  # deformer: bent purple bar
    # A column bent sideways (like a Bend deformer acting on it).
    pts_l, pts_r = [], []
    for i in range(21):
        t = i / 20
        y = 0.9 - 0.8 * t
        x = 0.35 + 0.35 * t * t
        pts_l.append((x - 0.11, y))
        pts_r.append((x + 0.11, y))
    poly(d, pts_l + pts_r[::-1], fill=PURPLE)
    for i in range(1, 5):
        a, b = pts_l[i * 4], pts_r[i * 4]
        d.line([P(*a), P(*b)], fill=PURPLE_D, width=W // 2)
    save(im, "deformer")

    im, d = canvas()  # floor: perspective grid
    poly(d, [(0.05, 0.85), (0.95, 0.85), (0.72, 0.35), (0.28, 0.35)], fill=(70, 120, 180, 255), outline=BLUE, width=W // 2)
    for i in range(1, 4):
        t = i / 4
        d.line([P(0.05 + 0.9 * t, 0.85), P(0.28 + 0.44 * t, 0.35)], fill=WHITE, width=W // 3)
        y = 0.35 + 0.5 * t
        x0 = 0.28 - 0.23 * t
        d.line([P(x0, y), P(1 - x0, y)], fill=WHITE, width=W // 3)
    save(im, "floor")

    im, d = canvas()  # camera
    d.rounded_rectangle([P(0.1, 0.4), P(0.66, 0.8)], radius=S * 0.05, fill=WHITE)
    poly(d, [(0.66, 0.52), (0.92, 0.4), (0.92, 0.8), (0.66, 0.68)], fill=WHITE)
    d.ellipse([P(0.1, 0.12), P(0.36, 0.38)], outline=WHITE, width=W)
    d.ellipse([P(0.38, 0.12), P(0.64, 0.38)], outline=WHITE, width=W)
    save(im, "camera")

    im, d = canvas()  # light bulb
    d.ellipse([P(0.24, 0.08), P(0.76, 0.6)], fill=(250, 240, 200, 255))
    poly(d, [(0.34, 0.5), (0.66, 0.5), (0.6, 0.72), (0.4, 0.72)], fill=(250, 240, 200, 255))
    d.rectangle([P(0.38, 0.74), P(0.62, 0.9)], fill=GREY)
    save(im, "light")

    # Left palette
    im, d = canvas()  # make editable: cube with polygon points
    v = cube(d, r=0.3)
    for k in v.values():
        d.ellipse([P(k[0] - 0.045, k[1] - 0.045), P(k[0] + 0.045, k[1] + 0.045)], fill=ORANGE)
    save(im, "make_editable")

    im, d = canvas()  # model mode
    cube(d, top=(210, 210, 210, 255), left=(140, 140, 140, 255), right=(175, 175, 175, 255))
    save(im, "mode_model")

    im, d = canvas()  # UV / texture mode: checker cube
    v = cube(d, top=(220, 220, 220, 255), left=(60, 60, 60, 255), right=(220, 220, 220, 255))
    poly(d, [v["tl"], v["c"], ((v["c"][0] + v["b"][0]) / 2, (v["c"][1] + v["b"][1]) / 2),
             ((v["tl"][0] + v["bl"][0]) / 2, (v["tl"][1] + v["bl"][1]) / 2)], fill=(220, 220, 220, 255))
    save(im, "mode_uv")

    grey = dict(top=(110, 110, 110, 255), left=(70, 70, 70, 255), right=(90, 90, 90, 255))
    im, d = canvas()  # points
    v = cube(d, edge=(170, 170, 170, 255), **grey)
    for k in v.values():
        d.ellipse([P(k[0] - 0.055, k[1] - 0.055), P(k[0] + 0.055, k[1] + 0.055)], fill=ORANGE)
    save(im, "mode_points")

    im, d = canvas()  # edges
    v = cube(d, edge=(170, 170, 170, 255), **grey)
    for a, z in (("t", "tr"), ("tr", "br"), ("c", "b"), ("tl", "c")):
        d.line([P(*v[a]), P(*v[z])], fill=ORANGE, width=W)
    save(im, "mode_edges")

    im, d = canvas()  # polygons
    v = cube(d, edge=(170, 170, 170, 255), **grey)
    poly(d, [v["c"], v["tr"], v["br"], v["b"]], fill=ORANGE)
    save(im, "mode_polygons")

    im, d = canvas()  # enable axis
    arrow(d, 0.24, 0.8, 0.24, 0.14, ORANGE, width=W + 4, head=0.14)
    arrow(d, 0.24, 0.8, 0.88, 0.8, ORANGE, width=W + 4, head=0.14)
    save(im, "axis_mode")

    for name, fill in (("solo_off", GREY), ("solo_on", ORANGE)):
        im, d = canvas()  # solo: S in a circle
        d.ellipse([P(0.1, 0.1), P(0.9, 0.9)], fill=fill)
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("arialbd.ttf", int(S * 0.56))
        except OSError:
            font = ImageFont.load_default()
        d.text(P(0.5, 0.52), "S", fill=DARK, font=font, anchor="mm")
        save(im, name)

    for name, col in (("snap_off", GREY), ("snap_on", ORANGE)):
        im, d = canvas()  # magnet
        d.arc([P(0.16, 0.16), P(0.84, 0.84)], 0, 180, fill=col, width=int(S * 0.16))
        d.rectangle([P(0.16, 0.2), P(0.32, 0.5)], fill=col)
        d.rectangle([P(0.68, 0.2), P(0.84, 0.5)], fill=col)
        d.rectangle([P(0.16, 0.1), P(0.32, 0.22)], fill=WHITE)
        d.rectangle([P(0.68, 0.1), P(0.84, 0.22)], fill=WHITE)
        save(im, name)

    # Object Manager traffic-light dots and enable check / cross
    for name, fill in (("om_dot_grey", (135, 135, 135, 255)), ("om_dot_green", (70, 200, 90, 255)),
                       ("om_dot_red", (225, 60, 55, 255))):
        im, d = canvas()
        d.ellipse([P(0.3, 0.3), P(0.7, 0.7)], fill=fill, outline=(30, 30, 30, 255), width=W // 3)
        save(im, name)
    im, d = canvas()
    d.line([P(0.18, 0.52), P(0.42, 0.76), P(0.84, 0.24)], fill=(90, 210, 100, 255), width=W + 10, joint="curve")
    save(im, "om_check")
    im, d = canvas()
    d.line([P(0.24, 0.24), P(0.76, 0.76)], fill=(225, 60, 55, 255), width=W + 10)
    d.line([P(0.76, 0.24), P(0.24, 0.76)], fill=(225, 60, 55, 255), width=W + 10)
    save(im, "om_cross")

    im, d = canvas()  # workplane
    poly(d, [(0.05, 0.75), (0.5, 0.95), (0.95, 0.75), (0.5, 0.55)], fill=(200, 140, 60, 255), outline=ORANGE, width=W // 2)
    for t in (0.33, 0.66):
        d.line([P(0.05 + 0.45 * t, 0.75 - 0.2 * t), P(0.5 + 0.45 * t, 0.95 - 0.2 * t)], fill=DARK, width=W // 3)
        d.line([P(0.05 + 0.45 * t, 0.75 + 0.2 * t), P(0.5 + 0.45 * t, 0.55 + 0.2 * t)], fill=DARK, width=W // 3)
    save(im, "workplane")


if __name__ == "__main__":
    build()
    print("icons ->", os.path.abspath(OUT_DIR))
