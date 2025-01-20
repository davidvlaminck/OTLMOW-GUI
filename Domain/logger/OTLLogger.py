import datetime
import logging
import os
from pathlib import Path

from Domain.project.ProgramFileStructure import ProgramFileStructure


class OTLLogger:

    @classmethod
    def init(cls):
        logging_file = cls.create_logging_file()
        cls.remove_old_logging_files()

        file_handler = logging.FileHandler(logging_file)
        file_handler.setLevel(logging.DEBUG)

        logger = logging.getLogger()
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        # logger.propagate = False #turns logging off
        logger.handlers[0].setFormatter(logging.Formatter(fmt='%(asctime)s ln %(lineno)-4d:%(filename)-25s %(levelname)-8s %(message)s',
             datefmt='%Y-%m-%d %H:%M:%S'))

    @classmethod
    def create_logging_file(cls) -> Path:
        """
                    what is this doing here?
                """
        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir() / 'logs'
        if not work_dir_path.exists():
            work_dir_path.mkdir()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        logging_filepath = work_dir_path / f'logging_{timestamp}.log'
        if not logging_filepath.exists():
            open(Path(logging_filepath), 'w').close()
        return logging_filepath

    @classmethod
    def remove_old_logging_files(cls) -> None:

        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir() / 'logs'
        for file in os.listdir(work_dir_path):
            file_name = Path(file).stem
            split_file = file_name.split('_')

            date_str = str(split_file[-1])
            logging.debug(f"split file date {date_str}")
            datetime_obj = datetime.datetime.strptime(split_file[-1], "%Y%m%d%H%M%S")
            if datetime_obj < datetime.datetime.now() - datetime.timedelta(days=7):
                os.remove(work_dir_path / file)
