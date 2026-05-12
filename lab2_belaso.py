alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'


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


def format5(text):
    text = text.upper()
    return ' '.join(text[i:i + 5] for i in range(0, len(text), 5))


def bellaso(text, keyword, encrypt=True):
    """
    Шифр Белазо: многоалфавитная замена с циклически повторяющимся ключевым словом.
    Алгоритм идентичен шифру Виженера, но ключ — фиксированное слово (не самоключ).

    text    — строка из символов алфавита (уже после replace)
    keyword — ключевое слово из букв алфавита
    encrypt — True = шифрование, False = расшифрование
    """
    text = text.lower()
    keyword = keyword.lower()
    clean = [c for c in text if c in alphabet]
    n = len(alphabet)
    result = ''
    for i, c in enumerate(clean):
        t_pos = alphabet.index(c)
        k_pos = alphabet.index(keyword[i % len(keyword)])
        if encrypt:
            result += alphabet[(t_pos + k_pos) % n]
        else:
            result += alphabet[(t_pos - k_pos) % n]
    return result


def run_menu(mode_code):
    mode_name = "ШИФРОВАНИЕ" if mode_code == 1 else "РАСШИФРОВАНИЕ"
    print(f"\n--- {mode_name} (Шифр Белазо) ---")

    keyword = input("Введите ключевое слово: ").lower()
    if not keyword or not all(c in alphabet for c in keyword):
        print("Ошибка: ключ должен состоять из букв русского алфавита!")
        return

    message = input("Введите текст: ")
    processed_msg = replace(message)

    encrypt = (mode_code == 1)
    result_raw = bellaso(processed_msg, keyword, encrypt=encrypt)

    if mode_code == 2:
        print(f"\nИТОГ: {restore(result_raw)}")
    else:
        print(f"\nИТОГ: {format5(result_raw)}")


if __name__ == "__main__":
    while True:
        print("\n=== Шифр Белазо ===")
        print("1. Зашифровать\n2. Расшифровать\n0. Выход")
        ch = input(">> ")
        if ch == '1':
            run_menu(1)
        elif ch == '2':
            run_menu(2)
        elif ch == '0':
            break
