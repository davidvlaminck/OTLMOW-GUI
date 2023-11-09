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

    def filter_relations_and_abstract(self):
        relations = self.collector.relations
        relations_uri = {y.objectUri for y in relations}
        classes = self.get_all_classes()
        return [x for x in classes if x.abstract == 0 and x.objectUri not in relations_uri]

    def get_name_project(self):
        info = dict(self.subset_db.get_general_info_project())
        return info.get('Naam')

    def close_subset_db(self):
        self.subset_db.close_connection()
