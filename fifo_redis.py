import redis

redisconn = redis.StrictRedis(password="1ee5f1d25745de4d5ccc09a69119da6c82636cdb20bed280e595ed16cee6301a")

def save_last10chat(dtm, msisdn, mesg):
    chat = dtm + "," + msisdn + "," + mesg
    id = "savedchat/" + msisdn
    chat_len = len(redisconn.lrange(id,0,-1))
    if chat_len > 2:
        redisconn.lpop(id)	
    redisconn.rpush(id, chat)
                            
                              
save_last10chat('2016-10-21 00:00:01','123','halo')
save_last10chat('2016-10-21 00:00:02','123','halo2')
save_last10chat('2016-10-21 00:00:03','123','halo3')
print redisconn.lrange('savedchat/123',0,-1)
save_last10chat('2016-10-21 00:00:04','123','halo4')
print redisconn.lrange('savedchat/123',0,-1)