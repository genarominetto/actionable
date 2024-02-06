from kivy.config import Config
Config.set('graphics', 'rotation', '0')

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
import sqlite3

# Load KV files
Builder.load_file('kv/tasks.kv')
Builder.load_file('kv/steps.kv')
Builder.load_file('kv/pending.kv')

from screens.tasks import tasksScreen
from screens.steps import stepsScreen
from screens.pending import pendingScreen

class MainApp(App):

    def get_last_action(self):
        db_path = "tasks.db"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ACTION FROM HISTORY ORDER BY ID DESC LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result else None

    def build(self):
        sm = ScreenManager(transition=NoTransition())
        tasks_screen = tasksScreen(name='tasks')
        steps_screen = stepsScreen(name='steps')
        pending_screen = pendingScreen(name='pending')

        sm.add_widget(tasks_screen)
        sm.add_widget(steps_screen)
        sm.add_widget(pending_screen)

        last_action = self.get_last_action()
        if last_action in ["Started"]:
            sm.current = 'steps'
        else:
            sm.current = 'tasks'

        return sm

if __name__ == '__main__':
    MainApp().run()

