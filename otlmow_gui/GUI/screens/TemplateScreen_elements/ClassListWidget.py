from PyQt6.QtWidgets import QListWidget

from otlmow_gui.Domain.step_domain.TemplateDomain import TemplateDomain


class ClassListWidget(QListWidget):



    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.sync_selected_items_with_backend()

    def sync_selected_items_with_backend(self):
        TemplateDomain.set_selected_indexes([item.data(1)[1] for item in self.selectedItems()])
