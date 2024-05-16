import requests
import json

# Konfiguration
moodle_url = 'https://moodle2.htlinn.ac.at'
webservice_url = moodle_url + '/webservice/rest/server.php'
token = 'token'
userid = 'userid'

# API-Endpunkt und Parameter für den Kalenderabruf
calendar_function = 'core_calendar_get_calendar_events'
params = {
    'wstoken': token,
    'wsfunction': calendar_function,
    'userid': userid
}

try:
    # Anfrage an die Moodle-API senden
    response = requests.post(webservice_url, params=params)
    # JSON-Daten erhalten und parsen
    data = response.json()
    # Kalenderdaten anzeigen
    for event in data['events']:
        print("Event: {}".format(event['name']))
        print("Start: {}".format(event['timestart']))
        print("End: {}".format(event['timeend']))
        print("Description: {}".format(event['description']))
        print("Location: {}".format(event['location']))
        print("----------")
except requests.exceptions.RequestException as e:
    print('Error:', e)