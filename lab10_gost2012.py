import sys


def check_is_numeric(value):
    """Проверка, является ли строка числом."""
    try:
        int(value)
        return True, int(value)
    except ValueError:
        return False, None


def detect_input_type(text):
    """Определяет, HEX это или русский текст."""
    text = text.replace(' ', '')
    if len(text) == 0:
        return 'empty'
    if all(c in '0123456789abcdefABCDEF' for c in text):
        return 'hex'
    return 'text'


def is_prime(n):
    """Проверка числа на простоту."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def mod_inverse(k, p):
    """Нахождение обратного элемента по модулю p."""
    return pow(k, p - 2, p)


def add_points(P, Q, a, p):
    """Сложение двух точек на эллиптической кривой."""
    if P is None:
        return Q
    if Q is None:
        return P

    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if x1 == x2 and y1 == y2:
        numerator = (3 * x1 * x1 + a) % p
        denominator = (2 * y1) % p
    else:
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p

    lam = (numerator * mod_inverse(denominator, p)) % p

    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p

    return (x3, y3)


def multiply_point(k, P, a, p):
    """Умножение точки на скаляр."""
    if P is None or k == 0:
        return None

    result = None
    current = P
    k_bin = k

    while k_bin > 0:
        if k_bin & 1:
            result = add_points(result, current, a, p)
        current = add_points(current, current, a, p)
        k_bin >>= 1

    return result


def find_all_points(a, b, p):
    """Нахождение всех точек на кривой."""
    points = []
    for x in range(p):
        right_side = (pow(x, 3, p) + a * x + b) % p
        for y in range(p):
            if pow(y, 2, p) == right_side:
                points.append((x, y))
    return points


def format_points(points):
    """Форматирует список точек для вывода."""
    if not points:
        return "Точек не найдено"
    return ' '.join([f"({x},{y})" for x, y in points])


def factorize(n):
    """Разложение числа на простые множители."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def find_subgroup_order(a, b, p):
    """Вычисление порядка подгруппы."""
    points = find_all_points(a, b, p)
    n = len(points) + 1
    factors = factorize(n)
    q = max(factors)
    return q, points


def find_points_orders(points, a, p):
    """Нахождение порядков точек."""
    orders = {}
    for point in points:
        order = find_point_order(point, a, p)
        orders[point] = order
    return orders


def find_point_order(P, a, p):
    """Находит порядок точки P на кривой."""
    if P is None:
        return 1
    current = P
    order = 1
    while current is not None:
        current = add_points(current, P, a, p)
        order += 1
        if order > p * 2:
            break
    return order


def find_cryptographic_points(points, orders):
    """Выбор точек, пригодных для криптографических целей."""
    suitable = []
    for point in points:
        order = orders[point]
        if order > 2:
            factors = factorize(order)
            is_prime_order = (len(factors) == 1 and order > 1)
            if is_prime_order:
                suitable.append(point)
    return suitable


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


# Алфавит и таблицы соответствия
ALPHABET = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
CHAR_TO_NUM = {c: i + 1 for i, c in enumerate(ALPHABET)}
NUM_TO_CHAR = {v: k for k, v in CHAR_TO_NUM.items()}


def preprocess_text(text, encrypt_mode=True):
    """Предобработка текста (замена спецсимволов)."""
    replacements = {
        '.': 'тчк', ',': 'зпт', '-': 'тире', ':': 'двтчк',
        '!': 'вскл', '?': 'впрс', '(': 'скб', ')': 'скб',
        '"': 'квч', "'": 'квч', '—': 'длтире'
    }
    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)
    return text


def postprocess_text(text):
    """Постобработка текста (обратная замена спецсимволов)."""
    replacements = {
        'тчк': '.', 'зпт': ',', 'тире': '-', 'двтчк': ':',
        'вскл': '!', 'впрс': '?', 'скб': '(', 'квч': '"',
        'длтире': '—'
    }
    for sequence, symbol in replacements.items():
        text = text.replace(sequence, symbol)
    return text


def gost2012_cipher(text, question2):
    """
    ГОСТ Р 34.10-2012 — цифровая подпись на основе эллиптических кривых.
    question2 = 1 – создание подписи
    question2 = 2 – проверка подписи
    """
    if question2 == 1:  # СОЗДАНИЕ ПОДПИСИ
        # Ввод модуля p
        while True:
            try:
                p_str = input("Введите модуль p (простое число): ")
                is_valid, p_val = check_is_numeric(p_str)
                if not is_valid:
                    print("Ошибка: введите целое число")
                    continue
                p = int(p_val)
                if not is_prime(p):
                    print("Ошибка: p должно быть простым числом")
                    continue
                break
            except ValueError:
                print("Ошибка: введите целое число")

        # Ввод параметров кривой
        while True:
            try:
                a_str = input("Введите параметр a: ")
                b_str = input("Введите параметр b: ")
                is_num_a, a = check_is_numeric(a_str)
                is_num_b, b = check_is_numeric(b_str)
                if not (is_num_a and is_num_b):
                    print("Ошибка: введите числа")
                    continue
                a = int(a)
                b = int(b)
                break
            except ValueError:
                print("Ошибка ввода")

        # Вычисление порядка подгруппы и вывод всех точек
        try:
            q, points = find_subgroup_order(a, b, p)
            print(f"Точки кривой: {format_points(points)}")
            print(f"Вычисленный порядок подгруппы q = {q}")
        except Exception as e:
            return f"Ошибка при вычислении порядка подгруппы: {e}"

        # Находим криптографические точки
        orders = find_points_orders(points, a, p)
        crypto_points = find_cryptographic_points(points, orders)
        print(f"Точки, пригодные для криптографии: {crypto_points}")

        # Ввод базовой точки G
        while True:
            try:
                G_input = input("Введите координаты базовой точки G (x y): ").split()
                if len(G_input) != 2:
                    print("Ошибка: введите два числа (x и y)")
                    continue
                Gx = int(G_input[0])
                Gy = int(G_input[1])
                G = (Gx, Gy)

                right_side = (pow(Gx, 3, p) + a * Gx + b) % p
                if pow(Gy, 2, p) != right_side:
                    print(f"Ошибка: точка ({Gx},{Gy}) не лежит на кривой")
                    continue
                break
            except ValueError:
                print("Ошибка ввода")

        # Вычисляем порядок точки G
        q_point = find_point_order(G, a, p)
        print(f"Порядок точки G: q = {q_point}")

        # Ввод секретного ключа x
        while True:
            try:
                x_str = input(f"Введите секретный ключ x (1 < x < {q_point}): ")
                is_valid, x = check_is_numeric(x_str)
                if not is_valid:
                    print("Ошибка: введите целое число")
                    continue
                x = int(x)
                if x <= 1 or x >= q_point:
                    print(f"Ошибка: x должно быть в диапазоне 1 < x < {q_point}")
                    continue
                break
            except ValueError:
                print("Ошибка: введите целое число")

        # Вычисление открытого ключа Y = [x]G
        Y = multiply_point(x, G, a, p)
        print(f"Открытый ключ Y = {Y}")

        # Ввод сообщения
        message = text.replace(' ', '')
        if not message:
            return "Ошибка: пустое сообщение"

        # Предобработка сообщения
        processed = preprocess_text(message.lower())

        # Вычисление хеша
        hash_p = p
        h = hash_message(processed, hash_p)
        Hm = h % q_point

        if Hm == 0:
            Hm = 1

        print(f"\nХеш сообщения H(m) = {Hm}")

        # Генерация подписи
        while True:
            while True:
                try:
                    k_str = input(f"Введите k (1 ≤ k < {q_point}): ")
                    is_valid, k = check_is_numeric(k_str)
                    if not is_valid:
                        print("Ошибка: введите целое число")
                        continue
                    k = int(k)
                    if k < 1 or k >= q_point:
                        print(f"Ошибка: k должно быть в диапазоне 1 ≤ k < {q_point}")
                        continue
                    break
                except ValueError:
                    print("Ошибка: введите целое число")

            P = multiply_point(k, G, a, p)
            if P is None:
                print("Ошибка: P = None, выбираем другое k")
                continue
            x_P, y_P = P
            print(f"P = [k]G = ({x_P}, {y_P})")

            r = x_P % q_point
            if r == 0:
                print("r = 0, выбираем другое k")
                continue

            s = (k * Hm + r * x) % q_point
            if s == 0:
                print("s = 0, выбираем другое k")
                continue
            break

        result = (f"Хеш сообщения H(m) = {Hm}\n"
                  f"Подпись S = (r, s): ({r}, {s})\n"
                  f"Открытый ключ (p, a, b, G, Y, q): ({p}, {a}, {b}, {G}, {Y}, {q_point})")
        return result

    else:  # ПРОВЕРКА ПОДПИСИ
        # Ввод параметров кривой
        while True:
            try:
                p_str = input("Введите модуль p: ")
                a_str = input("Введите параметр a: ")
                b_str = input("Введите параметр b: ")
                is_num_p, p = check_is_numeric(p_str)
                is_num_a, a = check_is_numeric(a_str)
                is_num_b, b = check_is_numeric(b_str)
                if not (is_num_p and is_num_a and is_num_b):
                    print("Ошибка: введите числа")
                    continue
                p = int(p)
                a = int(a)
                b = int(b)
                break
            except ValueError:
                print("Ошибка ввода")

        # Вывод точек кривой
        try:
            _, points = find_subgroup_order(a, b, p)
            print(f"Точки кривой: {format_points(points)}")
        except:
            pass

        # Ввод базовой точки G
        while True:
            try:
                G_input = input("Введите координаты базовой точки G (x y): ").split()
                if len(G_input) != 2:
                    print("Ошибка: введите два числа (x и y)")
                    continue
                Gx = int(G_input[0])
                Gy = int(G_input[1])
                G = (Gx, Gy)
                break
            except ValueError:
                print("Ошибка ввода")

        # Вычисляем порядок точки G
        q = find_point_order(G, a, p)
        print(f"Порядок точки G: q = {q}")

        # Ввод открытого ключа Y
        while True:
            try:
                Y_input = input("Введите координаты открытого ключа Y (x y): ").split()
                if len(Y_input) != 2:
                    print("Ошибка: введите два числа (x и y)")
                    continue
                Yx = int(Y_input[0])
                Yy = int(Y_input[1])
                Y = (Yx, Yy)
                break
            except ValueError:
                print("Ошибка ввода")

        # Ввод сообщения
        message = text.replace(' ', '')
        if not message:
            return "Ошибка: пустое сообщение"

        # Предобработка сообщения
        processed = preprocess_text(message.lower())

        # Ввод подписи
        while True:
            try:
                r_str = input("Введите первую часть подписи r: ")
                s_str = input("Введите вторую часть подписи s: ")
                is_num_r, r = check_is_numeric(r_str)
                is_num_s, s = check_is_numeric(s_str)
                if not (is_num_r and is_num_s):
                    print("Ошибка: введите целые числа")
                    continue
                r = int(r)
                s = int(s)
                break
            except ValueError:
                print("Ошибка: введите целое число")

        if r <= 0 or r >= q or s <= 0 or s >= q:
            return f"Ошибка: r или s вне допустимого диапазона (0, {q})"

        # Вычисление хеша сообщения
        hash_p = p
        h = hash_message(processed, hash_p)
        Hm = h % q

        if Hm == 0:
            Hm = 1

        print(f"\nХеш сообщения H(m) = {Hm}")

        h_inv = mod_inverse(Hm, q)

        u1 = (s * h_inv) % q
        u2 = (-r * h_inv) % q

        point1 = multiply_point(u1, G, a, p)
        point2 = multiply_point(u2, Y, a, p)
        P = add_points(point1, point2, a, p)

        if P is None:
            return "ПОДПИСЬ НЕВЕРНА! (P = 0)"

        x_P, y_P = P
        x_P_mod_q = x_P % q

        if x_P_mod_q == r:
            return f"ПОДПИСЬ ВЕРНА! (x_P mod q = {x_P_mod_q} = r = {r})"
        else:
            return f"ПОДПИСЬ НЕВЕРНА! (x_P mod q = {x_P_mod_q} ≠ r = {r})"


def main():
    while True:
        print("\n" + "=" * 50)
        print("ГОСТ Р 34.10-2012 - ЭЛЛИПТИЧЕСКАЯ ПОДПИСЬ")
        print("=" * 50)
        print("1. Создать подпись")
        print("2. Проверить подпись")
        print("3. Выход")
        print("-" * 50)

        choice = input("Выберите действие (1-3): ").strip()

        if choice == '1':
            text = input("Введите сообщение: ").strip()
            if text:
                result = gost2012_cipher(text, 1)
                print("\n" + "=" * 50)
                print("РЕЗУЛЬТАТ:")
                print("=" * 50)
                print(result)
            else:
                print("Ошибка: сообщение не может быть пустым!")

        elif choice == '2':
            text = input("Введите сообщение: ").strip()
            if text:
                result = gost2012_cipher(text, 2)
                print("\n" + "=" * 50)
                print("РЕЗУЛЬТАТ:")
                print("=" * 50)
                print(result)
            else:
                print("Ошибка: сообщение не может быть пустым!")

        elif choice == '3':
            print("До свидания!")
            sys.exit(0)

        else:
            print("Ошибка: выберите 1, 2 или 3")


if __name__ == "__main__":
    main()