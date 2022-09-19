import os
import shutil
import win32com.client
import yaml
import csv

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

