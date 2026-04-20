alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"


def replace(text):
    replacements = {
        '.': 'тчк', '—': 'тире', '-': 'тире', ',': 'зпт',
        '!': 'вскл', '?': 'впрс', '«': 'квчл', '»': 'квчп', ' ': 'прб'
    }
    result = ""
    for i in text.lower():
        result += replacements.get(i, i)
    return result


def restore(text):
    replacements = [
        ('тчк', '.'), ('тире', '—'), ('зпт', ','), ('вскл', '!'),
        ('впрс', '?'), ('квчл', '«'), ('квчп', '»'), ('прб', ' ')
    ]
    result = text
    for code, symbol in replacements:
        result = result.replace(code, symbol)
    return result


def vigenere_process(text, initial_key_char, key_type, mode):
    """
    key_type: 1 - Самоключ (открытый текст), 2 - Ключ-шифртекст
    mode: 1 - Шифрование, 2 - Расшифрование
    """
    result = ""
    # Подготавливаем первый ключ
    current_key_idx = alphabet.index(initial_key_char)

    # Работаем посимвольно
    for i in range(len(text)):
        if text[i] not in alphabet:
            result += text[i]
            continue

        char_idx = alphabet.index(text[i])

        if mode == 1:  # ШИФРОВАНИЕ
            new_idx = (char_idx + current_key_idx) % 32
            res_char = alphabet[new_idx]
            result += res_char

            # Обновляем ключ для следующего шага
            if key_type == 1:
                current_key_idx = char_idx  # Ключ - открытый текст
            else:
                current_key_idx = new_idx  # Ключ - шифртекст

        else:  # РАСШИФРОВАНИЕ
            new_idx = (char_idx - current_key_idx) % 32
            res_char = alphabet[new_idx]
            result += res_char

            # Обновляем ключ для следующего шага
            if key_type == 1:
                current_key_idx = new_idx  # В самоключе при дешифровке ключ - это результат (открытый текст)
            else:
                current_key_idx = char_idx  # В ключе-шифртексте ключ - это то, что пришло на вход (шифртекст)

    return result


def run_menu(mode_code):
    mode_name = "ШИФРОВАНИЕ" if mode_code == 1 else "РАСШИФРОВАНИЕ"
    print(f"\n--- {mode_name} (Виженер / Автоключ) ---")

    print("Выберите вариант:\n 1 - Самоключ (Open Text)\n 2 - Ключ-шифртекст (Cipher Text)")
    k_type = int(input(">> "))

    init_key = input("Введите начальную секретную букву: ").lower()
    if init_key not in alphabet:
        print("Ошибка: нужна одна буква алфавита!")
        return

    message = input("Введите текст: ")
    processed_msg = replace(message)

    result_raw = vigenere_process(processed_msg, init_key, k_type, mode_code)

    if mode_code == 2:
        print(f"\nИТОГ: {restore(result_raw)}")
    else:
        print(f"\nИТОГ: {result_raw}")


while True:
    print("\n=== Шифр Виженера ===")
    print("1. Зашифровать\n2. Расшифровать\n0. Выход")
    ch = input(">> ")
    if ch == '1':
        run_menu(1)
    elif ch == '2':
        run_menu(2)
    elif ch == '0':
        break