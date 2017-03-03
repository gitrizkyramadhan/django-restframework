from nlp_rivescript import Nlp

lineNlp = Nlp()


lineNlp.redisconn.delete("profiling/U6fb98eb0f44be13523bbabd566e47dc4")
lineNlp.redisconn.delete("profiling/Ud88f406a9eeb745ac5e62f4595e5b105")