from kivy.uix.screenmanager import Screen
from utils.habits.create_new_habit import create_new_habit
from utils.habits.break_habit import break_habit
from utils.habits.keep import keep

class habitsScreen(Screen):
    def go_to_tasks(self):
        print('Navigating from habits to tasks')
        self.manager.current = 'tasks'
    def go_to_todos(self):
        print('Navigating from habits to todos')
        self.manager.current = 'todos'
    def go_to_habits(self):
        print('Navigating from habits to habits')
        self.manager.current = 'habits'
    def on_enter(self):
        print('habits screen has fully loaded')
    create_new_habit = staticmethod(create_new_habit)
    break_habit = staticmethod(break_habit)
    keep = staticmethod(keep)