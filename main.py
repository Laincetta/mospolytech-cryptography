#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Единый интерфейс управления криптографическими алгоритмами
Лабораторные работы 1-11 — МосПолитех
"""

import sys
import os
import subprocess
import importlib.util
import io
import contextlib
import random
import math
import textwrap

# UTF-8 вывод на Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, LAB_DIR)
os.chdir(LAB_DIR)

# ─── Пословица (26 вариант) ───────────────────────────────────────────────────
PROVERB       = "Плохой работник никогда не находит хорошего инструмента."
_BASE_REPEAT  = PROVERB + " "
PROVERB_1000  = (_BASE_REPEAT * 18)[:1000]

# ─── Параметры по умолчанию (подобраны для удобного ручного счёта) ────────────
# Используйте эту таблицу при оформлении отчёта:
#
#  Алгоритм           Параметры
#  ─────────────────────────────────────────────────────────────────
#  Цезарь             сдвиг = 3
#  Виженер            нач. буква = 'б' (сдвиг=1), самоключ откр.текст
#  Хилл               K = [[1,0,1],[0,1,0],[0,0,1]]  det=1
#                     Зашифр. вектор: [p1+p3,  p2,  p3]
#  Плейфер            ключ = 'код'
#  Вертик. перест.    ключ = 'КОД'
#  Шеннон (ЛКГ)       a=5, c=3, T0=1  =>  γ₀=8, γ₁=11, γ₂=26, γ₃=19, …
#  A5/1, A5/2         ключ = 0x0123456789ABCDEF
#  Фейстель           ключ = FFEEDDCC…FF (ГОСТ тест-вектор)
#  AES                ключ = 000102…0F (128-бит)
#  Кузнечик           ключ = 8899AABB… (ГОСТ тест-вектор)
#  Магма              ключ = FFEEDDCC… (ГОСТ тест-вектор)
#  RSA                P=37, Q=41, E=7, N=1517, D=823
#                     Проверка: 7×823 = 5761 = 4×1440 + 1  ✓
#                     Пример:  m=2 → c=2⁷=128
#  Эль-Гамаль         p=37, g=2, x=5, y=32  (y=2⁵ mod 37)
#                     Пример k=3: a=8, y^k=23 mod 37
#  ЭКЦ                y²=x³+x+1 mod 23, G=(1,7), cb=7, k=3
# ─────────────────────────────────────────────────────────────────

# ─── Загрузка модулей ────────────────────────────────────────────────────────
def _load(name, filename):
    path = os.path.join(LAB_DIR, filename)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _try_import(alias, modname):
    try:
        mod = __import__(modname)
        return mod
    except Exception as e:
        print(f"  [ПРЕДУПРЕЖДЕНИЕ] Не удалось загрузить {modname}: {e}")
        return None


import lab1_atbash     as _atbash
import lab1_chesar     as _caesar
import lab1_polyb      as _polyb
import lab2_s_block    as _sblock
import lab2_trithemius as _trithemius
import lab2_belaso     as _belaso
import lab2_vigenere   as _vigenere
_hill     = _try_import("_hill",     "lab3_matrix")
import lab3_pleifer    as _playfair
import lab4_cardano    as _cardano
import lab4_feistel    as _feistel
import lab4_vertical   as _vertical
import lab5_shanon     as _shannon   # text_to_numbers / format_numbers / ALPHABET
import lab5_gamma      as _gamma
import lab7_aes        as _aes
_kuz      = _try_import("_kuz",      "lab7_kyznechik")
_magma    = _try_import("_magma",    "lab7_magma")
import lab8_rsa        as _rsa
import lab8_elgamal    as _elgamal
import lab8_ecc        as _ecc

_a51 = _load("a5_1", "lab6_a5-1.py")
_a52 = _load("a5_2", "lab6_a5-2.py")


# ─── Вспомогательные функции ─────────────────────────────────────────────────
def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _preview(s, n=200):
    """Только для коротких inline-строк (заголовки, баннеры)."""
    s = str(s)
    return s[:n] + f"... (ещё {len(s) - n} симв.)" if len(s) > n else s


def _show(label, text, w=64):
    """Печатает label, затем text полностью, перенесённый по ширине w."""
    print(label)
    print(textwrap.fill(str(text), width=w,
                        initial_indent="  ",
                        subsequent_indent="  ",
                        break_long_words=True,
                        break_on_hyphens=False))


def _sep(title=""):
    w = 64
    if title:
        print(f"\n{'─' * w}")
        print(f"  {title}")
        print(f"{'─' * w}")
    else:
        print("─" * w)


def _launch(filename):
    path = os.path.join(LAB_DIR, filename)
    subprocess.run([sys.executable, path])


def _alph_idx(c, alph):
    idx = alph.find(c)
    return idx if idx >= 0 else 0


# ─── Функции прогона текста (text передаётся явно) ───────────────────────────

def _run_atbash(text):
    _sep("1. АТБАШ")
    print("Параметры: ключ не нужен (зеркальная замена А↔Я, Б↔Ю, …)")
    enc = _atbash.encrypt(text.lower())
    print(f"Открытый текст ({len(text)} симв.): {text}")
    _show("Шифртекст:", _atbash.format5(enc.upper()))


def _run_caesar(text):
    SHIFT = 3
    _sep("2. ЦЕЗАРЬ")
    print(f"Параметры: сдвиг = {SHIFT}  (А→Г, Б→Д, В→Е, …)")
    enc = _caesar.encrypt(text, SHIFT)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    _show("Шифртекст:", _caesar.format5(enc.upper()))


def _run_polybius(text):
    _sep("3. КВАДРАТ ПОЛИБИЯ")
    print("Параметры: ключ не нужен, алфавит 33+дефис, 6 столбцов")
    enc = _polyb.polibiy_encode(text)
    pairs = enc.split()
    print(f"Открытый текст ({len(text)} симв.): {text}")
    _show(f"Шифртекст ({len(pairs)} пар цифр):", enc)


def _run_sblock(text):
    _sep("4. S-БЛОКИ (ГОСТ / МАГМА)")
    ALPH = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    chars = [c for c in text.upper().replace('Ё', 'Е') if c in ALPH]
    results = []
    for i in range(0, len(chars) - 7, 8):
        x = 0
        for j in range(8):
            x |= (_alph_idx(chars[i + j], ALPH) & 0xF) << (4 * j)
        results.append(f"{_sblock.t(x):08X}")
    print("Параметры: 8 S-блоков ГОСТ (4 бита каждого символа → 32-бит блок)")
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"Символов: {len(chars)},  блоков: {len(results)}")
    _show("Результат (hex):", ' '.join(results))


def _run_trithemius(text):
    _sep("5. ШИФР ТРИТЕМИУСА")
    print("Параметры: ключ не нужен, сдвиг i-го символа = i  (0, 1, 2, …)")
    proc = _trithemius.replace(text)
    enc = _trithemius.trithemius_process(proc, 1)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    _show("Шифртекст:", enc)


def _run_belaso(text):
    KEY = 'зонд'   # пример из PDF, 4 буквы — удобно считать вручную
    _sep("6. ШИФР БЕЛАЗО")
    print(f"Параметры: ключевое слово = '{KEY}'  (циклически повторяется)")
    print(f"  Аналог Виженера, но ключ фиксированный, не самоключ")
    proc = _belaso.replace(text)
    enc = _belaso.bellaso(proc, KEY, encrypt=True)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    _show("Шифртекст:", _belaso.format5(enc))


def _run_vigenere(text):
    KEY = 'б'
    _sep("7. ШИФР ВИЖЕНЕРА")
    print(f"Параметры: нач. буква='{KEY}' (сдвиг=1), самоключ открытого текста")
    proc = _vigenere.replace(text)
    enc = _vigenere.vigenere_process(proc, KEY, 1, 1)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    _show("Шифртекст:", enc)


def _run_hill(text):
    if _hill is None:
        print("  [ПРОПУСК] Шифр Хилла: numpy не установлен"); return
    try:
        import numpy as np
    except ImportError:
        print("  [ПРОПУСК] numpy не установлен"); return
    M = [[1, 0, 1],
         [0, 1, 0],
         [0, 0, 1]]
    _sep("8. МАТРИЧНЫЙ ШИФР ХИЛЛА")
    print(f"Параметры: K = {M}   det = 1")
    print(f"  Шифрование триплета (p1,p2,p3) → (p1+p3, p2, p3)")
    mat = np.array(M, dtype=float)
    with _quiet():
        nums = _hill.encrypt_logic(text, mat)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    nums_str = ' '.join(str(int(round(x))) for x in nums)
    _show(f"Результат ({len(nums)} чисел):", nums_str)


def _run_playfair(text):
    KEY = 'код'
    _sep("9. ШИФР ПЛЕЙФЕРА")
    print(f"Параметры: ключ = '{KEY}'  (3 уникальных буквы)")
    rep = _playfair.replace(text)
    with _quiet():
        enc = _playfair.playfer(rep, False, True, KEY)
    if enc:
        print(f"Открытый текст ({len(text)} симв.): {text}")
        _show("Шифртекст:", _playfair.format5(enc))
    else:
        print("Ошибка шифрования")


def _run_cardano(text):
    _sep("10. ПОВОРОТНАЯ РЕШЕТКА КАРДАНО")
    print("Параметры: фиксированная решетка 6×10, 14 отверстий → 56 символов/блок")
    clean = _cardano.clean_final(_cardano.replace_punctuation(text))
    CHUNK = 56
    parts = []
    for i in range(0, len(clean), CHUNK):
        parts.append(_cardano.encrypt(clean[i:i + CHUNK]))
    enc = ''.join(parts)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"После очистки: {len(clean)} симв.,  блоков: {len(parts)}")
    _show("Шифртекст:", enc)


def _run_feistel(text):
    KEY_HEX = 'ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff'
    _sep("11. СЕТЬ ФЕЙСТЕЛЯ (ГОСТ 28147-89)")
    print(f"Параметры: ключ (256-бит) = {KEY_HEX[:32]}…{KEY_HEX[-8:]}")
    key = int(KEY_HEX, 16)
    rk = _feistel._key_schedule(key)
    alph = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    tb = bytes([alph.index(c) + 1 for c in text.lower() if c in alph])
    if len(tb) % 8:
        tb += b'\x00' * (8 - len(tb) % 8)
    enc_blocks = []
    for i in range(0, len(tb), 8):
        blk = tb[i:i + 8]
        a1 = int.from_bytes(blk[:4], 'big')
        a0 = int.from_bytes(blk[4:], 'big')
        for j in range(31):
            a1, a0 = _feistel.G(rk[j], a1, a0)
        a1, a0 = _feistel.G_star(rk[31], a1, a0)
        enc_blocks.append(f"{(a1 << 32) | a0:016X}")
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"Байт: {len(tb)},  блоков × 64 бит: {len(enc_blocks)}")
    _show("Результат (hex):", ' '.join(enc_blocks))


def _run_vertical(text):
    KEY = 'КОД'
    _sep("12. ВЕРТИКАЛЬНАЯ ПЕРЕСТАНОВКА")
    print(f"Параметры: ключ = '{KEY}'  → порядок столбцов: К=2, О=3, Д=1 → [Д К О]")
    with _quiet():
        enc = _vertical.vertical_permutation_logic(text, KEY, 'encrypt')
    print(f"Открытый текст ({len(text)} симв.): {text}")
    _show("Шифртекст:", enc)


def _run_shannon(text):
    A, C, T0 = 5, 3, 1
    _sep("13. ОДНОРАЗОВЫЙ БЛОКНОТ ШЕННОНА (ЛКГ)")
    print(f"Параметры: a={A}, c={C}, T0={T0}")
    print(f"  γ₀=(5×1+3)%32=8,  γ₁=(5×8+3)%32=11,  γ₂=(5×11+3)%32=26, …")
    text_clean = ''.join(c for c in text.lower() if c in _shannon.ALPHABET)
    text_nums = _shannon.text_to_numbers(text_clean)
    n = len(text_nums)
    gamma = [0] * n
    if n > 0:
        gamma[0] = (A * T0 + C) % 32
        for i in range(1, n):
            gamma[i] = (A * gamma[i - 1] + C) % 32
    res = []
    for i in range(n):
        s = (text_nums[i] + gamma[i]) % 32
        res.append(s if s != 0 else 32)
    out = _shannon.format_numbers(res)
    gamma_str = ' '.join(f"{g:02d}" for g in gamma)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    _show(f"Гамма ({n} чисел):", gamma_str)
    _show(f"Шифртекст ({n} чисел):", out)


def _run_gamma(text):
    KEY_HEX = 'ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff'
    IV_HEX  = '0000000000000001'
    _sep("14. ГАММИРОВАНИЕ МАГМА CTR (ГОСТ Р 34.13-2015)")
    print(f"Параметры: ключ (256-бит) = {KEY_HEX[:32]}…{KEY_HEX[-8:]}")
    print(f"  IV (синхропосылка) = {IV_HEX}")
    key = int(KEY_HEX, 16)
    rk  = _gamma._key_schedule(key)
    iv  = int(IV_HEX, 16)
    alph = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    tb = bytes([alph.index(c) + 1 for c in text.lower() if c in alph])
    if len(tb) % 8:
        tb += b'\x00' * (8 - len(tb) % 8)
    result = bytearray()
    ctr = iv
    for i in range(0, len(tb), 8):
        block = tb[i:i + 8]
        enc_ctr = _gamma.encrypt_64bit_block(ctr, rk)
        for j, b in enumerate(block):
            result.append(b ^ ((enc_ctr >> (56 - 8 * j)) & 0xFF))
        ctr = (ctr + 1) & ((1 << 64) - 1)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"Байт: {len(tb)},  блоков × 64 бит: {len(tb) // 8}")
    _show("Результат (hex):", result.hex().upper())


def _run_a51(text):
    KEY = 0x0123456789ABCDEF
    _sep("15. A5/1")
    print(f"Параметры: ключ = 0x{KEY:016X}")
    proc = _a51.replace(text.lower())
    bits = _a51.text_to_bits(proc)
    with _quiet():
        cipher = _a51.A5_1(KEY)
    gamma = cipher.get_keystream(len(bits))
    res_bits = [bits[i] ^ gamma[i] for i in range(len(bits))]
    enc = _a51.bits_to_text(res_bits)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"Бит обработано: {len(bits)}")
    _show("Шифртекст:", enc)


def _run_a52(text):
    KEY = 0x0123456789ABCDEF
    _sep("16. A5/2")
    print(f"Параметры: ключ = 0x{KEY:016X}")
    proc = _a52.replace(text.lower())
    bits = _a52.text_to_bits(proc)
    cipher = _a52.A5_2(KEY)
    gamma = cipher.get_keystream(len(bits))
    res_bits = [bits[i] ^ gamma[i] for i in range(len(bits))]
    enc = _a52.bits_to_text(res_bits)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"Бит обработано: {len(bits)}")
    _show("Шифртекст:", enc)


def _run_aes(text):
    KEY_HEX = '000102030405060708090a0b0c0d0e0f'
    _sep("17. AES (FIPS-197)")
    print(f"Параметры: ключ = {KEY_HEX}  (128-бит)")
    key = bytes.fromhex(KEY_HEX)
    tb = text.encode('cp1251')
    if len(tb) % 16:
        tb += b'\x00' * (16 - len(tb) % 16)
    res = b''.join(_aes.aes_encrypt(tb[i:i + 16], key) for i in range(0, len(tb), 16))
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"Байт: {len(tb)},  блоков × 128 бит: {len(tb) // 16}")
    _show("Результат (hex):", res.hex().upper())


def _run_kuznyechik(text):
    if _kuz is None:
        print("  [ПРОПУСК] Кузнечик: модуль недоступен"); return
    KEY_HEX = '8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef'
    _sep("18. КУЗНЕЧИК (ГОСТ Р 34.12-2015)")
    print(f"Параметры: ключ (256-бит) = {KEY_HEX[:32]}…{KEY_HEX[-8:]}")
    cipher = _kuz.Kuznyechik(bytes.fromhex(KEY_HEX))
    tb = text.encode('cp1251')
    if len(tb) % 16:
        tb += b'\x00' * (16 - len(tb) % 16)
    res = b''.join(cipher.encrypt_block(tb[i:i + 16]) for i in range(0, len(tb), 16))
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"Байт: {len(tb)},  блоков × 128 бит: {len(tb) // 16}")
    _show("Результат (hex):", res.hex().upper())


def _run_magma(text):
    if _magma is None:
        print("  [ПРОПУСК] Магма: модуль недоступен"); return
    KEY_HEX = 'ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff'
    _sep("19. МАГМА (ГОСТ Р 34.12-2015)")
    print(f"Параметры: ключ (256-бит) = {KEY_HEX[:32]}…{KEY_HEX[-8:]}")
    cipher = _magma.Magma(bytes.fromhex(KEY_HEX))
    tb = text.encode('cp1251')
    if len(tb) % 8:
        tb += b'\x00' * (8 - len(tb) % 8)
    res = b''.join(cipher.encrypt_block(tb[i:i + 8]) for i in range(0, len(tb), 8))
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"Байт: {len(tb)},  блоков × 64 бит: {len(tb) // 8}")
    _show("Результат (hex):", res.hex().upper())


def _run_rsa(text):
    P, Q, E = 37, 41, 7
    N = P * Q
    D = pow(E, -1, (P - 1) * (Q - 1))
    ALPH = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    _sep("20. RSA")
    print(f"Параметры: P={P}, Q={Q}, E={E}")
    print(f"  N={N},  φ(N)={(P-1)*(Q-1)},  D={D}")
    print(f"  Проверка: E×D = {E}×{D} = {E*D} = {E*D // ((P-1)*(Q-1))}×φ(N)+1 ✓")
    print(f"  Пример: m=2 (Б) → c = 2⁷ mod {N} = {pow(2, E, N)}")
    proc = _rsa.replace(text)
    parts = []
    for ch in proc:
        if ch not in ALPH:
            continue
        m = ALPH.index(ch) + 1
        parts.append(str(pow(m, E, N)).zfill(len(str(N))))
    # Разбиваем блоки пробелами по 4 для читаемости
    grouped = ' '.join(parts[i] + ' ' + parts[i+1] if i+1 < len(parts) else parts[i]
                       for i in range(0, len(parts), 2))
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"Символов зашифровано: {len(parts)}")
    _show("Шифртекст:", grouped)


def _run_elgamal(text):
    p, g, x = 37, 2, 5
    y = pow(g, x, p)
    k_list = [k for k in range(2, p - 1) if math.gcd(k, p - 1) == 1]
    random.seed(42)
    ALPH = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    _sep("21. ШИФР ЭЛЬ-ГАМАЛЬ")
    print(f"Параметры: p={p}, g={g}, x={x}")
    print(f"  y = {g}^{x} mod {p} = {y}")
    print(f"  Пример k=3: a=2³ mod 37=8,  b=y³×m mod 37")
    proc = _elgamal.replace(text)
    res = _elgamal.encrypt(proc, p, g, y, k_list)
    cnt = sum(1 for c in proc if c in ALPH)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"Символов зашифровано: {cnt}")
    _show("Шифртекст:", res)


def _run_ecc(text):
    a_c, b_c, p_c = 1, 1, 23
    G_pt = (1, 7)
    cb, k = 7, 3
    ALPH = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    _sep("22. ЭКЦ (ЭЛЛИПТИЧЕСКИЕ КРИВЫЕ)")
    print(f"Параметры: y² = x³ + {a_c}x + {b_c}  mod {p_c}")
    print(f"  G = {G_pt},  секр. ключ cb = {cb},  эфемерный k = {k}")
    Db = _ecc.scalar_mult(cb, G_pt, a_c, p_c)
    R  = _ecc.scalar_mult(k,  G_pt, a_c, p_c)
    Pp = _ecc.scalar_mult(k,  Db,   a_c, p_c)
    print(f"  Открытый ключ Db = {Db},  R = {R},  P = {Pp}")
    if not Pp:
        print("Ошибка: точка P = None"); return
    prep = _ecc.replace_special_chars(text)
    e_vals = []
    for ch in prep:
        if ch not in ALPH:
            continue
        m = ALPH.index(ch) + 1
        e_vals.append((m * Pp[0]) % p_c)
    e_str = ' '.join(str(v) for v in e_vals)
    print(f"Открытый текст ({len(text)} симв.): {text}")
    print(f"Символов зашифровано: {len(e_vals)}")
    _show("e-значения:", e_str)


# ─── Сводная таблица ключей ──────────────────────────────────────────────────
def _print_keys_table():
    print("\n" + "═" * 64)
    print("  СВОДНАЯ ТАБЛИЦА КЛЮЧЕЙ (для отчёта)")
    print("═" * 64)
    rows = [
        ("Атбаш",              "—  (ключ не нужен)"),
        ("Цезарь",             "сдвиг = 3"),
        ("Квадрат Полибия",    "—  (ключ не нужен)"),
        ("S-блоки",            "—  (таблицы ГОСТ)"),
        ("Тритемиус",          "—  (сдвиг = позиция)"),
        ("Шифр Белазо",        "ключ = 'зонд'  (циклически повторяется)"),
        ("Виженер",            "нач. буква = 'б', самоключ откр.текста"),
        ("Хилл",               "K=[[1,0,1],[0,1,0],[0,0,1]], det=1"),
        ("Плейфер",            "ключ = 'код'"),
        ("Кардано",            "фиксированная решётка (14 отв.)"),
        ("Фейстель",           "ключ = FFEEDDCC…FCFDFEFF  (256-бит ГОСТ)"),
        ("Верт. перестановка", "ключ = 'КОД'"),
        ("Шеннон ЛКГ",         "a=5, c=3, T0=1  →  γ₀=8, γ₁=11, γ₂=26"),
        ("Гаммирование CTR",   "ключ = FFEEDDCC…FCFDFEFF, IV=0000000000000001"),
        ("A5/1",               "ключ = 0x0123456789ABCDEF  (64-бит)"),
        ("A5/2",               "ключ = 0x0123456789ABCDEF  (64-бит)"),
        ("AES",                "ключ = 000102030405060708090A0B0C0D0E0F  (128-бит)"),
        ("Кузнечик",           "ключ = 8899AABB…89ABCDEF  (256-бит ГОСТ)"),
        ("Магма",              "ключ = FFEEDDCC…FCFDFEFF  (256-бит ГОСТ)"),
        ("RSA",                "P=37, Q=41, E=7, N=1517, D=823"),
        ("Эль-Гамаль",         "p=37, g=2, x=5, y=32  (random.seed=42)"),
        ("ЭКЦ",                "a=1,b=1,p=23, G=(1,7), cb=7, k=3"),
    ]
    for name, params in rows:
        print(f"  {name:<22} {params}")
    print("═" * 64)


# ─── Общий прогон через все алгоритмы ────────────────────────────────────────
_RUNNERS = [
    _run_atbash,  _run_caesar,    _run_polybius,
    _run_sblock,  _run_trithemius,_run_belaso,   _run_vigenere,
    _run_hill,    _run_playfair,  _run_cardano,
    _run_feistel, _run_vertical,  _run_shannon,  _run_gamma,
    _run_a51,     _run_a52,
    _run_aes,     _run_kuznyechik,_run_magma,
    _run_rsa,     _run_elgamal,   _run_ecc,
]


def run_all(text, title):
    print("\n" + "═" * 64)
    print(f"  {title}")
    print("═" * 64)
    print(f"\nТекст ({len(text)} символов):")
    print(f"  «{text}»")

    _print_keys_table()

    for fn in _RUNNERS:
        try:
            fn(text)
        except Exception as e:
            import traceback
            print(f"  [ОШИБКА в {fn.__name__}]: {e}")
            traceback.print_exc()

    _sep()
    print("\nЭлектронная подпись (Лаб 9–10) и Диффи-Хеллман (Лаб 11)")
    print("  ► Не являются шифрами текста — запустите через меню (пп. 21–25).")
    _sep()
    print("\nПрогон завершён.")


# ─── Меню алгоритмов ─────────────────────────────────────────────────────────
ALGORITHMS = [
    ("Атбаш",                            "lab1_atbash.py",                "Лаб 1"),
    ("Цезарь",                           "lab1_chesar.py",                "Лаб 1"),
    ("Квадрат Полибия",                  "lab1_polyb.py",                 "Лаб 1"),
    ("S-блоки (ГОСТ/Магма)",             "lab2_s_block.py",               "Лаб 2"),
    ("Шифр Тритемиуса",                  "lab2_trithemius.py",            "Лаб 2"),
    ("Шифр Белазо",                      "lab2_belaso.py",                "Лаб 2"),
    ("Шифр Виженера",                    "lab2_vigenere.py",              "Лаб 2"),
    ("Матричный шифр Хилла",             "lab3_matrix.py",                "Лаб 3"),
    ("Шифр Плейфера",                    "lab3_pleifer.py",               "Лаб 3"),
    ("Поворотная решётка Кардано",       "lab4_cardano.py",               "Лаб 4"),
    ("Сеть Фейстеля (ГОСТ 28147-89)",    "lab4_feistel.py",               "Лаб 4"),
    ("Вертикальная перестановка",        "lab4_vertical.py",              "Лаб 4"),
    ("Одноразовый блокнот Шеннона",      "lab5_shanon.py",                "Лаб 5"),
    ("Гаммирование Магма CTR (ГОСТ Р 34.13-2015)", "lab5_gamma.py",      "Лаб 5"),
    ("A5/1",                             "lab6_a5-1.py",                  "Лаб 6"),
    ("A5/2",                             "lab6_a5-2.py",                  "Лаб 6"),
    ("AES (FIPS-197)",                   "lab7_aes.py",                   "Лаб 7"),
    ("Кузнечик (ГОСТ Р 34.12-2015)",     "lab7_kyznechik.py",             "Лаб 7"),
    ("Магма (ГОСТ Р 34.12-2015)",        "lab7_magma.py",                 "Лаб 7"),
    ("RSA",                              "lab8_rsa.py",                   "Лаб 8"),
    ("Эль-Гамаль",                       "lab8_elgamal.py",               "Лаб 8"),
    ("ЭКЦ — Эллиптические кривые",       "lab8_ecc.py",                   "Лаб 8"),
    ("Подпись Эль-Гамаль",               "lab9_elgamal_dig_signature.py", "Лаб 9"),
    ("Подпись RSA",                      "lab9_rsa_dig_signature.py",     "Лаб 9"),
    ("ГОСТ Р 34.10-94",                  "lab10_gost94.py",               "Лаб 10"),
    ("ГОСТ Р 34.10-2012 (ЭКЦ)",          "lab10_gost2012.py",             "Лаб 10"),
    ("Диффи-Хеллман",                    "lab11_diffie_hellman.py",       "Лаб 11"),
]


def print_menu():
    print("\n" + "═" * 64)
    print("       КРИПТОГРАФИЧЕСКАЯ СИСТЕМА — МосПолитех")
    print("═" * 64)
    groups = [
        ("── Симметричные шифры ──",   range(0, 19)),
        ("── Асимметричные шифры ──",  range(19, 22)),
        ("── Электронная подпись ──",  range(22, 26)),
        ("── Протоколы ──",            range(26, 27)),
    ]
    for title, rng in groups:
        print(f"\n  {title}")
        for i in rng:
            name, _, lab = ALGORITHMS[i]
            print(f"  {i + 1:>2}. {name:<46} [{lab}]")
    print()
    print("   P. Прогнать пословицу через все алгоритмы")
    print(f"      ({PROVERB})")
    print("   T. Тест 1000 символов (пословица × 18)")
    print("   K. Таблица ключей для отчёта")
    print("   0. Выход")
    print("─" * 64)


def main():
    while True:
        print_menu()
        choice = input("Выберите: ").strip().lower()

        if choice == '0':
            print("До свидания!")
            break
        elif choice == 'p':
            run_all(PROVERB, "ПРОГОН ПОСЛОВИЦЫ ЧЕРЕЗ ВСЕ АЛГОРИТМЫ")
            input("\nНажмите Enter для возврата в меню...")
        elif choice == 't':
            run_all(PROVERB_1000, "ТЕСТ 1000 СИМВОЛОВ ЧЕРЕЗ ВСЕ АЛГОРИТМЫ")
            input("\nНажмите Enter для возврата в меню...")
        elif choice == 'k':
            _print_keys_table()
            input("\nНажмите Enter для возврата в меню...")
        else:
            try:
                idx = int(choice) - 1
            except ValueError:
                print("Неверный ввод.")
                continue
            if idx < 0 or idx >= len(ALGORITHMS):
                print("Неверный номер.")
                continue
            name, filename, lab = ALGORITHMS[idx]
            # Check if module failed to load (numpy-dependent ones)
            _mod_map = {
                "lab3_matrix.py": (_hill,    "numpy"),
                "lab7_kyznechik.py": (_kuz,  "numpy/pycryptodome"),
                "lab7_magma.py": (_magma,    "numpy/pycryptodome"),
            }
            if filename in _mod_map:
                mod_ref, dep = _mod_map[filename]
                if mod_ref is None:
                    print(f"  ОШИБКА: {name} недоступен ({dep} не установлен)")
                    input("\nНажмите Enter для возврата в меню...")
                    continue
            print(f"\n>>> Запускается: {name}  [{lab}]")
            print("    (для выхода используйте опцию выхода программы)\n")
            _launch(filename)
            input("\nНажмите Enter для возврата в меню...")


if __name__ == "__main__":
    main()
