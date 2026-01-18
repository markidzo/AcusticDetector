from pathlib import Path
import hashlib
import numpy as np
import soundfile as sf
import librosa
import json

SAMPLE_RATE = 16000
DEBUG_MODE = False  # False
NORMALIZE = False


def write_wav(
        path: Path,
        y: np.ndarray,
        sr: int,
        normalize: bool = False
):
    path.parent.mkdir(parents=True, exist_ok=True)

    y = np.asarray(y, dtype=np.float32)

    if normalize:
        peak = np.max(np.abs(y))
        if peak > 0:
            y = y / peak

    y = np.clip(y, -1.0, 1.0)

    sf.write(
        file=str(path),
        data=y,
        samplerate=sr,
        subtype="PCM_16"
    )


def prepare_dataset(marking_data,
                    labels,
                    samples_dir,
                    slice_length: float  # slice length (seconds)
                    ):
    slice_win = int(slice_length * SAMPLE_RATE)
    step = slice_win // 2

    label_map = {c: i for i, c in enumerate(labels)}
    sample_marks = []

    for item in marking_data:
        file_path = Path(item['path'])
        new_file_name = file_path.stem if DEBUG_MODE else hashlib.md5(item['path'].encode("utf-8")).hexdigest()
        idx = 0
        data_, _ = librosa.load(file_path, sr=SAMPLE_RATE, mono=False)
        data = data_[0] if data_.ndim > 1 else data_

        for mark_item in item.get('mark_list', []):
            start = mark_item['start']
            end = mark_item['end']
            if end - start < slice_length:
                print(f'[ERROR] Sample duration is too small: {mark_item}. File: {item}')

            print('Next Mark')
            start_id = int(start * SAMPLE_RATE)
            end_id = int(end * SAMPLE_RATE)

            while start_id < end_id:
                delta = end_id - start_id
                if delta < slice_win:
                    if delta / step > 1.3:
                        start_id = end_id - slice_win
                    else:
                        break

                new_file_path = f"{samples_dir}/{new_file_name}-{idx:04d}.wav"
                idx += 1

                # TODO write to file
                print(f"{new_file_path} {(start_id / 16000):0.3f} {((start_id+slice_win) / 16000):0.3f}")
                # print(new_file_path, int(start_id / 16000), int((start_id + slice_win) / 16000))
                write_wav(Path(new_file_path),
                          data[start_id:start_id + slice_win],
                          SAMPLE_RATE,
                          normalize=NORMALIZE)

                # sample_labels = [label_map[lbl] for lbl in mark_item['labels']]
                sample_mark_item = {
                    'path': new_file_path,
                    'labels': mark_item['labels']
                }
                # if DEBUG_MODE:
                #     sample_mark_item['labels_'] = mark_item['labels']
                sample_marks.append(sample_mark_item)

                start_id += step

    for sample in sample_marks:
        print(sample)

    sample_descriptions_file = f"{samples_dir}/sample_descriptions.json"

    with open(sample_descriptions_file, "w", encoding="utf-8") as f:
        json.dump(sample_marks, f, ensure_ascii=False, indent=4)
    print(f"Файл '{sample_descriptions_file}' сформовано")


if __name__ == "__main__":
    marking_data_path = 'D:/WorkDataset/monitoring/code/Debug_Audio/module_1/marking_data.json'

    labels = [
        "ambient",
        "electric_noise",
        "friction",
        "gas_leak",
        "impact",
        "pump",
        "water_leak"
    ]

    marking_data = [
        {
            'id': 10,
            'path': 'C:/labelstudio/data/media/upload/9/4a855d94-Electric_Sparks_Sound_Effect.wav',
            "mark_list": [
                {
                    "start": 2.1,
                    "end": 7.66,
                    "labels": [
                        "electric_noise"
                    ]
                },
                {
                    "start": 8.8,
                    "end": 16.71,
                    "labels": [
                        "electric_noise"
                    ]
                },
                {
                    "start": 17.29,
                    "end": 28.74,
                    "labels": [
                        "electric_noise"
                    ]
                }
            ]
        }
    ]

    samples_dir = 'D:/WorkDataset/monitoring/code/Debug_Audio/module_1/debug_2'
    slice_length = 4.0

    prepare_dataset(marking_data,
                    labels,
                    samples_dir,
                    slice_length)

