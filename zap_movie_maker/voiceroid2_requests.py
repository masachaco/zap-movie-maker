from util import *
import pyvcroid2
import time
import winsound


def voiceroid2_towav(text, audio_filename, voice_vox_options):
    """
    VOICEVOXから音声を生成してファイルに保存
    """
    with pyvcroid2.VcRoid2() as vc:
        voice = voice_vox_options["speaker_id"].split(":")[0]
        style = voice_vox_options["speaker_id"].split(":")[1]
        vc.loadLanguage(style)
        vc.loadVoice(voice)
        print("発話スタイル:",voice,style)
        # Show parameters
        # print("Volume   : min={}, max={}, def={}, val={}".format(vc.param.minVolume, vc.param.maxVolume, vc.param.defaultVolume, vc.param.volume))
        # print("Speed    : min={}, max={}, def={}, val={}".format(vc.param.minSpeed, vc.param.maxSpeed, vc.param.defaultSpeed, vc.param.speed))
        # print("Pitch    : min={}, max={}, def={}, val={}".format(vc.param.minPitch, vc.param.maxPitch, vc.param.defaultPitch, vc.param.pitch))
        # print("Emphasis : min={}, max={}, def={}, val={}".format(vc.param.minEmphasis, vc.param.maxEmphasis, vc.param.defaultEmphasis, vc.param.emphasis))
        # print("PauseMiddle   : min={}, max={}, def={}, val={}".format(vc.param.minPauseMiddle, vc.param.maxPauseMiddle, vc.param.defaultPauseMiddle, vc.param.pauseMiddle))
        # print("PauseLong     : min={}, max={}, def={}, val={}".format(vc.param.minPauseLong, vc.param.maxPauseLong, vc.param.defaultPauseLong, vc.param.pauseLong))
        # print("PauseSentence : min={}, max={}, def={}, val={}".format(vc.param.minPauseSentence, vc.param.maxPauseSentence, vc.param.defaultPauseSentence, vc.param.pauseSentence))
        # print("MasterVolume  : min={}, max={}, def={}, val={}".format(vc.param.minMasterVolume, vc.param.maxMasterVolume, vc.param.defaultMasterVolume, vc.param.masterVolume))

        # "voice_option": {
        #     "pitch": self.current_character.voicevoxOptions.pitch,
        #     "speed": self.current_character.voicevoxOptions.speed,
        #     "intonation": self.current_character.voicevoxOptions.intonation,
        #     "speaker_id": self.current_character.voicevoxOptions.speaker_id,
        #     "is_same_timing": is_same_timing,
        #     "absolute_time":absolute_time,
        #     "timing_offset": timing_offset
        # }
        # Set parameters
        vc.param.volume = 2
        vc.param.speed = float(voice_vox_options["speed"])
        vc.param.pitch = float(voice_vox_options["pitch"])
        vc.param.emphasis = float(voice_vox_options["intonation"])
        vc.param.pauseMiddle = 80
        vc.param.pauseLong = 100
        vc.param.pauseSentence = 200
        vc.param.masterVolume = 1

        # Text to speech
        speech, tts_events = vc.textToSpeech(text)
        audio_filepath = get_path(f"./voicevox_wav/{audio_filename}")
        print("ファイルを出力します",text)
        with open(audio_filepath, "wb") as fp:
            fp.write(speech)

        # Play speech and display phonetic labels simultaneously
        # t = threading.Thread(target=display_phonetic_label, args=(tts_events,))
        # t.start()
        # winsound.PlaySound(speech, winsound.SND_MEMORY)
        # t.join()
    
# voiceroid2_towav("ずんだもんです", "test.wav", {"speed":1.5,"pitch":1,"intonation":1,"speaker_id": "akane_west_emo_44:standard"})