from file_apis.file_api import FileApi
import yaml


class FileLocal(FileApi):

    def read_file_yaml(self, file_path):
        # TODO: Error handling
        with open(file_path) as file:
            file_data = yaml.load(file, Loader=yaml.FullLoader)

        return file_data if file_data else {}

    def write_file_yaml(self, file_path, data):
        # TODO: Error handling
        with open(file_path, "w") as file:
            yaml.dump(data, file)
