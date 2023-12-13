import sqlite3
import random
from kivy.uix.screenmanager import Screen

class stepsScreen(Screen):
    class Step:
        db_path = "tasks.db"

        def __init__(self, screen):
            self.screen = screen
            self.state = None
            self.current_step_id, self.total_steps, self.step_name, self.order_sequence = (None, None, None, None)
            self.placeholders = self._get_placeholders()
            self.step_text = None

        def update_step_info(self):
            self.current_step_id, self.total_steps, self.step_name, self.order_sequence = self._get_step_info()
            self.step_text = f"({self.order_sequence}/{self.total_steps}) {self.replace_placeholders(self.step_name, self.placeholders)}"
            self.update_ui()

        def _get_step_info(self):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT STEP_ID FROM HISTORY WHERE ACTION = 'Started' ORDER BY ID DESC LIMIT 1")
                current_step_id = cursor.fetchone()[0]
                cursor.execute("SELECT TASK_ID, NAME, ORDER_SEQUENCE FROM STEPS WHERE ID = ?", (current_step_id,))
                task_id, step_name, order_sequence = cursor.fetchone()
                cursor.execute("SELECT COUNT(ID) FROM STEPS WHERE TASK_ID = ?", (task_id,))
                total_steps = cursor.fetchone()[0]
            return current_step_id, total_steps, step_name, order_sequence

        def _get_placeholders(self):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ID, TYPE, VALUE, RANK FROM PLACEHOLDERS")
                return cursor.fetchall()

        def select_by_zipf(self, items):
            if not items:
                return None
            harmonic_sum = sum(1.0 / i for i in range(1, len(items) + 1))
            probabilities = [(1.0 / i) / harmonic_sum for i in range(1, len(items) + 1)]
            return random.choices(items, weights=probabilities, k=1)[0]

        def replace_placeholders(self, step_name, placeholders):
            while '%' in step_name:
                start = step_name.find('%')
                end = step_name.find('%', start + 1)
                placeholder_type = step_name[start + 1:end]
                relevant_placeholders = [p for p in placeholders if p[1] == placeholder_type]
                placeholder_value = self.select_by_zipf(relevant_placeholders)[2] if relevant_placeholders else ''
                step_name = step_name[:start] + placeholder_value + step_name[end + 1:]
            return step_name

        def change_state(self, new_state):
            self.state = new_state
            self._record_history()
            self.update_ui()

        def _record_history(self):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO HISTORY (STEP_ID, ACTION, TIME) VALUES (?, ?, CURRENT_TIMESTAMP)", (self.current_step_id, self.state))
                conn.commit()

        def update_ui(self):
            # Update the step text only if it's the first time or the state has changed to "Finished" or "Next Step"
            if self.state in ["Finished", "Next Step"] or self.step_text is None:
                self.step_text = f"({self.order_sequence}/{self.total_steps}) {self.replace_placeholders(self.step_name, self.placeholders)}"

            self.screen.ids.steps_completed_label.text = self.step_text

            # Update button states based on current state
            if self.state == "Paused":
                self.screen.ids.pause_or_resume_button.text = "Resume"
                self.screen.ids.next_step_button.disabled = True
            elif self.state == "Started":
                self.screen.ids.pause_or_resume_button.text = "Pause"
                self.screen.ids.next_step_button.disabled = False

        def get_next_step(self):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ID, ORDER_SEQUENCE FROM STEPS WHERE TASK_ID = (SELECT TASK_ID FROM STEPS WHERE ID = ?) AND ORDER_SEQUENCE > ? ORDER BY ORDER_SEQUENCE ASC LIMIT 1", (self.current_step_id, self.order_sequence))
                result = cursor.fetchone()
            return result if result else (None, None)

        def set_next_step(self, next_step_id, next_order_sequence):
            self.current_step_id = next_step_id
            self.order_sequence = next_order_sequence
            self._update_step_name_and_placeholders()
            self.change_state("Next Step")

        def _update_step_name_and_placeholders(self):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT NAME FROM STEPS WHERE ID = ?", (self.current_step_id,))
                self.step_name = cursor.fetchone()[0]
            self.step_text = f"({self.order_sequence}/{self.total_steps}) {self.replace_placeholders(self.step_name, self.placeholders)}"


    def __init__(self, **kwargs):
        super(stepsScreen, self).__init__(**kwargs)
        self.step = self.Step(self)

    def on_enter(self):
        print('Steps screen has fully loaded')
        self.step.update_step_info()

    def go_to_tasks(self):
        print('Navigating from steps to tasks')
        self.manager.current = 'tasks'

    def pause_or_resume(self):
        if self.step.state == "Paused":
            self.step.change_state("Started")
        else:
            self.step.change_state("Paused")

    def cancel(self):
        self.step.change_state("Canceled")
        self.go_to_tasks()

    def next_step(self):
        self.step.change_state("Finished")
        next_step_id, next_order_sequence = self.step.get_next_step()
        if next_step_id is not None:
            self.step.set_next_step(next_step_id, next_order_sequence)
        else:
            self.go_to_tasks()