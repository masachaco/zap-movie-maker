import moviepy
from moviepy.editor import *
import requests
import os
import yaml
import csv
import hashlib
import time
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
    def __init__(self, textColor: str = "", textSize: int = 0):
        self.textColor = textColor
        self.textSize = textSize

class Character:
    def __init__(self, 
                voicevoxOptions: VoicevoxOptions = VoicevoxOptions(), 
                telopOptions: TelopOptions = TelopOptions(), 
                image_path: str = "./resource/character/tachie-normal.png"
        ):
        self.voicevoxOptions = voicevoxOptions
        self.telopOptions = telopOptions
        self.image_path = image_path

class Clip:
    config = None
    characters = {"default": Character()}
    current_character = characters["default"]
    scripts = []
    movie = {
        "current_duration": 0,
        "main_visual_clips": [],
        "text_clips": [],
        "se_clips": [],
        "bgm_clips": [],
        "wait_clips": [],
        "bgm_clips": [],
        "character_clips": [],
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
    def create_main_visual_clip(cls, clips, current_duration, movie_filepath):
        """
            メインビジュアルにに使用するクリップを作成する
        """

        # この動画の前に再生している動画の再生時間を、この動画を再生するまでに伸ばす
        if len(clips) > 0:
            past_movie = clips[-1]
            past_movie_duration = current_duration - past_movie.start
            clips[-1] = past_movie.set_duration(past_movie_duration)

        filetype = movie_filepath.split(".")[-1].lower()

        main_visual_clip = None
        if (Clip.is_imagefile(filetype)):
            main_visual_clip = ImageClip(movie_filepath).set_start(current_duration).set_duration(1)
        else:
            main_visual_clip = VideoFileClip(movie_filepath).set_start(current_duration).set_duration(1)
        
        # メインビジュアルの表示位置(左端)
        x = Clip.config["movie"]["background"]["main_vision_left_top_x"]
        y = Clip.config["movie"]["background"]["main_vision_left_top_y"]
        main_visual_potision = (x, y)
        main_visual_clip = main_visual_clip.set_position(main_visual_potision)

        # 動画サイズを自動調整する
        ratio = Clip.main_visual_resize_ratio(main_visual_clip.w, main_visual_clip.h)
        main_visual_clip = moviepy.video.fx.resize.resize(main_visual_clip, ratio, ratio)
        main_visual_clip = main_visual_clip.fx(moviepy.audio.fx.all.volumex, 0)
        return main_visual_clip

    @classmethod
    def create_text_clip(cls, text_clip_options, current_duration, has_audio):
        """
        テロップを作成する
        """
        # ファイル名はハッシュで振っておいて簡易的にキャッシュできるようにする
        # TODO: このハッシュ生成処理が重いので修正する。
        # TODO: パラメータ変更の場合古い音声を使ってしまうので修正する。
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
            fontsize=float(Clip.config["movie"]["text"]["font_size"]),
            font=font_path,
            color="white",
        )

        # テロップの表示位置
        x = Clip.config["movie"]["text"]["x"]
        y = Clip.config["movie"]["text"]["y"]
        text_position = (x, y)

        txtclip = txtclip.set_duration(float(audioclip.duration)).set_position(text_position)

        # 読み上げる場合は音声を設定
        if has_audio:
            txtclip = txtclip.set_audio(audioclip)

        return txtclip.set_start(t=current_duration, change_end=True)
    
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
    def create_character_clip(slc, clips, current_duration, movie_filepath):
        """
        立ち絵クリップを作成する
        """

        # この立ち絵の前に再生している立ち絵の再生時間を、この立ち絵を再生するまでに伸ばす
        if len(clips) > 0:
            past_char = clips[-1]
            past_char_duration = current_duration - past_char.start
            clips[-1] = past_char.set_duration(past_char_duration)

        char_clip = ImageClip(movie_filepath).set_duration(1)

        # 立ち絵を拡大・縮小
        ratio = Clip.config["movie"]["character"]["resize"]
        char_clip = moviepy.video.fx.resize.resize(char_clip, ratio, ratio)

        # 立ち絵の表示位置
        x = Clip.config["movie"]["character"]["x"]
        y = Clip.config["movie"]["character"]["y"]
        char_position = (x,y)
        char_clip = char_clip.set_start(current_duration).set_position(char_position)

        return char_clip


    @classmethod
    def set_character(cls, characterName :str, characterOptions: Character):
        Clip.characters[characterName] = characterOptions

    @classmethod
    def chanege_character(cls, characterName :str):
        if characterName not in Clip.characters:
            Clip.characters[characterName] = Character()
        Clip.current_character = Clip.characters[characterName]

    @classmethod
    def voice(cls, telop :str,say :str = None) -> None:
        if say is None:
            say = telop


        Clip.scripts.append({
            "command": "voice",
            "telop": telop,
            "say": say,
            "voice_engine": "voicevox",
            "voice_option": {
                "pitch": Clip.current_character.voicevoxOptions.pitch,
                "speed": Clip.current_character.voicevoxOptions.speed,
                "intonation": Clip.current_character.voicevoxOptions.intonation,
                "speaker_id": Clip.current_character.voicevoxOptions.speaker_id,
            }
        })
        print(Clip.scripts[-1])

    @classmethod
    def text(cls, telop :str,say :str = None) -> None:
        if say is None:
            say = telop


        Clip.scripts.append({
            "command": "text",
            "telop": telop,
            "say": say,
            "voice_engine": "voicevox",
            "voice_option": {
                "pitch": Clip.current_character.voicevoxOptions.pitch,
                "speed": Clip.current_character.voicevoxOptions.speed,
                "intonation": Clip.current_character.voicevoxOptions.intonation,
                "speaker_id": Clip.current_character.voicevoxOptions.speaker_id,
            }
        })
        print(Clip.scripts[-1])

    @classmethod
    def main_visual(cls, path):
        Clip.scripts.append({
            "command": "main_visual",
            "filepath": path,
        })

    @classmethod
    def char(cls, character: Character = Character()):
        Clip.scripts.append({
            "command": "char",
            "image_path": character.image_path
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
            if command == "main_visual":
                main_visual_clip = Clip.create_main_visual_clip(Clip.movie["main_visual_clips"], Clip.movie["current_duration"], script["filepath"])
                Clip.movie["main_visual_clips"].append(main_visual_clip)
                pass
            if command == "char":
                # TODO: ここ修正
                character_clip = Clip.create_character_clip(Clip.movie["character_clips"], Clip.movie["current_duration"], script["image_path"])
                Clip.movie["character_clips"].append(character_clip)
                pass
            if command == "voice":
                txtclip = Clip.create_text_clip(script, Clip.movie["current_duration"], True)
                Clip.movie["current_duration"] += txtclip.duration
                Clip.movie["text_clips"].append(txtclip)
                pass
            if command == "text":
                txtclip = Clip.create_text_clip(script, Clip.movie["current_duration"], False)
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
            if last_video_duration > 0:
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
        if len(Clip.movie["character_clips"]) > 0:
            # 最後キャラクタ表示時間を動画の最後までに設定する
            last_character_duration = total_duration - Clip.movie["character_clips"][-1].start
            if last_character_duration > 0:
                Clip.movie["character_clips"][-1] = Clip.movie["character_clips"][-1].set_duration(
                    last_character_duration
                )
            output_layers.extend(Clip.movie["character_clips"])
        
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

def main():
    # BGMとメイン動画を設定
    Clip.bgm("./resource/bgm/bgm01.wav")
    Clip.main_visual("./resource/movie/sample_movie.mp4")

    # ずんだもん設定
    vop = VoicevoxOptions(speakerName="ずんだもん", speakerStyle="ノーマル")
    top = TelopOptions(textColor="green")
    Clip.set_character("ずんだもん", Character(vop,top))
    Clip.chanege_character("ずんだもん")

    for i in range(3):
        Clip.voice(f"{i}個めのセリフ")
        Clip.wait(0.5)
    
    Clip.voice("こんな感じでコードを組み込んで文章の生成もできるのだ")

    Clip.create_movie()


if __name__ == "__main__":
    main()
