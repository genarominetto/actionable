import sqlite3
import datetime
import random
from kivy.uix.screenmanager import Screen
from utils.steps.pause import pause
from utils.steps.cancel import cancel
from utils.steps.next_step import next_step
from kivy.clock import Clock

class stepsScreen(Screen):
    def go_to_tasks(self):
        print('Navigating from steps to tasks')
        self.manager.current = 'tasks'

    def on_enter(self):
        print('steps screen has fully loaded')
        self.update_labels()
        Clock.schedule_interval(self.update_timer, 1)

    def update_labels(self):
        # Connect to the database
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()

        # 1. Fetch Task Text
        cursor.execute('''
            SELECT TASK_TEXT FROM HISTORY
            WHERE ACTION = 'Started'
            ORDER BY TIME DESC
            LIMIT 1
        ''')
        task_text = cursor.fetchone()[0]

        # 2. Determine Current Step and Total Steps for the Current Task
        cursor.execute('''
            SELECT STEPS.TASK_ID, STEPS.NAME FROM HISTORY
            JOIN STEPS ON HISTORY.STEP_ID = STEPS.ID
            WHERE ACTION = 'Started'
            ORDER BY TIME DESC
            LIMIT 1
        ''')
        current_task_id, current_step_name = cursor.fetchone()

        cursor.execute(f'''
            SELECT COUNT(*) FROM STEPS
            WHERE TASK_ID = {current_task_id}
        ''')
        total_steps = cursor.fetchone()[0]

        cursor.execute(f'''
            SELECT MAX(STEPS.ORDER_SEQUENCE) FROM HISTORY
            JOIN STEPS ON HISTORY.STEP_ID = STEPS.ID
            WHERE STEPS.TASK_ID = {current_task_id} AND ACTION = 'Finished'
        ''')
        last_completed_step_order = cursor.fetchone()[0] or 0
        current_step = last_completed_step_order + 1

        # Fetch placeholders
        cursor.execute("SELECT * FROM PLACEHOLDERS;")
        placeholders = cursor.fetchall()
        
        # Replace placeholders in the step name
        step_name_with_placeholders = self.replace_placeholders(current_step_name, placeholders)

        steps_text = f'Step {current_step}/{total_steps} {step_name_with_placeholders}'

        # 3. Countdown Timer
        self.countdown_duration = self.calculate_countdown(cursor, current_task_id, current_step)

        # Close the database connection
        conn.close()

        # Update the UI elements
        self.ids.task_text_label.text = task_text
        self.ids.steps_completed_label.text = steps_text
        self.ids.countdown_timer_label.text = str(self.countdown_duration)

    def replace_placeholders(self, task_name, placeholders):
        def select_by_zipf(items):
            if not items:
                return None
            harmonic_sum = sum(1.0 / i for i in range(1, len(items) + 1))
            probabilities = [(1.0 / i) / harmonic_sum for i in range(1, len(items) + 1)]
            return random.choices(items, weights=probabilities, k=1)[0]

        while '%' in task_name:
            start = task_name.find('%')
            end = task_name.find('%', start + 1)
            placeholder_type = task_name[start + 1:end]
            relevant_placeholders = [(p[2], p[0]) for p in placeholders if p[1] == placeholder_type]
            placeholder_value = select_by_zipf(relevant_placeholders)[0] if relevant_placeholders else ''
            task_name = task_name[:start] + placeholder_value + task_name[end + 1:]
        return task_name

    def calculate_countdown(self, cursor, task_id, step_order):
        cursor.execute(f'''
            SELECT TIME FROM HISTORY
            JOIN STEPS ON HISTORY.STEP_ID = STEPS.ID
            WHERE TASK_ID = {task_id} AND ORDER_SEQUENCE = {step_order} AND ACTION = 'Finished'
            ORDER BY TIME DESC
            LIMIT 3
        ''')
        finish_times = cursor.fetchall()

        if finish_times:
            finish_times = [datetime.datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S') for record in finish_times]
            durations = [finish_times[i] - finish_times[i - 1] for i in range(1, len(finish_times))]
            average_duration = sum(durations, datetime.timedelta()) / len(durations)
            countdown_duration = average_duration * 0.9
            self.countdown_start_time = datetime.datetime.now() - countdown_duration
            self.countdown_forward = False
        else:
            self.countdown_start_time = datetime.datetime.now()
            self.countdown_forward = True

        return self.countdown_start_time.strftime('%H:%M:%S')

    def update_timer(self, dt):
        if self.countdown_forward:
            current_time = datetime.datetime.now() - self.countdown_start_time
        else:
            current_time = self.countdown_start_time - datetime.datetime.now()

        self.ids.countdown_timer_label.text = str(current_time).split('.')[0]

    pause = staticmethod(pause)
    cancel = staticmethod(cancel)
    next_step = staticmethod(next_step)
