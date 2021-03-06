from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture

from settings_json import settings_json

from sightengine.client import SightengineClient
from twilio.rest import Client
from email.mime.multipart import MIMEMultipart

from email.mime.text import MIMEText
import threading
from PIL import Image as PILImage
from kivy.base import EventLoop
import cv2
import smtplib
import time


class StartMenuScreen(Screen):
    # Closes the window
    def exit(self):
        EventLoop.close()

# Class for handling all of the display elements of the detector
class DetectorScreen(Screen):

    # Start the detector before the screen is displayed
    def on_pre_enter(self, *args):
        self.ids.detector.initDetector(self)
        return self

    # Updates detection label at specified time interval
    def labelCallback(self, dt):
        if self.ids.detector.detected:
            self.ids.output.text = "Weapon detected! Take action now!"
        else:
            self.ids.output.text = ""

    # Safely stops the video stream, closes threads, and goes to the start menu
    def goBack(self):
        if self.ids.detector.capture is not None:
            self.ids.detector.capture.release()
            self.ids.detector.analysisThead.join()
        app.root.current = 'start'

    # Safely stops the video stream, closes threads, and closes window
    def exit(self):
        if self.ids.detector.capture is not None:
            self.ids.detector.capture.release()
            self.ids.detector.analysisThead.join()
        self.ids.detector.server.quit()

        EventLoop.close()


class Detector(Image):

    def initDetector(self, DetectorScreen, **kwargs):
        # Used to safely modify the variables used by multiple threads
        self.data_lock = threading.Lock()
        # Reinitialize credentials in case of updated parameters
        self.initCreds()
        self.start_detector(DetectorScreen)

    def initCreds(self):
        # Read in Sightengine credentials
        credentials = open("sight_engine_KEY.txt", "r")
        api_user = credentials.readline()
        api_secret = credentials.readline()
        credentials.close()

        # Instantiate Sightengine client with credentials
        self.client = SightengineClient(api_user, api_secret)

        # Read in credentials for messenger email
        credentials = open("email_credentials.txt", "r")

        # Instantiate message object
        self.msg = MIMEMultipart()

        # Set up the parameters of the message
        self.msg['From'] = credentials.readline()
        self.msg['Subject'] = "Gun Detected! ACT IMMEDIATELY!"
        self.emailcontacts = app.emails.split(', ')

        # Get information for logging into email account
        password = credentials.readline()
        credentials.close()

        # Body of text and email Alerts
        message = "Gun Detected! ACT IMMEDIATELY!"

        # Add in the message body
        self.msg.attach(MIMEText(message, 'plain'))

        # Create server to send email
        self.server = smtplib.SMTP('smtp.gmail.com: 587')
        print('server started')
        self.server.starttls()

        # Login to the messenger account with proper credentials
        self.server.login(self.msg['From'], password)

        # Read in twilio credentials
        credentials = open("twilio_credentials.txt", "r")
        account_sid = credentials.readline()
        auth_token = credentials.readline()
        self.detectorNumber = credentials.readline()
        credentials.close()

        # Instantiate Twilio object
        self.twilioClient = Client(account_sid, auth_token)
        self.phoneNumbers = app.numbers.split(', ')

    # Start initial frame analysis and schedule callbacks
    def start_detector(self, DetectorScreen, **kwargs):

        # Used to manage thread safety and update labels
        self.detected = False
        self.requestComplete = False

        if app.source == 'Live Feed':
            # Use webcam as main video stream
            self.capture = cv2.VideoCapture(0)
        else:
            self.capture = cv2.VideoCapture(app.path)  # Use local file

        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = cv2.__version__.split('.')

        # Determine video stream fps
        if int(major_ver) < 3:
            fps = self.capture.get(cv2.cv.CV_CAP_PROP_FPS)
            print("Framerate: %s" % (fps))
        else:
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            print("Framerate: %s" % (fps))

        # Convert initial frame to PILImage
        newFrame = PILImage.fromarray(self.capture.read()[1])

        # Start analysis on the first frame
        self.analysisThead = threading.Thread(
            target=self.analyzeFrame, kwargs={
                'inputFrame': newFrame})
        self.analysisThead.start()

        callbackInteval = 1.0 / fps    # Callbacks should be scheduled to run every frame

        # Creates callback for displaying and analyzing new frames
        Clock.schedule_interval(self.update, 1.0 / fps)

        # Creates callback to update the detection label
        Clock.schedule_interval(DetectorScreen.labelCallback, 1.0 / fps)

    # Called every frame to update the display and run the analysis
    def update(self, dt):

        # Grabs status (ret) and frame (frame) from video capture
        ret, frame = self.capture.read()

        # Frame successfully grabbed
        if ret:

            # Frame is recolored to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Old thread has completed its job
            if self.requestComplete:

                # Old thread is shut down
                self.analysisThead.join()

                # Current frame is copied to a PILImage
                newFrame = PILImage.fromarray(frame)

                # Start new frame analysis
                self.analysisThead = threading.Thread(
                    target=self.analyzeFrame, kwargs={
                        'inputFrame': newFrame})
                self.analysisThead.start()

            # Scale up image to be displayed
            frame = cv2.resize(frame,
                               (int(frame.shape[1] * 1.65),
                                int(frame.shape[0] * 1.65)),
                               interpolation=cv2.INTER_AREA)

            # Frame is buffered and converted to a string
            buf = cv2.flip(frame, -1).tostring()

            # Create texture to display image
            imageTexture = Texture.create(
                size=(
                    frame.shape[1],
                    frame.shape[0]),
                colorfmt='rgb')

            # Texture is filled from buffer with blit_buffer
            imageTexture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

            # Displaying image from the texture
            self.texture = imageTexture

    # Check if a weapon was detected
    def analyzeFrame(self, inputFrame, **kwargs):

        # Safely modify the variable
        with self.data_lock:
            # Marks current thread as active, another one should not be created
            self.requestComplete = False

        # Check for a gun only if has not been previously detected
        if not self.detected:

            # Stores frame in a temporary file in order to send the API request
            inputFrame.save("Image.jpg")

            # API request with timing
            start = time.process_time()
            output = self.client.check('wad').set_file("Image.jpg")
            end = time.process_time()
            print("output received in %s seconds" % (end - start))
            print(output)

            # Checks to make sure API request didn't fail
            if output['status'] != 'failure':

                # Checks to see if a weapon was detected
                if output['weapon'] > 0.1:
                    print("detected")

                    # Marks that a gun was detected
                    with self.data_lock:
                        self.detected = True

                    self.notifyAuthorities()  # Alert authorities

        # Marks thread as finished, another can be started
        with self.data_lock:
            self.requestComplete = True

    # Sends email and text messages
    def notifyAuthorities(self):

        for number in self.phoneNumbers:
            # Twilio text messages sent
            self.twilioClient.messages \
                .create(
                    body="Gun Detected! ACT IMMEDIATELY!",
                    from_=self.detectorNumber,
                    to=number
                )

            # Optional phone calls
            # self.twilioClient.calls.create(
            #             url='http://demo.twilio.com/docs/voice.xml',
            #             from_=self.detectorNumber,
            #             to=number
            # )

        # Email messages sent via the server
        for email in self.emailcontacts:
            self.server.sendmail(self.msg['From'], email, self.msg.as_string())
            print("successfully sent email to %s:" % email)


class ScreenManager(ScreenManager):
    pass


class GunDetector(App):
    def build(self):
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False

        self.source = self.config.get('App Settings', 'source')
        self.path = self.config.get('App Settings', 'path')
        self.emails = self.config.get('App Settings', 'emails')
        self.numbers = self.config.get('App Settings', 'numbers')

        return super().build()

    def build_config(self, config):
        config.setdefaults('App Settings', {
            'source': 'Pre-Recorded',
            'path': 'C:/Users/mwola/Desktop/Files/Coding/TSA-2019/storerobberytest.mp4',
            'emails': 'kaushikpprakash@gmail.com, mwolak07@gmail.com',
            'numbers': '7327725794, 8482188011'
        })

    def build_settings(self, settings):
        settings.add_json_panel('App Settings',
                                self.config,
                                data=settings_json)

    def on_config_change(self, config, section, key, value):
        if key == 'source':
            print("changed source", value)
            self.source = value
        elif key == 'path':
            print("changed path", value)
            self.path = value
        elif key == 'emails':
            print("changed emails", value)
            self.emails = value
        elif key == 'numbers':
            print("changed numbers", value)
            self.numbers = value


if __name__ == '__main__':
    Window.fullscreen = 'auto'
    app = GunDetector()
    app.run()
