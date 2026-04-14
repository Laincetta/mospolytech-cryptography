import math


def get_key_order(key):
    """Преобразует ключ в последовательность приоритетов (длина ключа = ширина)"""
    key = key.upper().replace(' ', '')
    key_list = list(key)
    # Создаем пары (символ, исходный индекс) и сортируем их по алфавиту
    indexed = [(key_list[i], i) for i in range(len(key_list))]
    sorted_chars = sorted(indexed)

    # Массив порядка: какое место занимает i-й столбец при чтении
    order = [0] * len(key_list)
    for priority, (char, original_idx) in enumerate(sorted_chars):
        order[original_idx] = priority + 1
    return order


def prepare_text(text):
    replacements = {
        '.': 'ТЧК', '—': 'ТИРЕ', '-': 'ТИРЕ', ',': 'ЗПТ',
        '!': 'ВСКЛ', '?': 'ВПРС', '«': 'КВЧЛ', '»': 'КВЧП'
    }
    text = text.upper().replace(' ', '')

    result = ""
    for char in text:
        result += replacements.get(char, char)
    return result


def restore_text(text):
    replacements = [
        ('ТЧК', '.'), ('ТИРЕ', '—'), ('ЗПТ', ','), ('ВСКЛ', '!'),
        ('ВПРС', '?'), ('КВЧЛ', '«'), ('КВЧП', '»')
    ]
    result = text
    for code, symbol in replacements:
        result = result.replace(code, symbol)
    return result


def vertical_permutation_logic(text, key, mode='encrypt'):
    key = key.upper().replace(' ', '')
    n = len(key)
    if n == 0: return "Ошибка: Пустой ключ"

    if mode == 'encrypt':
        clean_text = prepare_text(text)
        length = len(clean_text)
        m = math.ceil(length / n)

        matrix = []
        for r in range(m):
            start = r * n
            end = min(start + n, length)  # Берем только существующие символы
            matrix.append(list(clean_text[start:end]))

        print("\n--- Сформированная матрица ---")
        for row in matrix:
            print(" ".join(row))

        # ЧИТАЕМ ПО СТОЛБЦАМ
        col_order = get_key_order(key)
        sorted_indices = sorted(range(n), key=lambda x: col_order[x])

        result = ""
        for col_idx in sorted_indices:
            for row_idx in range(m):
                # Проверяем, есть ли в текущей строке символ в нужном столбце
                if col_idx < len(matrix[row_idx]):
                    result += matrix[row_idx][col_idx]
        return result

    else:
        # ДЕШИФРОВКА
        cipher_text = text.upper().replace(' ', '')
        length = len(cipher_text)
        m = math.ceil(length / n)

        # Вычисляем точную длину каждого столбца
        # (сколько букв попало в последнюю неполную строку)
        chars_in_last_row = length % n
        if chars_in_last_row == 0: chars_in_last_row = n

        col_lengths = []
        for c in range(n):
            # Если индекс столбца меньше количества символов в последней строке,
            # значит этот столбец "длинный" (высота M)
            if c < chars_in_last_row:
                col_lengths.append(m)
            else:
                col_lengths.append(m - 1)

        # Создаем пустую структуру под расшифровку
        decrypt_matrix = [["" for _ in range(len(row))] for row in
                          [list(range(n)) if i < m - 1 else list(range(chars_in_last_row)) for i in range(m)]]

        col_order = get_key_order(key)
        sorted_indices = sorted(range(n), key=lambda x: col_order[x])

        # Заполняем по столбцам
        idx = 0
        for col_idx in sorted_indices:
            for row_idx in range(m):
                # Проверяем, существует ли ячейка в этой строке для этого столбца
                if row_idx < m - 1 or col_idx < chars_in_last_row:
                    if idx < length:
                        decrypt_matrix[row_idx][col_idx] = cipher_text[idx]
                        idx += 1

        # Собираем строки в текст
        res_list = []
        for row in decrypt_matrix:
            res_list.append("".join(row))

        return restore_text("".join(res_list))


def main():
    while True:
        print("\n" + "═" * 45)
        print("   ВЕРТИКАЛЬНАЯ ПЕРЕСТАНОВКА ")
        print("═" * 45)
        print(" [1] Зашифровать")
        print(" [2] Расшифровать")
        print(" [3] Выход")
        print("─" * 45)

        cmd = input("Выбор: ").strip()
        if cmd == '3': break

        if cmd in ['1', '2']:
            key = input("Ключ: ").strip()
            if not key: continue

            text = input("Текст/Шифр: ").strip()

            if cmd == '1':
                res = vertical_permutation_logic(text, key, 'encrypt')
                print(f"\nРЕЗУЛЬТАТ:\n{res}")
            else:
                res = vertical_permutation_logic(text, key, 'decrypt')
                print(f"\nРАСШИФРОВАНО:\n{res}")


if __name__ == "__main__":
    main()