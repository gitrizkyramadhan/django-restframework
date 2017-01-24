
import MySQLdb
from datetime import datetime, timedelta

class DBUtil():
    def fetch(self, sql):
        try:
            db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB)
            # Create cursor
            cursor = db_connect.cursor()
            cursor.execute(sql)
            sqlout = cursor.fetchall()
            return sqlout
        except MySQLdb.Error, e:
            logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
            print e.args
            print "ERROR: %d: %s" % (e.args[0], e.args[1])

    def execSQL(self, sql):
        try:
            db_connect = MySQLdb.connect(host=MYSQL_HOST, port=3306, user=MYSQL_USER, passwd=MYSQL_PWD, db=MYSQL_DB)
            # Create cursor
            cursor = db_connect.cursor()
            cursor.execute(sql)
            db_connect.commit()
        except MySQLdb.Error, e:
            logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
            print e.args
            print "ERROR: %d: %s" % (e.args[0], e.args[1])

with open('BJCONFIG.txt') as f:
    content = f.read().splitlines()
f.close()
MYSQL_HOST=content[4].split('=')[1]
MYSQL_USER=content[5].split('=')[1]
MYSQL_PWD=content[6].split('=')[1]
MYSQL_DB=content[7].split('=')[1]