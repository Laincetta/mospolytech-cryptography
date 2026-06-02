"""
Блок K: ОБМЕН КЛЮЧАМИ
28. Обмен ключами по Диффи-Хеллману  (ЛАБКРИПТ_2022)

Общие параметры: простое n и основание a (первообразный корень, 1 < a < n).
Пользователи A и B выбирают секретные ключи K_A, K_B из [2, n-1] и вычисляют
открытые ключи:
    Y_A = a^K_A mod n,   Y_B = a^K_B mod n.
После обмена Y_A, Y_B по открытому каналу общий секрет:
    K = Y_B^K_A mod n = Y_A^K_B mod n = a^(K_A·K_B) mod n.
Стойкость опирается на трудность дискретного логарифмирования.
"""


def is_prime(n):
    """Проверка числа на простоту (перебор до корня)."""
    if n < 2: return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0: return False
    return True

def compute_keys(n, a, KA, KB):
    """Вычисление открытых ключей и общего секрета."""
    # Открытые ключи (публичные)
    YA = pow(a, KA, n)
    YB = pow(a, KB, n)
    # Общие секретные ключи
    Ka = pow(YB, KA, n)
    Kb = pow(YA, KB, n)
    return YA, YB, Ka, Kb

def diffie_hellman_cipher():
    print("\n--- АЛГОРИТМ ДИФФИ-ХЕЛЛМАНА ---")

    # 1. Ввод и валидация n
    while True:
        try:
            n = int(input("Введите простое n (модуль): "))
            if is_prime(n): break
            print("Ошибка: n должно быть простым!")
        except ValueError:
            print("Ошибка: введите целое число.")

    # 2. Ввод и валидация a
    while True:
        try:
            a = int(input(f"Введите основание a (1 < a < {n}): "))
            if 1 < a < n: break
            print(f"Ошибка: a должно быть в диапазоне (1, {n}).")
        except ValueError:
            print("Ошибка: введите целое число.")

    # 3. Ввод секретов
    print("\n[Пользователь A]")
    try:
        KA = int(input(f"Введите секретный ключ KA (2..{n - 1}): "))
    except ValueError:
        return "\nОшибка: некорректный ввод секрета KA."

    print("[Пользователь B]")
    try:
        KB = int(input(f"Введите секретный ключ KB (2..{n - 1}): "))
    except ValueError:
        return "\nОшибка: некорректный ввод секрета KB."

    # 4. Расчет
    YA, YB, Ka, Kb = compute_keys(n, a, KA, KB)

    # 5. Проверки безопасности (коллизии)
    error = None
    if Ka <= 1 or Kb <= 1:
        error = "Секретный ключ K должен быть > 1"
    elif Ka == KA or Kb == KA:
        error = f"Секретный ключ K совпал с закрытым ключом KA ({KA})"
    elif Ka == KB or Kb == KB:
        error = f"Секретный ключ K совпал с закрытым ключом KB ({KB})"
    elif Ka == YA or Kb == YA:
        error = f"Секретный ключ K совпал с открытым ключом YA ({YA})"
    elif Ka == YB or Kb == YB:
        error = f"Секретный ключ K совпал с открытым ключом YB ({YB})"

    if error:
        return f"\nОШИБКА БЕЗОПАСНОСТИ: {error}"

    # 6. Формирование результата
    result = (f"\n--- ИТОГИ ОБМЕНА ---\n"
              f"Открытый ключ YA = {YA}\n"
              f"Открытый ключ YB = {YB}\n"
              f"Секретный ключ Ka = {Ka}\n"
              f"Секретный ключ Kb = {Kb}\n")

    if Ka == Kb:
        result += f"Статус: Ключи успешно согласованы (K = {Ka})"
    else:
        result += "Статус: Ошибка! Ключи не совпадают."

    return result

def main():
    while True:
        print("\n=== ГЛАВНОЕ МЕНЮ ===")
        print("1. Начать обмен ключами")
        print("2. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            print(diffie_hellman_cipher())
        elif choice == '2':
            print("Завершение работы.")
            break
        else:
            print("Неверный ввод.")

if __name__ == "__main__":
    main()