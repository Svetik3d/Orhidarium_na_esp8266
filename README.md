# Orhidarium_na_esp8266

Новая версия управления орхидариумом на плате NodeMCU. Моя прошивка умеет:

    Измерять температуру снаружи
    Включать/выключать лампу по расписанию
    Регулировать скорость вентилятора
    Отправлять данные с датчиков в graphite
    Возможность изменять скорость вентилятора и расписания лампы, меняя файл на сервере, подключаясь к нему по wi-fi.

Ссылки на внешние библиотеки

    DS18b20 https://github.com/micropython/micropython/blob/master/drivers/onewire/ds18x20.py
    Библиотека для работы по http https://github.com/balloob/micropython-http-client/blob/master/http_client.py
