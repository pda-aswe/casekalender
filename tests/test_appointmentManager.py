import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src import appointmentManager

class TestappointmentManager(unittest.TestCase):
    def setUp(self):
        # Create a mock MQTT client
        self.mqtt_client = Mock()

        # Create an instance of EntryManager with the mock MQTT client
        self.entry_manager = appointmentManager.appointmentManager(self.mqtt_client)

    @patch('src.appointmentManager.datetime')
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
        self.entry_manager.new_appointment(start, end, summary, location)

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
        self.entry_manager.delete_appointment(appointment_id)

        # Assert that the MQTT publish method was called with the correct topic and payload
        self.mqtt_client.publish.assert_called_once_with(
            "appointment/delete",
            '{"id": "12345"}'
        )

    @patch('src.appointmentManager.datetime')
    def test_update_entry(self, mock_datetime):
        # Mock the current datetime
        now = '2023-04-06 10:00:00'
        mock_datetime.now.return_value = now

        # Mock the MQTT publish method
        self.mqtt_client.publish = Mock()

        # Call the update_entry method with sample data
        start = '2023-04-06 11:00:00'
        end = '2023-04-06 12:00:00'
        summary = "Test Appointment"
        location = "Test Location"
        appointment_id = "12345"
        status = "tentative"
        self.entry_manager.delay_appointment(appointment_id, start, end, summary, location, status)

        # Assert that the MQTT publish method was called with the correct topic and payload
        self.mqtt_client.publish.assert_called_once_with(
            "appointment/update",
            '{"start": "2023-04-06 11:00:00", "end": "2023-04-06 12:00:00", "id": "12345", "summary": "Test Appointment", "location": "Test Location", "status": "tentative"}'
        )


    def test_send_tts_notification(self):
        # Mock the MQTT publish method
        self.mqtt_client.publish = Mock()

        # Set up a sample next appointment within 5 minutes from now
        next_appointment_start = datetime.now() + timedelta(minutes=3)
        next_appointment_end = next_appointment_start + timedelta(hours=1)
        self.entry_manager.next_appointment = {
            "start": next_appointment_start,
            "end": next_appointment_end,
            "summary": "Test Appointment",
            "location": "Test Location",
            "id": "12345",
            "status": "confirmed"
        }

        # Call the send_tts_notification method
        self.entry_manager.send_tts_notification()

        # Assert that the MQTT publish method was called with the correct topic and payload
        self.mqtt_client.publish.assert_called_once_with(
            "tts",
            f"{self.entry_manager.next_appointment['summary']} beginnt gleich"
        )

    def test_send_tts_notification_no_next_appointment(self):
        # Mock the MQTT publish method
        self.mqtt_client.publish = Mock()

        # Set next_appointment to None
        self.entry_manager.next_appointment = None

def datetime_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError('Object of type {} is not JSON serializable'.format(type(obj)))
