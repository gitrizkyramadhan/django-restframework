from datetime import datetime, timedelta
import MySQLdb
import logging
from nlp_rivescript import Nlp

class UserProfileService():

    def __init__(self):
        print "UserProfileService is loaded"
        with open('BJCONFIG.txt') as f:
            content = f.read().splitlines()
        f.close()

        self.MYSQL_HOST=content[12].split('=')[1]
        self.MYSQL_USER=content[13].split('=')[1]
        self.MYSQL_PWD=content[14].split('=')[1]
        self.MYSQL_DB=content[15].split('=')[1]


    def _request(self, sql):
        try:
            db_connect = MySQLdb.connect(host=self.MYSQL_HOST, port=3306, user=self.MYSQL_USER, passwd=self.MYSQL_PWD, db=self.MYSQL_DB)
            # Create cursor
            cursor = db_connect.cursor()
            cursor.execute(sql)
            sqlout = cursor.fetchall()
            return sqlout
        except MySQLdb.Error, e:
            logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
            print e.args
            print "ERROR: %d: %s" % (e.args[0], e.args[1])


    def _insert(self, sql):
        try:
            db_connect = MySQLdb.connect(host=self.MYSQL_HOST, port=3306, user=self.MYSQL_USER, passwd=self.MYSQL_PWD, db=self.MYSQL_DB)
            # Create cursor
            cursor = db_connect.cursor()
            cursor.execute(sql)
            db_connect.commit()
        except MySQLdb.Error, e:
            logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
            print e.args
            print "ERROR: %d: %s" % (e.args[0], e.args[1])


    def update_profile(self, msisdn, **params):
        sql_select = "SELECT * FROM user_profile WHERE msisdn = '"+msisdn+"'"
        row = self._request(sql_select)
        if row :
            data = ''
            for key, value in params.iteritems():
                data += str(key) + " = '" + str(value) + "', "

            data = data[:len(data) - 1]
            sql = "UPDATE user_profile SET " + data + " WHERE msisdn='"+msisdn+"'"
            self._insert(sql)
        else :
            sql = "INSERT INTO user_profile (msisdn) VALUES ('" + msisdn + "')"
            self._insert(sql)
