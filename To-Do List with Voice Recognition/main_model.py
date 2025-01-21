import csv
import time
import speech_recognition as sr
import pyttsx3
import spacy
import schedule
import threading
from googleapiclient.discovery import build
from fpdf import FPDF
from transformers import pipeline
from tensorflow import keras

class TodoManager:
    def __init__(self, file_name="todo_list.csv"):
        self.file_name = file_name
        self.headers = ["Task ID", "Task Importance", "Task Added Time", "Main Task", "Task To Be Completed", "Task Status"]
        self.initialize_csv()

    def initialize_csv(self):
        try:
            with open(self.file_name, "x", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)
        except FileExistsError:
            pass

    def add_task(self, task_id, importance, main_task, completion_date):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.file_name, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([task_id, importance, current_time, main_task, completion_date, "Pending"])

    def get_tasks_due_today(self):
        today = time.strftime("%Y-%m-%d")
        tasks_due = []
        with open(self.file_name, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Task To Be Completed"].startswith(today) and row["Task Status"] == "Pending":
                    tasks_due.append(row)
        return tasks_due

    def export_to_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="To-Do List", ln=True, align='C')

        with open(self.file_name, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                pdf.cell(200, 10, txt=", ".join(row), ln=True)

        pdf.output("todo_list.pdf")

    def sync_to_google_calendar(self):
        # Placeholder for Google Calendar sync functionality
        pass

class VoiceAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.nlp = spacy.load("en_core_web_sm")
        self.sentiment_analyzer = pipeline("sentiment-analysis")

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio).lower()
            return command
        except Exception:
            return None

    def parse_command(self, command):
        doc = self.nlp(command)
        return doc

# Background task for reminders
def schedule_reminders(todo_manager):
    schedule.every(1).hour.do(check_due_tasks, todo_manager)
    while True:
        schedule.run_pending()
        time.sleep(1)

def check_due_tasks(todo_manager):
    tasks_due = todo_manager.get_tasks_due_today()
    for task in tasks_due:
        speak(f"Reminder: Task {task['Task ID']} is due today!")

# Main function
def main():
    todo_manager = TodoManager()
    assistant = VoiceAssistant()
    threading.Thread(target=schedule_reminders, args=(todo_manager,)).start()

    assistant.speak("Say 'Hey Bro' to start.")
    while True:
        command = assistant.listen()
        if command:
            if "hey bro" in command:
                assistant.speak("How can I assist you?")
                command = assistant.listen()

                if "create a task" in command:
                    assistant.speak("Please describe the task.")
                    main_task = assistant.listen()
                    assistant.speak("Please provide the importance. Say High, Medium, or Low.")
                    importance = assistant.listen()
                    assistant.speak("When should this task be completed? Say 'On <day> <month>'.")
                    completion_date = assistant.listen()
                    current_year = time.strftime("%Y")
                    completion_date = f"{completion_date} {current_year}"
                    task_id = str(int(time.time()))  # Unique task ID based on timestamp
                    todo_manager.add_task(task_id, importance, main_task, completion_date)
                    assistant.speak("Task added successfully!")

                elif "show tas" in command:
                    assistant.speak("Here are your tasks.")
                    tasks_due = todo_manager.get_tasks_due_today()
                    for task in tasks_due:
                        assistant.speak(f"Task ID: {task['Task ID']}, Task: {task['Main Task']}, Due: {task['Task To Be Completed']}.")

                elif "export tasks" in command:
                    todo_manager.export_to_pdf()
                    assistant.speak("Tasks exported to PDF.")

                elif "stop program" in command:
                    assistant.speak("Goodbye!")
                    break

if __name__ == "__main__":
    main()
