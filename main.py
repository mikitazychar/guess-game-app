from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from game_logic import GuessGameLogic

Window.size = (360, 640)


class MenuScreen(Screen):
    pass


class GameScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.game = GuessGameLogic()
        self.current_value = ""

    def on_enter(self):
        self.reset_ui()

    def reset_ui(self, *args):
        self.current_value = ""
        container = self.ids.container
        container.clear_widgets()
        self.ids.info_label.text = "ВЫБЕРИТЕ УРОВЕНЬ"

        container.add_widget(Factory.StyledButton(
            text="ЛЕГКИЙ (1-10)",
            on_press=lambda x: self.start_game(10, 5)))
        container.add_widget(Factory.StyledButton(
            text="СЛОЖНЫЙ (1-100)",
            on_press=lambda x: self.start_game(100, 7)))
        container.add_widget(Factory.StyledButton(
            text="В МЕНЮ",
            on_press=lambda x: setattr(self.manager, 'current', 'menu')))

    def start_game(self, max_range, attempts):
        self.diff_name = "Hard" if max_range > 10 else "Easy"
        msg = self.game.start_new_game(max_range, attempts)
        container = self.ids.container
        container.clear_widgets()
        self.ids.info_label.text = msg

        self.display = Factory.DisplayLabel(text="?")
        container.add_widget(self.display)

        kb = GridLayout(cols=3, spacing=5, size_hint_y=1.5)
        for i in list(range(1, 10)) + ['C', 0, '⌫']:
            kb.add_widget(Factory.Key(text=str(i), on_press=self.handle_key))
        container.add_widget(kb)
        container.add_widget(Factory.StyledButton(
            text="ПРОВЕРИТЬ",
            on_press=self.check_input))

    def handle_key(self, instance):
        key = instance.text
        if key == "C": self.current_value = ""
        elif key == "⌫": self.current_value = self.current_value[:-1]
        elif len(self.current_value) < 3: self.current_value += key
        self.display.text = self.current_value if self.current_value else "?"

    def check_input(self, instance):
        if not self.current_value: return
        status, result = self.game.check_guess(int(self.current_value))
        if status in ["win", "lose"]:
            if status == "win": self.game.save_score(result, self.diff_name)
            self.ids.info_label.text = f"ОЧКИ: {result}" if status == "win" else result
            self.ids.container.clear_widgets()
            self.ids.container.add_widget(Factory.StyledButton(
                text="ИГРАТЬ СНОВА",
                on_press=self.reset_ui))
        else:
            self.ids.info_label.text = result
            self.current_value = ""
            self.display.text = "?"


class ScoresScreen(Screen):
    def update_table(self):
        self.manager.current = 'scores'
        container = self.ids.scores_container
        container.clear_widgets()

        logic = GuessGameLogic()
        data = logic.get_top_scores()
        res_text = "[b][size=24sp]TOP 5[/size][/b]\n\n"
        for date, score, diff in data:
            res_text += f"{date} | {diff} | [color=1ed7ff]{score}[/color]\n"

        self.ids.score_label.text = res_text
        container.add_widget(self.ids.score_label)
        container.add_widget(Factory.StyledButton(
            text="НАЗАД",
            on_press=lambda x: setattr(self.manager, 'current', 'menu')))


class GuessApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.3))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(ScoresScreen(name='scores'))
        return sm


if __name__ == "__main__":
    GuessApp().run()
