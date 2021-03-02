import pandas as pd
from tabulate import tabulate


class Individual:
    def __init__(self, uid=None, name=None, sex=None, birt=None, deat=None, famc=None, fams=None):
        self.uid = uid
        self.name = name
        self.sex = sex
        self.birt = birt
        self.deat = deat
        self.alive = True if self.deat is None else False
        self.famc = famc
        self.fams = fams

    def as_dict(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'sex': self.sex,
            'birt': self.birt,
            'deat': self.deat,
            'alive': self.alive,
            'famc': self.famc,
            'fams': self.fams
        }


class Family:
    def __init__(self, uid=None, husb=None, husb_name=None, wife=None, wife_name=None, marr=None, div=None, childrens=[]):
        self.uid = uid
        self.husb = husb
        self.husb_name = husb_name
        self.wife = wife
        self.wife_name = wife_name
        self.marr = marr
        self.div = div
        self.childrens = childrens

    def as_dict(self):
        return {
            'uid': self.uid,
            'husb': self.husb,
            'husb_name': self.husb_name,
            'wife': self.wife,
            'wife_name': self.wife_name,
            'marr': self.marr,
            'div': self.div,
            'childrens': self.childrens
        }


class GEDCOM:
    def __init__(self, filename):
        self.fileparser(filename)

    @staticmethod
    def fileLength(f):
        for i, l in enumerate(f):
            pass
        return i + 1

    @staticmethod
    def Name(x):
        xdata = ''
        for i in x:
            if(i != '/'):
                xdata = i + i
        return xdata

    def fileparser(self, filename):
        File = open(filename, 'r')
        f = GEDCOM.fileLength(open(filename))
        indi = 0
        fam = 0
        indiData = Individual()
        familyData = Family()
        indi_pd = pd.DataFrame(columns=list(
            indiData.as_dict().keys()))      # pandas dataframe of INDI objects
        fam_pd = pd.DataFrame(columns=list(
            familyData.as_dict().keys()))    # pandas dataframe of FAM objects

        for line in File:
            elems = line.split()
            if(elems != []):
                if(elems[0] == '1'):
                    if(elems[1] == 'NAME'):
                        indiData.name = elems[2] + " " + GEDCOM.Name(elems[3])
                    if(elems[1] == 'SEX'):
                        indiData.sex = elems[2]
                    if(elems[1] == 'BIRT'):
                        dateID = 'BIRT'
                    if(elems[1] == 'DEAT'):
                        dateID = 'DEAT'
                    if(elems[1] == 'MARR'):
                        dateID = 'MARR'
                    if(elems[1] == 'DIV'):
                        dateID = 'DIV'
                    if(elems[1] == 'FAMS'):
                        indiData.fams = elems[2]
                    if(elems[1] == 'FAMC'):
                        indiData.famc = elems[2]
                    if(elems[1] == 'HUSB'):
                        familyData.husb = elems[2]
                        familyData.husb_name = indi_pd[indi_pd.uid ==
                                                       familyData.husb].iloc[0]['name']     # Find the husband's name in the individual list
                    if(elems[1] == 'WIFE'):
                        familyData.wife = elems[2]
                        familyData.wife_name = indi_pd[indi_pd.uid ==
                                                       familyData.wife].iloc[0]['name']     # Find the wife's name in the individual list
                    if(elems[1] == 'CHIL'):
                        familyData.childrens.append(elems[2])

                if(elems[0] == '2'):
                    if(elems[1] == 'DATE'):
                        date = elems[4] + " " + elems[3] + " " + elems[2]
                        if(dateID == 'BIRT'):
                            indiData.birt = date
                        if(dateID == 'DEAT'):
                            indiData.deat = date
                            indiData.alive = False
                        if(dateID == 'MARR'):
                            familyData.marr = date
                        if(dateID == 'DIV'):
                            familyData.div = date

                if(elems[0] == '0'):
                    if(indi == 1):  # adding the last object in the file
                        indi_pd = indi_pd.append(
                            indiData.as_dict(), ignore_index=True)
                        indiData = Individual()
                        indi = 0
                    if(fam == 1):
                        fam_pd = fam_pd.append(
                            familyData.as_dict(), ignore_index=True)
                        famData = Family()
                        fam = 0
                    if(elems[1] in ['NOTE', 'TRLR', 'HEAD']):
                        pass
                    else:
                        if(elems[2] == 'INDI'):
                            indi = 1
                            indiData.uid = (elems[1])
                        if(elems[2] == 'FAM'):
                            fam = 1
                            familyData.uid = (elems[1])

        self.indi_pd = indi_pd
        self.fam_pd = fam_pd


if __name__ == '__main__':
    gedcom1 = GEDCOM('project1.ged')
    print(tabulate(gedcom1.indi_pd, headers='keys', tablefmt='psql'), '\n')
    print(tabulate(gedcom1.fam_pd, headers='keys', tablefmt='psql'))
