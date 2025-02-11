import csv
import sqlite3
from pathlib import Path

import otlmow_converter.OtlmowConverter
from urllib3.util.proxy import connection_requires_http_tunnel

from Domain.Helpers import Helpers
from Domain.logger.OTLLogger import OTLLogger
from Exceptions.NotASqlliteFileError import NotASqlliteFileError

OTLLogger.init()

csv_path_str = "C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\FDO_tooblox_csv_to_SDF\\created-wegkantkast-3-2OTL_Wegkantkast.csv"
sqlite_path_str = "C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\FDO_tooblox_csv_to_SDF\\created_wegkantkast_from_csv_data.db"

with open(csv_path_str) as f:
    text = f.read()

# print(text)
#
# csv_reader = csv.reader(text)
#
# for row in csv_reader:
#     print(row)

assets, exceptions_group = Helpers.converter_from_file_to_object( Path(csv_path_str),
                                                            include_tab_info=True,
                                                            delimiter=",")
print(assets)


dict_iterator =  otlmow_converter.OtlmowConverter.OtlmowConverter.from_objects_to_dotnotation_dicts(assets)

for object_dict in dict_iterator:
    print(object_dict)

table_name = "OTL_wegkantkast"

try:
    connection = sqlite3.connect(sqlite_path_str )
    cursor = connection.cursor()
    for object_dict in dict_iterator:
        print(object_dict)
        placeholders = ', '.join(['?'] * len(object_dict))
        columns_str = ', '.join(f'"{col}"' for col in object_dict.keys())
        sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})'

        # Execute the statement
        cursor.execute(sql, tuple(object_dict.values()))

    # Commit changes and close the connection
    connection.commit()

    connection.close()
except sqlite3.OperationalError as e:
    OTLLogger.logger.error(e)
    raise NotASqlliteFileError(e)



