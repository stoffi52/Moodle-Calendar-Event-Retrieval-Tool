from moodleAPI import MoodleAPI
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
from bs4 import BeautifulSoup

class MoodleApp:
    def __init__(self, root):
        self.api = MoodleAPI("config.ini")  # Pfad zur Konfigurationsdatei angeben, falls nötig
        self.api.login()

        # Hauptfenster konfigurieren
        root.title("Moodle Aufgaben Übersicht")
        root.geometry("1000x700")

        # Frame für die Aufgaben
        frame_assignments = ttk.LabelFrame(root, text="Kurse und Aufgaben")
        frame_assignments.pack(fill="both", expand="yes", padx=20, pady=20)

        # Scrollbare Textbox für die Aufgaben
        self.assignment_listbox = tk.Listbox(frame_assignments, width=120, height=30, font=("Helvetica", 12))
        self.assignment_listbox.pack(padx=10, pady=10)
        self.assignment_listbox.bind('<Double-1>', self.show_assignment_details)

        # Daten abrufen und anzeigen
        self.load_data()

    def load_data(self):
        site_info = self.api.get_site_info()
        response = self.api.post("core_enrol_get_users_courses", site_info["userid"])

        assignments = self.api.get_assignments()
        self.assignment_details = []

        if "courses" in assignments:
            for course in assignments["courses"]:
                course_index = self.assignment_listbox.size()
                self.assignment_listbox.insert(tk.END, f"Kurs: {course['fullname']}")
                self.assignment_listbox.itemconfig(course_index, {'bg': '#D3D3D3'})  # Kurszeile hervorheben
                if "assignments" in course:
                    sorted_assignments = sorted(course["assignments"], key=lambda x: x["duedate"])
                    for assign in sorted_assignments:
                        name = assign["name"]
                        duedate = assign["duedate"]
                        duedate_str = "kein Abgabedatum" if duedate == 0 else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(duedate))
                        self.assignment_listbox.insert(tk.END, f"  Aufgabe: {name} - Abgabedatum: {duedate_str}")
                        self.assignment_details.append(assign)
                else:
                    self.assignment_listbox.insert(tk.END, "  Keine Aufgaben gefunden.")
                self.assignment_listbox.insert(tk.END, "-" * 120)
        else:
            self.assignment_listbox.insert(tk.END, "Keine Aufgaben gefunden.")

    def show_assignment_details(self, event):
        selected_index = self.assignment_listbox.curselection()[0]

        # Berechnen Sie die Aufgabe im Assignment-Details-Array
        # Wir müssen alle Nicht-Aufgaben-Zeilen überspringen
        actual_index = -1
        for idx in range(selected_index + 1):
            if not self.assignment_listbox.get(idx).startswith("  "):
                continue
            actual_index += 1

        if actual_index < 0 or actual_index >= len(self.assignment_details):
            return

        assign = self.assignment_details[actual_index]
        detail_window = tk.Toplevel()
        detail_window.title(f"Details für {assign['name']}")
        detail_window.geometry("800x600")

        detail_text = tk.Text(detail_window, width=100, height=20, wrap="word", font=("Helvetica", 12))
        detail_text.pack(padx=10, pady=10)

        duedate_str = "kein Abgabedatum" if assign["duedate"] == 0 else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(assign["duedate"]))
        details_html = assign.get('intro', 'Keine Details verfügbar')

        # HTML-Tags entfernen und den Text schön formatieren
        soup = BeautifulSoup(details_html, "html.parser")
        details = soup.get_text()

        formatted_details = (
            f"Aufgabe: {assign['name']}\n"
            f"Abgabedatum: {duedate_str}\n"
            f"{'='*50}\n"
            f"{details}\n"
        )

        detail_text.insert(tk.END, formatted_details)
        detail_text.config(state=tk.DISABLED)  # Textfeld schreibgeschützt machen

# Hauptprogramm
root = tk.Tk()
app = MoodleApp(root)
root.mainloop()
