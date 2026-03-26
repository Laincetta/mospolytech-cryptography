import math
import ast

# Твой алфавит
ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def replace_special_chars(text):
    replacements = {'.': 'ТЧК', ',': 'ЗПТ', ' ': 'ПРБ', '?': 'ВПРС', '!': 'ВСКЛ'}
    result = ""
    for char in text.upper():
        if char in ALPHABET:
            result += char
        else:
            result += replacements.get(char, '')
    return result


# --- Математика ECC ---

def mod_inv(n, p):
    try:
        return pow(n % p, -1, p)
    except:
        return None


def add_points(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P == Q:
        if y1 == 0: return None
        num = (3 * x1 ** 2 + a) % p
        den = (2 * y1) % p
    else:
        num = (y2 - y1) % p
        den = (x2 - x1) % p
    inv = mod_inv(den, p)
    if inv is None: return None
    lam = (num * inv) % p
    x3 = (lam ** 2 - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def scalar_mult(k, P, a, p):
    R = None
    Q = P
    while k > 0:
        if k % 2 == 1: R = add_points(R, Q, a, p)
        Q = add_points(Q, Q, a, p)
        k //= 2
    return R


def get_all_points(a, b, p):
    pts = []
    for x in range(p):
        y_sq = (x ** 3 + a * x + b) % p
        for y in range(p):
            if (y ** 2) % p == y_sq:
                pts.append((x, y))
    return pts


def find_point_order(G, a, p):
    if G is None: return 1
    q = 1
    temp = G
    while temp is not None:
        temp = add_points(temp, G, a, p)
        q += 1
        if q > 1000: break
    return q


# --- Интерфейс ---

def main():
    params = {}
    while True:
        print("\n" + "=" * 50)
        print("--- ECC ---")
        print("1. Параметры кривой (a, b, p)")
        print("2. Ввод G, ключей и расчет порядка q")
        print("3. ЗАШИФРОВАТЬ ТЕКСТ")
        print("4. РАСШИФРОВАТЬ ТЕКСТ (показ m)")
        print("0. Выход")
        choice = input("Выбор: ")

        if choice == '1':
            params['a'] = int(input("Введите a: "))
            params['b'] = int(input("Введите b: "))
            params['p'] = int(input("Введите p: "))
            all_pts = get_all_points(params['a'], params['b'], params['p'])
            params['all_pts'] = all_pts
            print(f"\nТочки на плоскости: {all_pts}")
            print(f"Кол-во точек: {len(all_pts)}")

        elif choice == '2':
            if 'p' not in params: print("Сначала пункт 1!"); continue
            gx, gy = int(input("Gx: ")), int(input("Gy: "))
            params['G'] = (gx, gy)
            q = find_point_order(params['G'], params['a'], params['p'])
            params['q'] = q
            print(f"Порядок точки G (q): {q}")
            params['cb'] = int(input(f"Секретный ключ Cb: "))
            params['k'] = int(input(f"Эфемерный ключ k: "))
            params['Db'] = scalar_mult(params['cb'], params['G'], params['a'], params['p'])
            print(f"Открытый ключ Db: {params['Db']}")

        elif choice == '3':
            if 'Db' not in params: print("Сначала пункт 2!"); continue
            text = input("Текст: ")
            prepared = replace_special_chars(text)
            R = scalar_mult(params['k'], params['G'], params['a'], params['p'])
            P_point = scalar_mult(params['k'], params['Db'], params['a'], params['p'])

            print(f"\n[Шифрование] R: {R}, P: {P_point}")
            cipher_list = []
            for char in prepared:
                m = ALPHABET.index(char) + 1
                e = (m * P_point[0]) % params['p']
                cipher_list.append((R, e))
                print(f"'{char}' -> m:{m} -> e:{e}")
            print(f"\nИТОГ: {cipher_list}")

        elif choice == '4':
            if 'cb' not in params: print("Нужен Cb!"); continue
            raw = input("Вставь список [((x, y), e), ...]: ")
            try:
                data = ast.literal_eval(raw)
                result = ""
                print("\n[Расшифровка]")
                print(f"{'e':<5} | {'Точка Q':<15} | {'m':<5} | {'Буква'}")
                print("-" * 40)

                for R_point, e in data:
                    # Q = Cb * R = k * Cb * G = k * Db = P
                    Q = scalar_mult(params['cb'], R_point, params['a'], params['p'])
                    if Q:
                        inv_x = mod_inv(Q[0], params['p'])
                        if inv_x:
                            m = (e * inv_x) % params['p']
                            idx = (m - 1) % 32
                            char = ALPHABET[idx]
                            result += char
                            print(f"{e:<5} | {str(Q):<15} | {m:<5} | {char}")

                print("-" * 40)
                print(f"РЕЗУЛЬТАТ: {result}")
            except Exception as err:
                print(f"Ошибка формата: {err}")

        elif choice == '0':
            break


if __name__ == "__main__":
    main()