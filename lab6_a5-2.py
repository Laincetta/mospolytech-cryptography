alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"


def replace(text):
    replacements = {
        '.': 'тчк', '—': 'тире', '-': 'тире', ',': 'зпт',
        '!': 'вскл', '?': 'впрс', '«': 'квчл', '»': 'квчп', ' ': 'прб'
    }
    result = ""
    for i in text.lower():
        result += replacements.get(i, i)
    return result


def restore(text):
    replacements = [
        ('тчк', '.'), ('тире', '—'), ('зпт', ','), ('вскл', '!'),
        ('впрс', '?'), ('квчл', '«'), ('квчп', '»'), ('прб', ' ')
    ]
    result = text
    for code, symbol in replacements:
        result = result.replace(code, symbol)
    return result


class Register:
    def __init__(self, length, feedback, mask):
        self.length = length
        self.feedback = feedback
        self.mask = mask
        self.reg = 0

    def shift(self, injecting_bit=0):
        fb = 0
        for fb_inx in self.feedback:
            fb ^= (self.reg >> fb_inx) & 1
        new_bit = fb ^ injecting_bit
        self.reg = ((self.reg << 1) | new_bit) & self.mask


class A5_2:
    def __init__(self, key_int, frame_number=0):
        self.r1 = Register(19, [13, 16, 17, 18], 0x7FFFF)
        self.r2 = Register(22, [20, 21], 0x3FFFFF)
        self.r3 = Register(23, [7, 20, 21, 22], 0x7FFFFF)
        self.r4 = Register(17, [11, 16], 0x1FFFF)

        for i in range(64):
            bit = (key_int >> i) & 1
            self.r1.shift(bit)
            self.r2.shift(bit)
            self.r3.shift(bit)
            self.r4.shift(bit)

        for i in range(22):
            bit = (frame_number >> i) & 1
            self.r1.shift(bit)
            self.r2.shift(bit)
            self.r3.shift(bit)
            self.r4.shift(bit)

        self.r4.reg |= (1 << 3) | (1 << 7) | (1 << 10)

        for _ in range(99):
            self.clock_with_majority()

    def maj(self, x, y, z):
        return (x & y) | (x & z) | (y & z)

    def clock_with_majority(self, generate_gamma_bit=False):
        r4_3 = (self.r4.reg >> 3) & 1
        r4_7 = (self.r4.reg >> 7) & 1
        r4_10 = (self.r4.reg >> 10) & 1

        f = self.maj(r4_3, r4_7, r4_10)

        if ((self.r4.reg >> 10) & 1) == f: self.r1.shift()
        if ((self.r4.reg >> 3) & 1) == f: self.r2.shift()
        if ((self.r4.reg >> 7) & 1) == f: self.r3.shift()

        self.r4.shift()

        if generate_gamma_bit:
            out1 = ((self.r1.reg >> 18) & 1) ^ self.maj((self.r1.reg >> 12) & 1, (self.r1.reg >> 14) & 1,
                                                        (self.r1.reg >> 15) & 1)
            out2 = ((self.r2.reg >> 21) & 1) ^ self.maj((self.r2.reg >> 9) & 1, (self.r2.reg >> 13) & 1,
                                                        (self.r2.reg >> 16) & 1)
            out3 = ((self.r3.reg >> 22) & 1) ^ self.maj((self.r3.reg >> 13) & 1, (self.r3.reg >> 16) & 1,
                                                        (self.r3.reg >> 18) & 1)
            return out1 ^ out2 ^ out3
        return None

    def get_keystream(self, length):
        return [self.clock_with_majority(generate_gamma_bit=True) for _ in range(length)]


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
        if len(chunk) < 5: break
        idx = 0
        for bit in chunk:
            idx = (idx << 1) | bit
        text += alphabet[idx % 32]
    return text


def run_menu(mode):
    print(f"\n--- {mode} (A5/2) ---")
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
        for b in k_bits: key_int = (key_int << 1) | b

    if key_int > 0xFFFFFFFFFFFFFFFF:
        print("ОШИБКА: Ключ превышает 64 бита!")
        return

    message = input("Текст: ")
    processed_msg = replace(message)
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