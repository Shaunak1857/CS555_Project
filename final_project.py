import datetime
import re

import pandas as pd
from tabulate import tabulate


class Individual:
    DEFAULT_DATE_FORMAT = '%Y %b %d'

    def __init__(self, uid=None, name=None, sex=None, birt=None, deat=None, famc=None, fams=None):
        self.uid = uid
        self.name = name
        self.sex = sex
        self.birt = birt
        self.deat = deat
        self.age = self.get_age()
        self.alive = True if self.deat is None else False
        self.famc = famc
        self.fams = fams

    def get_age(self, date_format=DEFAULT_DATE_FORMAT):
        if self.birt is not None:
            last_year = datetime.date.today().year
            if self.deat is not None:
                last_year = datetime.datetime.strptime(
                    self.deat, date_format).year
            return last_year - datetime.datetime.strptime(self.birt, date_format).year
        else:
            return None

    # Validation functions to be used in validate() that follows the standard:
    # Input : self
    # Output: type (ANOMALY or ERROR), uid, message (in regard to the nomaly/error)
    def validate_birt_deat(self, date_format=DEFAULT_DATE_FORMAT):
        if self.birt is None:
            return 'ERROR', self.uid, self.name, 'has no birth date'

        if self.deat is None:
            return None

        birthday = datetime.datetime.strptime(self.birt, date_format)
        deathday = datetime.datetime.strptime(self.deat, date_format)
        if (deathday - birthday).days < 0:
            pronoun = 'his' if self.sex == 'M' else 'her'
            return 'ERROR', self.name, self.uid, 'has a birth date later than ' + pronoun + ' death date'
        else:
            return None

    # Takes in a list of validation functions that follows the above mentioned standard
    # Input : self, list of validation functions
    # Output: List of errors/anomalies associated with this Individual object
    def validate(self, validations=[validate_birt_deat]):
        messages = []
        for v in validations:
            results = v(self)
            if results is not None:
                msg = '{type}: {name} ({uid}) {msg}.'.format(
                    type=results[0], uid=results[1], name=results[2], msg=results[3])
                messages.append(msg)
        return messages

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
    DEFAULT_DATE_FORMAT = '%Y %b %d'

    def __init__(self, uid=None, husb=None, husb_name=None, wife=None, wife_name=None, marr=None, div=None, childrens=None):
        self.uid = uid
        self.husb = husb
        self.husb_name = husb_name
        self.wife = wife
        self.wife_name = wife_name
        self.marr = marr
        self.div = div
        self.childrens = [] if childrens is None else childrens

    # Validation functions to be used in validate() that follows the standard:
    # Input : self
    # Output: type (ANOMALY or ERROR), uid, message (in regard to the nomaly/error),
    #         list of uid of individuals involved,
    #         list of name of individuals involved (order must match list of individual uid)
    def validate_marr_div(self, date_format=DEFAULT_DATE_FORMAT):
        if self.div is None:
            return None

        marriage_date = datetime.datetime.strptime(self.marr, date_format)
        divorce_date = datetime.datetime.strptime(self.div, date_format)
        if (divorce_date - marriage_date).days < 0:
            return 'ERROR', self.uid, 'has a marriage date later than its divorce date', [self.husb, self.wife], [self.husb_name, self.wife_name]
        else:
            return None

    # Takes in a list of validation functions that follows the above mentioned standard
    # Input : self, list of validation functions
    # Output: List of errors/anomalies associated with this Family object
    def validate(self, validations=[validate_marr_div]):
        messages = []
        for v in validations:
            results = v(self)
            if results is not None:
                indi_uids = results[3]
                indi_names = results[4]
                indi_involved = ', '.join(
                    [uid + ' (' + name + ')' for uid, name in zip(indi_uids, indi_names)])
                msg = '{type}: Family {uid} {msg}.\nIndividual(s) involved: {indis}'.format(
                    type=results[0], uid=results[1], msg=results[2], indis=indi_involved)
                messages.append(msg)
        return messages

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


class Gedcom:
    def __init__(self, filename, sort=None):
        indi_df, fam_df, reports = self.fileparser(filename)

        self.indi_df = indi_df
        self.fam_df = fam_df
        self.reports = reports

        if sort is not None:
            self.sort(sort)

    # @staticmethod
    # def fileLength(f):
    #     for i, l in enumerate(f):
    #         pass
    #     return i + 1

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
        f = open(filename)
        # f = Gedcom.fileLength(open(filename))
        indi = 0
        fam = 0
        indiData = Individual()
        familyData = Family()
        indi_df = pd.DataFrame(columns=list(
            indiData.as_dict().keys()))      # pandas dataframe of INDI objects
        fam_df = pd.DataFrame(columns=list(
            familyData.as_dict().keys()))    # pandas dataframe of FAM objects
        reports = {}    # Dictionary that maps line number to a list of anomalies/errors

        for i, line in enumerate(f):
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
                            indiData.age = indiData.get_age()
                            indiData.alive = False
                        if(dateID == 'MARR'):
                            familyData.marr = date
                        if(dateID == 'DIV'):
                            familyData.div = date

                if(elems[0] == '0'):
                    if(indi == 1):  # adding the last object in the file
                        report = indiData.validate()
                        if len(report) > 0:
                            reports[i] = report
                        indi_df = indi_df.append(
                            indiData.as_dict(), ignore_index=True)
                        indiData = Individual()
                        indi = 0
                    if(fam == 1):
                        report = familyData.validate()
                        if len(report) > 0:
                            reports[i] = report
                        fam_df = fam_df.append(
                            familyData.as_dict(), ignore_index=True)
                        familyData = Family()
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
        f.close()
        return indi_df.reset_index(drop=True), fam_df.reset_index(drop=True), reports

    def pretty_print(self, filename=None):
        tables = self.__str__()
        print(tables)
        if filename is not None:
            with open(filename, 'w+') as f:
                f.write(tables)

    def __str__(self):
        tables = 'Individuals\n'
        tables += tabulate(self.indi_df, headers='keys', tablefmt='psql')
        tables += '\n'
        tables += 'Families\n'
        tables += tabulate(self.fam_df, headers='keys', tablefmt='psql')
        tables += '\n'

        if self.reports:
            tables += 'Anomalies/Errors\n'
            tables += '\n'.join(['Line ' + str(k) + ':\n' +
                                 '\n'.join(v) for k, v in self.reports.items()])
        return tables


if __name__ == '__main__':
    gedcom_wrong = Gedcom('./tests/test_wrong.ged', sort='uid')
    gedcom_wrong.pretty_print(filename='./tests/gedcom_wrong_table.txt')
    gedcom_correct = Gedcom('./tests/test_correct.ged', sort='uid')
    gedcom_correct.pretty_print(filename='./tests/gedcom_correct_table.txt')
    gedcom1 = Gedcom('Test.ged', sort='uid')
    gedcom1.pretty_print(filename='gedcom1_table.txt')
