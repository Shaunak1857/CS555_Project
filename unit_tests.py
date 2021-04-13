import unittest
import os

from final_project import *


# Unit tests for Steven.
# US03: Birth should occur before death of an individual
# US04: Marriage should occur before divorce of spouses, and divorce can only occur after marriage
class TestGedcomSteven(unittest.TestCase):
    def setUp(self):
        self.ged_correct = Gedcom(
            './tests/steven/steven_test_correct.ged', './tests/steven/steven_test_correct.db', sort='uid')
        self.ged_wrong = Gedcom(
            './tests/steven/steven_test_wrong.ged', './tests/steven/steven_test_wrong.db', sort='uid')

    def test_birt_after_deat(self):
        indi_wrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='1990 AUG 10',
            deat='1989 NOV 10',
            db='./tests/steven/steven_test_wrong.db'
        )
        expected = ('ERROR', 'First Last', '@I1@',
                    'has a birth date later than his death date')
        received = indi_wrong.validate_birt_deat()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_marr_after_div(self):
        fam_wrong = Family(
            uid='@F1@',
            husb='@I2@',
            husb_name='Husband Name',
            wife='@I3@',
            wife_name='Wife Name',
            marr='2000 MAY 5',
            div='1999 MAY 5',
            db='./tests/steven/steven_test_wrong.db'
        )
        expected = ('ERROR', '@F1@', 'has a marriage date later than its divorce date',
                    ['@I2@', '@I3@'], ['Husband Name', 'Wife Name'])
        received = fam_wrong.validate_marr_div()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_birt_before_marr(self):
        indi_wrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='1990 AUG 10',
            deat='1989 NOV 10',
            famc='@F1@',
            db='./tests/steven/steven_test_wrong.db'
        )
        expected = ('ANOMALY', 'First Last', '@I1@',
                    'has a birth date before his parents\' marriage date')
        received = indi_wrong.validate_birt_before_marr()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_birt_after_div(self):
        indi_wrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='1991 AUG 10',
            deat='2039 NOV 10',
            famc='@F3@',
            db='./tests/steven/steven_test_wrong.db'
        )
        expected = ('ANOMALY', 'First Last', '@I1@',
                    'has a birth date more than 280 days later than his parents\' divorce date')
        received = indi_wrong.validate_birt_before_marr()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_parents_age(self):
        fam_wrong = Family(
            uid='@F5@',
            husb='@I10@',
            husb_name='Joe /Lane/',
            wife='@I11@',
            wife_name='Amy /Luis/',
            childrens=['@I8@', '@I12@'],
            db='./tests/steven/steven_test_wrong.db'
        )
        error_msg = 'Amy /Luis/ is more than 60 years older than her child Henry /Lane/, Joe /Lane/ is more than 80 years older than his child Henry /Lane/, Amy /Luis/ is more than 60 years older than her child Alex /Lane/'
        expected = ('ERROR', '@F5@', error_msg,
                    ['@I11@', '@I10@', '@I8@', '@I12@'], ['Amy /Luis/', 'Joe /Lane/', 'Henry /Lane/', 'Alex /Lane/'])
        received = fam_wrong.validate_parents_age()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_marriage_to_descendants(self):
        fam_wrong = Family(
            uid='@F6@',
            husb='@I4@',
            husb_name='Bruce /Wayne/',
            wife='@I2@',
            wife_name='Mary /Jane/',
            db='./tests/steven/steven_test_wrong.db'
        )
        error_msg = 'Bruce /Wayne/ (@I4@) is married to his descendant Mary /Jane/ (@I2@)'
        expected = ('ERROR', '@F6@', error_msg,
                    ['@I2@', '@I4@'], ['Mary /Jane/', 'Bruce /Wayne/'])
        received = fam_wrong.validate_marriage_to_descendants()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_marriage_to_niblings(self):
        fam_wrong = Family(
            uid='@F8@',
            husb='@I14@',
            husb_name='Gabe /Lane/',
            wife='@I2@',
            wife_name='Mary /Lane/',
            db='./tests/steven/steven_test_wrong.db'
        )
        error_msg = 'Mary /Lane/ (@I2@) is married to her nibling Gabe /Lane/ (@I14@)'
        expected = ('ERROR', '@F8@', error_msg,
                    ['@I2@', '@I14@'], ['Mary /Lane/', 'Gabe /Lane/'])
        received = fam_wrong.validate_marriage_to_niblings()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

        def test_corresponding_entry_indi(self):
        indi_wrong = Individual(
            uid='@I8@',
            name='Not Real',
            famc='@F999@',
            fams='@F888@',
            db='./tests/steven/steven_test_wrong.db'
        )
        error_msg = 'Family @F999@ this individual is a child in does not exist, Family @F888@ this individual is a spouse in does not exist'
        expected = ('ERROR', '@I8@', 'Not Real', error_msg)
        received = indi_wrong.validate_corresponding_entry()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_corresponding_entry_fam(self):
        fam_wrong = Family(
            uid='@F8@',
            husb='@I112@',
            wife='@I321@',
            childrens=['@I9999@', '@I1111@'],
            db='./tests/steven/steven_test_wrong.db'
        )
        error_msg = 'Husband @I112@ does not exist, Wife @I321@ does not exist, Child @I9999@ does not exist, Child @I1111@ does not exist'
        expected = ('ERROR', '@F8@', error_msg, ['@I112@', '@I321@', '@I9999@', '@I1111@'],
                    ['Does Not Exist', 'Does Not Exist', 'Does Not Exist', 'Does Not Exist'])
        received = fam_wrong.validate_corresponding_entry()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_list_living_married(self):
        expected = '''+----+--------+------------------+-------+-------------+-------+--------+---------+--------+--------+
|    | uid    | name             | sex   | birt        |   age | deat   | alive   | famc   | fams   |
|----+--------+------------------+-------+-------------+-------+--------+---------+--------+--------|
|  0 | @I1@   | John /Smith/     | M     | 1969 NOV 10 |    52 |        | True    | @F2@   | @F1@   |
|  1 | @I2@   | Mary /Jane/      | F     | 1972 MAR 18 |    49 |        | True    | @F4@   | @F8@   |
|  2 | @I4@   | Bruce /Wayne/    | M     | 1950 OCT 16 |    71 |        | True    |        | @F4@   |
|  3 | @I5@   | Martha /Barbara/ | F     | 1950 SEP 17 |    71 |        | True    |        | @F4@   |
|  4 | @I6@   | Adam /Smith/     | M     | 1949 JUN 6  |    72 |        | True    |        | @F2@   |
|  5 | @I7@   | Jane /List/      | F     | 1948 SEP 6  |    73 |        | True    |        | @F2@   |
|  6 | @I10@  | Joe /Lane/       | M     | 1850 DEC 20 |   171 |        | True    |        | @F5@   |
|  7 | @I12@  | Alex /Lane/      | M     | 1970 JUN 9  |    51 |        | True    | @F5@   | @F7@   |
|  8 | @I13@  | Alyssa /Rex/     | F     | 1971 MAY 10 |    50 |        | True    | @F4@   | @F7@   |
|  9 | @I14@  | Gabe /Lane/      | M     | 1991 MAY 10 |    30 |        | True    | @F7@   | @F8@   |
| 10 | @I999@ | Not /Real/       | M     | 1991 MAY 10 |    30 |        | True    | @F990@ | @F991@ |
+----+--------+------------------+-------+-------------+-------+--------+---------+--------+--------+'''
        received = self.ged_wrong.list_living_married()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_ged_correct(self):
        received = str(self.ged_correct)

        expected = ''
        with open('./tests/steven/steven_gedcom_correct_table.txt') as f:
            expected = f.read()
        msg = 'Expected:\n' + expected + '\nReceived:\n' + received
        #print(expected, received)

        self.assertEqual(received, expected)

    def test_ged_wrong(self):
        received = str(self.ged_wrong)

        expected = ''
        with open('./tests/steven/steven_gedcom_wrong_table.txt') as f:
            expected = f.read()

        msg = 'Expected: ' + str(expected) + '\nReceived: ' + str(received)

        self.assertEqual(received, expected, msg)

    # def tearDown(self):
    #     os.remove('./tests/steven_test_correct.db')
    #     os.remove('./tests/steven_test_wrong.db')


class TestGedcomBrendan(unittest.TestCase):
    def setUp(self):
        self.ged_correct = Gedcom(
            './tests/steven/steven_test_correct.ged', './tests/steven/steven_test_correct.db', sort='uid')
        self.ged_wrong = Gedcom(
            './tests/brendan/brendan_test_wrong.ged', './tests/brendan/brendan_test_wrong.db', sort='uid')

    # US1: Unit Test, Brendan

    def test_birth_after_current_date(self):
        indi_wrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='2022 AUG 10'
        )

        expected = ('ERROR', 'First Last', '@I1@',
                    'has a birth date later than today\'s date')
        received = indi_wrong.validate_birth_before_current_date()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_death_after_current_date(self):
        indi_wrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='1955 AUG 10',
            deat='2022 AUG 12'
        )

        expected = ('ERROR', 'First Last', '@I1@',
                    'has a death date later than today\'s date')
        received = indi_wrong.validate_death_before_current_date()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_wed_after_current_date(self):
        fam_wrong = Family(
            uid='@F1@',
            husb='@I11@',
            husb_name='Joe Philipson',
            wife='@I2@',
            wife_name='Susan Johnson',
            marr='2023 MAY 5'

        )

        expected = ('ERROR', '@F1@',
                    'has a marriage date later than today\'s date',
                    ['@I11@', '@I2@'], ['Joe Philipson', 'Susan Johnson'])
        received = fam_wrong.validate_marr_before_current_date()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_div_after_current_date(self):
        fam_wrong = Family(
            uid='@F1@',
            husb='@I11@',
            husb_name='Joe Philipson',
            wife='@I2@',
            wife_name='Susan Johnson',
            marr='2020 MAY 5',
            div='2027 MAR 10'

        )

        expected = ('ERROR', '@F1@',
                    'has a divorce date later than today\'s date',
                    ['@I11@', '@I2@'], ['Joe Philipson', 'Susan Johnson'])
        received = fam_wrong.validate_div_before_current_date()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    # US7- age from birth
    def test_age_from_birth(self):
        indi_wrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='1800 AUG 10'
        )

        expected = ('ERROR', '@I1@', 'First Last',
                    'is older than 150 years old')
        received = indi_wrong.validate_age_from_birth()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_age_from_death(self):
        indi_wrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='1850 AUG 10',
            deat='2005 AUG 12'
        )

        expected = ('ERROR', '@I1@', 'First Last',
                    'is older than 150 years old')
        received = indi_wrong.validate_age_from_birth()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_multipleBirths(self):
        fam_wrong = Family(db='./tests/brendan/brendan_sprint2_tests.db')

        fam_wrong = fam_wrong.db_family_select('@F4@')

        expected = ('ERROR', '@F4@', 'cannot have more than 5 children at once.', 'Individual(s) involved - ',
                    ['@I9@', '@I10@'], ['Jack /Fakename/', 'Judy /Rickles/'])

        received = fam_wrong.validate_multipleBirths()
        
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)

        self.assertEqual(received, expected, msg)
    
    def test_first_cousin_marriage(self):
        fam_wrong = Family(db='./tests/brendan/brendan_sprint2_tests.db')

        fam_wrong = fam_wrong.db_family_select('@F1@')

        expected = ('ERROR', '@F1@', 'cannot marry as they are first cousins.', 'Individual(s) involved - ',
                    ['@I1@', '@I8@'], ['John /Personson/', 'Judy /Realperson/'])

        received = fam_wrong.validate_firstCousinMarriage()
        
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)

        self.assertEqual(received, expected, msg)

    def test_ged_correct(self):
        received = str(self.ged_correct)

        expected = ''
        with open('./tests/steven/steven_gedcom_correct_table.txt') as f:
            expected = f.read()
        msg = 'Expected:\n' + expected + '\nReceived:\n' + received
        #print(expected, received)

        self.assertEqual(received, expected)

    def test_ged_wrong(self):
        received = str(self.ged_wrong)

        expected = ''
        with open('./tests/brendan/brendan_gedcom_wrong_table.txt') as f:
            expected = f.read()

        msg = 'Expected: ' + str(expected) + '\nReceived: ' + str(received)

        self.assertEqual(received, expected, msg)


class TestGedcomRachi(unittest.TestCase):
    def setUp(self):
        self.ged_correct = Gedcom(
            './tests/rachi/lopez.ged', './tests/rachi/lopez.db', sort='uid')
        self.ged_wrong = Gedcom(
            './tests/rachi/lopez.ged', './tests/rachi/lopez.db', sort='uid')

    # US5 : Unit Test, Rachi
    def test_mar_before_deat(self):
        fam_wrong = Family(
            uid='@F1@',
            husb='@I11@',
            husb_name='Joe Philipson',
            wife='@I2@',
            wife_name='Susan Johnson',
            marr='2000 MAY 5',
            div='1999 MAY 5',
            db='Test.db'
        )

        expected = ('ERROR', '@I11@', 'has a marriage date after his death date',
                    ['@I11@', '@I2@'], ['Joe Philipson', 'Susan Johnson'])

        received = fam_wrong.validate_marr_before_death()

        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)

        self.assertEqual(received, expected, msg)

    # US6 : Unit Test, Rachi
    def test_div_before_deat(self):
        fam_wrong = Family(
            uid='@F1@',
            husb='@I11@',
            husb_name='Joe Philipson',
            wife='@I2@',
            wife_name='Susan Johnson',
            marr='2000 MAY 5',
            div='1999 MAY 5',
            db='Test.db'
        )

        expected = ('ERROR', '@I11@', 'has a divorce date after his death',
                    ['@I11@', '@I2@'], ['Joe Philipson', 'Susan Johnson'])

        received = fam_wrong.validate_divorce_before_death()

        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)

        self.assertEqual(received, expected, msg)
        
    # US 11 No Bigamy
    def test_bigamy(self):
        fam_wrong = Family(
            uid='@F1@',
            husb='@I11@',
            husb_name='Joe Philipson',
            wife='@I2@',
            wife_name='Susan Johnson',
            marr='2000 MAY 5',
            div='1999 MAY 5',
            db='Test.db'
        )

        expected = """ERROR: Family ['@F4@', '@F9@'] Marriage should not occur during marriage to another spouse.
                    Individual(s) involved - @I5@ (Jane /Adams/), @I19@ (Alisha /Jones/)"""
        received = fam_wrong.validate_bigamy()

        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)

<<<<<<< HEAD
        #self.assertEqual(received, expected, msg)
    
    # 13 Sibling Spacing
=======
        self.assertEqual(received, expected, msg)

    # US 13 Sibling Spacing
>>>>>>> 60579e3cbea1ec9910796fe393c5c78b0e2906dc
    def test_siblings(self):
        fam_wrong = Family(
            uid='@F1@',
            husb='@I11@',
            husb_name='Joe Philipson',
            wife='@I2@',
            wife_name='Susan Johnson',
            marr='2000 MAY 5',
            div='1999 MAY 5',
            db='Test.db'
        )

        expected = "ERROR : SIBLINGS TOGETHER"
        expected = """ERROR: Family @F1@ Birthdate of siblings should be more than 8 months apart or less than 2 days apart.
                        Individual(s) involved - @I3@ (Steve /Tester/), @I8@ (Jim /Tester/)"""

        received = fam_wrong.validate_checksiblings()

        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        
        self.assertEqual(received, expected, msg)
    
    # US 25: Unique first names in families
    def test_validate_unique_first_name(self):
        fam_wrong = Family(
            uid='@F1@',
            husb='@I11@',
            husb_name='Joe Philipson',
            wife='@I2@',
            wife_name='Susan Johnson',
            marr='2000 MAY 5',
            div='1999 MAY 5',
            db='Test.db'
        )
        expected = """ERROR: Family @F70@ No more than one child with the same name and birth date should appear in a family.
                        Individual(s) involved - @I22@ (Julio /Lopez/), @I23@ (Julio /Lopez/)"""
        received = fam_wrong.validate_unique_first_name()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        
        self.assertEqual(received, expected, msg)

    
    def test_ged_correct(self):
        received = str(self.ged_correct)

        expected = ''
        with open('./tests/steven/steven_gedcom_correct_table.txt') as f:
            expected = f.read()
        msg = 'Expected:\n' + expected + '\nReceived:\n' + received

        self.assertEqual(received, expected)

    def test_ged_wrong(self):
        received = str(self.ged_wrong)

        expected = ''
        with open('./tests/rachi/rachi_wrong_table.txt') as f:
            expected = f.read()

        msg = 'Expected: ' + str(expected) + '\nReceived: ' + str(received)

        self.assertEqual(received, expected, msg)

        
class TestGedcomShaunak(unittest.TestCase):
    def setUp(self):
        self.ged_correct = Gedcom(
            './tests/steven/steven_test_correct.ged', './tests/steven/steven_test_correct.db', sort='uid')
        self.ged_wrong = Gedcom(
            './tests/steven/steven_test_wrong.ged', './tests/steven/steven_test_wrong.db', sort='uid')

    def test_validate_marr_after_14(self):
        # unit test US10 Shaunak Saklikar
        familyWrong = Family(
            uid="@F4@",
            husb="@I4@",
            husb_name="Bruce Wayne",
            wife="@I5@",
            wife_name="Martha Barbara",
            marr="1940 NOV 6",
            div="",
            childrens="[@I2@]",
            db='./tests/steven/steven_test_wrong.db'
        )
        expected = ('Error', '@F4@', ' has married before the age of 14',
                    ['@I4@', '@I5@'], ['Bruce Wayne', 'Martha Barbara'])

        received = familyWrong.validate_marr_after_14()

        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_birth_before_marr_US02(self):
        # unit test US02 Shaunak Saklikar
        indiWrong = Individual(
            uid='@I4@',
            name='Bruce Wayne',
            sex='M',
            birt='1950 OCT 16',
            deat='2050 OCT 20',
            fams='@F4@',
            db='./tests/steven/steven_test_wrong.db'

        )

        expected = ('Error', '@I4@', 'Bruce Wayne',
                    'has married before its birth date')
        received = indiWrong.birth_before_marr_US02()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_birth_before_death_of_parents(self):
        # unit test US09 Shaunak Saklikar PART 1
        indiWrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='1971 JAN 5',
            deat='2050 OCT 20',
            famc='@F3@',
            db='Test.db'
        )
        expected = ('Error', '@I1@', 'First Last',
                    'is born after death of mother')
        received = indiWrong.birth_before_death_of_parents()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test2_birth_before_death_of_parents(self):
        # unit test US09 Shaunak Saklikar PART 2
        indiWrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='1998 JAN 5',
            deat='2050 OCT 20',
            famc='@F2@',
            db='Test.db'
        )
        expected = ('Error', '@I1@', 'First Last',
                    'is born before 9 months after death of father')
        received = indiWrong.birth_before_death_of_parents()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    def test_ged_correct(self):
        received = str(self.ged_correct)

        expected = ''
        with open('./tests/steven/steven_gedcom_correct_table.txt') as f:
            expected = f.read()
        msg = 'Expected:\n' + expected + '\nReceived:\n' + received
        #print(expected, received)

        self.assertEqual(received, expected)
        
    def test_siblingsShouldNotBeMarried(self):
        familyWrong = Family(
            uid="@F4@",
            husb="@I13@",
            husb_name="Alex Jane",
            wife="@I2@",
            wife_name="Mary Lane",
            marr="1940 DEC 6",
            div="",
            childrens="[@I13@]",
            db='./tests/steven/steven_test_wrong.db'
        )
        expected = ('Error', '@F4@', ' are married siblings',
                    ['@I13@', '@I2@'], ['Alex Jane', 'Mary Lane'])

        received = familyWrong.validate_siblingsShouldNotBeMarried()

        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)
        
        
    def test_maleSameLastName(self):
        familyWrong = Family(
            uid="@F4@",
            husb="@I13@",
            husb_name="Alex /Jane/",
            wife="@I2@",
            wife_name="Mary Lane",
            marr="1940 DEC 6",
            div="",
            childrens=['@I4@'],
            db='./tests/steven/steven_test_wrong.db'
        )
        expected = ('Error:', '@F4@', ' doesnt have sme male last names',
                    ['@I13@', '@I4@'], ['Alex /Jane/', 'Bruce /Wayne/'])

        received = familyWrong.validate_maleSameLastName()
        
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)
        
        
    def test_fewerThan15Siblings(self):
        familyWrong = Family(
            uid="@F4@",
            husb="@I13@",
            husb_name="Alex Jane",
            wife="@I2@",
            wife_name="Mary Lane",
            marr="1940 DEC 6",
            div="",
            childrens=['@I4@', '@I1@', '@I5@', '@I3@', '@I4@', '@I6@', '@I7@', '@I8@', '@I9@', '@I10@', '@I11@', '@I13@', '@I14@', '@I27@', '@I23@', '@I24@', '@I118@'],
            db='./tests/steven/steven_test_wrong.db'
        )
        expected = ('Error: ', '@F4@', 'has a children greater than 15',
                    ['@I13@', '@I2@'], ['Alex Jane', 'Mary Lane'])

        received = familyWrong.validate_fewerThan15Siblings()
        
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)
        
        
    def test_correctGenderRole(self):
        familyWrong = Family(
            uid="@F4@",
            husb="@I4@",
            husb_name="Bruce /Wayne/",
            wife="@I7@",
            wife_name="Jane /List/",
            marr="1940 DEC 6",
            div="",
            childrens=[],
            db='./tests/steven/steven_test_wrong.db'
        )
        expected = ('Error:', '@F4@', ' has wrong sex',
                    ['@I7@', '@I4@'], ['Jane /List/', 'Bruce /Wayne/'])

        received = familyWrong.validate_correctGenderRole()

        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)
        
    def test_orderSiblingsByAges(self):
        familyWrong = Family(
            uid="@F4@",
            husb="@I13@",
            husb_name="Alex Jane",
            wife="@I2@",
            wife_name="Mary Lane",
            marr="1940 DEC 6",
            div="",
            childrens=['@I4@', '@I1@', '@I5@', '@I3@', '@I4@', '@I6@', '@I7@', '@I8@', '@I9@',
                       '@I10@', '@I11@', '@I13@', '@I14@', '@I27@', '@I23@', '@I24@', '@I118@'],
            db='./tests/steven/steven_test_wrong.db'
        )
        expected = ('Error: ', '@F4@', 'has a children greater than 15',
                    ['@I13@', '@I2@'], ['Alex Jane', 'Mary Lane'])

        received = familyWrong.validate_orderSiblingsByAge()

        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        #self.assertEqual(received, expected, msg)


def steven_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestGedcomSteven('test_birt_after_deat'))
    suite.addTest(TestGedcomSteven('test_marr_after_div'))
    suite.addTest(TestGedcomSteven('test_birt_before_marr'))
    suite.addTest(TestGedcomSteven('test_birt_after_div'))
    suite.addTest(TestGedcomSteven('test_parents_age'))
    suite.addTest(TestGedcomSteven('test_marriage_to_descendants'))
    suite.addTest(TestGedcomSteven('test_marriage_to_niblings'))
    suite.addTest(TestGedcomSteven('test_ged_correct'))
    # suite.addTest(TestGedcomSteven('test_ged_wrong'))

    return suite


def rachi_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestGedcomRachi('test_mar_before_deat'))
    suite.addTest(TestGedcomRachi('test_div_before_deat'))
    suite.addTest(TestGedcomRachi('test_ged_correct'))
    suite.addTest(TestGedcomRachi('test_siblings'))
    suite.addTest(TestGedcomRachi('test_bigamy'))
    # suite.addTest(TestGedcomRachi('test_ged_wrong'))

    return suite


def brendan_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestGedcomBrendan('test_birth_after_current_date'))
    suite.addTest(TestGedcomBrendan('test_death_after_current_date'))
    suite.addTest(TestGedcomBrendan('test_death_after_current_date'))
    suite.addTest(TestGedcomBrendan('test_wed_after_current_date'))
    suite.addTest(TestGedcomBrendan('test_div_after_current_date'))
    suite.addTest(TestGedcomBrendan('test_age_from_birth'))
    suite.addTest(TestGedcomBrendan('test_age_from_death'))
    suite.addTest(TestGedcomBrendan('test_multipleBirths'))
    suite.addTest(TestGedcomBrendan('test_first_cousin_marriage'))
    # suite.addTest(TestGedcomBrendan('test_ged_wrong'))

    return suite


def shaunak_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestGedcomShaunak('test_validate_marr_after_14'))
    suite.addTest(TestGedcomShaunak('test_birth_before_marr_US02'))
    suite.addTest(TestGedcomShaunak('test_birth_before_death_of_parents'))
    suite.addTest(TestGedcomShaunak('test2_birth_before_death_of_parents'))
    suite.addTest(TestGedcomShaunak('test_ged_correct'))
    suite.addTest(TestGedcomShaunak('test_siblingsShouldNotBeMarried'))
    suite.addTest(TestGedcomShaunak('test_maleSameLastName'))
    suite.addTest(TestGedcomShaunak('test_fewerThan15Siblings'))
    suite.addTest(TestGedcomShaunak('test_orderSiblingsByAges'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(steven_suite())
    runner.run(rachi_suite())
    runner.run(brendan_suite())
    runner.run(shaunak_suite())
