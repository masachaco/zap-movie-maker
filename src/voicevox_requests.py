import requests
import time
from util import *
import json

def get_voicevox_audio_query(text, voice_vox_options):
    """
    VOICEVOXから合成音声用のクエリを発行する
    http://localhost:50021/docs#/%E3%82%AF%E3%82%A8%E3%83%AA%E4%BD%9C%E6%88%90/audio_query_audio_query_post
    """
    for i in range(3):
        url = f"http://localhost:50021/audio_query"
        r = requests.post(url, params={"text": text, "speaker": voice_vox_options["speaker_id"]}, timeout=(10.0, 300.0))
        if r.status_code == 200:
            return r.json()
        time.sleep(1)


def get_voicevox_synthesis(query, voicevox_options):
    """
    VOICEVOXと合成音声用のクエリを使用して、音声合成を行う
    http://localhost:50021/docs#/%E9%9F%B3%E5%A3%B0%E5%90%88%E6%88%90/synthesis_synthesis_post
    """
    # voicevox_options = {
    #     "pitch": Clip.current_character.voicevoxOptions.pitch,
    #     "speed": Clip.current_character.voicevoxOptions.speed,
    #     "intonation": Clip.current_character.voicevoxOptions.intonation,
    #     "speaker_id": Clip.current_character.voicevoxOptions.speaker_id,
    # }
    speaker_id = voicevox_options["speaker_id"]
    query["speedScale"] = voicevox_options["speed"]
    query["pitchScale"] = voicevox_options["pitch"]
    query["intonationScale"] = voicevox_options["intonation"]

    for i in range(3):
        url = f"http://localhost:50021/synthesis"
        r = requests.post(
            url,
            params={"speaker": speaker_id},
            data=json.dumps(query),
            timeout=(10.0, 300.0),
        )
        if r.status_code == 200:
            return r.content
        time.sleep(1)


def get_voicevox_audio(text, voicevox_options):
    """
    VOICEVOXから音声を生成
    """
    audio_query = get_voicevox_audio_query(text, voicevox_options)
    return get_voicevox_synthesis(audio_query, voicevox_options)



def voice_vox_towav(text, audio_filename, voice_vox_options):
    """
    VOICEVOXから音声を生成してファイルに保存
    """

    audio_filepath = get_path(f"./voicevox_wav/{audio_filename}")
    # キャッシュが存在する場合はそれを使う
    if os.path.exists(audio_filepath):
        return

    voicevoix_audio = get_voicevox_audio(text, voice_vox_options)
    with open(audio_filepath, "wb") as fp:
        fp.write(voicevoix_audio)

