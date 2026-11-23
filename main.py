import os
import traceback
from dotenv import load_dotenv
from graph import app
from export import export_to_docx, export_to_pdf

def get_project_description():
    print("\nОпишите ваш программный проект.")
    print("Можно использовать несколько строк.")
    print("Для завершения ввода нажмите Enter на пустой строке.\n")

    lines = []

    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    return "\n".join(lines).strip()

def print_result(result):
    print("\n" + "=" * 60)
    print("                 РЕЗУЛЬТАТ АНАЛИЗА")
    print("=" * 60)

    print("\nАНАЛИЗ ПРОЕКТА:")
    print(result["analysis"])

    print("\nПРОВЕРКА ОБЯЗАТЕЛЬНЫХ КРИТЕРИЕВ:")

    print(
        f"Что необходимо разработать: "
        f"{'Да' if result['has_product'] else 'Нет'}"
    )

    print(
        f"Назначение проекта: "
        f"{'Да' if result['has_purpose'] else 'Нет'}"
    )

    print(
        f"Основные функции: "
        f"{'Да' if result['has_features'] else 'Нет'}"
    )

    # Если информации достаточно
    if result["is_sufficient"]:

        print("\n[OK] ИНФОРМАЦИИ ДОСТАТОЧНО!")

        print("\nПОШАГОВЫЙ ПЛАН РАЗРАБОТКИ:\n")

        print(result["develop_plan"])

    # Если информации недостаточно
    elif result.get("iteration", 0) >= 3:
        print("\n[!] Достигнут лимит уточнений.")
        print("Необходимо дополнить описание проекта вручную.")
    else:

        print("\n[!] ИНФОРМАЦИИ НЕДОСТАТОЧНО!")

        print("\nУТОЧНЯЮЩИЕ ВОПРОСЫ:\n")

        print(result["questions"])

    print("\n" + "=" * 60)
    print("                 АНАЛИЗ ЗАВЕРШЕН")
    print("=" * 60)

def main():
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        print("False, GROQ UNFOUND")
        print("Check .env")
        return
    print("=" * 60)
    print("             AI-ПРОВЕРКА ТЕХНИЧЕСКОГО ЗАДАНИЯ")
    print("=" * 60)

    project_description = get_project_description()
    if not project_description:
        print("\nОшибка в описании проекта")
        return

    initial_state = {
        "project_description": project_description,
        "iteration": 0
    }

    try:
        print("LangGraph loading...")

        result = app.invoke(initial_state)

        print_result(result)
        if result.get("specification"):
            print("\n========== ЭКСПОРТ ТЕХНИЧЕСКОГО ЗАДАНИЯ ==========")

            print("1. Сохранить в PDF")
            print("2. Сохранить в DOCX")
            print("3. Сохранить в обоих форматах")
            print("0. Пропустить экспорт")

            choice = input("\nВаш выбор:").strip()
            try:
                if choice == "1":
                    export_to_pdf(result["specification"])
                elif choice == "2":
                    export_to_docx(result["specification"])
                elif choice == "3":
                    export_to_docx(result["specification"])
                    export_to_pdf(result["specification"])
                elif choice == "0":
                    print("Export cancel")
                else:
                    print("Некорректный выбор.")
            except Exception:
                    import traceback
                    traceback.print_exc()
        if result.get("specification"):
            print("\n========TASK=========")
            for section, content in result["specification"].items():
                print(f"\n--- {section.upper()} ---")

                if isinstance(content, list):
                    for item in content:
                        print(item)
                elif isinstance(content, dict):
                    for key, value in content.items():
                        print(f"{key}: {value}")
                else:
                    print(content)
    except Exception:

        print("\n[ERROR] Подробная информация об ошибке:")
        traceback.print_exc()

if __name__ == "__main__":

    main()



