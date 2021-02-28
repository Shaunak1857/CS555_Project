def indiList():
    return [0 for i in range(7)]


def familyList():
    flist = [0 for i in range(6)]
    flist[5] = []
    return flist


def Name(x):
    xdata = ''
    for i in x:
        if(i != '/'):
            xdata = i + i
    return xdata


def getID(indiList, ID):
    for i in indiList:
        if(i[0] == ID):
            return i[1]


def fileLength(f):
    for i, l in enumerate(f):
        pass
    return i + 1


def fileparser(fileName):
    File = open(fileName, 'r')
    f = fileLength(open(fileName))
    indi = 0
    fam = 0
    indi_list = []   # list of INDI objects
    fam_list = []    # list of FAM objects
    indiData = indiList()
    familyData = familyList()

    for line in File:
        elems = line.split()
        if(elems != []):
            if(elems[0] == '1'):
                if(elems[1] == 'NAME'):
                    indiData[1] = elems[2] + " " + Name(elems[3])
                if(elems[1] == 'SEX'):
                    indiData[2] = elems[2]
                if(elems[1] == 'BIRT'):
                    dateID = 'BIRT'
                if(elems[1] == 'DEAT'):
                    dateID = 'DEAT'
                if(elems[1] == 'MARR'):
                    dateID = 'MARR'
                if(elems[1] == 'DIV'):
                    dateID = 'DIV'
                if(elems[1] == 'FAMS'):
                    indiData[5] = elems[2]
                if(elems[1] == 'FAMC'):
                    indiData[6] = elems[2]
                if(elems[1] == 'HUSB'):
                    familyData[1] = elems[2]
                if(elems[1] == 'WIFE'):
                    familyData[2] = elems[2]
                if(elems[1] == 'CHIL'):
                    familyData[5].append(elems[2])

            if(elems[0] == '2'):
                if(elems[1] == 'DATE'):
                    date = elems[4] + " " + elems[3] + " " + elems[2]
                    if(dateID == 'BIRT'):
                        indiData[3] = date
                    if(dateID == 'DEAT'):
                        indiData[4] = date
                    if(dateID == 'MARR'):
                        familyData[3] = date
                    if(dateID == 'DIV'):
                        familyData[4] = date

            if(elems[0] == '0'):
                if(indi == 1):  # adding the last object in the file
                    indi_list.append(indiData)
                    indiData = indiList()
                    indi = 0
                if(fam == 1):
                    fam_list.append(familyData)
                    famData = familyList()
                    fam = 0
                if(elems[1] in ['NOTE', 'TRLR', 'HEAD']):
                    pass
                else:
                    if(elems[2] == 'INDI'):
                        indi = 1
                        indiData[0] = (elems[1])
                    if(elems[2] == 'FAM'):
                        fam = 1
                        familyData[0] = (elems[1])
    return indi_list, fam_list
