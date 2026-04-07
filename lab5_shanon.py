"""
ШИФР ШЕННОНА (ГАММИРОВАНИЕ С ЛКГ)
Автономная версия без внешних зависимостей
"""

ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
ALPHABET_LEN = len(ALPHABET)  # = 32


def check_is_numeric(s):
    """Проверяет, является ли строка целым числом"""
    if not s or not isinstance(s, str):
        return False, ""
    s = s.strip()
    if not s:
        return False, ""
    if s[0] in ('-', '+'):
        s = s[1:]
    if not s.isdigit():
        return False, ""
    return True, s


def check_is_text(s):
    """Проверяет, содержит ли строка только русские буквы и пробелы"""
    if not isinstance(s, str):
        return False, "входные данные не являются строкой"
    if not s:
        return False, "строка пуста"
    allowed = set(ALPHABET + ' ')
    for ch in s:
        if ch.lower() not in allowed:
            return False, f"недопустимый символ: '{ch}'"
    return True, ""


def format_with_spaces(text, chars_per_group=5):
    """Форматирует текст с пробелами каждые chars_per_group символов"""
    if not text:
        return ""
    return ' '.join(text[i:i + chars_per_group] for i in range(0, len(text), chars_per_group))


def text_to_numbers(text):
    """Переводит строку в список чисел (1..32)"""
    return [ALPHABET.index(char) + 1 for char in text]


def numbers_to_text(numbers):
    """Переводит список чисел обратно в строку"""
    return ''.join(ALPHABET[(num - 1) % ALPHABET_LEN] for num in numbers)


def format_numbers(numbers):
    """Форматирует числа в двузначный вид с пробелами"""
    return ' '.join(f"{num:02d}" for num in numbers)


def shannon_otp(text, question2):
    """
    Шифрование (question2=1) или расшифрование (question2=2)
    по методу гаммирования с линейным конгруэнтным генератором
    """
    # === БЛОК 1: преобразование входного текста в числа ===
    if question2 == 1:
        # Режим шифрования — на входе обычный текст
        is_valid, msg = check_is_text(text)
        if not is_valid:
            return f"Ошибка: {msg}"
        text = text.replace(' ', '').lower()
        if not text:
            return "Ошибка: пустой текст"
        text_nums = text_to_numbers(text)
        n = len(text_nums)
    else:
        # Режим расшифрования — на входе строка с двузначными числами
        if ' ' in text:
            parts = text.split()
        else:
            if len(text) % 2 != 0:
                return "Ошибка: длина строки должна быть чётной (каждое число двузначное)"
            parts = [text[i:i + 2] for i in range(0, len(text), 2)]

        if not parts:
            return "Ошибка: пустой ввод"
        cipher_nums = []
        for p in parts:
            is_valid_num, num_val = check_is_numeric(p)
            if not is_valid_num:
                return f"Ошибка: '{p}' не является числом"
            num = int(num_val)
            if num < 1 or num > 32:
                return f"Ошибка: число {num} вне диапазона 1..32"
            cipher_nums.append(num)
        n = len(cipher_nums)

    # === БЛОК 2: ввод параметров ЛКГ с проверками ===
    while True:
        try:
            a_str = input("Введите параметр a:\n")
            c_str = input("Введите параметр c:\n")
            t0_str = input("Введите начальное значение T0:\n")

            is_num_a, a_val = check_is_numeric(a_str)
            is_num_c, c_val = check_is_numeric(c_str)
            is_num_t0, t0_val = check_is_numeric(t0_str)

            if not (is_num_a and is_num_c and is_num_t0):
                print("Ошибка: все параметры должны быть числами.")
                continue

            a = int(a_val)
            c = int(c_val)
            T0 = int(t0_val)

            # Условия для максимального периода (по теореме Халла — Добелла)
            if a == 1:
                print("Ошибка: параметр a не должен быть равен 1 (иначе генератор вырождается).")
                continue
            if a % 4 != 1:
                print(
                    "Ошибка: параметр a должен удовлетворять условию a ≡ 1 (mod 4) для максимального периода при m=2^k.")
                continue
            if c % 2 == 0:
                print("Ошибка: параметр c должен быть нечётным (иначе период будет короче).")
                continue

            break
        except ValueError:
            print("Ошибка преобразования. Попробуйте снова.")

    # === БЛОК 3: генерация гаммы ===
    gamma = [0] * n
    if n > 0:
        gamma[0] = (a * T0 + c) % ALPHABET_LEN
        for i in range(1, n):
            gamma[i] = (a * gamma[i - 1] + c) % ALPHABET_LEN

    print(f"\nСгенерированная гамма: {format_numbers(gamma)}")

    # === БЛОК 4: шифрование / расшифрование ===
    if question2 == 1:
        result_nums = []
        for i in range(n):
            s = (text_nums[i] + gamma[i]) % ALPHABET_LEN
            if s == 0:
                s = ALPHABET_LEN
            result_nums.append(s)

        result_str = format_numbers(result_nums)
        return f"Зашифрованный текст: {result_str}"
    else:
        result_nums = []
        for i in range(n):
            s = (cipher_nums[i] - gamma[i]) % ALPHABET_LEN
            if s == 0:
                s = ALPHABET_LEN
            result_nums.append(s)

        plain_text = numbers_to_text(result_nums)
        formatted = format_with_spaces(plain_text)
        return f"Расшифрованный текст: {formatted}"


def main_menu():
    """Главное меню программы"""

    while True:
        print("\nОдноразовый блокнот Шеннона:")
        print("=======================")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("=======================")

        choice = input("\nВыберите действие (1-2): ").strip()

        if choice == '1':
            print("\n" + "─" * 50)
            text = input("Введите текст для шифрования (только русские буквы):\n")
            print("─" * 50)
            result = shannon_otp(text, 1)
            print("\n" + "═" * 50)
            print("РЕЗУЛЬТАТ ШИФРОВАНИЯ:")
            print(result)
            print("═" * 50)

        elif choice == '2':
            print("\n" + "─" * 50)
            text = input("Введите шифротекст (двузначные числа, через пробел или слитно):\n")
            print("─" * 50)
            result = shannon_otp(text, 2)
            print("\n" + "═" * 50)
            print("РЕЗУЛЬТАТ РАСШИФРОВАНИЯ:")
            print(result)
            print("═" * 50)

        else:
            print("\nОшибка: пожалуйста, выберите 1 или 2.")


if __name__ == "__main__":
    main_menu()