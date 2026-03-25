import struct

class Magma:
    def __init__(self, key: bytes):
        # Таблица замен (S-блоки). 8 узлов замены, по 16 значений в каждом.
        # Используется для внесения нелинейности в алгоритм.
        self.pi = [
            [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
            [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
            [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
            [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
            [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
            [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
            [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
            [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
        ]
        # Развертывание ключа: создание 32 раундовых ключей
        self.keys = self._key_schedule(key)

    def _key_schedule(self, key):
        """Разбивает 256-битный ключ на восемь 32-битных итерационных ключей.
        Порядок использования: K1..K8, K1..K8, K1..K8, K8..K1 (всего 32)."""
        parts = [struct.unpack(">I", key[i:i + 4])[0] for i in range(0, 32, 4)]
        return parts * 3 + parts[::-1]

    def _g(self, k, a):
        """Функция преобразования (F-функция в сети Фейстеля):
        1. Сложение с ключом по модулю 2^32.
        2. Замена по таблице S-блоков.
        3. Циклический сдвиг влево на 11 бит."""
        # Сложение с ключом
        x = (a + k) & 0xFFFFFFFF
        y = 0
        # Замена по 4 бита (S-блоки)
        for i in range(8):
            y |= self.pi[i][(x >> (4 * i)) & 0xF] << (4 * i)
        # Циклический сдвиг на 11 бит
        return ((y << 11) | (y >> 21)) & 0xFFFFFFFF

    def encrypt_block(self, block: bytes) -> bytes:
        """Шифрование блока 64 бита (8 байт). 
        Используется классическая сеть Фейстеля: 31 раунд с перестановкой и 32-й без."""
        a1, a0 = struct.unpack(">II", block[:8])
        for i in range(31):
            # Правая часть становится левой, а новая правая = левая XOR g(ключ, правая)
            a1, a0 = a0, self._g(self.keys[i], a0) ^ a1
        # Финальный шаг (без перестановки половин)
        return struct.pack(">II", self._g(self.keys[31], a0) ^ a1, a0)

    def decrypt_block(self, block: bytes) -> bytes:
        """Расшифрование — те же операции, но раундовые ключи в обратном порядке."""
        a1, a0 = struct.unpack(">II", block[:8])
        keys = self.keys[::-1]
        for i in range(31):
            a1, a0 = a0, self._g(keys[i], a0) ^ a1
        return struct.pack(">II", self._g(keys[31], a0) ^ a1, a0)

def main():
    # P = 92def06b3c130a59db54c704f8189d204a98fb2e67a8024c8912409b17b57e41
    # Тестовый 256-битный ключ
    key_hex = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    cipher = Magma(bytes.fromhex(key_hex))

    print("=== МАГМА ГОСТ 34.12-2015 ===")
    while True:
        print("\n1. Зашифровать\n2. Расшифровать\n0. Выход")
        choice = input("Выбор: ")
        if choice == '0': break

        data_hex = input("Введите HEX данные: ").strip().replace(" ", "")
        if not data_hex: continue

        try:
            data = bytes.fromhex(data_hex)
            # Выравнивание данных по границе 8 байт (Zero Padding)
            if len(data) % 8 != 0:
                data = data.ljust((len(data) // 8 + 1) * 8, b'\x00')

            res = b""
            # Шифрование/расшифрование по блокам в режиме ECB
            for i in range(0, len(data), 8):
                block = data[i:i + 8]
                if choice == '1':
                    res += cipher.encrypt_block(block)
                else:
                    res += cipher.decrypt_block(block)

            print(f"РЕЗУЛЬТАТ: {res.hex().lower()}")
        except ValueError:
            print("Ошибка: неверный HEX формат.")

if __name__ == "__main__":
    main()