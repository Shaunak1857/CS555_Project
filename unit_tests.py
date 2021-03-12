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


def steven_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestGedcomSteven('test_birt_after_deat'))
    suite.addTest(TestGedcomSteven('test_marr_after_div'))
    suite.addTest(TestGedcomSteven('test_birt_before_marr'))
    suite.addTest(TestGedcomSteven('test_birt_after_div'))
    suite.addTest(TestGedcomSteven('test_ged_correct'))
    suite.addTest(TestGedcomSteven('test_ged_wrong'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(steven_suite())
