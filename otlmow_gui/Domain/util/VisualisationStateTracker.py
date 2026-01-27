from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.util.Helpers import Helpers


class VisualisationStateTracker:

    def __init__(self):
        super().__init__()

        self.relations_to_be_inserted: list[RelatieObject] =  []
        self.relations_to_be_removed: list[RelatieObject] = []
        self.clear_all: bool = False

    def insert_relation(self,relation_object:RelatieObject) -> None:
        indexes_list = []
        for i,relation_to_remove in enumerate(self.relations_to_be_removed):
            if Helpers.compare_RelatieObjects(relation_to_remove,relation_object):
                indexes_list.append(i)

        if indexes_list:
            OTLLogger.logger.debug("cancel insert_relation " + str(indexes_list))
            for i in indexes_list:
                # if this relation has been removed before updating the visual
                self.relations_to_be_removed.pop(i)
        else:
            self.relations_to_be_inserted.append(relation_object)

    def remove_relation(self, relation_object: RelatieObject) -> None:

        indexes_list = []
        for i, relation_to_add in enumerate(self.relations_to_be_inserted):
            if Helpers.compare_RelatieObjects(relation_to_add, relation_object):
                indexes_list.append(i)

        if indexes_list:
            OTLLogger.logger.debug("cancel remove_relation " + str(indexes_list))
            for i in indexes_list:
                # if this relation has been added before updating the visual
                self.relations_to_be_inserted.pop(i)
        else:
            self.relations_to_be_removed.append(relation_object)

    def reset_relations_uptodate(self) -> None:
        self.relations_to_be_inserted.clear()
        self.relations_to_be_removed.clear()

    def reset_full_state(self) -> None:
        self.reset_relations_uptodate()
        self.set_clear_all(False)

    def is_uptodate(self) -> bool:
        return (len(self.relations_to_be_inserted) == 0 and
                len(self.relations_to_be_removed) == 0 and
                not self.clear_all)

    def get_clear_all(self) -> bool:
        return self.clear_all

    def set_clear_all(self,clear_all:bool) -> None:
        self.clear_all = clear_all

    def get_to_be_inserted_relations(self) -> list[RelatieObject]:
        OTLLogger.logger.debug("self.relations_to_be_inserted " + str(self.relations_to_be_inserted))
        return self.relations_to_be_inserted

    def get_to_be_removed_relations(self) -> list[RelatieObject]:
        OTLLogger.logger.debug(
            "self.relations_to_be_removed " + str(self.relations_to_be_removed))
        return self.relations_to_be_removed