import MyLIB
#Скорость работы вентилятора от 0 до 1000(default)
s_fan = 50
#Время включения в минутах(default)
t_ON = 9*60 + 0
#Время выключения в минутах(default)
t_OFF = 19*60 + 0
#1 - вкл режим отладки(с print), 0 - выкл(без print)
DEBUG_FLAG = 0

orhid = MyLIB.Orhidarium(s_fan, t_ON, t_OFF, DEBUG_FLAG)

MAX = 1

if DEBUG_FLAG:
    STEP = 5
else:
    STEP = 60

funcs = [
    [orhid.wifi, 1],
    [orhid.set_time, 1],
    [orhid.graphite, 1],
    [orhid.get_http, 1],
    [orhid.relay, 1],
    [orhid.pwm_fan, 1]
]

acc = 1
while True:
    time_before = time.time()
    for func, period in funcs:
        if acc % period == 0:
            try:
                func()
                time.sleep(0.5)
            except Exception as err:
                if DEBUG_FLAG:
                    print(err)
                orhid.wifi()
    time_after = time.time()
    if STEP>(time_after - time_before)>0:
        time.sleep(STEP - (time_after - time_before))
    else:
        if DEBUG_FLAG:
            print("ERROR time!!!")
        time.sleep(1)
    if acc == MAX:
        acc = 0
    acc += 1
    if DEBUG_FLAG:
        print("Next step")
