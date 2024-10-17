
class ExcelFileUnavailableError(Exception):
    def __init__(self,file_path:str, exception: Exception,*args):
        super().__init__(exception,*args)
        self.error_window_message_key = "permission_to_file_was_denied_likely_due_to_the_file_being_open_in_excel"
        self.error_window_title_key = "permission_denied"
        self.file_path = file_path