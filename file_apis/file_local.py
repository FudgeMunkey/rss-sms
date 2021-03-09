from file_apis.file_api import FileApi
import yaml


class FileLocal(FileApi):

    # When instantiated, don't create a client
    def __init__(self):
        pass

    def read_file_yaml(self, file_path):
        # TODO: Error handling
        with open(file_path) as file:
            file_data = yaml.load(file, Loader=yaml.FullLoader)

        if not file_data:
            file_data = {}

        return file_data

    def write_file_yaml(self, file_path, data):
        # TODO: Error handling
        with open(file_path, "w") as file:
            yaml.dump(data, file)
