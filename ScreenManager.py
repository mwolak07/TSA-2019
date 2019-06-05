import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen

kivy.require("1.10.1")

# Starting Screen
class StartMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'

        # Initialize Next Page Button
        self.btn1 = Button(text='Move to Next Page', size_hint=(0.8, 1.0))
        self.btn1.bind(on_press=self.move_page)
        self.add_widget(self.btn1)

    # The two parameters are required
    def move_page(self, instance):
        detector.screen_manager.current = 'NewPage' # Bring the New Page to the forefront using screen manager

class NewPage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.message = Label(text="You made it to new page")
        self.add_widget(self.message)


class GunDetector(App):
    def build(self):
        self.screen_manager = ScreenManager()
        
        # Create start menu and add it to the screen manager
        self.start_menu = StartMenu()
        screen = Screen(name='Start')
        screen.add_widget(self.start_menu)
        self.screen_manager.add_widget(screen)

        # Create new page and add it to the screen manager
        self.new_page = NewPage()
        screen = Screen(name='NewPage')
        screen.add_widget(self.new_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager


if __name__ == "__main__":
    # Allows us to reference the instance of the app; needed for screen manager
    detector = GunDetector()
    detector.run()