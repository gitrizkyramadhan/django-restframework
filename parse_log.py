import re

log_path_unstructured = '..\\line3\\celerylog\\'
class UnstructureLog(object):

    def __init__(self):
        
        print "UnstructureLog added ..."

    def parse_celery_log(self, file_name): # result msisdn and location
        def clean(text):
            if text.__contains__('user_id'):
                msisdn = re.findall("'(.*?)'", text)
                return msisdn[0]
            elif text.__contains__('[LOC]'):
                location = re.findall("LOC](.*?)\n", text)
                date_location = re.findall("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}", text)
                return [location[0], date_location[0]]
        file = open(log_path_unstructured + file_name, 'r')
        file.readline()
        list_information = []
        for data in file:
            if 'row_information' in locals():
                if len(row_information) >= 2:
                    row_information = []
            if data.__contains__("=NEW LINE REQUEST="):
                row_information = []
            elif data.__contains__("[LOC]") | data.__contains__("user_id"):
                if 'row_information' in locals():
                    if len(row_information) == 1:
                        if data.__contains__("user_id") & row_information[0].__contains__('user_id'):
                            row_information = []
                        elif data.__contains__("[LOC]") & row_information[0].__contains__('[LOC]'):
                            row_information = []
                        else:
                            row_information.append(data)
                    else:
                        row_information.append(data)
            if 'row_information' in locals():
                if len(row_information) >= 2:
                    if not row_information[0].__contains__("user_id"):
                        a = 0
                        b = 1
                        row_information[b], row_information[a] = row_information[a], row_information[b]
                    row_information[0] = clean(row_information[0])
                    row_information[1] = clean(row_information[1])
                    # print row_information
                    list_information.append(row_information)
        return list_information


log_path_structured = '..\\LOGBJ\\'
class StructuredLog(object):
    
    def __init__(self):
        
        print "StructuredLog added ..."

    def get_pattern_separator(self,file_name):
        
        flatfile_separator = 'flatfile_separator.dat'
        file = open(flatfile_separator, 'r')
        file.readline
        for data in file:
            split_data = data.split('=')
        if split_data[0] == file_name:
            return split_data[1].replace('\n', '')

    def parse_log(self, file_name):
        
        separator = get_pattern_separator(file_name)
        file = open(log_path_structured + file_name,'r')
        file.readline()            
        list_one_row_data = []
        for one_row in file:
            separate_data = re.split(separator, one_row)
            splited_one_row_data = []
            for data in separate_data:
                data_split = data.split('=')
                try:
                    data_split[1]
                    splited_one_row_data.append(data_split[1].strip().replace('\n',''))
                except:
                    splited_one_row_data.append(data_split[0].strip().replace('\n',''))
            list_one_row_data.append(splited_one_row_data)
        return list_one_row_data

# ul = UnstructureLog()
# print ul.parse_celery_log('celery1__20170205_12.log')
# print ul.clean( "Process] [LOC]-6.164737;106.610214\n" )
# for data in ul.parse_celery_log('celery1__20170301_00.log'):
#     print data[0]

