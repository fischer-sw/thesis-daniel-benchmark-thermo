import csv
import os
import re
import sys
import math
import json

data_file_name = 'horstmann_data'
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

def get_tab_length(word):
    res = 0

    tabs = {
        "a" : 0.5,
        "b" : 0.5,
        "c" : 0.5,
        "d" : 0.5,
        "e" : 0.5,
        "f" : 0.25,
        "g" : 0.5,
        "h" : 0.5,
        "i" : 0.20,
        "j" : 0.20,
        "k" : 0.5,
        "l" : 0.2,
        "m" : 0.5,
        "n" : 0.5,
        "o" : 0.5,
        "p" : 0.5,
        "q" : 0.5,
        "r" : 0.25,
        "s" : 0.5,
        "t" : 0.25,
        "u" : 0.5,
        "v" : 0.5,
        "w" : 0.5,
        "x" : 0.5,
        "y" : 0.5,
        "z" : 0.5,
        "A" : 0.5,
        "B" : 0.5,
        "C" : 0.5,
        "D" : 0.5,
        "E" : 0.5,
        "F" : 0.5,
        "G" : 0.5,
        "H" : 0.5,
        "I" : 0.25,
        "J" : 0.5,
        "K" : 0.5,
        "L" : 0.5,
        "M" : 0.5,
        "N" : 0.5,
        "O" : 0.5,
        "P" : 0.5,
        "Q" : 0.5,
        "R" : 0.5,
        "S" : 0.5,
        "T" : 0.5,
        "U" : 0.5,
        "V" : 0.5,
        "W" : 0.5,
        "X" : 0.5,
        "Y" : 0.5,
        "Z" : 0.5,
        "0" : 0.5,
        "1" : 0.5,
        "2" : 0.5,
        "3" : 0.5,
        "4" : 0.5,
        "5" : 0.5,
        "6" : 0.5,
        "7" : 0.5,
        "8" : 0.5,
        "9" : 0.5,
        "-" : 0.25,
        " " : 0.5,
        "(" : 0.25,
        "[" : 0.25,
        ")" : 0.25,
        "]" : 0.25,
        "." : 0.25,
        "," : 0.25,
        "/" : 0.25,
        "_" : 0.5,
        "+" : 0.5,
        "'" : 0.15,
        "<" : 0.5,
        ">" : 0.5,
        "@" : 0.5
    }

    for ele in word:
        res += tabs[ele]
    return math.floor(res)


def write_fld(file_name, data):
    path = os.path.join(sys.path[0], file_name + ".fld")
    with open(path, "w") as f:
        for i in range(len(data)):
            line = data[i]
            
            
            
            line_str = ""

            for ele in line:

                tab_number = 17

                ele = str(ele)
                delta = 0
                
                # delta = get_tab_length(ele)
                delta = math.ceil(len(ele)/4)
                rest = len(ele)%4

                if rest != 0:
                
                    tab_number -= delta

                else:
                    tab_number -= (delta + 1)

                line_str += (ele + tab_number * "\t")
            f.write(line_str + "\n")
            

def write_mappings(data, file_name):

    path = os.path.join(sys.path[0], file_name + ".json")

    if os.path.exists(path) == False:
        with open(path, "w") as f:
            json.dump(data, f , ensure_ascii=False, indent=2, sort_keys=True)
    else:
        print("File {} already there".format(file_name + ".json"))


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
                    element = d[element_idx].split('*')[0].lower()
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
                    
                    mass = round(molar_mass(formula),2)
                    
                    y.append(str(mass))
                    continue

                y.append('0')
        fluids.append(y)
    fluids.append(['@END'])
    return fluids

def read_systems(filename):

    path = os.path.join(sys.path[0], filename + ".json")
    with open(path) as f:
        data = json.loads(f.read())

    return data

def check_systems(systems, data):

    res = {}

    found = 0
    number = len(systems)

    for ele in systems.keys():

        res[ele] = False
        ele_cas = systems[ele]

        for i in range(len(data)-1):
            data_cas = data[i][2]
            if ele_cas == data_cas:
                found += 1
                data_ele = data[i][0]
                res[ele] = data_ele
                break

            

    return (res, number, found)


def molar_mass(formula):
    weights = {
        'C': 12.01,
        'O': 16,
        'H': 1,
        'Br': 79.9,
        'Si': 28.08,
        'N': 14,
        'F': 18.99,
        'Cl': 35.4,
        'S': 32.06,
        'I': 126.9
    }
    result = 0
    for item in re.findall('[A-Z][a-z]*[0-9]*', formula):
        m = re.match('([A-Z][a-z]*)(\d+)*', item)
        if m:
            if m.groups()[1] != None:
                test = m.groups()
                result += weights[m.group(1)] * int(m.group(2))
            else:
                result += weights[m.group(1)]

    return result

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
systems = read_systems("database_components")

res, n_sys, n_found = check_systems(systems, merged)

write_mappings(res, "mappings")

found_per = round(n_found/n_sys * 100, 0)

print(str(found_per) + " % gefunden")