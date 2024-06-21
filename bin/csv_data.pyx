# -*- coding: utf-8 -*-
# cython:language_level=3
import json

from libc.stdio cimport FILE, fopen, fclose, fgets, printf
from libc.stdlib cimport malloc, free
from libc.string cimport strcmp, strtok, strcpy, strlen, strncpy
from libc.math cimport fabs

cdef struct Row:
    char * version
    int start_et
    int end_et
    char * job
    char * material_JP
    char * material_EN
    char * material_CN
    char * type
    char * type_CN
    int level
    char * area_JP
    char * area_EN
    char * area_CN
    char * near_crystal
    char * near_crystal_CN
    char * coords
    int image
    char * patch

cdef char * _strndup(const char * s, size_t n):
    cdef char * p = <char *> malloc(n + 1)
    if not p:
        return NULL
    strncpy(p, s, n)
    p[n] = b'\0'
    return p

ctypedef int (*compare_func)(char *, char *)

cdef int compare_floats_field(char * field, char * value):
    return fabs(float(field) - float(value)) < 1e-7

cdef int compare_floats_field_not(char * field, char * value):
    return not fabs(float(field) - float(value)) < 1e-7

cdef int compare_char_field(char * field, char * value):
    return strcmp(field, value) == 0

cdef int compare_char_field_in_list(char * field, list value):
    cdef char * item
    for item in value:
        if strcmp(field, item) == 0:
            return True
    return False

cdef int compare_int_field(char * field, char * value):
    return int(field) == int(value)

cdef int compare_ET_time_field(int start_et, int end_et, char * value):
    return start_et <= int(value) < end_et

def dict_to_tuple(d):
    return tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in sorted(d.items()))

def tuple_to_dict(t):
    return {k: list(v) if isinstance(v, tuple) else v for k, v in t}

cdef Row create_row_from_tokens(list tokens, int token_count):
    cdef Row row

    row.version = _strndup(tokens[0], strlen(tokens[0]))

    row.start_et = int(tokens[1])
    row.end_et = int(tokens[2])

    row.job = _strndup(tokens[3], strlen(tokens[3]))

    row.material_JP = _strndup(tokens[4], strlen(tokens[4]))
    row.material_EN = _strndup(tokens[5], strlen(tokens[5]))
    row.material_CN = _strndup(tokens[6], strlen(tokens[6]))

    row.type = _strndup(tokens[7], strlen(tokens[7]))
    row.type_CN = _strndup(tokens[8], strlen(tokens[8]))

    row.level = int(tokens[9])

    row.area_JP = _strndup(tokens[10], strlen(tokens[10]))
    row.area_EN = _strndup(tokens[11], strlen(tokens[11]))
    row.area_CN = _strndup(tokens[12], strlen(tokens[12]))

    row.near_crystal = _strndup(tokens[13], strlen(tokens[13]))
    row.near_crystal_CN = _strndup(tokens[14], strlen(tokens[14]))

    row.coords = _strndup(tokens[15], strlen(tokens[15]))

    row.image = int(tokens[16])
    row.patch = _strndup(tokens[17], strlen(tokens[17]))

    # printf("Added row: material_CN=%s, start_et=%d, end_et=%d\n", row.material_CN, row.start_et, row.end_et)

    return row

cdef list parse_csv_line(char * line):
    cdef list tokens = []
    cdef int start, end, in_quotes, length
    cdef char ch

    length = strlen(line)
    while length > 0 and (line[length - 1] == b'\n' or line[length - 1] == b'\r' or line[length - 1] == b' '):
        length -= 1

    start = 0
    in_quotes = 0
    for end in range(length):
        ch = line[end]
        if ch == b'"':
            in_quotes = not in_quotes
        elif ch == b',' and not in_quotes:
            tokens.append(_strndup(line + start, end - start))
            start = end + 1
    tokens.append(_strndup(line + start, length - start))
    return tokens

def load_csv(char * filename):
    cdef FILE * file = fopen(filename, "r")
    cdef char line[1024]
    cdef list tokens
    cdef list rows = []
    cdef int token_count

    if not file:
        raise FileNotFoundError(f"Cannot open file: {filename}")

    fgets(line, sizeof(line), file)

    while fgets(line, sizeof(line), file):
        tokens = parse_csv_line(line)
        token_count = len(tokens)
        row = create_row_from_tokens(tokens, token_count)
        rows.append(row)

    fclose(file)
    return rows

def filter_data(rows, all_filter_dict: list[tuple[str, str | int | float | list]]) -> list | None:
    result_set_list = []
    for i in all_filter_dict:
        filter_name = i[0]
        filter_value = i[1]
        if isinstance(filter_value, str):
            _filter_value = filter_value.encode('utf-8')
        elif isinstance(filter_value, int) or isinstance(filter_value, float):
            _filter_value = str(filter_value).encode('utf-8')
        elif isinstance(filter_value, list):
            _filter_value = b'|'.join([str(val).encode('utf-8') for val in filter_value])
        else:
            raise ValueError("Unsupported filter_value type")
        result_set_list.append(filter_data_func(rows, filter_name.encode('utf-8'), _filter_value))
        result = list(set.intersection(*result_set_list))
    return result

def set_to_dict(result_set_list: list) -> list:
    if not result_set_list:
        return []
    else:
        result: list = [tuple_to_dict(i) for i in result_set_list]
        for i in result:
            i['version'] = i['version'].decode('utf-8')
            i['job'] = i['job'].decode('utf-8')
            i['material_JP'] = i['material_JP'].decode('utf-8')
            i['material_EN'] = i['material_EN'].decode('utf-8')
            i['material_CN'] = i['material_CN'].decode('utf-8')
            i['type'] = i['type'].decode('utf-8')
            i['type_CN'] = i['type_CN'].decode('utf-8')
            i['area_JP'] = i['area_JP'].decode('utf-8')
            i['area_EN'] = i['area_EN'].decode('utf-8')
            i['area_CN'] = i['area_CN'].decode('utf-8')
            i['near_crystal'] = i['near_crystal'].decode('utf-8')
            i['near_crystal_CN'] = i['near_crystal_CN'].decode('utf-8')
            i['coords'] = json.loads(json.loads(i['coords'].decode('utf-8')))
            i['patch'] = float(i['patch'].decode('utf-8'))
        result.sort(key=lambda x: x['level'], reverse=True)
        return result

cdef compare_func get_comparator(char * filter_name):
    if strcmp(filter_name, b'version') == 0:
        return compare_char_field
    elif strcmp(filter_name, b'job') == 0:
        return compare_char_field
    elif strcmp(filter_name, b'!name') == 0:
        return compare_char_field
    elif strcmp(filter_name, b'name') == 0:
        return compare_char_field
    elif strcmp(filter_name, b'type') == 0:
        return compare_char_field
    elif strcmp(filter_name, b'in_type') == 0:
        return compare_char_field
    elif strcmp(filter_name, b'!type') == 0:
        return compare_char_field
    elif strcmp(filter_name, b'level') == 0:
        return compare_int_field
    elif strcmp(filter_name, b'patch') == 0:
        return compare_floats_field
    elif strcmp(filter_name, b'!patch') == 0:
        return compare_floats_field_not
    else:
        return NULL
def filter_data_func(rows, char * filter_name, char * filter_value):
    cdef set filtered_data = set()
    cdef Row row
    cdef char * field
    cdef compare_func comparator

    comparator = get_comparator(filter_name)
    if comparator is NULL and filter_name != b'ET_time':
        raise ValueError(f"Unknown filter name: {filter_name}")

    for row in rows:
        if filter_name == b'ET_time':
            if compare_ET_time_field(row.start_et, row.end_et, filter_value):
                filtered_data.add(dict_to_tuple(row))
        elif filter_name == b'version':
            field = row.version
            if comparator(field, filter_value):
                filtered_data.add(dict_to_tuple(row))
        elif filter_name == b'job':
            field = row.job
            if comparator(field, filter_value):
                filtered_data.add(dict_to_tuple(row))
        elif filter_name == b'name':
            field_list = [row.material_JP, row.material_EN, row.material_CN]
            filter_value_list = filter_value.split(b'|')
            for field in field_list:
                if field in filter_value_list:
                    filtered_data.add(dict_to_tuple(row))
                    break
        elif filter_name == b'!name':
            field_list = [row.material_JP, row.material_EN, row.material_CN]
            filter_value_list = filter_value.split(b'|')
            for field in field_list:
                if field in filter_value_list:
                    break
            else:
                filtered_data.add(dict_to_tuple(row))
        elif filter_name == b'type':
            field = row.type
            if filter_value in field:
                filtered_data.add(dict_to_tuple(row))
        elif filter_name == b'in_type':
            field = row.type
            filter_value_list = filter_value.split(b'|')
            if field in filter_value_list:
                filtered_data.add(dict_to_tuple(row))
        elif filter_name == b'!type':
            field = row.type
            filter_value_list = filter_value.split(b'|')
            if field not in filter_value_list:
                filtered_data.add(dict_to_tuple(row))
        elif filter_name == b'level':
            filter_value_list = filter_value.split(b'|')
            if int(filter_value_list[1]) >= row.level >= int(filter_value_list[0]):
                filtered_data.add(dict_to_tuple(row))
        elif filter_name == b'patch':
            field = row.patch
            filter_value_list = filter_value.split(b'|')
            if field in filter_value_list:
                filtered_data.add(dict_to_tuple(row))
            continue
        elif filter_name == b'!patch':
            field = row.patch
            if comparator(field, filter_value):
                filtered_data.add(dict_to_tuple(row))
        else:
            raise ValueError(f"Unknown filter name: {filter_name}")

    return filtered_data
