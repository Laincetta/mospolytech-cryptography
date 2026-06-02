"""
Блок F: ПОТОЧНЫЕ ШИФРЫ
16. А5/2  (ЛАБКРИПТ_2022)

Развитие A5/1: добавлен четвёртый регистр R4 (17 бит), который УПРАВЛЯЕТ
тактированием R1, R2, R3. Регистры и многочлены обратной связи:
    R1 — 19 бит: x^19+x^18+x^17+x^14+1,
    R2 — 22 бита: x^22+x^21+1,
    R3 — 23 бита: x^23+x^22+x^21+x^8+1,
    R4 — 17 бит: x^17+x^12+1.
Тактирование: F = majority(R4[3], R4[7], R4[10]); R1 сдвигается если R4[10]=F,
R2 — если R4[3]=F, R3 — если R4[7]=F; R4 сдвигается каждый такт.
Выходной бит = XOR старших битов R1[18],R2[21],R3[22] и мажоритарных функций
определённых битов: R1(12,14,15), R2(9,13,16), R3(13,16,18).
Символы текста и гаммы складываются по модулю 2 (XOR).
"""

alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"


def replace(text):
    replacements = {'.': 'тчк', '—': 'тире', '-': 'тире', ',': 'зпт', '!': 'вскл',
                    '?': 'впрс', '«': 'квчл', '»': 'квчп', ' ': 'прб'}
    return ''.join(replacements.get(c, c) for c in text)


def restore(text):
    replacements = [('тчк', '.'), ('тире', '—'), ('зпт', ','), ('вскл', '!'),
                    ('впрс', '?'), ('квчл', '«'), ('квчп', '»'), ('прб', ' ')]
    for code, symbol in replacements:
        text = text.replace(code, symbol)
    return text


class Register:
    """РСЛОС: биты хранятся в целом числе, разряд 0 — младший."""

    def __init__(self, length, feedback, mask):
        self.length = length
        self.feedback = feedback     # позиции битов обратной связи
        self.mask = mask
        self.reg = 0

    def bit(self, pos):
        return (self.reg >> pos) & 1

    def shift(self, injecting_bit=0):
        fb = 0
        for fb_inx in self.feedback:
            fb ^= (self.reg >> fb_inx) & 1
        new_bit = fb ^ injecting_bit
        self.reg = ((self.reg << 1) | new_bit) & self.mask

    def msb(self):
        return (self.reg >> (self.length - 1)) & 1


def majority(x, y, z):
    return (x & y) | (x & z) | (y & z)


class A5_2:
    def __init__(self, key_int, frame_number=0):
        self.r1 = Register(19, [13, 16, 17, 18], 0x7FFFF)
        self.r2 = Register(22, [20, 21], 0x3FFFFF)
        self.r3 = Register(23, [7, 20, 21, 22], 0x7FFFFF)
        self.r4 = Register(17, [11, 16], 0x1FFFF)

        # 1) загрузка сеансового ключа (64 такта) — тактируются все 4 регистра
        for i in range(64):
            bit = (key_int >> i) & 1
            self._clock_all(bit)
        # 2) загрузка номера кадра (22 такта)
        for i in range(22):
            bit = (frame_number >> i) & 1
            self._clock_all(bit)
        # 3) принудительно ставим биты R4(3), R4(7), R4(10) = 1
        for p in (3, 7, 10):
            self.r4.reg |= (1 << p)
        # 4) 99 тактов с управлением сдвигами (без выдачи гаммы)
        for _ in range(99):
            self.clock_controlled()

    def _clock_all(self, bit):
        self.r1.shift(bit); self.r2.shift(bit)
        self.r3.shift(bit); self.r4.shift(bit)

    def clock_controlled(self, generate_gamma_bit=False):
        f = majority(self.r4.bit(3), self.r4.bit(7), self.r4.bit(10))
        if self.r4.bit(10) == f: self.r1.shift()
        if self.r4.bit(3) == f:  self.r2.shift()
        if self.r4.bit(7) == f:  self.r3.shift()
        out = self._out_bit() if generate_gamma_bit else None
        self.r4.shift()
        return out

    def _out_bit(self):
        return (self.r1.msb() ^ self.r2.msb() ^ self.r3.msb()
                ^ majority(self.r1.bit(12), self.r1.bit(14), self.r1.bit(15))
                ^ majority(self.r2.bit(9), self.r2.bit(13), self.r2.bit(16))
                ^ majority(self.r3.bit(13), self.r3.bit(16), self.r3.bit(18)))

    def get_keystream(self, length):
        return [self.clock_controlled(generate_gamma_bit=True) for _ in range(length)]


def text_to_bits(text):
    bits = []
    for char in text.lower().replace('ё', 'е'):
        if char in alphabet:
            idx = alphabet.index(char)
            bits.extend([(idx >> i) & 1 for i in range(4, -1, -1)])
    return bits


def bits_to_text(bits):
    text = ""
    for i in range(0, len(bits), 5):
        chunk = bits[i:i + 5]
        if len(chunk) < 5:
            break
        idx = 0
        for bit in chunk:
            idx = (idx << 1) | bit
        text += alphabet[idx % 32]
    return text


def run_menu(mode):
    print(f"\n--- {mode} ---")
    print("1. Слово\n2. HEX")
    k_type = input("Тип ключа: ")
    raw_key = input("Ключ: ")

    if k_type == '2':
        key_int = int(raw_key, 16)
    else:
        k_bits = text_to_bits(raw_key)
        if len(k_bits) > 64:
            print("ОШИБКА: Ключ превышает 64 бита!")
            return
        key_int = 0
        for b in k_bits:
            key_int = (key_int << 1) | b

    if key_int > 0xFFFFFFFFFFFFFFFF:
        print("ОШИБКА: Ключ превышает 64 бита!")
        return

    message = input("Текст: ")
    processed_msg = replace(message) if mode == "ШИФРОВАНИЕ" else message
    msg_bits = text_to_bits(processed_msg)

    print(f"\nДвоичный код: {''.join(map(str, msg_bits))}")

    cipher = A5_2(key_int)
    gamma = cipher.get_keystream(len(msg_bits))
    print(f"Гамма:        {''.join(map(str, gamma))}")

    res_bits = [msg_bits[i] ^ gamma[i] for i in range(len(msg_bits))]
    print(f"Результат:    {''.join(map(str, res_bits))}")

    final_text = bits_to_text(res_bits)
    if mode == "РАСШИФРОВАНИЕ":
        print(f"\nИТОГ: {restore(final_text)}")
    else:
        print(f"\nИТОГ: {final_text}")


def main():
    while True:
        print("\n=== A5/2 ===")
        print("1. Зашифровать\n2. Расшифровать\n0. Выход")
        ch = input(">> ")
        if ch == '1':
            run_menu("ШИФРОВАНИЕ")
        elif ch == '2':
            run_menu("РАСШИФРОВАНИЕ")
        elif ch == '0':
            break


if __name__ == "__main__":
    main()
