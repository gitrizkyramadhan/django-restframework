from datetime import datetime, timedelta
import MySQLdb
import logging
from nlp_rivescript import Nlp
from log_mongo import MongoLog


class BJPayService() :

    def __init__(self):
        print "BJPayService is loaded"
        with open('BJCONFIG.txt') as f:
            content = f.read().splitlines()
        f.close()

        self.MYSQL_HOST=content[12].split('=')[1]
        self.MYSQL_USER=content[13].split('=')[1]
        self.MYSQL_PWD=content[14].split('=')[1]
        self.MYSQL_DB=content[15].split('=')[1]

        self._setup_logger('F_BJPAY', '/home/bambangs/LOGBJ/F_BJPAY.log')
        self._setup_logger('F_BJPTRX', '/home/bambangs/LOGBJ/F_BJPTRX.log')
        self.F_BJPAY = logging.getLogger('F_BJPAY')
        self.F_BJPTRX = logging.getLogger('F_BJPTRX')
        self.mongo_log = MongoLog()

        self._min_balance = 0

        self.lineNlp = Nlp()

    def _setup_logger(self,loggername, logfile):
        l = logging.getLogger(loggername)
        fileHandler = logging.FileHandler(logfile, mode='a')
        streamHandler = logging.StreamHandler()
        l.setLevel(level=logging.INFO)
        l.addHandler(fileHandler)
        l.addHandler(streamHandler)

    def _write_log(self, logger, message):
        print message
        # logger.info(message)

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


    def _set_redis(self, msisdn, amount, va_number, phone):
        # payload = self.lineNlp.redisconn.get("bjpay/" + msisdn)
        # current_balance = int(payload.split('|')[0])
        # va_no = payload.split('|')[1]
        # phone = payload.split('|')[2]

        payload = str(amount) + "|" + va_number + "|" + phone
        self.lineNlp.redisconn.set("bjpay/%s" % (msisdn), payload)


    def _get_redis(self, msisdn):
        payload = self.lineNlp.redisconn.get("bjpay/" + msisdn)
        current_balance = int(payload.split('|')[0])
        va_no = payload.split('|')[1]
        phone = payload.split('|')[2]
        return (current_balance, va_no, phone)


    def register(self, msisdn, va_number, phone, initial_amount = 0):
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')

        check_row = self._request("SELECT * FROM bjpay_account WHERE va_no = '"+va_number+"'")
        if check_row :
            last_amt = 0
            last_msisdn = ""
            for row in check_row:
                last_amt = int(row[3])
                last_msisdn = row[1]
            # for row in check_row:
            self.lineNlp.redisconn.delete("bjpay/%s" % (last_msisdn))
            print "BJPAY EXIST :: msisdn="+msisdn+", va_number="+va_number+", phone="+phone
            sql = "UPDATE bjpay_account SET update_time=now(), msisdn='"+msisdn+"' where va_no='"+va_number+"'"
            self._insert(sql)
            # initial_amount = row[0]
            self._set_redis(msisdn, last_amt, va_number, phone)
        else :
            sql = "INSERT INTO bjpay_account (va_no, msisdn, phone_number, amount, register_date, update_time, status) VALUES ('"+va_number+"', '"+msisdn+"', '"+phone+"', '0', now(), now(), 1)"
            self._insert(sql)
            self._write_log(self.F_BJPAY, "Register BJPAY :: msisdn="+str(msisdn)+", va_number="+str(va_number)+", phone="+str(phone)+", initial_amount=0, log_dtm="+str(logDtm))
            self.mongo_log.log_bjpay_register(msisdn, phone, va_number)

            if int(initial_amount) != 0:
                self._set_redis(msisdn, initial_amount, va_number, phone)
                self.credit(msisdn, phone, initial_amount, "1000", "Initial amount for account "+va_number)
            self._set_redis(msisdn, initial_amount, va_number, phone)


    def transfer(self, originPhone, destinationPhone, amount):
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')


    def fetch_balance(self, msisdn, phone):
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
        check_row = self._request("SELECT * FROM bjpay_account WHERE va_no = '" + phone + "'")

        payload = self.lineNlp.redisconn.get("bjpay/" + msisdn)
        current_balance = int(payload.split('|')[0])
        va_no = payload.split('|')[1]
        phone = payload.split('|')[2]


    def update_db_balance(self, msisdn, phone):
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')

        if self.lineNlp.redisconn.exists("bjpay/%s" % (msisdn)):
            bjpay_row = self._request("SELECT * FROM bjpay_account WHERE phone_number = '" + phone + "'")
            if bjpay_row :
                (current_balance, va_no, redis_phone) = self._get_redis(msisdn)
                sql = "UPDATE bjpay_account SET amount = "+str(current_balance)+" WHERE phone_number='"+str(phone)+"'"
                self._insert(sql)
            else:
                raise Exception('') #bjpay tidak ada
        else:
            raise Exception('')  # bjpay tidak disimpan di redis


    def update_redis_balance(self, msisdn, phone):
        bjpay_row = self._request("SELECT * FROM bjpay_account WHERE va_no = '" + phone + "'")
        if bjpay_row:
            self._set_redis(msisdn, bjpay_row[0], bjpay_row[1], phone)


    def debit(self, msisdn, transaction_amount, transaction_id, description):
        (current_balance, va_no, redis_phone) = self._get_redis(msisdn)
        remaining_amount = int(current_balance) - int(transaction_amount)
        if int(remaining_amount) < self._min_balance :
            return "3001"
        else :
            logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO account_statement (id, trx_date, type, user_id, va_no, amount, description, trx_id) VALUES ('', now(), 'D', '"+str(msisdn)+"', '"+str(redis_phone)+"', '"+str(transaction_amount) + "', '" + str(description) + "', '" + str(transaction_id) + "')"
            self._write_log(self.F_BJPTRX, "DEBIT TRX :: msisdn=" + str(msisdn) +", phone=" + str(redis_phone) +", amount=" + str(transaction_amount) + ", transaction_id=" + str(transaction_id) + ", log_dtm=" + str(logDtm))
            self.mongo_log.log_debit(msisdn, redis_phone, transaction_amount, transaction_id, description)

            (current_balance, va_no, redis_phone) = self._get_redis(msisdn)

            self._set_redis(msisdn, remaining_amount, va_no, redis_phone)
            self.update_db_balance(msisdn, redis_phone)
            self._insert(sql)


    def credit(self, msisdn, phone, transaction_amount, transaction_id, description):
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO account_statement (id, trx_date, type, user_id, va_no, amount, description, trx_id) VALUES ('', now(), 'C', '" + str(msisdn) + "', '" + str(phone) + "', '" + str(transaction_amount) + "', '" + str(description) + "', '" + str(transaction_id) + "')"
        self._write_log(self.F_BJPTRX, "CREDIT TRX :: msisdn=" + str(msisdn) +", phone=" + str(phone) +", amount=" + str(transaction_amount) + ", transaction_id=" + str(transaction_id) + ", log_dtm=" + str(logDtm))
        self.mongo_log.log_credit(msisdn, phone, transaction_amount, transaction_id, description)

        (current_balance, va_no, redis_phone) = self._get_redis(msisdn)
        total_amount = int(current_balance) + int(transaction_amount)

        self._set_redis(msisdn, total_amount, va_no, redis_phone)
        self.update_db_balance(msisdn, phone)
        self._insert(sql)

    def is_exist(self, msisdn):
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
        if self.lineNlp.redisconn.exists("bjpay/%s" % (msisdn)):
            return True
        else :
            # sql = "SELECT * FROM bjpay_account WHERE va_no = '" + phone + "'"
            # row = self._request(sql)
            # if row :
            #     payload = str(row[0]) + "|" + row[1] + "|" + row[2]
            #     self.lineNlp.redisconn.set("bjpay/%s" % (msisdn), payload)
            #     return True
            # else :
            #     return False
            return False

    def check_balance(self, msisdn, transaction_amount):
        (current_balance, va_no, redis_phone) = self._get_redis(msisdn)
        print "CHECKING BALANCE FOR ID : "+msisdn+", BALANCE : "+str(current_balance)+", TX_AMOUNT : "+str(transaction_amount)
        remaining_amount = int(current_balance) - int(transaction_amount)
        if int(remaining_amount) < self._min_balance :
            return "3001"

    def get(self, msisdn):
        return self._get_redis(msisdn)