from inspect import isfunction
from operator import is_
from unicodedata import name
import moviepy
from moviepy.editor import *
import requests
import os
import yaml
import csv
import hashlib
import time
import json
import win32com.client
import shutil

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

def set_bgm_repeat(bgm_clips, total_duration):
    """
    BGMを次のBGMの指定があるまでループさせる。
    最後に指定されたBGMは動画の最後までループさせる。
    TODO: 特にやっつけで作ってしまったので修正する
    """

    new_bgm_clips = []
    bgm = None
    while True:
        # 何もなかったら何もしない
        if len(new_bgm_clips) == 0 and len(bgm_clips) == 0:
            break

        # 先頭BGMは無条件で突っ込む
        if len(new_bgm_clips) == 0:
            bgm = bgm_clips.pop(0)
            new_bgm_clips.append(bgm)
            if len(bgm_clips) > 0:
                bgm = bgm_clips.pop(0)
            continue

        # 次に流す現在のBGMの再生位置を取得して
        current_time = bgm.start

        # 現在再生しているBGMが終わるタイミング
        before_bgm_end_time = new_bgm_clips[-1].start + new_bgm_clips[-1].duration
        # print("current:",current_time, "before:",before_bgm_end_time)

        # 最後のトラックで、動画のおわりより短かったらリピ－ト
        if (
            total_duration >= before_bgm_end_time
            and before_bgm_end_time >= bgm.start
            and len(bgm_clips) == 0
        ):
            repeat_bgm = bgm.set_start(before_bgm_end_time).set_duration(bgm.duration)
            new_bgm_clips.append(repeat_bgm)
            continue

        # # 最後のトラックで、動画のおわりより長かったらそこで終了
        if total_duration <= before_bgm_end_time and len(bgm_clips) == 0:
            break

        # 再生位置以下だったら現在のBGMをループ
        if before_bgm_end_time < current_time:
            repeat_bgm = (
                new_bgm_clips[-1]
                .set_start(before_bgm_end_time)
                .set_duration(new_bgm_clips[-1].duration)
            )
            new_bgm_clips.append(repeat_bgm)
            continue

        # 再生位置を超えていたら次のBGMに差し替える
        if before_bgm_end_time >= current_time:
            duration = new_bgm_clips[-1].duration
            new_bgm_clips[-1] = new_bgm_clips[-1].set_duration(
                duration - (before_bgm_end_time - current_time)
            )
            new_bgm_clips.append(bgm)
            if len(bgm_clips) == 0:
                break
            bgm = bgm_clips.pop(0)

    return new_bgm_clips

BASE_PATH = None
def get_base_path():
    """
    プロジェクトの配置されているディレクトリのフルパスを取得する
    """
    global BASE_PATH
    if BASE_PATH is None:
        before_path = os.getcwd()
        source_code_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(source_code_path)
        os.chdir("../")
        BASE_PATH = os.getcwd()
        os.chdir(before_path)
    return BASE_PATH


def get_path(path):
    before_path = os.getcwd()
    os.chdir(get_base_path())
    abspath = os.path.abspath(path)
    os.chdir(before_path)
    return abspath

def open_by_utf8(path):
    """
    Windowsで実行する際、デフォルトの文字エンコードが
    cp932(だいたいshift-jis)になっているのでUTF-8で読み込むようにする
    """
    return open(path, encoding="utf-8")


def load_conf(path):
    """
    conf.yamlを読み込む
    """

    with open_by_utf8(path) as file:
        return yaml.safe_load(file)


def load_script(path):
    """
    スクリプトを読み込む
    """

    with open_by_utf8(path) as file:
        data = file.read().split("\n")
        # 空行とコメント行はスキップ
        filtered_data = filter(lambda txt: (not txt.strip().startswith("#")) and (not txt.strip() == ""),data)

        # CSVをパース
        return csv.reader(list(filtered_data))


class VoicevoxOptions:
    _skpeakers=None

    def __init__(
            self, 
            speakerName :str = "四国めたん", 
            speakerStyle :str = "ノーマル",volume :float = 1.0, 
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

class TelopOptions:
    def __init__(self, text_color: str = "white", text_size: int = 25):
        self.text_color = text_color
        self.text_size = text_size

class CharacterVoice:
    def __init__(self, 
                voicevoxOptions: VoicevoxOptions = VoicevoxOptions(), 
                telopOptions: TelopOptions = TelopOptions(),
        ):
        self.voicevoxOptions = voicevoxOptions
        self.telopOptions = telopOptions

class CharacterImageSettings:
    def __init__(self, 
        x=0,
        y=0,
        resize=1
        ):
        self.x = x
        self.y = y
        self.resize = resize

class CharacterImageStyle:
    def __init__(self, 
                name="ノーマル",
                image_path="./resource/character/tachie-normal.png"
        ):
        self.image_path = image_path
        self.name = name

class Clip:
    config = None
    characters = {"default": CharacterVoice()}
    character_images = {}
    current_character = characters["default"]
    scripts = []
    movie = {
        "current_duration": 0,
        "main_visual_clips": [],
        "fullscreen_visual_clips":[],
        "text_clips": [],
        "se_clips": [],
        "bgm_clips": [],
        "wait_clips": [],
        "bgm_clips": [],
        "character_clips": {},
    }

    @classmethod
    def is_imagefile(cls, filetype):
        """
            簡易的に画像のファイルタイプを判定
        """
        return filetype == "png" or filetype == "jpg" or filetype == "jpeg" or filetype == "gif"

    @classmethod
    def main_visual_resize_ratio(cls, width, height):
        """
            メインビジュアルに表示する動画の拡大・縮小率を取得する
        """

        top_x = Clip.config["movie"]["background"]["main_vision_left_top_x"]
        top_y = Clip.config["movie"]["background"]["main_vision_left_top_y"]
        bottom_x = Clip.config["movie"]["background"]["main_vision_right_bottom_x"]
        bottom_y = Clip.config["movie"]["background"]["main_vision_right_bottom_y"]

        bg_width = bottom_x - top_x
        bg_height = bottom_y - top_y
        height_ratio = bg_height / height
        width_ratio = bg_width / width
        return width_ratio if width_ratio > height_ratio else height_ratio

    @classmethod
    def main_visual_fullscreen_resize_ratio(cls, width, height):
        """
            メインビジュアルに表示する動画の拡大・縮小率を取得する
        """

        top_x = 0
        top_y = 0
        bottom_x =1280
        bottom_y = 720

        bg_width = bottom_x - top_x
        bg_height = bottom_y - top_y
        height_ratio = bg_height / height
        width_ratio = bg_width / width
        return width_ratio if width_ratio > height_ratio else height_ratio


    @classmethod
    def cut_func(cls, from_sec, to_sec):
        def cut(t):
            ret = t+from_sec
            if (to_sec) <= (ret):
                return  to_sec
            return ret
        return cut

    @classmethod
    def create_main_visual_clip(cls, clips, current_duration, movie_filepath, options):
        """
            メインビジュアルにに使用するクリップを作成する
        """
        # この動画の前に再生している動画の再生時間を、この動画を再生するまでに伸ばす
        if len(clips) > 0:
            past_movie = clips[-1]
            if past_movie.duration != -1:
                past_movie_duration = current_duration - past_movie.start
                clips[-1] = past_movie.set_duration(past_movie_duration)

        filetype = movie_filepath.split(".")[-1].lower()
        
        if options["is_mute"]:
            mute_clip = TextClip(
                        " ",
                        size=(1, 1),
                        align="West",
                        fontsize=30,
                        color="white",
                )
            return mute_clip.set_duration(-1)

        main_visual_clip = None
        if (Clip.is_imagefile(filetype)):
            main_visual_clip = ImageClip(movie_filepath).set_start(current_duration).set_duration(1)
        else:
            main_visual_clip = VideoFileClip(movie_filepath).set_start(current_duration).set_duration(-1)
            from_sec = options["from"]
            to_sec = options["to"]
            main_visual_clip = main_visual_clip.fl_time(Clip.cut_func(from_sec, to_sec))

        # メインビジュアルの表示位置(左端)
        x = Clip.config["movie"]["background"]["main_vision_left_top_x"]
        y = Clip.config["movie"]["background"]["main_vision_left_top_y"]
        main_visual_potision = (x, y)
        # 動画サイズを自動調整する
        ratio = Clip.main_visual_resize_ratio(main_visual_clip.w, main_visual_clip.h)
        # フルスクリーン表示の場合
        if options["is_fullscreen"]:
            main_visual_potision = (0,0)
            ratio = Clip.main_visual_fullscreen_resize_ratio(main_visual_clip.w, main_visual_clip.h)
        
        main_visual_clip = main_visual_clip.set_position(main_visual_potision)
        main_visual_clip = moviepy.video.fx.resize.resize(main_visual_clip, ratio, ratio)
        main_visual_clip = main_visual_clip.fx(moviepy.audio.fx.all.volumex, 0)
        return main_visual_clip

    @classmethod
    def create_text_clip(cls,clips, text_clip_options, current_duration, has_audio):
        """
        テロップを作成する
        """
        # ファイル名はハッシュで振っておいて簡易的にキャッシュできるようにする
        # TODO: このハッシュ生成処理が重いので修正する。
        # TODO: パラメータ変更の場合古い音声を使ってしまうので修正する。
        telop_options = text_clip_options["telop_options"]
        say = text_clip_options["say"]
        hash = hashlib.md5(say.encode()).hexdigest()
        voice_vox_towav(say, f"{hash}.wav", text_clip_options["voice_option"])
        audioclip = AudioFileClip(get_path(f"./voicevox_wav/{hash}.wav"))
        
        # Windowsの場合バックスラッシュでファイルパスが切られているとフォントを読み込めないので置換する
        font_path = get_path(Clip.config["movie"]["text"]["font_normal"]).replace("\\", "/")
        
        telop = text_clip_options["telop"]
        print("telop:",telop)

        txtclip = TextClip(
            f"{telop}",
            method="label",
            size=(2000, 30),
            align="West",
            fontsize=float(telop_options.text_size),
            font=font_path,
            color=telop_options.text_color,
        )

        # テロップの表示位置
        x = Clip.config["movie"]["text"]["x"]
        y = Clip.config["movie"]["text"]["y"]
        text_position = (x, y)

        txtclip = txtclip.set_duration(float(audioclip.duration)).set_position(text_position).fx(moviepy.audio.fx.all.volumex, 1.2)

        # 読み上げる場合は音声を設定
        if has_audio:
            txtclip = txtclip.set_audio(audioclip)
        
        start_timing = current_duration
        if text_clip_options["voice_option"]["is_same_timing"] and len(clips) > 0:
            start_timing = clips[-1].start

        return txtclip.set_start(t=start_timing, change_end=True)
    
    @classmethod
    def create_audio_clip(cls, audio_clip_options, current_duration, volume):
        """
        オーディオクリップを作成する
        """
        file_path = audio_clip_options["file_path"]
        bgm = AudioFileClip(file_path)

        # TODO: 一旦透明なテキストクリップを使ってしまったけど別途オーディオだけ再生することができるはず
        bgmclip = TextClip(
            " ",
            size=(1, 1),
            align="West",
            fontsize=30,
            font=get_path(Clip.config["movie"]["text"]["font_normal"]),
            color="white",
        )
        bgmclip = bgmclip.set_duration(float(bgm.duration))
        bgmclip = bgmclip.set_audio(bgm).set_start(t=current_duration, change_end=True)
        bgmclip = bgmclip.fx(moviepy.audio.fx.all.volumex, volume)
        return bgmclip


    @classmethod
    def create_character_clip(slc, clips, current_duration, options):
        """
        立ち絵クリップを作成する
        """
        print(options)
        character_name = options["name"]
        character_image = options["image_settings"]
        character_style = options["style"]

        if character_name not in clips:
            clips[character_name] = []

        char_clips = clips[character_name]

        # この立ち絵の前に再生している立ち絵の再生時間を、この立ち絵を再生するまでに伸ばす
        if len(char_clips) > 0:
            past_char = char_clips[-1]
            past_char_duration = current_duration - past_char.start
            char_clips[-1] = past_char.set_duration(past_char_duration)

        char_clip = ImageClip(character_style.image_path).set_duration(1)

        # 立ち絵を拡大・縮小
        ratio = character_image.resize
        char_clip = moviepy.video.fx.resize.resize(char_clip, ratio, ratio)

        # 立ち絵の表示位置
        x = character_image.x
        y = character_image.y
        char_position = (x,y)
        char_clip = char_clip.set_start(current_duration).set_position(char_position)

        return char_clip


    @classmethod
    def set_voice(cls, characterName :str, characterOptions: CharacterVoice):
        Clip.characters[characterName] = characterOptions

    @classmethod
    def add_character(cls, name:str="デフォルト", characterImage: CharacterImageSettings = CharacterImageSettings()):
        if name not in Clip.character_images:
            Clip.character_images[name] = {
                "image_settings": characterImage,
                "style": {
                    "デフォルト": CharacterImageStyle()
                }
            }

    @classmethod
    def add_character_style(cls,name :str="デフォルト", characterOptions: CharacterImageStyle = CharacterImageStyle()):
        if name not in Clip.character_images:
            Clip.add_character(name, CharacterImageSettings())

        Clip.character_images[name]["style"][characterOptions.name] = characterOptions

    @classmethod
    def ch_voice(cls, characterName :str):
        if characterName not in Clip.characters:
            Clip.characters[characterName] = CharacterVoice()
        Clip.current_character = Clip.characters[characterName]

    @classmethod
    def voice(cls, telop :str,say :str = None,is_same_timing=False) -> None:
        if say is None:
            say = telop


        Clip.scripts.append({
            "command": "voice",
            "telop": telop,
            "say": say,
            "voice_engine": "voicevox",
            "telop_options": Clip.current_character.telopOptions,
            "voice_option": {
                "pitch": Clip.current_character.voicevoxOptions.pitch,
                "speed": Clip.current_character.voicevoxOptions.speed,
                "intonation": Clip.current_character.voicevoxOptions.intonation,
                "speaker_id": Clip.current_character.voicevoxOptions.speaker_id,
                "is_same_timing": is_same_timing
            }
        })
        print(Clip.scripts[-1])

    @classmethod
    def text(cls, telop :str,say :str = None,is_same_timing=False) -> None:
        if say is None:
            say = telop


        Clip.scripts.append({
            "command": "text",
            "telop": telop,
            "say": say,
            "voice_engine": "voicevox",
            "telop_options": Clip.current_character.telopOptions,
            "voice_option": {
                "pitch": Clip.current_character.voicevoxOptions.pitch,
                "speed": Clip.current_character.voicevoxOptions.speed,
                "intonation": Clip.current_character.voicevoxOptions.intonation,
                "speaker_id": Clip.current_character.voicevoxOptions.speaker_id,
                "is_same_timing": is_same_timing
            }
        })
        print(Clip.scripts[-1])

    @classmethod
    def main_visual(cls, path, from_sec=0,to_sec=-1, is_fullscreen=False,is_mute=False):
        command = "main_visual"
        if is_fullscreen:
            command = "full_screen_visual"
        Clip.scripts.append({
            "command": command,
            "filepath": path,
            "options": {
                "from": from_sec,
                "to": to_sec,
                "is_fullscreen": is_fullscreen,
                "is_mute": is_mute
            }
        })

    @classmethod
    def char(cls, name :str="デフォルト", style: str="ノーマル"):
        Clip.scripts.append({
            "command": "char",
            "options": {
                "name": name,
                "style": Clip.character_images[name]["style"][style],
                "image_settings": Clip.character_images[name]["image_settings"]
            }
        })
        pass

    @classmethod
    def bgm(cls, file_path):
        Clip.scripts.append({
            "command": "bgm",
            "file_path": file_path
        })
        pass

    @classmethod
    def se(cls, file_path):
        Clip.scripts.append({
            "command": "se",
            "file_path": file_path
        })
        pass


    @classmethod
    def wait(cls, duration):
        Clip.scripts.append({
            "command": "wait",
            "duration": duration
        })
        pass

    @classmethod
    def create_movie(cls):
        if not os.path.exists(get_path(f"./config.yml")):
            print("プロジェクト設定(config.yml)が存在しません。config.ymlを作成してください")
            print("プロジェクト設定(config.yml)の作成方法はREADME.mdを確認してください。")
            exit(1)

        if not os.path.exists(get_path(f"./script.csv")):
            print("シナリオファイル(script.csv)が存在しません。config.ymlを作成してください")
            print("シナリオファイル(script.csv)の作成方法はREADME.mdを確認してください。")
            exit(1)

        Clip.config = load_conf(get_path(f"./config.yml"))
        print(Clip.config)
        # 動画の長さや、各種クリップ

        # スクリプトごとに編集処理を順次実行していく
        for script in Clip.scripts:
            command = script["command"]
            print("command:", command)
            if command == "full_screen_visual":
                fullscreen_visual_clip = Clip.create_main_visual_clip(Clip.movie["fullscreen_visual_clips"], Clip.movie["current_duration"], script["filepath"], script["options"])
                Clip.movie["fullscreen_visual_clips"].append(fullscreen_visual_clip)
                pass
            if command == "main_visual":
                main_visual_clip = Clip.create_main_visual_clip(Clip.movie["main_visual_clips"], Clip.movie["current_duration"], script["filepath"], script["options"])
                Clip.movie["main_visual_clips"].append(main_visual_clip)
                pass
            if command == "char":
                # TODO: ここ修正
                character_clip = Clip.create_character_clip(Clip.movie["character_clips"], Clip.movie["current_duration"], script["options"])
                Clip.movie["character_clips"][script["options"]["name"]].append(character_clip)
                pass
            if command == "voice":
                txtclip = Clip.create_text_clip(Clip.movie["text_clips"], script, Clip.movie["current_duration"], True)
                Clip.movie["current_duration"] += txtclip.duration
                Clip.movie["text_clips"].append(txtclip)
                pass
            if command == "text":
                txtclip = Clip.create_text_clip(Clip.movie["text_clips"], script, Clip.movie["current_duration"], False)
                Clip.movie["current_duration"] += txtclip.duration
                Clip.movie["text_clips"].append(txtclip)
                pass
            if command == "bgm":
                bgmclip = Clip.create_audio_clip(script, Clip.movie["current_duration"], 0.1)
                Clip.movie["bgm_clips"].append(bgmclip)
                pass
            if command == "se":
                seclip = Clip.create_audio_clip(script, Clip.movie["current_duration"], 0.3)
                Clip.movie["se_clips"].append(seclip)
                pass
            if command == "wait":
                # wait_clip = Clip.create_wait(script, Clip.movie["current_duration"])
                Clip.movie["current_duration"] += float(script["duration"])
                # Clip.movie["wait_clips"].append(wait_clip)
                pass

        # 動画の総再生時間
        additional_time = Clip.config["movie"]["additional_time"]
        total_duration = float(Clip.movie["current_duration"]) + float(additional_time)
        print("総再生時間：", total_duration)

        # 動画の出力レイヤ
        output_layers = []

        # 最後の動画の再生時間を動画の最後までに設定する
        if len(Clip.movie["main_visual_clips"]) > 0:
            last_video_duration = total_duration - Clip.movie["main_visual_clips"][-1].start

            if last_video_duration > 0 and Clip.movie["main_visual_clips"][-1].duration != -1:
                Clip.movie["main_visual_clips"][-1] = Clip.movie["main_visual_clips"][-1].set_duration(last_video_duration)
            output_layers.extend(Clip.movie["main_visual_clips"])

        # 背景画像を出力レイヤに追加
        background_clip = (
            ImageClip(get_path(Clip.config["movie"]["background"]["image_path"]))
            .fx(vfx.mask_color, color=[0, 255, 0], thr=100, s=5)
            .set_duration(total_duration)
        )
        output_layers.append(background_clip)


        # テロップクリップがあれば出力レイヤに追加
        if len(Clip.movie["text_clips"]) > 0:
            output_layers.extend(Clip.movie["text_clips"])

        # 効果音クリップがあれば出力レイヤに追加
        if len(Clip.movie["se_clips"]) > 0:
            output_layers.extend(Clip.movie["se_clips"])

        # BGMクリップがあれば出力レイヤに追加
        if len(Clip.movie["bgm_clips"]) > 0:
            # BGMをリピートさせる
            Clip.movie["bgm_clips"] = set_bgm_repeat(Clip.movie["bgm_clips"], total_duration)
            output_layers.extend(Clip.movie["bgm_clips"])

        # 無音クリップがあれば出力レイヤに追加
        if len(Clip.movie["wait_clips"]) > 0:
            output_layers.extend(Clip.movie["wait_clips"])

        # 立ち絵クリップがあれば出力レイヤに追加
        for character_name in Clip.movie["character_clips"].keys():
            if len(Clip.movie["character_clips"][character_name]) > 0:
                # 最後キャラクタ表示時間を動画の最後までに設定する
                last_character_duration = total_duration - Clip.movie["character_clips"][character_name][-1].start
                if last_character_duration > 0 :
                    Clip.movie["character_clips"][character_name][-1] = Clip.movie["character_clips"][character_name][-1].set_duration(
                        last_character_duration
                    )
                output_layers.extend(Clip.movie["character_clips"][character_name])

        # 最後の動画の再生時間を動画の最後までに設定する
        if len(Clip.movie["fullscreen_visual_clips"]) > 0:
            last_video_duration = total_duration - Clip.movie["fullscreen_visual_clips"][-1].start

            if last_video_duration > 0 and Clip.movie["fullscreen_visual_clips"][-1].duration != -1:
                Clip.movie["fullscreen_visual_clips"][-1] = Clip.movie["fullscreen_visual_clips"][-1].set_duration(last_video_duration)
            output_layers.extend(Clip.movie["fullscreen_visual_clips"])


        # 動画出力を開始する時間
        output_start_time = 0

        # 動画出力を終了する時間
        output_end_time = float(total_duration)

        # プレビューしたい場合は設定値の指定した範囲だけを動画に書き出す
        if Clip.config["preview"]["enable"]:
            output_start_time = Clip.config["preview"]["start"]
            output_end_time = Clip.config["preview"]["end"]

        # 各種クリップを1つのクリップにまとめて
        # TODO: 動画のサイズを変更できるようにする
        final = CompositeVideoClip(output_layers, size=(1280, 720))

        # 指定した範囲の動画を書き出す
        final = final.subclip(output_start_time, output_end_time)

        # 動画を出力する
        final.write_videofile(
            get_path(f'./output/{Clip.config["movie"]["output_filename"]}.mp4'),
            # NVIDIAのGPUが使えたらその設定を使う
            codec="h264_nvenc" if Clip.config["hasNvidiaGpu"] else "libx264",
            preset= "fast" if Clip.config["hasNvidiaGpu"] else "ultrafast",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            fps=24,
            threads=Clip.config["numOfThread"],
            write_logfile=True,
        )
    

def get_slide_path(index):
    return get_path(f"./resource/slide_img/スライド{index}.PNG")

def conv_pptx_to_img(pptx_path):
    from_path = get_path(pptx_path)
    to_path = get_path("./resource/temp_slide/temp_slide.pptx")
    shutil.copyfile(from_path, to_path)
    application = win32com.client.DispatchEx("Powerpoint.Application")
    application.Visible = True
    pp = application.Presentations.open(to_path)
    pp.Export(get_path("./resource/slide_img/"), FilterName="png")
    pp.close()
    # application.quit()


def v(style="四国めたん",text="",say=None,is_same_timing=False):
    Clip.ch_voice(style)
    Clip.voice(text,say,is_same_timing)

def main():
    # めたんちゃんの設定
    vop = VoicevoxOptions(speakerName="四国めたん", speakerStyle="ノーマル",speed=1.0)
    top = TelopOptions(text_color="pink",text_size=25)
    四国めたん=CharacterVoice(vop,top)
    Clip.set_voice("四国めたん", 四国めたん)
    Clip.set_voice("四国めたん", 四国めたん)

    # ずんだもんの設定
    vop = VoicevoxOptions(speakerName="ずんだもん", speakerStyle="ノーマル",speed=1.2)
    top = TelopOptions(text_color="#33FF33")
    ずんだもん=CharacterVoice(vop,top)
    Clip.set_voice("ずんだもん", ずんだもん)

    # パワポを画像に変換
    conv_pptx_to_img("./resource/slide/vol1.pptx")

    # # BGMとメイン動画を設定
    Clip.se("./resource/se/イントロ.wav")    
    
    # パワポ1ページ目を表示
    Clip.main_visual(get_slide_path(1), is_fullscreen=True)
    Clip.wait(0.5)

    # パワポ2ページ目を表示
    Clip.main_visual(get_slide_path(2), is_fullscreen=True)
    Clip.se("./resource/se/pon.mp3")
    v("ずんだもん", "ずんだもんと")
    Clip.wait(0.5)

    # パワポ3ページ目を表示
    Clip.main_visual(get_slide_path(3), is_fullscreen=True)
    Clip.se("./resource/se/pon.mp3")
    v("四国めたん", "四国めたんの")
    Clip.wait(0.5)

    # パワポ4ページ目を表示
    Clip.main_visual(get_slide_path(4), is_fullscreen=True)
    Clip.se("./resource/se/kansei.mp3")
    v("ずんだもん", f"ずんだ競馬！")
    v("四国めたん", f"ずんだ競馬！!", is_same_timing=True)
    Clip.wait(1.5)

    # # 紫苑ステークスの動画の12秒から50秒目までを表示
    # Clip.main_visual("./resource/movie/nakayama11r.mov", 12, 50)
    # # めたんちゃん設定(興奮気味に少し早口)



    # # キャラクタの初期設定
    Clip.add_character("四国めたん", CharacterImageSettings(x=900,y=320,resize=0.3))
    Clip.add_character_style("四国めたん", CharacterImageStyle(name="ノーマル",image_path="./resource/character/四国めたん_ノーマル.png"))
    Clip.add_character_style("四国めたん", CharacterImageStyle(name="目そらし",image_path="./resource/character/四国めたん_目そらし.png"))

    Clip.add_character("ずんだもん", CharacterImageSettings(x=1000,y=320,resize=0.3))
    Clip.add_character_style("ずんだもん", CharacterImageStyle(name="ノーマル",image_path="./resource/character/ずんだもん_ノーマル.png"))
    Clip.add_character_style("ずんだもん", CharacterImageStyle(name="ビックリ",image_path="./resource/character/ずんだもん_ビックリ.png"))

    # # キャラクタを初期表示
    Clip.char("四国めたん", "ノーマル")
    Clip.char("ずんだもん", "ノーマル")
    
    # Clip.se("./resource/se/pon.mp3")
    # Clip.ch_voice("四国めたん")
    # Clip.voice(f"全画面表示をテストしてみます")
    # Clip.se("./resource/se/シーン切り替え1.mp3")
    # Clip.main_visual("./resource/screen/screen1.png",is_fullscreen=True)
    # Clip.wait(2)
    # Clip.ch_voice("ずんだもん")
    # Clip.voice(f"もちろん動画も表示できるのだ")
    # Clip.main_visual("./resource/movie/nakayama11r.mov", 12, 50,is_fullscreen=True)
    # Clip.wait(2)
    # Clip.voice(f"全画面表示おわり")
    # Clip.se("./resource/se/pon.mp3")
    # Clip.main_visual("", is_fullscreen=True,is_mute=True)
    # Clip.voice(f"シーン切り替えやタイトル表示にも使えそうだね")
    Clip.wait(1)
    Clip.main_visual("", is_fullscreen=True,is_mute=True)
    Clip.text(f"使用キャラクタ: VOICEVOX: ずんだもん/四国めたん")
    Clip.text(f"立ち絵素材: 坂本あひる様")
    Clip.create_movie()


if __name__ == "__main__":
    main()

