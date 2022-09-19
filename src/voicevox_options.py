import requests

class VoicevoxOptions:
    _skpeakers=None

    def __init__(
            self, 
            speakerName :str = "四国めたん", 
            speakerStyle :str = "ノーマル",
            volume :float = 2.0, 
            speed :float = 1.0, 
            pitch :float = 0, 
            intonation: float = 1.0
        ):

        self.speaker_id = VoicevoxOptions.get_speaker_id(speakerName,speakerStyle)
        self.volume = volume
        self.speed = speed
        self.pitch = pitch
        self.intonation = intonation

    @classmethod
    def get_speakers(cls):
        if VoicevoxOptions._skpeakers is None:
            VoicevoxOptions.set_speakers()
        return VoicevoxOptions._skpeakers

    @classmethod
    def set_speakers(cls):
        response = VoicevoxOptions.load_speakers()
        VoicevoxOptions._skpeakers = {}
        speakers = VoicevoxOptions._skpeakers
        for speaker in response:
            speakers[speaker["name"]] = {}
            styles = speaker["styles"]
            for style in styles:
                speakers[speaker["name"]][style["name"]] = style["id"]
    
    @classmethod
    def get_speaker_id(cls, name, style):
        return VoicevoxOptions.get_speakers()[name][style]

    @classmethod
    def load_speakers(cls):
        url = f"http://localhost:50021/speakers"
        r = requests.get(url, timeout=(10.0, 300.0))
        # print(r.status_code)
        if r.status_code == 200:
            return r.json()
