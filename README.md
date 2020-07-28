# Multiagentes (Simulación con v-rep y open-cv)

Basado en [Tutorial de Vrep y OpenCV-Python](https://robologs.net/2016/07/07/tutorial-de-vrep-y-opencv-python/)

## Entorno 

```bash
virtualenv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Configurar puertos 19997 y 19998 en el archivo `C:\Program Files\V-REP3\V-REP_PRO_EDU\remoteApiConnections.txt`

```bash
portIndex1_port             = 19997
portIndex1_debug            = false
portIndex1_syncSimTrigger   = true

portIndex2_port             = 19998
portIndex2_debug            = false
portIndex2_syncSimTrigger   = true

# Si se necesitan más puertos, bajo la siguiente convención:
portIndex@_port = xxxx            (puerto libre)
portIndex@_debug = xxxx           (true o false)     
portIndex@_syncSimTrigger = xxxx  (true o false)   
```

## Ejecución
Abrir  `simulation_files/robotin_v3.ttt` con v-rep, ejecutar la simulación, posteriormente los scripts:

```bash
python example/main_19997.py
python example/main_19998.py
```


## Consideraciones
Verificar la versión de Python instalada, remoteApi.dll debe ir de acuerdo a la versión. (32 o 64 bits respectivamente).