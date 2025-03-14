import os
import json
from datetime import datetime

class TodoManager:
    def __init__(self, todo_file_path="Data/todo/tasks.json"):
        """Initialize the TodoManager with a file path for storing tasks."""
        self.todo_file_path = todo_file_path
        self.tasks = []
        self._ensure_directory_exists()
        self._load_tasks()

    def _ensure_directory_exists(self):
        """Ensure the directory for the todo file exists."""
        directory = os.path.dirname(self.todo_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def _load_tasks(self):
        """Load tasks from the JSON file."""
        if os.path.exists(self.todo_file_path):
            try:
                with open(self.todo_file_path, 'r') as file:
                    self.tasks = json.load(file)
            except json.JSONDecodeError:
                self.tasks = []
        else:
            self.tasks = []

    def _save_tasks(self):
        """Save tasks to the JSON file."""
        with open(self.todo_file_path, 'w') as file:
            json.dump(self.tasks, file, indent=4)

    def add_task(self, task, priority="medium", due_date=None):
        """
        Add a new task to the todo list.
        
        Args:
            task (str): The task description
            priority (str): Priority level (low, medium, high)
            due_date (str): Due date in format YYYY-MM-DD (optional)
        
        Returns:
            bool: True if task was added successfully
        """
        task_id = len(self.tasks) + 1
        new_task = {
            "id": task_id,
            "task": task,
            "priority": priority,
            "due_date": due_date,
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.tasks.append(new_task)
        self._save_tasks()
        return True

    def list_tasks(self, show_completed=False):
        """
        List all tasks.
        
        Args:
            show_completed (bool): Whether to include completed tasks
            
        Returns:
            list: List of tasks
        """
        if not show_completed:
            return [task for task in self.tasks if not task["completed"]]
        return self.tasks

    def complete_task(self, task_id):
        """
        Mark a task as completed.
        
        Args:
            task_id (int): The ID of the task to mark as completed
            
        Returns:
            bool: True if task was marked as completed, False if not found
        """
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_tasks()
                return True
        return False

    def remove_task(self, task_id):
        """
        Remove a task from the todo list.
        
        Args:
            task_id (int): The ID of the task to remove
            
        Returns:
            bool: True if task was removed, False if not found
        """
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                self.tasks.pop(i)
                self._save_tasks()
                return True
        return False

    def get_task(self, task_id):
        """
        Get a specific task by ID.
        
        Args:
            task_id (int): The ID of the task to retrieve
            
        Returns:
            dict: The task if found, None otherwise
        """
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def update_task(self, task_id, task=None, priority=None, due_date=None):
        """
        Update a task's details.
        
        Args:
            task_id (int): The ID of the task to update
            task (str, optional): New task description
            priority (str, optional): New priority level
            due_date (str, optional): New due date
            
        Returns:
            bool: True if task was updated, False if not found
        """
        for t in self.tasks:
            if t["id"] == task_id:
                if task:
                    t["task"] = task
                if priority:
                    t["priority"] = priority
                if due_date:
                    t["due_date"] = due_date
                self._save_tasks()
                return True
        return False

def format_task_for_speech(task):
    """Format a task for speech output."""
    result = f"Task {task['id']}: {task['task']}"
    if task["priority"]:
        result += f", Priority: {task['priority']}"
    if task["due_date"]:
        result += f", Due: {task['due_date']}"
    return result