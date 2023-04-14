import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from src import appointmentManager
import json

class TestappointmentManager(unittest.TestCase):
    def setUp(self):
        # Create a mock MQTT client
        self.mqtt_client = Mock()

        # Create an instance of EntryManager with the mock MQTT client
        self.appointmentManager = appointmentManager.appointmentManager(self.mqtt_client)

    @patch('appointmentManager.datetime')
    def test_add_entry(self, mock_datetime):
        # Mock the current datetime
        now = '2023-04-06 10:00:00'
        mock_datetime.now.return_value = now

        # Mock the MQTT publish method
        self.mqtt_client.publish = Mock()

        # Call the add_entry method with sample data
        start = '2023-04-06 11:00:00'
        end = '2023-04-06 12:00:00'
        summary = "Test Appointment"
        location = "Test Location"
        self.appointmentManager.new_appointment(start, end, summary, location)

        # Assert that the MQTT publish method was called with the correct topic and payload
        self.mqtt_client.publish.assert_called_once_with(
            "appointment/create",
            '{"start": "2023-04-06 11:00:00", "end": "2023-04-06 12:00:00", "summary": "Test Appointment", "location": "Test Location"}'
        )

    def test_delete_entry(self):
        # Mock the MQTT publish method
        self.mqtt_client.publish = Mock()

        # Call the delete_entry method with sample data
        appointment_id = "12345"
        self.appointmentManager.delete_appointment(appointment_id)

        # Assert that the MQTT publish method was called with the correct topic and payload
        self.mqtt_client.publish.assert_called_once_with(
            "appointment/delete",
            '{"id": "12345"}'
        )

    @patch('appointmentManager.json.dumps')
    @patch('appointmentManager.datetime')
    def test_update_entry(self, mock_datetime, mock_dumps):
        # Mock the current datetime
        now = '2023-04-06 10:00:00'
        mock_datetime.now.return_value = now

        # Mock the MQTT publish method
        self.mqtt_client.publish = Mock()

        # Call the update_entry method with sample data
        test_app = '{"start": "2023-04-06 10:00:00", "end": "2023-04-06 11:00:00", "id": "12345", "summary": "Test Appointment", "location": "Test Location", "status": "Test status"}'
        self.appointmentManager.next_appointment = json.loads(test_app)
        self.appointmentManager.delay_appointment(1)

        # Assert that the MQTT publish method was called with the correct topic and payload
        self.mqtt_client.publish.assert_called_once_with('appointment/update', mock_dumps())


    def test_send_tts_notification(self):
        # Mock the MQTT publish method
        self.mqtt_client.publish = Mock()

        # Set up a sample next appointment within 5 minutes from now
        next_appointment_start = datetime.now(tzlocal()) + timedelta(minutes=3)
        next_appointment_end = next_appointment_start + timedelta(hours=1)
        next_appointment_start = str(next_appointment_start.isoformat())
        next_appointment_end = str(next_appointment_end.isoformat())
        test_app = '{"start": "' + next_appointment_start + '", "end": "' + next_appointment_end + '", "id": "12345", "summary": "Test Appointment", "location": "Test Location", "status": "Test status"}'
        self.appointmentManager.next_appointment = json.loads(test_app)

        # Call the send_tts_notification method
        self.appointmentManager.send_tts_notification()

        # Assert that the MQTT publish method was called with the correct topic and payload
        self.mqtt_client.publish.assert_called_once_with(
            "tts",
            f"{self.appointmentManager.next_appointment['summary']} beginnt gleich"
        )

    def test_send_tts_notification_no_next_appointment(self):
        # Mock the MQTT publish method
        self.mqtt_client.publish = Mock()

        # Set next_appointment to None
        self.appointmentManager.next_appointment = None

    def test_extract_information_from_text_new_appointment(self):
        text = "Erstelle einen Termin am 14.04, um 12 Uhr, mit dem Titel Test. Er geht 2 Stunden"
        assert appointmentManager.extract_information_from_text_new_appointment(text) == ("2024-04-14T12:00:00+02:00", "2024-04-14T14:00:00+02:00", "Test")

    def test_extract_information_from_text_delay_appointment(self):
        text = "Verschiebe den Termin um 3 Stunden"
        assert appointmentManager.extract_information_from_text_delay_appointment(text) == 3
