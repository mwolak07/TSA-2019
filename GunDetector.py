from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.settings import SettingsWithSidebar

from settings_json import settings_json 


# Declare both screens
class StartMenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class ScreenManager(ScreenManager):
    pass

class GunDetector(App):
    def build(self):
        self.settings_cls = SettingsWithSidebar
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

if __name__ == '__main__':
    GunDetector().run()