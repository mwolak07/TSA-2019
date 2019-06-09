from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen


# Declare both screens
class StartMenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class ScreenManager(ScreenManager):
    pass

class GunDetector(App):
    pass

if __name__ == '__main__':
    GunDetector().run()