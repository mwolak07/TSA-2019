from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.image import Image
from settings_json import settings_json 
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from sightengine.client import SightengineClient
from twilio.rest import Client
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from kivy.core.window import Window
from threading import Thread
from PIL import Image as PILImage
from kivy.base import EventLoop
import cv2
import smtplib
import time


# Read in sightengine credentials
credentials = open("sight_engine_KEY.txt", "r")
api_user = credentials.readline()
api_secret = credentials.readline()
credentials.close()

# Create a new sightengine client with credentials
client = SightengineClient(api_user, api_secret)

# Create new instance of a message object
msg = MIMEMultipart()

# Body of Text and Email Alerts
message = "Gun Detected! ACT IMMEDIATELY!"

# Reads email account credentials
credentials = open("email_credentials.txt", "r")

# setup the parameters of the message
msg['From'] = credentials.readline()
password = credentials.readline()
credentials.close()
msg['To'] = "kaushikpprakash@gmail.com"
msg['Subject'] = "Gun Detected! ACT IMMEDIATELY!"
 
# add in the message body
msg.attach(MIMEText(message, 'plain'))
 
# create server
server = smtplib.SMTP('smtp.gmail.com: 587')
 
server.starttls()
 
# Login Credentials for sending the mail
server.login(msg['From'], password)

# Read in twilio credentials
credentials = open("twilio_credentials.txt", "r")


account_sid = credentials.readline()
auth_token = credentials.readline()
credentials.close()
twilioClient = Client(account_sid, auth_token)

# Global variables for marking detection and timing threads
detected = False
request_complete = True
capture = None
process = None

def analyzeFrame(inputFrame):
    # Adding required global variables
    global detected
    global request_complete
    # Marks current thread as active, to not initialize another one
    request_complete = False

    # Only requests from API/ sends messages if gun hasn't been detected
    if not detected:
        # Stores frame in temporary file
        inputFrame.save("Image.jpg")
        print("file saved")

        # API request with timing
        start = time.process_time()
        output = client.check('wad').set_file("Image.jpg")
        end = time.process_time()
        print("output received in %s seconds" % (end - start))
        print(output)

        # Checks to make sure API request didn't fail
        if output['status'] != 'failure':
            # Checks to see if weapon was detected
            if output['weapon'] > 0.1:
                print("detected")

                # Twilio text messages sent
                message = twilioClient.messages \
                    .create(
                    body="Gun Detected! ACT IMMEDIATELY!",
                    from_='+18482334348',
                    to='+17327725794'
                )
                message = twilioClient.messages \
                    .create(
                    body="Gun Detected! ACT IMMEDIATELY!",
                    from_='+18482334348',
                    to='+18482188011'
                )

                # Email messages sent via the server.
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                server.sendmail(msg['From'], "mwolak07@gmail.com", msg.as_string())
                server.quit()
                print("successfully sent email to %s:" % (msg['To']))

                # Marks gun as detected in global variable
                detected = True
                print(message.sid)

    # Marks thread as finished, another can be started
    request_complete = True

# Declare both screens
class StartMenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class Detector(Image):

    # Constructor taking cv2 capture, process (thread), and framerate
    def __init__(self, **kwargs):
        super(Detector, self).__init__(**kwargs)
        self.capture = None
        self.process = None


    def start_detector(self, capture, process, fps=30, **kwargs):
        self.capture = capture
        self.process = process
        
        # Creates callback for grabbing and displaying frame
        Clock.schedule_interval(self.update, 1.0 / fps)

    # Callback for camera, grabs and displays frame along with starting threaded analysis
    def update(self, dt):
        # Required for timing thread creation
        global request_complete

        # Grabs status (ret) and frame (frame) from video capture
        ret, frame = self.capture.read()

        # Frame successfully grabbed
        if ret:
            # Frame is recolored to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Thread is not active, new one is started
            if request_complete:
                # Old thread is shut down
                self.process.join()
                # Frame is copied to a PILImage, and threaded frame analysis is started
                newFrame = PILImage.fromarray(frame)
                self.process = Thread(target=analyzeFrame, kwargs={'inputFrame': newFrame})
                self.process.start()

            # Frame is buffered and converted to a kivy texture
            buf = cv2.flip(frame, 0).tostring()
            # Texture defined
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            # Texture filled form buffer with blit_buffer
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            # Displaying image from the texture
            self.texture = image_texture

class DetectorScreen(Screen):
    def init_detector(self):
        global capture
        global process
        
        capture = cv2.VideoCapture(0)
       
        # Initial copy of frame to PILImage to start analysis
        newFrame = PILImage.fromarray(capture.read()[1])
        
        # Starts frame analysis on seperate thread
        process = Thread(target=analyzeFrame, kwargs={'inputFrame': newFrame})
        process.start()

        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = cv2.__version__.split('.')

        # Detecting fps from the video stream
        if int(major_ver) < 3:
            fps = capture.get(cv2.cv.CV_CAP_PROP_FPS)
            print("Framerate: %s" % (fps))
        else:
            fps = capture.get(cv2.CAP_PROP_FPS)
            print("Framerate: %s" % (fps))

        self.ids.detector.start_detector(capture=capture, process=process, fps=fps)
        
        # Dynamic callback (at same rate as video fps) scheduled with Clock to display label for result
        Clock.schedule_interval(self.labelCallback, 1.0/fps)

    def exit(self):
        global capture
        global process
        if capture != None:
            capture.release()
            process.join()
            capture = None
        EventLoop.close()
    
    def on_pre_enter(self, *args):
        self.init_detector()
        return self
    
    # Refreshes label at specified time interval, checking for change in detection boolean
    def labelCallback(self, dt):
        if detected:
            self.ids.output.text = "Weapon detected! Call the proper authorities!"
        else:
            self.ids.output.text = ""

class ScreenManager(ScreenManager):
    pass

class GunDetector(App):
    def build(self):
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        return super().build()
    
    def build_config(self, config):
        config.setdefaults('Video Settings', {
            'source': 'Pre-Recorded'
        })
        return super().build_config(config)
 
    def build_settings(self, settings):
        settings.add_json_panel('Panel Name',
                                self.config,
                                data=settings_json)

        return super().build_settings(settings)
    
    def on_config_change(self, config, section, key, value):
        print(self, config, section, key, value)

if __name__ == '__main__':
    GunDetector().run()