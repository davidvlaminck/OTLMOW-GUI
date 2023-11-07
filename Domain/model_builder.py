from pathlib import Path

from otlmow_modelbuilder.OSLOCollector import OSLOCollector


class ModelBuilder:

    def __init__(self, path):
        self.collector = OSLOCollector(Path(path))
        self.collector.collect_all()

    def get_all_classes(self):
        return self.collector.classes

    def filter_abstracts(self):
        return [x for x in self.get_all_classes() if x.abstract == 0]


if __name__ == '__main__':
    builder = ModelBuilder(path='C:/#schoolwerk/Jaar III/Stage/testDb/FlitspaalTest.db')
    test = builder.filter_abstracts()
    for i in test:
        print(i)
