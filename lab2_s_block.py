import sys

# Прямые таблицы замен (S-блоки)
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

# Генерация обратных таблиц замен
pi_inv = []
for row in pi:
    inv_row = [0] * 16
    for i in range(16):
        inv_row[row[i]] = i
    pi_inv.append(inv_row)


def t(x):
    """Прямое преобразование (зашифрование в S-блоках)"""
    y = 0
    for i in range(8):
        # Извлекаем 4 бита (тетраду), начиная с младших
        shift = 4 * i
        j = (x >> shift) & 0xF
        s_value = pi[i][j]
        y |= (s_value << shift)
    return y


def t_inv(x):
    """Обратное преобразование (расшифрование в S-блоках)"""
    y = 0
    for i in range(8):
        shift = 4 * i
        j = (x >> shift) & 0xF
        s_value = pi_inv[i][j]
        y |= (s_value << shift)
    return y


def main():
    while True:
        print("\n--- Преобразование S-блоков (Магма) ---")
        print("1. Прямое преобразование (t)")
        print("2. Обратное преобразование (t_inv)")
        print("3. Выход")

        choice = input("\nВыберите опцию: ").strip()

        if choice in ['1', '2']:
            try:
                hex_input = input("Введите 32-битное hex-число (8 символов): ").strip()
                if len(hex_input) != 8:
                    print("Ошибка: требуется ровно 8 hex-символов (например, 12345678)")
                    continue

                x = int(hex_input, 16)

                if choice == '1':
                    result = t(x)
                    print(f"Результат t({hex_input.upper()}): {result:08X}")
                else:
                    result = t_inv(x)
                    print(f"Результат t_inv({hex_input.upper()}): {result:08X}")

            except ValueError:
                print("Ошибка: некорректный ввод. Используйте только 0-9 и A-F.")
        elif choice == '3':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()