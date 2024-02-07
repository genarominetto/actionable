from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import sqlite3
from datetime import datetime
import random

class habitsScreen(Screen):
    db_path = "tasks.db"  # Database path
    current_habit_id = None  # Current habit ID
    
    def __init__(self, **kwargs):
        super(habitsScreen, self).__init__(**kwargs)
        self.refresh()  # Initialize current_habit_id
    
    def refresh(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        today = datetime.now().date()
        cur.execute("SELECT ID FROM HABITS WHERE LAST_KEEP_DATE != ?", (today,))
        habits = cur.fetchall()
        
        if habits:
            self.current_habit_id = random.choice(habits)[0]
            # Enable buttons because there is a current habit
            self.ids.break_button.disabled = False
            self.ids.keep_button.disabled = False
        else:
            self.current_habit_id = None
            # Disable buttons because there is no current habit
            self.ids.break_button.disabled = True
            self.ids.keep_button.disabled = True
        
        if self.current_habit_id is None:
            self.ids.current_habit_label.text = "Everything up to date"
            self.ids.question_label.text = ""
        else:
            cur.execute("SELECT NAME, STARTED_DATE FROM HABITS WHERE ID = ?", (self.current_habit_id,))
            name, started_date = cur.fetchone()
            started_date = datetime.strptime(started_date, '%Y-%m-%d').date()
            days_passed = (today - started_date).days
            self.ids.current_habit_label.text = f"{days_passed} days {name}"
            self.ids.question_label.text = 'Do you want to break or keep your current habit?'
        
        conn.close()

    def create_new_habit(self):
        name = self.ids.new_habit.text
        today = datetime.now().date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO HABITS (NAME, STARTED_DATE, LAST_KEEP_DATE) VALUES (?, ?, ?)", (name, today, today))
        conn.commit()
        conn.close()
        
        self.ids.new_habit.text = ""  # Clear the TextInput
        self.refresh()  # Refresh to update UI

    def break_habit(self):
        # Create the content layout for the popup
        content = BoxLayout(orientation='vertical', spacing=10)
        message = Label(text='Are you sure you want to break this habit?')
        button_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        # Initialize the popup without specifying content yet
        popup = Popup(title='Confirm Break Habit', size_hint=(None, None), size=(400, 200), auto_dismiss=False)
        
        # Define the Yes and No buttons
        yes_button = Button(text='Yes')
        no_button = Button(text='No')
        
        # Bind the on_press events
        yes_button.bind(on_press=lambda instance: self.confirm_break_habit(popup))
        no_button.bind(on_press=lambda instance: popup.dismiss())
        
        # Add widgets to the layout
        content.add_widget(message)
        button_box.add_widget(yes_button)
        button_box.add_widget(no_button)
        content.add_widget(button_box)
        
        # Set the popup's content and open it
        popup.content = content
        popup.open()

    def confirm_break_habit(self, popup, *args):
        # Delete the current habit
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        if self.current_habit_id is not None:
            cur.execute("DELETE FROM HABITS WHERE ID = ?", (self.current_habit_id,))
            conn.commit()
        conn.close()
        
        # Refresh the UI and dismiss the popup
        self.refresh()
        popup.dismiss()



    def keep(self):
        today = datetime.now().date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        if self.current_habit_id is not None:
            cur.execute("UPDATE HABITS SET LAST_KEEP_DATE = ? WHERE ID = ?", (today, self.current_habit_id))
            conn.commit()
        conn.close()
        self.refresh()  # Refresh to update UI




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
        self.refresh()
