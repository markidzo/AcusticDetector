import json

# Шляхи до файлів
input_json_path = "label_audio.json"   # вихідний JSON
output_json_path = "label_change_result.json" # куди збережемо результат

# JSON
with open(input_json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Оновгення шляхів
for item in data.get("data", []):
    original_path = item.get("path", "")
    #  "/data" на потрібний шлях
    item["path"] = original_path.replace("/data", "C:/labelstudio/data/media")

# Зберіг. результат у новий JSON
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Шляхи успішно оновлено і збережено у {output_json_path}")

