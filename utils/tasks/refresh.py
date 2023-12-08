from utils.tasks.select_zipf_tasks import select_zipf_tasks

def refresh(self):
	task_list = select_zipf_tasks()
	for index, task in enumerate(task_list):
		button_id = f"t{index + 1}"
		button = self.ids[button_id]
		button.text = task['text']