import datetime
import re
from datetime import datetime
from datetime import date
import pandas as pd
from tabulate import tabulate

today = date.today()
dateList = []


def getIndiByID(indi, iD):
    return next((dictionary for dictionary in indi if dictionary['INDI'] == iD), None)


def getFamByID(fam, iD):
    return next((dictionary for dictionary in fam if dictionary["FAM"] == iD), None)


def getNamebyId(indi, Id):
    name = " "
    for i in indi:
        if (i["INDI"] == Id):
            name = i["NAME"]

    return name


def getAliveById(indi, Id):
    alive = True
    for i in indi:
        if (i["DEAT"] == "NA"):
            alive = True
        else:
            alive = False

    return alive


def calculateage(birth, death):
    from datetime import date
    latest = date.today()
    if death != "NA":
        latest = death.date()

    days_in_year = 365.2425
    age = int((latest - birth.date()).days / days_in_year)
    return str(age)


def search(uid, itemlist):
    for i in itemlist:
        if i["INDI"] == uid:
            return i


def us05(indi, fam, f):
    print("User Story 5 - Marriage before death, Running")
    flag = True
    for families in fam:
        for individuals in indi:
            # checking for husband id is equal to individual id
            if families['HUSB'] == individuals['INDI']:
                # getting death date for husband individual
                m = individuals['DEAT']
                # If individual's death date is not null
                if m != 'NA':
                    # checking for marriage date greater than the individual's death date
                    if families['MARR'] > m:
                        f.write(
                            f"ERROR: INDIVIDUAL : US05 : {individuals['INDI']} : Married {families['MARR']} after husband's ({individuals['INDI']}) death on {individuals['DEAT']} \n")
                        flag = False

            # checking for wife id is equal to individual id
            elif families['WIFE'] == individuals['INDI']:
                # getting death date for wifi individual
                n = individuals['DEAT']
                # If individual's death date is not null
                if n != 'NA':
                    # checking for marriage date greater than the individual's death date
                    if families['MARR'] > n:
                        f.write(
                            f"ERROR: INDIVIDUAL : US05 : {individuals['INDI']} : Married {families['MARR']} after wifi's ({individuals['INDI']}) death on {individuals['DEAT']} \n")
                        flag = False

    print("User Story 5 Completed")
    return flag


def us06(indi, fam, f):
    print("User Story 6 - Divorce before death, Running")
    flag = True
    for families in fam:
        for individuals in indi:
            # checking for husband id is equal to individual id
            if families['HUSB'] == individuals['INDI']:
                # getting death date for husband's individual
                m = individuals['DEAT']
                # If individual's death date is not null and families divorce date is not null
                if m != 'NA' and families['DIV'] != 'NA':
                    # checking for husband's death date less than the divorces date
                    if m < families['DIV']:
                        f.write(
                            f"ERROR: FAMILY : US06 : {individuals['INDI']} : Divorced {families['DIV']} after husband's ({individuals['INDI']}) death on {individuals['DEAT']} \n")
                        flag = False

            # checking for wife id is equal to individual id
            if families['WIFE'] == individuals['INDI']:
                # getting death date for wifi's individual
                n = individuals['DEAT']
                # If individual's death date is not null and families divorce date is not null
                if n != 'NA' and families['DIV'] != 'NA':
                    # checking for wife's death date less than the divorces date
                    if n < families['DIV']:
                        f.write(
                            f"ERROR: FAMILY : US06 : {individuals['INDI']} : Divorced {families['DIV']} after wifi's ({individuals['INDI']}) death on {individuals['DEAT']} \n")
                        flag = False

    print("User Story 6 Completed")
    print(" SPRINT 1 COMPLETED \n \n")
    return flag
