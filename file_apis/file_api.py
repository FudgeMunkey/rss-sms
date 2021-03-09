class FileApi:

    client = None

    # When instantiated, create a client
    def __init__(self):
        self.create_client()

    # Get the contents of a yaml file
    def read_file_yaml(self, file_path):
        raise Exception("Implement send get_file_yaml()...")

    # Write to a yaml file
    def write_file_yaml(self, file_path, data):
        raise Exception("Implement send write_file_yaml()...")

    # Create client
    def create_client(self):
        raise Exception("Implement create create_client()...")
