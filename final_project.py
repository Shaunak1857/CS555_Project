import datetime
import re
import os
import json
import sqlite3

import pandas as pd
from tabulate import tabulate


class GedcomeItem:
    def __init__(self, db):
        self.db = db

    def db_indi_select(self, uid):
        select_query = '''SELECT * FROM individuals WHERE uid=?'''
        individual = None

        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute(select_query, [uid])

            indi = cursor.fetchone()
            indi = [i if i != 'null' else None for i in indi]
            individual = Individual(uid=indi[0],
                                    name=indi[1],
                                    sex=indi[2],
                                    birt=indi[3],
                                    deat=indi[5],
                                    famc=indi[7],
                                    fams=indi[8], db=self.db)
        except sqlite3.Error as e:
            print("ERRROR FROM SQLITE",e)
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            return individual

    def db_family_select(self, uid):
        select_query = '''SELECT * FROM families WHERE uid=?'''
        family = None

        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute(select_query, [uid])

            fam = cursor.fetchone()
            fam = [f if f != 'null' else None for f in fam]
            family = Family(uid=fam[0],
                            husb=fam[1],
                            husb_name=fam[2],
                            wife=fam[3],
                            wife_name=fam[4],
                            marr=fam[5],
                            div=fam[6],
                            childrens=json.loads(fam[7]),
                            db=self.db)
        except sqlite3.Error as e:
            print(e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            return family


class Individual(GedcomeItem):
    DEFAULT_DATE_FORMAT = '%Y %b %d'

    def __init__(self, uid=None, name=None, sex=None, birt=None, deat=None, famc=None, fams=None, db=None, additional_validations=None):
        super().__init__(db)

        self.uid = uid
        self.name = name
        self.sex = sex
        self.birt = birt
        self.deat = deat
        self.age = self.get_age()
        self.alive = True if self.deat is None else False
        self.famc = famc
        self.fams = fams

        self.additional_validations = additional_validations

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

    #US1- validate birth is not after today's date
    def validate_birth_before_current_date(self, date_format=DEFAULT_DATE_FORMAT):
        if self.birt is None:
            return 'ERROR', self.uid, self.name, 'has no birth date'

        birthday = datetime.datetime.strptime(self.birt, date_format)
        today = datetime.date.today()

        if (today - birthday).days < 0:
            return 'ERROR', self.name, self.uid, 'has a birth date later than today\'s date' 
        else:
            return None

    #US1- validate death is not after today's date
    def validate_death_before_current_date(self, date_format=DEFAULT_DATE_FORMAT):
        if self.deat is None:
            return None
        
        deathday = datetime.datetime.strptime(self.deat, date_format)
        today = datetime.date.today()

        if (today - deathday).days < 0:
            return 'ERROR', self.name, self.uid, 'has a date date later than today\'s date' 
        else:
            return None

    # US3 - validate birth before death
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
    #US7 - validate age is less than 150 years old
    def validate_age_from_birth(self,date_format=DEFAULT_DATE_FORMAT):
        if self.birt is None:
            return 'ERROR', self.uid, self.name, 'has no birth date'
        if self.deat is None:
            age = self.get_age()

            if age >= 150:
                return 'Error', self.uid, self.name, 'is older than 150 years old'
            else:
                return None
        else:
            birthday = datetime.datetime.strptime(self.birt, date_format)
            deathday = datetime.datetime.strptime(self.deat, date_format)

            if (deathday - birthday).days < 0:
                return 'ERROR', self.name, self.uid, 'is older than 150 years old'
            else:
                return None

        
        


    # US8 - validate birth is after marriage of parents, and birth is no later than 9 month after divorce.
    def validate_birt_before_marr(self, date_format=DEFAULT_DATE_FORMAT):
        if self.famc is None:
            return None

        family = self.db_family_select(self.famc)
        father = family.husb_name
        mother = family.wife_name

        birth_date = datetime.datetime.strptime(self.birt, date_format)
        marriage_date = datetime.datetime.strptime(family.marr, date_format)
        divorce_date = None
        if family.div is not None:
            divorce_date = datetime.datetime.strptime(family.div, date_format)
        pronoun = 'his' if self.sex == 'M' else 'her'
        if (birth_date - marriage_date).days < 0:
            return 'ANOMALY', self.name, self.uid, 'has a birth date before ' + pronoun + ' parents\' marriage date'
        elif divorce_date and (birth_date - divorce_date).days > 280:
            return 'ANOMALY', self.name, self.uid, 'has a birth date more than 280 days later than ' + pronoun + ' parents\' divorce date'
        else:
            return None

    validations = [validate_birth_before_current_date, validate_death_before_current_date, validate_birt_deat, validate_birt_before_marr, validate_age_from_birth]
    # Go through the list of validation functions in self.validations that follows the above mentioned standard
    # Input : self
    # Output: List of errors/anomalies associated with this Individual object

    def validate(self):
        messages = []
        if self.additional_validations is not None:
            self.validations += self.additional_validations
        for v in self.validations:
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


class Family(GedcomeItem):
    DEFAULT_DATE_FORMAT = '%Y %b %d'

    def __init__(self, uid=None, husb=None, husb_name=None, wife=None, wife_name=None, marr=None, div=None, childrens=None, db=None, additional_validations=None):
        super().__init__(db)

        self.uid = uid
        self.husb = husb
        self.husb_name = husb_name
        self.wife = wife
        self.wife_name = wife_name
        self.marr = marr
        self.div = div
        self.childrens = [] if childrens is None else childrens

        self.db = db

        self.additional_validations = additional_validations

    # Validation functions to be used in validate() that follows the standard:
    # Input : self
    # Output: type (ANOMALY or ERROR), uid, message (in regard to the nomaly/error),
    #         list of uid of individuals involved,
    #         list of name of individuals involved (order must match list of individual uid)

    #US1- validate marriage before today's date
    def validate_marr_before_current_date(self, date_format=DEFAULT_DATE_FORMAT):
        if self.marr is None:
            return 'ERROR', self.uid, 'has no marriage date'
        marriage_date = datetime.datetime.strptime(self.marr, date_format)
        today = datetime.date.today()

        if (today - marriage_date).days < 0:
            return 'ERROR', self.uid, 'has a marriage date later than today\'s date' 
        else:
            return None

    #US1- validate divorce before today's date
    def validate_div_before_current_date(self, date_format=DEFAULT_DATE_FORMAT):
        if self.div is None:
            return None

        divorce_date = datetime.datetime.strptime(self.div, date_format)
        today = datetime.date.today()

        if (today - divorce_date).days < 0:
            return 'ERROR', self.uid, 'has a divorce date later than today\'s date' 
        else:
            return None


    # US4 - validate marriage before divorce
    def validate_marr_div(self, date_format=DEFAULT_DATE_FORMAT):
        if self.div is None:
            return None

        marriage_date = datetime.datetime.strptime(self.marr, date_format)
        divorce_date = datetime.datetime.strptime(self.div, date_format)
        if (divorce_date - marriage_date).days < 0:
            return 'ERROR', self.uid, 'has a marriage date later than its divorce date', [self.husb, self.wife], [self.husb_name, self.wife_name]
        else:
            return None

    

    # US5 - Marriage should occur before death of either spouse
    def validate_marr_before_death(self,date_format=DEFAULT_DATE_FORMAT):
        husb, wife = self.db_indi_select(uid = self.husb), self.db_indi_select(uid = self.wife)
        if husb.deat is None:
            #alive
            if wife.deat is None:
                # alive
                return None
            else:
                wifedeat = datetime.datetime.strptime(wife.deat, date_format)
                marrdeat = datetime.datetime.strptime(self.marr, date_format)
                if (wifedeat - marrdeat).days<0:
                    return 'ERROR', self.wife, 'has a marriage date after her death date', [self.husb, self.wife], [self.husb_name, self.wife_name]
                else:
                    return None
        else:
            husbdeat = datetime.datetime.strptime(husb.deat, date_format)
            marrdeat = datetime.datetime.strptime(self.marr, date_format)
            if (husbdeat - marrdeat).days<0:
                return 'ERROR', self.husb, 'has a marriage date after his death date', [self.husb, self.wife], [self.husb_name, self.wife_name]
            else:
                if wife.deat is None:
                    # alive
                    return None
                else:
                    wifedeat = datetime.datetime.strptime(wife.deat, date_format)
                    marrdeat = datetime.datetime.strptime(self.marr, date_format)
                    if (wifedeat - marrdeat)<0:
                        return 'ERROR', self.wife, 'has a marriage date after her death date', [self.husb, self.wife], [self.husb_name, self.wife_name]
                    else:
                        return None

        
    # US6 - Divorce can only occur before death of both spouses
    def validate_divorce_before_death(self,date_format=DEFAULT_DATE_FORMAT):
        if self.div is None:
            # not divroced
            return None
        else:
            # only if divorced
            divorce_date = datetime.datetime.strptime(self.div, date_format)
            husb, wife = self.db_indi_select(uid = self.husb), self.db_indi_select(uid = self.wife)

            if husb.deat is None:
                #husb living
                if wife.deat is None:
                    #wife living
                    return None
                else:
                    # wife is dead, check error
                    wifedeat = datetime.datetime.strptime(self.div, date_format)
                    if (wifedeat - divorce_date).days < 0:
                        # husband alive, wife died but error, wife might be dead before divorce
                        return 'ERROR', self.wife, 'has a divorce date after her death', [self.husb, self.wife], [self.husb_name, self.wife_name]
                    else:
                        # husband alive, wife died but no error
                        return None
            else:
                #husb died, and check error
                husbdeat = datetime.datetime.strptime(husb.deat, date_format)
                if (husbdeat - divorce_date).days < 0:
                    # husband dided and there is an error
                    return 'ERROR', self.husb, 'has a divorce date after his death', [self.husb, self.wife], [self.husb_name, self.wife_name]
                else:
                    if wife.deat is None:
                        #wife living
                        return None
                    else:
                        # wife is dead, check error
                        wifedeat = datetime.datetime.strptime(self.div, date_format)
                        if (wifedeat - divorce_date).days < 0:
                            # husband alive, wife died but error, wife might be dead before divorce
                            return 'ERROR', self.wife, 'has a divorce date after her death', [self.husb, self.wife], [self.husb_name, self.wife_name]
                        else:
                            # husband alive, wife died but no error
                            return None
    
    validations = [validate_marr_before_current_date, validate_div_before_current_date, validate_marr_div, validate_marr_before_death, validate_divorce_before_death]
    # Takes in a list of validation functions that follows the above mentioned standard
    # Input : self
    # Output: List of errors/anomalies associated with this Family object

    def validate(self):
        messages = []
        if self.additional_validations is not None:
            self.validations += self.additional_validations
        for v in self.validations:
            results = v(self)
            if results is not None:
                indi_uids = results[3]
                indi_names = results[4]
                indi_involved = ', '.join(
                    [uid + ' (' + name + ')' for uid, name in zip(indi_uids, indi_names)])
                msg = '{type}: Family {uid} {msg}.\nIndividual(s) involved - {indis}'.format(
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
    def __init__(self, filename, db, indi_validations=None, fam_validations=None, sort=None):
        self.indi_validations = indi_validations
        self.fam_validations = fam_validations

        if Gedcom.db_setup(db):
            self.db = db
        else:
            raise

        individuals, families, indi_df, fam_df = self.fileparser(
            filename)

        self.indi_df = indi_df
        self.fam_df = fam_df
        self.individuals = individuals
        self.families = families
        self.reports = self.validate()

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

    @staticmethod
    def db_setup(db_file):
        if os.path.exists(db_file):
            os.remove(db_file)

        conn = None
        success = False

        create_indi_table = '''
                            CREATE TABLE individuals(
                                uid TEXT PRIMARY KEY,
                                name TEXT,
                                sex TEXT,
                                birt TEXT,
                                age TEXT,
                                deat TEXT,
                                alive INTEGER,
                                famc TEXT,
                                fams TEXT
                            )
                            '''
        create_family_table = '''
                                CREATE TABLE families(
                                    uid TEXT PRIMARY KEY,
                                    husb TEXT,
                                    husb_name TEXT,
                                    wife TEXT,
                                    wife_name TEXT,
                                    marr TEXT,
                                    div TEXT,
                                    childrens TEXT
                                )'''

        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute(create_family_table)
            cursor.execute(create_indi_table)
            success = True
        except sqlite3.Error as e:
            print(e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            return success

    def db_insert(self, obj):
        success = False
        insert_query = ''
        if type(obj) is Individual:
            insert_query = '''INSERT INTO individuals(uid, name, sex, birt, age, deat, alive, famc, fams)
                              VALUES (?,?,?,?,?,?,?,?,?)'''
            params = list(obj.as_dict().values())
            # Turn famc and fams list into string representation
            # params[-2] = json.dumps(params[-2])
            # params[-1] = json.dumps(params[-1])
            # Turn alive into int
            params[6] = int(params[6])
        elif type(obj) is Family:
            insert_query = '''INSERT INTO families(uid, husb, husb_name, wife, wife_name, marr, div, childrens)
                              VALUES (?,?,?,?,?,?,?,?)'''
            params = list(obj.as_dict().values())
            # Turn childrens list into string representation
            params[-1] = json.dumps(params[-1])

        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute(insert_query, params)
            conn.commit()
            success = True
        except sqlite3.Error as e:
            print(e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            return success

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
        fam = 0
        indi = 0
        indiData = Individual(
            db=self.db, additional_validations=self.indi_validations)
        familyData = Family(
            db=self.db, additional_validations=self.fam_validations)
        indi_df = pd.DataFrame(columns=list(
            indiData.as_dict().keys()))      # pandas dataframe of all individuals
        fam_df = pd.DataFrame(columns=list(
            familyData.as_dict().keys()))    # pandas dataframe of all families
        individuals = []    # List of all Individual object. Should match the info in indi_df
        families = []       # List of all Family object. Should match the info in family_df

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
                        # insert individual into database
                        if not self.db_insert(indiData):
                            raise
                        # report = indiData.validate()
                        # if len(report) > 0:
                        #     reports[i] = report
                        individuals.append(indiData)
                        indi_df = indi_df.append(
                            indiData.as_dict(), ignore_index=True)
                        indiData = Individual(
                            db=self.db, additional_validations=self.indi_validations)
                        indi = 0
                    if(fam == 1):
                        # Insert family into database
                        if not self.db_insert(familyData):
                            raise
                        # report = familyData.validate()
                        # if len(report) > 0:
                        #     reports[i] = report
                        families.append(familyData)
                        fam_df = fam_df.append(
                            familyData.as_dict(), ignore_index=True)
                        familyData = Family(
                            db=self.db, additional_validations=self.indi_validations)
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
        return individuals, families, indi_df.reset_index(drop=True), fam_df.reset_index(drop=True)

    def validate(self):
        reports = []
        for i in self.individuals:
            r = i.validate()
            if r:
                reports.append(i.validate())

        for f in self.families:
            r = f.validate()
            if r:
                reports.append(f.validate())

        return reports

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
            tables += '\n'.join(sum(self.reports, []))

        return tables

    # def __del__(self):
    #     os.remove(self.db)


if __name__ == '__main__':
    gedcom_wrong = Gedcom('./tests/steven/steven_test_wrong.ged',
                          db='./tests/steven/steven_test_wrong.db', sort='uid')
    gedcom_wrong.pretty_print(
        filename='./tests/steven/steven_gedcom_wrong_table.txt')

    gedcom_correct = Gedcom('./tests/steven/steven_test_correct.ged',
                            db='./tests/steven/steven_test_correct.db', sort='uid')
    gedcom_correct.pretty_print(
        filename='./tests/steven/steven_gedcom_correct_table.txt')

    gedcom1 = Gedcom('Test.ged', db='Test.db', sort='uid')
    gedcom1.pretty_print(filename='gedcom1_table.txt')
