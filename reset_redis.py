from nlp_rivescript import Nlp

lineNlp = Nlp()


lineNlp.redisconn.delete("profiling/U6fb98eb0f44be13523bbabd566e47dc4")
lineNlp.redisconn.delete("profiling/Ud88f406a9eeb745ac5e62f4595e5b105")
lineNlp.redisconn.delete("profiling/U90a846efb4bc03eec9e66cbf61fea960")
lineNlp.redisconn.delete("profiling/U06ebb682542ad76886a4a202d9ac5094")