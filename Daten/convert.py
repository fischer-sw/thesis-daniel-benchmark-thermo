import csv
import os
import re
import sys

data_file_name = 'srk_data'
fluids_file_name = 'srkfluids'

def fld_to_csv(file_name):
    with open(file_name + '.csv', 'w') as g:
        with open(file_name + '.fld') as f:
            line_nr = 1
            for line in f.readlines():
                line = re.sub('\t+', '\t', line)
                if line_nr == 1:
                    line = line.replace('\tgroups', '\tg' + '\tg'.join(list(map(str, range(1, 30)))))
                else:
                    line = line.replace(' ', '')
                line = line.strip()
                line_nr += 1
                g.write(line + '\n')

#fld_to_csv(fluids_file_name)

def read_csv(file_name):
    result = []
    with open(file_name + '.csv', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            result.append(row)
    return result

def get_row(data, key, value):
    for x in data:
        if x[key] == value:
            return x
    return None

def merge(data, fluids, mappings):
    for d in data:
        f = get_row(fluids, 2, d[2])
        if f:
            continue
        y = []
        for i in range(len(fluids[0])):
            item = fluids[i]
            if mappings[item]:
                y.append(d[i])
            else:
                y.append(0)
        fluids.append(y)
    return fluids

data = read_csv(data_file_name)
print(len(data), data[0])
fluids = read_csv(fluids_file_name)
print(len(fluids), fluids[0])

mappings = {
#   996 ['english name', 'formula', 'CAS-nr.', 'Tc,i / K', 'Pc,i / kPa', 'vc,i / cm3 mol-1', 'Ï‰i', 'c1,i', 'c2,i', 'c3,i', 'Tmin / K', 'Tmax / K', 'increments [counter Ã— sub group number]']
#   136 ['BEZEICHNUNG', 'ALTERNATIVER NAME', 'CAS-NR', 'M / (g/mol)', 'Azentr. Fak.', 'Pkrit / MPa', 'Tcrit / K', 'Ptr / Mpa', 'Ttr / K', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'c1', 'c2', 'c3', 'nr_of_groups', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'g9', 'g10', 'g11', 'g12', 'g13', 'g14', 'g15', 'g16', 'g17', 'g18', 'g19', 'g20', 'g21', 'g22', 'g23', 'g24', 'g25', 'g26', 'g27', 'g28', 'g29'] ''
    'ALTERNATIVER NAME': 'english name',
    'CAS-NR': 'CAS-nr.',
    'Tcrit / K': 'Tc,i / K',
    'Pkrit / MPa': 'Pc,i / kPa',
    'Azentr. Fak.': 'Ï‰i',
    'c1': 'c1,i', 
    'c2': 'c2,i', 
    'c3': 'c3,i'
}
merged = merge(data, fluids, mappings)
print(len(fluids), fluids[0])
