from time import sleep
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.button import MDRectangleFlatButton
from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import MDList
from kivymd.uix.gridlayout import GridLayout
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

import pytesseract
pytesseract.pytesseract.tesseract_cmd="/usr/bin/tesseract"

import sqlite3
con = sqlite3.connect('library_data.db')
import scan_qr as qr
######
#DATABASE
######
import sqlite3
con = sqlite3.connect('library_data.db')

cur = con.cursor()

# cur.execute('''DROP TABLE exchange''')

cur.execute('''CREATE TABLE IF NOT EXISTS users
               (name text, id text, stdid text PRIMARY KEY)''')

cur.execute('''CREATE TABLE IF NOT EXISTS books
               (name text, id text PRIMARY KEY, pcs INTEGER )''')

cur.execute('''CREATE TABLE IF NOT EXISTS exchange
               (book_id text, std_id text , status INTEGER,CONSTRAINT unq UNIQUE (book_id, std_id, status) )''')
con.commit()
######
# Camera Setup
######
import cv2

#########
# Globa Variables
#########

class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='home_screen'
        self.home_loop=None

    def close_app(self):
        print(self)

    def on_enter(self):
        print('Entered '+self.name)
        self.home_loop=Clock.schedule_interval(self.loop,0)

    def on_pre_leave(self):
        Clock.unschedule(self.home_loop)
        print('Leaving '+self.name)

    def go_enrole_screen(self):
        my_app.screen_manager.current='enrole_screen'

    def go_exchange_screen(self):
        my_app.screen_manager.current='exchange_screen'

    def go_check_screen(self):
        my_app.screen_manager.current='list_select_screen'

    def loop(self,dt):
        pass
        
class EnroleScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='enrole_screen'
    
    def on_enter(self):
        self.this_loop=Clock.schedule_interval(self.loop,0)
        print('Entered '+self.name)

    def on_pre_leave(self):
        Clock.unschedule(self.this_loop)
        print('Leaving '+self.name)
    
    def loop(self,dt):
        pass
class ExchangeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='exchange_screen'
        self.stage=0
        
    
    def on_enter(self):
        print('Entered '+self.name)
        self.cap = cv2.VideoCapture(0)
        # self.cap.set(3,400)
        # self.cap.set(4,400)
        if not self.cap.isOpened():
            print("Cannot open webcam")
        else:
            print("cam Found")
        self.this_loop=Clock.schedule_interval(self.loop,0)
    def back(self):
        my_app.screen_manager.current='home_screen'
    def on_pre_leave(self):
        Clock.unschedule(self.this_loop)
        self.cap.release()
        print('Leaving '+self.name)
    
    def loop(self,dt):
        ret, frame = self.cap.read()
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        book_id=qr.scan(frame)
        if book_id:
            print(book_id)
        # if self.stage==0:
        #     id=(pytesseract.image_to_string(frame))
        #     print(id)
        #     if id=='A':
        #         self.stage+=1
        # elif self.stage==1:
        #     my_app.screen_manager.current='home_screen'
        # Preview
        frame = cv2.flip(frame,-1)
        buf=frame.tobytes()
        image_texture= Texture.create(size=(frame.shape[1],frame.shape[0]),colorfmt='rgb')
        image_texture.blit_buffer(buf,colorfmt='rgb',bufferfmt='ubyte')
        self.ids['preview'].texture =image_texture
class BookListScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='book_list_screen'
        
    def on_enter(self):
        print('Entered '+self.name)
        self.this_loop=Clock.schedule_interval(self.loop,0)
        try:
            book_ids=[]
            borrowed=[]
            row_datas=[]
            for row in cur.execute('SELECT * FROM books ' ):
                book_ids.append(row[1])
            print(book_ids)
            for id in book_ids:
                borrowed.append(cur.execute(f'SELECT COUNT(*) FROM exchange WHERE book_id={id} AND status=1').fetchall()[0][0])
            print(borrowed)
            print("Name","ID", "Borrowed","Available","Total")
            for n, row in enumerate(cur.execute('SELECT * FROM books ')):
                row_datas.append((n+1,row[0],row[1], borrowed[n], row[2]-borrowed[n], row[2]))
                print(n+1,row[0],row[1], borrowed[n], row[2]-borrowed[n], row[2])
            print(row_datas)
            self.data_table = MDDataTable(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                    size_hint=(0.9, 0.9),
                                    #  check=True,
                                    rows_num=len(row_datas),
                                    column_data=[
                                        ("No.", dp(15)),
                                        ("Name", dp(50)),
                                        ("ID", dp(20)),
                                        ("Borrowed", dp(20)),
                                        ("Available", dp(20)),
                                        ("Total", dp(20))
                                    ],
                                    row_data=row_datas
                                    )
            self.ids["bookTable"].add_widget(self.data_table)
            self.data_table.bind(on_row_press=self.back)
        except Exception as e:
            print(e, "Table or data Not Found")

    def back(self,a,b):
        my_app.screen_manager.current='list_select_screen'
    def on_pre_leave(self):
        Clock.unschedule(self.this_loop)
        self.ids["bookTable"].remove_widget(self.data_table)
        print('Leaving '+self.name)
    
    def loop(self,dt):
        pass
        # sleep(5)
        # self.back()
class StudentListScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='student_list_screen'
        
    def on_enter(self):
        print('Entered '+self.name)
        self.this_loop=Clock.schedule_interval(self.loop,0)
        try:
            book_ids=[]
            borrowed=[]
            row_datas=[]
            for row in cur.execute('SELECT * FROM books ' ):
                book_ids.append(row[1])
            print(book_ids)
            for id in book_ids:
                borrowed.append(cur.execute(f'SELECT COUNT(*) FROM exchange WHERE book_id={id} AND status=1').fetchall()[0][0])
            print(borrowed)
            print("Name","ID", "Borrowed","Available","Total")
            for n, row in enumerate(cur.execute('SELECT * FROM books ')):
                row_datas.append((n+1,row[0],row[1], borrowed[n], row[2]-borrowed[n], row[2]))
                print(n+1,row[0],row[1], borrowed[n], row[2]-borrowed[n], row[2])
            print(row_datas)
            self.data_table = MDDataTable(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                    size_hint=(0.9, 0.9),
                                    #  check=True,
                                    rows_num=len(row_datas),
                                    column_data=[
                                        ("No.", dp(15)),
                                        ("Name", dp(50)),
                                        ("ID", dp(20)),
                                        ("Borrowed", dp(20)),
                                        ("Available", dp(20)),
                                        ("Total", dp(20))
                                    ],
                                    row_data=row_datas
                                    )
            self.ids["bookTable"].add_widget(self.data_table)
            self.data_table.bind(on_row_press=self.back)
        except Exception as e:
            print(e, "Table or data Not Found")
            
    def back(self,a,b):
        my_app.screen_manager.current='list_select_screen'
    def on_pre_leave(self):
        Clock.unschedule(self.this_loop)
        self.ids["bookTable"].remove_widget(self.data_table)
        print('Leaving '+self.name)
    
    def loop(self,dt):
        pass
        # sleep(5)
        # self.back()
class ListSelectScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='list_select_screen'
        
    def on_enter(self):
        print('Entered '+self.name)
        self.this_loop=Clock.schedule_interval(self.loop,0)
    def back(self):
        my_app.screen_manager.current='home_screen'
    def on_pre_leave(self):
        Clock.unschedule(self.this_loop)
        print('Leaving '+self.name)
    def go_book_screen(self):
        my_app.screen_manager.current='book_list_screen'
    def go_student_screen(self):
        my_app.screen_manager.current='student_list_screen'
    def loop(self,dt):
        pass
        # sleep(5)
        # self.back()
class LibraryApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):

        self.screen_manager = ScreenManager()

        self.home_screen = HomeScreen()
        self.screen_manager.add_widget(self.home_screen)

        self.enrole_screen = EnroleScreen()
        self.screen_manager.add_widget(self.enrole_screen)

        self.exchange_screen = ExchangeScreen()
        self.screen_manager.add_widget(self.exchange_screen)

        self.book_list_screen = BookListScreen()
        self.screen_manager.add_widget(self.book_list_screen)

        self.student_list_screen = StudentListScreen()
        self.screen_manager.add_widget(self.student_list_screen)

        self.list_select_screen = ListSelectScreen()
        self.screen_manager.add_widget(self.list_select_screen)


        # self.atd_complete_page = AtdCompletePage()
        # self.screen_manager.add_widget(self.atd_complete_page)

        return self.screen_manager

if __name__ == "__main__":
    my_app = LibraryApp()

    my_app.run()
