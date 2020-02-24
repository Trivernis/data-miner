import os
from os import path
import zipfile
import tempfile
import warnings

warnings.filterwarnings('ignore', module='zipfile')


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

    def get_file(self, directory, name, mode='w'):
        """
        Opens a new file with the given name in the directory
        :param mode:
        :param directory:
        :param name:
        :return:
        """
        if self.compress:
            f_name = path.join(self._tmpdir, name)
            if mode != 'w':
                z_name = path.join(self._data_dir, directory + '.zip')
                with get_zip(z_name) as zf:
                    if name in zf.namelist():
                        zf.extract(name, self._tmpdir)
                    zf.close()
            return open(f_name, mode)
        else:
            return open(path.join(self._data_dir, directory, name), mode)

    def store_file(self, directory, name):
        """
        Adds the file to the tarfile if compression is active.
        :param directory:
        :param name:
        :return:
        """
        if self.compress:
            z_name = path.join(self._data_dir, directory + '.zip')
            with get_zip(z_name) as zf:
                f_path = path.join(self._tmpdir, name)
                zf.write(f_path, name)
                zf.close()
                os.remove(f_path)

    @property
    def data_dir(self):
        return self._data_dir


def get_zip(name):
    mode = 'w'
    if path.exists(name):
        mode = 'a'
    return zipfile.ZipFile(name, mode, compression=zipfile.ZIP_DEFLATED)
