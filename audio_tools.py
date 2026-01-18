import librosa
import os
import json
import soundfile as sf
from pathlib import Path
from numba.core.types import Boolean

SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2
SAMPLE_WIDTH_BITS = SAMPLE_WIDTH * 8
SAMPLE_SUBTYPE = 'PCM_16'

LABEL_STUDIO_JSON = "label_audio.json"
OUTPUT_JSON = "marking_data.json"


def ensure_dir(path: Path) -> None:
    """Створює директорію, якщо її не існує."""
    path.mkdir(parents=True, exist_ok=True)


def get_wav_files(source_path: Path) -> list:
    files = []

    for src_file in source_path.rglob("*"):
        # Якщо це директорія, пропускаємо
        if src_file.is_dir():
            continue

        # Обробляємо тільки .wav
        if src_file.suffix.lower() != ".wav":
            continue

        files.append(src_file)

    return files


def process_file(file_path: Path, source_path: Path, destination_path: Path) -> (Boolean, str):
    try:
        # Перевіряємо sample_width - librosa автоматично переводить у float32
        # info = sf.info(file_path)
        # if info.subtype != SAMPLE_SUBTYPE:  # 16-bit PCM
        #     message = f"Skipping {file_path.name}, sample_width != 2 (not {SAMPLE_SUBTYPE}). Subtype: {info.subtype}"
        #     return False, message

        # Завантажуємо WAV (всі канали)
        data, sample_rate = librosa.load(file_path, sr=None, mono=False)

        # Якщо стерео або більше каналів → беремо нульовий
        if data.ndim > 1:
            data = data[0, :]

        # Ресемплінг
        if sample_rate != SAMPLE_RATE:
            data = librosa.resample(data, orig_sr=sample_rate, target_sr=SAMPLE_RATE)
            print(f"File {file_path.name} is resampled from {sample_rate / 1000:0.3f} kHz "
                  f"to {SAMPLE_RATE / 1000:0.3f} kHz")

        # Запис у dst
        relative = file_path.relative_to(source_path)
        new_file_path = destination_path / relative
        new_file_dir = new_file_path.parent
        ensure_dir(new_file_dir)
        sf.write(new_file_path, data, SAMPLE_RATE)

        # print(file_path, new_file_path)  # for debug mode

        return True, ''
    except Exception as e:
        print(f"[ERROR]: {e}")
        exit(-1)


def files_preprocessing(source_path: Path, destination_path: Path):
    print(f"Source folder: {source_path}")
    print(f"Destination folder: {destination_path}")

    if not source_path.exists():
        print(f"[ERROR] Source folder {source_path} does not exist.")
        return

    ensure_dir(destination_path)

    files = get_wav_files(source_path)
    # print(*files, sep='\n')
    print(f"Found {len(files)} wav-files in {source_path}")

    errors = []
    for file_path in files:
        res, message = process_file(file_path, source_path, destination_path)
        if not res:
            errors.append(message)

    print("Processing finished.")
    print(f'Total files: {len(files)}, processed: {len(files) - len(errors)}, errors: {len(errors)}')
    if len(errors) > 0:
        print(*errors, sep="\n")


def load_label_studio_data(label_studio_json: Path,
                           actual_path: str  # Фактичний шлях до даних Label Studio
                           ):
    with open(label_studio_json, "r", encoding="utf-8") as f:
        full_json = json.load(f)

    label_list = set()
    processed_data = []
    max_id = -1

    for item in full_json:
        if not isinstance(item, dict):
            continue

        item_id = item.get("id", None)
        if item_id is not None:
            max_id = max(max_id, item_id)

        raw_marks = item.get("fault_type", [])
        marks = []
        for m in raw_marks:
            labels = m.get("labels", [])
            if len(labels) == 0:
                print(f"[ERROR]. Empty labels in: {item}")
                continue

            for label_name in labels:
                label_list.add(label_name)

            marks.append({
                "start": round(m.get("start", 1)),
                "end": round(m.get("end", 1)),
                "labels": labels
            })

        # Оновлюємо шляхи
        original_path = item.get("audio", "")
        if len(original_path) == 0:
            print(f"[ERROR]. Empty path: {item}")
            continue
        actual_path = original_path.replace("/data", actual_label_studio_path)

        processed_data.append({
            "id": item_id,
            "path": str(actual_path),
            "mark_list": marks
        })

    return sorted(label_list), processed_data, max_id


def marking_json_formation(source_path: Path,
                           label_studio_json_path: Path,
                           actual_label_studio_path: str,
                           output_json_path: Path):
    # --- 1. Завантажуємо та переформатовуємо JSON із Label Studio ---
    labels, processed_data, max_id = load_label_studio_data(label_studio_json_path, actual_label_studio_path)
    labels_set = set(labels)

      # унікалізація
    data_list = processed_data[:]  # копія існуючих записів

    result = []
    # skip_folders = ["ambient", "Label"]
    skip_folders = ["Label"]

    # --- 2. Рекурсивний обхід ---
    for root, dirs, files in os.walk(source_path):
        root_path = Path(root)

        if root_path.parts[-1].lower() in [x.lower() for x in skip_folders]:
            continue

        if "NoLabel" not in root_path.parts and "ambient" not in root_path.parts:
            continue

        try:
            label = root_path.relative_to(source_path).parts[0]  # TODO для чого?
        except:
            continue

        for file in files:
            if file.lower().endswith(".wav"):
                file_path = root_path / file

                data, sr = sf.read(file_path)
                duration = len(data) / sr
                max_id += 1  # новий id

                result.append({
                    "id": max_id,
                    "path": str(file_path),
                    "mark_list": [
                        {
                            "start": 0.0,
                            "end": round(duration, 2),
                            "labels": [label]
                        }
                    ]
                })

                labels_set.add(label)

    # --- 3. Додаємо нові дані в кінець ---
    data_list.extend(result)

    # --- 4. Формуємо фінальний JSON ---
    final_output = {
        "labels": sorted(labels_set),
        "data": data_list
    }

    # --- 5. Запис у файл ---
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)

    print(f"Готово! Дані збережено у {output_json_path}")


if __name__ == "__main__":
    # ---------- Step 1. Формування датасету: моно та ресемпелінг ----------
    # source_path = Path("debug_full") / "src"  # папка звідки читаємо WAV
    # destination_path = Path("debug_full") / "dst"  # папка куди записуємо результати
    # files_preprocessing(source_path, destination_path)

    # # ---------- Step 2. Формування json-файлу розмітки ----------
    source_path = Path("debug_full") / "dst"  # папка звідки читаємо WAV
    label_studio_json_path = Path("label_studio.json")
    actual_label_studio_path = "C:/labelstudio/data/media"
    output_json_path = Path("marking_data.json")
    marking_json_formation(source_path,
                           label_studio_json_path,
                           actual_label_studio_path,
                           output_json_path)
    # # ---------------------------------------------------------



    # TODO DEBUG
    # source_path = Path("debug_1") / "dst"  # папка звідки читаємо WAV
    # label_studio_json_path = Path("label_studio_test.json")
    # actual_label_studio_path = "C:/labelstudio/data/media"
    # output_json_path = Path("marking_data_test.json")
    # marking_json_formation(source_path,
    #                        label_studio_json_path,
    #                        actual_label_studio_path,
    #                        output_json_path)
