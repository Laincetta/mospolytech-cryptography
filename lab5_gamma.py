"""
Блок E: ШИФРЫ ГАММИРОВАНИЯ
14. Гаммирование ГОСТ 28147-89 и ГОСТ Р 34.13-2015 («Магма»)  (ЛАБКРИПТ_2022)

Режим гаммирования Магма (Counter, CTR) по ГОСТ Р 34.13-2015:
    c_i = m_i ⊕ E_k(Ctr),   m_i = c_i ⊕ E_k(Ctr),
где E_k — зашифрование блока в режиме простой замены (сеть Фейстеля Магмы),
Ctr — счётчик, инициализируемый синхропосылкой S (здесь переменная IV).
Гамма Г_ш вырабатывается блоками по 64 бита и накладывается по модулю 2.
"""

# S-блоки из ГОСТ (узел замены)
pi = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
]

MASK32 = 0xFFFFFFFF
KEY = None
IV = None          # синхропосылка S (исходное заполнение счётчика Ctr)
ROUND_KEYS = None


def _key_schedule(k):
    """Генерация раундовых ключей"""
    keys = []
    key_parts = [(k >> (32 * i)) & MASK32 for i in range(8)]

    for i in range(7, -1, -1):
        keys.append(key_parts[i])
    for _ in range(2):
        for i in range(7, -1, -1):
            keys.append(key_parts[i])
    for i in range(8):
        keys.append(key_parts[i])

    return keys


def t(x):
    """Нелинейное преобразование t (S-блоки)"""
    y = 0
    for i in range(8):
        nibble = (x >> (4 * i)) & 0xF
        y |= pi[i][nibble] << (4 * i)
    return y


def rot11(x):
    """Циклический сдвиг на 11 бит влево"""
    return ((x << 11) | (x >> (32 - 11))) & MASK32


def g(k, a):
    """g[k](a) = rot11(t((a + k) mod 2³²))"""
    return rot11(t((a + k) & MASK32))


def G(k, a1, a0):
    return (a0, g(k, a0) ^ a1)


def G_star(k, a1, a0):
    return (g(k, a0) ^ a1, a0)


def encrypt_64bit_block(block, round_keys):
    """Шифрование 64-битного блока в режиме простой замены"""
    a1 = (block >> 32) & MASK32
    a0 = block & MASK32

    for i in range(31):
        a1, a0 = G(round_keys[i], a1, a0)
    a1, a0 = G_star(round_keys[31], a1, a0)

    return (a1 << 32) | a0


def set_key_iv(key_hex, iv_hex):
    """Установка ключа и IV для текущей сессии"""
    global KEY, IV, ROUND_KEYS

    try:
        KEY = int(key_hex.replace(' ', ''), 16)

        iv_str = iv_hex.replace(' ', '')
        if len(iv_str) < 16:
            iv_str = iv_str.ljust(16, '0')
        IV = int(iv_str[:16], 16)

        ROUND_KEYS = _key_schedule(KEY)

        print("\nКлючевые параметры успешно установлены!")
        print(f"KEY: {KEY:064X}")
        print(f"IV:  {IV:016X}")
        return True
    except Exception as e:
        print(f"Ошибка при установке параметров: {e}")
        return False


def process_blocks(data_hex, operation):
    """Обработка данных в режиме гаммирования CTR"""
    global ROUND_KEYS, IV

    if ROUND_KEYS is None or IV is None:
        print("Ошибка: сначала установите ключ и IV")
        return None

    try:
        data_bytes = bytes.fromhex(data_hex)
        result = bytearray()
        ctr = IV

        print(f"\n{'Шифрование' if operation == 'encrypt' else 'Расшифрование'}:")
        print("i\tСчётчик (CTR)\t\tГамма (E(CTR))\t\tРезультат (блок)")
        print("-" * 80)

        for i in range(0, len(data_bytes), 8):
            block_num = i // 8 + 1
            block = data_bytes[i:i + 8]

            encrypted_ctr = encrypt_64bit_block(ctr, ROUND_KEYS)

            processed_block = bytearray()
            for j, b in enumerate(block):
                processed_block.append(b ^ ((encrypted_ctr >> (56 - 8 * j)) & 0xFF))

            print(f"{block_num}\t{ctr:016X}\t{encrypted_ctr:016X}\t{processed_block.hex()}")

            result.extend(processed_block)
            ctr = (ctr + 1) & ((1 << 64) - 1)

        return result.hex().upper()

    except Exception as e:
        print(f"Ошибка при обработке: {e}")
        return None


def input_data():
    """Ввод данных (4 блока слитно = 64 hex символа)"""
    print("\nВведите данные (64 hex символа = 4 блока по 16 символов):")
    data_hex = input("Данные: ").strip().replace(' ', '')

    if len(data_hex) != 64:
        print(f"Ошибка: нужно 64 hex символа, получено {len(data_hex)}")
        return None

    try:
        bytes.fromhex(data_hex)
        return data_hex
    except ValueError:
        print("Ошибка: строка содержит недопустимые символы (только 0-9, A-F)")
        return None


def print_result(result, prefix):
    """Вывод результата (4 блока по 16 символов)"""
    print(f"\nРезультат ({prefix}):")
    print(f"{prefix}: {result}")
    print("\nПо блокам (по 16 символов):")
    for i in range(0, len(result), 16):
        print(f"{prefix}{i // 16 + 1}: {result[i:i + 16]}")


if __name__ == "__main__":
    print("=" * 80)
    print("РЕЖИМ ГАММИРОВАНИЯ (CTR) ДЛЯ ШИФРА МАГМА")
    print("ГОСТ Р 34.13-2015")
    print("=" * 80)

    print("\n--- ВВОД КЛЮЧЕВЫХ ПАРАМЕТРОВ ---")

    key_hex = input("Ключ (64 hex символа = 256 бит): ").strip()
    if len(key_hex.replace(' ', '')) != 64:
        print("Ошибка: ключ должен содержать 64 hex символа")
    else:
        iv_hex = input("Синхропосылка IV (до 16 hex символов = 64 бита): ").strip()

        if set_key_iv(key_hex, iv_hex):
            while True:
                print("\n" + "=" * 80)
                print("--- ВЫБОР ОПЕРАЦИИ ---")
                print("1 - Зашифровать (4 блока = 256 бит)")
                print("2 - Расшифровать (4 блока = 256 бит)")
                print("3 - Сменить ключ и IV")
                print("4 - Выход")

                choice = input("Ваш выбор: ").strip()

                if choice == '1':
                    print("\n--- ЗАШИФРОВАНИЕ ---")
                    data = input_data()
                    if data:
                        result = process_blocks(data, 'encrypt')
                        if result:
                            print_result(result, 'C')

                elif choice == '2':
                    print("\n--- РАСШИФРОВАНИЕ ---")
                    data = input_data()
                    if data:
                        result = process_blocks(data, 'decrypt')
                        if result:
                            print_result(result, 'P')

                elif choice == '3':
                    print("\n--- СМЕНА КЛЮЧЕВЫХ ПАРАМЕТРОВ ---")
                    key_hex = input("Новый ключ (64 hex символа): ").strip()
                    if len(key_hex.replace(' ', '')) != 64:
                        print("Ошибка: ключ должен содержать 64 hex символа")
                    else:
                        iv_hex = input("Новый IV (до 16 hex символов): ").strip()
                        set_key_iv(key_hex, iv_hex)

                elif choice == '4':
                    print("\nВыход из программы.")
                    break

                else:
                    print("Неверный выбор, попробуйте снова")
