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

def hash(text, p):
    h = 0
    text = text.upper()
    for i in text:
        if i in ALPH:
            m_i = ALPH.find(i) + 1
            h = ((h + m_i) ** 2) % p
    return h

ALPH = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def main_menu():
    keys = {"P": None, "Q": None, "N": None, "E": None, "D": None}

    while True:
        print("\n--- МЕНЮ ЦИФРОВОЙ ПОДПИСИ (RSA) ---")
        if keys['N']:
            print(f"Ключи установлены: Открытый (E={keys['E']}, N={keys['N']}), Секретный (D={keys['D']})")
        else:
            print("Параметры не заданы.")

        print("1. Генерация ключей (P, Q, E)")
        print("2. Подписать сообщение (Создать S)")
        print("3. Проверить подпись (Проверить S)")
        print("4. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            p = int(input('Введите простое P: '))
            while not is_prime(p): p = int(input('Ошибка! Введите простое P: '))

            q = int(input('Введите простое Q: '))
            while not is_prime(q): q = int(input('Ошибка! Введите простое Q: '))

            n = p * q

            if p == q:
                print("ОШИБКА: P и Q не должны быть равны!")
                continue

            if n <= len(ALPH):
                print(f"ОШИБКА: Модуль N ({n}) слишком мал!")
                print(f"Для корректной работы с алфавитом из {len(ALPH)} букв, N должно быть больше {len(ALPH)}.")
                print("Выберите более крупные простые числа P и Q.")
                continue

            euler_n = (p - 1) * (q - 1)
            print(f"N = {n}, f(N) = {euler_n}")

            while True:
                e = int(input(f'Введите E (1 < E < {euler_n} и взаимопростое с {euler_n}): '))
                if check_E(e, euler_n):
                    d = pow(e, -1, euler_n)  # создание закрытого ключа
                    if e != d:
                        keys.update({"P": p, "Q": q, "N": n, "E": e, "D": d})
                        print("Ключи сохранены!")
                        break
                    else:
                        print("E и D совпали (вырожденный случай), выберите другое E.")
                else:
                    print("Некорректное E.")

        elif choice == '2':
            if not keys["N"]:
                print("Сначала создайте ключи!")
                continue

            message = input('Введите текст сообщения M: ')
            processed_m = replace(message)

            m_hash = hash(processed_m, keys["N"])
            print(f"Хеш-код сообщения (m): {m_hash}")

            s_signature = pow(m_hash, keys["D"], keys["N"])  # зашифрование хэша (создание подписи)
            print(f"Цифровая подпись (S): {s_signature}")
            print(f"Отправьте получателю сообщение и число S.")

        elif choice == '3':
            if not keys["N"]:
                print("Параметры RSA не заданы!")
                continue

            msg_to_verify = input('Введите полученное сообщение M: ')
            sig_to_verify = int(input('Введите полученную подпись S: '))

            processed_received = replace(msg_to_verify)
            m_prime = hash(processed_received, keys["N"])

            m_recovered = pow(sig_to_verify, keys["E"], keys["N"])

            print(f"Вычисленный хеш m': {m_prime}")
            print(f"Восстановленный из подписи хеш m: {m_recovered}")

            if m_prime == m_recovered:
                print("РЕЗУЛЬТАТ: Подпись ВЕРНА.")
            else:
                print("РЕЗУЛЬТАТ: Подпись НЕВЕРНА (сообщение было изменено)!")

        elif choice == '4':
            break

if __name__ == '__main__':
    main_menu()