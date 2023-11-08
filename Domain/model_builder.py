from pathlib import Path

from otlmow_modelbuilder.OSLOCollector import OSLOCollector

from Domain.subset_db import SubsetDatabase


class ModelBuilder:

    def __init__(self, path):
        self.collector = OSLOCollector(Path(path))
        self.subset_db = SubsetDatabase(Path(path))
        self.collector.collect_all()

    def get_all_classes(self):
        return self.collector.classes

    @staticmethod
    def filter_abstracts(list_of_classes):
        return [x for x in list_of_classes if x.abstract == 0]

    def filter_relations(self):
        relations = self.collector.relations
        uri = [y.objectUri for y in relations]
        return [x for x in self.get_all_classes() if x.objectUri not in uri]

    def filter_functionality(self):
        step1 = self.filter_relations()
        step2 = self.filter_abstracts(step1)
        return step2

    def get_name_project(self):
        info = dict(self.subset_db.get_general_info_project())
        return info.get('Naam')

    def close_subset_db(self):
        self.subset_db.close_connection()