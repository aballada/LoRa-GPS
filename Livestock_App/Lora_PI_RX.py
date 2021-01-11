import mysql.connector
from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD



BOARD.setup()

db = mysql.connector.connect(
    host='localhost',
    user='aballada',
    password='raspberry',
    db='Lora_BD'
)
mycursor = db.cursor()
c = 0
print('Conexión establecida exitosamente con la base de datos')

# LORA
class LoRaRcvCont(LoRa):

    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_freq(868.0)
        self.set_dio_mapping([0] * 6)
        print("Iniciado")

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            sleep(.5)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()
                
    def on_rx_done(self):
        print("\nDato recibido: ")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        dataString = bytes(payload).decode("utf-8", 'ignore')
        print(dataString)
        dataModify = dataString.strip("-@\x00")
        dataList = dataModify.split(",")
        if len(dataList)==3:
            dataString = dataList.append('0')
            dataModify = dataString.strip("-@\x00")
            dataList = dataModify.split(",")
            print(dataList)
            
        if (dataList[1] =='1000.000000' or dataList[2]=='1000.000000') and (dataList[3]=='0' or dataList[3]=='01' or dataList[3]=='0@'):
            print("Falla de señal GPS y recepción de temperatura del Nodo " + str(dataList[0]))
            self.set_mode(MODE.SLEEP)
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT)
            sql = "INSERT INTO GPS (Nodo, Latitud, Longitud, Temperatura, StatusGPS, StatusTemp) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (dataList[0], 'Fail', 'Fail', 'Fail' , 'Fail', 'Fail')
            mycursor.execute(sql, val)
            db.commit()
        if (dataList[1] =='1000.000000' or dataList[2]=='1000.000000') and (dataList[3]!='0'):
            print("No hay señal de GPS del Nodo " + str(dataList[0]))
            self.set_mode(MODE.SLEEP)
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT)
            sql = "INSERT INTO GPS (Nodo, Latitud, Longitud, Temperatura, StatusGPS, StatusTemp) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (dataList[0], 'Fail', 'Fail', dataList[3] , 'Fail', 'Ok')
            mycursor.execute(sql, val)
            db.commit()
        
        if (dataList[1] !='1000.000000' or dataList[2]!='1000.000000') and (dataList[3]=='0' or dataList[3]=='01' or dataList[3]=='0@'):
            print("Falla de recepción de temperatura del Nodo " + str(dataList[0]))
            self.set_mode(MODE.SLEEP)
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT)
            sql = "INSERT INTO GPS (Nodo, Latitud, Longitud, Temperatura, StatusGPS, StatusTemp) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (dataList[0], dataList[1], dataList[2], 'Fail' , 'Ok', 'Fail')
            mycursor.execute(sql, val)
            db.commit()
        
        if (dataList[1] !='1000.000000' or dataList[2]!='1000.000000') and (dataList[3]!='0' or dataList[3]!='01' or dataList[3]!='0@'):
            print("Nodo: " + str(dataList[0]) + "; Latitud: " + str(dataList[1]) + "; Longitud: " + str(dataList[2]) + "; Temperatura: " + str(dataList[3]))
            self.set_mode(MODE.SLEEP)
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT)
            sql = "INSERT INTO GPS (Nodo, Latitud, Longitud, Temperatura, StatusGPS, StatusTemp) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (dataList[0], dataList[1], dataList[2], dataList[3] , 'Ok', 'Ok')
            mycursor.execute(sql, val)
            db.commit()

lora = LoRaRcvCont(verbose=False)
lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1)

try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
