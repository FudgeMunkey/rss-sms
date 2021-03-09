class UrlApi:

    client = None

    # When instantiated, create a client
    def __init__(self):
        self.create_client()

    # Shorten a url
    def shorten_url(self, url):
        raise Exception("Implement send shorten_url()...")

    # Create client
    def create_client(self):
        raise Exception("Implement create create_client()...")
