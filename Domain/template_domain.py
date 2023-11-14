import logging


class TemplateDomain:

    @staticmethod
    def check_for_no_deprecated_present(values):
        logging.debug(values)
        for value in values:
            if len(value.deprecated_version) != 0:
                return False
        return True
