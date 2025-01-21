import csv
import time
import speech_recognition as sr
import pyttsx3  # For text-to-speech
import pyaudio 

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

    def mark_task_complete(self, task_id):
        tasks = []
        with open(self.file_name, "r") as file:
            reader = csv.reader(file)
            tasks = list(reader)
        for task in tasks:
            if task[0] == task_id:
                task[-1] = "Completed"
        with open(self.file_name, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(tasks)

    def display_tasks(self):
        with open(self.file_name, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        speak("Sorry, I could not understand the audio.")
    except sr.RequestError:
        print("Could not request results, please check your internet connection.")
        speak("Could not request results, please check your internet connection.")
    return None

def main():
    todo_manager = TodoManager()
    speak("Say 'Hey Bro' to start or 'stop program' to exit.")
    print("Say 'Hey Bro' to start or 'stop program' to exit.")
    while True:
        command = listen_for_command()
        if command:
            if "hey bro" in command:
                speak("How can I assist you?")
                print("How can I assist you?")
                command = listen_for_command()
                if "create a task" in command:
                    speak("Please describe the task.")
                    print("Please describe the task.")
                    main_task = listen_for_command()
                    speak("Please provide the importance. Say High, Medium, or Low.")
                    print("Please provide the importance (High/Medium/Low).")
                    importance = listen_for_command()
                    speak("When should this task be completed? Say 'On <day> <month>'.")
                    print("When should this task be completed? Say 'On <day> <month>'.")
                    completion_date = listen_for_command()
                    current_year = time.strftime("%Y")
                    completion_date = f"{completion_date} {current_year}"
                    task_id = str(len(list(csv.reader(open(todo_manager.file_name)))) - 1)  # Sequential task ID
                    todo_manager.add_task(task_id, importance, main_task, completion_date)
                    speak("Task added successfully!")
                    print("Task added successfully!")
                elif "show tas" in command:  # when i say show task , it recognises it as "show tas"
                    speak("Here are your tasks.")
                    todo_manager.display_tasks()
                elif "complete task" in command:
                    speak("Please provide the task ID to mark as complete.")
                    print("Please provide the task ID to mark as complete.")
                    task_id = listen_for_command()
                    todo_manager.mark_task_complete(task_id)
                    speak("Task marked as complete!")
                    print("Task marked as complete!")
            elif "stop program" in command:
                speak("Goodbye!")
                print("Goodbye!")
                break

if __name__ == "__main__":
    main()
