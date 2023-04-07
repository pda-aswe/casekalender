import json
from datetime import datetime, timedelta

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

    def delay_appointment(self, appointment_id, start, end, summary, location, status):
        # Publish a request to delay an appointment by updating its details.
        payload = {
            "start": start,
            "end": end,
            "id": appointment_id,
            "summary": summary,
            "location": location,
            "status": status
        }
        self.client.publish("appointment/update", json.dumps(payload))
        print("Appointment delayed:", payload)

    def get_next_appointment(self):
        # Prepare the MQTT message and publish it to the appropriate topic
        topic = "req/appointment/next"
        # Set any additional parameters for the request, if needed
        self.client.publish(topic, 0)
    
    def get_next_appointment_id(self):
        return self.next_appointment["id"]
    
    def send_tts_notification(self):
        # Check if the next appointment is set and notification has not been sent yet
        if self.next_appointment != None and not self.next_appointment_notified:
            # Calculate the time difference between now and the next appointment start time
            time_difference = self.next_appointment['start'] - datetime.now()
            minutes_difference = time_difference.total_seconds() / 60

            # Check if the next appointment starts within 5 minutes
            if 0 <= minutes_difference <= 5:
                # Prepare the payload for the MQTT message
                payload = f"{self.next_appointment['summary']} beginnt gleich"

                # Publish the MQTT message with topic "tts" and payload
                self.client.publish("tts", payload)

                # Set the next_appointment_notified flag to True to indicate notification has been sent
                self.next_appointment_notified = True