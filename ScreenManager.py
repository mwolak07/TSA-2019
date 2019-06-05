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

        self.orientation = "vertical"

        # Initialize Next Page Button
        self.next_button = Button(text = "Move to the next page", size_hint = (0.8, 1.0))
        self.next_button.bind(on_press = self.move_page)
        self.add_widget(self.next_button)

    # The two parameters are required
    def move_page(self, instance):
        detector.screen_manager.current = "NewPage" # Bring the New Page to the forefront using screen manager

class NewPage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.orientation = "vertical"
        
        self.message = Label(text="You made it to new page")
        self.add_widget(self.message)

        self.back_button = Button(text = "Go back", size_hint=(0.8, 1.0))
        self.back_button.bind(on_press = self.go_back)
        self.add_widget(self.back_button)
    
    def go_back(self, instance):
        detector.screen_manager.current = "StartMenu"




class GunDetector(App):
    def build(self):
        self.screen_manager = ScreenManager()
        
        # Create start menu and add it to the screen manager
        self.start_menu = StartMenu()
        screen = Screen(name="StartMenu")   # NOTE: For convenience give the screen the same name as the class
        screen.add_widget(self.start_menu)
        self.screen_manager.add_widget(screen)

        # Create new page and add it to the screen manager
        self.new_page = NewPage()
        screen = Screen(name="NewPage")
        screen.add_widget(self.new_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager


if __name__ == "__main__":
    # Allows us to reference the instance of the app; needed for screen manager
    detector = GunDetector()
    detector.run()