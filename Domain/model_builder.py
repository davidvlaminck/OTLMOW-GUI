from pathlib import Path

from otlmow_modelbuilder.OSLOCollector import OSLOCollector


class ModelBuilder:

    def __init__(self, path):
        self.collector = OSLOCollector(Path(path))
        self.collector.collect_all()

    def get_all_classes(self):
        return self.collector.classes


if __name__ == '__main__':
    builder = ModelBuilder(path='C:/#schoolwerk/Jaar III/Stage/testDb/FlitspaalTest.db')
    test = builder.get_all_classes()
    for i in test:
        print(i.name)
