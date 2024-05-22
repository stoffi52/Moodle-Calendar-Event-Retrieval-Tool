from moodleAPI import MoodleAPI
from json import dumps

api = MoodleAPI("PW.py")
api.login()
site_info = api.get_site_info()
print(site_info)
with open("output.json", "w") as op:
    op.write(dumps(site_info, indent=4))

response = api.post("core_enrol_get_users_courses", site_info["userid"])
print(response, type(response))

with open("response.json", "w") as op:
    op.write(dumps(response, indent=4))


names = [course["fullname"] for course in response]

print(names)