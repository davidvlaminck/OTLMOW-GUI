
class ProjectExistsError(FileExistsError):
    def __init__(self, *args , eigen_referentie:str):
        super().__init__(*args)
        self.eigen_referentie = eigen_referentie