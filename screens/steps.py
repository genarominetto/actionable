from kivy.uix.screenmanager import Screen

class stepsScreen(Screen):
    def go_to_tasks(self):
        print('Navigating from steps to tasks')
        self.manager.current = 'tasks'

    def on_enter(self):
        print('steps screen has fully loaded')

    def pause_or_resume(self):
        pass

    def cancel(self):
        pass

    def next_step(self):
        pass