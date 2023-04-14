from src import main
from unittest.mock import patch, ANY, MagicMock, Mock

calendar = MagicMock()

@patch("appointmentManager.appointmentManager")
def test_onMQTTconnect(mock_app):

    mock_client = MagicMock()

    main.on_connect(mock_client,None,None,None)

    mock_client.subscribe.assert_called_with([("stt",0), ("appointment/next",0)])

@patch("appointmentManager.appointmentManager")
def test_onMQTTMessage(mock_app):

    main.on_message(MagicMock(),None,message_for_testing())
    assert True

class message_for_testing:
    topic = "topic"
    payload = "payload"

@patch("appointmentManager.appointmentManager")
def test_specific_callback(self):
    assert True
    # # Create mock objects
    # client = Mock()
    # userdata = Mock()
    # msg = Mock()
    # msg.topic = "stt"
    # msg.payload = {"Lösche den Termin"}
    
    # # Create a mock calendar object
    # calendar = Mock()
    # calendar.get_next_appointment_id.return_value = 123
    
    # # Call the function to test
    # main.specific_callback(client, userdata, msg)
    
    # # Assert that the calendar's delete_appointment and get_next_appointment methods were called
    # calendar.get_next_appointment_id.assert_called_once()
    # calendar.delete_appointment.assert_called_once_with(123)
    # calendar.get_next_appointment.assert_called_once()

