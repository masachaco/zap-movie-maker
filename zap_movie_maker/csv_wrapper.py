from queue import Empty
from zap_movie_maker import *
from enum import Enum
from moviepy.config import change_settings
from default_voice_preset import * 

change_settings({"FFMPEG_BINARY":"C:\\ffmpeg\\bin\\ffmpeg.exe"})

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

def main():
    clip = Clip()
    # デフォルトのキャラクタ音声プリセットを生成
    setup_default_voice(clip)
    # キャラの立ち絵を生成
    clip.back_ground("./resource/bg/fullscreen.png")
    
    csv_file = load_script("./script.csv")
    # キャラクタ設定の読み込み
    scripts = []
    for line in csv_file:
        scripts.append(line)
    for script in scripts:
        command = script[0].strip()
        if command == "load_power_point":
            path = script[1].strip()
            conv_pptx_to_img(path)

    for script in scripts:
        command = script[0].strip()
        if command == "char_setting":
            selected_char = script[1].strip()
            x = script[2].strip()
            y = script[3].strip()
            ratio = script[4].strip()
            clip.add_character(selected_char, CharacterImageSettings(x=int(x),y=int(y),resize=float(ratio)))
        if command == "char":
            selected_char = script[1].strip()
            style = script[2].strip()
            clip.add_character_style(selected_char, style_name=style,image_path=style)

    for script in scripts:
        command = script[0].strip()
        if command == "main":
            path = script[1].strip()
            clip.main_visual(path)
        if command == "slide":
            slide_no = script[1].strip()
            clip.main_visual(get_slide_path(slide_no))
        if command == "char":
            selected_char = script[1].strip()
            style = script[2].strip()
            clip.char(selected_char,style)
        if command == "voice" or command == "douji_voice":
            selected_char = script[1].strip()
            text=script[2].strip()
            say=script[3].strip()
            if len(say) == 0:
                say = text
            clip.v(selected_char,text, say, is_same_timing=(command == "douji_voice"))
        if command == "text":
            selected_char = script[1].strip()
            say=script[2].strip()
            text=script[3].strip()
            clip.ch_voice(selected_char)
            clip.text(text, say)
        if command == "bgm":
            clip.bgm(script[1].strip())
        if command == "se":
            clip.se(script[1].strip())
        if command == "wait":
            clip.wait(script[1].strip())

    # 動画を生成する
    clip.create_movie()


if __name__ == "__main__":
    main()


