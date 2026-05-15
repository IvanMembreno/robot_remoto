#!/usr/bin/env python3

import sys
import socket
import pygame
import paramiko

from PyQt6.QtWidgets import *
from PyQt6.QtCore import (
    QThread,
    pyqtSignal,
    QRegularExpression, 
    QTimer 
    )
from PyQt6.QtGui import (
    QColor,
    QTextCharFormat,
    QSyntaxHighlighter,
    QTextCursor,
    QFont,
    )

ROBOT_PORT = 5005
UMBRAL = 0.20

BOTONES = {
    0: "Cruz",
    1: "Circulo",
    2: "Cuadrado",
    3: "Triangulo",
    4: "Share",
    5: "PS Button",
    6: "Options",
    7: "L3",
    8: "R3",
    9: "L1",
    10: "R1",
    11: "Hat_up",
    12: "Hat_down",
    13: "Hat_left",
    14: "Hat_right",
    15: "Touchpad"
}

class JoystickThread(QThread):

    log_signal = pyqtSignal(str)
    button_signal = pyqtSignal(int, bool)
    axis_signal = pyqtSignal(int, float)

    def __init__(self):
        super().__init__()
        self.running = True
        self.joystick = None
        self.ultimo_move = ""
        self.l2_activo = False
        self.r2_activo = False
        self.robot_ip = ""
        self.sock = None

    def conectar_robot(self, ip):

        self.robot_ip = ip

        try:
            if self.sock:
                self.sock.close()

            self.sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.sock.connect((ip, ROBOT_PORT))

            self.log_signal.emit(
                f"Conectado al robot: {ip}"
            )

        except Exception as e:
            self.log_signal.emit(
                f"Error robot: {e}"
            )
    
    def enviar_robot(self, comando):

        if not self.sock:
            return

        try:
            self.sock.send(
                (comando + "\n").encode()
            )

        except Exception as e:
            self.log_signal.emit(
                f"Conexion perdida: {e}"
            )

            self.sock = None

    def reconnect(self):
        try:
            if self.joystick:
                try:
                    self.joystick.quit()
                except:
                    pass

                self.joystick = None
                
            pygame.joystick.quit()
            pygame.joystick.init()

            cantidad = pygame.joystick.get_count()

            if cantidad > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()

                self.log_signal.emit(f"Mando conectado: {self.joystick.get_name()}")
            else:
                self.log_signal.emit("No se detecto mando")

        except Exception as e:

            self.log_signal.emit(
                f"Error reconectando mando: {e}"
            )

    def run(self):

        pygame.init()
        pygame.joystick.init()

        self.reconnect()

        while self.running:
            try:
                if self.joystick and self.joystick.get_init():
                    pygame.event.pump()

                    for event in pygame.event.get():
                        if event.type == pygame.JOYBUTTONDOWN:
                            self.button_signal.emit(event.button, True)
                            cmd = f"btn_{event.button}"
                            if cmd != self.ultimo_move:
                                self.enviar_robot(cmd)
                                self.ultimo_move = cmd

                            self.log_signal.emit(
                                f"btn_{event.button}\t|   {BOTONES.get(event.button)}"
                            )

                        elif event.type == pygame.JOYBUTTONUP:
                            self.button_signal.emit(event.button, False)

                    # AXIS
                    for i in range(self.joystick.get_numaxes()):
                        valor = self.joystick.get_axis(i)

                        if abs(valor) < UMBRAL:
                            valor = 0

                        self.axis_signal.emit(i, valor)

                    x = self.joystick.get_axis(0)
                    y = self.joystick.get_axis(1)

                    if abs(x) < UMBRAL:
                        x = 0

                    if abs(y) < UMBRAL:
                        y = 0

                    vel_izq = int((-y + x) * 400)
                    vel_der = int((-y - x) * 400)

                    vel_izq = max(-400, min(400, vel_izq))
                    vel_der = max(-400, min(400, vel_der))

                    cmd = f"move:{vel_izq},{vel_der}"

                    if cmd != self.ultimo_move:
                        self.enviar_robot(cmd)
                        self.ultimo_move = cmd

                    # Gatillos
                    l2 = self.joystick.get_axis(4)
                    r2 = self.joystick.get_axis(5)

                    nuevo_l2 = l2 > 0.5
                    nuevo_r2 = r2 > 0.5

                    if nuevo_l2 and not self.l2_activo:
                        self.enviar_robot("l2_on")

                    if nuevo_r2 and not self.r2_activo:
                        self.enviar_robot("r2_on")

                    self.l2_activo = nuevo_l2
                    self.r2_activo = nuevo_r2

            except Exception as e:

                self.log_signal.emit(
                    f"Joystick error: {e}"
                )

                self.joystick = None

            self.msleep(30)

class SSHWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.client = None
        self.shell = None
        self.timer = QTimer()
        self.timer.timeout.connect(
            self.read_shell
        )
        layout = QVBoxLayout()

        # IP
        top = QHBoxLayout()

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP Robot")

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.connect_btn = QPushButton("Conectar SSH")

        self.setStyleSheet("""
            QLineEdit {
                color: white;
            }
                           
            QLineEdit:focus {
                border: 1px solid white;
            }
                           
            QPushButton {
                background:#0078d4;
                color:white;
                width: 90px;
            }
                                    
            QPushButton:hover {
                background:#0067b8;
                color:white;
            }
                                    
            QPushButton:pressed {
                background:#0067b8;
                font-size:11px;
                border-bottom: 2px solid #008800;
                border-right: 2px solid #008800;
                margin-bottom: 2px;
                margin-right: 2px;
                margin-left: 2px;
            }
        """)

        top.addWidget(self.ip_input)
        top.addWidget(self.user_input)
        top.addWidget(self.pass_input)
        top.addWidget(self.connect_btn)

        layout.addLayout(top)

        # TERMINAL
        self.terminal = QTextEdit()
        self.terminal.setStyleSheet("""
            QTextEdit{
                background:#111;
                color:#00ff88;
                border:1px solid #333;
                font-family:Consolas;
            }
        """)
        self.terminal.setReadOnly(True)

        layout.addWidget(self.terminal)

        # COMANDOS
        cmd_layout = QHBoxLayout()

        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Comando Linux")

        self.send_btn = QPushButton("Ejecutar")

        self.send_btn.setStyleSheet("""
            QPushButton {
                background:#00aa00;
                color:white;
                width: 60px;
            }
                                    
            QPushButton:hover {
                background:#00cc00;
                color:white;
            }
                                    
            QPushButton:pressed {
                background:#00cc00;
                font-size:11px;
                border-bottom: 2px solid #008800;
                border-right: 2px solid #008800;
                margin-bottom: 2px;
                margin-right: 2px;
                margin-left: 2px;
            }
        """)

        cmd_layout.addWidget(self.cmd_input)
        cmd_layout.addWidget(self.send_btn)

        layout.addLayout(cmd_layout)

        self.setLayout(layout)

        self.connect_btn.clicked.connect(self.connect_ssh)
        self.send_btn.clicked.connect(self.execute_command)

    def log(self, txt):
        self.terminal.append(txt)

    def connect_ssh(self):

        ip = self.ip_input.text()
        user = self.user_input.text()
        password = self.pass_input.text()

        try:

            self.client = paramiko.SSHClient()

            self.client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy()
            )

            self.client.connect(
                hostname=ip,
                username=user,
                password=password
            )

            self.log("Conexion SSH exitosa")

            # TERMINAL INTERACTIVA
            self.shell = self.client.invoke_shell()
            self.shell.settimeout(0.0)
            self.timer.start(50)
            self.log("Shell interactiva iniciada")

            self.sftp = self.client.open_sftp()
            self.log("SFTP conectado")

        except Exception as e:
            self.log(str(e))

    def read_shell(self):

        if not self.shell:
            return

        try:
            if self.shell.recv_ready():
                data = self.shell.recv(4096)
                texto = data.decode(
                    errors="ignore"
                )

                self.terminal.moveCursor(
                    QTextCursor.MoveOperation.End
                )

                self.terminal.insertPlainText(texto)

                self.terminal.moveCursor(
                    QTextCursor.MoveOperation.End
                )

        except:
            pass

    def execute_command(self):
        if not self.shell:
            self.log("No conectado")
            return

        cmd = self.cmd_input.text()

        if not cmd:
            return

        try:
            self.shell.send(cmd + "\n")
            self.cmd_input.clear()

        except Exception as e:
            self.log(str(e))

# Seccion del mando
class MandoWidget(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # TOP CONFIG
        top = QHBoxLayout()

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP Robot")

        self.reconnect_btn = QPushButton("Reconectar Mando")
        self.setStyleSheet("""
            QLineEdit {
                color: white;
            }
                           
            QLineEdit:focus {
                border: 1px solid white;
            }
                           
            QPushButton {
                background:#0078d4;
                color:white;
                width: 120px;
                border:1px solid #333;
                font-family:Consolas;
            }
                           
            QPushButton:hover {
                background:#0067b8;
                color:white;
            }
                           
            QPushButton:pressed {
                background:#0067b8;
                font-size:11px;
                border-bottom: 2px solid #008800;
                border-right: 2px solid #008800;
                margin-bottom: 2px;
                margin-right: 2px;
                margin-left: 2px;
            }
        """)

        top.addWidget(self.ip_input)
        top.addWidget(self.reconnect_btn)

        layout.addLayout(top)

        # BOTONES
        grid = QGridLayout()

        self.button_widgets = {}

        fila = 0
        col = 0

        for num, nombre in BOTONES.items():
            btn = QPushButton(nombre)
            btn.setEnabled(False)
            btn.setMinimumHeight(50)
            btn.setStyleSheet("""
                QPushButton{
                    background:#2d2d2d;
                    color:white;
                    font-size: 16px;
                    font-family:Consolas;
                    border:2px solid #444;
                    border-radius:10px;
                }
            """)

            self.button_widgets[num] = btn
            grid.addWidget(btn, fila, col)

            col += 1

            if col >= 4:
                col = 0
                fila += 1

        layout.addLayout(grid)

        # JOYSTICKS
        joy_layout = QHBoxLayout()

        self.left_label_x = QLabel()
        self.left_label_y = QLabel()
        self.left_label_master = QLabel()
        self.right_label_x = QLabel()
        self.right_label_y = QLabel()
        self.right_label_master = QLabel()
        self.trigger_label_x = QLabel()
        self.trigger_label_y = QLabel()
        self.trigger_label_master = QLabel()

        joy_layout.addWidget(self.left_label_master)
        joy_layout.addWidget(self.right_label_master)
        joy_layout.addWidget(self.trigger_label_master)

        layout.addLayout(joy_layout)

        # TERMINAL
        self.terminal = QTextEdit()
        self.terminal.setStyleSheet("""
            QTextEdit{
                background:#111;
                color:#00ff88;
                border:1px solid #333;
                font-family:Consolas;
            }
        """)
        self.terminal.setReadOnly(True)

        layout.addWidget(self.terminal)

        self.setLayout(layout)

    def log(self, txt):
        self.terminal.append(txt)

    def set_button_state(self, button, pressed):
        if button not in self.button_widgets:
            return

        btn = self.button_widgets[button]

        if pressed:
            btn.setStyleSheet("""
                QPushButton{
                    background: #00aa00;
                    color: #000000;
                    font-size: 14px;
                    border-right: 4px solid #004d00;
                    border-bottom: 4px solid #004d00;
                    border-radius: 10px;
                    margin-bottom: 4px; 
                    margin-right: 8px; 
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton{
                    background:#2d2d2d;
                    color:white;
                    font-size: 16px;
                    border:2px solid #444;
                    border-radius:10px;
                }
            """)

    def update_axis(self, axis, value):
        if axis in [0, 1]:
            if axis == 0:
                self.left_label_x.setText(
                    f"{value:.2f}"
                    #f"Axis {axis}: {value:.2f}"
                    )
            
            elif axis == 1:
                self.left_label_y.setText(
                    f"{value:.2f}"
                    #f"Axis {axis}: {value:.2f}"
                    )
                
            self.left_label_master.setText(
                f"Joystick Izqierdo\n{"-"*17}\nX: {self.left_label_x.text()}\nY: {self.left_label_y.text()}"
                )

        elif axis in [2, 3]:
            if axis == 2:
                self.right_label_x.setText(
                    f"{value:.2f}"
                    #f"Axis {axis}: {value:.2f}"
                    )
            
            elif axis == 3:
                self.right_label_y.setText(
                    f"{value:.2f}"
                    #f"Axis {axis}: {value:.2f}"
                    )
                
            self.right_label_master.setText(
                f"Joystick Derecho\n{"-"*17}\nX: {self.right_label_x.text()}\nY: {self.right_label_y.text()}"
                )

        elif axis in [4, 5]:
            if axis == 4:
                self.trigger_label_x.setText(
                    f"{value:.2f}"
                    #f"Axis {axis}: {value:.2f}"
                    )
            
            elif axis == 5:
                self.trigger_label_y.setText(
                    f"{value:.2f}"
                    #f"Axis {axis}: {value:.2f}"
                    )
                
            self.trigger_label_master.setText(
                f"Gatillos\n{"-"*17}\nL2: {self.trigger_label_x.text()}\nR2: {self.trigger_label_y.text()}"
                )

class PythonHighlighter(QSyntaxHighlighter):

    def __init__(self, document):
        super().__init__(document)

        self.rules = []

        # KEYWORDS
        keywords = [
            "def", "class", "import", "from",
            "return", "if", "elif", "else",
            "while", "for", "in", "try",
            "except", "finally", "with",
            "as", "pass", "break", "continue",
            "True", "False", "None"
        ]

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(
            QColor("#569CD6")
        )

        keyword_format.setFontWeight(
            QFont.Weight.Bold
        )

        for word in keywords:
            pattern = QRegularExpression(
                f"\\b{word}\\b"
            )

            self.rules.append(
                (pattern, keyword_format)
            )

        # STRINGS
        string_format = QTextCharFormat()
        string_format.setForeground(
            QColor("#CE9178")
        )

        self.rules.append((
            QRegularExpression("\".*\""),
            string_format
        ))

        self.rules.append((
            QRegularExpression("\'.*\'"),
            string_format
        ))

        # COMMENTS
        comment_format = QTextCharFormat()
        comment_format.setForeground(
            QColor("#6A9955")
        )

        self.rules.append((
            QRegularExpression("#[^\n]*"),
            comment_format
        ))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:

            iterator = pattern.globalMatch(text)

            while iterator.hasNext():

                match = iterator.next()

                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    fmt
                )

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Control Robot")
        self.resize(1200, 700)
        self.setStyleSheet("""
            QWidget{
                background:#202020;
                color:white;
            }

            QPushButton{
                background:#2d2d2d;
                border:1px solid #444;
                padding:8px;
                border-radius:8px;
            }

            QPushButton:hover{
                background:#3a3a3a;
            }

            QLineEdit{
                background:#2b2b2b;
                border:1px solid #444;
                padding:6px;
                border-radius:6px;
                color:white;
            }

            QTabWidget::pane{
                border:1px solid #333;
            }

            QTabBar::tab {
                background: transparent; /* No compite con el fondo */
                color: #888; /* Texto apagado para dar jerarquía */
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }

            QTabBar::tab:hover {
                background: #282828;
                color: white;
            }

            QTabBar::tab:selected {
                background: #252525;
                color: #00e5ff; /* El texto toma el color de acento */
                font-weight: bold;
                border-bottom: 2px solid #00e5ff; /* Línea de acento más elegante */
            }
        """)

        self.tabs = QTabWidget()

        self.mando_page = MandoWidget()
        self.robot_page = SSHWidget()

        self.tabs.addTab(self.mando_page, "Mando")
        self.tabs.addTab(self.robot_page, "Robot")

        self.setCentralWidget(self.tabs)

        # JOYSTICK THREAD
        self.joystick_thread = JoystickThread()

        self.joystick_thread.log_signal.connect(
            self.mando_page.log
        )

        self.joystick_thread.button_signal.connect(
            self.mando_page.set_button_state
        )

        self.joystick_thread.axis_signal.connect(
            self.mando_page.update_axis
        )

        self.mando_page.reconnect_btn.clicked.connect(
            self.reconnect_all
        )

        self.joystick_thread.start()

    def reconnect_all(self):
        ip = self.mando_page.ip_input.text()

        self.joystick_thread.reconnect()

        if ip:
            self.joystick_thread.conectar_robot(ip)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())