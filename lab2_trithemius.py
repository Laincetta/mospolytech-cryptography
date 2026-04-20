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


def trithemius_process(text, mode):
    """
    mode: 1 для шифрования, 2 для расшифрования
    Закон: сдвиг равен индексу символа (a = 0, 1, 2...)
    """
    result = ""
    step = 0

    for char in text:
        if char in alphabet:
            idx = alphabet.index(char)
            if mode == 1:
                # Шифрование: (позиция + шаг) % 32
                new_idx = (idx + step) % 32
            else:
                # Расшифрование: (позиция - шаг) % 32
                new_idx = (idx - step) % 32

            result += alphabet[new_idx]
            step += 1
        else:
            # Если символ не в алфавите (хотя после replace их быть не должно),
            # оставляем как есть, не увеличивая шаг
            result += char

    return result


def run_menu(mode_code):
    mode_name = "ШИФРОВАНИЕ" if mode_code == 1 else "РАСШИФРОВАНИЕ"
    print(f"\n--- {mode_name} (Тритемиус) ---")

    message = input("Введите текст: ")
    # Предварительная обработка (замена знаков на буквенные коды)
    processed_msg = replace(message)

    # Работа алгоритма
    result_raw = trithemius_process(processed_msg, mode_code)

    if mode_code == 2:
        # Для расшифрования возвращаем знаки препинания на место
        final_text = restore(result_raw)
    else:
        final_text = result_raw

    print(f"Результат: {final_text}")


while True:
    print("\n=== Шифр Тритемиуса ===")
    print("1. Зашифровать\n2. Расшифровать\n0. Выход")
    ch = input(">> ")
    if ch == '1':
        run_menu(1)
    elif ch == '2':
        run_menu(2)
    elif ch == '0':
        break