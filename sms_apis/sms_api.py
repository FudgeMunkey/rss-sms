class SmsApi:

    client = None

    # When instantiated, create a client
    def __init__(self):
        self.create_client()

    # Send an SMS
    def send_sms(self, sms_data):
        raise Exception("Implement send send_sms()...")

    # Create client
    def create_client(self):
        raise Exception("Implement create create_client()...")
