import csv
import os
import re
import sys
import math

data_file_name = 'srk_data'
fluids_file_name = 'srkfluids'

def fld_to_csv(file_name):

    csv_path = os.path.join(sys.path[0], file_name + '.csv')
    fld_path = os.path.join(sys.path[0], file_name + '.fld')


    with open(csv_path, 'w') as g:
        with open(fld_path) as f:
            line_nr = 1
            for line in f.readlines():
                line = re.sub('\t+', '\t', line)
                if line_nr == 1:
                    line = line.replace('\tgroups', '\tg' + '\tg'.join(list(map(str, range(1, 31)))))
                else:
                    line = line.replace(' ', '')
                line = line.strip()
                line_nr += 1
                g.write(line + '\n')



def read_csv(file_name):
    result = []

    path = os.path.join(sys.path[0], file_name + '.csv')

    with open(path, newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            result.append(row)
    return result

def get_row(data, key, value):
    for x in data:
        if len(x) > 1 and x[key] == value:
            return x
    return None

def write_fld(file_name, data):
    path = os.path.join(sys.path[0], file_name + ".fld")
    with open(path, "w") as f:
        for i in range(len(data)):
            line = data[i]
            
            
            
            line_str = ""

            for ele in line:

                tab_number = 15

                ele = str(ele)
                delta = 0

                delta = math.ceil((len(ele)/4))
                rest = len(ele)%4

                if rest == 0:
                    tab_number -= (delta + 1)
                else:
                    tab_number -= delta
                line_str += (ele + tab_number * "\t")
            f.write(line_str + "\n")
            

        


def merge(data, fluids, mappings):
    # delete @END
    fluids.pop()
    for d in data:
        #look for same CAS Nr
        f = get_row(fluids, 2, d[2])
        if f:
            continue
        #skip header
        if d[0] == "english name":
            continue
        
        y = []
        gr_skip = []

        for i in range(len(fluids[0])):

            item = fluids[0][i]
            if item in mappings.keys():
                element_idx = data[0].index(mappings[item])

                if item == 'Pkrit / MPa':
                    element = round(float(d[element_idx].split('*')[0])/1000,4)
                    element = str(element)
                else:
                    element = d[element_idx].split('*')[0]
                y.append(element)
            else:
                
                if item in gr_skip:
                    continue

                if item == 'g1':
                    groups = []


                    group_code = d[-1]
                    
                    if group_code != 'n.a.':
                    

                        group_list = group_code.split(";")
                        group_list = [i.strip() for i in group_list]

                        for ele in group_list:
                            amount = int(ele.split('×')[0])
                            group = ele.split('×')[1]

                            groups += amount*[group]
                        y[-1] = str(len(groups))
                        i += len(groups)
                        for k in range(len(groups)):
                            gr_skip.append("g"+str(k+1))
                            y.append(groups[k])
                        continue
                
                if item == "M / (g/mol)":
                    # calculate molar mass

                    mass = 0

                    C_mass = 12.01
                    O_mass = 16
                    H_mass = 1
                    Br_mass = 79.9
                    Si_mass = 28.08
                    N_mass = 14
                    F_mass = 18.99
                    Cl_mass = 35.4
                    S_mass = 32.06
                    I_mass = 126.9

                    formula = d[1]
                    # print(formula)
                    
                    y.append(mass)
                    continue

                y.append('0')
        fluids.append(y)
    fluids.append(['@END'])
    return fluids


fld_to_csv(fluids_file_name)
data = read_csv(data_file_name)
fluids = read_csv(fluids_file_name)

mappings = {
#   996 ['english name', 'formula', 'CAS-nr.', 'Tc,i / K', 'Pc,i / kPa', 'vc,i / cm3 mol-1', 'Ï‰i', 'c1,i', 'c2,i', 'c3,i', 'Tmin / K', 'Tmax / K', 'increments [counter Ã— sub group number]']
#   136 ['BEZEICHNUNG', 'ALTERNATIVER NAME', 'CAS-NR', 'M / (g/mol)', 'Azentr. Fak.', 'Pkrit / MPa', 'Tcrit / K', 'Ptr / Mpa', 'Ttr / K', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'c1', 'c2', 'c3', 'nr_of_groups', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'g9', 'g10', 'g11', 'g12', 'g13', 'g14', 'g15', 'g16', 'g17', 'g18', 'g19', 'g20', 'g21', 'g22', 'g23', 'g24', 'g25', 'g26', 'g27', 'g28', 'g29'] ''
    'BEZEICHNUNG': 'english name',
    'ALTERNATIVER NAME': 'english name',
    'CAS-NR': 'CAS-nr.',
    'Tcrit / K': 'Tc,i / K',
    'Pkrit / MPa': 'Pc,i / kPa',
    'Azentr. Fak.': 'ωi',
    'c1': 'c1,i', 
    'c2': 'c2,i', 
    'c3': 'c3,i'
}
merged = merge(data, fluids, mappings)
# print(len(fluids), fluids[0])
write_fld("test", merged)
