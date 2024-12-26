from twilio.rest import Client
import keys_example

def send_sms(msg):
    '''
    Send an SMS message using the Twilio API.

    :param msg: The text message to send
    '''

    try:
<<<<<<< HEAD
<<<<<<< HEAD
        client = Client(keys_example.account_sid, keys_example.auth_token)
        message = client.messages.create(
            body=msg,
            from_ = keys_example.twilio_number,
            to= keys_example.target_number
=======
        client = Client(keys.account_sid, keys.auth_token)
        message = client.messages.create(
            body=msg,
            from_ = keys.twilio_number,
            to= keys.target_number
>>>>>>> 84d5676 (Initial commit for DiaComp project)
=======
        client = Client(keys_example.account_sid, keys_example.auth_token)
        message = client.messages.create(
            body=msg,
            from_ = keys_example.twilio_number,
            to= keys_example.target_number
>>>>>>> ba128ee (Updated files to incorporate example configurations)
        )
    except Exception as e:
        print("Error sending SMS: ", e)
