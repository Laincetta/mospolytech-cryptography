def replace(text):
    replacements = {
        '.': 'ТЧК',
        '—': 'ТИРЕ',
        '-': 'ТИРЕ',
        ',': 'ЗПТ',
        '!': 'ВСКЛ',
        '?': 'ВПРС',
        '«': 'КВЧЛ',
        '»': 'КВЧП',
        ' ': 'ПРБ'
    }
    result = ""
    for i in text.upper():
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

def is_prime(num):
    prime = num > 1 and (num % 2 != 0 or num == 2) and (num % 3 != 0 or num == 3)
    i = 5;
    d = 2;

    while prime and i * i <= num:
        prime = num % i != 0
        i += d
        d = 6 - d
    return prime

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def check_E(E,euler_N):
    return 1 < E < euler_N and gcd(E, euler_N) == 1

ALPH = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

def main_menu():
    keys = {"P": None, "Q": None, "N": None, "E": None, "D": None, "block_size": 0}

    while True:
        print("\n--- ГЛАВНОЕ МЕНЮ RSA ---")
        print(f"Текущие ключи: E={keys['E']}, N={keys['N']} (D={keys['D']})")
        print("1. Установить/Изменить параметры (P, Q, E)")
        print("2. Зашифровать")
        print("3. Расшифровать")
        print("4. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            while True:
                p = int(input('Введите простое число P: '))
                while not is_prime(p):
                    p = int(input('Ошибка! Введите ПРОСТОЕ число P: '))

                q = int(input('Введите простое число Q: '))
                while not is_prime(q):
                    q = int(input('Ошибка! Введите ПРОСТОЕ число Q: '))

                n = p * q
                if n >= 33:
                    break
                else:
                    print(f"Ошибка! N = {n}, а должно быть >= 33 (размер алфавита).")
                    print("Задайте числа P и Q больше.")

            euler_n = (p - 1) * (q - 1)
            print(f"Число N = {n}, f(N) = {euler_n}")

            while True:
                e = int(input(f'Введите E (1 < E < {euler_n} и взаимопростое с {euler_n}): '))

                if not check_E(e, euler_n):
                    print("Некорректное E (не входит в диапазон или не взаимопростое с f(N)).")
                    continue

                d = pow(e, -1, euler_n)

                if e == d:
                    print(f"Внимание: E и D совпали ({e} = {d}). Перезадайте параметр E")
                else:
                    break

            keys.update({"P": p, "Q": q, "N": n, "E": e, "D": d, "block_size": len(str(n))})
            print("Параметры успешно сохранены!")

        elif choice == '2':
            if keys["E"] is None:
                print("Сначала установите параметры (пункт 1)!")
                continue

            text = input('Введите текст для шифрования: ')
            processed = replace(text)

            cipher_parts = []
            for char in processed:
                if char not in ALPH:
                    continue
                m = ALPH.index(char) + 1
                c = pow(m, keys["E"], keys["N"])
                cipher_parts.append(str(c).zfill(keys["block_size"]))

            full_cipher = "".join(cipher_parts)
            print(f"Зашифрованный текст (цифры): {full_cipher}")

        elif choice == '3':
            if keys["D"] is None:
                print("Сначала установите параметры!")
                continue

            cipher_str = input('Введите шифртекст для расшифровки: ')
            step = keys["block_size"]

            try:
                decrypted_chars = []
                for i in range(0, len(cipher_str), step):
                    block = int(cipher_str[i:i + step])
                    m = pow(block, keys["D"], keys["N"])
                    decrypted_chars.append(ALPH[m - 1])

                final_text = restore("".join(decrypted_chars))
                print(f"Расшифрованный текст: {final_text}")
            except Exception as e:
                print(f"Ошибка при расшифровке. Проверьте правильность строки и ключей. ({e})")

        elif choice == '4':
            print("Программа завершила работу")
            break
        else:
            print("Неверный выбор.")

if __name__ == '__main__':
    main_menu()

# Эта капуста зеленая, все равно что это зеленая капуста.