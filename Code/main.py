import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import StringProperty
from datetime import datetime
Window.size = (400, 500)

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from automation import wait_between, execute_auto
import os, sys
from sendmail import sendMail

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

class DisplayTxt(BoxLayout):
    lblTxtIn = StringProperty()

class MyLayout(BoxLayout):
    pass  

class MyApp(App):

    global log_file_path
 
    placeholder = "必須項目"
    lesson_name = "予約店舗名"
    lesson_index = "1"
    select_lesson = "選択"
    week_day = "曜日"
    time_range = "開始時間帯"
    user_email = ""
    cur_time_range = "8"
    cur_week_day = str(1 if ( datetime.now().weekday() + 2 ) % 8 == 0 else ( datetime.now().weekday() + 2 ) % 8)
    cur_lesson_data = {}
    cur_lesson_array = []

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
    weekday_array = ["日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"]    

    button_text = '予約を行う'
    selected_name = ""
    selected_weekday = ""
    lesson_tag = None
    weekday_tag = None

    def get_lesson_name(self, cur_lesson_index):
        try:
            return self.cur_lesson_array[int(cur_lesson_index, 10) - 1] 
        except Exception as e:
            print(e)
            return ""

    def get_weekday_string(self, cur_weekday_index):
        try: 
            return self.weekday_array[int(cur_weekday_index, 10) - 1]
        except:
            return ""            

    def get_input_data(self):
        # lesson and weekday
        try:
            with open('input.txt', encoding='utf-8') as f:
                input_data = f.readline().strip()
                [self.account_name, self.account_pwd, self.lesson_index, self.cur_week_day, self.cur_time_range] = input_data.split(" ")                
        except Exception as e:
            pass
        self.selected_name = self.cur_lesson_array[int(self.lesson_index) - 1]
        self.selected_weekday = self.weekday_array[int(self.cur_week_day) - 1]

        # email
        try:
            with open('email.txt', encoding='utf-8') as f:
                input_data = f.readline().strip()
                self.user_email = input_data
        except Exception as e:
            pass

    def change_input(self, cur_text, cur_id):

        if cur_id == "lesson":
            self.lesson_index = cur_text
            if self.lesson_tag:
                self.lesson_tag.lblTxtIn = self.get_lesson_name(self.lesson_index)
           
        elif cur_id == "weekday":
            self.cur_week_day = cur_text
            if self.weekday_tag:
                self.weekday_tag.lblTxtIn = self.get_weekday_string(self.cur_week_day)

    def build(self):
        self.title = "自動予約"
        self.cur_lesson_data = get_lesson_data()
        
        for cur_key in self.cur_lesson_data.keys():
            self.cur_lesson_array.append(cur_key)
        print(self.cur_lesson_array)

        self.get_input_data()

        with open('form.kv', encoding = 'utf-8') as f:
            self.root = Builder.load_string(f.read())
            self.lesson_tag = self.root.children[5]
            self.weekday_tag = self.root.children[3]
            return self.root

    def get_time_range(self, time_range):
        if time_range == "8":
            return "00-08"
        else:
            return "{0}-{0}".format(format(int(time_range), '02d'))

    def start_automation(self, userid, pwd, lesson_id, weekday, time_range):
        import ctypes

        # save user settings
        cur_path = os.path.dirname(os.path.abspath(__file__))
        input_file_path = os.path.join(cur_path, "input.txt")
        if os.path.exists(input_file_path):
            os.remove(input_file_path)
        f = open(input_file_path, "w")
        f.write("{0} {1} {2} {3} {4}\n".format(userid, pwd, lesson_id, weekday, time_range))
        f.close()

        # run auto
        id_array = []
        for key in self.cur_lesson_data:
            id_array.append(self.cur_lesson_data[key])

        if int(lesson_id) < 0 and int(lesson_id) > len(id_array):
            write_log_file(log_file_path, "レッスンの番号が無効です")
            return

        result_status = execute_auto(userid, pwd, id_array[int(lesson_id) - 1], weekday, self.get_time_range(time_range))

        if result_status == "true":
            write_log_file(log_file_path, "予約が成功しました")
            if self.user_email != "":
                sendMail("成功", "楽しい時間をお過ごしください。", self.user_email)
            ctypes.windll.user32.MessageBoxW(0, "予約が成功しました", "予約成功", 0x40000)
            
        elif result_status == "false":
            write_log_file(log_file_path, "予約が失敗しました")
            if self.user_email != "":
                sendMail("失敗", "予約が失敗しました。", self.user_email)
            ctypes.windll.user32.MessageBoxW(0, "予約が失敗しました", "予約失敗", 0x40000)
            
        elif result_status == "driver":
            write_log_file(log_file_path, "ドライバーを更新してください")
            if self.user_email != "":
                sendMail("失敗", "ドライバーを更新してください。", self.user_email)
            ctypes.windll.user32.MessageBoxW(0, "ドライバーを更新してください", "予約失敗", 0x40000)
            
        elif result_status == "account":
            write_log_file(log_file_path, "正確なアカウントを入力してください")
            if self.user_email != "":
                sendMail("失敗", "正確なアカウントを入力してください。", self.user_email)
            ctypes.windll.user32.MessageBoxW(0, "ログイン失敗", "予約失敗", 0x40000)
            

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

    
