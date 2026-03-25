russian_alphabet = {
    'А': 'Я', 'Б': 'Ю', 'В': 'Э', 'Г': 'Ь', 'Д': 'Ы', 'Е': 'Ъ', 'Ж': 'Щ', 'З': 'Ш',
    'И': 'Ч', 'Й': 'Ц', 'К': 'Х', 'Л': 'Ф', 'М': 'У', 'Н': 'Т', 'О': 'С', 'П': 'Р',
    'Р': 'П', 'С': 'О', 'Т': 'Н', 'У': 'М', 'Ф': 'Л', 'Х': 'К', 'Ц': 'Й', 'Ч': 'И',
    'Ш': 'З', 'Щ': 'Ж', 'Ъ': 'Е', 'Ы': 'Д', 'Ь': 'Г', 'Э': 'В', 'Ю': 'Б', 'Я': 'А'
}

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
        'ТИРЕ': '—',
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

def atbash(text):
    result = ""
    for char in text:
        upper_char = char.upper()
        if upper_char in russian_alphabet:
            new_char = russian_alphabet[upper_char]
            result += new_char.lower() if char.islower() else new_char
        else:
            result += char
    return result

def encrypt(text):
    replaced_text = replace(text)
    return atbash(replaced_text)

def decrypt(text):
    decrypted_text = atbash(text)
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

            encrypted = encrypt(text)
            print("Зашифровано:", format5(encrypted.upper()))

            decrypted = decrypt(encrypted)
            print("Расшифровано:", decrypted)

        elif choice == '2':
            break
        else:
            print("Неверный выбор. Пожалуйста, введите 1, 2.")

if __name__ == "__main__":
    main()