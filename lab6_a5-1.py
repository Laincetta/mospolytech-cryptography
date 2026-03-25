from distutils.command.register import register

test = "Плохой работник никогда не находит хорошего инструмента."

alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

def replace(text):
    replacements = {
        '.': 'тчк',
        '—': 'тире',
        '-': 'тире',
        ',': 'зпт',
        '!': 'вскл',
        '?': 'впрс',
        '«': 'квчл',
        '»': 'квчп',
        ' ': 'прб'
    }
    result = ""
    for i in text:
        result += replacements.get(i, i)
    return result

def restore(text):
    replacements = [
        ('тчк', '.'),
        ('тире', '—'),
        ('зпт', ','),
        ('вскл', '!'),
        ('впрс', '?'),
        ('квчл', '«'),
        ('квчп', '»'),
        ('прб', ' ')
    ]
    result = text
    for code, symbol in replacements:
        result = result.replace(code, symbol)
    return result


class Register:
    def __init__(self, length, feedback, sync_bit, mask):
        self.length = length
        self.feedback = feedback
        self.sync_bit = sync_bit
        self.mask = mask
        self.reg = 0

    def get_clock_bit(self):
        return (self.reg >> self.sync_bit) & 1

    def shift(self, injecting_bit=0):
        fb = 0
        for fb_inx in self.feedback:
            fb ^= (self.reg >> fb_inx) & 1
        new_bit = fb ^ injecting_bit
        self.reg = ((self.reg << 1) | new_bit) & self.mask

    def log_register(self, iter, reg_number):
        print(f"Регистр {reg_number}\nНомер такта: {iter}\nЗначение: {self.reg}")


class A5_1:
    def __init__(self, key_int, frame_number=0):
        self.r1 = Register(19, [13, 16, 17, 18], 8, 0x7FFFF)
        self.r2 = Register(22, [20, 21], 10, 0x3FFFFF)
        self.r3 = Register(23, [7, 20, 21, 22], 10, 0x7FFFFF)

        for i in range(64):
            bit = (key_int >> i) & 1
            self.r1.shift(bit)
            self.r2.shift(bit)
            self.r3.shift(bit)
            self.r1.log_register(i, 1)
            self.r2.log_register(i, 2)
            self.r3.log_register(i, 3)

        for i in range(22):
            bit = (frame_number >> i) & 1
            self.r1.shift(bit)
            self.r2.shift(bit)
            self.r3.shift(bit)

        for _ in range(100):
            self.clock_with_majority()

    def clock_with_majority(self, generate_gamma_bit=False):
        c1 = self.r1.get_clock_bit()
        c2 = self.r2.get_clock_bit()
        c3 = self.r3.get_clock_bit()
        maj = (c1 & c2) | (c1 & c3) | (c2 & c3)
        if c1 == maj: self.r1.shift()
        if c2 == maj: self.r2.shift()
        if c3 == maj: self.r3.shift()
        if generate_gamma_bit:
            return ((self.r1.reg >> 18) ^ (self.r2.reg >> 21) ^ (self.r3.reg >> 22)) & 1
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

    processed_msg = replace(message)
    msg_bits = text_to_bits(processed_msg)

    print(f"\nДвоичный код: {''.join(map(str, msg_bits))}")

    cipher = A5_1(key_int)
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
    print("\n=== A5/1 ===")
    print("1. Зашифровать\n2. Расшифровать\n0. Выход")
    ch = input(">> ")
    if ch == '1':
        run_menu("ШИФРОВАНИЕ")
    elif ch == '2':
        run_menu("РАСШИФРОВАНИЕ")
    elif ch == '0':
        break