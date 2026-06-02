# -*- coding: utf-8 -*-
"""
Тестирование A5/1 и A5/2 (мои входные данные).

Здесь только ВХОДНЫЕ ДАННЫЕ + логика генерации гаммы.
Меняй три параметра ниже — KEY_HEX, FRAME, WORD — под себя.
Потом из этого собирается Excel (Лист1 — потактовая трассировка, Лист2 — тест).
"""

# ============================ ВХОДНЫЕ ДАННЫЕ (МОИ) ============================
KEY_HEX = "0F1E2D3C4B5A6978"   # сеансовый ключ, 64 бита (16 hex-цифр)
FRAME   = 0                     # номер кадра Fn, 22 бита (0 = 00000000000000000000 00)
WORD    = "пло"                # первые 3 буквы слова «плохой» (вариант 26)
# =============================================================================

# Алфавит для A5: 32 буквы, 5-битные коды.  А=00000 (0) … Я=11111 (31).
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
assert len(ALPHABET) == 32


def text_to_bits(text):
    """Слово → список бит (по 5 бит на букву, старший бит первым)."""
    bits = []
    for ch in text.lower().replace("ё", "е"):
        if ch in ALPHABET:
            idx = ALPHABET.index(ch)
            bits += [(idx >> i) & 1 for i in range(4, -1, -1)]
    return bits


def bits_to_text(bits):
    """Список бит → слово (по 5 бит на букву)."""
    out = ""
    for i in range(0, len(bits) - 4, 5):
        idx = 0
        for b in bits[i:i + 5]:
            idx = (idx << 1) | b
        out += ALPHABET[idx]
    return out


def key_bits(hex_str):
    """64-битный ключ из hex → 64 бита, младший бит первым (как в программе lab6_a5-1)."""
    n = int(hex_str, 16)
    return [(n >> i) & 1 for i in range(64)]


def frame_bits(fn):
    """Номер кадра → 22 бита, младший бит первым (как в программе lab6_a5-1)."""
    return [(fn >> i) & 1 for i in range(22)]


def majority(a, b, c):
    """Мажоритарная функция (большинство из трёх бит)."""
    return (a & b) | (a & c) | (b & c)


class LFSR:
    """Регистр сдвига с линейной обратной связью (биты хранятся в списке,
    индекс 0 — младший разряд)."""

    def __init__(self, length, taps):
        self.length = length
        self.taps = taps              # позиции битов обратной связи
        self.reg = [0] * length

    def feedback(self):
        fb = 0
        for t in self.taps:
            fb ^= self.reg[t]
        return fb

    def clock(self, inject=0):
        """Один сдвиг: новый младший бит = обратная связь XOR вброшенный бит."""
        new = self.feedback() ^ inject
        self.reg = [new] + self.reg[:-1]

    def msb(self):
        return self.reg[self.length - 1]

    def as_str(self):
        # печать от старшего разряда к младшему
        return "".join(str(b) for b in reversed(self.reg))


# ============================== A5/1 ==============================
class A5_1:
    """Три РСЛОС, тактирование по мажоритарной функции (stop-and-go)."""

    def __init__(self, key_hex, frame):
        self.r1 = LFSR(19, [13, 16, 17, 18])   # x19+x18+x17+x14+1
        self.r2 = LFSR(22, [20, 21])           # x22+x21+1
        self.r3 = LFSR(23, [7, 20, 21, 22])    # x23+x22+x21+x8+1
        self.clk = (8, 10, 10)                 # биты синхронизации R1,R2,R3
        self.trace = []                        # потактовая трассировка
        self.k = 0
        # 1) загрузка ключа (64 такта, все регистры тактируются)
        for b in key_bits(key_hex):
            self._clock_all(b, "ключ")
        # 2) загрузка номера кадра (22 такта)
        for b in frame_bits(frame):
            self._clock_all(b, "кадр")
        # 3) 100 тактов «вхолостую» с мажоритарным тактированием
        for _ in range(100):
            self._clock_majority("холостой")

    def _rec(self, stage, inj, s1, s2, s3, f, sh, out):
        self.k += 1
        self.trace.append(dict(k=self.k, stage=stage, inj=inj,
                               r1=self.r1.as_str(), r2=self.r2.as_str(), r3=self.r3.as_str(),
                               s1=s1, s2=s2, s3=s3, f=f, sh=sh, out=out))

    def _clock_all(self, inject, stage):
        self.r1.clock(inject); self.r2.clock(inject); self.r3.clock(inject)
        self._rec(stage, inject, "", "", "", "", "все", "")

    def _clock_majority(self, stage, emit=False):
        c1 = self.r1.reg[self.clk[0]]
        c2 = self.r2.reg[self.clk[1]]
        c3 = self.r3.reg[self.clk[2]]
        f = majority(c1, c2, c3); sh = []
        if c1 == f: self.r1.clock(); sh.append("R1")
        if c2 == f: self.r2.clock(); sh.append("R2")
        if c3 == f: self.r3.clock(); sh.append("R3")
        out = (self.r1.msb() ^ self.r2.msb() ^ self.r3.msb()) if emit else ""
        self._rec(stage, "", c1, c2, c3, f, " ".join(sh), out)
        return out

    def keystream(self, n):
        return [self._clock_majority("гамма", emit=True) for _ in range(n)]


# ============================== A5/2 ==============================
class A5_2:
    """A5/2: добавлен регистр R4 (17 бит), он управляет тактированием R1,R2,R3.
    Выходной бит — XOR старших битов и мажоритарных функций определённых битов."""

    def __init__(self, key_hex, frame):
        self.r1 = LFSR(19, [13, 16, 17, 18])
        self.r2 = LFSR(22, [20, 21])
        self.r3 = LFSR(23, [7, 20, 21, 22])
        self.r4 = LFSR(17, [11, 16])           # x17+x12+1
        self.trace = []
        self.k = 0
        # 1) ключ и 2) кадр — тактируются все четыре регистра
        for b in key_bits(key_hex):
            self._clock_all(b, "ключ")
        for b in frame_bits(frame):
            self._clock_all(b, "кадр")
        # 3) принудительно ставим биты R4(3),R4(7),R4(10) = 1
        for p in (3, 7, 10):
            self.r4.reg[p] = 1
        # 4) 99 тактов с управлением сдвигами (без выдачи гаммы)
        for _ in range(99):
            self._clock_controlled("холостой")

    def _rec(self, stage, inj, c3b, c7b, c10b, f, sh, out):
        self.k += 1
        self.trace.append(dict(k=self.k, stage=stage, inj=inj,
                               r1=self.r1.as_str(), r2=self.r2.as_str(),
                               r3=self.r3.as_str(), r4=self.r4.as_str(),
                               c3=c3b, c7=c7b, c10=c10b, f=f, sh=sh, out=out))

    def _clock_all(self, inject, stage):
        self.r1.clock(inject); self.r2.clock(inject)
        self.r3.clock(inject); self.r4.clock(inject)
        self._rec(stage, inject, "", "", "", "", "все", "")

    def _clock_controlled(self, stage, emit=False):
        # тактированием управляет R4: биты 3,7,10
        b3, b7, b10 = self.r4.reg[3], self.r4.reg[7], self.r4.reg[10]
        f = majority(b3, b7, b10); sh = []
        if b10 == f: self.r1.clock(); sh.append("R1")
        if b3 == f:  self.r2.clock(); sh.append("R2")
        if b7 == f:  self.r3.clock(); sh.append("R3")
        out = self._out_bit() if emit else ""
        self.r4.clock()
        self._rec(stage, "", b3, b7, b10, f, " ".join(sh), out)
        return out

    def _out_bit(self):
        return (self.r1.msb() ^ self.r2.msb() ^ self.r3.msb()
                ^ majority(self.r1.reg[12], self.r1.reg[14], self.r1.reg[15])
                ^ majority(self.r2.reg[9], self.r2.reg[13], self.r2.reg[16])
                ^ majority(self.r3.reg[13], self.r3.reg[16], self.r3.reg[18]))

    def keystream(self, n):
        return [self._clock_controlled("гамма", emit=True) for _ in range(n)]


def run(name, cipher):
    """Шифрование слова WORD: биты слова XOR гамма → биты шифра → буквы."""
    mbits = text_to_bits(WORD)
    gamma = cipher.keystream(len(mbits))
    cbits = [mbits[i] ^ gamma[i] for i in range(len(mbits))]
    print(f"\n===== {name} =====")
    print(f"ключ:  {KEY_HEX}   кадр: {FRAME}   слово: {WORD}")
    print(f"биты слова: {''.join(map(str, mbits))}")
    print(f"гамма:      {''.join(map(str, gamma))}")
    print(f"шифр:       {''.join(map(str, cbits))}")
    print(f"шифр-буквы: {bits_to_text(cbits)}")
    # проверка обратимостью (тот же XOR с той же гаммой)
    back = [cbits[i] ^ gamma[i] for i in range(len(cbits))]
    print(f"расшифровка: {bits_to_text(back)}  (должно быть '{WORD}')")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    run("A5/1", A5_1(KEY_HEX, FRAME))
    run("A5/2", A5_2(KEY_HEX, FRAME))
