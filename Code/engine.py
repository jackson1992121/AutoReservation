import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.core.window import Window
from datetime import datetime
Window.size = (400, 420)

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from automation import wait_between, execute_auto
import os, sys

# add the following 2 lines to solve OpenGL 2.0 bug
from kivy import Config
Config.set('graphics', 'multisamples', '0')
os.environ['KIVY_GL_BACKEND'] = 'glew'

global log_file_path

lesson_data = {
    "表参道東京": "000014",
    "銀座東京": "000035",
    "銀座中央": "000053",
    "東中野東京": "000024",
    "四ツ谷東京": "000052"
}

def get_lesson_data():
    try:
        cur_data = {}
        with open('lessons.txt', encoding = 'utf-8') as f:
            for item in f:
                cur_line = item.strip()
                cur_data[cur_line.split("---")[0]] = cur_line.split("---")[1]
    except: 
        cur_data = lesson_data
        pass
    return cur_data

class LblTxt(BoxLayout):
    from kivy.properties import ObjectProperty
    theTxt = ObjectProperty(None)

class DropDownLayout(BoxLayout):    
    pass

class CustomSpinner(Spinner):
    pass

class MyApp(App):

    global log_file_path

    placeholder = "必須項目"
    lesson_name = "予約店舗名"
    select_lesson = "選択"
    week_day = "曜日"
    time_range = "開始時間帯"
    cur_time_range = 8
    cur_week_day = str(1 if ( datetime.now().weekday() + 1 ) % 7 == 0 else ( datetime.now().weekday() + 1 ) % 7)
    cur_lesson_data = {}

    account_id = "アカウントID"
    account_name = "calcio"
    account_password = "パスワード"
    account_pwd = "adam"

    lesson_1 = "表参道東京"
    lesson_2 = "銀座東京"
    lesson_3 = "銀座中央"
    lesson_4 = "東中野東京"
    lesson_5 = "四ツ谷東京"
    cur_lesson = "表参道東京"

    help_text_1 = "曜日 ⇒「 日：1, 月：2, ... , 土：7 」"
    help_text_2 = "開始時間帯 ⇒「 ～8時台: 8, 9時台: 9, ... , 23時台: 23 」"

    button_text = '予約を行う'

    def build(self):
        self.title = "自動予約"
        self.cur_lesson_data = get_lesson_data()
        print(self.cur_lesson_data)

        with open('form.kv', encoding = 'utf-8') as f:
            self.root = Builder.load_string(f.read())
            print(self.root)
            # self.root = Builder.load_file('form.kv')
            return self.root

    def get_time_range(self, time_range):
        if time_range == "8":
            return "00-08"
        else:
            return "{0}-{0}".format(format(int(time_range), '02d'))

    def start_automation(self, id, pwd, lesson_id, weekday, time_range):
        import ctypes

        id_array = []
        for key in self.cur_lesson_data:
            id_array.append(self.cur_lesson_data[key])

        if int(lesson_id) < 0 and int(lesson_id) > len(id_array):
            write_log_file(log_file_path, "レッスンの番号が無効です")
            return

        if execute_auto(id, pwd, id_array[int(lesson_id) - 1], weekday, self.get_time_range(time_range)):
            ctypes.windll.user32.MessageBoxW(0, "予約が成功しました", "予約成功", 0x40000)
        else:
            ctypes.windll.user32.MessageBoxW(0, "予約が失敗しました", "予約失敗", 0x40000)

def resourcePath():
    '''Returns path containing content - either locally or in pyinstaller tmp file'''
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)

    return os.path.join(os.path.abspath("."))

def write_log_file(cur_path, cur_log_text):    
    log_file = open(cur_path, "a", encoding="utf-8")
    cur_time_str = datetime.now().strftime("%m{0}%d{1} %H{2} %M{3} %S{4}: ").format(*"月日時分秒")
    log_file.write(cur_time_str + cur_log_text + "\n")
    
    log_file.close()

def main():
    global log_file_path
    # open log file
    file_name = "log_{0}.txt".format(datetime.now().strftime("%Y%m%d"))
    cur_path = os.path.dirname(os.path.abspath(__file__))
    cur_log = os.path.join(cur_path, "log")
    log_file_path = os.path.join(cur_log, file_name)
    
    if not os.path.exists(cur_log):
        os.mkdir(cur_log)    
    
    write_log_file(log_file_path, "スタート")
    kivy.resources.resource_add_path(resourcePath())
    my_app = MyApp()
    my_app.run()


if __name__ == '__main__':
    main()

    
