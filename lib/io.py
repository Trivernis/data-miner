import os
from os import path
import zipfile
import tempfile


class FileManager:

    def __init__(self, data_dir, directories: [str], compress=False, tmp='.tmp'):
        self._dirs = directories
        self.compress = compress
        self._data_dir = data_dir
        self._zips = {}
        self._tmpdir = tempfile.gettempdir()
        if not compress:
            self._open_directories()

    def _open_directories(self):
        for d in self._dirs:
            if not path.exists(path.join(self._data_dir, d)):
                os.mkdir(path.join(self._data_dir, d))

    def get_file(self, directory, name):
        """
        Opens a new file with the given name in the directory
        :param directory:
        :param name:
        :return:
        """
        if self.compress:
            return open(path.join(self._tmpdir, name), 'w')
        else:
            return open(path.join(self._data_dir, directory, name), 'w')

    def store_file(self, directory, name):
        """
        Adds the file to the tarfile if compression is active.
        :param directory:
        :param name:
        :return:
        """
        if self.compress:
            mode = 'w'
            z_name = path.join(self._data_dir, directory + '.zip')
            if path.exists(z_name):
                mode = 'a'
            with zipfile.ZipFile(z_name, mode, compression=zipfile.ZIP_LZMA) as zf:
                f_path = path.join(self._tmpdir, name)
                zf.write(f_path, name)
                zf.close()
                os.remove(f_path)
