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
        
        
    
    
    
    
    
    def test_validate_marr_after_14(self):
        #unit test US10 Shaunak Saklikar
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
        #unit test US02 Shaunak Saklikar
        indiWrong = Individual(
            uid='@I4@',
            name='Bruce Wayne',
            sex='M',
            birt='1950 OCT 16',
            deat='2050 OCT 20',
            fams='@F4@',
            db='./tests/steven/steven_test_wrong.db'
            
        )

        expected =('Error', '@I4@', 'Bruce Wayne',
                  'has married before its birth date')
        received = indiWrong.birth_before_marr_US02()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)
        
    def test_birth_before_death_of_parents(self):
        #unit test US09 Shaunak Saklikar PART 1
        indiWrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='1971 JAN 5',
            deat='2050 OCT 20',
            famc='@F3@',
            db='Test.db'
        )
        expected =('Error', '@I1@', 'First Last', 'is born after death of mother')
        received = indiWrong.birth_before_death_of_parents()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)
        
        
        
        
        
        
    def test2_birth_before_death_of_parents(self):
        #unit test US09 Shaunak Saklikar PART 2
        indiWrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='1998 JAN 5',
            deat='2050 OCT 20',
            famc='@F2@',
            db='Test.db'
        )
        expected = ('Error', '@I1@', 'First Last', 'is born before 9 months after death of father')
        received = indiWrong.birth_before_death_of_parents()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)
        

    # def tearDown(self):
    #     os.remove('./tests/steven_test_correct.db')
    #     os.remove('./tests/steven_test_wrong.db')


class TestGedcomBrendan(unittest.TestCase):
    def setUp(self):
        self.ged_correct = Gedcom(
            './tests/steven/steven_test_correct.ged', './tests/steven/steven_test_correct.db', sort='uid')
        self.ged_wrong = Gedcom(
            './tests/brendan/brendan_test_wrong.ged', './tests/steven/steven_test_wrong.db', sort='uid')
    
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
                    'has a marriage date later than today\'s date')
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
            div='2027 MARCH 10'

        )

        expected = ('ERROR', '@F1@',
                    'has a divorce date later than today\'s date')
        received = fam_wrong.validate_div_before_current_date()
        msg = 'Expected:\n' + str(expected) + '\nReceived:\n' + str(received)
        self.assertEqual(received, expected, msg)

    #US7- age from birth
    def test_age_from_birth(self):
        indi_wrong = Individual(
            uid='@I1@',
            name='First Last',
            sex='M',
            birt='1800 AUG 10'
        )

        expected = ('ERROR', 'First Last', '@I1@',
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

        expected = ('ERROR', 'First Last', '@I1@',
                    'is older than 150 years old')
        received = indi_wrong.validate_age_from_birth()
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


class TestGedcomRachi(unittest.TestCase):
    def setUp(self):
        self.ged_correct = Gedcom(
            './tests/steven/steven_test_correct.ged', './tests/steven/steven_test_correct.db', sort='uid')
        self.ged_wrong = Gedcom(
            './tests/steven/steven_test_wrong.ged', './tests/steven/steven_test_wrong.db', sort='uid')

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



def steven_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestGedcomSteven('test_birt_after_deat'))
    suite.addTest(TestGedcomSteven('test_marr_after_div'))
    suite.addTest(TestGedcomSteven('test_birt_before_marr'))
    suite.addTest(TestGedcomSteven('test_birt_after_div'))
    suite.addTest(TestGedcomSteven('test_ged_correct'))
    suite.addTest(TestGedcomSteven('test_ged_wrong'))
    suite.addTest(TestGedcomSteven('test_validate_marr_after_14'))
    suite.addTest(TestGedcomSteven('test_birth_before_marr_US02'))
    suite.addTest(TestGedcomSteven('test_birth_before_death_of_parents'))
    suite.addTest(TestGedcomSteven('test2_birth_before_death_of_parents'))

    return suite


def rachi_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestGedcomRachi('test_mar_before_deat'))
    suite.addTest(TestGedcomRachi('test_div_before_deat'))
    suite.addTest(TestGedcomRachi('test_ged_correct'))
    suite.addTest(TestGedcomRachi('test_ged_wrong'))

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
    suite.addTest(TestGedcomBrendan('test_ged_correct'))
    suite.addTest(TestGedcomBrendan('test_ged_wrong'))

    return suite

    


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(steven_suite())
    runner.run(rachi_suite())
    runner.run(brendan_suite())
