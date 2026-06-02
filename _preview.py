# -*- coding: utf-8 -*-
"""Грубый предпросмотр .drawio в PNG (Pillow) для проверки раскладки."""
import re, sys, html
from PIL import Image, ImageDraw, ImageFont

def font(sz):
    for n in (r"C:\Windows\Fonts\segoeui.ttf",
              r"C:\Windows\Fonts\arial.ttf",
              "DejaVuSans.ttf", "arial.ttf"):
        try: return ImageFont.truetype(n, sz)
        except: pass
    return ImageFont.load_default()

F = font(12); FB = font(13)

def wrap(draw, text, w, f):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=f) <= w - 12: cur = t
        else:
            if cur: lines.append(cur)
            cur = wd
    if cur: lines.append(cur)
    return lines

def parse(t):
    nodes, edges = {}, []
    for m in re.finditer(r'<mxCell id="([^"]+)" value="([^"]*)" style="([^"]*)"[^>]*vertex="1"[^>]*>\s*<mxGeometry x="([-\d]+)" y="([-\d]+)" width="(\d+)" height="(\d+)"', t):
        i, v, s, x, y, w, h = m.groups()
        nodes[i] = dict(text=html.unescape(v), style=s, x=int(x), y=int(y), w=int(w), h=int(h))
    for m in re.finditer(r'<mxCell id="[^"]+" value="([^"]*)" style="([^"]*)"[^>]*edge="1"[^>]*source="([^"]+)" target="([^"]+)"', t):
        v, s, src, dst = m.groups()
        edges.append((html.unescape(v), s, src, dst))
    pw = max(n["x"]+n["w"] for n in nodes.values())+40
    ph = max(n["y"]+n["h"] for n in nodes.values())+40
    return nodes, edges, pw, ph

def shape(s):
    if "rhombus" in s: return "dec"
    if "parallelogram" in s: return "io"
    if "shape=process" in s: return "pre"
    if "hexagon" in s: return "hex"
    if "loopLimit" in s: return "loop2" if "flipV=1" in s else "loop1"
    if "rounded=1" in s and "arcSize=50" in s: return "term"
    return "proc"

def _xy(style, key, default):
    m = re.search(key + r'=([-\d.]+)', style)
    return float(m.group(1)) if m else default

def _route(a, b, s):
    ex, ey = _xy(s, 'exitX', 0.5), _xy(s, 'exitY', 1.0)
    enx, eny = _xy(s, 'entryX', 0.5), _xy(s, 'entryY', 0.0)
    sx, sy = a["x"] + ex*a["w"], a["y"] + ey*a["h"]
    tx, ty = b["x"] + enx*b["w"], b["y"] + eny*b["h"]
    if ex in (0.0, 1.0) and ey == 0.5:           # выход вбок → горизонталь, потом вертикаль
        pts = [(sx, sy), (tx, sy), (tx, ty)]
    elif abs(sx - tx) < 2:                         # прямо вниз
        pts = [(sx, sy), (tx, ty)]
    else:                                          # вниз → вбок → вниз
        my = (sy + ty) / 2
        pts = [(sx, sy), (sx, my), (tx, my), (tx, ty)]
    return pts, (tx, ty), (enx, eny)

def render(xmltext, out):
    nodes, edges, pw, ph = parse(xmltext)
    img = Image.new("RGB", (pw, ph), "white"); d = ImageDraw.Draw(img)
    # 1-й проход: линии рёбер
    for _, s, src, dst in edges:
        if src not in nodes or dst not in nodes: continue
        pts, _, _ = _route(nodes[src], nodes[dst], s)
        d.line(pts, fill="#333", width=1)
    for i, n in nodes.items():
        x, y, w, h = n["x"], n["y"], n["w"], n["h"]; sh = shape(n["style"])
        cx, cy = x+w//2, y+h//2
        if sh == "dec":
            d.polygon([(cx, y), (x+w, cy), (cx, y+h), (x, cy)], outline="black", fill="white")
        elif sh == "io":
            o = 22; d.polygon([(x+o, y), (x+w, y), (x+w-o, y+h), (x, y+h)], outline="black", fill="white")
        elif sh == "hex":
            o = 18; d.polygon([(x+o, y), (x+w-o, y), (x+w, cy), (x+w-o, y+h), (x+o, y+h), (x, cy)], outline="black", fill="white")
        elif sh == "term":
            d.rounded_rectangle([x, y, x+w, y+h], radius=h//2, outline="black", fill="white")
        elif sh == "loop1":
            o = 14; d.polygon([(x+o, y), (x+w-o, y), (x+w, y+o), (x+w, y+h), (x, y+h), (x, y+o)], outline="black", fill="white")
        elif sh == "loop2":
            o = 14; d.polygon([(x, y), (x+w, y), (x+w, y+h-o), (x+w-o, y+h), (x+o, y+h), (x, y+h-o)], outline="black", fill="white")
        elif sh == "pre":
            d.rectangle([x, y, x+w, y+h], outline="black", fill="white")
            d.line([(x+8, y), (x+8, y+h)], fill="black"); d.line([(x+w-8, y), (x+w-8, y+h)], fill="black")
        else:
            d.rectangle([x, y, x+w, y+h], outline="black", fill="white")
        lines = wrap(d, n["text"], w, F)
        ty = cy - len(lines)*7
        for ln in lines:
            tw = d.textlength(ln, font=F)
            d.text((cx-tw/2, ty), ln, fill="black", font=F); ty += 14
    # 3-й проход: стрелки и подписи рёбер (поверх блоков)
    for v, s, src, dst in edges:
        if src not in nodes or dst not in nodes: continue
        pts, (tx, ty), (enx, eny) = _route(nodes[src], nodes[dst], s)
        ah = 5
        if eny == 0.0:    d.polygon([(tx-ah, ty-ah), (tx+ah, ty-ah), (tx, ty)], fill="#333")
        elif eny == 1.0:  d.polygon([(tx-ah, ty+ah), (tx+ah, ty+ah), (tx, ty)], fill="#333")
        elif enx == 0.0:  d.polygon([(tx-ah, ty-ah), (tx-ah, ty+ah), (tx, ty)], fill="#333")
        elif enx == 1.0:  d.polygon([(tx+ah, ty-ah), (tx+ah, ty+ah), (tx, ty)], fill="#333")
        if v:
            lx, ly = pts[0]
            d.text((lx+4, ly+2), v, fill="#c00", font=FB)
    img.save(out); print("preview", out, img.size)

if __name__ == "__main__":
    for f in sys.argv[1:]:
        full = open(f, encoding="utf-8").read()
        pages = re.findall(r'<diagram\b[^>]*>.*?</diagram>', full, re.S)
        base = f.replace("_diagram.drawio", "")
        for i, pg in enumerate(pages):
            suf = "" if len(pages) == 1 else f"_p{i+1}"
            render(pg, f"_preview_{base}{suf}.png")
