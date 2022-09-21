import moviepy
from moviepy.editor import *
import os
import hashlib
from .util import *
from .voicevox_requests import *
from .voiceroid2_requests import *
from .voicevox_options import *
from .voiceroid2_options import *
import moviepy.audio.fx.all as afx
import json

class TelopOptions:
    def __init__(self, text_color: str = "white", text_size: int = 25):
        self.text_color = text_color
        self.text_size = text_size

class CharacterVoice:
    def __init__(self, 
                softwareTalkOptions: VoicevoxOptions = VoicevoxOptions(), 
                telopOptions: TelopOptions = TelopOptions(),
        ):
        self.softwareTalkOptions = softwareTalkOptions
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
    def __init__(self):
        self.config = None
        self.characters = {"default": CharacterVoice()}
        self.character_images = {}
        self.current_character = self.characters["default"]
        self.scripts = []
        self.movie = {
            "current_duration": 0,
            "background_clips": [],
            "main_visual_clips": [],
            "fullscreen_visual_clips":[],
            "text_clips": [],
            "se_clips": [],
            "bgm_clips": [],
            "wait_clips": [],
            "bgm_clips": [],
            "character_clips": {},
        }
        self.mark = {}

    def is_imagefile(self, filetype):
        """
            簡易的に画像のファイルタイプを判定
        """
        return filetype == "png" or filetype == "jpg" or filetype == "jpeg" or filetype == "gif"

    def main_visual_resize_ratio(self, width, height):
        """
            メインビジュアルに表示する動画の拡大・縮小率を取得する
        """

        top_x = self.config["movie"]["background"]["main_vision_left_top_x"]
        top_y = self.config["movie"]["background"]["main_vision_left_top_y"]
        bottom_x = self.config["movie"]["background"]["main_vision_right_bottom_x"]
        bottom_y = self.config["movie"]["background"]["main_vision_right_bottom_y"]

        bg_width = bottom_x - top_x
        bg_height = bottom_y - top_y
        height_ratio = bg_height / height
        width_ratio = bg_width / width
        return width_ratio if width_ratio > height_ratio else height_ratio

    def main_visual_fullscreen_resize_ratio(self, width, height):
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


    def cut_func(self, from_sec, to_sec, max_duration):
        def cut(t):
            ret = t+from_sec
            if (to_sec) <= (ret):
                ret =  to_sec

            if max_duration <= ret:
                ret = max_duration - 0.1
            return ret
                
        return cut

    def create_main_visual_clip(self, clips, current_duration, movie_filepath, options):
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
        if (self.is_imagefile(filetype)):
            main_visual_clip = ImageClip(movie_filepath).set_start(current_duration).set_duration(1)
        else:
            movie_clip = VideoFileClip(movie_filepath)
            from_sec = options["from"]
            to_sec = options["to"]
            if options["stop"]:
                movie_clip = movie_clip.to_ImageClip(t=from_sec).set_duration(1)
            else:
                max_duration = movie_clip.duration
                movie_clip = movie_clip.fl_time(self.cut_func(from_sec, to_sec, max_duration)).set_duration(0)

            main_visual_clip = movie_clip.set_start(current_duration)

        # メインビジュアルの表示位置(左端)
        x = self.config["movie"]["background"]["main_vision_left_top_x"]
        y = self.config["movie"]["background"]["main_vision_left_top_y"]
        main_visual_potision = (x, y)
        # 動画サイズを自動調整する
        ratio = self.main_visual_resize_ratio(main_visual_clip.w, main_visual_clip.h)
        # フルスクリーン表示の場合
        if options["is_fullscreen"]:
            main_visual_potision = (0,0)
            ratio = self.main_visual_fullscreen_resize_ratio(main_visual_clip.w, main_visual_clip.h)
        
        main_visual_clip = main_visual_clip.set_position(main_visual_potision)
        main_visual_clip = moviepy.video.fx.resize.resize(main_visual_clip, ratio, ratio)
        main_visual_clip = main_visual_clip.fx(moviepy.audio.fx.all.volumex, float(options["volume"]))

        if options["is_background"]:
            main_visual_clip = main_visual_clip.fx(vfx.mask_color, color=[0, 255, 0], thr=100, s=5)

        return main_visual_clip

    def create_text_clip(self,clips, text_clip_options, current_duration, has_audio,skip_audio_render=False):
        """
        テロップを作成する
        """
        # ファイル名はハッシュで振っておいて簡易的にキャッシュできるようにする
        # TODO: このハッシュ生成処理が重いので修正する。
        # TODO: パラメータ変更の場合古い音声を使ってしまうので修正する。
        
        audioclip = None
        if text_clip_options["voice_option"]["audio_file_path"] is None:
            say = text_clip_options["voice_option"]["say"]
            # パラメータをベースにハッシュ値を生成。その値をファイル名にする
            print(vars(text_clip_options["voice_option"]))
            hash = hashlib.md5(json.dumps(vars(text_clip_options["voice_option"]))).hexdigest()
            if not skip_audio_render and text_clip_options["voice_engine"] == "voicevox":
                voice_vox_towav(say, f"{hash}.wav", text_clip_options["voice_option"])
            if text_clip_options["voice_engine"] == "voiceroid2":
                voiceroid2_towav(say, f"{hash}.wav", text_clip_options["voice_option"])
            audioclip = AudioFileClip(get_path(f"./voicevox_wav/{hash}.wav"))
        else:
            audioclip = AudioFileClip(get_path(text_clip_options["voice_option"]["audio_file_path"]))



        # Windowsの場合バックスラッシュでファイルパスが切られているとフォントを読み込めないので置換する
        font_path = get_path(self.config["movie"]["text"]["font_normal"]).replace("\\", "/")
        
        telop = text_clip_options["telop"]
        print("telop:",telop)
        txtclip = TextClip(
            f"{telop}",
            method="label",
            size=(2000, 30),
            align="West",
            fontsize=float(text_clip_options["telop_options"]["text_size"]),
            font=font_path,
            color=text_clip_options["telop_options"]["text_color"],
        )

        # テロップの表示位置
        
        x = self.config["movie"]["text"]["x"]
        y = self.config["movie"]["text"]["y"]
        if text_clip_options["voice_option"]["is_same_timing"] and len(clips) > 0:
            x += 10
            y += 10
        text_position = (x, y)

        txtclip = txtclip.set_duration(float(audioclip.duration)).set_position(text_position).fx(moviepy.audio.fx.all.volumex, float(text_clip_options["volume"]))

        # 読み上げる場合は音声を設定
        if has_audio:
            txtclip = txtclip.set_audio(audioclip)
        
        start_timing = current_duration
        if text_clip_options["voice_option"]["is_same_timing"] and len(clips) > 0:
            start_timing = clips[-1].start + 0.01

        # 発声タイミングを絶対時間で指定
        if text_clip_options["voice_option"]["absolute_time"] is not None:
            start_timing = text_clip_options["voice_option"]["absolute_time"]
        
        # 発声タイミングを遅らせる・食い気味
        if text_clip_options["voice_option"]["timing_offset"] is not None:
            start_timing = start_timing + text_clip_options["voice_option"]["timing_offset"]
        
        # 0より前なら0に寄せる
        # if (start_timing < 0):
        #     start_timing = 0

        return txtclip.set_start(t=start_timing, change_end=True)
    
    def create_audio_clip(self, audio_clip_options, current_duration, volume):
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
            font=get_path(self.config["movie"]["text"]["font_normal"]),
            color="white",
        )
        bgm = bgm.set_fps(44100)
        bgmclip = bgmclip.set_duration(float(bgm.duration))
        bgmclip = bgmclip.set_audio(bgm).set_start(t=current_duration, change_end=True)
        bgmclip = bgmclip.fx(moviepy.audio.fx.all.volumex, volume)
        return bgmclip


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


    def set_voice(self, characterName :str, characterOptions: CharacterVoice):
        self.characters[characterName] = characterOptions

    def add_character(self, name:str="デフォルト", characterImage: CharacterImageSettings = CharacterImageSettings()):
        if name not in self.character_images:
            self.character_images[name] = {
                "image_settings": characterImage,
                "style": {
                    "デフォルト": CharacterImageStyle()
                }
            }

    def add_character_style(self,name :str="デフォルト", characterOptions: CharacterImageStyle = CharacterImageStyle()):
        if name not in self.character_images:
            self.add_character(name, CharacterImageSettings())

        self.character_images[name]["style"][characterOptions.name] = characterOptions

    def ch_voice(self, characterName :str):
        if characterName not in self.characters:
            self.characters[characterName] = CharacterVoice()
        self.current_character = self.characters[characterName]


    def set_mark(self, name="default") -> None:
        self.scripts.append({
            "command": "mark",
            "name": name
        })
        print(self.scripts[-1])

    def voice(self, telop :str,say :str = None,is_same_timing=False,absolute_time=None,timing_offset=None,audio_file_path=None,volume=1.2) -> None:
        if say is None:
            say = telop

        self.scripts.append({
            "command": "voice",
            "telop": telop,
            "voice_engine": self.current_character.softwareTalkOptions.engine,
            "telop_options": {
                "text_color":  self.current_character.telopOptions.text_color,
                "text_size":  self.current_character.telopOptions.text_size,
            },
            "volume": volume,
            "voice_option": {
                "say": say,
                "audio_file_path": audio_file_path,
                "pitch": self.current_character.softwareTalkOptions.pitch,
                "speed": self.current_character.softwareTalkOptions.speed,
                "intonation": self.current_character.softwareTalkOptions.intonation,
                "speaker_id": self.current_character.softwareTalkOptions.speaker_id,
                "is_same_timing": is_same_timing,
                "absolute_time":absolute_time,
                "timing_offset": timing_offset
            }
        })
        print(self.scripts[-1])

    def text(self, telop :str,say :str = None,is_same_timing=False,absolute_time=None,timing_offset=None,audio_file_path=None) -> None:
        if say is None:
            say = telop

        self.scripts.append({
            "command": "text",
            "telop": telop,
            "voice_engine": self.current_character.softwareTalkOptions.engine,
            "telop_options": {
                "text_color":  self.current_character.telopOptions.text_color,
                "text_size":  self.current_character.telopOptions.text_size,
            },
            "volume": 0,
            "voice_option": {
                "say": say,
                "audio_file_path": audio_file_path,
                "pitch": self.current_character.softwareTalkOptions.pitch,
                "speed": self.current_character.softwareTalkOptions.speed,
                "intonation": self.current_character.softwareTalkOptions.intonation,
                "speaker_id": self.current_character.softwareTalkOptions.speaker_id,
                "is_same_timing": is_same_timing,
                "absolute_time":absolute_time,
                "timing_offset": timing_offset
            }
        })
        print(self.scripts[-1])

    def main_visual(self, path, from_sec=0,to_sec=-1, is_fullscreen=False,is_mute=False, stop=False,volume=0.5):
        command = "main_visual"
        if is_fullscreen:
            command = "full_screen_visual"
        self.scripts.append({
            "command": command,
            "filepath": path,
            "options": {
                "from": from_sec,
                "to": to_sec,
                "is_background": False,
                "is_fullscreen": is_fullscreen,
                "is_mute": is_mute,
                "stop": stop,
                "resize_base": "height",
                "volume": volume,
            }
        })


    def back_ground(self, path, from_sec=0,to_sec=-1,is_mute=False, stop=False):
        command = "back_ground"
        self.scripts.append({
            "command": command,
            "filepath": path,
            "options": {
                "from": from_sec,
                "to": to_sec,
                "is_background": True,
                "is_fullscreen": True,
                "is_mute": is_mute,
                "stop": stop,
                "resize_base": "height",
                "volume": 0,
            }
        })

    def char(self, name :str="デフォルト", style: str="ノーマル"):
        self.scripts.append({
            "command": "char",
            "options": {
                "name": name,
                "style": self.character_images[name]["style"][style],
                "image_settings": self.character_images[name]["image_settings"]
            }
        })
        pass

    def bgm(self, file_path,volume=0.1):
        self.scripts.append({
            "command": "bgm",
            "file_path": file_path,
            "volume":volume,
        })
        pass

    def se(self, file_path,volume=0.3):
        self.scripts.append({
            "command": "se",
            "file_path": file_path,
            "volume": volume
        })
        pass


    def wait(self, duration):
        self.scripts.append({
            "command": "wait",
            "duration": duration
        })
        pass

    def composit_movie(self,skip_audio_render=False):
        if not os.path.exists(get_path(f"./config.yml")):
            print("プロジェクト設定(config.yml)が存在しません。config.ymlを作成してください")
            print("プロジェクト設定(config.yml)の作成方法はREADME.mdを確認してください。")
            exit(1)

        self.config = load_conf(get_path(f"./config.yml"))
        print(self.config)
        # 動画の長さや、各種クリップ

        # スクリプトごとに編集処理を順次実行していく
        for script in self.scripts:
            command = script["command"]
            print("command:", command)
            if command == "back_ground":
                background_clips = self.create_main_visual_clip(self.movie["background_clips"], self.movie["current_duration"], script["filepath"], script["options"])
                self.movie["background_clips"].append(background_clips)
                pass                
            if command == "full_screen_visual":
                fullscreen_visual_clip = self.create_main_visual_clip(self.movie["fullscreen_visual_clips"], self.movie["current_duration"], script["filepath"], script["options"])
                self.movie["fullscreen_visual_clips"].append(fullscreen_visual_clip)
                pass
            if command == "main_visual":
                main_visual_clip = self.create_main_visual_clip(self.movie["main_visual_clips"], self.movie["current_duration"], script["filepath"], script["options"])
                self.movie["main_visual_clips"].append(main_visual_clip)
                pass
            if command == "char":
                # TODO: ここ修正
                character_clip = self.create_character_clip(self.movie["character_clips"], self.movie["current_duration"], script["options"])
                self.movie["character_clips"][script["options"]["name"]].append(character_clip)
                pass
            if command == "voice":
                txtclip = self.create_text_clip(self.movie["text_clips"], script, self.movie["current_duration"], True,skip_audio_render=skip_audio_render)
                self.movie["current_duration"] += txtclip.duration
                self.movie["text_clips"].append(txtclip)
                pass
            if command == "text":
                txtclip = self.create_text_clip(self.movie["text_clips"], script, self.movie["current_duration"], False,skip_audio_render=skip_audio_render)
                self.movie["current_duration"] += txtclip.duration
                self.movie["text_clips"].append(txtclip)
                pass
            if command == "bgm":
                bgmclip = self.create_audio_clip(script, self.movie["current_duration"], script["volume"])
                self.movie["bgm_clips"].append(bgmclip)
                pass
            if command == "se":
                seclip = self.create_audio_clip(script, self.movie["current_duration"], script["volume"])
                self.movie["se_clips"].append(seclip)
                pass
            if command == "wait":
                self.movie["current_duration"] += float(script["duration"])
                pass
            if command == "mark":
                self.mark[script["name"]] = self.movie["current_duration"]
                print("mark",self.mark)
                pass

        # 動画の総再生時間
        additional_time = self.config["movie"]["additional_time"]
        total_duration = float(self.movie["current_duration"]) + float(additional_time)
        print("総再生時間：", total_duration)

        # 動画の出力レイヤ
        output_layers = []

        # 最後の動画の再生時間を動画の最後までに設定する
        if len(self.movie["main_visual_clips"]) > 0:
            last_video_duration = total_duration - self.movie["main_visual_clips"][-1].start

            if last_video_duration > 0 and self.movie["main_visual_clips"][-1].duration != -1:
                self.movie["main_visual_clips"][-1] = self.movie["main_visual_clips"][-1].set_duration(last_video_duration)
            output_layers.extend(self.movie["main_visual_clips"])

        # 最後の動画の再生時間を動画の最後までに設定する
        if len(self.movie["background_clips"]) > 0:
            last_video_duration = total_duration - self.movie["background_clips"][-1].start

            if last_video_duration > 0 and self.movie["background_clips"][-1].duration != -1:
                self.movie["background_clips"][-1] = self.movie["background_clips"][-1].set_duration(last_video_duration)
            output_layers.extend(self.movie["background_clips"])

        # テロップクリップがあれば出力レイヤに追加
        if len(self.movie["text_clips"]) > 0:
            output_layers.extend(self.movie["text_clips"])

        # 効果音クリップがあれば出力レイヤに追加
        if len(self.movie["se_clips"]) > 0:
            output_layers.extend(self.movie["se_clips"])

        # BGMクリップがあれば出力レイヤに追加
        if len(self.movie["bgm_clips"]) > 0:
            # BGMをリピートさせる
            self.movie["bgm_clips"] = self.set_bgm_repeat(self.movie["bgm_clips"], total_duration)
            output_layers.extend(self.movie["bgm_clips"])

        # 無音クリップがあれば出力レイヤに追加
        if len(self.movie["wait_clips"]) > 0:
            output_layers.extend(self.movie["wait_clips"])

        # 立ち絵クリップがあれば出力レイヤに追加
        for character_name in self.movie["character_clips"].keys():
            if len(self.movie["character_clips"][character_name]) > 0:
                # 最後キャラクタ表示時間を動画の最後までに設定する
                last_character_duration = total_duration - self.movie["character_clips"][character_name][-1].start
                if last_character_duration > 0 :
                    self.movie["character_clips"][character_name][-1] = self.movie["character_clips"][character_name][-1].set_duration(
                        last_character_duration
                    )
                output_layers.extend(self.movie["character_clips"][character_name])

        # 最後の動画の再生時間を動画の最後までに設定する
        if len(self.movie["fullscreen_visual_clips"]) > 0:
            last_video_duration = total_duration - self.movie["fullscreen_visual_clips"][-1].start

            if last_video_duration > 0 and self.movie["fullscreen_visual_clips"][-1].duration != -1:
                self.movie["fullscreen_visual_clips"][-1] = self.movie["fullscreen_visual_clips"][-1].set_duration(last_video_duration)
            output_layers.extend(self.movie["fullscreen_visual_clips"])


        # 動画出力を開始する時間
        output_start_time = 0

        # 動画出力を終了する時間
        output_end_time = float(total_duration)

        # プレビューしたい場合は設定値の指定した範囲だけを動画に書き出す
        # 各種クリップを1つのクリップにまとめて
        # TODO: 動画のサイズを変更できるようにする
        composit = CompositeVideoClip(output_layers, size=(1280, 720))

        # 指定した範囲の動画を書き出す
        composit = composit.subclip(output_start_time, output_end_time)
        return composit
    
    def set_bgm_repeat(self, bgm_clips, total_duration):
        bgm_clips
        new_bgm_clips = []
        # 開始順にクリップをソート
        bgm_clips = sorted(bgm_clips, key=lambda bgm:bgm.start)
        while True:
            # BGMが無ければ終了
            if len(bgm_clips) == 0:
                break
            # 次に再生するBGM
            next_bgm = bgm_clips.pop(0)
            
            # このBGMを再生終了するべきタイミング。初期状態ではBGMを流し終えるまで
            play_end_time = (next_bgm.start + next_bgm.duration) 

            # 次のBGMが無ければ動画の最後まで
            if len(bgm_clips) == 0:
                play_end_time = total_duration
            # 次のBGMがあれば次のBGMの開始位置までになる
            else:
                play_end_time = bgm_clips[0].start
            
            # 今流しているBGMの再生終了タイミング
            current_bgm_end_time = (next_bgm.start + next_bgm.duration) 

            # いま流しているBGMが次のBGMを流し始めるタイミングでも終わらない場合
            if play_end_time <= current_bgm_end_time:
                offset = (current_bgm_end_time - play_end_time)
                # 超えた分、再生時間を短くして、再生リストに追加。次のBGMの設定へ
                next_bgm = next_bgm.set_duration(next_bgm.duration - offset)
                new_bgm_clips.append(next_bgm.set_audio(next_bgm.audio.fx(afx.audio_fadeout, 1)))
                continue

            # # いま流しているBGMが次のBGMより先に終わる場合
            # TODO: ループエフェクトがあるらしいのでそれを使う (https://zulko.github.io/moviepy/ref/audiofx.html)
            if play_end_time > current_bgm_end_time:
                while True:
                    # とりあえず今鳴らしている分を再生リストに追加。
                    new_bgm_clips.append(next_bgm)
                    
                    # 今鳴らしているBGMの終了位置がループ開始のタイミング
                    loop_start = (next_bgm.start + next_bgm.duration)
                    next_bgm = next_bgm.set_start(loop_start)

                    # 今流しているBGMの再生終了タイミングの更新
                    current_bgm_end_time = (next_bgm.start + next_bgm.duration) 

                    # ループさせるBGMが、終了するべき時間を超えていれば
                    if play_end_time <= current_bgm_end_time:
                        offset = (current_bgm_end_time - play_end_time)
                        # 超えた分、再生時間を短くして、再生リストに追加。次のBGMの設定へ
                        next_bgm = next_bgm.set_duration(next_bgm.duration - offset)
                        new_bgm_clips.append(next_bgm.set_audio(next_bgm.audio.fx(afx.audio_fadeout, 1)))
                        break
                    # ループさせるBGMが、終了するべき時間を超えてなければもう一度同じBGMを鳴らす

        return new_bgm_clips

    def create_movie(self,output_filename="movie.mp4",fps=24,range=None, range_by_mark=None):
        composit = self.composit_movie()
        if range is not None:
            composit = composit.subclip(range[0], range[1])
        if range_by_mark is not None:
            start = self.mark[range_by_mark[0]]
            end = self.mark[range_by_mark[1]]
            composit = composit.subclip(start, end)
        
        # 動画を出力する
        composit.write_videofile(
            get_path(f"./output/{output_filename}"),
            # NVIDIAのGPUが使えたらその設定を使う
            codec="h264_nvenc" if self.config["hasNvidiaGpu"] else "libx264",
            preset= "fast" if self.config["hasNvidiaGpu"] else "ultrafast",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            fps=fps,
            threads=self.config["numOfThread"],
            write_logfile=True,
        )
        exit(0)

    def preview(self,audio_samp_rate=11000,preview_fps=2,preview_resize=1,range=None, range_by_mark=None,skip_audio_render=False):
        composit = self.composit_movie(skip_audio_render=skip_audio_render)
        if range is not None:
            composit = composit.subclip(range[0], range[1])
        if range_by_mark is not None:
            start = self.mark[range_by_mark[0]]
            end = self.mark[range_by_mark[1]]
            composit = composit.subclip(start, end)

        aud = composit.audio.set_fps(audio_samp_rate)
        composit = composit.without_audio().set_audio(aud)
        composit.resize(width=720*preview_resize).preview(fps=preview_fps)
        exit(0)
    
    def show(self,timing=0):
        composit = self.composit_movie(skip_audio_render=True)
        composit.show(timing, interactive = True) 

    def v(self,style="四国めたん",text="",say=None,is_same_timing=False,absolute_time=None,timing_offset=None):
        self.ch_voice(style)
        self.voice(text,say,is_same_timing,absolute_time,timing_offset)
