import datetime
import re

import pandas as pd
from tabulate import tabulate


class Individual:
    def __init__(self, uid=None, name=None, sex=None, birt=None, deat=None, famc=None, fams=None):
        self.uid = uid
        self.name = name
        self.sex = sex
        self.birt = birt
        self.age = self.get_age()
        self.deat = deat
        self.alive = True if self.deat is None else False
        self.famc = famc
        self.fams = fams

    def get_age(self):
        if self.birt is not None:
            return datetime.date.today().year - datetime.datetime.strptime(self.birt, '%Y %b %d').year
        else:
            return None

    def as_dict(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'sex': self.sex,
            'birt': self.birt,
            'age': self.age,
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
    def __init__(self, filename, sort=None):
        indi_df, fam_df = self.fileparser(filename)

        self.indi_df = indi_df
        self.fam_df = fam_df

        if sort is not None:
            self.sort(sort)

    @staticmethod
    def fileLength(f):
        for i, l in enumerate(f):
            pass
        return i + 1

    # @staticmethod
    # def Name(x):
    #     xdata = ''
    #     for i in x:
    #         if(i != '/'):
    #             xdata = i + i
    #     return xdata

    def sort(self, sort):
        # for when sorting by id, sort by the number inside the id instead of alphabetically
        def human_sort(col): return pd.Series(
            [int(re.findall(r'(\d+)', x)[0]) for x in col])

        def sort_by_column(sort, df):
            human_sort_keys = ['uid', 'famc', 'fams', 'husb', 'wife']
            if sort in human_sort_keys:
                key = human_sort
            else:
                key = None

            if sort in df:
                return df.sort_values(sort, ignore_index=True,
                                      key=key).reset_index(drop=True)
            else:
                return df

        if type(sort) is str:
            self.indi_df = sort_by_column(sort, self.indi_df)
            self.fam_df = sort_by_column(sort, self.fam_df)
        elif type(sort) is list:
            self.indi_df = sort_by_column(sort[0], self.indi_df)
            self.fam_df = sort_by_column(sort[1], self.fam_df)

    def fileparser(self, filename):
        File = open(filename, 'r')
        f = GEDCOM.fileLength(open(filename))
        indi = 0
        fam = 0
        indiData = Individual()
        familyData = Family()
        indi_df = pd.DataFrame(columns=list(
            indiData.as_dict().keys()))      # pandas dataframe of INDI objects
        fam_df = pd.DataFrame(columns=list(
            familyData.as_dict().keys()))    # pandas dataframe of FAM objects

        for line in File:
            elems = line.split()
            if(elems != []):
                if(elems[0] == '1'):
                    if(elems[1] == 'NAME'):
                        indiData.name = ' '.join(elems[2:])
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
                        familyData.husb_name = indi_df[indi_df.uid ==
                                                       familyData.husb].iloc[0]['name']     # Find the husband's name in the individual list
                    if(elems[1] == 'WIFE'):
                        familyData.wife = elems[2]
                        familyData.wife_name = indi_df[indi_df.uid ==
                                                       familyData.wife].iloc[0]['name']     # Find the wife's name in the individual list
                    if(elems[1] == 'CHIL'):
                        familyData.childrens.append(elems[2])

                if(elems[0] == '2'):
                    if(elems[1] == 'DATE'):
                        date = elems[4] + " " + elems[3] + " " + elems[2]
                        if(dateID == 'BIRT'):
                            indiData.birt = date
                            indiData.age = indiData.get_age()
                        if(dateID == 'DEAT'):
                            indiData.deat = date
                            indiData.alive = False
                        if(dateID == 'MARR'):
                            familyData.marr = date
                        if(dateID == 'DIV'):
                            familyData.div = date

                if(elems[0] == '0'):
                    if(indi == 1):  # adding the last object in the file
                        indi_df = indi_df.append(
                            indiData.as_dict(), ignore_index=True)
                        indiData = Individual()
                        indi = 0
                    if(fam == 1):
                        fam_df = fam_df.append(
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

        return indi_df.reset_index(drop=True), fam_df.reset_index(drop=True)

    def pretty_print(self):
        print('Individuals')
        print(tabulate(self.indi_df, headers='keys', tablefmt='psql'), '\n')
        print('Families')
        print(tabulate(self.fam_df, headers='keys', tablefmt='psql'))


if __name__ == '__main__':
    gedcom1 = GEDCOM('Test.ged', sort='uid')
    gedcom1.pretty_print()
