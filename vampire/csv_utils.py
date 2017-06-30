import csv
import os
import dbfpy.dbf
import pandas

def add_field(table_name, new_field, value, type='DATE'):
    base,ext = os.path.splitext(table_name)
    if ext == '.csv':
        _new_csv = []
        with open(table_name, 'rb') as cf:
            _reader = csv.reader(cf)
            _header_row = next(_reader)
            _header_row.append(new_field)
            for row in _reader:
                _new_row = row
                _new_row.append(value)
                print _new_row
                _new_csv.append(_new_row)
        with open(table_name, 'wb') as wf:
            wr = csv.writer(wf)
            wr.writerow(_header_row)
            wr.writerows(_new_csv)
    return None

def calc_field(table_name, new_field, cal_field, multiplier=1.0, type='DOUBLE'):
    base,ext = os.path.splitext(table_name)
    if ext == '.csv':
        _new_csv = []
        with open(table_name, 'rb') as cf:
            _reader = csv.reader(cf)
            _header_row = next(_reader)
            _header_row.append(new_field)
            # convert all to lower case for comparison
            _lower_header = [x.lower() for x in _header_row]
            _calc_index = 0
            try:
                _calc_index = _lower_header.index(cal_field.lower())
            except ValueError, e:
                print '{0} not found in file header row.'.format(cal_field)
                return None
            for row in _reader:
                _new_row = row
                if row[_calc_index] != '':
                    _val = float(row[_calc_index])
                    if type == 'LONG':
                        _new_row.append(int(_val*multiplier))
                    else:
                        _new_row.append(float(_val*multiplier))
                else:
                    _new_row.append('')
                print _new_row
                _new_csv.append(_new_row)
        with open(table_name, 'wb') as wf:
            wr = csv.writer(wf)
            wr.writerow(_header_row)
            wr.writerows(_new_csv)
    return None

def csv_to_choropleth_format(input_filename, output_filename, area_field, value_field, start_date_field, end_date_field):
    _new_csv = []
    with open(input_filename, 'rb') as cf:
        _reader = csv.reader(cf)
        _header_row = next(_reader)
        _new_header_row = ['area_id', 'value', 'start_date', 'end_date']
        _area_index = 0
        _value_index = 0
        _start_date_index = 0
        _end_date_index = 0
        try:
            _area_index = _header_row.index(area_field)
            _value_index = _header_row.index(value_field)
            _start_date_index = _header_row.index(start_date_field)
            _end_date_index = _header_row.index(end_date_field)
        except ValueError, e:
            print 'Field name not found in file header row.', e
            return None

        for row in _reader:
            _new_row = []
            _new_row.append(row[_area_index])
            _new_row.append(row[_value_index])
            _new_row.append(row[_start_date_index])
            _new_row.append(row[_end_date_index])
            print _new_row
            _new_csv.append(_new_row)
    with open(output_filename, 'wb') as wf:
        wr = csv.writer(wf)
        wr.writerow(_new_header_row)
        wr.writerows(_new_csv)
    return output_filename

def convert_dbf_to_csv(input_dbf, output_csv):
    with open(output_csv, 'wb') as csv_file:
        _dbf_file = dbfpy.dbf.Dbf(input_dbf)
        _out_csv = csv.writer(csv_file)
        _header = []
        for field in _dbf_file.header.fields:
            _header.append(field.name)
        _out_csv.writerow(_header)
        for rec in _dbf_file:
            _out_csv.writerow(rec.fieldData)
        _dbf_file.close()
    return None

def merge_files(file1, file2, output_file, file1_field, file2_field):
    _first = pandas.read_csv(file1)
    _second = pandas.read_csv(file2)

    _merged = pandas.merge(_first, _second, how='inner', left_on=file1_field, right_on=file2_field)
    _merged.to_csv(output_file, index=False)

    return None

def aggregate_on_field(input, ref_field, output_fields_dict, output, all_fields=True):
    _input = pandas.read_csv(input)
    # create dictionary
    if all_fields:
        _fields_dict = {}
        _all_fields = _input.columns.values.tolist()
        for f in _all_fields:
            if not output_fields_dict.has_key(f):
                _fields_dict[f] = 'first'
            else:
                _fields_dict[f] = output_fields_dict[f]
    else:
        _fields_dict = output_fields_dict
    _result = _input.groupby(ref_field).agg(_fields_dict)
    _result.to_csv(output, index=False)
    return None