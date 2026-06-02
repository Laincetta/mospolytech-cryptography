"""
Блок С: ШИФРЫ БЛОЧНОЙ ЗАМЕНЫ
8. Матричный шифр  (ЛАБКРИПТ_2022)

Буквы нумеруются как элементы кольца (А=1…Я=32, пробел=0). n-грамма открытого
текста (вектор-блок B) умножается на ключевую матрицу A:
    вектор шифртекста  C = A · B,  по элементам  C_i = Σ_j a_ij · b_j.
Расшифрование — обратной матрицей:  B = A^(-1) · C.
Числовой эквивалент открытого слова обозначается T_Э.
"""

import numpy as np


def get_matrix():
    """Ввод ключевой матрицы A (3x3) с проверкой обратимости (det ≠ 0)."""
    print("\nВведите элементы матрицы 3x3 по очереди:")
    A_rows = []
    for i in range(3):
        row = []
        for j in range(3):
            while True:
                try:
                    val = int(input(f"Введите элемент a{i + 1}{j + 1}: "))
                    row.append(val)
                    break
                except ValueError:
                    print("Ошибка! Введите целое число.")
        A_rows.append(row)

    A = np.array(A_rows)
    # Считаем определитель |A| для проверки обратимости
    det = np.linalg.det(A)

    if abs(det) < 1e-10:
        print("\nОшибка: Определитель равен 0, матрица не подходит!")
        return None

    print("\nКлюч успешно установлен:")
    print(A)
    return A


def text_to_nums(text):
    """Числовой эквивалент T_Э: текст → числа (А=1...Я=32). Пробел = 0."""
    alphabet = " АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    return [alphabet.find(c.upper()) for c in text if c.upper() in alphabet]


def nums_to_text(nums):
    """Преобразование чисел в текст с очисткой от технических нулей на конце."""
    alphabet = " АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    res = ""
    for n in nums:
        idx = int(round(n))
        # Ограничиваем индекс рамками алфавита
        idx = max(0, min(idx, 32))
        res += alphabet[idx]

    # Убираем пробелы (нули) с правого края, которые добавились при дополнении блока
    return res.strip()


def replace(text):
    """Предобработка: знаки препинания и пробелы → буквенные коды (. → ТЧК и т. п.)."""
    replacements = {'.': 'ТЧК', '—': 'ТИРЕ', '–': 'ТИРЕ', '-': 'ТИРЕ', ',': 'ЗПТ',
                    '!': 'ВСКЛ', '?': 'ВПРС', '«': 'КВЧЛ', '»': 'КВЧП', ' ': 'ПРБ'}
    return "".join(replacements.get(c, c) for c in text.upper())


def restore(text):
    """Постобработка: буквенные коды → знаки препинания и пробелы (ТЧК → . и т. п.)."""
    replacements = {'ТЧК': '.', 'ТИРЕ': '—', 'ЗПТ': ',', 'ВСКЛ': '!',
                    'ВПРС': '?', 'КВЧЛ': '«', 'КВЧП': '»', 'ПРБ': ' '}
    for code, symbol in replacements.items():
        text = text.replace(code, symbol)
    return text


def encrypt_logic(text, A):
    """Шифрование: вектор шифртекста C = A · B (B — вектор-блок T_Э)."""
    nums = text_to_nums(replace(text))

    # Дополняем нулями (индекс пробела) до кратности 3 (триграммы)
    while len(nums) % 3 != 0:
        nums.append(0)

    blocks = np.array(nums).reshape(-1, 3)
    result = []
    for B in blocks:
        C = A.dot(B)  # C = A · B — умножение ключевой матрицы на вектор-блок
        result.extend(C)

    return result


def decrypt_logic(cipher_nums, A):
    """Расшифрование: вектор-блок B = A^(-1) · C."""
    # Вычисляем обратную матрицу A^(-1)
    A_inv = np.linalg.inv(A)

    blocks = np.array(cipher_nums).reshape(-1, 3)
    decoded_nums = []
    for C in blocks:
        B = A_inv.dot(C)  # B = A^(-1) · C — умножение обратной матрицы на вектор шифра
        decoded_nums.extend(B)

    return restore(nums_to_text(decoded_nums))


def main():
    A = None

    while True:
        print("\n--- МЕНЮ ---")
        print("1. Ввести/Сменить ключ (матрицу)")
        print("2. Зашифровать текст")
        print("3. Расшифровать числа")
        print("4. Выход")

        choice = input("Выберите действие: ").strip()

        if choice == '1':
            A = get_matrix()

        elif choice == '2':
            if A is None:
                print("Сначала введите ключ!")
                continue

            user_text = input("Введите текст: ")
            cipher_result = encrypt_logic(user_text, A)
            print(f"\nЗашифрованные числа:\n{' '.join(map(str, cipher_result))}")

        elif choice == '3':
            if A is None:
                print("Сначала введите ключ!")
                continue

            try:
                raw_input = input("Введите числа через пробел: ")
                cipher_nums = list(map(float, raw_input.split()))

                # Теперь длина не нужна, функция сама отсечет лишние пробелы в конце
                decrypted_text = decrypt_logic(cipher_nums, A)
                print(f"\nРасшифрованный текст: {decrypted_text}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == '4':
            print("Выход.")
            break


if __name__ == "__main__":
    main()