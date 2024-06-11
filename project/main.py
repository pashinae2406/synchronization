from loader import CloudService
from loguru import logger
from dotenv import dotenv_values
from datetime import datetime
import time


if __name__ == "__main__":
    config = dotenv_values()
    logger.add(config.get("PATH_LOGFILE"), format='{message}')
    cloud = CloudService(oauth_token=config.get("OAUTH_TOKEN"),
                         path_logfile=config.get("PATH_LOGFILE"),
                         path_synchronization_folder=config.get("PATH_SYNCHRONIZATION_FOLDER"),
                         synchronization_period=config.get("SYNCHRONIZATION_PERIOD"),
                         name_yandex_folder=config.get("NAME_YANDEX_FOLDER"))

    while True:
        time.sleep(int(cloud.synchronization_period))
        cloud.main()
        print(datetime.now())
