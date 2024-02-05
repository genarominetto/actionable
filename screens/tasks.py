import sqlite3
from datetime import datetime
from kivy.uix.screenmanager import Screen
from utils.tasks.select_zipf_tasks import select_zipf_tasks

class tasksScreen(Screen):
    def __init__(self, **kwargs):
        super(tasksScreen, self).__init__(**kwargs)
        self.task_id_mapping = {}

    def on_enter(self):
        print('Tasks screen has fully loaded')
        self.set_current_place()
        self.refresh()

    def set_current_place(self):
        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT NAME FROM PLACES WHERE IS_SELECTED = 1")
            selected_place_row = cursor.fetchone()

            if selected_place_row:
                self.ids.change_place.text = selected_place_row[0]
            else:
                print("No selected place found.")

    def refresh(self):
        with sqlite3.connect('tasks.db') as conn:
            task_list = select_zipf_tasks()
            for index, task in enumerate(task_list):
                button_id = f"t{index + 1}"
                button = self.ids[button_id]
                button.state = 'normal'
                button.text = task['text']
                self.task_id_mapping[button_id] = task['task id']

        self.update_start_button_state()

    def update_start_button_state(self):
        is_any_task_selected = any(self.ids[f"t{i}"].state == 'down' for i in range(1, 6))
        self.ids.start_button.disabled = not is_any_task_selected

    def start(self):
        selected_task_id = None
        selected_task_text = None
        for button_id, task_id in self.task_id_mapping.items():
            button = self.ids[button_id]
            if button.state == 'down':
                selected_task_id = task_id
                selected_task_text = button.text
                break

        if selected_task_id is not None:
            self.add_to_history(selected_task_id, selected_task_text)
            self.update_current_task_in_db(selected_task_text)
            self.go_to_steps()
        else:
            print("No task selected")

    def add_to_history(self, task_id, task_text):
        action = "Started"
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT ID FROM STEPS WHERE TASK_ID = ? AND ORDER_SEQUENCE = 1''', (task_id,))
            step_row = cursor.fetchone()

            if step_row:
                step_id = step_row[0]
                cursor.execute('''INSERT INTO HISTORY (STEP_ID, ACTION, TIME) VALUES (?, ?, ?)''', 
                            (step_id, action, time))


    def update_current_task_in_db(self, task_text):
        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''UPDATE VARIABLES SET VALUE = ? WHERE KEY = 'current_task' ''', (task_text,))

    def change_place(self):
        with sqlite3.connect('tasks.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ID, NAME FROM PLACES WHERE IS_SELECTED = 1")
            current_place = cursor.fetchone()

            if current_place:
                current_place_id, _ = current_place
                cursor.execute("UPDATE PLACES SET IS_SELECTED = 0 WHERE ID = ?", (current_place_id,))
                cursor.execute("SELECT ID, NAME FROM PLACES WHERE ID > ? ORDER BY ID ASC LIMIT 1", 
                               (current_place_id,))
                next_place = cursor.fetchone() or cursor.execute("SELECT ID, NAME FROM PLACES ORDER BY ID ASC LIMIT 1").fetchone()

                next_place_id, next_place_name = next_place
                cursor.execute("UPDATE PLACES SET IS_SELECTED = 1 WHERE ID = ?", (next_place_id,))
                self.ids.change_place.text = next_place_name

        self.refresh()

    def go_to_steps(self):
        print('Navigating from tasks to steps')
        self.manager.current = 'steps'

    def go_to_pending(self):
        print('Navigating from tasks to pending')
        self.manager.current = 'pending'
