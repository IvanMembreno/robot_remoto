# Objetivo
Controlar un robot de la marca fischertechnik mediante coneccion SSH para permitir la entrada de comandos de un mando de ps4

## Preparar el ambiente
Para ejecutar el proyecto usaremos vscode y sigue estos pasos:

1. Clonar el repositorio

```bash
git clone https://github.com/IvanMembreno/robot_remoto.git
```

2. Ingresar a la carpeta o abrirlo desde VSCode

```bash
cd robot_remoto
```

3. crear el environment

```bash
python -m venv .venv
```

4. Activar el environment

```bash
./.venv/Scripts/Activate
```

5. Instalar todas las librerias

```bash
pip install -r requirements.txt
```

6. Cambiar el kernel si no lee bien el control_ps4.py
```bash
6.1. Presionar `Ctrl + shift + p`
6.2. Seleccionar el interprete de python que tenga la ruta al .venv
```

7. Ejecutar el proyecto
