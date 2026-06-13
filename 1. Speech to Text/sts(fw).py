# This code uses the faster-whisper library to transcribe audio files in the 'Audios' directory and saves the transcriptions in JSON format in the 'jsons' directory. Each JSON file contains metadata about the transcription, including the number, title, start and end times of each segment, and the full transcribed text. The model used for transcription is the "large-v2" version of Whisper, and it runs on a CUDA-enabled GPU with float16 precision for faster processing.

from faster_whisper import WhisperModel
import json
import os

model = WhisperModel("large-v2", device="cuda", compute_type="float16")

audios = os.listdir('Audios')

for audio in audios:
    number = audio.split(' -')[0]
    title = audio.split('- ')[1].split('.mp3')[0]
    print(number, title)

    segments, info = model.transcribe(
        f'Audios/{audio}',
        language='hi',
        task='translate',
        word_timestamps=False
    )

    chunks = []
    full_text = ""

    for segment in segments:
        full_text += segment.text

        chunks.append({
            'number': number,
            'title': title,
            'start': segment.start,
            'end': segment.end,
            'text': segment.text
        })

    chunks_metadata = {
        'chunks': chunks,
        'text': full_text
    }

    with open(f'jsons/{audio}.json', 'w') as f:
        json.dump(chunks_metadata, f)