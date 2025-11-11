
def mahulu_hello():
    return "Hello, testing!"

def get_user_traffic_data():
    import random
    daily_visits = [random.randint(200, 1000) for _ in range(30)]
    return {
        'daily_visits': daily_visits,
        'total_visits': sum(daily_visits),
        'growth': '+8.3%'
    }

def get_helpers():
    return {
        "mahulu_hello": mahulu_hello,
        "get_user_traffic_data": get_user_traffic_data,
    }
