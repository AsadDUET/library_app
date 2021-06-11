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
from kivy.core.window import Window
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera
import re
from gpiozero import Button
from signal import pause
import scan_qr as qr

Window.size = (800, 480)
Window.fullscreen=True
######
# OCR
######
import pytesseract
# pytesseract.pytesseract.tesseract_cmd="/usr/bin/tesseract"

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

camera = PiCamera()
camera.resolution = (1024, 1024)
camera.rotation = 90
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(1024, 1024))
rawCapture.truncate()
############
## Finger print
############
from pyfingerprint.pyfingerprint import PyFingerprint
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    print("ok")
    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))

#########
# Globa Variables
#########
btn1 = Button(26)
btn2 = Button(6)
btn3 = Button(13)
btn4 = Button(19)
class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='home_screen'
        self.home_loop=None

    def say_hello():
        print("Hello!")

    def close_app(self):
        my_app.get_running_app().stop()

    def on_enter(self):
        print('Entered '+self.name)
        btn1.when_pressed = self.close_app
        btn2.when_pressed = self.go_enrole_screen
        btn3.when_pressed = self.go_check_screen
        btn4.when_pressed = self.go_exchange_screen
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
        self.i=0
    def clear(self):
        f.clearDatabase()

    def on_enter(self):
        print('Entered '+self.name)
        btn1.when_pressed = self.back
        btn2.when_pressed = self.fidPlus
        btn3.when_pressed = self.fidMinus
        btn4.when_pressed = self.submit
        self.state=0
        self.positionNumber=-1
        self.ids['fID'].text=""
        self.pi_image=None
        self.this_loop=Clock.schedule_interval(self.loop,0)
    def fidPlus(self):
        self.i+=1
        self.ids['fID'].text=f"{self.i}"
    def fidMinus(self):
        self.i-=1
        self.ids['fID'].text=f"{self.i}"
    def on_pre_leave(self):
        Clock.unschedule(self.this_loop)
        print('Leaving '+self.name)
    def back(self):
        my_app.screen_manager.current='home_screen'
    def submit(self):
        print("submitting")
        self.ids['instruction'].text="Submitting"
        rawCapture.truncate(0)
        # camera.capture(rawCapture, format="rgb",use_video_port=True)       
        x=500
        y=400
        self.pi_image = rawCapture.array[x: x+300, y: y+600]
        
        idimg = cv2.cvtColor(self.pi_image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('idimg2.jpg',idimg)
        try:
            text = pytesseract.image_to_string(idimg)
            num=re.findall(r'\d+', text)
            self.ids['stdID'].text=num[0]
        except:
            self.ids['stdID'].text=""

        if(self.ids['fID'].text!="" and self.ids['stdID'].text!=""):
            f.createTemplate()
            self.positionNumber = f.storeTemplate(self.i)
            try:
                con = sqlite3.connect('library_data.db')
                cur = con.cursor()
                cur.execute(f"INSERT INTO users VALUES ('{self.ids['stdName'].text}','{self.ids['fID'].text}','{self.ids['stdID'].text}')")
                con.commit()
                con.close()
                self.ids['instruction'].text="Done"
            except Exception as e:
                print(e," User id already exists. ",)
                self.ids['instruction'].text="DB Error"
            
        else:
            self.ids['instruction'].text="set finger ID and place ID then submit "
        print("submited")
        self.ids['stdName'].text=''
        self.ids['stdID'].text=''
        self.ids['fID'].text=''
        self.state=0
    def loop(self,dt):
        if self.state==0:
            self.ids['instruction'].text="Please Scan Finger"
            if (f.readImage() == True):
                f.readImage()
                f.convertImage(0x01)
                result = f.searchTemplate()
                self.positionNumber = result[0]
                self.state+=1
        if self.state==1:
            if ( self.positionNumber >= 0 ):
                self.ids['instruction'].text=('Template already exists at position #' + str(self.positionNumber))
                if (f.readImage() == False):
                    self.state-=1
            else:
                self.ids['instruction'].text=('Remove finger...')
                if (f.readImage() == False):
                    self.state+=1
        if self.state==2:
            self.ids['instruction'].text=('Waiting for same finger again...')
            if ( f.readImage() == True ):
                f.readImage()
                f.convertImage(0x02)
                self.state+=1
        if self.state==3:
            if ( f.compareCharacteristics() == 0 ):
                self.ids['instruction'].text=('Fingers do not match')
                if (f.readImage() == False):
                    self.state=0
            else:
                self.ids['instruction'].text=('Finger matched')
                if (f.readImage() == False):
                    self.state+=1
        if self.state==4:
            rawCapture.truncate(0)
            camera.capture(rawCapture, format="rgb",use_video_port=True)
            x=500
            y=400
            self.pi_image = rawCapture.array[x: x+300, y: y+600]
            self.pi_image = cv2.rotate(self.pi_image, cv2.ROTATE_180)
            self.pi_image = cv2.flip(self.pi_image, 1)
            buf=self.pi_image.tostring()
            image_texture= Texture.create(size=(self.pi_image.shape[1],self.pi_image.shape[0]),colorfmt='rgb')
            image_texture.blit_buffer(buf,colorfmt='rgb',bufferfmt='ubyte')
            self.ids['preview'].texture =image_texture
            rawCapture.truncate(0)

class ExchangeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='exchange_screen'
        self.state=0
        
    def scan_book(self):
        self.ids['instruction'].text="Scaning Book"
        ret, frame = self.cap.read()
        cv2.imwrite('image.png',frame)
        #frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        book_id=qr.scan(frame)
        if book_id:
            print(book_id)
            self.ids['bookID'].text=str(book_id)
    def scan_id(self):
        self.ids['instruction'].text="Scaning ID"
        rawCapture.truncate(0)
        # camera.capture(rawCapture, format="rgb",use_video_port=True)       
        x=500
        y=400
        self.pi_image = rawCapture.array[x: x+300, y: y+600]
        
        idimg = cv2.cvtColor(self.pi_image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('idimg2.jpg',idimg)
        try:
            text = pytesseract.image_to_string(idimg)
            num=re.findall(r'\d+', text)
            self.ids['stdID'].text=num[0]
        except:
            pass
    def on_enter(self):
        print('Entered '+self.name)
        btn1.when_pressed = self.back
        btn2.when_pressed = self.scan_id
        btn3.when_pressed = self.scan_book
        btn4.when_pressed = self.submit
        self.state=0
        self.positionNumber=-1
        self.ids['fID'].text=""
        self.ids['stdID'].text=""
        self.ids['bookID'].text=""
        self.pi_image=None
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
    def submit(self):
        con = sqlite3.connect('library_data.db')
        cur = con.cursor()
        try:
            cur.execute(f"INSERT INTO exchange VALUES ('{self.ids['bookID'].text}','{self.ids['stdID'].text}',1)")
        except Exception as e:
            print(e, "Multiple copy not allowed")

            ##UPDATE exchange
            try:
                cur.execute(f"UPDATE exchange SET status=0 WHERE book_id={self.ids['bookID'].text} AND std_id={self.ids['stdID'].text}")
            except Exception as e:
                print(e)
                cur.execute(f"DELETE FROM  exchange  WHERE book_id={self.ids['bookID'].text} AND std_id={self.ids['stdID'].text} AND status=1")
        con.commit()
        con.close()
        self.ids['bookID'].text=''
        self.ids['stdID'].text=''
        self.ids['fID'].text=''
        self.state=0
    
    def loop(self,dt):
        if self.state==0:
            self.ids['instruction'].text="Please Scan Finger"
            if (f.readImage() == True):
                f.readImage()
                f.convertImage(0x01)
                result = f.searchTemplate()
                self.positionNumber = result[0]
                self.state+=1
        if self.state==1:
            if ( self.positionNumber >= 0 ):
                self.ids['instruction'].text=('Match found at ID #' + str(self.positionNumber))
                self.ids['fID'].text=str(self.positionNumber)
                if (f.readImage() == False):
                    self.state+=1
            else:
                self.ids['instruction'].text=('No Match. Remove finger...')
                if (f.readImage() == False):
                    self.state=0
        
        if self.state==2:
            rawCapture.truncate(0)
            camera.capture(rawCapture, format="rgb",use_video_port=True)
            x=500
            y=400
            self.pi_image = rawCapture.array[x: x+300, y: y+600]
            self.pi_image = cv2.rotate(self.pi_image, cv2.ROTATE_180)
            self.pi_image = cv2.flip(self.pi_image, 1)
            buf=self.pi_image.tostring()
            image_texture= Texture.create(size=(self.pi_image.shape[1],self.pi_image.shape[0]),colorfmt='rgb')
            image_texture.blit_buffer(buf,colorfmt='rgb',bufferfmt='ubyte')
            self.ids['preview2'].texture =image_texture
        ####################
            ret, frame = self.cap.read()
            # cv2.imwrite('image.png',frame)
            # #frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            # book_id=qr.scan(frame)
            # if book_id:
            #     print(book_id)
        ##################
        #############
            frame = cv2.flip(frame,-1)
            buf=frame.tobytes()
            image_texture2= Texture.create(size=(frame.shape[1],frame.shape[0]),colorfmt='rgb')
            image_texture2.blit_buffer(buf,colorfmt='rgb',bufferfmt='ubyte')
            self.ids['preview'].texture =image_texture2
        #############

class BookListScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='book_list_screen'
        
    def on_enter(self):
        print('Entered '+self.name)
        btn1.when_pressed = self.back
        btn2.when_pressed = None
        btn3.when_pressed = None
        btn4.when_pressed = None
        con = sqlite3.connect('library_data.db')
        cur = con.cursor()
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
            # if(len(row_datas)>0):
            self.data_table = MDDataTable(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                    size_hint=(0.9, 0.9),
                                    #  check=True,
                                    rows_num=max(len(row_datas),1),
                                    column_data=[
                                        ("No.", dp(15)),
                                        ("Name", dp(50)),
                                        ("Book ID", dp(20)),
                                        ("Borrowed", dp(20)),
                                        ("Available", dp(20)),
                                        ("Total", dp(20))
                                    ],
                                    row_data=row_datas
                                    )
            self.ids["bookTable"].add_widget(self.data_table)
            self.data_table.bind(on_row_press=self.call_back)
        except Exception as e:
            print(e, "Table or data Not Found")
        con.close()
    def call_back(self,a,b):
        self.back()
    def back(self):
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
        print('Entered '+self.name)
        btn1.when_pressed = self.back
        btn2.when_pressed = None
        btn3.when_pressed = None
        btn4.when_pressed = None
        con = sqlite3.connect('library_data.db')
        cur = con.cursor()
        self.this_loop=Clock.schedule_interval(self.loop,0)
        try:
            user_ids=[]
            borrowed=[]
            row_datas=[]
            for row in cur.execute('SELECT * FROM users ' ):
                user_ids.append(row[2])
            print(user_ids)
            for id in user_ids:
                borrowed.append(cur.execute(f'SELECT COUNT(*) FROM exchange WHERE std_id={id} AND status=1').fetchall()[0][0])
            print(borrowed)
            print("Name","ID", "Borrowed")
            for n, row in enumerate(cur.execute('SELECT * FROM users ')):
                row_datas.append((n+1,row[0],row[2],row[1], borrowed[n]))
                print(n+1,row[0],row[1], borrowed[n])
            print(row_datas)
            # if(len(row_datas)>0):
            self.data_table = MDDataTable(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                    size_hint=(0.9, 0.9),
                                    #  check=True,
                                    rows_num=max(len(row_datas),1),
                                    column_data=[
                                        ("No.", dp(15)),
                                        ("Name", dp(50)),
                                        ("StdID", dp(20)),
                                        ("FingerID", dp(20)),
                                        ("Borrowed", dp(20))
                                    ],
                                    row_data=row_datas
                                    )
            self.ids["bookTable"].add_widget(self.data_table)
            self.data_table.bind(on_row_press=self.call_back)
        except Exception as e:
            print(e, "Table or data Not Found")
        con.close()  
    def call_back(self,a,b):
        self.back()
    def back(self):
        my_app.screen_manager.current='list_select_screen'
    def on_pre_leave(self):
        Clock.unschedule(self.this_loop)
        self.ids["bookTable"].remove_widget(self.data_table)
        print('Leaving '+self.name)
    
    def loop(self,dt):
        pass
        # sleep(5)
        # self.back()

class ExchangeListScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='exchange_list_screen'
        
    def on_enter(self):
        print('Entered '+self.name)
        print('Entered '+self.name)
        btn1.when_pressed = self.back
        btn2.when_pressed = None
        btn3.when_pressed = None
        btn4.when_pressed = None
        con = sqlite3.connect('library_data.db')
        cur = con.cursor()
        self.this_loop=Clock.schedule_interval(self.loop,0)
        try:
            # book_ids=[]
            # borrowed=[]
            row_datas=[]
            # for row in cur.execute('SELECT * FROM books ' ):
            #     book_ids.append(row[1])
            # print(book_ids)
            # for id in book_ids:
            #     borrowed.append(cur.execute(f'SELECT COUNT(*) FROM exchange WHERE book_id={id} AND status=1').fetchall()[0][0])
            # print(borrowed)
            print("Book ID","Std.ID", "Status")
            for n, row in enumerate(cur.execute('SELECT * FROM exchange ')):
                row_datas.append((n+1,row[0],row[1], row[2]))
                print(n+1,row[0],row[1], row[2])
            print(row_datas)
            # if(len(row_datas)>0):
            self.data_table = MDDataTable(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                    size_hint=(0.9, 0.9),
                                    #  check=True,
                                    rows_num=max(len(row_datas),1),
                                    column_data=[
                                        ("No.", dp(15)),
                                        ("Book ID", dp(50)),
                                        ("Std.ID", dp(20)),
                                        ("Status", dp(20))
                                    ],
                                    row_data=row_datas
                                    )
            self.ids["bookTable"].add_widget(self.data_table)
            self.data_table.bind(on_row_press=self.call_back)
        except Exception as e:
            print(e, "Table or data Not Found")
        con.close()  
    def call_back(self,a,b):
        self.back()
    def back(self):
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
        btn1.when_pressed = self.back
        btn2.when_pressed = self.go_book_screen
        btn3.when_pressed = self.go_student_screen
        btn4.when_pressed = self.go_exchange_list_screen
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
    def go_exchange_list_screen(self):
        my_app.screen_manager.current='exchange_list_screen'
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

        self.exchange_select_screen = ExchangeListScreen()
        self.screen_manager.add_widget(self.exchange_select_screen)


        # self.atd_complete_page = AtdCompletePage()
        # self.screen_manager.add_widget(self.atd_complete_page)

        return self.screen_manager

if __name__ == "__main__":
    my_app = LibraryApp()

    my_app.run()
