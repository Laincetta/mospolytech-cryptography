russian_alphabet = [
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З',
    'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П',
    'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч',
    'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я'
]

def replace(text):
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
    result = ""
    for i in text:
        result += replacements.get(i, i)
    return result

def restore(text):
    replacements = {
        'ТЧК': '.',
        'ТИРЕ': '–',
        'ЗПТ': ',',
        'ВСКЛ': '!',
        'ВПРС': '?',
        'КВЧЛ': '«',
        'КВЧП': '»',
        'ПРБ': ' '
    }
    result = text
    for code, symbol in replacements.items():
        result = result.replace(code, symbol)
    return result

def chesar(text, shift, decrypt=False):
    result = ""
    for char in text:
        upper_char = char.upper()
        if upper_char in russian_alphabet:
            idx = russian_alphabet.index(upper_char)
            new_idx = (idx + (-shift if decrypt else shift)) % 32
            new_char = russian_alphabet[new_idx]
            result += new_char.lower() if char.islower() else new_char
        else:
            result += char
    return result

def encrypt(text, shift):
    replaced_text = replace(text)
    return chesar(replaced_text, shift)

def decrypt(text, shift):
    decrypted_text = chesar(text, shift, decrypt=True)
    return restore(decrypted_text)


def format5(text):
    text = text.replace(' ', '')
    return ' '.join(text[i:i + 5] for i in range(0, len(text), 5))


def main():
    # 26 вар. Плохой работник никогда не находит хорошего инструмента.

    while True:
        print("Выберите:")
        print("1 - Ввести текст")
        print("2 - Выход")

        choice = input("Выберите: ").strip()
        print()

        if choice == '1':
            text = input("Введите текст: ")

            while True:
                try:
                    shift = int(input("Введите ключ (1-31): "))
                    if 1 <= shift <= 31:
                        break
                    print("Ошибка: ключ должен быть в диапазоне от 1 до 31.")
                except ValueError:
                    print("Ошибка: введите целое число.")

            encrypted = encrypt(text, shift)
            print("Зашифровано:", format5(encrypted.upper()))

            decrypted = decrypt(encrypted, shift)
            print("Расшифровано:", decrypted)
            print()

        elif choice == '2':
            break
        else:
            print("Неверный выбор. Пожалуйста, введите 1, 2.")


if __name__ == "__main__":
    main()