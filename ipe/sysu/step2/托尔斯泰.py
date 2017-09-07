import redis
def test():
    rediscon = redis.StrictRedis(host='localhost',port=6379)
    print(rediscon)
    rediscon.setex('mykey',100,'hehe')

test()
