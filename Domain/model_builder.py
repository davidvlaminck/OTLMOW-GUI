from pathlib import Path

from otlmow_modelbuilder.OSLOInMemoryCreator import OSLOInMemoryCreator
from otlmow_modelbuilder.SQLDataClasses.OSLOCollector import OSLOCollector
from otlmow_modelbuilder.SQLDbReader import SQLDbReader


class ModelBuilder:

    def __init__(self, path):
        file_location = Path(path)
        sql_reader = SQLDbReader(file_location)
        self.creator = OSLOInMemoryCreator(sql_reader)
        collector = OSLOCollector(self.creator)
        collector.collect()

    def get_all_classes(self):
        return self.creator.get_all_classes()


if __name__ == '__main__':
    creator = ModelBuilder(path='C:/#schoolwerk/Jaar III/Stage/testDb/FlitspaalTest.db')
    test = ModelBuilder.get_all_classes(creator)
    for i in test:
        print(i)
