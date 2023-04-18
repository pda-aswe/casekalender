#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time
import appointmentManager
import os
from datetime import datetime, timedelta
import json

calendar = None

def on_connect(client,userdata,flags, rc):
    #Hier sollten alle Topics aufgelistet werden, auf welche gehört werden soll
    #Der integer-Wert im Tuple ist egal, da er nicht von der Methode verwendet wird
    client.subscribe([("stt",0), ("appointment/next",0)])
    #pass

#Diese Funktion wird aufgerufen, wenn es für ein Topic kein spezielles Callback gibt
def on_message(client, userdata, msg):
    print("message: "+msg.topic+" "+str(msg.payload))

def specific_callback(client, userdata, msg):
    if msg.topic == "stt":
        sttData = json.loads(str(msg.payload.decode("utf-8")))
        payload = sttData['base'].strip().lower()
        
        # Check for "lösche den termin" in the payload and delete the next appointment.
        if "lösche den termin" in payload or "lösche den nächsten termin" in payload:
            # Get the ID of the next appointment
            appointment_id = calendar.get_next_appointment_id()
            if appointment_id != None:
                # Delete the next appointment
                calendar.delete_appointment(appointment_id)
                calendar.get_next_appointment()
                print("Termin geloescht")
                client.publish("tts", "Der Termin wurde gelöscht")
        
        # Check for "Erstelle einen Termin am <Datum, z.B. 21.04.>, um <12> Uhr, mit dem Titel <Testtitel>. Die Dauer beträgt <2> Stunden" in the payload and create a new appointment.
        elif "erstelle einen termin am" in payload:
            start, end, summary = appointmentManager.extract_information_from_text_new_appointment(payload)
            # Extract the date and summary from the payload
            if start == False:
                client.publish("tts", "Ich konnte leider nicht alle Daten verstehen. Versuche es bitte erneut")
            else:
                # Create a new appointment
                calendar.new_appointment(start=start, end=end, summary=summary, location="-")
                calendar.get_next_appointment()
                print("Termin erstellt")
                client.publish("tts", "Der Termin "+summary+" habe ich in den Kalender hinzugefügt.")
        
        # Check for "verschiebe den termin um <Stunden, z.B. 3> stunden" in the payload and delay the next appointment.
        #"b'verschiebe den n\\xc3\\xa4chsten termin um 3 stunden'"
        elif "verschiebe den nächsten termin um" in payload and "stunden" in payload:
            # Extract the number of hours to delay from the payload
            hours = appointmentManager.extract_information_from_text_delay_appointment(payload)
            
            # Get the ID of the next appointment
            appointment_id = calendar.get_next_appointment_id()
            if appointment_id != None and hours != 0:
                # Delay the next appointment
                calendar.delay_appointment(hours)
                calendar.get_next_appointment()
                print("Termin verschoben")
                client.publish("tts", "Der Termin wurde um "+str(hours)+" Stunden verschoben.")
    
    elif msg.topic == "appointment/next":
        payload = json.loads(msg.payload)
        if payload["id"] != calendar.get_next_appointment_id():
            calendar.next_appointment_notified = False
        calendar.next_appointment = payload
          
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
        calendar.send_tts_notification()
        calendar.get_next_appointment()
        time.sleep(10)

    #Sollte am Ende stehen, da damit die MQTT-Verbindung beendet wird
    client.loop_stop()
    client.disconnect()