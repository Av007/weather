from os import getenv, path
from flask import current_app


class FileHelper:
    def file_name(self):
        return path.join(f"{current_app.root_path}/../report", getenv('filename'))

    def write_file(self, df):
        file = self.file_name()
        df.to_csv(file, index=False)
