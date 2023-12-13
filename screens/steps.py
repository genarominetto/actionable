from kivy.uix.screenmanager import Screen
from utils.steps.pause import pause
from utils.steps.cancel import cancel
from utils.steps.next_step import next_step

class stepsScreen(Screen):
    def go_to_tasks(self):
        print('Navigating from steps to tasks')
        self.manager.current = 'tasks'
    def on_enter(self):
        print('steps screen has fully loaded')
    pause = staticmethod(pause)
    cancel = staticmethod(cancel)
    next_step = staticmethod(next_step)