from moodleAPI import MoodleAPI
import time
import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup
import webbrowser

class MoodleApp:
    def __init__(self, root):
        self.api = MoodleAPI("config.ini")
        self.api.login()

        # Hauptfenster konfigurieren
        root.title("Moodle Aufgaben Übersicht")
        root.geometry("1000x700")

        # Frame für die Aufgaben
        frame_assignments = ttk.LabelFrame(root, text="Kurse und Aufgaben")
        frame_assignments.pack(fill="both", expand="yes", padx=20, pady=20)

        # Frame für vergangene Aufgaben
        self.past_assignments_listbox = self.create_listbox(frame_assignments, "Vergangene Aufgaben")
        self.upcoming_assignments_listbox = self.create_listbox(frame_assignments, "Noch zu erledigen")

        # Daten abrufen und anzeigen
        self.load_data()

    def create_listbox(self, parent_frame, title):
        # Frame für Aufgaben
        frame = ttk.LabelFrame(parent_frame, text=title)
        frame.pack(fill="both", expand="yes", padx=10, pady=10)

        # Scrollbare Textbox für die Aufgaben
        listbox = tk.Listbox(frame, width=120, height=15, font=("Helvetica", 12))
        listbox.pack(padx=10, pady=10)
        listbox.bind('<Double-1>', self.on_double_click)

        return listbox

    def load_data(self):
        site_info = self.api.get_site_info()
        response = self.api.post("core_enrol_get_users_courses", site_info["userid"])

        assignments = self.api.get_assignments()
        self.assignment_details = []

        past_assignments = []
        upcoming_assignments = []

        if "courses" in assignments:
            for course in assignments["courses"]:
                if "assignments" in course:
                    for assign in course["assignments"]:
                        assign['course_name'] = course['fullname']
                        if assign["duedate"] != 0 and assign["duedate"] < time.time():
                            past_assignments.append(assign)
                        else:
                            upcoming_assignments.append(assign)

            # Sortieren der Aufgaben nach Abgabedatum
            past_assignments.sort(key=lambda x: x["duedate"])
            upcoming_assignments.sort(key=lambda x: x["duedate"])

            # Sortierte Aufgaben anzeigen
            for assign in past_assignments:
                self.display_assignment(assign, self.past_assignments_listbox)

            for assign in upcoming_assignments:
                self.display_assignment(assign, self.upcoming_assignments_listbox)
        else:
            self.past_assignments_listbox.insert(tk.END, "Keine Aufgaben gefunden.")
            self.upcoming_assignments_listbox.insert(tk.END, "Keine Aufgaben gefunden.")

    def display_assignment(self, assign, listbox):
        name = assign["name"]
        duedate = assign["duedate"]
        duedate_str = "kein Abgabedatum" if duedate == 0 else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(duedate))
        display_text = f"Aufgabe: {name} - Abgabedatum: {duedate_str}"
        listbox.insert(tk.END, display_text)
        self.assignment_details.append((listbox, display_text, assign))

    def on_double_click(self, event):
        widget = event.widget
        selected_index = widget.curselection()[0]
        selected_text = widget.get(selected_index)

        # Berechnen Sie die Aufgabe im Assignment-Details-Array
        actual_index = -1
        for idx, (listbox, display_text, assign) in enumerate(self.assignment_details):
            if listbox == widget and selected_text == display_text:
                actual_index = idx
                break

        if actual_index < 0 or actual_index >= len(self.assignment_details):
            return

        _, _, assign = self.assignment_details[actual_index]
        self.show_assignment_details(assign)

    def show_assignment_details(self, assign):
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
            f"Kurs: {assign['course_name']}\n"
            f"Aufgabe: {assign['name']}\n"
            f"Abgabedatum: {duedate_str}\n"
            f"{'='*50}\n"
            f"{details}\n"
        )

        detail_text.insert(tk.END, formatted_details)
        detail_text.config(state=tk.DISABLED)  # Textfeld schreibgeschützt machen

        # URL ermitteln
        assignment_url = f"{self.api.url}mod/assign/view.php?id={assign['cmid']}&token={self.api.token}"

        open_button = tk.Button(detail_window, text="Aufgabe im Browser öffnen", command=lambda: self.open_assignment_in_browser(assignment_url), bg="purple", fg="white")
        open_button.pack(pady=10)

    def open_assignment_in_browser(self, url):
        webbrowser.open(url)

# Hauptprogramm
root = tk.Tk()
app = MoodleApp(root)
root.mainloop()
