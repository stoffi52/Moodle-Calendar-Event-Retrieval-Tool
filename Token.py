from moodleAPI import MoodleAPI
from json import dumps
import json 
import time

api = MoodleAPI("")
api.login()
site_info = api.get_site_info()
#print(site_info)
with open("output.json", "w") as op:
    op.write(dumps(site_info, indent=4))

response = api.post("core_enrol_get_users_courses", site_info["userid"])
#print(response, type(response))

with open("response.json", "w") as op:
    op.write(dumps(response, indent=4))


names = [course["fullname"] for course in response]
#print(names)

json_schoen = json.dumps(names, indent=4, ensure_ascii=False)
print("Kursnamen:")
print(json_schoen)

assignments = api.get_assignments()

if "courses" in assignments:
    for course in assignments["courses"]:
        print(f"\nKurs: {course['fullname']}")
        if "assignments" in course:
            for assign in course["assignments"]:
                name = assign["name"]
                duedate = assign["duedate"]
                # Umwandeln des Unix-Zeitstempels in ein lesbares Datum
                duedate_str = "kein Abgabedatum" if duedate == 0 else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(duedate))
                print(f"  Aufgabe: {name}")
                print(f"    Abgabedatum: {duedate_str}")
else:
    print("Keine Assignments gefunden.")



