import struct

# Таблица нелинейного преобразования (S-блок)
PI = [
    252, 238, 221, 17, 207, 110, 49, 22, 251, 196, 250, 218, 35, 197, 4, 77,
    233, 119, 240, 219, 147, 46, 153, 186, 23, 54, 241, 187, 20, 205, 95, 193,
    249, 24, 101, 90, 226, 92, 239, 33, 129, 28, 60, 66, 139, 1, 142, 79,
    5, 132, 2, 174, 227, 106, 143, 160, 6, 11, 237, 152, 127, 212, 211, 31,
    235, 52, 44, 81, 234, 200, 72, 171, 242, 42, 104, 162, 253, 58, 206, 204,
    181, 112, 14, 86, 8, 12, 118, 18, 191, 114, 19, 71, 156, 183, 93, 135,
    21, 161, 150, 41, 16, 123, 154, 199, 243, 145, 120, 111, 157, 158, 178, 177,
    50, 117, 25, 61, 255, 53, 138, 126, 109, 84, 198, 128, 195, 189, 13, 87,
    223, 245, 36, 169, 62, 168, 67, 201, 215, 121, 214, 246, 124, 34, 185, 3,
    224, 15, 236, 222, 122, 148, 176, 188, 220, 232, 40, 80, 78, 51, 10, 74,
    167, 151, 96, 115, 30, 0, 98, 68, 26, 184, 56, 130, 100, 159, 38, 65,
    173, 69, 70, 146, 39, 94, 85, 47, 140, 163, 165, 125, 105, 213, 149, 59,
    7, 88, 179, 64, 134, 172, 29, 247, 48, 55, 107, 228, 136, 217, 231, 137,
    225, 27, 131, 73, 76, 63, 248, 254, 141, 83, 170, 144, 202, 216, 133, 97,
    32, 113, 103, 164, 45, 43, 9, 91, 203, 155, 37, 208, 190, 229, 108, 82,
    89, 166, 116, 210, 230, 244, 180, 192, 209, 102, 175, 194, 57, 75, 99, 182
]

PI_INV = [0] * 256
for i, v in enumerate(PI): PI_INV[v] = i

# Вектор коэффициентов для линейного преобразования L
L_VEC = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]


def gf_mul(a, b):
    """Умножение двух чисел в поле Галуа GF(2^8) по модулю 0x1C3."""
    res = 0
    for _ in range(8):
        if b & 1: res ^= a
        a <<= 1
        if a & 0x100: a ^= 0x1C3
        b >>= 1
    return res & 0xFF


class Kuznyechik:
    def __init__(self, key: bytes):
        # Развертывание ключа: создание 10 раундовых ключей из одного 32-байтного
        self.keys = self._expand_key(key)

    def _X(self, a, b):
        """Преобразование X: побайтовое сложение по модулю 2 (XOR)."""
        return bytes(x ^ y for x, y in zip(a, b))

    def _S(self, data):
        """Преобразование S: нелинейная замена каждого байта по таблице PI."""
        return bytes(PI[x] for x in data)

    def _S_inv(self, data):
        """Обратное преобразование S (для расшифровки)."""
        return bytes(PI_INV[x] for x in data)

    def _L(self, data):
        """Линейное преобразование L: перемешивание байтов на основе LFSR."""
        state = list(data)
        for _ in range(16):
            s = 0
            for i in range(16):
                s ^= gf_mul(state[i], L_VEC[i])
            state = [s] + state[:-1]
        return bytes(state)

    def _L_inv(self, data):
        """Обратное линейное преобразование L (для расшифровки)."""
        state = list(data)
        for _ in range(16):
            # В L_inv мы восстанавливаем "выпавший" байт
            s = state[0]
            for i in range(1, 16):
                s ^= gf_mul(state[i], L_VEC[i - 1])
            state = state[1:] + [s]
        return bytes(state)

    def _expand_key(self, key):
        """Генерация 10 итерационных ключей."""
        k = [key[:16], key[16:]]
        # Константы C получаются применением L к номеру итерации (в младшем байте)
        c = [self._L(bytes([0] * 15 + [i])) for i in range(1, 33)]

        for i in range(4):
            a1, a0 = k[2 * i], k[2 * i + 1]
            for j in range(8):
                # Сеть Фейстеля для вычисления новых ключей
                tmp = self._L(self._S(self._X(a1, c[i * 8 + j])))
                a1, a0 = self._X(tmp, a0), a1
            k.extend([a1, a0])
        return k

    def encrypt_block(self, block):
        """Шифрование одного блока (16 байт) — 9 раундов S, L, X + финальный X."""
        for i in range(9):
            block = self._L(self._S(self._X(block, self.keys[i])))
        return self._X(block, self.keys[9])

    def decrypt_block(self, block):
        """Расшифрование одного блока — обратные операции в обратном порядке."""
        block = self._X(block, self.keys[9])
        for i in reversed(range(9)):
            block = self._S_inv(self._L_inv(block))
            block = self._X(block, self.keys[i])
        return block


def main():
    # 1122334455667700ffeeddccbbaa998800112233445566778899aabbcceeff0a112233445566778899aabbcceeff0a002233445566778899aabbcceeff0a0011

    print("=" * 45)
    print("   ГОСТ Р 34.12-2015 КУЗНЕЧИК (ECB РЕЖИМ)")
    print("=" * 45)

    # ключ из документации ГОСТ
    default_key = "8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef"
    key_input = input(f"Введите ключ (hex) [Enter для теста]: ").strip().replace(" ", "")

    key = bytes.fromhex(key_input if key_input else default_key)
    cipher = Kuznyechik(key)

    while True:
        print("\n--- МЕНЮ ---")
        print("1. Зашифровать (hex)")
        print("2. Расшифровать (hex)")
        print("0. Выход")

        choice = input("Выбор: ").strip()
        if choice == '0': break
        if choice not in ('1', '2'): continue

        data_hex = input("Введите данные в hex: ").strip().replace(" ", "")
        try:
            data = bytes.fromhex(data_hex)
            if len(data) % 16 != 0:
                print("(!) Внимание: Длина данных не кратна 16 байтам (блоку).")
                # В ECB режиме данные должны быть кратны блоку

            result = b""
            for i in range(0, len(data), 16):
                block = data[i:i + 16]
                if len(block) < 16: break  # Пропускаем неполный блок для простоты

                if choice == '1':
                    result += cipher.encrypt_block(block)
                else:
                    result += cipher.decrypt_block(block)

            print(f"РЕЗУЛЬТАТ: {result.hex()}")
        except ValueError:
            print("Ошибка: Некорректный HEX ввод.")


if __name__ == "__main__":
    main()