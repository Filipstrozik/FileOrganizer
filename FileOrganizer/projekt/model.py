import json
import os
import shutil
import time
from pathlib import Path

from win32com.client import Dispatch

from extensions import extensions_paths


class Model:
    destination: Path
    watch: Path

    def __init__(self):

        try:
            self.extensions_paths = json.load(open('My extension.json'))
        except:
            self.extensions_paths = extensions_paths
            self.save_extensions()
        return

    def save_extensions(self):
        j = json.dumps(self.extensions_paths)
        with open('My extension.json', 'w') as f:
            f.write(j)
            f.close()

    def createNewDir(self, path):
        os.mkdir(path)

    def add_date_to_path(self, path: Path, child: Path):
        child_date = time.ctime(os.path.getctime(child))
        child_year = child_date[-4:]
        child_month = child_date[4:7]
        dated_path = path / f'{child_year}' / f'{child_month}'
        dated_path.mkdir(parents=True, exist_ok=True)
        return dated_path

    def cleanup(self, watch_path: Path, destination_root: Path, deep, dated, shortcut, only_view):
        self.destination = destination_root
        self.watch = watch_path
        for child in watch_path.iterdir():
            if child.is_file() and child.suffix.lower() in self.extensions_paths:
                destination_path = destination_root / self.extensions_paths[child.suffix.lower()]
                if dated.get() == 1:
                    destination_path = self.add_date_to_path(destination_path, child)
                else:
                    destination_path.mkdir(parents=True, exist_ok=True)
                if only_view.get() == 1:
                    self.create_shortcut(path=destination_path, target=str(child), name=child.stem)
                else:
                    shutil.move(src=child, dst=destination_path)
            if child.is_dir() and deep.get() == 1:
                self.cleanup(child, destination_root, deep, dated, shortcut, only_view)
        if shortcut.get() == 1:
            short = destination_root.stem
            self.create_shortcut(watch_path, str(destination_root), name=short)

            short = watch_path.stem
            self.create_shortcut(destination_root, str(watch_path), name=short)

    def undo_help(self, path: Path):
        for child in path.iterdir():
            if child.is_file():
                shutil.move(src=child, dst=self.watch)
            if child.is_dir():
                self.undo_help(child)

    def undo(self, path: Path, only_view):
        if only_view.get() != 1:
            self.undo_help(path)
        shutil.rmtree(self.destination)

    def create_shortcut(self, path, target='', name='shortcut'):
        link_filepath = os.path.join(path, name)
        link_filepath += '.lnk'
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(link_filepath)
        shortcut.Targetpath = target
        shortcut.save()

    def edit_ext_dir_name(self, extension, dir_name):
        self.extensions_paths[extension] = dir_name
        self.save_extensions()

    def delete_ext(self, extension):
        self.extensions_paths.pop(extension)
        self.save_extensions()


if __name__ == "__main__":
    model = Model()
