import random

ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
CHAR_TO_NUM = {c: i + 1 for i, c in enumerate(ALPHABET)}
NUM_TO_CHAR = {v: k for k, v in CHAR_TO_NUM.items()}


def check_is_numeric(value):
    """Проверка, является ли строка числом"""
    try:
        int(value)
        return True, value
    except ValueError:
        return False, None


def is_prime(n):
    """Проверка числа на простоту."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def gcd(a, b):
    """Наибольший общий делитель."""
    while b:
        a, b = b, a % b
    return a


def mod_inverse(a, m):
    """Нахождение обратного элемента по модулю m."""
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m


def egcd(a, b):
    """Расширенный алгоритм Евклида."""
    if a == 0:
        return b, 0, 1
    g, y, x = egcd(b % a, a)
    return g, x - (b // a) * y, y


def hash_message(message, p):
    """Хеширование сообщения."""
    h = 0
    for char in message.lower():
        if char in CHAR_TO_NUM:
            Mi = CHAR_TO_NUM[char]
        else:
            Mi = ord(char) % 32
        h = (h + Mi) ** 2 % p
    return h


def find_prime_factors(n):
    """Поиск простых множителей числа."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            if d not in factors:
                factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def sign_message(text):
    """Создание подписи"""
    # Ввод p
    while True:
        try:
            p_str = input("Введите большое простое число p: ")
            is_valid, p_val = check_is_numeric(p_str)
            if not is_valid:
                print("Ошибка: введите целое число")
                continue
            p = int(p_val)
            if not is_prime(p):
                print("Ошибка: p должно быть простым числом")
                continue
            if p < 32:
                print("Ошибка: p должно быть больше 32")
                continue
            break
        except ValueError:
            print("Ошибка: введите целое число")

    # Поиск простого сомножителя q числа (p-1)
    factors = find_prime_factors(p - 1)

    while True:
        try:
            q_str = input(f"Введите простой сомножитель q (из {factors}): ")
            is_valid, q_val = check_is_numeric(q_str)
            if not is_valid:
                print("Ошибка: введите целое число")
                continue
            q = int(q_val)
            if q not in factors:
                print(f"Ошибка: q должен быть простым сомножителем {p - 1}")
                continue
            break
        except ValueError:
            print("Ошибка: введите целое число")

    # Поиск a: 1 < a < p-1, a^q mod p = 1
    a_candidates = []
    for test_a in range(2, p - 1):
        if pow(test_a, q, p) == 1:
            a_candidates.append(test_a)
            if len(a_candidates) >= 5:
                break

    if not a_candidates:
        return "Ошибка: не удалось найти подходящее a. Попробуйте другие p и q."

    while True:
        try:
            a_str = input(f"Выберите a из {a_candidates}: ")
            is_valid, a_val = check_is_numeric(a_str)
            if not is_valid:
                print("Ошибка: введите целое число")
                continue
            a = int(a_val)
            if a not in a_candidates:
                print("Ошибка: выберите a из предложенных кандидатов")
                continue
            break
        except ValueError:
            print("Ошибка: введите целое число")

    # Ввод секретного ключа x
    while True:
        try:
            x_str = input(f"Введите секретный ключ x (1 < x < {q}): ")
            is_valid, x_val = check_is_numeric(x_str)
            if not is_valid:
                print("Ошибка: введите целое число")
                continue
            x = int(x_val)
            if x <= 1 or x >= q:
                print(f"Ошибка: x должно быть в диапазоне 1 < x < {q}")
                continue
            break
        except ValueError:
            print("Ошибка: введите целое число")

    # Вычисление открытого ключа y = a^x mod p
    y = pow(a, x, p)
    print(f"Открытый ключ y = {y}")

    # Ввод сообщения
    message = text.replace(' ', '')
    if not message:
        return "Ошибка: пустое сообщение"

    # Предобработка сообщения
    processed = message.lower()
    replacements = {
        '.': 'тчк', ',': 'зпт', '-': 'тире', ':': 'двтчк',
        '!': 'вскл', '?': 'впрс', '(': 'скб', ')': 'скб',
        '"': 'квч', "'": 'квч'
    }
    for symbol, replacement in replacements.items():
        processed = processed.replace(symbol, replacement)

    # Вычисление хеша
    hash_p = p
    h = hash_message(processed, hash_p)
    Hm = h % q

    if Hm == 0:
        Hm = 1

    print(f"\nХеш сообщения H(m) = {Hm}")

    # Генерация случайного k < q
    while True:
        k = random.randint(1, q - 1)
        print(f"Сгенерировано k = {k}")

        # Вычисление r = (a^k mod p) mod q
        r = pow(a, k, p) % q

        if r != 0:
            break
        print("r = 0, выбираем другое k")

    # Вычисление s = (x*r + k*H(m)) mod q
    s = (x * r + k * Hm) % q

    result = (f"\n{'=' * 50}\n"
              f"РЕЗУЛЬТАТ ПОДПИСАНИЯ\n"
              f"{'=' * 50}\n"
              f"Хеш сообщения H(m) = {Hm}\n"
              f"Подпись S = (r, s): ({r}, {s})\n"
              f"Открытый ключ (p, q, a, y): ({p}, {q}, {a}, {y})\n"
              f"{'=' * 50}")
    return result


def verify_signature(text):
    """Проверка подписи"""
    # Ввод параметров
    while True:
        try:
            p_str = input("Введите параметр p: ")
            is_valid, p_val = check_is_numeric(p_str)
            if not is_valid:
                print("Ошибка: введите целое число")
                continue
            p = int(p_val)
            break
        except ValueError:
            print("Ошибка: введите целое число")

    while True:
        try:
            q_str = input("Введите параметр q: ")
            is_valid, q_val = check_is_numeric(q_str)
            if not is_valid:
                print("Ошибка: введите целое число")
                continue
            q = int(q_val)
            break
        except ValueError:
            print("Ошибка: введите целое число")

    while True:
        try:
            a_str = input("Введите параметр a: ")
            is_valid, a_val = check_is_numeric(a_str)
            if not is_valid:
                print("Ошибка: введите целое число")
                continue
            a = int(a_val)
            break
        except ValueError:
            print("Ошибка: введите целое число")

    while True:
        try:
            y_str = input("Введите открытый ключ y: ")
            is_valid, y_val = check_is_numeric(y_str)
            if not is_valid:
                print("Ошибка: введите целое число")
                continue
            y = int(y_val)
            break
        except ValueError:
            print("Ошибка: введите целое число")

    # Ввод сообщения
    message = text.replace(' ', '')
    if not message:
        return "Ошибка: пустое сообщение"

    # Предобработка сообщения
    processed = message.lower()
    replacements = {
        '.': 'тчк', ',': 'зпт', '-': 'тире', ':': 'двтчк',
        '!': 'вскл', '?': 'впрс', '(': 'скб', ')': 'скб',
        '"': 'квч', "'": 'квч'
    }
    for symbol, replacement in replacements.items():
        processed = processed.replace(symbol, replacement)

    # Ввод подписи
    while True:
        try:
            r_str = input("Введите первую часть подписи r: ")
            is_valid, r_val = check_is_numeric(r_str)
            if not is_valid:
                print("Ошибка: введите целое число")
                continue
            r = int(r_val)
            break
        except ValueError:
            print("Ошибка: введите целое число")

    while True:
        try:
            s_str = input("Введите вторую часть подписи s: ")
            is_valid, s_val = check_is_numeric(s_str)
            if not is_valid:
                print("Ошибка: введите целое число")
                continue
            s = int(s_val)
            break
        except ValueError:
            print("Ошибка: введите целое число")

    signature = (r, s)

    # Вычисление хеша сообщения
    hash_p = p
    h = hash_message(processed, hash_p)
    Hm = h % q

    if Hm == 0:
        Hm = 1

    print(f"\nХеш сообщения H(m) = {Hm}")

    # Проверка подписи
    v = pow(Hm, q - 2, q)
    z1 = (s * v) % q
    z2 = ((q - r) * v) % q
    u = (pow(a, z1, p) * pow(y, z2, p)) % p % q

    print(f"\n{'=' * 50}")
    print("РЕЗУЛЬТАТ ПРОВЕРКИ")
    print(f"{'=' * 50}")
    if u == r:
        return f" ПОДПИСЬ ВЕРНА! (u = {u} = r = {r})"
    else:
        return f" ПОДПИСЬ НЕВЕРНА! (u = {u} ≠ r = {r})"


def print_header():
    """Вывод заголовка"""
    print("\n" + "=" * 50)
    print("ГОСТ Р 34.10-94 - ЦИФРОВАЯ ПОДПИСЬ")
    print("=" * 50)


def main_menu():
    """Главное меню программы"""
    while True:
        print_header()
        print("\n--- МЕНЮ ---")
        print("1. Создать подпись")
        print("2. Проверить подпись")
        print("3. Выход")

        choice = input("\nВыберите действие (1-3): ").strip()

        if choice == '1':
            print("\n--- СОЗДАНИЕ ПОДПИСИ ---")
            text = input("Введите текст для подписи: ")
            result = sign_message(text)
            print(result)
            input("\nНажмите Enter...")

        elif choice == '2':
            print("\n--- ПРОВЕРКА ПОДПИСИ ---")
            text = input("Введите текст для проверки: ")
            result = verify_signature(text)
            print(result)
            input("\nНажмите Enter...")

        elif choice == '3':
            print("\nДо свидания!")
            break

        else:
            print("\n Неверный выбор! Введите 1, 2 или 3.")
            input("\nНажмите Enter...")


if __name__ == "__main__":
    main_menu()