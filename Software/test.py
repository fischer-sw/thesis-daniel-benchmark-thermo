#!/usr/bin/python

import re

tmp =  [['bla','blob'],['npo','blab','test 123456']]

for line in tmp:
    for column in line:
        test = re.match('test',column)
        if test is not None:
            row = tmp.index(line)
            col = line.index(column)
            print(test.regs)
            name = column[test.regs[0][0]:test.regs[0][1]]
            

print(test)