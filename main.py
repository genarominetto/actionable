from kivy.config import Config
Config.set('graphics', 'rotation', '0')  # This should be set to 0 for normal orientation
    
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition

# Load KV files
Builder.load_file('kv/tasks.kv')
Builder.load_file('kv/steps.kv')

from screens.tasks import tasksScreen
from screens.steps import stepsScreen

class MainApp(App):

    def build(self):
        sm = ScreenManager(transition=NoTransition())
        tasks_screen = tasksScreen(name='tasks')
        sm.add_widget(tasks_screen)
        steps_screen = stepsScreen(name='steps')
        sm.add_widget(steps_screen)
        sm.current = 'tasks'
        return sm

if __name__ == '__main__':
    MainApp().run()


