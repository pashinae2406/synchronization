import requests
from requests import Response
from datetime import datetime, timedelta
import os
from methods import load, reload, delete, get_info, create_folder
from loguru import logger


class CloudService:

    def __init__(self, oauth_token,
                 path_logfile,
                 path_synchronization_folder,
                 synchronization_period,
                 name_yandex_folder):
        self.oauth_token = oauth_token
        self.path_logfile = path_logfile
        self.path_synchronization_folder = path_synchronization_folder
        self.synchronization_period = synchronization_period
        self.name_yandex_folder = name_yandex_folder

    @logger.catch()
    def main(self) -> None:
        headers: dict = {'Content-Type': 'application/json; charset=utf-8',
                         'Accept': 'application/json',
                         'Authorization': f'OAuth {self.oauth_token}'}
        url_disk: str = 'https://cloud-api.yandex.net/v1/disk/resources'
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        url_folder: str = os.path.abspath(os.path.join("..", "..", "..", "Documents", "скиллбокс", self.path_synchronization_folder))
        files_dir: list = os.listdir(url_folder)
        files_synchronization: dict = {f"{file}": datetime.fromtimestamp(os.path.getmtime(os.path.join(url_folder, file)))
                                       for file in files_dir}
        files_disk_url: Response = requests.get(f'{url_disk}?path=%2F{self.name_yandex_folder}', headers=headers)

        if files_disk_url.status_code != 200:
            create_folder(path_disk=url_disk,
                          name_dir_disk=self.name_yandex_folder,
                          headers=headers)
        else:
            files_dir_disk: dict = {
                f"{file['name']}": datetime.strptime(f"{file['modified'][:10]} {file['modified'][11:19]}.000000",
                                                     "%Y-%m-%d %H:%M:%S.%f")
                for file in files_disk_url.json()["_embedded"]["items"]}
            change: bool = False
            for i in files_dir:
                if not i in files_dir_disk.keys():
                    print("Файл для загрузки: ", i)
                    load(path_disk=url_disk,
                         name_dir_disk=self.name_yandex_folder,
                         filename=i,
                         path_folder=url_folder,
                         headers=headers)
                    change = True
            for key, value in files_dir_disk.items():
                if not key in files_synchronization.keys():
                    print("Файл для удаления: ", key)
                    delete(filename=key,
                           name_dir_disk=self.name_yandex_folder,
                           path_disk=url_disk,
                           headers=headers)
                    change = True
                else:
                    if (value + timedelta(hours=3)) < files_synchronization[key]:
                        print(value, files_synchronization[key])
                        print("Файл для перезаписи: ", key)
                        reload(path_disk=url_disk,
                               name_dir_disk=self.name_yandex_folder,
                               filename=key,
                               path_folder=url_folder,
                               headers=headers)
                        change = True
                        print("На компьютере: ", key, files_synchronization[key], "На диске: ", files_dir_disk[key])
            if change == True:
                get_info(path_disk=url_disk,
                         name_dir_disk=self.name_yandex_folder,
                         headers=headers)
