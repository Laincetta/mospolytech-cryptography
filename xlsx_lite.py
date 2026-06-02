# -*- coding: utf-8 -*-
"""Мини-генератор .xlsx без сторонних библиотек (только stdlib).
Поддержка: значения (числа/строки), стили (шрифт, заливка, рамка, выравнивание),
ширины столбцов, объединение ячеек, закрепление строк."""
import zipfile
from xml.sax.saxutils import escape


def colref(c):
    s = ""
    while c:
        c, r = divmod(c - 1, 26)
        s = chr(65 + r) + s
    return s


class Sheet:
    def __init__(self, name):
        self.name = name
        self.rows = []        # список строк; строка — список (value, style) | None
        self.colw = {}        # столбец(1-based) -> ширина
        self.merges = []      # (r1,c1,r2,c2)
        self.freeze = None    # (n_rows, n_cols)

    def add(self, cells):
        self.rows.append(cells)

    def width(self, **kw):     # width(A=8, B=20) — буквами
        for k, v in kw.items():
            col = 0
            for ch in k:
                col = col * 26 + (ord(ch) - 64)
            self.colw[col] = v

    def merge(self, r1, c1, r2, c2):
        self.merges.append((r1, c1, r2, c2))


class Workbook:
    def __init__(self):
        self.sheets = []
        self._fonts, self._fontlist = {}, []
        self._fills, self._filllist = {}, []
        self._borders, self._borderlist = {}, []
        self._xfs, self._xflist = {}, []
        self._font(False, False, False, "000000", "Calibri", 11)
        self._filllist += ['<fill><patternFill patternType="none"/></fill>',
                           '<fill><patternFill patternType="gray125"/></fill>']
        self._fills["__none__"], self._fills["__g__"] = 0, 1
        self._borderlist.append('<border><left/><right/><top/><bottom/><diagonal/></border>')
        self._borders[False] = 0
        self._xflist.append('<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>')
        self._xfs[(0, 0, 0, None, None, False)] = 0

    def sheet(self, name):
        s = Sheet(name); self.sheets.append(s); return s

    def _font(self, b, i, u, color, name, sz):
        key = (b, i, u, color, name, sz)
        if key in self._fonts:
            return self._fonts[key]
        idx = len(self._fontlist)
        p = "<font>" + ("<b/>" if b else "") + ("<i/>" if i else "") + ("<u/>" if u else "")
        p += f'<sz val="{sz}"/><color rgb="FF{color}"/><name val="{name}"/></font>'
        self._fontlist.append(p); self._fonts[key] = idx; return idx

    def _fill(self, color):
        if color is None:
            return 0
        if color in self._fills:
            return self._fills[color]
        idx = len(self._filllist)
        self._filllist.append(
            f'<fill><patternFill patternType="solid"><fgColor rgb="FF{color}"/>'
            f'<bgColor indexed="64"/></patternFill></fill>')
        self._fills[color] = idx; return idx

    def _border(self, on):
        if on in self._borders:
            return self._borders[on]
        idx = len(self._borderlist)
        s = '<{0} style="thin"><color rgb="FFAFC4C6"/></{0}>'
        self._borderlist.append("<border>" + s.format("left") + s.format("right") +
                                s.format("top") + s.format("bottom") + "<diagonal/></border>")
        self._borders[on] = idx; return idx

    def _xf(self, st):
        if not st:
            return 0
        fb = self._font(st.get("b", False), st.get("i", False), st.get("u", False),
                        st.get("color", "000000"), st.get("font", "Calibri"), st.get("sz", 11))
        fl = self._fill(st.get("fill"))
        bd = self._border(st.get("border", False))
        ha, va, wrap = st.get("align"), st.get("valign"), st.get("wrap", False)
        key = (fb, fl, bd, ha, va, wrap)
        if key in self._xfs:
            return self._xfs[key]
        idx = len(self._xflist)
        al = ""
        if ha or va or wrap:
            al = "<alignment" + (f' horizontal="{ha}"' if ha else "") + \
                 (f' vertical="{va}"' if va else "") + (' wrapText="1"' if wrap else "") + "/>"
        self._xflist.append(
            f'<xf numFmtId="0" fontId="{fb}" fillId="{fl}" borderId="{bd}" xfId="0" '
            f'applyFont="1" applyFill="1" applyBorder="1"'
            f'{" applyAlignment=\"1\"" if al else ""}>{al}</xf>')
        self._xfs[key] = idx; return idx

    def _styles_xml(self):
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                f'<fonts count="{len(self._fontlist)}">' + "".join(self._fontlist) + "</fonts>"
                f'<fills count="{len(self._filllist)}">' + "".join(self._filllist) + "</fills>"
                f'<borders count="{len(self._borderlist)}">' + "".join(self._borderlist) + "</borders>"
                '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
                f'<cellXfs count="{len(self._xflist)}">' + "".join(self._xflist) + "</cellXfs>"
                '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
                "</styleSheet>")

    def _sheet_xml(self, sh):
        out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
        if sh.freeze:
            nr, nc = sh.freeze
            tl = f"{colref(nc + 1)}{nr + 1}"
            out.append('<sheetViews><sheetView workbookViewId="0">'
                       f'<pane xSplit="{nc}" ySplit="{nr}" topLeftCell="{tl}" '
                       'activePane="bottomRight" state="frozen"/></sheetView></sheetViews>')
        if sh.colw:
            cols = "".join(f'<col min="{c}" max="{c}" width="{w}" customWidth="1"/>'
                           for c, w in sorted(sh.colw.items()))
            out.append(f"<cols>{cols}</cols>")
        out.append("<sheetData>")
        for ri, row in enumerate(sh.rows, 1):
            cells = []
            for ci, cell in enumerate(row, 1):
                if cell is None:
                    continue
                val, st = cell if isinstance(cell, tuple) else (cell, None)
                if val is None or val == "":
                    if st:
                        cells.append(f'<c r="{colref(ci)}{ri}" s="{self._xf(st)}"/>')
                    continue
                s = self._xf(st)
                sattr = f' s="{s}"' if s else ""
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    cells.append(f'<c r="{colref(ci)}{ri}"{sattr}><v>{val}</v></c>')
                else:
                    cells.append(f'<c r="{colref(ci)}{ri}"{sattr} t="inlineStr">'
                                 f'<is><t xml:space="preserve">{escape(str(val))}</t></is></c>')
            out.append(f'<row r="{ri}">' + "".join(cells) + "</row>")
        out.append("</sheetData>")
        if sh.merges:
            m = "".join(f'<mergeCell ref="{colref(c1)}{r1}:{colref(c2)}{r2}"/>'
                        for r1, c1, r2, c2 in sh.merges)
            out.append(f'<mergeCells count="{len(sh.merges)}">{m}</mergeCells>')
        out.append("</worksheet>")
        return "".join(out)

    def save(self, path):
        ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="xml" ContentType="application/xml"/>'
              '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
              '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>')
        for i in range(len(self.sheets)):
            ct += (f'<Override PartName="/xl/worksheets/sheet{i+1}.xml" '
                   'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        ct += "</Types>"
        rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                "</Relationships>")
        wb_sheets = "".join(f'<sheet name="{escape(s.name)}" sheetId="{i+1}" r:id="rId{i+1}"/>'
                            for i, s in enumerate(self.sheets))
        workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                    f"<sheets>{wb_sheets}</sheets></workbook>")
        wb_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">')
        for i in range(len(self.sheets)):
            wb_rels += (f'<Relationship Id="rId{i+1}" '
                        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                        f'Target="worksheets/sheet{i+1}.xml"/>')
        wb_rels += ('<Relationship Id="rId100" '
                    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
                    'Target="styles.xml"/></Relationships>')
        # ВАЖНО: сперва рендерим листы (это регистрирует стили), потом styles.xml
        sheet_xmls = [self._sheet_xml(s) for s in self.sheets]
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", ct)
            z.writestr("_rels/.rels", rels)
            z.writestr("xl/workbook.xml", workbook)
            z.writestr("xl/_rels/workbook.xml.rels", wb_rels)
            z.writestr("xl/styles.xml", self._styles_xml())
            for i, xml in enumerate(sheet_xmls):
                z.writestr(f"xl/worksheets/sheet{i+1}.xml", xml)
