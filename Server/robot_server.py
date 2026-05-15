#!/usr/bin/env python3

import socket
import time
import threading
import os

try:
    import ft
    txt = ft.fttxt2("auto")
    motor_izq = txt.motor(1)
    motor_der = txt.motor(2)
    VELOCIDAD = 400
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

musica_activada = False
accion_en_curso = False
rotacion_continua = False
hilo_accion = None
hilo_musica = None

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

# Figuras predefinias
def figura_cuadrado():
    print("FIGURA: Cuadrado")
    for _ in range(4):
        adelante()
        time.sleep(1.5)
        parar()
        time.sleep(0.1)
        derecha()
        time.sleep(0.5)
        parar()
        time.sleep(0.1)
    parar()

def figura_triangulo():
    print("FIGURA: Triangulo")
    for _ in range(3):
        adelante()
        time.sleep(1.5)
        parar()
        time.sleep(0.1)
        derecha()
        time.sleep(0.65)
        parar()
        time.sleep(0.1)
    parar()

def figura_circulo():
    print("FIGURA: Circulo")
    motor_izq.setSpeed(300)
    motor_der.setSpeed(500)
    time.sleep(4.0)
    parar()

def figura_equis():
    print("FIGURA: Aspa (X)")
    adelante()
    time.sleep(1.2)
    parar()
    time.sleep(0.2)
    atras()
    time.sleep(1.2)
    parar()

# Acciones de la cruz direccional
def accion_hat_up():
    """Mini-baile: movimiento en área pequeña"""
    global accion_en_curso
    accion_en_curso = True
    print("MINI-BAILE: Iniciando")
    pasos = [
        (200, -200, 0.3),
        (-200, 200, 0.3),
        (300, 300, 0.4),
        (-300, -300, 0.3),
        (200, -200, 0.25),
        (-200, 200, 0.25),
        (0, 0, 0.2),
    ]
    for izq, der, dur in pasos:
        if not accion_en_curso:
            break
        motor_izq.setSpeed(izq)
        motor_der.setSpeed(der)
        time.sleep(dur)
    parar()
    accion_en_curso = False
    print("MINI-BAILE: Fin")

def accion_hat_down():
    """Baile: rota de un lado a otro"""
    global accion_en_curso
    accion_en_curso = True
    print("BAILE: Iniciando")
    inicio = time.time()
    while accion_en_curso and time.time() - inicio < 20:
        rotar_derecha()
        time.sleep(0.8)
        rotar_izquierda()
        time.sleep(0.8)
    parar()
    print("BAILE: Finalizado")

def accion_hat_left():
    """Rotacion continua izquierda"""
    global accion_en_curso
    accion_en_curso = True
    print("ROTACION CONTINUA: Izquierda")
    while accion_en_curso:
        rotar_izquierda()
        time.sleep(0.05)
    parar()

def accion_hat_right():
    """Rotacion continua derecha"""
    global accion_en_curso
    accion_en_curso = True
    print("ROTACION CONTINUA: Derecha")
    while accion_en_curso:
        rotar_derecha()
        time.sleep(0.05)
    parar()

# Acciones de los botones
def accion_l1():
    print("L1: Zigzag")
    for _ in range(4):
        izquierda()
        time.sleep(0.3)
        derecha()
        time.sleep(0.3)
    parar()

def accion_r1():
    print("R1: Ocho")
    for _ in range(2):
        motor_izq.setSpeed(400)
        motor_der.setSpeed(200)
        time.sleep(2.8)
        motor_izq.setSpeed(200)
        motor_der.setSpeed(400)
        time.sleep(2.8)
    parar()

def accion_l2():
    global accion_en_curso
    accion_en_curso = True

    print("L2: Espiral")
    for vel in range(200, 500, 50):
        if not accion_en_curso:
            break

        motor_izq.setSpeed(vel)
        motor_der.setSpeed(vel + 80)
        time.sleep(0.6)
    parar()
    accion_en_curso = False

def accion_r2():
    global accion_en_curso
    accion_en_curso = True

    print("R2: Temblor")
    for _ in range(8):
        if not accion_en_curso:
            break
        motor_izq.setSpeed(350)
        motor_der.setSpeed(-350)
        time.sleep(0.1)
        motor_izq.setSpeed(-350)
        motor_der.setSpeed(350)
        time.sleep(0.1)
    parar()
    accion_en_curso = False

def accion_l3():
    print("L3: Saludo - Adelante y atras")
    adelante()
    time.sleep(0.8)
    parar()
    time.sleep(0.3)
    atras()
    time.sleep(0.8)
    parar()

def accion_r3():
    print("R3: Remolino")
    for vel in range(100, 500, 40):
        motor_izq.setSpeed(vel)
        motor_der.setSpeed(-vel)
        time.sleep(0.15)
    parar()

def accion_share():
    print("SHARE: Detener todo movimiento")
    global accion_en_curso, musica_activada
    if accion_en_curso:
        accion_en_curso = False
    parar()
    print("Todo detenido")

def accion_options():
    print("OPTIONS: Reiniciar sistema")
    global accion_en_curso, musica_activada
    accion_en_curso = False
    musica_activada = False
    parar()
    print("Sistema reiniciado")

def accion_ps():
    print("PS: Apagando motores (modo seguro)")
    global accion_en_curso
    accion_en_curso = False
    parar()
    print("Motores apagados")

def accion_touchpad():
    print("TOUCHPAD: Baile rapido")
    for _ in range(6):
        rotar_derecha()
        time.sleep(0.2)
        rotar_izquierda()
        time.sleep(0.2)
    parar()

# Control del joistick
def control_joystick(comando):
    """Control normal del robot con joystick"""
    global accion_en_curso

    if accion_en_curso:
        accion_en_curso = False
        time.sleep(0.1)
        
    if comando.startswith("move:"):
        valores = comando.replace("move:", "")
        izq, der = valores.split(",")
        motor_izq.setSpeed(int(izq))
        motor_der.setSpeed(int(der))
 
# Procesamiento de comandos
def ejecutar_accion(comando):
    global accion_en_curso, hilo_accion

    print("Comando recibido: {}".format(comando))

    if comando.startswith("move:"):
        if not accion_en_curso:
            control_joystick(comando)
        return

    # Detener cualquier accion en curso
    if accion_en_curso:
        accion_en_curso = False
        if hilo_accion:
            hilo_accion.join(timeout=0.5)
        parar()
        time.sleep(0.1) 

    # Botones de acción
    elif comando == "btn_0":
        figura_equis()
    elif comando == "btn_1":
        figura_circulo()
    elif comando == "btn_2":
        figura_cuadrado()
    elif comando == "btn_3":
        figura_triangulo()

    # Cruz direccional
    elif comando == "btn_11":
        accion_en_curso = True
        hilo_accion = threading.Thread(target=accion_hat_up)
        hilo_accion.daemon = True
        hilo_accion.start()
    elif comando == "btn_12":
        accion_en_curso = True
        hilo_accion = threading.Thread(target=accion_hat_down)
        hilo_accion.daemon = True
        hilo_accion.start()
    elif comando == "btn_13":
        accion_en_curso = True
        hilo_accion = threading.Thread(target=accion_hat_left)
        hilo_accion.daemon = True
        hilo_accion.start()
    elif comando == "btn_14":
        accion_en_curso = True
        hilo_accion = threading.Thread(target=accion_hat_right)
        hilo_accion.daemon = True
        hilo_accion.start()

    # Gatillos L2 y R2
    elif comando == "l2_on":
        accion_l2()
    elif comando == "r2_on":
        accion_r2()

    # Botones adicionales
    elif comando == "btn_4":
        accion_share()
    elif comando == "btn_5":
        accion_ps()
    elif comando == "btn_6":
        accion_options()
    elif comando == "btn_7":
        accion_l3()
    elif comando == "btn_8":
        accion_r3()
    elif comando == "btn_9":
        accion_l1()
    elif comando == "btn_10":
        accion_r1()
    elif comando == "btn_15":
        accion_touchpad()

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
            parar()

        except KeyboardInterrupt:
            print("\nApagando servidor...")
            global accion_en_curso
            accion_en_curso = False
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
        parar()