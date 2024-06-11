import os
import requests
from requests import Response
from datetime import datetime, timedelta
from loguru import logger


def create_folder(path_disk: str, name_dir_disk: str, headers: dict) -> None:
    """Функция создания папки синхронизации на яндекс диске"""
    try:
        res: Response = requests.put(f"{path_disk}?path=%2F{name_dir_disk}", headers=headers)
        print(res.status_code)
        message: str = f"Создана папка {name_dir_disk} на диске"
    except:
        message: str = "Что-то пошло не так. Ошибка соединения"
    logger.info(message)


def load(path_disk: str, name_dir_disk: str, filename: str, path_folder: str, headers: dict) -> None:
    """Метод для загрузки файла в хранилище"""

    res: dict = requests.get(f'{path_disk}/upload?path={name_dir_disk}/{filename}', headers=headers).json()
    message: str = ""
    with open(os.path.join(path_folder, filename), 'rb') as f:
        try:
            response: Response = requests.put(res['href'], files={'file': f})
            if response.status_code == 201:
                message = f"{name_dir_disk} {datetime.now()} INFO Файл {filename} успешно записан."
            else:
                message = f"{name_dir_disk} {datetime.now()} ERROR Файл {filename} не записан. Ошибка соединения"
        except KeyError:
            message = f"{name_dir_disk} {datetime.now()} ERROR Файл {filename} не записан. Ошибка соединения"
        logger.info(message)


def delete(filename: str, name_dir_disk: str, path_disk: str, headers: dict) -> None:
    """Метод для удаления файла из хранилища"""

    res: Response = requests.get(f'{path_disk}?path={name_dir_disk}/{filename}', headers=headers)
    message: str = ""
    try:
        response: Response = requests.delete(res.url, headers=headers, params={"name": filename})
        if response.status_code == 204:
            message = f"{name_dir_disk} {datetime.now()} INFO Файл {filename} успешно удален."
        else:
            message = f"{name_dir_disk} {datetime.now()} ERROR Файл {filename} не удален. Ошибка соединения"
    except KeyError:
        message = f"{name_dir_disk} {datetime.now()} ERROR Файл {filename} не удален. Ошибка соединения"
    logger.info(message)


def reload(path_disk: str, name_dir_disk: str, filename: str, path_folder: str, headers: dict) -> None:
    """Метод для перезаписи файла в хранилище"""

    res: Response = requests.get(f'{path_disk}?path={name_dir_disk}/{filename}', headers=headers)
    message: str = ""
    try:
        response: Response = requests.delete(res.url, headers=headers, params={"name": filename})
        if response.status_code == 204:
            res: dict = requests.get(f'{path_disk}/upload?path={name_dir_disk}/{filename}', headers=headers).json()
            try:
                with open(os.path.join(path_folder, filename), 'rb') as f:
                    response: Response = requests.put(res["href"], files={'file': f})
                    if response.status_code == 201:
                        message = f"{name_dir_disk} {datetime.now()} INFO Файл {filename} успешно перезаписан."
                    else:
                        message = f"{name_dir_disk} {datetime.now()} ERROR Файл {filename} не перезаписан. Ошибка соединения"
            except KeyError:
                message = f"{name_dir_disk} {datetime.now()} ERROR Файл {filename} не перезаписан. Ошибка соединения"
    except KeyError:
        message = f"{name_dir_disk} {datetime.now()} ERROR Файл {filename} не перезаписан. Ошибка соединения"
    logger.info(message)


def get_info(path_disk: str, name_dir_disk: str, headers: dict):
    """Метод для получения информации о хранящихся в удалённом хранилище файлах"""

    message: str = f"На Яндекс диске в папке {name_dir_disk} хранятся следующие файлы:\n"
    res: dict = requests.get(f'{path_disk}?path={name_dir_disk}', headers=headers).json()
    for i in res["_embedded"]["items"]:
        date: datetime = datetime.strptime(f"{i['modified'][:10]} {i['modified'][11:19]}.000000",
                                                 "%Y-%m-%d %H:%M:%S.%f") + timedelta(hours=3)
        message += f"Имя файла: {i['name']}, дата изменения: {date}\n"
    logger.info(message)