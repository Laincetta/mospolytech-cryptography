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


ALPHABET = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"  # Без Ё и Й согласно документу


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


# Хеш-функция квадратичной свертки из вашего документа
def get_hash(text, p):
    h = 0
    text = text.upper()
    for char in text:
        if char in ALPHABET:
            m_i = ALPHABET.find(char) + 1
            h = ((h + m_i) ** 2) % p
    return h


def get_params():
    print("\n--- Настройка ключей Эль-Гамаля ---")
    p = get_int_input("Введите простое число P (рекомендуется большое): ",
                      lambda x: is_prime(x), "Число должно быть простым.")

    g = get_int_input(f"Введите G (G < {p}): ",
                      lambda x: 1 < x < p, f"G должно быть в диапазоне (1, {p}).")

    x = get_int_input(f"Введите секретный ключ X (1 < X < {p - 1}): ",
                      lambda val: 1 < val < p - 1, "Неверный диапазон для X.")

    y = pow(g, x, p)
    print(f"Открытый ключ Y = G^X mod P = {y}")

    return {'p': p, 'g': g, 'x': x, 'y': y}


def sign_message(message, p, g, x):
    # 1. Хеширование
    m = get_hash(replace(message), p - 1)
    if m == 0: m = 1  # m должно быть в интервале (1, p-1)

    print(f"Хеш сообщения (m): {m}")

    # 2. Выбор случайного K, взаимно простого с (P-1)
    while True:
        k = random.randint(2, p - 2)
        if math.gcd(k, p - 1) == 1:
            break

    # 3. Вычисление a = G^k mod P
    a = pow(g, k, p)

    # 4. Вычисление b из уравнения: m = (x*a + k*b) mod (p-1)
    # k*b = (m - x*a) mod (p-1)
    # b = (m - x*a) * k^(-1) mod (p-1)
    k_inv = pow(k, -1, p - 1)
    b = (k_inv * (m - x * a)) % (p - 1)

    return a, b


def verify_signature(message, a, b, p, g, y):
    if not (0 < a < p): return False

    # 1. Хеширование полученного сообщения
    m = get_hash(replace(message), p - 1)
    if m == 0: m = 1

    # 2. Проверка условия: (Y^a * a^b) mod P == G^m mod P
    left_side = (pow(y, a, p) * pow(a, b, p)) % p
    right_side = pow(g, m, p)

    print(f"A1 (Y^a * a^b mod P): {left_side}")
    print(f"A2 (G^m mod P): {right_side}")

    return left_side == right_side


def main():
    params = None
    while True:
        print("\n=== ЭЦП ЭЛЬ-ГАМАЛЯ ===")
        if params:
            print(f"Параметры: P={params['p']}, G={params['g']}, Y={params['y']} (X={params['x']})")

        print("1. Установить ключи")
        print("2. Подписать сообщение")
        print("3. Проверить подпись")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            params = get_params()
        elif choice == '2':
            if not params: continue
            msg = input("Введите текст для подписи: ")
            a, b = sign_message(msg, params['p'], params['g'], params['x'])
            print(f"Подпись S = (a: {a}, b: {b})")
        elif choice == '3':
            if not params: continue
            msg = input("Введите сообщение: ")
            a = int(input("Введите компонент подписи a: "))
            b = int(input("Введите компонент подписи b: "))

            if verify_signature(msg, a, b, params['p'], params['g'], params['y']):
                print("РЕЗУЛЬТАТ: Подпись верна!")
            else:
                print("РЕЗУЛЬТАТ: Подпись НЕВЕРНА!")
        elif choice == '0':
            break


if __name__ == "__main__":
    main()