# -*- coding: utf-8 -*-
"""
Генератор блок-схем .drawio по ГОСТ 19.701-90 в стиле Колесниковой.
- Текст: интуитивный русский, без англ. слов (латиница только в формулах).
- Шифрование и расшифрование — двумя отдельными схемами на ОДНОМ листе (рядом).
- Широкие блоки + авто-высота: текст не выходит за рамки.
- Цикл: ГОСТ «граница цикла». Открывающая часть — с описанием итерации,
  закрывающая часть — ПУСТАЯ (символ сам обозначает конец цикла).
"""
from html import escape
from PIL import ImageFont


def _font(sz):
    for n in (r"C:\Windows\Fonts\segoeui.ttf",
              r"C:\Windows\Fonts\arial.ttf",
              "DejaVuSans.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(n, sz)
        except Exception:
            pass
    return ImageFont.load_default()

_F = _font(13)


def _lines(text, inner_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if _F.getlength(t) <= inner_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return max(1, len(lines))

BASE = "fillColor=#ffffff;strokeColor=#000000;strokeWidth=1.5;fontSize=11;whiteSpace=wrap;html=1;"
STYLE = {
    'term':  "rounded=1;arcSize=50;" + BASE,
    'proc':  "rounded=0;" + BASE,
    'io':    "shape=parallelogram;perimeter=parallelogramPerimeter;size=0.1;" + BASE,
    'dec':   "rhombus;" + BASE,
    'pre':   "shape=process;size=0.07;" + BASE,
    'prep':  "shape=hexagon;perimeter=hexagonPerimeter2;" + BASE,
    'loop1': "shape=loopLimit;" + BASE,
    'loop2': "shape=loopLimit;flipV=1;" + BASE,
    'title': "text;html=1;align=center;verticalAlign=middle;fontSize=15;fontStyle=1;",
}
SPEC = {  # (width, inner_pad, line_h, vpad, min_h, fixed_h)
    'term':  (200, 40, 16, 0, 50, 50),
    'proc':  (360, 44, 16, 30, 58, None),
    'io':    (380, 100, 16, 30, 58, None),
    'pre':   (360, 64, 16, 30, 58, None),
    'dec':   (330, 110, 16, 66, 120, None),
    'prep':  (360, 80, 16, 30, 58, None),
    'loop1': (340, 90, 16, 26, 52, None),
    'loop2': (340, 90, 16, 26, 52, None),
}
COL, ROW, TOP, TITLE_Y = 430, 140, 96, 26


def _size(typ, text):
    w, pad, lh, vpad, minh, fixed = SPEC[typ]
    if fixed:
        return w, fixed
    return w, max(minh, _lines(text, w - pad) * lh + vpad)


def _loop_text(typ, text):
    if text.startswith("Начало цикла: "):
        t = text[len("Начало цикла: "):]
        return t[:1].upper() + t[1:]
    return text


class Page:
    def __init__(self):
        self.cells, self.boxes, self.maxx, self.maxy = [], [], 0, 0

    def node(self, nid, typ, text, x, row):
        text = _loop_text(typ, text)
        w, h = _size(typ, text)
        y = int(TOP + row * ROW)
        x = int(x - w / 2)
        self.boxes.append((nid, x, y, w, h))
        self.maxx, self.maxy = max(self.maxx, x + w), max(self.maxy, y + h)
        self.cells.append(
            f'        <mxCell id="{nid}" value="{escape(text)}" style="{STYLE[typ]}" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')

    def title(self, nid, text, x, w=320):
        y = TITLE_Y
        self.cells.append(
            f'        <mxCell id="{nid}" value="{escape(text)}" style="{STYLE["title"]}" '
            f'vertex="1" parent="1"><mxGeometry x="{int(x - w / 2)}" y="{y}" width="{w}" height="30" as="geometry"/></mxCell>')

    def edge(self, src, dst, label="", exit=None, entry=None):
        st = EDGE
        if exit:
            st += f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
        if entry:
            st += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        self.cells.append(
            f'        <mxCell id="e_{src}_{dst}" value="{escape(label)}" style="{st}" edge="1" '
            f'parent="1" source="{src}" target="{dst}"><mxGeometry relative="1" as="geometry"/></mxCell>')

    def overlaps(self):
        out = []
        for i in range(len(self.boxes)):
            for j in range(i + 1, len(self.boxes)):
                _, x1, y1, w1, h1 = self.boxes[i]; _, x2, y2, w2, h2 = self.boxes[j]
                if x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2:
                    out.append((self.boxes[i][0], self.boxes[j][0]))
        return out

EDGE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;startArrow=none;"
        "strokeWidth=1.5;fontSize=11;fontColor=#000000;labelBackgroundColor=#FFFFFF;jettySize=auto;")


def flow_width(ps):
    nodes = ps['head'] + ps.get('tail', [])
    if ps.get('split'):
        nodes += [('x', 'dec', ps['split']['dec'][1])] + ps['split']['left'] + ps['split']['right']
    return max(_size(it[1], it[2])[0] for it in nodes)


def place_flow(p, ps, cx, pref, title=None):
    """Размещает поток (head/split/tail) в колонке с центром cx, id с префиксом pref."""
    def I(x):
        return pref + x

    def lbl(it):
        return it[3] if len(it) > 3 else ""

    if title:
        p.title(I("title"), title, cx)
    head, split, tail = ps['head'], ps.get('split'), ps.get('tail', [])
    r = 0
    for it in head:
        p.node(I(it[0]), it[1], it[2], cx, r); r += 1
    for a, b in zip(head, head[1:]):
        p.edge(I(a[0]), I(b[0]), lbl(a))

    if split:
        dec = split['dec']
        p.node(I(dec[0]), 'dec', dec[1], cx, r)
        if head:
            p.edge(I(head[-1][0]), I(dec[0]), lbl(head[-1]))
        rs = r + 1
        left, right = split['left'], split['right']
        for k, it in enumerate(left):
            p.node(I(it[0]), it[1], it[2], cx - COL, rs + k)
        for k, it in enumerate(right):
            p.node(I(it[0]), it[1], it[2], cx + COL, rs + k)
        p.edge(I(dec[0]), I(left[0][0]), split['llabel'], exit=(0, 0.5), entry=(0.5, 0))
        p.edge(I(dec[0]), I(right[0][0]), split['rlabel'], exit=(1, 0.5), entry=(0.5, 0))
        for a, b in zip(left, left[1:]):
            p.edge(I(a[0]), I(b[0]), lbl(a))
        for a, b in zip(right, right[1:]):
            p.edge(I(a[0]), I(b[0]), lbl(a))
        tr = rs + max(len(left), len(right))
        for k, it in enumerate(tail):
            p.node(I(it[0]), it[1], it[2], cx, tr + k)
        if tail:
            p.edge(I(left[-1][0]), I(tail[0][0]), exit=(0.5, 1), entry=(0.5, 0))
            p.edge(I(right[-1][0]), I(tail[0][0]), exit=(0.5, 1), entry=(0.5, 0))
        for a, b in zip(tail, tail[1:]):
            p.edge(I(a[0]), I(b[0]), lbl(a))
    else:
        for k, it in enumerate(tail):
            p.node(I(it[0]), it[1], it[2], cx, r + k)
        if head and tail:
            p.edge(I(head[-1][0]), I(tail[0][0]), lbl(head[-1]))
        for a, b in zip(tail, tail[1:]):
            p.edge(I(a[0]), I(b[0]), lbl(a))

    for be in ps.get('backedges', []):
        p.edge(I(be[0]), I(be[1]), be[2], exit=(1, 0.5), entry=(1, 0.5))


def _diagram(name, did, p):
    pw, ph = p.maxx + 60, p.maxy + 60
    return (f'  <diagram name="{escape(name)}" id="{did}">\n'
            f'    <mxGraphModel dx="640" dy="480" grid="1" gridSize="10" guides="1" tooltips="1" '
            f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{pw}" '
            f'pageHeight="{ph}" math="0" shadow="0">\n      <root>\n        <mxCell id="0"/>\n'
            f'        <mxCell id="1" parent="0"/>\n' + "\n".join(p.cells) +
            f'\n      </root>\n    </mxGraphModel>\n  </diagram>\n')


def write_file(path, did, pages):
    """pages: 1 → одна схема; 2 → две схемы рядом на одном листе (ШИФР/РАСШИФР)."""
    p = Page()
    if len(pages) == 1:
        place_flow(p, pages[0], 70 + (COL if pages[0].get('split') else 0) + flow_width(pages[0]) / 2,
                   "a_", pages[0].get('title'))
        name = pages[0]['name']
    else:
        w0, w1 = flow_width(pages[0]), flow_width(pages[1])
        cx0 = 70 + (COL if pages[0].get('split') else 0) + w0 / 2
        cx1 = cx0 + w0 / 2 + 150 + (COL if pages[1].get('split') else 0) + w1 / 2
        place_flow(p, pages[0], cx0, "a_", pages[0]['name'].upper())
        place_flow(p, pages[1], cx1, "b_", pages[1]['name'].upper())
        name = pages[0]['name'] + " / " + pages[1]['name']
    warn = p.overlaps()
    open(path, "w", encoding="utf-8").write(
        '<mxfile host="app.diagrams.net" pages="1">\n%s</mxfile>\n' % _diagram(name, did, p))
    return warn
