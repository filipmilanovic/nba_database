# DEFINE USEFUL DICTIONARIES
import datetime as dt

season_start_dates = {2017: dt.datetime(2016, 10, 25),
                      2016: dt.datetime(2015, 10, 27),
                      2015: dt.datetime(2014, 10, 28),
                      2014: dt.datetime(2013, 10, 29),
                      2013: dt.datetime(2012, 10, 30),
                      2012: dt.datetime(2011, 12, 25),
                      2011: dt.datetime(2010, 10, 26),
                      2010: dt.datetime(2009, 10, 27),
                      2009: dt.datetime(2008, 10, 28),
                      2008: dt.datetime(2007, 10, 30),
                      2007: dt.datetime(2006, 10, 31),
                      2006: dt.datetime(2005, 11, 1),
                      2005: dt.datetime(2004, 11, 2),
                      2004: dt.datetime(2003, 10, 28),
                      2003: dt.datetime(2002, 10, 29),
                      2002: dt.datetime(2001, 10, 30),
                      2001: dt.datetime(2000, 10, 31)
                      }

positions = {'Center': 'C',
             'Power': 'PF',
             'Small': 'SF',
             'Shooting': 'SG',
             'Point': 'PG'}

period_name = {'1st': 'Q1',
               '2nd': 'Q2',
               '3rd': 'Q3',
               '4th': 'Q4',
               'OT1': 'OT1',
               'OT2': 'OT2',
               'OT3': 'OT3',
               'OT4': 'OT4'}
