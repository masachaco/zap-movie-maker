from tkinter import font
import moviepy
from moviepy.editor import *
import os
import hashlib
from .util import *
from .telop import create_fuchidori_telop_image
from .voicevox_requests import *
from .voiceroid2_requests import *
from .voicevox_options import *
from .voiceroid2_options import *
import moviepy.audio.fx.all as afx
from .exo import *
from exolib import EXO

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
        y=0
        ):
        self.x = x
        self.y = y

class CharacterImageStyle:
    def __init__(self, 
                name="ノーマル",
                image_path="./resource/character/tachie-normal.png",
                resize=1
        ):
        self.image_path = image_path
        self.name = name
        self.resize = resize


class Clip:
    def __init__(self):
        self.current_telop_font = ""
        self.current_telop_position = ()
        self.current_main_visual_area = ()
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
            "absolute_text_clips": [],
            "se_clips": [],
            "bgm_clips": [],
            "wait_clips": [],
            "bgm_clips": [],
            "character_clips": {},
        }
        self.mark = {}
    
    def create_telop_image(self,text,font_path,font_size,fill_color="white",stroke_fill_color="black",background_color="white"):
        return create_fuchidori_telop_image(text,font_path,font_size,fill_color,stroke_fill_color,background_color)

    def is_imagefile(self, filetype):
        """
            簡易的に画像のファイルタイプを判定
        """
        return filetype == "png" or filetype == "jpg" or filetype == "jpeg" or filetype == "gif"

    def main_visual_resize_ratio(self, width, height,based_on=None,main_visual_area=None):
        """
            メインビジュアルに表示する動画の拡大・縮小率を取得する
        """

        top_x = main_visual_area[0]
        top_y = main_visual_area[1]
        bottom_x = main_visual_area[2]
        bottom_y = main_visual_area[3]

        bg_width = bottom_x - top_x
        bg_height = bottom_y - top_y
        height_ratio = bg_height / height
        width_ratio = bg_width / width
        if based_on == "height":
            return height_ratio
        if based_on == "width":
            return width_ratio
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
            last_video_duration = current_duration - past_movie.start

            if last_video_duration > 0 and past_movie.duration != -1:
                if past_movie.duration is None or past_movie.duration >= last_video_duration:
                    clips[-1] = past_movie.set_duration(last_video_duration)
                else:
                    stop_movie = past_movie.to_ImageClip(t=past_movie.duration-0.03)
                    stop_movie = stop_movie.set_start(past_movie.start + past_movie.duration)
                    stop_movie = stop_movie.set_duration(last_video_duration - past_movie.duration)
                    x = past_movie.pos(0)[0]
                    y = past_movie.pos(0)[1]
                    main_visual_potision = (x, y)
                    stop_movie = stop_movie.set_position(main_visual_potision)
                    clips.append(stop_movie)

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
            main_visual_clip = ImageClip(movie_filepath).set_start(current_duration)
            main_visual_clip.filename = movie_filepath
        else:
            movie_clip = VideoFileClip(movie_filepath)
            duration = movie_clip.duration
            from_sec = options["from"]
            to_sec = options["to"]
            if options["stop"]:
                movie_clip = movie_clip.to_ImageClip(t=from_sec)
            else:
                fr = 0 if from_sec < 0 else from_sec
                to = duration if to_sec < 0 or to_sec > duration else to_sec
                movie_clip = movie_clip.subclip(fr,to-0.01)
                movie_clip.fr =  fr
                movie_clip.to =  to


            main_visual_clip = movie_clip.set_start(current_duration)

        # メインビジュアルの表示位置(左端)
        x = options["main_visual_area"][0]
        y = options["main_visual_area"][1]
        main_visual_potision = (x, y)
        # 動画サイズを自動調整する
        ratio = self.main_visual_resize_ratio(main_visual_clip.w, main_visual_clip.h, options["resize_based_on"], options["main_visual_area"])
        # フルスクリーン表示の場合
        if options["is_fullscreen"]:
            main_visual_potision = (0,0)
            ratio = self.main_visual_fullscreen_resize_ratio(main_visual_clip.w, main_visual_clip.h)
        
        main_visual_clip = main_visual_clip.set_position(main_visual_potision)
        main_visual_clip = moviepy.video.fx.resize.resize(main_visual_clip, ratio, ratio)
        main_visual_clip.resize_ratio = ratio
        main_visual_clip = main_visual_clip.fx(moviepy.audio.fx.all.volumex, float(options["volume"]))
        main_visual_clip.volume = float(options["volume"])
        
        if options["is_background"] or options["is_green_back"]:
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
            print(str(text_clip_options["voice_option"]).encode('utf-8'))
            hash = hashlib.md5(str(text_clip_options["voice_option"]).encode('utf-8')).hexdigest()
            if not skip_audio_render and text_clip_options["voice_engine"] == "voicevox":
                voice_vox_towav(say, f"{hash}.wav", text_clip_options["voice_option"])
            if text_clip_options["voice_engine"] == "voiceroid2":
                voiceroid2_towav(say, f"{hash}.wav", text_clip_options["voice_option"])
            audioclip = AudioFileClip(get_path(f"./resource/generated_wav/{hash}.wav"))
        else:
            audioclip = AudioFileClip(get_path(text_clip_options["voice_option"]["audio_file_path"]))


        # Windowsの場合バックスラッシュでファイルパスが切られているとフォントを読み込めないので置換する

        font_path = get_path(text_clip_options["telop_options"]["font_path"]).replace("\\", "/")
        telop = text_clip_options["telop"]
        telop_image_path = self.create_telop_image(
            text=telop,
            font_path=font_path,
            font_size=float(text_clip_options["telop_options"]["text_size"]),
            stroke_fill_color=text_clip_options["telop_options"]["text_color"],
        )
        print("telop:", telop_image_path)
        txtclip = ImageClip(telop_image_path).set_start(current_duration).set_duration(1)
        txtclip.filename = telop_image_path

        # テロップの表示位置
        
        x = text_clip_options["telop_options"]["right_top_x"]
        y = text_clip_options["telop_options"]["right_top_y"]
        if text_clip_options["voice_option"]["is_same_timing"] and len(clips) > 0:
            x += 10
            y += 10
        text_position = (x, y)

        txtclip = txtclip.set_duration(float(audioclip.duration)).set_position(text_position)

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
        txtclip = txtclip.fx(afx.audio_normalize).fx(moviepy.audio.fx.all.volumex, float(text_clip_options["volume"]))
        txtclip.volume = float(text_clip_options["volume"])
        txtclip.speaker_id = text_clip_options["voice_option"]["speaker_id"]
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
            font=get_path(self.current_telop_font),
            color="white",
        )
        bgm = bgm.set_fps(44100)
        bgmclip = bgmclip.set_duration(float(bgm.duration))
        bgmclip = bgmclip.set_audio(bgm).set_start(t=current_duration, change_end=True)
        bgmclip = bgmclip.fx(afx.audio_normalize).fx(moviepy.audio.fx.all.volumex, volume)
        bgmclip.volume = volume
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

        # char_clips = clips[character_name]

        # この立ち絵の前に再生している立ち絵の再生時間を、この立ち絵を再生するまでに伸ばす
        # if len(char_clips) > 0:
        #     past_char = char_clips[-1]
        #     past_char_duration = current_duration - past_char.start
        #     char_clips[-1] = past_char.set_duration(past_char_duration)

        char_clip = ImageClip(character_style.image_path).set_duration(1)
        char_clip.filename = character_style.image_path

        # 立ち絵を拡大・縮小
        ratio = character_style.resize
        char_clip = moviepy.video.fx.resize.resize(char_clip, ratio, ratio)
        char_clip.resize_ratio = ratio

        # 立ち絵の表示位置
        x = character_image.x
        y = character_image.y
        char_position = (x,y)
        start_time = current_duration
        if options["absolute_time"] is not None:
            start_time = options["absolute_time"]

        char_clip = char_clip.set_start(start_time).set_position(char_position)

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

    def add_character_style(self,character_name :str="デフォルト", style_name :str="ノーマル", image_path:str="./resource/character/tachie-normal.png",resize=1.0):
        if character_name not in self.character_images:
            self.add_character(character_name, CharacterImageSettings())

        self.character_images[character_name]["style"][style_name] = CharacterImageStyle(image_path=image_path, name=style_name, resize=resize)


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

    def voice(self, telop :str,say :str = None,is_same_timing=False,absolute_time=None,timing_offset=None,audio_file_path=None,volume=None,telop_positon=None,font_path=None,font_size=None,font_color=None) -> None:
        if say is None:
            say = telop
        if volume is None:
            if audio_file_path is not None:
                volume = 1
            else:
                volume = self.current_character.softwareTalkOptions.masterVolume
        if telop_positon is None:
            telop_positon = (
                self.current_telop_position[0],
                self.current_telop_position[1],
            )

        if font_path is None:
            font_path = self.current_telop_font
        
        if font_size is None:
            font_size = self.current_character.telopOptions.text_size
        
        if font_color is None:
            font_color = self.current_character.telopOptions.text_color


        self.scripts.append({
            "command": "voice",
            "telop": telop,
            "voice_engine": self.current_character.softwareTalkOptions.engine,
            "telop_options": {
                "text_color":  font_color,
                "text_size":  font_size,
                "font_path": font_path,
                "right_top_x": telop_positon[0],
                "right_top_y": telop_positon[1],
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
                "timing_offset": timing_offset,
                "pauseMiddl": self.current_character.softwareTalkOptions.pauseMiddle,
                "pauseLong": self.current_character.softwareTalkOptions.pauseLong,
                "pauseSentence": self.current_character.softwareTalkOptions.pauseSentence,
                "masterVolume": 1,
                "volume": self.current_character.softwareTalkOptions.volume,
            }
        })
        print(self.scripts[-1])

    def text(self, telop :str,say :str = None,is_same_timing=False,absolute_time=None,timing_offset=None,audio_file_path=None,telop_positon=None,font_path=None,font_size=None,font_color=None) -> None:
        if say is None:
            say = telop

        if telop_positon is None:
            telop_positon = (
                self.current_telop_position[0],
                self.current_telop_position[1],
            )

        if font_path is None:
            font_path = self.current_telop_font
        
        if font_size is None:
            font_size = self.current_character.telopOptions.text_size
        
        if font_color is None:
            font_color = self.current_character.telopOptions.text_color

        self.scripts.append({
            "command": "text",
            "telop": telop,
            "voice_engine": self.current_character.softwareTalkOptions.engine,
            "telop_options": {
                "text_color":  font_color,
                "text_size":  font_size,
                "font_path": font_path,
                "right_top_x": telop_positon[0],
                "right_top_y": telop_positon[1],
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
                "timing_offset": timing_offset,
                "pauseMiddl": self.current_character.softwareTalkOptions.pauseMiddle,
                "pauseLong": self.current_character.softwareTalkOptions.pauseLong,
                "pauseSentence": self.current_character.softwareTalkOptions.pauseSentence,
                "masterVolume": 1,
                "volume": 1,
            }
        })
        print(self.scripts[-1])

    def main_visual(self, path, from_sec=0,to_sec=-1, is_fullscreen=False,is_mute=False, stop=False,volume=0.5,is_green_back=False,resize_based_on=None,main_visual_area=None):
        command = "main_visual"
        if is_fullscreen:
            command = "full_screen_visual"

        main_visual_area = self.current_main_visual_area
        if main_visual_area is not None:
            main_visual_area = (
                main_visual_area[0],
                main_visual_area[1],
                main_visual_area[2],
                main_visual_area[3],
            )

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
                "is_green_back":is_green_back,
                "resize_based_on": resize_based_on,
                "main_visual_area": main_visual_area
            }
        })


    def set_display_settings(self,
        background_path,
        main_visual_area,
        telop_position,
        telop_font):
        
        command = "display_settings"
        self.current_main_visual_area = (
            main_visual_area[0],
            main_visual_area[1],
            main_visual_area[2],
            main_visual_area[3],
        )
        self.current_telop_position = (
            telop_position[0],
            telop_position[1]
        )
        self.current_telop_font = telop_font
        self.scripts.append({
            "command": command,
            "filepath": background_path,
            "options": {
                "from": 0,
                "to": -1,
                "is_background": True,
                "is_fullscreen": True,
                "is_mute": False,
                "stop": False,
                "resize_base": "height",
                "volume": 0,
                "is_green_back":True,
                "resize_based_on": None,
                "main_visual_area": self.current_main_visual_area
            }
        })

    def char(self, name :str="デフォルト", style: str="ノーマル",absolute_time=None):
        self.scripts.append({
            "command": "char",
            "options": {
                "name": name,
                "style": self.character_images[name]["style"][style],
                "image_settings": self.character_images[name]["image_settings"],
                "absolute_time":absolute_time,
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
        # 動画の長さや、各種クリップ

        # スクリプトごとに編集処理を順次実行していく
        for script in self.scripts:
            command = script["command"]
            print("command:", command)
            if command == "display_settings":
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
                character_clip = self.create_character_clip(self.movie["character_clips"], self.movie["current_duration"], script["options"])
                self.movie["character_clips"][script["options"]["name"]].append(character_clip)
                pass
            if command == "voice":
                clips = self.movie["text_clips"]
                if script["voice_option"]["absolute_time"] is not None:
                    clips = self.movie["absolute_text_clips"]
                txtclip = self.create_text_clip(clips, script, self.movie["current_duration"], True,skip_audio_render=skip_audio_render)
                # TODO: abusolute_timeで指定した後にis_sametimeすると時間軸がバグるので別クリップに分けたい
                if script["voice_option"]["absolute_time"] is None:
                    self.movie["current_duration"] = txtclip.start + txtclip.duration
                clips.append(txtclip)
                pass
            if command == "text":
                clips = self.movie["text_clips"]
                if script["voice_option"]["absolute_time"] is not None:
                    clips = self.movie["absolute_text_clips"]
                txtclip = self.create_text_clip(clips, script, self.movie["current_duration"], False,skip_audio_render=skip_audio_render)
                # TODO: abusolute_timeで指定した後にis_sametimeすると時間軸がバグるので別クリップに分けたい
                if script["voice_option"]["absolute_time"] is None:
                    self.movie["current_duration"] = txtclip.start + txtclip.duration
                clips.append(txtclip)
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
        total_duration = float(self.movie["current_duration"])
        print("総再生時間：", total_duration)

        # 動画の出力レイヤ
        output_layers = []

        # 最後の動画の再生時間を動画の最後までに設定する
        if len(self.movie["main_visual_clips"]) > 0:
            past_movie = self.movie["main_visual_clips"][-1]
            last_video_duration = total_duration - past_movie.start

            if last_video_duration > 0 and past_movie.duration != -1:
                if past_movie.duration is None or past_movie.duration >= last_video_duration:
                    self.movie["main_visual_clips"][-1] = past_movie.set_duration(last_video_duration)
                else:
                    stop_movie = past_movie.to_ImageClip(t=past_movie.duration-0.03)
                    stop_movie = stop_movie.set_start(past_movie.start + past_movie.duration)
                    stop_movie = stop_movie.set_duration(last_video_duration - past_movie.duration)
                    x = past_movie.pos(0)[0]
                    y = past_movie.pos(0)[1]
                    main_visual_potision = (x, y)
                    stop_movie = stop_movie.set_position(main_visual_potision)
                    self.movie["main_visual_clips"].append(stop_movie)
                    
            output_layers.extend(self.movie["main_visual_clips"])

        # 最後の動画の再生時間を動画の最後までに設定する
        if len(self.movie["background_clips"]) > 0:
            last_video_duration = total_duration - self.movie["background_clips"][-1].start
            if last_video_duration > 0 and self.movie["background_clips"][-1].duration != -1:
                self.movie["background_clips"][-1] = self.movie["background_clips"][-1].set_duration(last_video_duration)
            output_layers.extend(self.movie["background_clips"])

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
                self.movie["character_clips"][character_name] = sorted(self.movie["character_clips"][character_name], key=lambda m: m.start)
                for i,current_movie in enumerate(self.movie["character_clips"][character_name]):
                    if i == len(self.movie["character_clips"][character_name])-1:
                        last_character_duration = total_duration - current_movie.start
                        if last_character_duration > 0 :
                            self.movie["character_clips"][character_name][i] = current_movie.set_duration(last_character_duration)
                    if i == 0:
                        continue
                    new_duration = current_movie.start - self.movie["character_clips"][character_name][i-1].start
                    self.movie["character_clips"][character_name][i-1] = self.movie["character_clips"][character_name][i-1].set_duration(new_duration)
                output_layers.extend(self.movie["character_clips"][character_name])

        # テロップクリップがあれば出力レイヤに追加
        if len(self.movie["text_clips"]) > 0:
            output_layers.extend(self.movie["text_clips"])

        if len(self.movie["absolute_text_clips"]) > 0:
            output_layers.extend(self.movie["absolute_text_clips"])

        # 最後の動画の再生時間を動画の最後までに設定する
        if len(self.movie["fullscreen_visual_clips"]) > 0:
            last_video_duration = total_duration - self.movie["fullscreen_visual_clips"][-1].start

            if last_video_duration > 0 and self.movie["fullscreen_visual_clips"][-1].duration != -1:
                self.movie["fullscreen_visual_clips"][-1] = self.movie["fullscreen_visual_clips"][-1].set_duration(last_video_duration)
            output_layers.extend(self.movie["fullscreen_visual_clips"])

        # TODO:　最終段階でテロップ位置の自動調整を入れたい

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

    def create_movie(self,output_filename="./output/movie.mp4",fps=24,range=None, range_by_mark=None, useNvidiaGpuRendering=False):
        composit = self.composit_movie()
        if range is not None:
            composit = composit.subclip(range[0], range[1])
        if range_by_mark is not None:
            start = self.mark[range_by_mark[0]]
            end = self.mark[range_by_mark[1]]
            composit = composit.subclip(start, end)
        # NVIDIAのGPUが使えたらその設定を使う
        codec = "h264_nvenc" if useNvidiaGpuRendering else "libx264"
        codec_preset = "fast" if useNvidiaGpuRendering else "ultrafast"
        print("codec:",codec,"preset:",codec_preset)
        # 動画を出力する
        audio = composit.audio.set_fps(48000)
        composit = composit.set_audio(audio)
        composit = composit.fx(afx.audio_normalize)
        composit.write_videofile(
            output_filename,
            codec=codec,
            preset= codec_preset,
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            fps=fps,
            write_logfile=False,
        )

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
    
    def show(self,timing=0):
        composit = self.composit_movie(skip_audio_render=True)
        composit.show(timing, interactive = True) 

    def v(self,style="四国めたん",text="",say=None,is_same_timing=False,absolute_time=None,timing_offset=None,audio_file_path=None):
        self.ch_voice(style)
        self.voice(text,say,is_same_timing,absolute_time,timing_offset,audio_file_path=audio_file_path)
    
    def set_preset_voice(self, preset_json):
        for preset in preset_json:
            vop = None
            if preset["engine"] == "voiceroid":
                vop = Voiceroid2Options(speakerName=preset["speaker_name"],speakerStyle=preset["speaker_style"],speed=preset["speed"],intonation=preset["intonation"],pitch=preset["pitch"])
            elif preset["engine"] == "voicevox":
                vop = VoicevoxOptions(speakerName=preset["speaker_name"],speakerStyle=preset["speaker_style"],speed=preset["speed"],intonation=preset["intonation"],pitch=preset["pitch"])
            top = TelopOptions(text_color=preset["color"],text_size=37)
            voiceConfig=CharacterVoice(vop,top)
            self.set_voice(preset["preset_name"], voiceConfig)

    def set_characters(self,preset_json):
        # # キャラクタの初期設定
        for preset in preset_json:
            character_name = preset["character_name"]
            position_x = preset["position_x"]
            position_y = preset["position_y"]
            self.add_character(character_name, CharacterImageSettings(x=int(position_x),y=int(position_y)))
            for style in preset["styles"]:
                self.add_character_style(character_name, style_name=style["style_name"],image_path=get_path(style["image_file_path"]),resize=0.3)

    def set_display_fullscreen_setting(self):
        self.set_display_settings(
            background_path=get_path("./resource/bg/fullscreen.png"),
            main_visual_area=(0,0,1280,720),
            telop_position=(22,618),
            telop_font=get_path("./resource/fonts/Noto_Sans_JP/NotoSansJP-Black.otf")
        )
    def set_display_signage_setting(self):
        self.set_display_settings(
            background_path=get_path("./resource/bg/keiba_bg.png"),
            main_visual_area=(37,20,934,544),
            telop_position=(22,618),
            telop_font=get_path("./resource/fonts/Noto_Sans_JP/NotoSansJP-Black.otf")
        )        

    def create_movie_from_csv(self, csv_str):
        # 背景を設定
        self.set_display_signage_setting()
        
        # CSVの読み込み
        splitted_csv = csv_str.split("\n")
        
        # 空行とコメント行はスキップ
        filtered_data = filter(lambda txt: (not txt.strip().startswith("#")) and (not txt.strip() == ""),splitted_csv)

        # CSVをパース
        csv_lines = csv.reader(list(filtered_data))
        scripts = []
        for line in csv_lines:
            scripts.append(line)

        # パワポを画像に変換
        for script in scripts:
            command = script[0].strip()
            if command == "load_power_point":
                path = script[1].strip()
                conv_pptx_to_img(path)

        # キャラクタ設定の読み込み
        for script in scripts:
            command = script[0].strip()
            if command == "char_setting":
                selected_char = script[1].strip()
                x = script[2].strip()
                y = script[3].strip()
                self.add_character(selected_char, CharacterImageSettings(x=int(x),y=int(y)))

            if command == "char" or command == "abs_char":
                selected_char = script[1].strip()
                style = script[2].strip()
                resize = float(script[3].strip())
                self.add_character_style(selected_char, style_name=get_path(style),image_path=get_path(style),resize=resize)

        # スクリプトに沿って動画を作成していく
        bf_time = 0
        for script in scripts:
            command = script[0].strip()
            if command == "main":
                path = script[1].strip()
                self.main_visual(get_path(path),volume=0.3)

            if command == "slide":
                slide_no = script[1].strip()
                self.main_visual(get_path(get_slide_path(slide_no)))

            if command == "char":
                selected_char = script[1].strip()
                style = script[2].strip()
                self.char(selected_char,get_path(style))

            if command == "abs_char":
                selected_char = script[1].strip()
                style = script[2].strip()
                resize = float(script[3].strip())
                time = script[4].strip()
                if str(time).strip() == "bf":
                    time = bf_time
                self.char(selected_char,get_path(style),absolute_time=time,)

            if command == "voice" or command == "douji_voice":
                selected_char = script[1].strip()
                text=script[2].strip()
                say=script[3].strip()
                if len(say) == 0:
                    say = text
                self.v(selected_char,text, say, is_same_timing=(command == "douji_voice"))

            if command == "abs_voice":
                selected_char = script[1].strip()
                text=script[2].strip()
                say=script[3].strip()
                time=script[4].strip()
                bf_time=time
                if len(say) == 0:
                    say = text
                print(selected_char,text,say,time)
                self.v(selected_char,text, say, is_same_timing=(command == "douji_voice"),absolute_time=float(time))

            if command == "text":
                selected_char = script[1].strip()
                say=script[2].strip()
                text=script[3].strip()
                self.ch_voice(selected_char)
                self.text(text, say)

            if command == "abs_text":
                selected_char = script[1].strip()
                text=script[2].strip()
                say=script[3].strip()
                time=script[4].strip()
                bf_time=time
                if len(say) == 0:
                    say = text
                self.ch_voice(selected_char)
                self.text(text, say,absolute_time=float(time))

            if command == "bgm":
                self.bgm(get_path(script[1].strip()))

            if command == "se":
                self.se(get_path(script[1].strip()))

            if command == "wait":
                self.wait(script[1].strip())

        #     if command == "show":
        #         print("\n\nプレビューを終了するには、この画面でCtrl + C を複数回押してください。")
        #         self.show()
        #         exit(0)

        #     if command == "preview":
        #         self.preview()
        #         exit(0)
        # # self.preview()
        # exit(0)
        # 動画を生成する
        # to_aviutil_exo(this)
        # self.create_movie()

    def to_aviutil_exo(self, outputfile_name):
        self.composit_movie()

        with open(outputfile_name, "w", encoding="cp932") as stream:
            exo = EXO(width=1280, height=720, rate=24)
            main_visual_clips(exo,self.movie["main_visual_clips"],1,2)

            background_clips(exo,self.movie["background_clips"],3)
            # 10まではメインレイヤー

            # 11～25はキャラクターレイヤー(15キャラクター分)
            layer=10
            for charName in self.movie["character_clips"].keys():
                layer+=1
                character_clips(exo,self.movie["character_clips"][charName],layer)
            
            #26～40はテロップのレイヤー(15キャラクター分)
            #41～55はキャラクターの音声レイヤー(15キャラクター分)
            layer=31
            VOICE_RAYER_MAP = {"max_9bef0e58_96ec_41c5_b091_acf4b7586e55":0,}
            text_clip_list = []
            text_clip_list.extend(self.movie["text_clips"])
            text_clip_list.extend(self.movie["absolute_text_clips"])
            text_clips(exo, text_clip_list,26, 41, VOICE_RAYER_MAP)

            # 56～75 はbgmレイヤー(20件)
            layer+=2
            BGM_RAYER_MAP = {"max_9bef0e58_96ec_41c5_b091_acf4b7586e55":0,}
            audio_clips(exo,self.movie["bgm_clips"], 56,BGM_RAYER_MAP)

            # 76～95 はseレイヤー(20件)
            layer+=1
            SE_RAYER_MAP = {"max_9bef0e58_96ec_41c5_b091_acf4b7586e55":0,}
            audio_clips(exo,self.movie["se_clips"], 76, SE_RAYER_MAP)
            
            # 96/97は全画面用レイヤー(1件)
            layer+=1
            main_visual_clips(exo,self.movie["fullscreen_visual_clips"],96, 97)
            exo.dump(stream)
