from kivy.uix.screenmanager import Screen
from utils.tasks.t1 import t1
from utils.tasks.t2 import t2
from utils.tasks.t3 import t3
from utils.tasks.t4 import t4
from utils.tasks.t5 import t5
from utils.tasks.change_place import change_place
from utils.tasks.refresh import refresh
from utils.tasks.start import start
from utils.tasks.select_zipf_tasks import select_zipf_tasks

class tasksScreen(Screen):
    def go_to_steps(self):
        print('Navigating from tasks to steps')
        self.manager.current = 'steps'
    def on_enter(self):
        print('tasks screen has fully loaded')
    t1 = staticmethod(t1)
    t2 = staticmethod(t2)
    t3 = staticmethod(t3)
    t4 = staticmethod(t4)
    t5 = staticmethod(t5)
    change_place = staticmethod(change_place)

    def refresh(self):
        task_list = select_zipf_tasks()
        for index, task in enumerate(task_list):
            button_id = f"t{index + 1}"
            button = self.ids[button_id]
            button.text = task['text']

    start = staticmethod(start)