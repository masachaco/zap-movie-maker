import math
from zap_movie_maker import *
from zap_movie_maker import *
from exolib import (
    ObjectNode,
    StandardDrawingParamNode,
    PositionRange,
    InsertionMode,
    VideoParamNode,
    AudioParamNode,
    ImageParamNode,
    StandardPlayingParamNode,
    ObjectParamNode
)
from exofile import String, Int

def main_visual_clips(exo,clips,layer_num,layer_num_2):
        for mv in clips:
            movie = ObjectNode()
            movie.add_objparam(
                VideoParamNode(
                    playbackposition=mv.fr * mv.fps,
                    file=mv.filename,
                )
            )
            x = mv.pos(0)[0]
            y = mv.pos(0)[1]
            x = (mv.w/2) - (1280/2) + x
            y = (mv.h/2) - (720/2) + y
            movie.add_objparam(StandardDrawingParamNode(x,y,0,scale=mv.resize_ratio*100))

            audio = ObjectNode(audio=True)
            audio.add_objparam(AudioParamNode(mv.audio.filename))
            audio.add_objparam(StandardPlayingParamNode(volume=mv.volume*100))
            
            mv_start = mv.start*24
            mv_end = mv.start*24 + 24*(mv.end-mv.start)
            mv_start = math.floor(1 if mv_start < 1 else mv_start)
            mv_end = math.floor(2 if mv_end < 1 else mv_end) - 1
            
            exo.insert_object(layer_num, PositionRange(mv_start, mv_end), movie, InsertionMode.SHIFT_LEFT)
            exo.insert_object(layer_num_2, PositionRange(mv_start, mv_end), audio, InsertionMode.SHIFT_LEFT)

def  background_clips(exo, clips,layer_num):
    class ChromakeyParamNode (ObjectParamNode):
        transformation_table = ObjectParamNode.transformation_table | {
            ("色相範囲", "色相範囲"): Int,
            ("彩度範囲", "彩度範囲"): Int,
            ("境界補正", "境界補正"): Int,
            ("色彩補正", "色彩補正"): Int,
            ("透過補正", "透過補正"): Int,
            ("color_yc", "color_yc"): String,
            ("status", "status"): Int,
        }

        def __init__ (self, **params):
            super().__init__(**params | { 
            "_name": "クロマキー",
            "色相範囲": 0,
            "彩度範囲": 0,
            "境界補正": 0,
            "色彩補正": 1,
            "透過補正": 0,
            "color_yc": "6109b3fa4af9", 
            "status": 1, 
            })

    for mv in clips:
        movie = ObjectNode()
        movie.add_objparam(
            ImageParamNode(
                file=mv.filename,
            )
        )
        movie.add_objparam(ChromakeyParamNode())
        x = mv.pos(0)[0]
        y = mv.pos(0)[1]
        x = (mv.w/2) - (1280/2) + x
        y = (mv.h/2) - (720/2) + y
        movie.add_objparam(StandardDrawingParamNode(x, y,0))

        mv_start = mv.start*24
        mv_end = mv.start*24 + 24*(mv.end-mv.start)
        mv_start = math.floor(1 if mv_start < 1 else mv_start)
        mv_end = math.floor(2 if mv_end < 1 else mv_end) - 1
        
        exo.insert_object(layer_num, PositionRange(mv_start, mv_end), movie, InsertionMode.SHIFT_LEFT)

def  character_clips(exo, clips,layer_num):
    for mv in clips:
        movie = ObjectNode()
        movie.add_objparam(
            ImageParamNode(
                file=mv.filename,
            )
        )
        x = mv.pos(0)[0]
        y = mv.pos(0)[1]
        x = (mv.w/2) - (1280/2) + x
        y = (mv.h/2) - (720/2) + y
        movie.add_objparam(StandardDrawingParamNode(x, y,0,scale=mv.resize_ratio*100))

        mv_start = mv.start*24
        mv_end = mv.start*24 + 24*(mv.end-mv.start)
        mv_start = math.floor(1 if mv_start < 1 else mv_start)
        mv_end = math.floor(2 if mv_end < 1 else mv_end) - 1
        exo.insert_object(layer_num, PositionRange(mv_start, mv_end), movie, InsertionMode.OVERWRITE)

def text_clips(exo,clips,telop_base_layer,voice_base_layer,rayer_map):
    for mv in clips:
        telop = ObjectNode()
        telop.add_objparam(ImageParamNode(mv.filename))
        x = mv.pos(0)[0]
        y = mv.pos(0)[1]
        x = (mv.w/2) - (1280/2) + x
        y = (mv.h/2) - (720/2) + y

        # speaker_idごとにレイヤを用意する
        voice_layer_id = 0
        if mv.speaker_id not in rayer_map:
            new_layer_id = rayer_map["max_9bef0e58_96ec_41c5_b091_acf4b7586e55"]+1
            voice_layer_id = new_layer_id
            rayer_map["max_9bef0e58_96ec_41c5_b091_acf4b7586e55"] = new_layer_id
            rayer_map[mv.speaker_id] = new_layer_id
        else:
            voice_layer_id = rayer_map[mv.speaker_id]

        mv_start = mv.start*24
        mv_end = mv.start*24 + 24*(mv.end-mv.start)
        mv_start = math.floor(1 if mv_start < 1 else mv_start)
        mv_end = math.floor(2 if mv_end < 1 else mv_end) - 1

        telop.add_objparam(StandardDrawingParamNode(x, y,0))
        exo.insert_object(voice_layer_id+telop_base_layer, PositionRange(mv_start, mv_end), telop, InsertionMode.OVERWRITE)

        audio = ObjectNode(audio=True)
        if mv.audio is not None and mv.audio.filename is not None:
            audio.add_objparam(AudioParamNode(mv.audio.filename))

        audio.add_objparam(StandardPlayingParamNode(volume=mv.volume*100))
        exo.insert_object(voice_layer_id+voice_base_layer, PositionRange(mv_start, mv_end), audio, InsertionMode.OVERWRITE)


def audio_clips(exo,clips,base_layer_id,rayer_map):
    for mv in clips:
        audio = ObjectNode(audio=True)
        audio.add_objparam(AudioParamNode(mv.audio.filename))
        audio.add_objparam(StandardPlayingParamNode(volume=mv.volume*100))
        # オーディオファイルごとにレイヤを用意する
        se_layer_id = 0
        if mv.audio.filename not in rayer_map:
            new_layer_id = rayer_map["max_9bef0e58_96ec_41c5_b091_acf4b7586e55"]+1
            se_layer_id = new_layer_id+base_layer_id
            rayer_map["max_9bef0e58_96ec_41c5_b091_acf4b7586e55"] = new_layer_id
            rayer_map[mv.audio.filename] = new_layer_id
        else:
            se_layer_id = rayer_map[mv.audio.filename]
            
        mv_start = mv.start*24
        mv_end = mv.start*24 + 24*(mv.end-mv.start)
        mv_start = math.floor(1 if mv_start < 1 else mv_start)
        mv_end = math.floor(2 if mv_end < 1 else mv_end) - 1

        exo.insert_object(se_layer_id, PositionRange(mv_start, mv_end), audio, InsertionMode.OVERWRITE)


