from kivy.uix.screenmanager import Screen
from utils.tasks.t1 import t1
from utils.tasks.t2 import t2
from utils.tasks.t3 import t3
from utils.tasks.t4 import t4
from utils.tasks.t5 import t5
from utils.tasks.change_place import change_place
from utils.tasks.select_zipf_tasks import select_zipf_tasks

class tasksScreen(Screen):
    def __init__(self, **kwargs):
        super(tasksScreen, self).__init__(**kwargs)
        self.task_id_mapping = {}

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
        # Untoggle any currently toggled buttons
        for i in range(1, 6):  # Assuming you have 5 task buttons (t1 to t5)
            button_id = f"t{i}"
            button = self.ids[button_id]
            button.state = 'normal'  # Set the state to 'normal' to untoggle

        # Load new tasks and update button texts
        task_list = select_zipf_tasks()
        for index, task in enumerate(task_list):
            button_id = f"t{index + 1}"
            button = self.ids[button_id]
            button.text = task['text']
            self.task_id_mapping[button_id] = task['task id']  # Store task id

    def start(self):
        selected_task_id = None
        for button_id, task_id in self.task_id_mapping.items():
            button = self.ids[button_id]
            if button.state == 'down':  # Check if the button is toggled
                selected_task_id = task_id
                break

        if selected_task_id is not None:
            print(f"Starting task with id {selected_task_id}")
            # Add your logic here to handle the selected task
        else:
            print("No task selected")


