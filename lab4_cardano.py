import math
import random

russian_alphabet = [
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З',
    'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П',
    'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч',
    'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я'
]

# Ваша фиксированная решетка 10x6
CARDANO_GRID = [
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 1, 1, 0, 0, 1]
]

current_grid = CARDANO_GRID
current_rows = 6
current_cols = 10


def replace_punctuation(text):
    """Заменяет знаки препинания на текстовые коды"""
    replacements = {
        '.': 'ТЧК',
        '—': 'ТИРЕ',
        '–': 'ТИРЕ',
        ',': 'ЗПТ',
        '!': 'ВСКЛ',
        '?': 'ВПРС',
        '«': 'КВЧЛ',
        '»': 'КВЧП',
        ' ': ''  # Пробелы просто удаляем для этого шифра
    }
    result = ""
    for i in text:
        result += replacements.get(i, i)
    return result


def clean_final(text):
    """Оставляет только буквы алфавита в верхнем регистре"""
    text = text.upper().replace('Ё', 'Е')
    return "".join([c for c in text if c in russian_alphabet])


def get_positions_for_state(grid, state):
    rows, cols = len(grid), len(grid[0])
    positions = []
    for i in range(rows):
        for j in range(cols):
            if state == 0 and grid[i][j] == 1:
                positions.append((i, j))
            elif state == 1 and grid[i][j] == 1:  # Поворот 180
                positions.append((rows - 1 - i, cols - 1 - j))
            elif state == 2 and grid[i][j] == 1:  # Переворот
                positions.append((rows - 1 - i, j))
            elif state == 3 and grid[i][j] == 1:  # 180 от перевернутого
                positions.append((i, cols - 1 - j))

    positions.sort(key=lambda x: (x[0], x[1]))
    return positions


def encrypt(text):
    # 1. Заменяем знаки на ТЧК, ЗПТ и т.д.
    text_with_codes = replace_punctuation(text)
    # 2. Очищаем от мусора и приводим к ВЕРХНЕМУ регистру
    processed_text = clean_final(text_with_codes)

    table = [['' for _ in range(current_cols)] for _ in range(current_rows)]
    text_index = 0

    # Заполнение по 4 состояниям решетки
    for state in range(4):
        positions = get_positions_for_state(current_grid, state)
        for i, j in positions:
            if text_index < len(processed_text):
                table[i][j] = processed_text[text_index]
                text_index += 1
            else:
                table[i][j] = random.choice(russian_alphabet)

    # Сборка итоговой строки (чтение таблицы построчно)
    ciphertext = ''
    for i in range(current_rows):
        for j in range(current_cols):
            ciphertext += table[i][j]
    return ciphertext.lower()


def decrypt(text):
    text = clean_final(text)
    expected_length = current_rows * current_cols
    text = text[:expected_length].ljust(expected_length, ' ')

    table = [['' for _ in range(current_cols)] for _ in range(current_rows)]
    index = 0
    for i in range(current_rows):
        for j in range(current_cols):
            table[i][j] = text[index]
            index += 1

    result = []
    for state in range(4):
        positions = get_positions_for_state(current_grid, state)
        for i, j in positions:
            result.append(table[i][j])

    return "".join(result).lower()


def format5(text):
    return ' '.join(text[i:i + 5] for i in range(0, len(text), 5))


def main():
    print("\n" + "=" * 50)
    print("ШИФР ПОВОРОТНАЯ РЕШЕТКА КАРДАНО".center(50))
    print("=" * 50)

    while True:
        print("\nМЕНЮ:")
        print("1 - Зашифровать текст")
        print("2 - Расшифровать текст")
        print("3 - Выход")
        choice = input("\nВыберите действие: ").strip()

        if choice == '1':
            text = input("Введите текст: ")
            res = encrypt(text)
            print(f"\nРезультат:\n{res}")
            print(f"Форматированный: {format5(res)}")
        elif choice == '2':
            text = input("Введите шифртекст: ").replace(' ', '')
            res = decrypt(text)
            print(f"\nРасшифрованный текст (с кодами):")
            print(res)
        elif choice == '3':
            print("Программа завершена.")
            break
        else:
            print("Неверный ввод.")


if __name__ == "__main__":
    main()