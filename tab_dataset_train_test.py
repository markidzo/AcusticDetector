import json
import os
import pandas as pd

# ==== ШЛЯХИ ====
INPUT_JSON = "marking_data.json"      # твій json
OUTPUT_EXCEL = "tab_dataset.xlsx"     # excel файл

def main():

    # --- Читаємо JSON ---
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    total_files = 0
    processed = 0
    skipped_multi = 0
    skipped_empty = 0

    # --- Проходимо по файлах ---
    for item in data["data"]:
        total_files += 1

        file_path = item["path"]
        file_name = os.path.basename(file_path)
        mark_list = item.get("mark_list", [])

        # Якщо немає сегментів
        if not mark_list:
            skipped_empty += 1
            continue

        # Збираємо всі унікальні labels
        unique_labels = set()

        for segment in mark_list:
            for label in segment.get("labels", []):
                unique_labels.add(label)

        # Якщо більше 1 класу — пропускаємо
        if len(unique_labels) != 1:
            skipped_multi += 1
            continue

        label = list(unique_labels)[0]

        # --- Рахуємо тривалість ---
        total_duration = 0.0

        for segment in mark_list:
            start = float(segment["start"])
            end = float(segment["end"])
            total_duration += (end - start)

        # Округлюємо до 3 знаків
        total_duration = round(total_duration, 3)

        # Додаємо рядок
        rows.append([label, file_name, total_duration])
        processed += 1

    # --- Створюємо DataFrame ---
    df = pd.DataFrame(rows, columns=["Label", "FileName", "Duration_sec"])

    # --- Зберігаємо в Excel ---
    df.to_excel(OUTPUT_EXCEL, index=False)

    # --- Статистика ---
    print("\n📊 Статистика:")
    print("Всього у JSON:", total_files)
    print("Оброблено:", processed)
    print("Пропущено (кілька labels):", skipped_multi)
    print("Пропущено (порожній mark_list):", skipped_empty)

    print("\n✅ Готово!")
    print("Збережено у файл:", OUTPUT_EXCEL)


if __name__ == "__main__":
    main()