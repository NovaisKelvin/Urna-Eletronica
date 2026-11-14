import serial, time

def tentar(rotulo, timeout):
    try:
        s = serial.Serial("COM7", 9600, timeout=timeout)
        print(rotulo, "-> ABRIU")
        s.close()
    except Exception as e:
        print(rotulo, "-> ERRO:", e)

tentar("1a abertura, timeout=1  ", 1)
time.sleep(1)
tentar("2a abertura, timeout=1  ", 1)
time.sleep(1)
tentar("3a abertura, timeout=0.1", 0.1)
time.sleep(1)
tentar("4a abertura, timeout=0.1", 0.1)