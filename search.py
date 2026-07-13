import os
import json
from openai import OpenAI

def get_all_library_files():
    """Эта функция сама обходит все папки вашей библиотеки и собирает пути к файлам"""
    file_paths = []
    # Начинаем сканирование с текущей папки проекта
    for root, dirs, files in os.walk("."):
        # Игнорируем скрытые папки GitHub и системные файлы
        if '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            # Строим чистый путь, например: "documents/templates/info.txt"
            relative_path = os.path.relpath(os.path.join(root, file), ".")
            # Игнорируем сам файл поиска
            if relative_path != "search.py":
                file_paths.append(relative_path)
    return file_paths

def ask_github_model(user_query):
    # Берем токен из системы безопасности компьютера (так намного надежнее и профессиональнее)
    github_token = os.environ.get("GITHUB_TOKEN")
    
    if not github_token:
        return "Ошибка: Вы не настроили GITHUB_TOKEN на своем компьютере!"

    # Подключаемся к GitHub Models
    client = OpenAI(
        base_url="https://azure.com",
        api_key=github_token,
    )

    # Собираем актуальный список файлов прямо сейчас
    current_files = get_all_library_files()

    SYSTEM_PROMPT = """
    Ты — умный файловый навигатор по этой библиотеке. Твоя задача — помочь пользователю найти нужные файлы. 
    Ты видишь ТОЛЬКО список путей к файлам. У тебя НЕТ доступа к их содержимому. 
    Ориентируйся строго по названиям папок, названиям файлов и их расширениям.

    ПРАВИЛА:
    1. Анализируй смысл и синонимы запроса пользователя.
    2. Возвращай строго чистый список подходящих путей к файлам.
    3. Не пиши никаких приветствий, объяснений или лишнего текста.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Список файлов библиотеки:\n{json.dumps(current_files, indent=2)}\n\nЗапрос: '{user_query}'"}
        ],
        temperature=0.1,
    )

    return response.choices.message.content

# --- Пример запуска поиска ---
# =====================================================================
# ИНТЕРФЕЙС ДЛЯ ПОЛЬЗОВАТЕЛЯ (ИНТЕРАКТИВНАЯ СТРОКА)
# =====================================================================
if __name__ == "__main__":
    print("=== Умный поиск в библиотеке через GitHub Models запущен ===")
    print("Для завершения работы введите слово: выход\n")
    
    while True:
        # Программа останавливается и ждет, пока вы введете текст
        user_request = input("Введите ваш поисковый запрос: ")
        
        # Если вы ввели слово "выход", программа закроется
        if user_request.strip().lower() == "выход":
            print("Работа завершена. До свидания!")
            break
            
        # Если вы ничего не ввели, пропускаем шаг
        if not user_request.strip():
            continue
            
        print("Ищем в папочной структуре библиотеки...")
        result = ask_github_model(user_request)
        
        print("\n[Результат поиска от GitHub Models]:")
        print(result)
        print("-" * 50 + "\n")
