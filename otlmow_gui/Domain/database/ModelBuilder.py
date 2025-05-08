from pathlib import Path

from otlmow_modelbuilder.OSLOCollector import OSLOCollector

from otlmow_gui.Domain.database.SubsetDatabase import SubsetDatabase


class ModelBuilder:

    def __init__(self, path):
        self.collector = OSLOCollector(Path(path))
        self.subset_db = SubsetDatabase(Path(path))
        self.info_dict = dict(self.subset_db.get_general_info_project())
        if self.subset_db.is_valid_subset_database():
            self.collector.collect_all()
        self.close_subset_db()

    def get_all_classes(self):
        return self.collector.classes

    def filter_relations_and_abstract(self):
        relations = self.collector.relations
        relations_uri = {y.objectUri for y in relations}
        classes = self.get_all_classes()
        return [x for x in classes if x.abstract == 0 and x.objectUri not in relations_uri]

    def get_name_project(self):
        return self.info_dict.get('Naam')

    def get_operator_name(self):
        return self.info_dict.get('Operator')

    def get_otl_version(self):
        if 'BronVersie' in self.info_dict:
            # Subsets have a 'BronVersie' field to indicate the OTL version
            return self.info_dict.get('BronVersie')
        else:
            # Full OTL-model SQLite files have a 'Version' field to indicate the OTL version
            return self.info_dict.get('Version')

    def close_subset_db(self):
        self.subset_db.close_connection()
