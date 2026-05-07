import kivy
import random
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock




class StartScreen(Screen):

    pass

class QuizSelectButton(Button):
    disabled = BooleanProperty(False)
    
    pass

class QuizSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quiz_options = [
            {"text": "Basic Numbers Quiz", "screen": "basic_numbers"},
            # Add more quiz options here as needed
        ]
        self.btns = []
        self.create_quiz_buttons()
    
    def create_quiz_buttons(self):
        for option in self.quiz_options:
            btn = QuizSelectButton(text=option["text"])
            btn.bind(on_release=lambda btn, option=option: self.select_quiz(option))
            self.add_widget(btn)
            self.btns.append(btn)

    def select_quiz(self, option):
        for btn in self.btns:
            if btn.text == option["text"]:
                btn.disabled = True
                btn.background_color = (0.5, 0.5, 0.5, 1)  # Gray out the button
        
        self.manager.current = option["screen"]

    
        


class AnswerButton(Button):
    correct = BooleanProperty(False)
    disabled = BooleanProperty(False)

    def on_release(self):
        super().on_release()
        if not self.disabled:
            parent = self.parent

            while parent is not None and not isinstance(parent, Screen):
                parent = parent.parent

            if parent is not None and hasattr(parent, "stop_timer"):
                if self.correct:
                    parent.correct_answer(self)
                else:
                    parent.incorrect_answer(self)

    pass

    def reset_color(self):
        self.background_color = (1, 1, 1, 1)  # Reset to default white

    def fade_out(self):
        # Fade out the button over 0.5 seconds
        anim = kivy.animation.Animation(opacity=0, duration=0.5)
        anim.start(self)

    class CompletionMessage(Screen):
        
        def on_pre_enter(self, *args):
            # Get the latest score from the manager
            if self.manager.scores:
                quiz_name, score = self.manager.scores[-1]
                self.ids.message_label.text = f"Quiz Completed!\n{quiz_name}\nYour Score: {score}"
                for score in self.manager.scores:
                    # create a list of all scores in the format "Quiz Name: Score"
                    self.ids.scores_label.text += f"{score[0]}: {score[1]}\n"
            else:
                self.ids.message_label.text = "Quiz Completed!\nNo score available."


class GenericQuizScreen(Screen):
    quiz = StringProperty("")
    elapsed_time = NumericProperty(0)
    clock_text = StringProperty("0.00")
    _clock_event = None


    def on_pre_enter(self, *args):
        self.reset_timer()
        self.start_timer()

    def on_leave(self, *args):
        self.stop_timer()


    def start_timer(self):
        if self._clock_event is None:
            self._clock_event = Clock.schedule_interval(self.update_timer, 0.01)

    def update_timer(self, dt):
        self.elapsed_time += dt
        self.clock_text = f"{self.elapsed_time:.2f}"

    def stop_timer(self):
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None

    def reset_timer(self):
        self.stop_timer()
        self.elapsed_time = 0
        self.clock_text = "0.00"

    def calculate_score(self):
        # Current Scoring: 100 points minus 1 point for every second elapsed, with a minimum score of 0
        score = max(0, 100 - int(self.elapsed_time))
        return score

    def get_answer_btns(self):
        buttons = []
        for child in self.walk():
            if isinstance(child, AnswerButton):
                buttons.append(child)
        return buttons
    
    def show_completion_message(self, dt):
        score = self.calculate_score()
        # Send the elapsed time to the completion message screen
        self.manager.scores.append([self.quiz, score])
        self.manager.current = "completion_message"
    
        




class BasicNumbersScreen(GenericQuizScreen):

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.populate_random_numbers()
        self.quiz = "Basic Numbers Quiz"

    def correct_answer(self, button):
        button.background_color = (0, 1, 0, 1)  # Green for 0.5 seconds, then fade out and disable
        Clock.schedule_once(lambda dt: button.fade_out(), 0.5)
        # fade out button, then disable
        button.disabled = True
        self.btns.remove(button)
        if not self.btns:
            self.stop_timer()
            # Show a message or transition to the next screen after a short delay
            Clock.schedule_once(self.show_completion_message, 1)

        else:
            self.sorted_btns.remove(button)
            self.sorted_btns[0].correct = True


    def incorrect_answer(self, button):
        self.elapsed_time += 5  # Add 5 seconds penalty
        button.background_color = (1, 0, 0, 1)  # red for 0.5 seconds, then reset to normal
        Clock.schedule_once(lambda dt: button.reset_color(), 0.5)


        
        

    def populate_random_numbers(self):
        # Pick three unique values so buttons are always different.
        self.btns = self.get_answer_btns()
        self.values = random.sample(range(1, 10), len(self.btns))
        for i in range(len(self.btns)):
            self.btns[i].text = str(self.values[i])
        self.sorted_btns = sorted(self.btns, key=lambda b: b.text)
        self.sorted_btns[0].correct = True  # Mark the smallest number as correct

        

    pass




class RootManager(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scores = []

    pass

    



class Quizzical(App):
    def build(self):
        return RootManager()
        

if __name__ == '__main__':
    Quizzical().run()