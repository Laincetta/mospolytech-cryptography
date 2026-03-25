ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ-"
COLS = 6


def replace_marks(text):
    replacements = {
        '.': 'ТЧК',
        '—': 'ТИРЕ',
        '–': 'ТИРЕ',
        ',': 'ЗПТ',
        '!': 'ВСКЛ',
        '?': 'ВПРС',
        '«': 'КВЧЛ',
        '»': 'КВЧП',
        ' ': 'ПРБ'
    }
    text = text.upper()
    result = ""
    for char in text:
        if char in replacements:
            result += replacements[char]
        elif char in ALPHABET:
            result += char
    return result


def restore_marks(text):
    replacements = {
        'ТЧК': '.', 'ТИРЕ': '–', 'ЗПТ': ',', 'ВСКЛ': '!',
        'ВПРС': '?', 'КВЧЛ': '«', 'КВЧП': '»', 'ПРБ': ' '
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def polibiy_encode(text):
    processed_text = replace_marks(text)
    encoded = ""
    for char in processed_text:
        if char in ALPHABET:
            index = ALPHABET.find(char)
            row = (index // COLS) + 1
            col = (index % COLS) + 1
            encoded += f"{row}{col} "
    return encoded.strip()


def polibiy_decode(encoded_text):
    clean_code = encoded_text.replace(" ", "")
    decoded_chars = ""

    for i in range(0, len(clean_code) - 1, 2):
        row = int(clean_code[i]) - 1
        col = int(clean_code[i + 1]) - 1
        index = row * COLS + col

        if 0 <= index < len(ALPHABET):
            decoded_chars += ALPHABET[index]

    return restore_marks(decoded_chars)


def menu():
    while True:
        print("\n--- КВАДРАТ ПОЛИБИЯ ---")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            msg = input("Введите текст: ")
            print(f"Результат: {polibiy_encode(msg)}")
        elif choice == '2':
            code = input("Введите цифры (можно с пробелами): ")
            print(f"Результат: {polibiy_decode(code)}")
        elif choice == '3':
            break


if __name__ == "__main__":
    menu()