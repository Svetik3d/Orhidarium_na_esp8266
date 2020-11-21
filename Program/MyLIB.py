import machine
import onewire
import ds18x20
import dht
import time
import libraries_AM2320
import usocket
import ntptime
import http
import network
import webrepl

#Везде при указании пина используется GPIO номер

# Т к в Micropython time.time() возвращает, не время с 01-01-1970, а 
# время с 01-01-2000, то добавляем эту константу, чтобы превратить 
# time.time в unixtime
MAGIC_TIME_CONST = 946684800

class Orhidarium(object):
    def __init__(self, s_fan, t_ON, t_OFF, DEBUG_FLAG):
        #Скорость работы вентилятора
        self.s_fan = s_fan
        #Время включения в минутах
        self.t_ON = t_ON
        #Время выключения в минутах
        self.t_OFF = t_OFF
        self.time_now = 0
        self.wlan = network.WLAN(network.STA_IF)
        self.DEBUG_FLAG = DEBUG_FLAG

    #DS18B20
    #По умолчанию пин D2
    def got_data_from_DS18B20(self, DS_p=4):
        ds_pin = machine.Pin(DS_p)
        ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
        roms = ds_sensor.scan()
        if self.DEBUG_FLAG:
            print('Found DS devices: ', roms) #roms - это список, он ищет ВСЕ подключенные на 1 ногу DS18B20
        ds_sensor.convert_temp()
        time.sleep(1)
        #У меня 1 датчик, поэтому roms[0]
        return(ds_sensor.read_temp(roms[0]))

    #Реле SRD-05VDC-SL-C
    #По умолчанию пин D1
    #s - строчка, ON - включить ток, OFF - выключить
    def relay(self, R_p=5):
        r_pin = machine.Pin(R_p, machine.Pin.OUT)
        # ~ print(self.t_OFF, self.time_now, self.t_ON)
        if self.t_OFF >= self.time_now and self.time_now  >= self.t_ON:
            r_pin.value(1)
            if self.DEBUG_FLAG:
                print("ON")
        else:
            r_pin.value(0)
            if self.DEBUG_FLAG:
                print("OFF")

    #Отправка данных в graphite на сервере(ip 192.168.0.1)
    def graphite(self):
 
        # Получаем unixtime
        untime = time.time() + MAGIC_TIME_CONST
        try:
            ds18b20_temp = self.got_data_from_DS18B20()
        except Exception as err:
            if self.DEBUG_FLAG:
                print("Get data for graphite error: %s" % err)
        sock = usocket.socket()
        sock.connect(('192.168.0.1', 2003))
        sock.send("orchid.temp_from_ds18b20 " + str(ds18b20_temp) + " " + str(untime) + "\n")
        if self.DEBUG_FLAG:
            print("Send to graphite")
        sock.close()

    #Ставим правильное время с ntp, возвращаем кортёж (year, month, day, weekday, hours, minutes, seconds, subseconds) [пример (2020, 4, 27, 0, 17, 10, 4, 837)] в UTC, поэтому прибавляем ещё 3 часа
    def set_time(self):
        rtc = machine.RTC()
        ntptime.settime()
        #Время сейчас в минутах 
        self.time_now = (rtc.datetime()[4]+3)*60 + rtc.datetime()[5]
        if self.DEBUG_FLAG:
            print("NTP finish")

    #Файл
    #1 строчка - время вкл
    #2 строчка - время выкл
    #3 строчка - скорость вентилятора
    def get_http(self):
        get_text = http.get('http://192.168.0.1/orchid/config').text.strip().split("\n")
        t_on_m = get_text[0].split(":")
        self.t_ON = int(t_on_m[0])*60 + int(t_on_m[1])
        t_off_m = get_text[1].split(":")
        self.t_OFF = int(t_off_m[0])*60 + int(t_off_m[1])
        self.s_fan = int(get_text[2])
        if self.DEBUG_FLAG:
            print("http finish")

    # Пин вентилятора по умолчанию D5
    def pwm_fan(self, f_p=14):
        pwm = machine.PWM(machine.Pin(f_p), duty=self.s_fan)
        if self.DEBUG_FLAG:
            print("PWM finihed. Speed fan =",self.s_fan)

    #Если не подконектился к wi-fi, то... Конектимся)
    def wifi(self):
        if not self.wlan.isconnected() or self.wlan.ifconfig()[0] != '192.168.0.24':
            # Enable local IP
            self.wlan.active(True)
            self.wlan.ifconfig(('192.168.0.24', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
            while True:
                self.wlan.connect('network name', 'password')
                time.sleep(10)
                if not self.wlan.isconnected():
                    self.wlan.disconnect()
                else:
                    break
            if self.DEBUG_FLAG:
                print("Wi-fi")
