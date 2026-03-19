import kivy
from kivy.app import App
from kivy.uix.widget import Widget




class Base(Widget):
        
    pass

class Quizzical(App):
    def build(self):
        return Base()

if __name__ == '__main__':
    Quizzical().run()