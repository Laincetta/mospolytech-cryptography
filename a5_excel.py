# -*- coding: utf-8 -*-
"""Сборка двух Excel-файлов A5/1 и A5/2 (моё оформление).
Каждая книга: лист «Тест» (вход/гамма/шифр) + лист «Трассировка» (потактовая).
Данные берутся из a5_test.py (там же входные параметры)."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import a5_test as A
from xlsx_lite import Workbook

KEY, FRAME, WORD = A.KEY_HEX, A.FRAME, A.WORD
ALPH = A.ALPHABET

# --- палитра ---
TEALD, TEAL, LGRAY = "16524F", "2E8B8B", "E8EEF0"
PALEY, PALEB, PALEG = "FFF3D1", "E6F0FB", "E9F5EC"

# --- стили ---
TITLE = dict(b=True, color="FFFFFF", fill=TEALD, sz=14, align="center", valign="center")
SUB   = dict(i=True, color="FFFFFF", fill=TEAL, align="center")
HDR   = dict(b=True, color="FFFFFF", fill=TEAL, border=True, align="center", wrap=True, valign="center")
LBL   = dict(b=True, fill=LGRAY, border=True, align="left")
VAL   = dict(border=True, align="center")
VALL  = dict(border=True, align="left")
MONO  = dict(font="Consolas", sz=10, border=True, align="center")
KEYV  = dict(font="Consolas", sz=11, b=True, border=True, align="left")
GAM   = dict(font="Consolas", sz=10, b=True, fill=PALEY, border=True, align="center")
LET   = dict(b=True, fill=PALEG, border=True, align="center")
NOTE  = dict(i=True, color="808080", sz=9)

STAGEFILL = {"ключ": PALEB, "кадр": PALEG, "холостой": None, "гамма": PALEY}


def mono_fill(fill):
    s = dict(MONO)
    if fill:
        s["fill"] = fill
    return s


def cell_fill(base, fill):
    s = dict(base)
    if fill:
        s["fill"] = fill
    return s


def build_test_sheet(wb, title, mbits, gamma, cbits):
    s = wb.sheet("Тест")
    s.width(A=7, B=14, C=12, D=12, E=10, F=2, G=10, H=10, I=10, J=10)
    s.add([(title, TITLE)])
    s.merge(1, 1, 1, 5)
    s.add([(f"вариант 26 · слово «{WORD}»", SUB)])
    s.merge(2, 1, 2, 5)
    s.add([])
    s.add([("Ключ (hex, 64 бит)", LBL), (KEY, KEYV)]); s.merge(4, 2, 4, 5)
    fb = "".join(str(b) for b in A.frame_bits(FRAME))
    s.add([("Кадр (22 бит)", LBL), (fb, KEYV)]); s.merge(5, 2, 5, 5)
    wbits = "".join(str(b) for b in mbits)
    s.add([("Слово → биты", LBL), (wbits, KEYV)]); s.merge(6, 2, 6, 5)
    s.add([])
    s.add([("№", HDR), ("бит слова", HDR), ("бит гаммы", HDR),
           ("шифр = ⊕", HDR), ("буква", HDR)])
    for i in range(len(mbits)):
        letter = ""
        if i % 5 == 4:
            idx = 0
            for b in cbits[i - 4:i + 1]:
                idx = (idx << 1) | b
            letter = ALPH[idx].upper()
        s.add([(i, VAL), (mbits[i], MONO), (gamma[i], GAM),
               (cbits[i], MONO), (letter, LET)])
    r = len(mbits) + 9
    s.add([("Шифр-слово", LBL), (A.bits_to_text(cbits).upper(), LET)])
    s.merge(r, 2, r, 5)
    back = [cbits[i] ^ gamma[i] for i in range(len(cbits))]
    s.add([("Расшифровка", LBL), (A.bits_to_text(back), VALL)])
    s.merge(r + 1, 2, r + 1, 5)
    s.add([])
    s.add([("Алфавит (5-битные коды):", NOTE)])
    # легенда 8x4
    for row0 in range(8):
        cells = []
        for col0 in range(4):
            n = col0 * 8 + row0
            if n < 32:
                cells.append((f"{ALPH[n].upper()}={n:05b}", dict(font="Consolas", sz=9)))
            else:
                cells.append(None)
        s.add(cells)
    return s


def build_trace_sheet(wb, trace, has_r4):
    s = wb.sheet("Трассировка")
    if has_r4:
        head = ["Такт", "Этап", "Вброс", "R1 (19)", "R2 (22)", "R3 (23)", "R4 (17)",
                "R4[3]", "R4[7]", "R4[10]", "F", "Сдвиг", "Гамма"]
        s.width(A=6, B=9, C=7, D=22, E=25, F=26, G=20, H=7, I=7, J=8, K=5, L=10, M=7)
    else:
        head = ["Такт", "Этап", "Вброс", "R1 (19)", "R2 (22)", "R3 (23)",
                "R1[8]", "R2[10]", "R3[10]", "F", "Сдвиг", "Гамма"]
        s.width(A=6, B=9, C=7, D=22, E=25, F=26, G=7, H=8, I=8, J=5, K=10, L=7)
    s.add([(h, HDR) for h in head])
    s.freeze = (1, 0)
    for t in trace:
        fill = STAGEFILL.get(t["stage"])
        row = [(t["k"], cell_fill(VAL, fill)), (t["stage"], cell_fill(VALL, fill)),
               (t["inj"], cell_fill(VAL, fill)),
               (t["r1"], mono_fill(fill)), (t["r2"], mono_fill(fill)), (t["r3"], mono_fill(fill))]
        if has_r4:
            row += [(t["r4"], mono_fill(fill)),
                    (t["c3"], cell_fill(VAL, fill)), (t["c7"], cell_fill(VAL, fill)),
                    (t["c10"], cell_fill(VAL, fill))]
        else:
            row += [(t["s1"], cell_fill(VAL, fill)), (t["s2"], cell_fill(VAL, fill)),
                    (t["s3"], cell_fill(VAL, fill))]
        row += [(t["f"], cell_fill(VAL, fill)), (t["sh"], cell_fill(VAL, fill)),
                (t["out"], cell_fill(GAM, PALEY) if t["out"] != "" else cell_fill(VAL, fill))]
        s.add(row)
    return s


def build(cipher, title, fname, has_r4):
    mbits = A.text_to_bits(WORD)
    gamma = cipher.keystream(len(mbits))
    cbits = [mbits[i] ^ gamma[i] for i in range(len(mbits))]
    wb = Workbook()
    build_test_sheet(wb, title, mbits, gamma, cbits)
    build_trace_sheet(wb, cipher.trace, has_r4)
    try:
        wb.save(fname)
    except PermissionError:
        fname = fname.replace(".xlsx", "_NEW.xlsx")
        wb.save(fname)
        print("  (файл был занят — сохранил в", fname, ")")
    print(f"{fname}: шифр-слово = {A.bits_to_text(cbits)}  (слово={WORD}, тактов: {len(cipher.trace)})")


if __name__ == "__main__":
    build(A.A5_1(KEY, FRAME), "Тестирование A5/1", "A5_1.xlsx", False)
    build(A.A5_2(KEY, FRAME), "Тестирование A5/2", "A5_2.xlsx", True)
