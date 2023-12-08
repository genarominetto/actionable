# @title Select Five Tasks
import sqlite3
import random

def select_zipf_tasks(cursor):
    """
    Selects 5 unique tasks for the selected place in the database using Zipf distribution.
    Replaces placeholders in task names and returns a list of dicts with task id and text.

    Args:
    cursor (sqlite3.Cursor): A cursor to execute queries on the database.

    Returns:
    list of dicts: A list of 5 dictionaries with keys 'task id' and 'text'.
    """

    def select_by_zipf(items):
        """
        Applies Zipf's law to select an item based on rank.
        """
        if not items:
            return None

        harmonic_sum = sum(1.0 / i for i in range(1, len(items) + 1))
        probabilities = [(1.0 / i) / harmonic_sum for i in range(1, len(items) + 1)]
        return random.choices(items, weights=probabilities, k=1)[0]

    def replace_placeholders(task_name, placeholders):
        """
        Replaces placeholders in a task name using Zipf distribution.
        """
        while '%' in task_name:
            start = task_name.find('%')
            end = task_name.find('%', start + 1)
            placeholder_type = task_name[start + 1:end]
            relevant_placeholders = [p for p in placeholders if p[1] == placeholder_type]
            placeholder_value = select_by_zipf(relevant_placeholders)[2] if relevant_placeholders else ''
            task_name = task_name[:start] + placeholder_value + task_name[end + 1:]
        return task_name

    # Select the place marked as selected
    cursor.execute("SELECT * FROM PLACES WHERE IS_SELECTED = 1;")
    selected_place = cursor.fetchone()
    if not selected_place:
        return "No place is selected."

    selected_place_id = selected_place[0]
    selected_tasks = set()
    final_tasks = []

    # Fetch all placeholders for replacement
    cursor.execute("SELECT * FROM PLACEHOLDERS;")
    placeholders = cursor.fetchall()

    while len(final_tasks) < 5:
        # Context, Tag, and Task selection
        cursor.execute(f"SELECT * FROM CONTEXTS WHERE PLACE_ID = {selected_place_id};")
        contexts = cursor.fetchall()
        selected_context = select_by_zipf(contexts)
        cursor.execute(f"SELECT * FROM TAGS WHERE CONTEXT_ID = {selected_context[0]};")
        tags = cursor.fetchall()
        selected_tag = select_by_zipf(tags)
        cursor.execute(f"SELECT * FROM TASKS WHERE TAG_ID = {selected_tag[0]};")
        tasks = cursor.fetchall()
        selected_task = select_by_zipf(tasks)

        # Ensure uniqueness of tasks
        if selected_task[0] not in selected_tasks:
            selected_tasks.add(selected_task[0])
            task_with_placeholders_replaced = replace_placeholders(selected_task[2], placeholders)
            final_tasks.append({"task id": selected_task[0], "text": task_with_placeholders_replaced})

    return final_tasks

# Example of how to use the function
# Create a database connection and cursor
conn = sqlite3.connect('tasks.db')
cursor = conn.cursor()

# Execute the function
tasks_output = select_zipf_tasks(cursor)

# Closing the database connection
conn.close()

print(tasks_output)
