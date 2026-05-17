#!/usr/bin/env python3

import socket
import time
import threading #hilos de trabajo

try:
    import ft
    txt = ft.fttxt2("auto")
    motor_izq = txt.motor(1)
    motor_der = txt.motor(2)
    VELOCIDAD = 400 # potencia del motor entre (0-510)
    API_OK = True
    print("Motores configurados")
except Exception as e:
    print("Error en motores: {}".format(e))
    print("Modo simulacion")
    API_OK = False
    class MotorDummy:
        def setSpeed(self, v): pass
    motor_izq = MotorDummy()
    motor_der = MotorDummy()
    VELOCIDAD = 400

accion_en_curso = False
rotacion_continua = False
hilo_accion = None
_stop_event = threading.Event()

# Funciones basicas
def adelante():
    motor_izq.setSpeed(VELOCIDAD)
    motor_der.setSpeed(VELOCIDAD)

def atras():
    motor_izq.setSpeed(-VELOCIDAD)
    motor_der.setSpeed(-VELOCIDAD)

def izquierda():
    motor_izq.setSpeed(-VELOCIDAD)
    motor_der.setSpeed(VELOCIDAD)

def derecha():
    motor_izq.setSpeed(VELOCIDAD)
    motor_der.setSpeed(-VELOCIDAD)

def parar():
    motor_izq.setSpeed(0)
    motor_der.setSpeed(0)

def rotar_izquierda():
    motor_izq.setSpeed(-VELOCIDAD)
    motor_der.setSpeed(VELOCIDAD)

def rotar_derecha():
    motor_izq.setSpeed(VELOCIDAD)
    motor_der.setSpeed(-VELOCIDAD)

# Permitir que cualquier hilo de accion responda a la señal de stop
def _sleep_interruptible(segundos, paso=0.05):
    """Duerme 'segundos' pero sale antes si _stop_event esta activo."""
    fin = time.time() + segundos
    while time.time() < fin:
        if _stop_event.is_set():
            return
        time.sleep(paso)

# Figuras predefinias
def figura_cuadrado():
    print("FIGURA: Cuadrado")
    for _ in range(4):
        adelante()
        _sleep_interruptible(1.5)
        if _stop_event.is_set(): break
        parar()
        _sleep_interruptible(0.1)
        derecha()
        _sleep_interruptible(0.5)
        if _stop_event.is_set(): break
        parar()
        _sleep_interruptible(0.1)
    parar()

def figura_triangulo():
    print("FIGURA: Triangulo")
    for _ in range(3):
        adelante()
        _sleep_interruptible(1.5)
        if _stop_event.is_set(): break
        parar()
        _sleep_interruptible(0.1)
        derecha()
        _sleep_interruptible(0.65)
        if _stop_event.is_set(): break
        parar()
        _sleep_interruptible(0.1)
    parar()

def figura_circulo():
    print("FIGURA: Circulo")
    motor_izq.setSpeed(300)
    motor_der.setSpeed(500)
    _sleep_interruptible(4.0)
    parar()

def figura_equis():
    print("FIGURA: Aspa (X)")
    adelante()
    _sleep_interruptible(1.2)
    parar()
    _sleep_interruptible(0.2)
    if not _stop_event.is_set():
        atras()
        _sleep_interruptible(1.2)
    parar()

# Acciones de la cruz direccional
def accion_hat_up():
    """Mini-baile: secuencia de movimientos cortos en area reducida."""
    global accion_en_curso
    print("MINI-BAILE: Iniciando")

    # Cada tupla: (vel_izq, vel_der, duracion_seg)
    pasos = [
        ( 250, -250, 0.30),
        (-250,  250, 0.30),
        ( 300,  300, 0.35),
        (-300, -300, 0.30),
        ( 250, -250, 0.25),
        (-250,  250, 0.25),
        ( 300,  300, 0.20),
        (   0,    0, 0.15),
        ( 350, -350, 0.20),
        (-350,  350, 0.20),
    ]

    for izq, der, dur in pasos:
        if _stop_event.is_set():
            break
        motor_izq.setSpeed(izq)
        motor_der.setSpeed(der)
        _sleep_interruptible(dur)

    parar()
    accion_en_curso = False
    print("MINI-BAILE: Fin")

def accion_hat_down():
    """Baile: rota de un lado a otro"""
    global accion_en_curso
    print("BAILE: Iniciando")
    inicio = time.time()
    while not _stop_event.is_set() and time.time() - inicio < 20:
        rotar_derecha()
        _sleep_interruptible(0.8)
        if _stop_event.is_set(): break
        rotar_izquierda()
        _sleep_interruptible(0.8)
    parar()
    accion_en_curso = False
    print("BAILE: Finalizado")

def accion_hat_left():
    """Rotacion continua izquierda"""
    global accion_en_curso
    print("ROTACION CONTINUA: Izquierda")
    while not _stop_event.is_set():
        rotar_izquierda()
        _sleep_interruptible(0.05)
    parar()
    accion_en_curso = False

def accion_hat_right():
    """Rotacion continua derecha"""
    global accion_en_curso
    print("ROTACION CONTINUA: Derecha")
    while not _stop_event.is_set():
        rotar_derecha()
        _sleep_interruptible(0.05)
    parar()
    accion_en_curso = False

# Acciones de los botones
def accion_l1():
    print("L1: Zigzag")
    for _ in range(4):
        if _stop_event.is_set(): break
        izquierda()
        _sleep_interruptible(0.3)
        derecha()
        _sleep_interruptible(0.3)
    parar()

def accion_r1():
    print("R1: Ocho")
    for _ in range(2):
        if _stop_event.is_set(): break
        motor_izq.setSpeed(400)
        motor_der.setSpeed(200)
        _sleep_interruptible(2.8)
        if _stop_event.is_set(): break
        motor_izq.setSpeed(200)
        motor_der.setSpeed(400)
        _sleep_interruptible(2.8)
    parar()

def accion_l2():
    global accion_en_curso
    print("L2: Espiral")
    for vel in range(200, 500, 50):
        if _stop_event.is_set():
            break
        motor_izq.setSpeed(vel)
        motor_der.setSpeed(vel + 80)
        _sleep_interruptible(0.6)
    parar()
    accion_en_curso = False

def accion_r2():
    global accion_en_curso
    print("R2: Temblor")
    for _ in range(8):
        if _stop_event.is_set():
            break
        motor_izq.setSpeed(350)
        motor_der.setSpeed(-350)
        _sleep_interruptible(0.1)
        if _stop_event.is_set(): break
        motor_izq.setSpeed(-350)
        motor_der.setSpeed(350)
        _sleep_interruptible(0.1)
    parar()
    accion_en_curso = False

def accion_l3():
    print("L3: Saludo - Adelante y atras")
    adelante()
    _sleep_interruptible(0.8)
    parar()
    _sleep_interruptible(0.3)
    if not _stop_event.is_set():
        atras()
        _sleep_interruptible(0.8)
    parar()

def accion_r3():
    print("R3: Remolino")
    for vel in range(100, 500, 40):
        if _stop_event.is_set(): break
        motor_izq.setSpeed(vel)
        motor_der.setSpeed(-vel)
        _sleep_interruptible(0.15)
    parar()

def accion_share():
    print("SHARE: Detener todo movimiento")
    global accion_en_curso
    _detener_accion_en_curso()
    parar()
    print("Todo detenido")

def accion_options():
    print("OPTIONS: Reiniciar sistema")
    global accion_en_curso
    _detener_accion_en_curso()
    parar()
    print("Sistema reiniciado")

def accion_ps():
    print("PS: Apagando motores (modo seguro)")
    _detener_accion_en_curso()
    parar()
    print("Motores apagados")

def accion_touchpad():
    print("TOUCHPAD: Baile rapido")
    for _ in range(6):
        if _stop_event.is_set(): break
        rotar_derecha()
        _sleep_interruptible(0.2)
        rotar_izquierda()
        _sleep_interruptible(0.2)
    parar()

# Control del joistick
def control_joystick(comando):
    """Control normal del robot con joystick"""
    if comando.startswith("move:"):
        valores = comando.replace("move:", "")
        izq, der = valores.split(",")
        motor_izq.setSpeed(int(izq))
        motor_der.setSpeed(int(der))
 
# detener accion n curso
def _detener_accion_en_curso():
    global accion_en_curso, hilo_accion
    accion_en_curso = False
    _stop_event.set()
    if hilo_accion and hilo_accion.is_alive():
        hilo_accion.join(timeout=0.3)
    _stop_event.clear()
    hilo_accion = None

def _lanzar_en_hilo(func):
    global accion_en_curso, hilo_accion
    _stop_event.clear()
    accion_en_curso = True
    hilo_accion = threading.Thread(target=func)
    hilo_accion.daemon = True
    hilo_accion.start()

# Procesamiento de comandos
def ejecutar_accion(comando):
    global accion_en_curso, hilo_accion

    print("Comando recibido: {}".format(comando))

    if comando.startswith("move:"):
        valores = comando.replace("move:", "")
        izq, der = valores.split(",")
        if int(izq) != 0 or int(der) != 0:
            if accion_en_curso:
                _detener_accion_en_curso()
                parar()
        elif accion_en_curso:
            return
        control_joystick(comando)
        return

    # Detener cualquier accion en curso
    if accion_en_curso:
        _detener_accion_en_curso()
        parar()
        time.sleep(0.05)

    _stop_event.clear()

    # Botones de acción
    if comando == "btn_0":
        figura_equis()
    elif comando == "btn_1":
        figura_circulo()
    elif comando == "btn_2":
        figura_cuadrado()
    elif comando == "btn_3":
        figura_triangulo()

    # Cruz direccional
    elif comando == "btn_11":
        _lanzar_en_hilo(accion_hat_up)
    elif comando == "btn_12":
        _lanzar_en_hilo(accion_hat_down)
    elif comando == "btn_13":
        _lanzar_en_hilo(accion_hat_left)
    elif comando == "btn_14":
        _lanzar_en_hilo(accion_hat_right)

    # Gatillos L2 y R2
    elif comando == "l2_on":
        _lanzar_en_hilo(accion_l2)
    elif comando == "r2_on":
        _lanzar_en_hilo(accion_r2)

    # Todos los demas botones
    elif comando == "btn_4":
        accion_share()
    elif comando == "btn_5":
        accion_ps()
    elif comando == "btn_6":
        accion_options()
    elif comando == "btn_7":
        _lanzar_en_hilo(accion_l3)
    elif comando == "btn_8":
        _lanzar_en_hilo(accion_r3)
    elif comando == "btn_9":
        _lanzar_en_hilo(accion_l1)
    elif comando == "btn_10":
        _lanzar_en_hilo(accion_r1)
    elif comando == "btn_15":
        _lanzar_en_hilo(accion_touchpad)

# Ejecutar el txt
def iniciar_servidor():
    PUERTO = 5005
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("", PUERTO))
    servidor.listen(1)

    print("=" * 50)
    print("   ROBOT SERVER - ESPERANDO COMANDOS")
    print("=" * 50)
    print("Puerto: {}".format(PUERTO))
    print("Esperando conexion del controlador...")
    print("")

    while True:
        try:
            cliente, addr = servidor.accept()
            print("Controlador conectado desde: {}".format(addr[0]))
            print("Listo para recibir comandos\n")
            buffer = ""
            
            while True:
                datos = cliente.recv(1024)

                if not datos:
                    break

                buffer += datos.decode()

                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    ejecutar_accion(linea.strip())

            cliente.close()
            print("Controlador desconectado")
            _detener_accion_en_curso()
            parar()

        except KeyboardInterrupt:
            print("\nApagando servidor...")
            _detener_accion_en_curso()
            parar()
            break
        except Exception as e:
            print("Error: {}".format(e))
            continue

if __name__ == "__main__":
    try:
        iniciar_servidor()
    except KeyboardInterrupt:
        print("\nServidor detenido")
        _detener_accion_en_curso()
        parar()