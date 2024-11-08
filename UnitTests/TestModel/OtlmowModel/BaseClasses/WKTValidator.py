from typing import List


class WKTValidator:
    coord_params = {
        'POINT': {'level': 1, 'min': 1, 'len_point': 2},
        'POINT Z': {'level': 1, 'min': 1, 'len_point': 3},
        'LINESTRING': {'level': 1, 'min': 2, 'len_point': 2},
        'LINESTRING Z': {'level': 1, 'min': 2, 'len_point': 3},
        'POLYGON': {'level': 2, 'min': 3, 'len_point': 2},
        'POLYGON Z': {'level': 2, 'min': 3, 'len_point': 3},
        'MULTIPOINT': {'level': 2, 'min': 1, 'len_point': 2},
        'MULTIPOINT Z': {'level': 2, 'min': 1, 'len_point': 3},
        'MULTILINESTRING': {'level': 2, 'min': 2, 'len_point': 2},
        'MULTILINESTRING Z': {'level': 2, 'min': 2, 'len_point': 3},
        'MULTIPOLYGON': {'level': 3, 'min': 3, 'len_point': 2},
        'MULTIPOLYGON Z': {'level': 3, 'min': 3, 'len_point': 3},
        'GEOMETRYCOLLECTION': 0
    }

    @classmethod
    def split_and_add_to_list(cls, coords_list: list, coords_str: str):
        if coords_str.startswith('('):
            coords_str = coords_str[1:-1]
            for new_coords_str in coords_str.split('),('):
                new_list = []
                cls.split_and_add_to_list(coords_list=new_list, coords_str=new_coords_str)
                coords_list.append(new_list)
        else:
            for c in coords_str.split(','):
                x_y_z = tuple(float(co) for co in c.strip().split(' '))
                coords_list.append(x_y_z)

    @classmethod
    def validate_wkt(cls, input_string: str) -> bool:
        if '(' not in input_string or ')' not in input_string:
            return False
        input_string = input_string.upper()
        geo_type = input_string.split(' (')[0]

        if geo_type not in (
                'POINT', 'POINT Z', 'LINESTRING', 'LINESTRING Z', 'POLYGON', 'POLYGON Z', 'MULTIPOINT', 'MULTIPOINT Z',
                'MULTILINESTRING', 'MULTILINESTRING Z', 'MULTIPOLYGON', 'MULTIPOLYGON Z', 'GEOMETRYCOLLECTION'):
            return False

        coords_list = cls.get_coords_list_from_wkt_string(input_string)

        level = cls.coord_params[geo_type]['level']
        if level == 1 and not isinstance(coords_list[0], tuple):
            return False
        elif level == 2 and not isinstance(coords_list[0][0], tuple):
            return False
        elif level == 3 and not isinstance(coords_list[0][0][0], tuple):
            return False
        # TODO: if level == 0

        if level == 1:
            return cls.validate_coords_list(coords_list, geo_type)
        elif level == 2:
            return all(
                cls.validate_coords_list(coords, geo_type)
                for coords in coords_list
            )
        elif level == 3:
            for coords in coords_list:
                for coords2 in coords:
                    if not cls.validate_coords_list(coords2, geo_type):
                        return False
            return True

    @classmethod
    def get_coords_list_from_wkt_string(cls, input_string) -> List:
        coords_string = input_string.split(' (')[1][:-1].replace(', ', ',').replace(' ,', ',')
        coords_list = []
        cls.split_and_add_to_list(coords_list, coords_string)
        return coords_list

    @classmethod
    def validate_coords_list(cls, coords_list, geo_type):
        len_point = cls.coord_params[geo_type]['len_point']
        min_point = cls.coord_params[geo_type]['min']

        if len(coords_list) < min_point:
            return False

        for point in coords_list:
            if geo_type.endswith(' Z') and len(point) != len_point:
                return False
            if not geo_type.endswith(' Z') and len(point) != len_point:
                return False

            val_0 = point[0]
            if val_0 < 14637.2 or val_0 > 291015.3:
                return False
            val_1 = point[1]
            if val_1 < 22608.2 or val_1 > 246424.3:
                return False
            if len_point == 3 and point[2] > 700:
                return False

        return True
