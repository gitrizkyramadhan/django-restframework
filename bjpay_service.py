from datetime import datetime, timedelta
import MySQLdb
import logging
from nlp_rivescript import Nlp


class BJPayService() :

    def __init__(self):
        print "BJPayService is loaded"
        with open('BJCONFIG.txt') as f:
            content = f.read().splitlines()
        f.close()

        self.EMAIL_NOTIF = content[9].split('=')[1]
        self.MYSQL_HOST=content[4].split('=')[1]
        self.MYSQL_USER=content[5].split('=')[1]
        self.MYSQL_PWD=content[6].split('=')[1]
        self.MYSQL_DB=content[7].split('=')[1]

        self._setup_logger('F_BJPAY', '/home/bambangs/LOGBJ/F_BJPAY.log')
        self._setup_logger('F_BJPTRX', '/home/bambangs/LOGBJ/F_BJPTRX.log')
        self.F_BJPAY = logging.getLogger('F_BJPAY')
        self.F_BJPTRX = logging.getLogger('F_BJPTRX')

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
        logger.info(message)

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
            print "BJPAY EXIST :: msisdn="+msisdn+", va_number="+va_number+", phone="+phone
            sql = "UPDATE bjpay_account SET update_time=now(), msisdn='"+msisdn+"'"
            self._insert(sql)
            initial_amount = check_row[0]
        else :
            sql = "INSERT INTO bjpay_account (va_no, msisdn, phone_number, amount, register_date, update_time, status) VALUES ('"+va_number+"', '"+msisdn+"', '"+phone+"', '0', now(), now(), 1)"
            self._insert(sql)
            self._write_log(self.F_BJPAY, "Register BJPAY :: msisdn="+str(msisdn)+", va_number="+str(va_number)+", phone="+str(phone)+", initial_amount="+str(initial_amount)+", log_dtm="+str(logDtm))

            if int(initial_amount) != 0:
                self.credit(msisdn, phone, initial_amount, "", "Initial amount for account "+va_number)
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

    def debit(self, msisdn, phone, transaction_amount, transaction_id, description):
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO account_statement (id, trx_date, type, user_id, va_no, amount, description, trx_id) VALUES ('', now(), 'D', '"+str(msisdn)+"', '"+str(phone)+"', '"+str(transaction_amount) + "', '" + str(description) + "', '" + str(transaction_id) + "')"
        self._write_log(self.F_BJPTRX, "DEBIT TRX :: msisdn=" + str(msisdn) +", phone=" + str(phone) +", amount=" + str(transaction_amount) + ", transaction_id=" + str(transaction_id) + ", log_dtm=" + str(logDtm))

        (current_balance, va_no, redis_phone) = self._get_redis(msisdn)
        total_amount = int(current_balance) + int(transaction_amount)

        self._set_redis(msisdn, total_amount, va_no, redis_phone)
        self.update_db_balance(msisdn, phone)
        self._insert(sql)


    def credit(self, msisdn, phone, transaction_amount, transaction_id, description):
        logDtm = (datetime.now() + timedelta(hours=0)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO account_statement (id, trx_date, type, user_id, va_no, amount, description, trx_id) VALUES ('', now(), 'D', '" + str(msisdn) + "', '" + str(phone) + "', '" + str(transaction_amount) + "', '" + str(description) + "', '" + str(transaction_id) + "')"
        self._write_log(self.F_BJPTRX, "CREDIT TRX :: msisdn=" + str(msisdn) +", phone=" + str(phone) +", amount=" + str(transaction_amount) + ", transaction_id=" + str(transaction_id) + ", log_dtm=" + str(logDtm))

        (current_balance, va_no, redis_phone) = self._get_redis(msisdn)
        total_amount = int(current_balance) - int(transaction_amount)

        self._set_redis(msisdn, total_amount, va_no, redis_phone)
        self.update_db_balance(msisdn, phone)
        self._insert(sql)

