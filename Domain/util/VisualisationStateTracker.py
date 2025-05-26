from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject


class VisualisationStateTracker:

    def __init__(self):
        super().__init__()

        self.relations_to_be_inserted: list[RelatieObject] =  []
        self.relations_to_be_removed: list[RelatieObject] = []
        self.clear_all: bool = False

    def insert_relation(self,relation_object:RelatieObject) -> None:

        if relation_object in self.relations_to_be_removed:
            # if this relation has been removed before updating the visual
            self.relations_to_be_removed.remove(relation_object)
        else:
            self.relations_to_be_inserted.append(relation_object)

    def remove_relation(self, relation_object: RelatieObject) -> None:

        if relation_object in self.relations_to_be_inserted:
            # if this relation has been added before updating the visual
            self.relations_to_be_inserted.remove(relation_object)
        else:
            self.relations_to_be_removed.append(relation_object)

    def reset_relations_uptodate(self) -> None:
        self.relations_to_be_inserted.clear()
        self.relations_to_be_removed.clear()

    def reset_full_state(self) -> None:
        self.reset_relations_uptodate()
        self.clear_all = True

    def is_uptodate(self) -> bool:
        return (len(self.relations_to_be_inserted) == 0 and
                len(self.relations_to_be_removed) == 0 and
                not self.clear_all)

    def get_clear_all(self) -> bool:
        return self.clear_all

    def set_clear_all(self,clear_all:bool) -> None:
        self.clear_all = clear_all

    def get_to_be_inserted_relations(self) -> list[RelatieObject]:
        return self.relations_to_be_inserted

    def get_to_be_removed_relations(self) -> list[RelatieObject]:
        return self.relations_to_be_removed