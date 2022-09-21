class Voiceroid2Options:
    _skpeakers=None

    def __init__(
            self, 
            speakerName :str = "琴葉茜", 
            speakerStyle :str = "ノーマル",
            volume :float = 2.0, 
            speed :float = 1.0, 
            pitch :float = 1.0, 
            intonation: float = 1.0,
            speaker_id: str = None,
            pauseMiddle : int = 80,
            pauseLong : int = 100,
            pauseSentence : int = 400,
            voiceroidMasterVolume : float = 1,
        ):
        self.engine = "voiceroid2"
        if speaker_id is None:
            self.speaker_id = Voiceroid2Options.get_speaker_id(speakerName,speakerStyle)
        else:
            self.speaker_id = speaker_id
        self.volume = volume
        self.speed = speed
        self.pitch = pitch
        self.intonation = intonation
        self.pauseMiddle = pauseMiddle
        self.pauseLong = pauseLong
        self.pauseSentence = pauseSentence
        self.masterVolume = voiceroidMasterVolume

    @classmethod
    def get_speakers(cls):
        if Voiceroid2Options._skpeakers is None:
            Voiceroid2Options.set_speakers()
        return Voiceroid2Options._skpeakers

    @classmethod
    def set_speakers(cls):
        Voiceroid2Options._skpeakers = {}
        speakers = Voiceroid2Options._skpeakers
        speakers["琴葉茜"] = {}
        speakers["琴葉茜"]["ノーマル"] = "akane_west_44:standard"
        speakers["琴葉茜"]["関西弁"] = "akane_west_44:standard_kansai"

        speakers["琴葉葵"] = {}
        speakers["琴葉葵"]["ノーマル"] = "aoi_44:standard"
        speakers["琴葉葵"]["関西弁"] = "aoi_44:standard_kansai"

        speakers["琴葉茜_v2"] = {}
        speakers["琴葉茜_v2"]["ノーマル"] = "akane_west_emo_44:standard"
        speakers["琴葉茜_v2"]["関西弁"] = "akane_west_emo_44:standard_kansai"

        speakers["琴葉葵_v2"] = {}
        speakers["琴葉葵_v2"]["ノーマル"] = "aoi_emo_44:standard"
        speakers["琴葉葵_v2"]["関西弁"] = "aoi_emo_44:standard_kansai"
        
        speakers["東北きりたん"] = {}
        speakers["東北きりたん"]["ノーマル"] = "kiritan_44:standard"

        speakers["東北イタコ_v2"] = {}
        speakers["東北イタコ_v2"]["ノーマル"] = "itako_emo_44:standard"

        speakers["東北ずん子"] = {}
        speakers["東北ずん子"]["ノーマル"] = "zunko_44:standard"

        speakers["東北ずん子_v2"] = {}
        speakers["東北ずん子_v2"]["ノーマル"] = "zunko_emo_44:standard"

        speakers["結月ゆかり"] = {}
        speakers["結月ゆかり"]["ノーマル"] = "yukari_44:standard"

        speakers["結月ゆかり_v2"] = {}
        speakers["結月ゆかり_v2"]["ノーマル"] = "yukari_44:standard"

        speakers["京町セイカ"] = {}
        speakers["京町セイカ"]["ノーマル"] = "seika_44:standard"

        speakers["弦巻マキ"] = {}
        speakers["弦巻マキ"]["ノーマル"] = "tamiyasu_44:standard"

        speakers["紲星あかり_v2"] = {}
        speakers["紲星あかり_v2"]["ノーマル"] = "akari_44:standard"



    @classmethod
    def get_speaker_id(cls, name, style):
        return Voiceroid2Options.get_speakers()[name][style]

