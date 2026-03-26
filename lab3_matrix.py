import numpy as np


def get_matrix():
    """Ввод элементов матрицы ключа 3x3 с проверкой на обратимость."""
    print("\nВведите элементы матрицы 3x3 по очереди:")
    matrix = []
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
        matrix.append(row)

    matrix_np = np.array(matrix)
    # Считаем определитель для проверки
    det = np.linalg.det(matrix_np)

    if abs(det) < 1e-10:
        print("\nОшибка: Определитель равен 0, матрица не подходит!")
        return None

    print("\nКлюч успешно установлен:")
    print(matrix_np)
    return matrix_np


def text_to_nums(text):
    """Преобразование текста в числа (А=1...Я=32). Пробел = 0."""
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


def encrypt_logic(text, matrix):
    """Шифрование: C = A * B."""
    nums = text_to_nums(text)

    # Дополняем нулями (индекс пробела) до кратности 3
    while len(nums) % 3 != 0:
        nums.append(0)

    vecs = np.array(nums).reshape(-1, 3)
    result = []
    for v in vecs:
        res_vec = matrix.dot(v)  # Умножение матрицы на вектор-блок
        result.extend(res_vec)

    return result


def decrypt_logic(cipher_nums, matrix):
    """Расшифрование: B = A^-1 * C."""
    # Вычисляем обратную матрицу
    inv_matrix = np.linalg.inv(matrix)

    vecs = np.array(cipher_nums).reshape(-1, 3)
    decoded_nums = []
    for v in vecs:
        res_vec = inv_matrix.dot(v)  # Умножение обратной матрицы на вектор шифра
        decoded_nums.extend(res_vec)

    return nums_to_text(decoded_nums)


def main():
    matrix = None

    while True:
        print("\n--- МЕНЮ ---")
        print("1. Ввести/Сменить ключ (матрицу)")
        print("2. Зашифровать текст")
        print("3. Расшифровать числа")
        print("4. Выход")

        choice = input("Выберите действие: ").strip()

        if choice == '1':
            matrix = get_matrix()

        elif choice == '2':
            if matrix is None:
                print("Сначала введите ключ!")
                continue

            user_text = input("Введите текст: ")
            cipher_result = encrypt_logic(user_text, matrix)
            print(f"\nЗашифрованные числа:\n{' '.join(map(str, cipher_result))}")

        elif choice == '3':
            if matrix is None:
                print("Сначала введите ключ!")
                continue

            try:
                raw_input = input("Введите числа через пробел: ")
                cipher_nums = list(map(float, raw_input.split()))

                # Теперь длина не нужна, функция сама отсечет лишние пробелы в конце
                decrypted_text = decrypt_logic(cipher_nums, matrix)
                print(f"\nРасшифрованный текст: {decrypted_text}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == '4':
            print("Выход.")
            break


if __name__ == "__main__":
    main()