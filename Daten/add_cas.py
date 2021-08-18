import cirpy
import os
import sys


readpath = os.path.join(sys.path[0], "A-G_original.txt")
writepath = os.path.join(sys.path[0], "A-G.txt")


def read_data(path):
    with open(path, "r", encoding='utf-8') as f:
        data = f.readlines()

    return data

def write_data(path, data):
    with open(path, "w") as f:
        for line in data:
            line_str = " ".join(line)
            f.write(line_str + "\n")


data = read_data(readpath)

lis = [["Name", "CAS", "A", "B", "C", "D", "E", "F", "G"]]

for line in data:
    tmp = []
    elements = line.split(" ")
    elements[-1] = elements[-1].split("\n")[0]
    name = elements[0]

    cas = cirpy.resolve(name, "cas")
    
    tmp.append(elements[0])
    if cas != None and type(cas) != type([]):
        tmp.append(cas)
    else:
        if cas != None:
            min = 10

            for i in range(len(cas)):
                ele = cas[i]
                length_first = len(ele.split("-")[0])
                if length_first < min:
                    min = length_first
                    min_idx = i
            
            cas = cas[min_idx]
            tmp.append(cas)
        else:
            tmp.append("<cas>")

    for i in range(-7, 0):
        tmp.append(elements[i])
    lis.append(tmp)
    print("Element: {}, CAS: {}".format(name, cas))

write_data(writepath, lis)
