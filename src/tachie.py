from email.mime import base
from select import select
import psd_tools
from enum import Enum

class PsdUtil:
    target_layers = []
    @classmethod
    def show_visible_layer_list(cls, kaisou, layer,route):
        if layer.is_group():
            for k, child in enumerate(layer):
                PsdUtil.show_visible_layer_list(kaisou+1, child,route+"/"+child.name)
        else:
            if layer.is_visible():
                print(route)

    @classmethod
    def show_layer_list(cls, kaisou, layer,route):
        if layer.is_group():
            for k, child in enumerate(layer):
                PsdUtil.show_layer_list(kaisou+1, child,route+"/"+child.name)
        else:
            print(route)
    @classmethod
    def set_visibility(cls, kaisou, layer,route):
        if layer.is_group():
            for k, child in enumerate(layer):
                PsdUtil.set_visibility(kaisou+1, child,route+"/"+child.name)
        else:
            if route in PsdUtil.target_layers:
                layer.visible = True
            else:
                layer.visible = False
    @classmethod
    def export(cls, psd,name):
        for k, layer in enumerate(psd):
            PsdUtil.set_visibility(0, layer,layer.name)
        psd.composite(force=True).save(f'./resource/character/{name}.png')
        psd.composite(force=True).save(f'./sample.png')
    @classmethod
    def show_layers(cls, psd):
        for k, layer in enumerate(psd):
            PsdUtil.show_layer_list(0, layer,layer.name)
    @classmethod
    def show_visible_layers(cls, psd):
        for k, layer in enumerate(psd):
            PsdUtil.show_visible_layer_list(0, layer,layer.name)


class 四国めたん:

    def gen(self, path, name):
        ret = []
        ret.extend(self.white_eye)
        ret.extend(self.base_layers)
        ret.extend(self.eye)
        ret.extend(self.left_hand)
        ret.extend(self.right_hand)
        ret.extend(self.mouth)
        ret.extend(self.eyebrow)
        ret.extend(self.complexion)
        ret.extend(self.extention)
        ret.sort()
        PsdUtil.target_layers = ret
        psd = psd_tools.PSDImage.open(path)
        PsdUtil.export(psd,name)

    def __init__(self):
        self.base_layers = [
            "ツインドリル右",
            "ツインドリル左",
            "*白ロリ服/!体",        
            "頭部アクセサリ/髪留めハート",
            "頭部アクセサリ/ヘッドドレス",
            "!前髪もみあげ",
        ]
        self.white_eye = ["!目/*目セット/*普通白目"]
        self.eye = ["!目/*目セット/!黒目/*カメラ目線"]
        self.left_hand = ["*白ロリ服/!左腕/*普通",]
        self.right_hand = ["*白ロリ服/!右腕/*普通"]
        self.mouth = ["!口/*ほほえみ"]
        self.eyebrow = ["!眉/*太眉ごきげん"]   
        self.complexion = ["!顔色/*普通2"]
        self.extention = []

    def set_右腕(self, add):
        self.right_hand = add
        return self
    
    def set_左腕(self, add):
        self.left_hand = add
        return self

    def set_口(self, add):
        self.mouth = add
        return self

    def set_黒目(self, add):
        self.eye = add
        return self
    
    def set_白目(self,add):
        self.white_eye = add
        return self

    def set_眉(self, add):
        self.eyebrow = add
        return self
    
    def set_記号(self,add):
        self.extention = add
        return self
    
    def set_顔色(self, add):
        self.complexion = add
        return self

    def 記号_汗(self):
        self.set_記号(["記号など/汗"])
        return self

    def 記号_涙(self):
        self.set_記号(["記号など/涙"])
        return self

    def 顔色_かげり(self):
        self.set_顔色(["!顔色/かげり"])
        return self

    def 顔色_非表示(self):
        self.set_顔色(["!顔色/*(非表示)"])
        return self

    def 顔色_青ざめ(self):
        self.set_顔色(["!顔色/*青ざめ"])
        return self

    def 顔色_赤面(self):
        self.set_顔色(["!顔色/*赤面"])
        return self

    def 顔色_普通2(self):
        self.set_顔色(["!顔色/*普通2"])
        return self

    def 顔色_普通(self):
        self.set_顔色(["!顔色/*普通"])
        return self

    def 眉_太眉こまり(self):
        self.set_眉(["!眉/*太眉こまり"])
        return self

    def 眉_太眉おこ(self):
        self.set_眉(["!眉/*太眉おこ"])
        return self

    def 眉_太眉ごきげん(self):
        self.set_眉(["!眉/*太眉ごきげん"])
        return self

    def 眉_こまり(self):
        self.set_眉(["!眉/*こまり"])
        return self

    def 眉_おこ(self):
        self.set_眉(["!眉/*おこ"])
        return self

    def 眉_ややおこ(self):
        self.set_眉(["!眉/*ややおこ"])
        return self

    def 眉_ごきげん(self):
        self.set_眉(["!眉/*ごきげん"])
        return self

    def 黒目_ぐるぐる(self):
        self.set_白目([])
        self.set_黒目(["!目/*ぐるぐる"])
        return self

    def 黒目_キャー(self):
        self.set_白目([])
        self.set_黒目(["!目/*><"])
        return self

    def 黒目_oo(self):
        self.set_白目([])
        self.set_黒目(["!目/*○○"])
        return self

    def 黒目_目閉じ2(self):
        self.set_白目([])
        self.set_黒目(["!目/*目閉じ2"])
        return self

    def 黒目_目閉じ(self):
        self.set_白目([])
        self.set_黒目(["!目/*目閉じ"])
        return self

    def 黒目_見上げ2(self):
        self.set_白目([])
        self.set_黒目(["!目/*見上げ2"])
        return self

    def 黒目_見上げ(self):
        self.set_白目([])
        self.set_黒目(["!目/*見上げ"])
        return self

    def 白目_見開き(self):
        self.set_白目(["!目/*目セット/*見開き白目"])
        return self

    def 白目_普通(self):
        self.set_白目(["!目/*目セット/*普通白目"])
        return self

    def 黒目_普通(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*普通目"])
        return self

    def 黒目_普通2(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*普通目2"])
        return self

    def 黒目_カメラ目線(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*カメラ目線"])
        return self

    def 黒目_カメラ目線2(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*カメラ目線2"])
        return self

    def 黒目_目そらし(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*目そらし"])
        return self

    def 黒目_目そらし2(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*目そらし2"])
        return self

    def 口_もむー(self):
        self.set_口(["!口/*もむー"])
        return self

    def 口_んー(self):
        self.set_口(["!口/*んー"])
        return self

    def 口_うえー(self):
        self.set_口(["!口/*うえー"])
        return self

    def 口_いー(self):
        self.set_口(["!口/*いー"])
        return self

    def 口_む(self):
        self.set_口(["!口/*む"])
        return self

    def 口_上サンカク(self):
        self.set_口(["!口/*△"])
        return self

    def 口_ゆ(self):
        self.set_口(["!口/*ゆ"])
        return self

    def 口_お(self):
        self.set_口(["!口/*お"])
        return self

    def 口_ぺろり(self):
        self.set_口(["!口/*ぺろり"])
        return self

    def 口_にやり(self):
        self.set_口(["!口/*にやり"])
        return self

    def 口_下サンカク(self):
        self.set_口(["!口/*▽"])
        return self

    def 口_ほほえみ(self):
        self.set_口(["!口/*ほほえみ"])
        return self

    def 口_わあー(self):
        self.set_口(["!口/*わあー"])
        return self

    def 左腕_まんじゅう袋(self):
        self.set_左腕(["*白ロリ服/!左腕/*抱える", "*白ロリ服/!左腕/まんじゅう袋"])
        return self
    
    def 左腕_抱える(self):
        self.set_左腕(["*白ロリ服/!左腕/*抱える"])
        return self
        
    def 左腕_マイク(self):
        self.set_左腕(["*白ロリ服/!左腕/*マイク"])
        return self
    
    def 左腕_ひそひそ(self):
        self.set_左腕(["*白ロリ服/!左腕/*ひそひそ"])
        return self
        
    def 左腕_口元に指(self):
        self.set_左腕(["*白ロリ服/!左腕/*口元に指"])
        return self
        
    def 左腕_普通(self):
        self.set_左腕(["*白ロリ服/!左腕/*普通"])
        return self

    def 右腕_饅頭(self):
        self.set_右腕(["*白ロリ服/!右腕/*手をかざす","*白ロリ服/!右腕/まんじゅう"])
        return self

    def 右腕_手をかざす(self):
        self.set_右腕(["*白ロリ服/!右腕/*手をかざす"])
        return self

    def 右腕_指差す(self):
        self.set_右腕(["*白ロリ服/!右腕/*指差す"])
        return self

    def 右腕_普通(self):
        self.set_右腕(["*白ロリ服/!右腕/*普通"])
        return self

class ずんだもん:

    def gen(self, path, name):
        ret = []
        ret.extend(self.base_layers)
        ret.extend(self.white_eye)
        ret.extend(self.eye)
        ret.extend(self.left_hand)
        ret.extend(self.right_hand)
        ret.extend(self.mouth)
        ret.extend(self.eyebrow)
        ret.extend(self.complexion)
        ret.extend(self.extention)
        ret.sort()
        PsdUtil.target_layers = ret
        psd = psd_tools.PSDImage.open(path)
        PsdUtil.export(psd,name)

    def __init__(self):
        self.base_layers = [
            "尻尾的なアレ",
            "*服装1/*いつもの服",
            "!枝豆/*枝豆通常",
        ]
        self.white_eye = ["!目/*目セット/*普通白目"]
        self.eye = ["!目/*目セット/!黒目/*普通目",]
        self.left_hand = ["*服装1/!左腕/*基本",]
        self.right_hand = ["*服装1/!右腕/*基本",]
        self.mouth = ["!口/*ほあー",]
        self.eyebrow = ["!眉/*怒り眉",]   
        self.complexion = ["!顔色/*ほっぺ",]
        self.extention = []

    def set_右腕(self, add):
        self.right_hand = add
        return self
    
    def set_左腕(self, add):
        self.left_hand = add
        return self

    def set_口(self, add):
        self.mouth = add
        return self
    
    def set_白目(self, add):
        self.white_eye = add
        return self

    def set_黒目(self, add):
        self.eye = add
        return self

    def set_眉(self, add):
        self.eyebrow = add
        return self
    
    def set_顔色(self, add):
        self.complexion = add
        return self
    
    def set_記号(self,add):
        self.extention = add
        return self

    def 左腕_非表示(self):
        self.set_左腕(["*服装1/!左腕/*(非表示)"])
        return self

    def 左腕_ひそひそ(self):
        self.set_左腕(["*服装1/!左腕/*ひそひそ"])
        return self

    def 左腕_考える(self):
        self.set_左腕(["*服装1/!左腕/*考える"])
        return self

    def 左腕_苦しむ(self):
        self.set_左腕(["*服装1/!左腕/*苦しむ"])
        return self

    def 左腕_口元(self):
        self.set_左腕(["*服装1/!左腕/*口元"])
        return self

    def 左腕_手を挙げる(self):
        self.set_左腕(["*服装1/!左腕/*手を挙げる"])
        return self

    def 左腕_腰(self):
        self.set_左腕(["*服装1/!左腕/*腰"])
        return self

    def 左腕_基本(self):
        self.set_左腕(["*服装1/!左腕/*基本"])
        return self

    def 右腕_非表示(self):
        self.set_右腕(["*服装1/!右腕/*(非表示)"])
        return self

    def 右腕_マイク(self):
        self.set_右腕(["*服装1/!右腕/*マイク"])
        return self

    def 右腕_指差し(self):
        self.set_右腕(["*服装1/!右腕/*指差し"])
        return self

    def 右腕_苦しむ(self):
        self.set_右腕(["*服装1/!右腕/*苦しむ"])
        return self

    def 右腕_口元(self):
        self.set_右腕(["*服装1/!右腕/*口元"])
        return self

    def 右腕_手を挙げる(self):
        self.set_右腕(["*服装1/!右腕/*手を挙げる"])
        return self

    def 右腕_腰(self):
        self.set_右腕(["*服装1/!右腕/*腰"])
        return self

    def 右腕_基本(self):
        self.set_右腕(["*服装1/!右腕/*基本"])
        return self

    def 口_ほあー(self):
        self.set_口(["!口/*ほあー"])
        return self

    def 口_ほあ(self):
        self.set_口(["!口/*ほあ"])
        return self

    def 口_ほー(self):
        self.set_口(["!口/*ほー"])
        return self

    def 口_むふ(self):
        self.set_口(["!口/*むふ"])
        return self

    def 口_上サンカク(self):
        self.set_口(["!口/*△"])
        return self

    def 口_んあー(self):
        self.set_口(["!口/*んあー"])
        return self

    def 口_んへー(self):
        self.set_口(["!口/*んへー"])
        return self

    def 口_んー(self):
        self.set_口(["!口/*んー"])
        return self

    def 口_はへえ(self):
        self.set_口(["!口/*はへえ"])
        return self

    def 口_おほお(self):
        self.set_口(["!口/*おほお"])
        return self

    def 口_お(self):
        self.set_口(["!口/*お"])
        return self

    def 口_ゆ(self):
        self.set_口(["!口/*ゆ"])
        return self

    def 口_むー(self):
        self.set_口(["!口/*むー"])
        return self

    def 顔色_かげり(self):
        self.set_顔色(["!顔色/かげり"])
        return self

    def 顔色_非表示(self):
        self.set_顔色(["!顔色/*(非表示)"])
        return self

    def 顔色_青ざめ(self):
        self.set_顔色(["!顔色/*青ざめ"])
        return self

    def 顔色_ほっぺ赤め(self):
        self.set_顔色(["!顔色/*ほっぺ赤め"])
        return self

    def 顔色_ほっぺ2(self):
        self.set_顔色(["!顔色/*ほっぺ2"])
        return self

    def 顔色_ほっぺ(self):
        self.set_顔色(["!顔色/*ほっぺ"])
        return self

    def 白目_見開き白目(self):
        self.set_白目(["!目/*目セット/*見開き白目"])
        return self

    def 白目_ジト白目(self):
        self.set_白目(["!目/*目セット/*ジト白目"])
        return self

    def 白目_普通白目(self):
        self.set_白目(["!目/*目セット/*普通白目"])
        return self

    def 黒目_ぐるぐる(self):
        self.set_黒目(["!目/*ぐるぐる"])
        return self

    def 黒目_oo(self):
        self.set_白目([])
        self.set_黒目(["!目/*〇〇"])
        return self

    def 黒目_キャー(self):
        self.set_白目([])
        self.set_黒目(["!目/*><"])
        return self

    def 黒目_UU(self):
        self.set_白目([])
        self.set_黒目(["!目/*UU"])
        return self

    def 黒目_にっこり2(self):
        self.set_白目([])
        self.set_黒目(["!目/*にっこり2"])
        return self

    def 黒目_にっこり(self):
        self.set_白目([])
        self.set_黒目(["!目/*にっこり"])
        return self

    def 黒目_なごみ(self):
        self.set_白目([])
        self.set_黒目(["!目/*なごみ目"])
        return self

    def 黒目_ジト目(self):
        self.set_白目([])
        self.set_黒目(["!目/*ジト目"])
        return self

    def 黒目_細め目(self):
        self.set_白目([])
        self.set_黒目(["!目/*細め目"])
        return self

    def 黒目_細め目ハート(self):
        self.set_白目([])
        self.set_黒目(["!目/*細め目ハート"])
        return self

    def 黒目_上向き3(self):
        self.set_白目([])
        self.set_黒目(["!目/*上向き3"])
        return self

    def 黒目_上向き2(self):
        self.set_白目([])
        self.set_黒目(["!目/*上向き2"])
        return self

    def 黒目_上向き(self):
        self.set_白目([])
        self.set_黒目(["!目/*上向き"])
        return self

    def 黒目_目逸らし3(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*目逸らし3"])
        return self

    def 黒目_目逸らし2(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*目逸らし2"])
        return self

    def 黒目_目逸らし(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*目逸らし"])
        return self

    def 黒目_カメラ目線3(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*カメラ目線3"])
        return self

    def 黒目_カメラ目線2(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*カメラ目線2"])
        return self

    def 黒目_カメラ目線(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*カメラ目線"])
        return self

    def 黒目_普通目3(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*普通目3"])
        return self

    def 黒目_普通目2(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*普通目2"])
        return self

    def 黒目_普通目(self):
        if len(self.white_eye) == 0:
            self.白目_普通()
        self.set_黒目(["!目/*目セット/!黒目/*普通目"])
        return self

    def 眉_困り眉2(self):
        self.set_眉(["!眉/*困り眉2"])
        return self

    def 眉_困り眉1(self):
        self.set_眉(["!眉/*困り眉1"])
        return self

    def 眉_上がり眉(self):
        self.set_眉(["!眉/*上がり眉"])
        return self

    def 眉_怒り眉(self):
        self.set_眉(["!眉/*怒り眉"])
        return self

    def 眉_普通眉(self):
        self.set_眉(["!眉/*普通眉"])
        return self

    def 記号_汗1(self):
        self.set_記号(["記号など/汗1"])
        return self

    def 記号_汗2(self):
        self.set_記号(["記号など/汗2"])
        return self

    def 記号_汗3(self):
        self.set_記号(["記号など/汗3"])
        return self

    def 記号_汗3(self):
        self.set_記号(["記号など/汗3"])
        return self

    def 記号_涙(self):
        self.set_記号(["記号など/涙"])
        return self

    def 記号_アヒルちゃん(self):
        self.set_記号(["記号など/アヒルちゃん"])
        return self

def main():
    print("filename.")
    name = input()
    if name is None or name.strip() == "":
        name = "sample"
    # PsdUtil.show_layers(psd)
    # PsdUtil.show_visible_layers(psd)
    四国めたん_PATH = 'C:\\Users\\Masa\\Desktop\\ずんだもんの競馬場紀行\\zap-movie-maker\\resource\\psd\\四国めたん立ち絵素材2.1.psd'
    四国めたん().gen(四国めたん_PATH, name)

    # ずんだもん_PATH = "C:\\Users\\Masa\\Desktop\\ずんだもんの競馬場紀行\\zap-movie-maker\\resource\\psd\\ずんだもん立ち絵素材2.3.psd"
    # ずんだもん().眉_普通眉().黒目_oo().口_むふ().記号_涙().gen(ずんだもん_PATH,name)


main()


