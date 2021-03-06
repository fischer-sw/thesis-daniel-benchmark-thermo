#!/usr/bin/python

import math
import xlrd
import re
import sys
import os

class Filereader():
    #Konstruktor definieren
    def __init__(self, path):
        self.path = path
        self.dic = {}
        self.header = []
        self.basepath = os.path.join(sys.path[0], "..", "..")
    
    #Funktionen definieren
    def cleanlist(self, liste):
        #remove all '' elements
        tmp = [x for x in liste if x]
        #remove "\n" from last element
        last = tmp.pop()
        #tmp.append(last.strip())
        return tmp


    def read_hostmann(self):

        res = {}
        res["Header"] = []
        header_len = 13

        filename = "srk_data.txt"
        path = os.path.join(self.basepath, "Daten", filename)

        with open(path) as file:
            data = file.readlines()

        #clean data
        for i in range(len(data)):
            val = data[i].split("\n")[0] 
            pos = i % header_len

            if i < header_len:
                res["Header"].append(val)
                continue

            if pos == 0 and i >= header_len:
                system =  data[i].split("\n")[0]

                res[system] = {}
            
            if i >= header_len:
                name = data[pos].split("\n")[0]
                res[system][name] = val

        return res

    def append_header(self, header_target):
        
        # remove groups key
        if "groups" in self.header:
            self.header.remove("groups")
        
        len_hed = len(self.header)
        groups = header_target - len_hed

        # append g<n> keys
        for i in range (1, groups + 1):
            element = "g" + str(i)
            if not element in self.header: 
                self.header.append(element)

        print(self.header)
        

    def addvaltodic(self, dictio, liste):
        
            
        len_hed = len(self.header)
        len_list = len(liste)
        splittedpath = self.path.split('\\') 
        filename = splittedpath[-1]
        if len_hed < len_list:
            print("Es sind Spalten f??r die Substanz: "+liste[0]+ " in der Datei " +filename+ " nicht beschriftet --> Leertasten durch Tabs ersetzen")
            self.append_header(len_list)
        
        elif len_hed > len_list:
            print("Es sind zu wenig Werte f??r die Substanz: "+liste[0]+" in der Datei " +filename+ " vorhanden")
            
        #Create Dictionary for substance
        subs = {}
        #dict[<key>] = value
        #Counter for reading through list
        i = 0
        for i in range(50):
            element = liste[i]
            if element != None:
                subs[self.header[i]] = element

        self.dic[liste[0]]= subs

    def adddata(self, data, data_header):
        #Add additional data
        for key, val in data.items():
            if key == "Header":
                
                for element in data_header:
                    if not element in self.header:
                        self.header.append(element)
                continue
            if not key in self.dic:
                self.dic[key] = data[key]
            else:
                for element in val:
                    if not element in self.dic[key]:
                        self.dic[key][element] = val[element]
        self.addmissingdata()
            
        
    def addmissingdata(self):
        #Add missing data
        for key, val in self.dic.items():
            if key == "Header":
                continue
            for element in self.header:
                if not element in self.dic[key]:
                    self.dic[key][element] = "0.000"
        
    
    def addcolums(self, data):
        for element in data:
            if not element in self.header:
                self.header.append(element)
        self.addmissingdata()
    
    
    def readdata(self):
        with open(self.path,'r') as file:
            header = file.readline()
            hed = header.split("\t")
            self.header = self.cleanlist(hed)
            self.dic["Header"] = self.header
            
            #for i in range(0,99):
            for i in range(0, self.file_len(self.path)):
                line = file.readline()
                lis = self.cleanlist(line.split("\t"))
                #print("Line "+str(i)+ ":")
                #print(line)
                self.addvaltodic(self.dic, lis)
        
        return self.dic
    
    def file_len(self,path):
        with open(self.path) as f:
            for i, l in enumerate(f):
                pass
        return i - 1 #skip the @END at the End of File
    
    def writefile(self, path):
        pos = {}
        tabs = '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t'
        num_tabs = 15
        counter = 0
        with open(path, 'w') as file:
            #write header:
            for element in self.header:
                #print("Element = " + str(element))
                if len(element) == 1 or len(element) == 2:
                    file.write('\t' + element + tabs)
                else:
                    file.write(element+ tabs)
                
                #get Position of each element
                pos[element] = counter
                delta = math.ceil((len(element)/4))
            
            #correct the position of elements
                
                if (len(element)%4) == 0:
                    counter += delta + num_tabs
            
                else:
                    if len(element) != 1:
        
                        if len(element) !=2:
                            counter += delta + num_tabs - 1
                        else:
                            counter += delta + num_tabs
                    else:
                        counter += delta + num_tabs
                        
                            
                if (self.header.index(element) + 1) < len(self.header):
                    if len(self.header[self.header.index(element) + 1]) == 1 and len(element) != 1:
                        counter = counter + 1
            #rint(pos)
            #print(self.header)
            file.write('\n')
            
            #write data:
            
            counter = 0
            
            for element in self.dic:
                if element == "Header":
                    continue
                for i in range(0,len(self.header)):
                   
                    file.write(self.dic[element][self.header[i]])
                    if i+1 < len(self.header):
                        header = self.header[i+1]
                    ele = len(self.dic[element][self.header[i]])
                    
                    counter += math.floor(ele/4)
                    
                    for i in range (counter, pos[header]):
                        file.write('\t')
                        counter += 1
                counter = 0
                
                #break
                file.write('\t')
                file.write('\n')
                #write End of file
            file.write('@END')


    def appendAtoG(self, data, path):


        new_data = []

        with open(path) as f:
            AtoGdata = f.readlines()



        for line in AtoGdata:
             new_data.append(line.split("\n")[0])

        for i in range(1,len(new_data)):
            
            line = new_data[i]

            line_splt = line.split(" ") 
            
            search_cas = line_splt[1]

            for key in data.keys():
                if key == "Header":
                    continue
                data_cas = data[key]["CAS-NR"]

                if search_cas == data_cas:
                    data[key]["A"] = line_splt[-7]
                    data[key]["B"] = line_splt[-6]
                    data[key]["C"] = line_splt[-5]
                    data[key]["D"] = line_splt[-4]
                    data[key]["E"] = line_splt[-3]
                    data[key]["F"] = line_splt[-2]
                    data[key]["G"] = line_splt[-1]
                    break


        return data


    def stripdata(self, data, length):

        stripped = {}

        for key in data.keys():
            if key == "Header":
                continue
            if len(key) <= length:
                stripped[key] = data[key]

        return stripped


    def komma2dot(self, data):

        for key in data:
            if key == "Header":
                continue

            for ele in ["A", "B", "C", "D", "E", "F", "G"]:

                value = data[key][ele]

                if "," in value:

                    new_value = value.replace(",",".")
                    data[key][ele] = new_value

        return data


if __name__ == "__main__":
    path = os.path.join(sys.path[0], "..", "..","Daten", "test1_fertig_lang.fld")
    reader = Filereader(path)
    srk_data = reader.readdata()

    # stripped_data = reader.stripdata(srk_data, 8)

    # reader.dic = stripped_data

    # AtoGpath = os.path.join(sys.path[0], "..", "..","Daten", "A-G.txt")


    # new_data = reader.appendAtoG(reader.dic, AtoGpath)

    
    srk_data = reader.komma2dot(srk_data)
    
    reader.dic = srk_data






    output_path = os.path.join(sys.path[0], "..", "..","Daten", "test1_fertig_lang.fld")

    reader.writefile(output_path)