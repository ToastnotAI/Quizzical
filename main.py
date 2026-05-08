import kivy
import random
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window




class StartScreen(Screen):
    def on_enter(self, *args):
        # Reset scores when returning to the start screen
        self.manager.scores = []
        # Rebuild quiz buttons so all quizzes are enabled again.
        try:
            quiz_select = self.manager.get_screen("quiz_select")
            quiz_select.reset_quiz_buttons()
        except:
            pass
        

    pass

class QuizSelectButton(Button):
    disabled = BooleanProperty(False)
    
    pass

class QuizSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quiz_options = [
            {"text": "Basic Numbers Quiz", "screen": "basic_numbers"},
            {"text": "Basic Alphabet Quiz", "screen": "basic_alphabet"},
            {"text": "Advanced Maths Quiz", "screen": "advanced_maths"},
            {"text": "Advanced Memory Quiz", "screen": "advanced_memory"},
            # Add more quiz options here as needed
        ]
        self.btns = []

    def on_kv_post(self, *args):
        self.create_quiz_buttons()
    
    def create_quiz_buttons(self):
        if "quiz_button_container" not in self.ids:
            return

        self.ids.quiz_button_container.clear_widgets()
        self.btns = []
        for option in self.quiz_options:
            btn = QuizSelectButton(text=option["text"])
            btn.bind(on_release=lambda btn, option=option: self.select_quiz(option))
            self.ids.quiz_button_container.add_widget(btn)
            self.btns.append(btn)

    def reset_quiz_buttons(self):
        self.create_quiz_buttons()

    def select_quiz(self, option):
        for btn in self.btns:
            if btn.text == option["text"]:
                btn.disabled = True
                btn.background_color = (0.5, 0.5, 0.5, 1)  # Gray out the button
        
        self.manager.current = option["screen"]

    def go_to_results(self, *args):
        self.manager.current = "final_screen"

    # if all buttons are disabled, show a button to go to a results screen
    def on_enter(self, *args):
        if all(btn.disabled for btn in self.btns):
            #remove all buttons from the quiz select screen
            self.ids.quiz_button_container.clear_widgets()

            results_btn = Button(text="View Results", size_hint=(0.5, None), height=56, pos_hint={"center_x": 0.5})
            results_btn.bind(on_release=self.go_to_results)
            self.ids.quiz_button_container.add_widget(results_btn)


class AnswerButton(Button):
    correct = BooleanProperty(False)
    disabled = BooleanProperty(False)

    def on_release(self):
        super().on_release()
        if not self.disabled:
            parent = self.parent

            while parent is not None and not isinstance(parent, Screen):
                parent = parent.parent

            if parent is not None and hasattr(parent, "is_showing_sequence") and parent.is_showing_sequence:
                return

            if parent is not None and hasattr(parent, "stop_timer"):
                if self.correct:
                    parent.correct_answer(self)
                else:
                    parent.incorrect_answer(self)

    pass

    def reset_color(self):
        self.background_color = (1, 1, 1, 1)  # Reset to default white

    def fade_in(self):
        # Fade in the button over 0.5 seconds
        Animation.cancel_all(self, "opacity")
        self.opacity = 0
        anim = Animation(opacity=1, duration=0.5, t="out_quad")
        anim.start(self)

    def fade_out(self):
        # Fade out the button over 0.5 seconds
        Animation.cancel_all(self, "opacity")
        anim = Animation(opacity=0, duration=0.5, t="in_quad")
        anim.start(self)

    class CompletionMessage(Screen):
        
        def on_pre_enter(self, *args):
            # Get the latest score from the manager
            if self.manager.scores:
                quiz_name, score = self.manager.scores[-1]
                self.ids.message_label.text = f"Quiz Completed!\n{quiz_name}\nYour Score: {score}"
                self.ids.scores_label.text = "Previous Scores:\n"
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
        Clock.schedule_once(lambda dt: self.start_timer(), 0.3)  # Start timer after a short delay to ensure screen is fully loaded
        self.sorted_btns = None # This will be set in the specific quiz screen when buttons are populated.

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
        self.elapsed_time = round(self.elapsed_time-10) # Subtract 10 seconds to allow for a perfect score
        #make max score 100 and minimum score 0
        score = max(0, min(100, int(100 - self.elapsed_time)))
        return score

    def get_answer_btns(self):
        buttons = []
        for child in self.walk():
            if isinstance(child, AnswerButton):
                buttons.append(child)
        return buttons


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


    def populate_random_numbers(self):
        # Pick three unique values so buttons are always different.
        self.btns = self.get_answer_btns()
        self.values = random.sample(range(1, 10), len(self.btns))
        for i in range(len(self.btns)):
            self.btns[i].text = str(self.values[i])
        self.sorted_btns = sorted(self.btns, key=lambda b: b.text)
        self.sorted_btns[0].correct = True  # Mark the smallest number as correct


class BasicAlphabetScreen(GenericQuizScreen):

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.populate_random_letters()
        self.quiz = "Basic Alphabet Quiz"

    def populate_random_letters(self):
        self.btns = self.get_answer_btns()
        letters = random.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZ", len(self.btns))
        for i in range(len(self.btns)):
            self.btns[i].text = letters[i]
        self.sorted_btns = sorted(self.btns, key=lambda b: b.text)
        self.sorted_btns[0].correct = True  # Mark the alphabetically first letter as correct

class AdvancedMathsScreen(GenericQuizScreen):
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.populate_random_equations()
        self.quiz = "Advanced Maths Quiz"

    def populate_random_equations(self):
        self.btns = self.get_answer_btns()
        equations = []
        used_results = set()
        while len(equations) < len(self.btns):
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            op = random.choice(["+", "-"])
            if op == "+":
                result = a + b
            elif op == "-":
                result = a - b
                
            # Ensure each equation has a unique numeric result.
            if result not in used_results:
                equations.append((f"{a} {op} {b}", result))
                used_results.add(result)
        
        for i in range(len(self.btns)):
            self.btns[i].text = equations[i][0]
            self.btns[i].result = equations[i][1]  # Store the result for sorting
        
        self.sorted_btns = sorted(self.btns, key=lambda b: b.result)
        self.sorted_btns[0].correct = True  # Mark the equation with the smallest result as correct

    def calculate_score(self):
        # Override to give more points for faster answers in the advanced quiz
        self.elapsed_time = round(self.elapsed_time-10) # Subtract 10 seconds to allow for a perfect score
        score = max(0, min(200, int(200 - self.elapsed_time * 1.5)))  # Scale time penalty for more points
        return score


class AdvancedMemoryScreen(GenericQuizScreen):
    def on_pre_enter(self, *args):
        # Default behaviour is overwritten to allow for showing the buttons
        self.sorted_btns = None # This will be set in the specific quiz screen when buttons are populated.
        self.is_showing_sequence = False
        self._sequence_events = []
        self.reset_timer()
        self.btns = self.get_answer_btns()
        self.populate_random_order()
        self.quiz = "Advanced Memory Quiz"
        for btn in self.btns:
            Animation.cancel_all(btn, "opacity")
            btn.opacity = 0
            btn.disabled = False

        self.set_status_text("Press Start Sequence to begin")

    def cancel_sequence_events(self):
        for event in self._sequence_events:
            event.cancel()
        self._sequence_events = []

    def get_sequence_timing(self):
        step = 0.6
        hide_delay = max(1.2, len(self.full_sequence) * step + 0.6)
        ready_delay = hide_delay + 2
        return step, hide_delay, ready_delay

    def populate_random_order(self):
        # sorted_btns will be the buttons in a random order
        self.sorted_btns = self.btns.copy()
        random.shuffle(self.sorted_btns)
        self.full_sequence = self.sorted_btns.copy()  # Store the full sequence for later reference
        self.sorted_btns[0].correct = True  # Mark the first button in the original order as correct

    def show_sequence(self, dt):
        step, hide_delay, _ = self.get_sequence_timing()

        for i, btn in enumerate(self.full_sequence):
            event = Clock.schedule_once(lambda _dt, b=btn: b.fade_in(), i * step)
            self._sequence_events.append(event)

        for btn in self.full_sequence:
            event = Clock.schedule_once(lambda _dt, b=btn: b.fade_out(), hide_delay)
            self._sequence_events.append(event)

    def start_sequence(self):
        self.cancel_sequence_events()
        self.is_showing_sequence = True
        for btn in self.btns:
            Animation.cancel_all(btn, "opacity")
            btn.correct = False
            btn.opacity = 0
            btn.disabled = False

        if self.sorted_btns:
            self.sorted_btns[0].correct = True

        self.set_status_text("Watch the sequence...")
        self.show_sequence(0)
        _, _, ready_delay = self.get_sequence_timing()
        event = Clock.schedule_once(self.start_quiz, ready_delay)
        self._sequence_events.append(event)

    def set_status_text(self, text):
        label = self.ids.get("message_label")
        if label is not None:
            label.text = text

    def start_quiz(self, *args):
        self.is_showing_sequence = False
        for btn in self.btns:
            Animation.cancel_all(btn, "opacity")
            btn.opacity = 1
            btn.disabled = False
        self.start_timer()
        self.set_status_text("Select the buttons in the order they were shown!")

        
    def standby_screen(self, *args):
        for btn in self.btns:
            btn.opacity = 0
            btn.disabled = True
        # Show a message to the user to prepare for the sequence, then start the sequence after a short delay
        self.set_status_text("Get Ready!")
        Clock.schedule_once(lambda dt: self.show_sequence(0), 2)

    def refresh_sequence(self):
        self.cancel_sequence_events()
        self.stop_timer()
        self.update_timer(10)  # Add 10 seconds penalty for refreshing the sequence
        self.is_showing_sequence = False
        for btn in self.btns:
            Animation.cancel_all(btn, "opacity")
            btn.correct = False
            btn.opacity = 0
            btn.disabled = False

        if self.sorted_btns:
            self.sorted_btns[0].correct = True

        self.set_status_text("Time penalty applied! Watch the sequence again when ready.")

    def enable_buttons(self):
        self.is_showing_sequence = False
        for btn in self.btns:
            btn.disabled = False

    def on_enter(self, *args):
        # Keep buttons hidden until the user starts the sequence.
        self.cancel_sequence_events()
        self.is_showing_sequence = False
        for btn in self.btns:
            Animation.cancel_all(btn, "opacity")
            btn.opacity = 0
            btn.disabled = False
        self.sorted_btns[0].correct = True
        self.set_status_text("Press Start Sequence to begin")

    def on_leave(self, *args):
        self.cancel_sequence_events()
        self.is_showing_sequence = False
        super().on_leave(*args)

    def calculate_score(self):
        # Override to give more points for faster answers in the memory quiz
        self.elapsed_time = round(self.elapsed_time-10) # Subtract 10 seconds to allow for a perfect score
        score = max(0, min(500, int(500 - self.elapsed_time * 5)))  # Scale time penalty for more points
        return score
        

class FinalScreen(Screen):

    def on_pre_enter(self, *args):
        if self.manager.scores:
            self.ids.message_label.text = "All quizzes completed!\nHere are your scores:"
            self.ids.scores_label.text = ""
            for quiz_name, score in self.manager.scores:
                self.ids.scores_label.text += f"{quiz_name}: {score}\n"

            total_score = sum(score for _, score in self.manager.scores)
            self.ids.total_score_label.text = f"Total Score: {total_score}"



class RootManager(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Fade avoids exposing the Window background during screen changes.
        self.transition = FadeTransition(duration=0.1)
        # Keep a light fallback color in case anything is briefly uncovered.
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        self.scores = []

    pass

    



class Quizzical(App):
    def build(self):
        return RootManager()
        

if __name__ == '__main__':
    Quizzical().run()