# Video to Photo GPS

Extractor de fotogramas de un video, manteniendo georeferenciación.

## Descripción

Este programa está diseñado para realizar fotogrametría a partir de vídeos grabados con drones DJI, preparándolos para su procesamiento con servicios como [WebODM](https://webodm.net). El programa extrae fotogramas de vídeos y los geolocaliza utilizando los archivos SRT que contienen datos GPS.

WebODM crea excelentes ortofotos, nubes de puntos y modelos 3D a partir de las escenas procesadas.

## Características

- ✅ Extracción de fotogramas de vídeos con control de frecuencia
- ✅ Geolocalización automática de fotogramas usando archivos SRT
- ✅ Concatenación de múltiples vídeos y sus archivos SRT
- ✅ Compatible con vídeos de drones DJI
- ✅ Soporte para procesamiento por lotes
- ✅ Interfaz de línea de comandos completa

## Requisitos Previos

Este programa se maneja completamente mediante la línea de comandos. Necesitarás instalar los siguientes programas gratuitos:

1. **FFmpeg** - Para extraer fotogramas de vídeos
   - Descarga: https://ffmpeg.org/
   
2. **Python 3** - Para ejecutar los scripts
   - Descarga: https://www.python.org/downloads/
   - Versión mínima: Python 3.6+
   
3. **ExifTool** - Para escribir metadatos GPS en las imágenes
   - Descarga: https://exiftool.org/

### Instalación en Linux/Ubuntu

```bash
sudo apt-get update
sudo apt-get install ffmpeg python3 python3-pip libimage-exiftool-perl
```

### Instalación en macOS

```bash
brew install ffmpeg python exiftool
```

### Instalación en Windows

1. Descarga e instala FFmpeg desde https://ffmpeg.org/download.html
2. Descarga e instala Python desde https://www.python.org/downloads/windows/
3. Descarga e instala ExifTool desde https://exiftool.org/

Asegúrate de agregar todos los programas al PATH del sistema.

## Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/Paisano7780/Video_to_Photo_GPS.git
cd Video_to_Photo_GPS
```

2. (Opcional) Crea un entorno virtual de Python:
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Los scripts no requieren dependencias adicionales de Python más allá de la biblioteca estándar.

## Uso

### Opción 1: Video Único

Si tienes un solo vídeo, sigue estos pasos:

#### Paso 1: Extraer fotogramas del vídeo

```bash
ffmpeg -i DJI_0123.MP4 -vf fps=1 frames/%04d.jpg
```

- `fps=1` - Extrae 1 fotograma por segundo
- `fps=0.5` - Extrae 1 fotograma cada 2 segundos
- `frames/` - Directorio donde se guardarán los fotogramas
- `%04d.jpg` - Formato de nombre (0001.jpg, 0002.jpg, etc.)

Puedes usar PNG en lugar de JPG para mejor calidad (archivos más grandes):
```bash
ffmpeg -i DJI_0123.MP4 -vf fps=1 frames/%04d.png
```

#### Paso 2: Geolocalizar los fotogramas

```bash
python srt_tag.py -s DJI_0123.SRT -d frames/ -p 30 -x jpg -f 1
```

Parámetros:
- `-s` : Archivo SRT con datos GPS
- `-d` : Directorio con los fotogramas extraídos
- `-p` : Frame rate original del vídeo (generalmente 30 o 60 fps)
- `-x` : Extensión de archivos (jpg o png)
- `-f` : Frame rate de extracción (1 = 1fps, 0.5 = 1 frame cada 2 segundos)

#### Paso 3: Subir a WebODM

Simplemente arrastra y suelta los fotogramas geolocalizados en tu proyecto WebODM. ¡Listo!

### Opción 2: Múltiples Videos (Concatenación)

Si tu grabación está dividida en varios vídeos, necesitas concatenarlos primero:

#### Paso 1: Crear lista de vídeos

Crea un archivo de texto (por ejemplo, `files.txt`) con las rutas de tus vídeos:

```
file '/ruta/completa/DJI_0251.MP4'
file '/ruta/completa/DJI_0252.MP4'
file '/ruta/completa/DJI_0253.MP4'
```

**Importante:** Usa rutas absolutas o relativas correctas.

#### Paso 2: Concatenar los vídeos

```bash
ffmpeg -f concat -safe 0 -i files.txt -c copy output.mp4
```

Esto crea `output.mp4` con todos los vídeos concatenados.

#### Paso 3: Concatenar los archivos SRT

```bash
python srt_concat.py -i files.txt -o output.srt
```

Este script lee la misma lista de vídeos y concatena automáticamente los archivos SRT correspondientes, ajustando los tiempos correctamente.

#### Paso 4: Extraer fotogramas del vídeo concatenado

```bash
ffmpeg -i output.mp4 -vf fps=1 frames/%04d.jpg
```

#### Paso 5: Geolocalizar los fotogramas

```bash
python srt_tag.py -s output.srt -d frames/ -p 30 -x jpg -f 1
```

#### Paso 6: Subir a WebODM

Sube los fotogramas a tu proyecto WebODM. ¡Terminado!

## Scripts Incluidos

### srt_tag.py

Geolocaliza fotogramas de vídeo usando datos GPS de archivos SRT.

```bash
python srt_tag.py -h
```

**Uso:**
```bash
python srt_tag.py -s <archivo.SRT> -d <directorio/> -p <fps_original> -x <extensión> -f <fps_extraído>
```

**Ejemplos:**
```bash
# Fotogramas JPG a 1 fps de vídeo 30 fps
python srt_tag.py -s video.SRT -d frames/ -p 30 -x jpg -f 1

# Fotogramas PNG a 0.5 fps (1 cada 2 segundos) de vídeo 60 fps
python srt_tag.py -s video.SRT -d frames/ -p 60 -x png -f 0.5
```

### srt_concat.py

Concatena múltiples archivos SRT ajustando los tiempos.

```bash
python srt_concat.py -h
```

**Uso:**
```bash
python srt_concat.py -i <archivo_lista.txt> -o <salida.srt>
```

**Ejemplo:**
```bash
python srt_concat.py -i concat_files.txt -o output.srt
```

## Ejemplos de Flujo Completo

### Ejemplo 1: Video único con fotogramas cada segundo

```bash
# 1. Extraer fotogramas
mkdir frames
ffmpeg -i DJI_0123.MP4 -vf fps=1 frames/%04d.jpg

# 2. Geolocalizar
python srt_tag.py -s DJI_0123.SRT -d frames/ -p 30 -x jpg -f 1

# 3. Subir a WebODM (manualmente)
```

### Ejemplo 2: Múltiples videos con fotogramas cada 2 segundos

```bash
# 1. Crear lista de archivos
cat > files.txt << EOF
file '/home/user/videos/DJI_0251.MP4'
file '/home/user/videos/DJI_0252.MP4'
file '/home/user/videos/DJI_0253.MP4'
EOF

# 2. Concatenar vídeos
ffmpeg -f concat -safe 0 -i files.txt -c copy output.mp4

# 3. Concatenar SRT
python srt_concat.py -i files.txt -o output.srt

# 4. Extraer fotogramas
mkdir frames
ffmpeg -i output.mp4 -vf fps=0.5 frames/%04d.jpg

# 5. Geolocalizar
python srt_tag.py -s output.srt -d frames/ -p 30 -x jpg -f 0.5

# 6. Subir a WebODM (manualmente)
```

## Consejos y Trucos

### Frame Rate de Extracción

- **fps=1** : 1 fotograma por segundo (bueno para la mayoría de casos)
- **fps=0.5** : 1 fotograma cada 2 segundos (menos fotogramas, procesamiento más rápido)
- **fps=2** : 2 fotogramas por segundo (más fotogramas, mejor cobertura)

### Formato de Imagen

- **JPG** : Archivos más pequeños, adecuados para la mayoría de casos
- **PNG** : Archivos más grandes, mejor calidad, útil para ortofotos de alta precisión

### Verificar Geolocalización

Para verificar que los fotogramas tienen GPS:

```bash
exiftool -GPS* frames/0001.jpg
```

### Calidad de Video

Para mejor calidad, extrae fotogramas sin recompresión:

```bash
ffmpeg -i input.mp4 -vf fps=1 -qscale:v 2 frames/%04d.jpg
```

## Solución de Problemas

### Error: "exiftool not found"

Asegúrate de que ExifTool está instalado y en el PATH del sistema.

```bash
# Verificar instalación
exiftool -ver
```

### Error: "No GPS data found in SRT file"

Verifica que:
1. El archivo SRT es el correcto para el vídeo
2. El archivo SRT contiene datos GPS (ábrelo con un editor de texto)
3. El formato del archivo SRT es compatible

### Los fotogramas no tienen GPS

Verifica los parámetros:
1. El `-p` (fps original) debe coincidir con el frame rate del vídeo
2. El `-f` (fps extraído) debe coincidir con el valor usado en ffmpeg

### Calidad de la ortofoto es baja

Prueba:
1. Usar PNG en lugar de JPG
2. Aumentar el frame rate de extracción (más fotogramas)
3. Asegurar buena iluminación en las grabaciones originales

## Estructura del Proyecto

```
Video_to_Photo_GPS/
├── srt_tag.py          # Script para geolocalizar fotogramas
├── srt_concat.py       # Script para concatenar archivos SRT
├── README.md           # Este archivo
├── requirements.txt    # Dependencias de Python (vacío, usa stdlib)
└── examples/           # Ejemplos de archivos de configuración
    └── files.txt.example
```

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un Pull Request

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Créditos

Basado en el flujo de trabajo de fotogrametría con drones DJI y WebODM.

## Soporte

Si tienes preguntas o problemas:

1. Revisa la sección de Solución de Problemas
2. Busca en los Issues existentes
3. Crea un nuevo Issue con detalles del problema

## Referencias

- [WebODM](https://webodm.net) - Plataforma de procesamiento fotogramétrico
- [FFmpeg](https://ffmpeg.org/) - Herramienta de procesamiento multimedia
- [ExifTool](https://exiftool.org/) - Herramienta de metadatos de imágenes

---

¡Esperamos que este programa te sea útil para tus proyectos de fotogrametría!
