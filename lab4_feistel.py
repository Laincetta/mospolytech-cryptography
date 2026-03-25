# S-блоки из ГОСТ
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


def _key_schedule(k):
    """Генерация раундовых ключей для шифрования"""
    keys = []

    # Извлекаем 8 32-битных слов из 256-битного ключа
    key_parts = []
    for i in range(8):
        key_parts.append((k >> (32 * i)) & MASK32)

    # K1...K8 = ключи в порядке, обратном извлечению
    for i in range(7, -1, -1):
        keys.append(key_parts[i])

    # K9...K16 = снова K1...K8
    for i in range(8):
        keys.append(key_parts[7 - i])

    # K17...K24 = снова K1...K8
    for i in range(8):
        keys.append(key_parts[7 - i])

    # K25...K32 = ключи в порядке, обратном K1...K8
    for i in range(8):
        keys.append(key_parts[i])

    return keys


def _key_schedule_decrypt(k):
    """Генерация раундовых ключей для расшифрования"""
    # Для расшифрования используем ключи в обратном порядке
    enc_keys = _key_schedule(k)
    return enc_keys[::-1]


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
    sum_mod = (a + k) & MASK32
    return rot11(t(sum_mod))


def G(k, a1, a0):
    """G[k](a1, a0) = (a0, g[k](a0) ⊕ a1) - обычный раунд с перестановкой"""
    return (a0, g(k, a0) ^ a1)


def G_star(k, a1, a0):
    """G*[k](a1, a0) = (g[k](a0) ⊕ a1, a0) - последний раунд без перестановки"""
    return (g(k, a0) ^ a1, a0)


def encrypt_block(a1, a0, round_keys):
    """Шифрование блока"""
    # 31 раунд с G
    for i in range(31):
        a1, a0 = G(round_keys[i], a1, a0)

    # 32-й раунд с G*
    a1, a0 = G_star(round_keys[31], a1, a0)
    return a1, a0


def decrypt_block(a1, a0, round_keys):
    """Расшифрование блока (те же функции, но ключи в обратном порядке)"""
    # Для расшифрования используем те же функции G и G*
    # Но ключи подаются в обратном порядке
    return encrypt_block(a1, a0, round_keys)


def main():
    print("ПРЕОБРАЗОВАНИЯ g[k] И G[k] (СЕТЬ ФЕЙСТЕЛЯ)")
    print("ГОСТ 28147-89 - Режим простой замены\n")

    try:
        # Выбор режима
        mode = input("Выберите режим (1 - Обычный режим, 2 - В обратную сторону): ").strip()

        # Ввод основного ключа
        key_hex = input("Введите основной ключ (hex, 32 байта / 64 символа): ").strip()
        key = int(key_hex, 16)

        # Генерация раундовых ключей в зависимости от режима
        if mode == "1":
            round_keys = _key_schedule(key)
            print("\nРежим: Обычный режим")
        else:
            round_keys = _key_schedule_decrypt(key)
            print("\nРежим: В обратную сторону")

        # Ввод начального сообщения
        state_hex = input("\nВведите сообщение (hex, 16 символов): ").strip()
        state = int(state_hex, 16)
        a1 = (state >> 32) & MASK32
        a0 = state & MASK32


        for i in range(31):
            a1, a0 = G(round_keys[i], a1, a0)

        a1, a0 = G_star(round_keys[31], a1, a0)

        final = (a1 << 32) | a0
        print(f"\nИтоговое состояние: {final:016X}")

    except ValueError as e:
        print(f"Ошибка: некорректный HEX формат - {e}")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()

# K = ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff
# a = fedcba9876543210   4EE901E5C2D8CA3D