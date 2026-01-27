import datetime
import logging
import os
import traceback
import warnings

from pathlib import Path

from otlmow_gui.Domain.ProgramFileStructure import ProgramFileStructure


class OTLLogger(logging.Logger):

    logger = None
    ref_key_to_time_dict = {}
    loading_window = None


    def __init__(self, name, level=0):
        super().__init__(name, level)

    @classmethod
    def init(cls):
        cls.logger = cls(__name__)

        logging_file = cls.create_logging_file()
        cls.remove_old_logging_files()

        file_handler = logging.FileHandler(logging_file) # logger will write to file
        stderr_handler = logging.StreamHandler() # logger will write to stderr
        #
        cls.logger.addHandler(stderr_handler)
        cls.logger.addHandler(file_handler)

        logging.getLogger().addHandler(stderr_handler)
        logging.getLogger().addHandler(file_handler) # loggers from other libraries will write to file

        # cls.logger = logging.getLogger()
        cls.logger.setLevel(logging.DEBUG)

        # Warning are written to console and to file
        # Function to redirect warnings to the logger
        def log_runtime_warnings(message, category, filename, lineno, file=None, line=None):
            cls.logger.warning(f"{category.__name__}: {message} (File: {filename}, Line: {lineno})")
        # Redirect warnings to logger
        warnings.showwarning = log_runtime_warnings

        for handler in cls.logger.handlers:
            handler.setFormatter(logging.Formatter(
                fmt='%(asctime)s %(message)s',
                                   datefmt='%Y-%m-%d %H:%M:%S'))

    @classmethod
    def create_logging_file(cls) -> Path:

        work_dir_path = ProgramFileStructure.get_otl_wizard_work_dir() / 'logs'
        if not work_dir_path.exists():
            work_dir_path.mkdir()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        logging_filepath = work_dir_path / f'OTL_wizard_2_{timestamp}.log'
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
            # cls.logger.debug(f"split file date {date_str}")
            datetime_obj = datetime.datetime.strptime(split_file[-1], "%Y%m%d%H%M%S")
            if datetime_obj < datetime.datetime.now() - datetime.timedelta(days=7):
                os.remove(work_dir_path / file)

    def _alter_msg(self,msg,extra):

        ref_key = None
        if extra and "timing_ref" in extra :
            ref_key = extra["timing_ref"]

        if not  ref_key:
            # return "{status:5s}({time:07.3f}s) {msg}".format(status="", time=0,msg=msg)
            return msg

        current_time = datetime.datetime.now()
        if ref_key and ref_key in OTLLogger.ref_key_to_time_dict:
            ref_time = OTLLogger.ref_key_to_time_dict.pop(ref_key)
            time_dif:datetime.timedelta = current_time - ref_time
            time_dif_seconds = time_dif.seconds + time_dif.microseconds/1000000
            state = "END"

            return "{msg} {status:5s} {ref} ({time:07.3f}s) ".format(status=state, time=time_dif_seconds,
                                                              ref=ref_key, msg=msg)
        else:
            state = "START"
            OTLLogger.ref_key_to_time_dict[ref_key] = current_time
            # OTLLogger.attempt_show_loading_screen(ref_key)
            time_dif_seconds = 0
            return "{msg} {status:5s} {ref}".format(status=state,
                                                              msg=msg,ref=ref_key)




    def debug(self, msg, *args, exc_info=None, stack_info=False, stacklevel=1, extra=None):

        msg = self._alter_msg(msg,extra)
        stack =traceback.extract_stack(f=None, limit=2)
        filename = Path(stack[0].filename).name
        lineno = stack[0].lineno
        levelname = "DEBUG"
        super().debug(f"ln {lineno:4d}:{filename:25s}  {levelname:8s}  {msg}" , *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                      extra=extra)

    def info(self, msg, *args, exc_info=None, stack_info=False, stacklevel=1, extra=None):
        msg = self._alter_msg(msg, extra)
        stack = traceback.extract_stack(f=None, limit=2)
        filename = Path(stack[0].filename).name
        lineno = stack[0].lineno
        levelname = "INFO"
        super().info(f"ln {lineno:4d}:{filename:25s}  {levelname:8s}  {msg}", *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                     extra=extra)

    def warning(self, msg, *args, exc_info=None, stack_info=False, stacklevel=1, extra=None):
        msg = self._alter_msg(msg, extra)
        stack = traceback.extract_stack(f=None, limit=2)
        filename = Path(stack[0].filename).name
        lineno = stack[0].lineno
        levelname = "WARN"
        super().warning(f"ln {lineno:4d}:{filename:25s}  {levelname:8s}  {msg}", *args, exc_info=exc_info, stack_info=stack_info,
                        stacklevel=stacklevel, extra=extra)

    def warn(self, msg, *args, exc_info=None, stack_info=False, stacklevel=1, extra=None):
        msg = self._alter_msg(msg, extra)
        stack = traceback.extract_stack(f=None, limit=2)
        filename = Path(stack[0].filename).name
        lineno = stack[0].lineno
        levelname = "WARN"
        super().warn(f"ln {lineno:4d}:{filename:25s}  {levelname:8s}  {msg}", *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                     extra=extra)

    def error(self, msg, *args, exc_info=None, stack_info=False, stacklevel=1, extra=None):
        msg = self._alter_msg(msg, extra)
        stack = traceback.extract_stack(f=None, limit=2)
        filename = Path(stack[0].filename).name
        lineno = stack[0].lineno
        levelname = "ERR"
        super().error(f"ln {lineno:4d}:{filename:25s}  {levelname:8s}  {msg}", *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                      extra=extra)

    def critical(self, msg, *args, exc_info=None, stack_info=False, stacklevel=1, extra=None):
        msg = self._alter_msg(msg, extra)
        stack = traceback.extract_stack(f=None, limit=2)
        filename = Path(stack[0].filename).name
        lineno = stack[0].lineno
        levelname = "CRIT"
        super().critical(f"ln {lineno:4d}:{filename:25s}  {levelname:8s}  {msg}", *args, exc_info=exc_info, stack_info=stack_info,
                         stacklevel=stacklevel, extra=extra)

    def exception(self, msg, *args, exc_info=True, stack_info=False, stacklevel=1, extra=None):
        msg = self._alter_msg(msg, extra)
        stack = traceback.extract_stack(f=None, limit=2)
        filename = Path(stack[0].filename).name
        lineno = stack[0].lineno
        levelname = "EXCE"
        super().exception(f"ln {lineno:4d}:{filename:25s}  {levelname:8s}  {msg}", *args, exc_info=exc_info, stack_info=stack_info,
                          stacklevel=stacklevel, extra=extra)


