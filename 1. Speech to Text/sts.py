# This code uses the Whisper model to transcribe audio files in the 'Audios' directory and saves the transcriptions along with metadata in JSON format in the 'jsons' directory. Each audio file is expected to be named in the format "number - title.mp3". The transcriptions are done in Hindi and the task is set to 'translate' to get the translated text. The resulting JSON files contain both the segmented chunks of text with their corresponding start and end times, as well as the full transcribed text.

import whisper
import json
import os

model = whisper.load_model('large-v2')

audios = os.listdir('Audios')

for audio in audios:
    number = audio.split(' -')[0]
    title = audio.split('- ')[1].split('.mp3')[0]
    print(number, title)
    result = model.transcribe(audio=f'Audios/{audio}',
                              language='hi',
                              task='translate',
                              word_timestamps=False)
    
    chunks = []

    for segment in result['segments']:
        chunks.append({
            'number': number,
            'title': title,
            'start': segment['start'],
            'end': segment['end'],
            'text': segment['text']
        })

    chunks_metadata = {'chunks': chunks, 'text': result['text']}

    with open(f'jsons/{audio}.json', 'w') as f:
        json.dump(chunks_metadata, f)