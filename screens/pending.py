from kivy.uix.screenmanager import Screen
from utils.pending.create_new_task import create_new_task
from utils.pending.mark_as_completed import mark_as_completed
from utils.pending.next import next

class pendingScreen(Screen):
    def go_to_tasks(self):
        print('Navigating from pending to tasks')
        self.manager.current = 'tasks'
    def go_to_pending(self):
        print('Navigating from pending to pending')
        self.manager.current = 'pending'
    def on_enter(self):
        print('pending screen has fully loaded')
    create_new_task = staticmethod(create_new_task)
    mark_as_completed = staticmethod(mark_as_completed)
    next = staticmethod(next)