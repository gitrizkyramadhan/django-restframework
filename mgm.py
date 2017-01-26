from dbutils import DBUtil
import random

CODE_LENGTH = 4
CODE_CHAR = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
db = DBUtil()

class MGM():

    def __init__(self):
        print ""

    def generateRefCode(self, msisdn):
        sqlQuery = "SELECT * FROM user_ref_code WHERE msisdn='" + msisdn + "'"
        fetchedRows = db.fetch(sqlQuery)

        if fetchedRows:
            if fetchedRows[0][2]:
                print "Get code from msisdn=%s => %s" % (msisdn, fetchedRows[0][2])
                return fetchedRows[0][2]
            else:
                return self.createNewCode(msisdn, False)
        else :
            return self.createNewCode(msisdn, True)

    def createNewCode(self, msisdn, isNew = True):
        result = ''.join(random.choice(CODE_CHAR) for i in range(CODE_LENGTH))
        result = 'BANGJONI' + result
        print "Create new code for msisdn=%s => %s" % (msisdn, result)
        sqlQuery = "SELECT * FROM user_ref_code WHERE ref_code='" + result + "'"
        fetchedRows = db.fetch(sqlQuery)

        if fetchedRows:
            self.createNewCode(result)
        else:
            if isNew:
                sqlQuery = "INSERT INTO user_ref_code (id, msisdn, ref_code, other_ref_code, generated_date, used_ref_date) VALUES (NULL, '" + msisdn + "', '" + result + "', NULL, now(), NULL)"
                db.execSQL(sqlQuery)
                print sqlQuery
                return result
            else:
                sqlQuery = "UPDATE user_ref_code SET ref_code = '"+result+"', generated_date=now() WHERE msisdn = '"+msisdn+"'"
                db.execSQL(sqlQuery)
                print sqlQuery
                return result

    def useRefCode(self, msisdn, refCode):
        refCode = refCode.upper()
        print "Trying to redeem code for msisdn=%s => %s" % (msisdn, refCode)

        sqlQuery = "SELECT * FROM user_ref_code WHERE ref_code='" + refCode + "'"
        fetchedRowsCode = db.fetch(sqlQuery)
        if not fetchedRowsCode:
            return "1001"  # refcode tidak ditemukan

        sqlQuery = "SELECT * FROM user_ref_code WHERE msisdn='" + msisdn + "'"
        fetchedRows = db.fetch(sqlQuery)

        if fetchedRows:
            if fetchedRows[0][3]:
                return "1002" #refcode sudah pernah digunakan
            sqlQuery = "UPDATE user_ref_code SET other_ref_code='" + refCode + "', used_ref_date=now() WHERE msisdn='" + msisdn + "'"
            db.execSQL(sqlQuery)
            return "200"
        else:
            sqlQuery = "INSERT INTO user_ref_code (id, msisdn, ref_code, other_ref_code, generated_date, used_ref_date) VALUES (NULL, '" + msisdn + "', NULL, '" + refCode + "', NULL, now())"
            db.execSQL(sqlQuery)
            print sqlQuery
            return "200"

    def getMsisdnFromRefCode(self, refCode):
        sqlQuery = "SELECT msisdn FROM user_ref_code WHERE ref_code='" + refCode + "'"
        fetchedRows = db.fetch(sqlQuery)
        if fetchedRows:
            return fetchedRows[0][0]

# mgm = MGM()
# result = mgm.generateRefCode('anuku')
# print mgm.useRefCode('anuku', result)