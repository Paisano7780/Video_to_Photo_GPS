#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script para validar funcionalidades del extractor
"""

import os
import sys
import tempfile
import cv2
import numpy as np
from PIL import Image
import piexif
import json
import logging
import traceback
from datetime import datetime


def setup_logging(log_file='test_results.log'):
    """Configura el sistema de logging para los tests"""
    # Crear logger
    logger = logging.getLogger('test_extractor')
    logger.setLevel(logging.DEBUG)
    
    # Limpiar handlers existentes
    logger.handlers = []
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


logger = None  # Global logger instance


def create_test_video(filepath, duration=5, fps=30):
    """Crea un video de prueba"""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width, height = 640, 480
    out = cv2.VideoWriter(filepath, fourcc, fps, (width, height))

    total_frames = int(duration * fps)
    for i in range(total_frames):
        # Crear un frame con un número visible
        frame = np.ones((height, width, 3), dtype=np.uint8) * 255
        text = f"Frame {i}"
        cv2.putText(frame, text, (50, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        out.write(frame)

    out.release()
    print(f"Video de prueba creado: {filepath}")
    return filepath


def test_video_reading(video_path):
    """Prueba la lectura de video"""
    print("\n=== Test: Lectura de Video ===")
    logger.info("=== Test: Lectura de Video ===")
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            error_msg = f"No se pudo abrir el video: {video_path}"
            logger.error(error_msg)
            print(f"✗ {error_msg}")
            return False
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()

        print(f"✓ FPS: {fps}")
        print(f"✓ Total frames: {total_frames}")
        print(f"✓ Duración: {duration:.2f}s")
        
        logger.info(f"FPS: {fps}")
        logger.info(f"Total frames: {total_frames}")
        logger.info(f"Duración: {duration:.2f}s")
        logger.info("Test de lectura de video: PASS")
        
        return True
    except Exception as e:
        error_msg = f"Error durante test de lectura de video: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"✗ {error_msg}")
        return False


def test_frame_extraction(video_path, output_dir):
    """Prueba la extracción de frames"""
    print("\n=== Test: Extracción de Frames ===")
    logger.info("=== Test: Extracción de Frames ===")
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            error_msg = f"No se pudo abrir el video: {video_path}"
            logger.error(error_msg)
            print(f"✗ {error_msg}")
            return False

        start_frame = 0
        frame_interval = 30
        extracted = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

            if (current_frame - start_frame) % frame_interval == 0:
                output_path = os.path.join(
                    output_dir, f"test_frame_{current_frame:06d}.jpg")
                success = cv2.imwrite(output_path, frame)
                if not success:
                    logger.warning(
                        f"No se pudo escribir frame {current_frame} en {output_path}")
                else:
                    extracted += 1
                    logger.debug(f"Frame {current_frame} extraído exitosamente")

        cap.release()
        print(f"✓ Frames extraídos: {extracted}")
        logger.info(f"Frames extraídos: {extracted}")
        logger.info("Test de extracción de frames: PASS")
        return extracted > 0
    except Exception as e:
        error_msg = f"Error durante test de extracción de frames: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"✗ {error_msg}")
        return False


def test_gps_metadata(output_dir):
    """Prueba la adición de metadatos GPS"""
    print("\n=== Test: Metadatos GPS ===")
    logger.info("=== Test: Metadatos GPS ===")
    try:
        # Crear una imagen de prueba
        test_image_path = os.path.join(output_dir, "test_gps.jpg")
        img = Image.new('RGB', (100, 100), color='white')
        img.save(test_image_path)
        logger.debug(f"Imagen de prueba creada en: {test_image_path}")

        # Función para convertir coordenadas
        def convert_to_degrees(value):
            d = int(value)
            m = int((value - d) * 60)
            s = (value - d - m / 60) * 3600
            return ((d, 1), (m, 1), (int(s * 100), 100))

        # Agregar GPS
        lat, lon, alt = 40.416775, -3.703790, 650

        exif_dict = {
            "0th": {},
            "Exif": {},
            "GPS": {},
            "1st": {},
            "thumbnail": None}

        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
            piexif.GPSIFD.GPSLatitude: convert_to_degrees(abs(lat)),
            piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
            piexif.GPSIFD.GPSLongitude: convert_to_degrees(abs(lon)),
            piexif.GPSIFD.GPSAltitudeRef: 0 if alt >= 0 else 1,
            piexif.GPSIFD.GPSAltitude: (int(abs(alt) * 100), 100)
        }

        exif_dict["GPS"] = gps_ifd
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, test_image_path)
        logger.debug("Metadatos GPS insertados en la imagen")

        # Verificar que se guardó
        exif_data = piexif.load(test_image_path)
        has_gps = "GPS" in exif_data and len(exif_data["GPS"]) > 0

        print(f"✓ GPS metadata agregado: {has_gps}")
        print(f"✓ Latitud: {lat}, Longitud: {lon}, Altitud: {alt}m")
        
        logger.info(f"GPS metadata agregado: {has_gps}")
        logger.info(f"Latitud: {lat}, Longitud: {lon}, Altitud: {alt}m")
        logger.info("Test de metadatos GPS: PASS")
        
        return has_gps
    except Exception as e:
        error_msg = f"Error durante test de metadatos GPS: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"✗ {error_msg}")
        return False


def test_json_gps_loading():
    """Prueba la carga de datos GPS desde JSON"""
    print("\n=== Test: Carga de GPS desde JSON ===")
    logger.info("=== Test: Carga de GPS desde JSON ===")
    
    try:
        # Crear un archivo JSON de prueba
        gps_data = {
            "latitude": 40.416775,
            "longitude": -3.703790,
            "altitude": 650,
            "description": "Test location"
        }

        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.json', delete=False) as f:
            json.dump(gps_data, f)
            json_path = f.name
        
        logger.debug(f"Archivo JSON temporal creado: {json_path}")

        # Cargar y verificar
        with open(json_path, 'r') as f:
            loaded_data = json.load(f)

        os.unlink(json_path)
        logger.debug("Archivo JSON temporal eliminado")

        is_valid = all(key in loaded_data for key in ['latitude', 'longitude'])
        print(f"✓ JSON cargado correctamente: {is_valid}")
        print(
            f"✓ Coordenadas: ({loaded_data['latitude']}, "
            f"{loaded_data['longitude']})")
        
        logger.info(f"JSON cargado correctamente: {is_valid}")
        logger.info(
            f"Coordenadas: ({loaded_data['latitude']}, "
            f"{loaded_data['longitude']})")
        logger.info("Test de carga de GPS desde JSON: PASS")
        
        return is_valid
    except Exception as e:
        error_msg = f"Error durante test de carga de GPS desde JSON: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"✗ {error_msg}")
        return False


def run_all_tests():
    """Ejecuta todas las pruebas"""
    global logger
    
    # Configurar logging
    log_file = 'test_results.log'
    logger = setup_logging(log_file)
    
    print("=" * 50)
    print("EJECUTANDO TESTS DEL EXTRACTOR DE FRAMES")
    print("=" * 50)
    
    logger.info("=" * 50)
    logger.info("INICIANDO TESTS DEL EXTRACTOR DE FRAMES")
    logger.info(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Archivo de log: {log_file}")
    logger.info("=" * 50)

    # Crear directorio temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info(f"Directorio temporal creado: {tmpdir}")
        video_path = os.path.join(tmpdir, "test_video.mp4")
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Directorio de salida creado: {output_dir}")

        # Crear video de prueba
        try:
            create_test_video(video_path)
            logger.info(f"Video de prueba creado exitosamente: {video_path}")
        except Exception as e:
            logger.error(f"Error al crear video de prueba: {str(e)}")
            logger.error(traceback.format_exc())
            return False

        # Ejecutar tests
        results = []
        results.append(("Video Reading", test_video_reading(video_path)))
        results.append(
            ("Frame Extraction",
             test_frame_extraction(
                 video_path,
                 output_dir)))
        results.append(("GPS Metadata", test_gps_metadata(output_dir)))
        results.append(("JSON GPS Loading", test_json_gps_loading()))

        # Resumen
        print("\n" + "=" * 50)
        print("RESUMEN DE TESTS")
        print("=" * 50)
        
        logger.info("\n" + "=" * 50)
        logger.info("RESUMEN DE TESTS")
        logger.info("=" * 50)
        
        passed_count = 0
        failed_count = 0
        
        for name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {name}")
            logger.info(f"{status}: {name}")
            if result:
                passed_count += 1
            else:
                failed_count += 1

        all_passed = all(r[1] for r in results)
        print("\n" + ("=" * 50))
        logger.info("\n" + ("=" * 50))
        
        summary = (
            f"Tests ejecutados: {len(results)} | "
            f"Exitosos: {passed_count} | "
            f"Fallidos: {failed_count}"
        )
        
        if all_passed:
            print("✓ TODOS LOS TESTS PASARON")
            logger.info("✓ TODOS LOS TESTS PASARON")
        else:
            print("✗ ALGUNOS TESTS FALLARON")
            logger.error("✗ ALGUNOS TESTS FALLARON")
        
        print(summary)
        logger.info(summary)
        print("=" * 50)
        logger.info("=" * 50)
        print(f"\nLog detallado guardado en: {log_file}")
        logger.info(f"Log detallado guardado en: {log_file}")

        return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
