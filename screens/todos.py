from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import sqlite3

class todosScreen(Screen):
    db_path = "tasks.db"  # Database path as an instance variable

    def __init__(self, **kwargs):
        super(todosScreen, self).__init__(**kwargs)

    def go_to_tasks(self):
        self.manager.current = 'tasks'
    
    def go_to_habits(self):
        self.manager.current = 'habits'
    
    def on_enter(self):
        self.refresh()

    def create_new_task(self):
        task_text = self.ids.new_task_input.text
        if task_text:  # Ensure the task text is not empty
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO TODOS (NAME) VALUES (?)", (task_text,))
            conn.commit()
            conn.close()
            self.ids.new_task_input.text = ''  # Clear the input field
            self.refresh()  # Refresh the UI to reflect the new task

    def mark_as_completed(self):
        # Create the content for the popup
        content = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        btn_layout = BoxLayout(size_hint_y=None, height=50)
        yes_btn = Button(text='Yes', size_hint=(0.5, 1))
        no_btn = Button(text='No', size_hint=(0.5, 1))
        content.add_widget(Label(text='Are you sure you want to mark the task as completed?'))
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)

        # Create the popup
        popup = Popup(title='Confirm', content=content, size_hint=(None, None), size=(500, 600), auto_dismiss=False)

        # Bind the on_press event to the Yes and No buttons
        yes_btn.bind(on_press=lambda instance: self.delete_task(popup))
        no_btn.bind(on_press=lambda instance: popup.dismiss())

        popup.open()

    def delete_task(self, popup):
        # Insert the deletion logic here
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT VALUE FROM VARIABLES WHERE KEY = 'todo_pointer'")
        todo_pointer = int(cur.fetchone()[0])
        cur.execute("DELETE FROM TODOS WHERE ID = ?", (todo_pointer,))
        cur.execute("UPDATE TODOS SET ID = ID - 1 WHERE ID > ?", (todo_pointer,))
        cur.execute("UPDATE VARIABLES SET VALUE = '1' WHERE KEY = 'todo_pointer'")
        conn.commit()
        conn.close()
        popup.dismiss()  # Close the popup after deletion
        self.refresh()  # Refresh the UI to reflect changes

    def next(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT MAX(ID) FROM TODOS")
        max_id = cur.fetchone()[0]
        cur.execute("SELECT VALUE FROM VARIABLES WHERE KEY = 'todo_pointer'")
        todo_pointer = int(cur.fetchone()[0])
        new_pointer = 1 if todo_pointer >= max_id else todo_pointer + 1
        cur.execute("UPDATE VARIABLES SET VALUE = ? WHERE KEY = 'todo_pointer'", (str(new_pointer),))
        conn.commit()
        conn.close()
        self.refresh()

    def refresh(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM TODOS")
        count = cur.fetchone()[0]
        if count == 0:
            self.ids.next.disabled = True
            self.ids.mark_as_completed.disabled = True
            self.ids.task_label.text = ''
        elif count == 1:
            self.ids.next.disabled = True
            self.ids.mark_as_completed.disabled = False
            cur.execute("SELECT NAME FROM TODOS WHERE ID = 1")
            self.ids.task_label.text = cur.fetchone()[0]
        else:
            self.ids.next.disabled = False
            self.ids.mark_as_completed.disabled = False
            cur.execute("SELECT VALUE FROM VARIABLES WHERE KEY = 'todo_pointer'")
            todo_pointer = int(cur.fetchone()[0])
            cur.execute("SELECT NAME FROM TODOS WHERE ID = ?", (todo_pointer,))
            self.ids.task_label.text = cur.fetchone()[0]
        conn.close()
