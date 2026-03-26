import math
import random

def replace(text):
    replacements = {
        '.': 'ТЧК', '—': 'ТИРЕ', '-': 'ТИРЕ', ',': 'ЗПТ',
        '!': 'ВСКЛ', '?': 'ВПРС', '«': 'КВЧЛ', '»': 'КВЧП', ' ': 'ПРБ'
    }
    result = ""
    for i in text.upper():
        result += replacements.get(i, i)
    return result

def restore(text):
    replacements = {
        'ТЧК': '.', 'ТИРЕ': '—', 'ЗПТ': ',', 'ВСКЛ': '!',
        'ВПРС': '?', 'КВЧЛ': '«', 'КВЧП': '»', 'ПРБ': ' '
    }
    result = text
    for code in sorted(replacements.keys(), key=len, reverse=True):
        result = result.replace(code, replacements[code])
    return result

ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
CHAR_TO_NUM = {char: i + 1 for i, char in enumerate(ALPHABET)}
NUM_TO_CHAR = {i + 1: char for i, char in enumerate(ALPHABET)}

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0: return False
    return True

def get_int_input(prompt, condition_lambda, error_msg):
    while True:
        try:
            val = int(input(prompt))
            if condition_lambda(val):
                return val
            print(f"Ошибка! {error_msg}")
        except ValueError:
            print("Ошибка! Введите целое число.")

def get_params():
    print("\n--- Выбор режима работы ---")
    print("1. Обычный режим")
    print("2. Режим тестирования (ввод 3-х чисел k вручную)")
    mode = input("Ваш выбор (1/2): ")

    print("\n--- Ввод основных параметров ---")
    p = get_int_input("Введите простое число p (p > 33): ",
                      lambda x: x > 33 and is_prime(x),
                      "Число должно быть простым и больше 33.")

    g = get_int_input(f"Введите g (1 < g < {p}): ",
                      lambda x: 1 < x < p,
                      f"Число g должно быть в диапазоне (1, {p}).")

    while True:
        x = get_int_input(f"Введите секретный ключ x (1 < x < {p}): ",
                          lambda val: 1 < val < p,
                          f"Ключ x должен быть в диапазоне (1, {p}).")
        y = pow(g, x, p)
        if x != y:
            break
        print(f"Внимание: вычисленный открытый ключ y ({y}) совпал с секретным ключом x!")

    k_list = []
    if mode == '2':
        while True:
            k_input = input(f"Введите ровно 3 числа k через запятую (1 < k < {p - 1}): ")
            try:
                k_list_raw = [int(i.strip()) for i in k_input.split(',')]
                if len(k_list_raw) != 3:
                    print(f"Ошибка: Вы ввели {len(k_list_raw)} чисел вместо 3!")
                    continue

                valid = True
                for k in k_list_raw:
                    if not (1 < k < p - 1) or math.gcd(k, p - 1) != 1:
                        print(f"Число k={k} недопустимо (вне диапазона или НОД(k, {p - 1}) != 1)!")
                        valid = False
                        break
                if valid:
                    k_list = k_list_raw
                    break
            except ValueError:
                print("Используйте только числа и запятые.")
    else:
        print("Генерация пула всех валидных k...")
        k_list = [k for k in range(2, p - 1) if math.gcd(k, p - 1) == 1]
        print(f"Пул создан! Доступно вариантов: {len(k_list)}")

    y = pow(g, x, p)
    return {
        'p': p, 'g': g, 'x': x, 'y': y, 'k_list': k_list,
        'mode_name': "Тестирование" if mode == '2' else "Обычный"
    }

def encrypt(text, p, g, y, k_list):
    prepared_text = replace(text)
    cipher_parts = []
    pad_len = len(str(p - 1))

    for char in prepared_text:
        if char not in CHAR_TO_NUM: continue
        m = CHAR_TO_NUM[char]

        current_k = random.choice(k_list)
        a = pow(g, current_k, p)
        b = (pow(y, current_k, p) * m) % p

        cipher_parts.append(str(a).zfill(pad_len))
        cipher_parts.append(str(b).zfill(pad_len))

    return "".join(cipher_parts)

def decrypt(cipher_str, p, x):
    pad_len = len(str(p - 1))
    char_step = 2 * pad_len
    decoded_chars = ""

    for i in range(0, len(cipher_str), char_step):
        block = cipher_str[i: i + char_step]
        if len(block) < char_step: break

        a = int(block[:pad_len])
        b = int(block[pad_len:])

        # M = b * (a^x)^(-1) mod p
        ax_inv = pow(pow(a, x, p), -1, p)
        m = (b * ax_inv) % p

        if m in NUM_TO_CHAR:
            decoded_chars += NUM_TO_CHAR[m]

    return restore(decoded_chars)

def main():
    params = None
    while True:
        print("\n=== ГЛАВНОЕ МЕНЮ ELGAMAL===")
        if params:
            print(f"ПАРАМЕТРЫ:")
            print(f"Открытые ключи: p={params['p']}, g={params['g']}, y={params['y']}")
            print(f"Секретный ключ: x={params['x']}")
            print(f"РЕЖИМ: {params['mode_name']} (доступно k: {len(params['k_list'])})")
        else:
            print("ПАРАМЕТРЫ НЕ ЗАДАНЫ")

        print("1. Настроить параметры и выбрать режим")
        print("2. Зашифровать")
        print("3. Расшифровать")
        print("0. Выход")

        cmd = input("Выберите действие: ")

        if cmd == '1':
            params = get_params()
        elif cmd == '2':
            if not params:
                print("Сначала настройте параметры!")
                continue
            text = input("Введите текст: ")
            res = encrypt(text, params['p'], params['g'], params['y'], params['k_list'])
            print(f"Шифртекст: {res}")
        elif cmd == '3':
            if not params:
                print("Сначала настройте параметры!")
                continue
            cipher = input("Введите шифртекст (цифры): ")
            try:
                res = decrypt(cipher, params['p'], params['x'])
                print(f"Результат: {res}")
            except Exception as e:
                print(f"Ошибка расшифровки: {e}")
        elif cmd == '0':
            break

if __name__ == "__main__":
    main()

# Эта капуста зеленая, все равно что это зеленая капуста.