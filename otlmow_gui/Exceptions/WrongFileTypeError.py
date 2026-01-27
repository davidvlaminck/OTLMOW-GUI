class WrongFileTypeError(Exception):

    def __init__(self, language, expected_filetype_name,expected_filetype_suffix):
        self._ = language
        self.expected_filetype_name = expected_filetype_name
        self.expected_filetype_suffix = expected_filetype_suffix

        super().__init__()


    def __str__(self):
        translation = self._("The path to the provided file is not a {0} file with extension ({1})")
        return translation.format(self.expected_filetype_name,self.expected_filetype_suffix)
