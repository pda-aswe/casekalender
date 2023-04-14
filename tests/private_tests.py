#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time
import os

def on_connect(client,userdata,flags, rc):
    #Hier sollten alle Topics aufgelistet werden, auf welche gehört werden soll
    #Der integer-Wert im Tuple ist egal, da er nicht von der Methode verwendet wird
    client.subscribe([("stt",0), ("tts",0), ("appointment/delete",0), ("appointment/create",0), ("appointment/update",0), ("req/appointment/next",0), ("appointment/next",0)])
    #pass

#Diese Funktion wird aufgerufen, wenn es für ein Topic kein spezielles Callback gibt
def on_message(client, userdata, msg):
    print("message: "+msg.topic+" "+str(msg.payload))

class message_for_testing:
    topic = "topic"
    payload = "payload"


if __name__ == "__main__": # pragma: no cover
    #aufbau der MQTT-Verbindung
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    docker_container = os.environ.get('DOCKER_CONTAINER', False)
    if docker_container:
        mqtt_address = "broker"
    else:
        mqtt_address = "localhost"
    client.connect(mqtt_address,1883,60)
    client.loop_start()
    
    #Hier kann der eigene Code stehen. Loop oder Threads
    while True:
        # client.publish("stt", "Erstelle den Termin am 14.04, um 12 Uhr, mit dem Titel Test. Er geht 2 Stunden")
        # time.sleep(5)
        client.publish("appointment/next", '{"start":"2023-04-13T16:35:00+02:00","end":"2023-04-13T22:00:00+02:00","id":"124","summary":"test2","location":"<STRING-MIT-DEM-STANDORT>","status":"<STATUS MEIST confirmed>"}')
        time.sleep(5)
        # client.publish("stt", "Verschiebe den Termin um 3 Stunden")
        # time.sleep(30)
        # client.publish("stt", "Lösche den Termin")
        # time.sleep(30)

    #Sollte am Ende stehen, da damit die MQTT-Verbindung beendet wird
    client.loop_stop()
    client.disconnect()