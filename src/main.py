#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time
import appointmentManager
import os

calendar = None

def on_connect(client,userdata,flags, rc):
    #Hier sollten alle Topics aufgelistet werden, auf welche gehört werden soll
    #Der integer-Wert im Tuple ist egal, da er nicht von der Methode verwendet wird
    client.subscribe([("stt",0)])
    #pass

#Diese Funktion wird aufgerufen, wenn es für ein Topic kein spezielles Callback gibt
def on_message(client, userdata, msg):
    print("message: "+msg.topic+" "+str(msg.payload))

def specific_callback(client, userdata, msg):
    if msg.topic == "stt":
        payload = msg.payload
        
        # Check for "Lösche den Termin" in the payload and delete the next appointment.
        if "Lösche den Termin" in payload:
            # Get the ID of the next appointment
            appointment_id = calendar.get_next_appointment_id()
            # Delete the next appointment
            calendar.delete_appointment(appointment_id)
            calendar.get_next_appointment()
        
        # Check for "Erstelle den Termin am <Datum, z.B. 06.04.> mit dem Titel <Testtitel>" in the payload and create a new appointment.
        elif "Erstelle den Termin am" in payload and "mit dem Titel" in payload:
            # Extract the date and summary from the payload
            date_start_idx = payload.find("am") + 3
            date_end_idx = payload.find("mit dem Titel")
            date = payload[date_start_idx:date_end_idx].strip()
            
            summary_start_idx = payload.find("Titel") + 6
            summary = payload[summary_start_idx:].strip()
            
            # Create a new appointment
            calendar.new_appointment(start=date, end=date, summary=summary, location="")
            calendar.get_next_appointment()
        
        # Check for "Verschiebe den nächsten Termin um <Stunden, z.B. 3,5> Stunden" in the payload and delay the next appointment.
        elif "Verschiebe den nächsten Termin um" in payload and "Stunden" in payload:
            # Extract the number of hours to delay from the payload
            hours_start_idx = payload.find("um") + 2
            hours_end_idx = payload.find("Stunden")
            hours = float(payload[hours_start_idx:hours_end_idx].strip().replace(",", "."))
            
            # Get the ID of the next appointment
            appointment_id = calendar.get_next_appointment_id()
            # Delay the next appointment
            calendar.delay_appointment(appointment_id, hours)
            calendar.get_next_appointment()
    
    elif msg.topic == "appointment/next":
        if msg.payload["id"] != calendar.get_next_appointment_id:
            calendar.next_appointment_notified = False
        calendar.next_appointment = msg.payload

if __name__ == "__main__": # pragma: no cover
    #aufbau der MQTT-Verbindung
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    #Definition einer Callback-Funktion für ein spezielles Topic
    client.message_callback_add("stt", specific_callback)
    client.message_callback_add("appointment/next", specific_callback)

    docker_container = os.environ.get('DOCKER_CONTAINER', False)
    if docker_container:
        mqtt_address = "broker"
    else:
        mqtt_address = "localhost"
    client.connect(mqtt_address,1883,60)
    client.loop_start()
    
    calendar = appointmentManager.appointmentManager(client)

    #Hier kann der eigene Code stehen. Loop oder Threads
    while True:
        time.sleep(30)
        calendar.send_tts_notification()

    #Sollte am Ende stehen, da damit die MQTT-Verbindung beendet wird
    client.loop_stop()
    client.disconnect()