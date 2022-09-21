from inspect import isfunction
from operator import is_
from unicodedata import name
from moviepy.editor import *
from voicevox_options import *
from voiceroid2_options import *
from clip import *
import platform

def setup(clip:Clip):
    # めたんちゃんの設定
    vop = VoicevoxOptions(speakerName="四国めたん", speakerStyle="ノーマル",speed=1.1)
    top = TelopOptions(text_color="pink",text_size=25)
    四国めたん=CharacterVoice(vop,top)
    clip.set_voice("四国めたん", 四国めたん)
    clip.set_voice("四国めたん", 四国めたん)

    # ずんだもんの設定
    vop = VoicevoxOptions(speakerName="ずんだもん", speakerStyle="ノーマル",speed=1.2)
    top = TelopOptions(text_color="#33FF33")
    ずんだもん=CharacterVoice(vop,top)
    clip.set_voice("ずんだもん", ずんだもん)
    
    vop = Voiceroid2Options(speakerName="琴葉茜_v2",speakerStyle="関西弁",speed=1.5,intonation=2)
    top = TelopOptions(text_color="red")
    琴葉茜_関西弁=CharacterVoice(vop,top)
    clip.set_voice("琴葉茜", 琴葉茜_関西弁)

    vop = Voiceroid2Options(speakerName="琴葉葵_v2",speakerStyle="ノーマル",speed=1.5,intonation=1.2,pitch=1.1)
    top = TelopOptions(text_color="blue")
    琴葉葵=CharacterVoice(vop,top)
    clip.set_voice("琴葉葵", 琴葉葵)

    vop = Voiceroid2Options(speakerName="東北きりたん",speakerStyle="ノーマル",speed=1.2,intonation=1.2,pitch=1)
    top = TelopOptions(text_color="#734e30")
    東北きりたん=CharacterVoice(vop,top)
    clip.set_voice("東北きりたん", 東北きりたん)

    vop = Voiceroid2Options(speakerName="結月ゆかり",speakerStyle="ノーマル",speed=1.4,intonation=1.2,pitch=1.2)
    top = TelopOptions(text_color="#a260bf")
    結月ゆかり=CharacterVoice(vop,top)
    clip.set_voice("結月ゆかり", 結月ゆかり)

    vop = Voiceroid2Options(speakerName="紲星あかり_v2",speakerStyle="ノーマル",speed=1.4,intonation=1.2,pitch=1.2)
    top = TelopOptions(text_color="yellow")
    紲星あかり=CharacterVoice(vop,top)
    clip.set_voice("紲星あかり", 紲星あかり)

    vop = Voiceroid2Options(speakerName="東北イタコ_v2",speakerStyle="ノーマル",speed=1.2,intonation=1.2,pitch=1)
    top = TelopOptions(text_color="white")
    東北イタコ=CharacterVoice(vop,top)
    clip.set_voice("東北イタコ", 東北イタコ)

    vop = Voiceroid2Options(speakerName="京町セイカ",speakerStyle="ノーマル",speed=1,intonation=1.2,pitch=1)
    top = TelopOptions(text_color="green")
    京町セイカ=CharacterVoice(vop,top)
    clip.set_voice("京町セイカ", 京町セイカ)

    vop = Voiceroid2Options(speakerName="弦巻マキ",speakerStyle="ノーマル",speed=1.4,intonation=1.2,pitch=1.2)
    top = TelopOptions(text_color="yellow")
    弦巻マキ=CharacterVoice(vop,top)
    clip.set_voice("弦巻マキ", 弦巻マキ)

    しょんぼりずんだもん=CharacterVoice(VoicevoxOptions(speakerName="ずんだもん", speakerStyle="ノーマル",speed=1.2,pitch=-0.05,intonation=0.7),TelopOptions(text_color="#33FF33"))
    clip.set_voice("しょんぼりずんだもん", しょんぼりずんだもん)
    clip.back_ground(get_slide_path(6))
    setup_characters(clip)

def setup_characters(clip:Clip):
    # # キャラクタの初期設定
    clip.add_character("四国めたん", CharacterImageSettings(x=900,y=320,resize=0.3))
    clip.add_character("ずんだもん", CharacterImageSettings(x=1050,y=320,resize=0.3))
    clip.add_character_style("四国めたん", CharacterImageStyle(name="ノーマル",image_path="./resource/character/四国めたん_ノーマル.png"))
    clip.add_character_style("四国めたん", CharacterImageStyle(name="目そらし",image_path="./resource/character/四国めたん_目そらし.png"))
    clip.add_character_style("四国めたん", CharacterImageStyle(name="イエー",image_path="./resource/character/四国めたん_イエー.png"))
    clip.add_character_style("四国めたん", CharacterImageStyle(name="困り顔",image_path="./resource/character/四国めたん_困り顔.png"))
    clip.add_character_style("四国めたん", CharacterImageStyle(name="汗キャー",image_path="./resource/character/四国めたん_汗キャー.png"))
    clip.add_character_style("四国めたん", CharacterImageStyle(name="ペロ",image_path="./resource/character/四国めたん_ペロ.png"))
    clip.add_character_style("四国めたん", CharacterImageStyle(name="あっ",image_path="./resource/character/四国めたん_あっ.png"))

    clip.add_character_style("ずんだもん", CharacterImageStyle(name="ノーマル",image_path="./resource/character/ずんだもん_ノーマル.png"))
    clip.add_character_style("ずんだもん", CharacterImageStyle(name="ビックリ",image_path="./resource/character/ずんだもん_ビックリ.png"))
    clip.add_character_style("ずんだもん", CharacterImageStyle(name="イエー",image_path="./resource/character/ずんだもん_イエー.png"))
    clip.add_character_style("ずんだもん", CharacterImageStyle(name="右手挙げ",image_path="./resource/character/ずんだもん_右手挙げ.png"))
    clip.add_character_style("ずんだもん", CharacterImageStyle(name="困り顔",image_path="./resource/character/ずんだもん_困り顔.png"))
    clip.add_character_style("ずんだもん", CharacterImageStyle(name="目とじ考え",image_path="./resource/character/ずんだもん_目とじ考え.png"))
    clip.add_character_style("ずんだもん", CharacterImageStyle(name="両手挙げ",image_path="./resource/character/ずんだもん_両手挙げ.png"))
    clip.add_character_style("ずんだもん", CharacterImageStyle(name="推理",image_path="./resource/character/ずんだもん_推理.png"))
    clip.add_character_style("ずんだもん", CharacterImageStyle(name="ふんす",image_path="./resource/character/ずんだもん_ふんす.png"))
    clip.add_character_style("ずんだもん", CharacterImageStyle(name="汗アハハ",image_path="./resource/character/ずんだもん_汗アハハ.png"))
    clip.add_character_style("ずんだもん", CharacterImageStyle(name="涙むふ",image_path="./resource/character/ずんだもん_涙むふ.png"))


def show_title(clip:Clip):
    # # BGMとメイン動画を設定
    clip.se("./resource/se/イントロ.wav")    
    
    # パワポ1ページ目を表示
    clip.main_visual(get_slide_path(1), is_fullscreen=True)
    clip.wait(0.5)

    # パワポ2ページ目を表示
    clip.main_visual(get_slide_path(2), is_fullscreen=True)
    clip.se("./resource/se/pon.mp3")
    clip.v("ずんだもん", "ずんだもんと")
    clip.wait(0.5)

    # パワポ3ページ目を表示
    clip.main_visual(get_slide_path(3), is_fullscreen=True)
    clip.se("./resource/se/pon.mp3")
    clip.v("四国めたん", "四国めたんの")
    clip.wait(0.2)

    # パワポ4ページ目を表示
    clip.main_visual(get_slide_path(4), is_fullscreen=True)
    clip.se("./resource/se/kansei.mp3")
    clip.v("ずんだもん", f"スプラ実況")
    clip.v("四国めたん", f"スプラ実況!", is_same_timing=True)
    clip.main_visual(get_slide_path(5), is_fullscreen=True)
    clip.wait(2)
    clip.main_visual("", is_fullscreen=True, is_mute=True)



def main():
    clip = Clip()
    # パワポを画像に変換
    conv_pptx_to_img("./resource/slide/splatoon.pptx")
    setup(clip)

    clip.main_visual("./resource/movie/splatoon.mp4",0, 0,stop=True)
    clip.se("./resource/se/pon.mp3")
    clip.v("四国めたん", f"四国めたんです")
    clip.v("ずんだもん", f"ずんだもんなのだ")
    clip.v("東北イタコ", f"東北イタコです")
    clip.v("琴葉茜", f"茜ちゃんやで")
    clip.v("琴葉葵", f"葵です")
    clip.v("弦巻マキ", f"弦巻マキだよー")
    clip.v("結月ゆかり", f"ゆかりさんです")
    clip.v("紲星あかり", f"紲星あかりです")
    clip.v("京町セイカ", f"京町セイカです")

    clip.wait(0.5)
    clip.create_movie()

if __name__ == "__main__":
    main()

