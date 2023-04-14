import json
from datetime import datetime, timedelta
from dateutil.tz import tzlocal

class appointmentManager:
    def __init__(self, mqtt_client):
        self.next_appointment = None
        self.client = mqtt_client
        self.next_appointment_notified = False

    def new_appointment(self, start, end, summary, location):
        # Publish a new appointment to create an appointment.
        payload = {
            "start": start,
            "end": end,
            "summary": summary,
            "location": location
        }
        self.client.publish("appointment/create", json.dumps(payload))
        print("New appointment created:", payload)

    def delete_appointment(self, appointment_id):
        # Publish a request to delete an appointment by ID.
        payload = {
            "id": appointment_id
        }
        self.client.publish("appointment/delete", json.dumps(payload))
        print("Appointment deleted:", payload)

    def delay_appointment(self, hours):
        # Publish a request to delay an appointment by updating its details.
        if self.next_appointment != None:
            payload = {
                "start": (datetime.fromisoformat(self.next_appointment["start"]) + timedelta(hours=int(hours))).isoformat(),
                "end": (datetime.fromisoformat(self.next_appointment["end"]) + timedelta(hours=hours)).isoformat(),
                "id": self.next_appointment["id"],
                "summary": self.next_appointment["summary"],
                "location": self.next_appointment["location"],
                "status": self.next_appointment["status"]
            }
            self.client.publish("appointment/update", json.dumps(payload))
            print("Appointment delayed:", payload)

    def get_next_appointment(self):
        # Prepare the MQTT message and publish it to the appropriate topic
        topic = "req/appointment/next"
        # Set any additional parameters for the request, if needed
        self.client.publish(topic, 0)
    
    def get_next_appointment_id(self):
        try:
            return self.next_appointment["id"]
        except:
            return None
    
    def send_tts_notification(self):
        # Check if the next appointment is set and notification has not been sent yet
        if self.next_appointment != None and not self.next_appointment_notified:
            # Calculate the time difference between now and the next appointment start time
            time_difference = datetime.fromisoformat(self.next_appointment["start"]) - datetime.now(tzlocal())
            minutes_difference = time_difference.total_seconds() / 60

            # Check if the next appointment starts within 15 minutes
            if 0 <= minutes_difference <= 15:
                # Prepare the payload for the MQTT message
                payload = f"{self.next_appointment['summary']} beginnt gleich"

                # Publish the MQTT message with topic "tts" and payload
                self.client.publish("tts", payload)

                # Set the next_appointment_notified flag to True to indicate notification has been sent
                self.next_appointment_notified = True


#"Erstelle den Termin am <Datum, z.B. 06.04.>, um <12> Uhr, mit dem Titel <Testtitel>. Er geht <2> Stunden"
def extract_information_from_text_new_appointment(text):
    words = text.split(" ")
    #for word in range(len(words)):
    #    print(f"{word} {words[word]}")
    
    start = str(words[4]) + str(words[6])
    year = datetime.now().year
    month = words[4].split(".")[1].strip(",")
    day = words[4].split(".")[0]
    hour = words[6]
    start = datetime(int(year), int(month), int(day), int(hour), tzinfo=tzlocal())
    if start < datetime.now(tzlocal()):
        start = datetime(int(year) + 1, int(month), int(day), int(hour), tzinfo=tzlocal())
    end = datetime(start.year, int(month), int(day), int(hour) + int(words[14]), tzinfo=tzlocal())
    summary = str(words[11]).strip(".")
    return start.isoformat(), end.isoformat(), summary


def extract_information_from_text_delay_appointment(text):
    words = text.split(" ")
    #for word in range(len(words)):
    #    print(f"{word} {words[word]}")
    return int(words[4])