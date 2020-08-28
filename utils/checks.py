import os
from shutil import copyfile


class FileCheck:
    @staticmethod
    def check_folder(path):
        if os.path.exists(path):
            return True
        return False

    def check_create_folder(self, path):
        if not self.check_folder(path):
            print(f"[Action] Creating a folder for you... ({path})")
            os.makedirs(path)

    @staticmethod
    def check_file(path):
        if os.path.isfile(path):
            return True
        return False

    def check_copy_file(self, path):
        if not self.check_file(path):
            print(f"[Action] Copying a base file for you... ({path}). \nYou have to manually edit something in it!")
            source_path = path.split("/")[-1]
            copyfile(f"utils/base/{source_path}", path)
            exit(1)

    def check_create_file(self, path, content):
        if not self.check_file(path):
            print(f"[Action] Creating a file for you... ({path})")
            with open(path, "w") as f:
                f.write(content)
