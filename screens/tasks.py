from kivy.uix.screenmanager import Screen
from utils.tasks.t1 import t1
from utils.tasks.t2 import t2
from utils.tasks.t3 import t3
from utils.tasks.t4 import t4
from utils.tasks.t5 import t5
from utils.tasks.select_zipf_tasks import select_zipf_tasks
import sqlite3
from datetime import datetime

class tasksScreen(Screen):
    def __init__(self, **kwargs):
        super(tasksScreen, self).__init__(**kwargs)
        self.task_id_mapping = {}

    def go_to_steps(self):
        print('Navigating from tasks to steps')
        self.manager.current = 'steps'
    def on_enter(self):
        print('tasks screen has fully loaded')
        self.set_current_place()
        self.refresh()

    def set_current_place(self):
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()

        # Query for the currently selected place
        cursor.execute("SELECT NAME FROM PLACES WHERE IS_SELECTED = 1")
        selected_place_row = cursor.fetchone()

        if selected_place_row:
            # Update the Change Place button text
            self.ids.change_place.text = selected_place_row[0]
        else:
            print("No selected place found.")

        conn.close()

    t1 = staticmethod(t1)
    t2 = staticmethod(t2)
    t3 = staticmethod(t3)
    t4 = staticmethod(t4)
    t5 = staticmethod(t5)

    def change_place(self):
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()

        # Find the current selected place
        cursor.execute("SELECT ID, NAME FROM PLACES WHERE IS_SELECTED = 1")
        current_place = cursor.fetchone()

        if current_place:
            current_place_id, current_place_name = current_place

            # Set the current place's IS_SELECTED to 0
            cursor.execute("UPDATE PLACES SET IS_SELECTED = 0 WHERE ID = ?", (current_place_id,))

            # Find the next place or loop back to the first
            cursor.execute("SELECT ID, NAME FROM PLACES WHERE ID > ? ORDER BY ID ASC LIMIT 1", (current_place_id,))
            next_place = cursor.fetchone()

            if not next_place:
                # If no next place, select the first place
                cursor.execute("SELECT ID, NAME FROM PLACES ORDER BY ID ASC LIMIT 1")
                next_place = cursor.fetchone()

            next_place_id, next_place_name = next_place

            # Set the next place's IS_SELECTED to 1
            cursor.execute("UPDATE PLACES SET IS_SELECTED = 1 WHERE ID = ?", (next_place_id,))

            # Update the button text to the new place
            self.ids.change_place.text = next_place_name

            conn.commit()
        else:
            print("No selected place found.")

        conn.close()

        # Refresh tasks
        self.refresh()

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
            self.add_to_history(selected_task_id)
        else:
            print("No task selected")

    def add_to_history(self, task_id):
        action = "Started"
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()

        # Find the step_id for the given task_id with ORDER_SEQUENCE = 1
        cursor.execute('''SELECT ID FROM STEPS WHERE TASK_ID = ? AND ORDER_SEQUENCE = 1''', (task_id,))
        step_row = cursor.fetchone()

        if step_row is None:
            print(f"No step found for task_id: {task_id}")
            conn.close()
            return

        step_id = step_row[0]

        # Insert into HISTORY table
        cursor.execute('''INSERT INTO HISTORY (STEP_ID, ACTION, TIME)
                        VALUES (?, ?, ?)''', (step_id, action, time))

        conn.commit()
        conn.close()

        print(f"Record added to HISTORY with step_id: {step_id}, action: {action}, time: {time}")




