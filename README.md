# Video_to_Photo_GPS

Aplicación para Windows que extrae fotogramas de videos manteniendo la georeferenciación.

## Características

- ✅ Extracción de fotogramas de videos en múltiples formatos (MP4, AVI, MOV, MKV, FLV, WMV)
- ✅ Selección de intervalo de tiempo (inicio y fin en segundos)
- ✅ Selección de intervalo de fotogramas (extraer cada N fotogramas)
- ✅ Preservación de datos GPS en las imágenes extraídas
- ✅ Interfaz gráfica intuitiva en español
- ✅ Barra de progreso para seguimiento de la extracción

## Requisitos

- Python 3.7 o superior
- Windows (también funciona en Linux/Mac)

## Instalación

1. Clona o descarga este repositorio
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

### Opción 1: Usando el archivo batch (Windows)

Simplemente haz doble clic en `run_extractor.bat`

### Opción 2: Desde la línea de comandos

```bash
python video_frame_extractor.py
```

## Instrucciones de uso

1. **Seleccionar Video**: Haz clic en "Seleccionar Video" y elige tu archivo de video
   - La aplicación mostrará automáticamente información del video (FPS, duración, fotogramas totales)

2. **Configurar Intervalo de Tiempo**:
   - **Inicio**: Tiempo en segundos desde donde comenzar la extracción (por defecto: 0)
   - **Fin**: Tiempo en segundos donde terminar la extracción (por defecto: duración del video)

3. **Configurar Intervalo de Fotogramas**:
   - Especifica cada cuántos fotogramas quieres extraer una imagen
   - Ejemplo: valor 30 = extraer 1 fotograma cada 30 fotogramas
   - Con un video a 30 FPS, esto equivale a 1 imagen por segundo

4. **Cargar Datos GPS** (Opcional):
   - Haz clic en "Cargar Datos GPS (JSON)"
   - Selecciona un archivo JSON con los datos de georeferenciación
   - Ver `gps_example.json` para el formato requerido

5. **Seleccionar Carpeta de Salida**:
   - Elige dónde guardar los fotogramas extraídos

6. **Extraer Fotogramas**:
   - Haz clic en "Extraer Fotogramas"
   - La barra de progreso mostrará el avance
   - Los archivos se guardarán con el formato: `frame_XXXXXX_tYY.YYs.jpg`

## Formato del archivo GPS JSON

Los datos GPS deben estar en un archivo JSON con el siguiente formato:

```json
{
  "latitude": 40.416775,
  "longitude": -3.703790,
  "altitude": 650,
  "description": "Descripción opcional"
}
```

Donde:
- `latitude`: Latitud en grados decimales (positivo = Norte, negativo = Sur)
- `longitude`: Longitud en grados decimales (positivo = Este, negativo = Oeste)
- `altitude`: Altitud en metros (opcional)

## Ejemplo de uso

Para extraer fotogramas de un video de 10 minutos:
- Inicio: 60 (comenzar en el segundo 60)
- Fin: 300 (terminar en el segundo 300)
- Intervalo de fotogramas: 30 (extraer cada 30 fotogramas)

Si el video es de 30 FPS, esto extraerá aproximadamente 240 imágenes (240 segundos × 30 fotogramas por segundo = 7200 fotogramas; 7200 / 30 = 240 imágenes, es decir, una imagen por segundo).

## Notas

- Los fotogramas se guardan en formato JPEG con alta calidad
- Los datos GPS se insertan en los metadatos EXIF de las imágenes
- Las imágenes mantienen la resolución original del video
- El nombre de cada archivo incluye el número de fotograma y el timestamp

## Solución de problemas

**Error: "No se puede abrir el video"**
- Verifica que el archivo de video no esté corrupto
- Asegúrate de que el formato de video sea compatible

**Error al instalar dependencias**
- Asegúrate de tener instalado Visual C++ Build Tools (para opencv-python en Windows)
- Intenta: `pip install --upgrade pip` antes de instalar requirements.txt

**La aplicación no se abre**
- Verifica que Python esté correctamente instalado
- Ejecuta desde la línea de comandos para ver mensajes de error

## Licencia

Este proyecto es de código abierto.
