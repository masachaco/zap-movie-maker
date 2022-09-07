from moviepy.editor import *
import os
import moviepy
from webbrowser import get
import requests
import json
import time
import hashlib
import csv
import yaml

BASE_PATH = None
CONFIG = None

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


def get_voicevox_audio_query(text, speaker):
    """
    VOICEVOXから合成音声用のクエリを発行する
    http://localhost:50021/docs#/%E3%82%AF%E3%82%A8%E3%83%AA%E4%BD%9C%E6%88%90/audio_query_audio_query_post
    """
    for i in range(3):
        url = f"http://localhost:50021/audio_query"
        r = requests.post(url, params={"text": text, "speaker": speaker}, timeout=(10.0, 300.0))
        if r.status_code == 200:
            return r.json()
        time.sleep(1)


def get_voicevox_synthesis(speaker, query):
    """
    VOICEVOXと合成音声用のクエリを使用して、音声合成を行う
    http://localhost:50021/docs#/%E9%9F%B3%E5%A3%B0%E5%90%88%E6%88%90/synthesis_synthesis_post
    """
    for i in range(3):
        url = f"http://localhost:50021/synthesis"
        r = requests.post(
            url,
            params={"speaker": speaker},
            data=json.dumps(query),
            timeout=(10.0, 300.0),
        )
        if r.status_code == 200:
            return r.content
        time.sleep(1)


def get_voicevox_audio(text, speaker=2):
    """
    VOICEVOXから音声を生成
    """
    audio_query = get_voicevox_audio_query(text, speaker)
    return get_voicevox_synthesis(speaker, audio_query)


def voice_vox_towav(text, audio_filename):
    """
    VOICEVOXから音声を生成してファイルに保存
    """

    audio_filepath = get_path(f"./voicevox_wav/{audio_filename}")
    # キャッシュが存在する場合はそれを使う
    if os.path.exists(audio_filepath):
        return

    voicevoix_audio = get_voicevox_audio(text)
    with open(audio_filepath, "wb") as fp:
        fp.write(voicevoix_audio)

def is_imagefile(filetype):
    """
        簡易的に画像のファイルタイプを判定
    """
    return filetype == "png" or filetype == "jpg" or filetype == "jpeg" or filetype == "gif"

def main_visual_resize_ratio(width, height):
    """
        メインビジュアルに表示する動画の拡大・縮小率を取得する
    """

    top_x = CONFIG["movie"]["background"]["main_vision_left_top_x"]
    top_y = CONFIG["movie"]["background"]["main_vision_left_top_y"]
    bottom_x = CONFIG["movie"]["background"]["main_vision_right_bottom_x"]
    bottom_y = CONFIG["movie"]["background"]["main_vision_right_bottom_y"]

    bg_width = bottom_x - top_x
    bg_height = bottom_y - top_y
    height_ratio = bg_height / height
    width_ratio = bg_width / width
    return width_ratio if width_ratio > height_ratio else height_ratio

def create_main_visual_clip(clips, current_duration, movie_filepath):
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
    if (is_imagefile(filetype)):
        main_visual_clip = ImageClip(movie_filepath).set_start(current_duration).set_duration(1)
    else:
        main_visual_clip = VideoFileClip(movie_filepath).set_start(current_duration).set_duration(1)
    
    # メインビジュアルの表示位置(左端)
    x = CONFIG["movie"]["background"]["main_vision_left_top_x"]
    y = CONFIG["movie"]["background"]["main_vision_left_top_y"]
    main_visual_potision = (x, y)
    main_visual_clip = main_visual_clip.set_position(main_visual_potision)

    # 動画サイズを自動調整する
    ratio = main_visual_resize_ratio(main_visual_clip.w, main_visual_clip.h)
    main_visual_clip = moviepy.video.fx.resize.resize(main_visual_clip, ratio, ratio)
    main_visual_clip = main_visual_clip.fx(moviepy.audio.fx.all.volumex, 0)
    return main_visual_clip


def create_character_clip(clips, current_duration, movie_filepath):
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
    ratio = CONFIG["movie"]["character"]["resize"]
    char_clip = moviepy.video.fx.resize.resize(char_clip, ratio, ratio)

    # 立ち絵の表示位置
    x = CONFIG["movie"]["character"]["x"]
    y = CONFIG["movie"]["character"]["y"]
    char_position = (x,y)
    char_clip = char_clip.set_start(current_duration).set_position(char_position)

    return char_clip


def create_text_clip(text, current_duration, has_audio, ruby):
    """
    テロップを作成する
    """

    # 読み方が指定されていなければ表示するテキストをVOICEVOXに読ませる
    if ruby is None or ruby.strip() == "":
        ruby = text

    # ファイル名はハッシュで振っておいて簡易的にキャッシュできるようにする
    # TODO: このハッシュ生成処理が重いので修正する。
    # TODO: パラメータ変更の場合古い音声を使ってしまうので修正する。
    hash = hashlib.md5(ruby.encode()).hexdigest()
    voice_vox_towav(ruby, f"{hash}.wav")


    audioclip = AudioFileClip(get_path(f"./voicevox_wav/{hash}.wav"))
    
    # Windowsの場合バックスラッシュでファイルパスが切られているとフォントを読み込めないので置換する
    font_path = get_path(CONFIG["movie"]["text"]["font_normal"]).replace("\\", "/")

    txtclip = TextClip(
        f"{text}",
        method="label",
        size=(2000, 30),
        align="West",
        fontsize=float(CONFIG["movie"]["text"]["font_size"]),
        font=font_path,
        color="white",
    )

    # テロップの表示位置
    x = CONFIG["movie"]["text"]["x"]
    y = CONFIG["movie"]["text"]["y"]
    text_position = (x, y)

    txtclip = txtclip.set_duration(float(audioclip.duration)).set_position(text_position)

    # 読み上げる場合は音声を設定
    if has_audio:
        txtclip = txtclip.set_audio(audioclip)

    return txtclip.set_start(t=current_duration, change_end=True)


def create_audio_clip(file_path, current_duration, volume):
    """
    オーディオクリップを作成する
    """
    bgm = AudioFileClip(file_path)

    # TODO: 一旦透明なテキストクリップを使ってしまったけど別途オーディオだけ再生することができるはず
    bgmclip = TextClip(
        " ",
        size=(1, 1),
        align="West",
        fontsize=30,
        font=get_path(CONFIG["movie"]["text"]["font_normal"]),
        color="white",
    )
    bgmclip = bgmclip.set_duration(float(bgm.duration))
    bgmclip = bgmclip.set_audio(bgm).set_start(t=current_duration, change_end=True)
    bgmclip = bgmclip.fx(moviepy.audio.fx.all.volumex, volume)
    return bgmclip


def create_wait(wait_time_sec, current_duration):
    """
    無音クリップを作成する
    """

    # TODO: 一旦透明なテキストクリップを使ってしまったけど別のいい方法があるはず
    waitclip = TextClip(
        " ",
        size=(1, 1),
        align="West",
        fontsize=30,
        font=get_path(CONFIG["movie"]["text"]["font_normal"]),
        color="white",
    )
    waitclip = waitclip.set_duration(float(wait_time_sec))
    waitclip = waitclip.set_start(t=current_duration, change_end=True)
    return waitclip


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

def gen_movie():
    if not os.path.exists(get_path(f"./config.yml")):
        print("プロジェクト設定(config.yml)が存在しません。config.ymlを作成してください")
        print("プロジェクト設定(config.yml)の作成方法はREADME.mdを確認してください。")
        exit(1)

    if not os.path.exists(get_path(f"./script.csv")):
        print("シナリオファイル(script.csv)が存在しません。config.ymlを作成してください")
        print("シナリオファイル(script.csv)の作成方法はREADME.mdを確認してください。")
        exit(1)

    global CONFIG
    CONFIG = load_conf(get_path(f"./config.yml"))

    scripts = load_script(get_path(f"./script.csv"))

    # 動画の長さや、各種クリップ
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

    # スクリプトごとに編集処理を順次実行していく
    for script in scripts:
        command = script[0].strip()
        value = script[1].strip()
        option = None
        if len(script) > 2:
            option = script[2]
        print(command, value)
        if command == "main_visual":
            main_visual_clip = create_main_visual_clip(movie["main_visual_clips"], movie["current_duration"], value)
            movie["main_visual_clips"].append(main_visual_clip)
        if command == "char":
            character_clip = create_character_clip(movie["character_clips"], movie["current_duration"], value)
            movie["character_clips"].append(character_clip)
        if command == "voice":
            txtclip = create_text_clip(value, movie["current_duration"], True, option)
            movie["current_duration"] += txtclip.duration
            movie["text_clips"].append(txtclip)
        if command == "text":
            txtclip = create_text_clip(value, movie["current_duration"], False, option)
            movie["current_duration"] += txtclip.duration
            movie["text_clips"].append(txtclip)
        if command == "bgm":
            bgmclip = create_audio_clip(value, movie["current_duration"], 0.1)
            movie["bgm_clips"].append(bgmclip)
        if command == "se":
            seclip = create_audio_clip(value, movie["current_duration"], 0.3)
            movie["se_clips"].append(seclip)
        if command == "wait":
            wait_clip = create_wait(value, movie["current_duration"])
            movie["current_duration"] += float(value)
            movie["wait_clips"].append(wait_clip)

    # 動画の総再生時間
    additional_time = CONFIG["movie"]["additional_time"]
    total_duration = float(movie["current_duration"]) + float(additional_time)
    print("総再生時間：", total_duration)

    # 動画の出力レイヤ
    output_layers = []

    # 最後の動画の再生時間を動画の最後までに設定する
    if len(movie["main_visual_clips"]) > 0:
        last_video_duration = total_duration - movie["main_visual_clips"][-1].start
        if last_video_duration > 0:
            movie["main_visual_clips"][-1] = movie["main_visual_clips"][-1].set_duration(last_video_duration)
        output_layers.extend(movie["main_visual_clips"])

    # 背景画像を出力レイヤに追加
    background_clip = (
        ImageClip(get_path(CONFIG["movie"]["background"]["image_path"]))
        .fx(vfx.mask_color, color=[0, 255, 0], thr=100, s=5)
        .set_duration(total_duration)
    )
    output_layers.append(background_clip)

    # テロップクリップがあれば出力レイヤに追加
    if len(movie["text_clips"]) > 0:
        output_layers.extend(movie["text_clips"])

    # 効果音クリップがあれば出力レイヤに追加
    if len(movie["se_clips"]) > 0:
        output_layers.extend(movie["se_clips"])

    # BGMクリップがあれば出力レイヤに追加
    if len(movie["bgm_clips"]) > 0:
        # BGMをリピートさせる
        movie["bgm_clips"] = set_bgm_repeat(movie["bgm_clips"], total_duration)
        output_layers.extend(movie["bgm_clips"])

    # 無音クリップがあれば出力レイヤに追加
    if len(movie["wait_clips"]) > 0:
        output_layers.extend(movie["wait_clips"])

    # 立ち絵クリップがあれば出力レイヤに追加
    if len(movie["character_clips"]) > 0:
        # 最後キャラクタ表示時間を動画の最後までに設定する
        last_character_duration = total_duration - movie["character_clips"][-1].start
        if last_character_duration > 0:
            movie["character_clips"][-1] = movie["character_clips"][-1].set_duration(
                last_character_duration
            )
        output_layers.extend(movie["character_clips"])
    
    # 動画出力を開始する時間
    output_start_time = 0

    # 動画出力を終了する時間
    output_end_time = float(total_duration)

    # プレビューしたい場合は設定値の指定した範囲だけを動画に書き出す
    if CONFIG["preview"]["enable"]:
        output_start_time = CONFIG["preview"]["start"]
        output_end_time = CONFIG["preview"]["end"]

    # 各種クリップを1つのクリップにまとめて
    # TODO: 動画のサイズを変更できるようにする
    final = CompositeVideoClip(output_layers, size=(1280, 720))

    # 指定した範囲の動画を書き出す
    final = final.subclip(output_start_time, output_end_time)

    # 動画を出力する
    final.write_videofile(
        get_path(f'./output/{CONFIG["movie"]["output_filename"]}'),
        # NVIDIAのGPUが使えたらその設定を使う
        codec="h264_nvenc" if CONFIG["hasNvidiaGpu"] else "libx264",
        preset= "fast" if CONFIG["hasNvidiaGpu"] else "ultrafast",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        fps=24,
        threads=CONFIG["numOfThread"],
        write_logfile=True,
    )

if __name__ == "__main__":
    gen_movie()
