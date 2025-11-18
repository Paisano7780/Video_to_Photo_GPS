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
        cv2.putText(frame, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        out.write(frame)
    
    out.release()
    print(f"Video de prueba creado: {filepath}")
    return filepath

def test_video_reading(video_path):
    """Prueba la lectura de video"""
    print("\n=== Test: Lectura de Video ===")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    cap.release()
    
    print(f"✓ FPS: {fps}")
    print(f"✓ Total frames: {total_frames}")
    print(f"✓ Duración: {duration:.2f}s")
    return True

def test_frame_extraction(video_path, output_dir):
    """Prueba la extracción de frames"""
    print("\n=== Test: Extracción de Frames ===")
    cap = cv2.VideoCapture(video_path)
    
    frame_interval = 30
    extracted = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        
        if current_frame % frame_interval == 0:
            output_path = os.path.join(output_dir, f"test_frame_{current_frame:06d}.jpg")
            cv2.imwrite(output_path, frame)
            extracted += 1
    
    cap.release()
    print(f"✓ Frames extraídos: {extracted}")
    return extracted > 0

def test_gps_metadata(output_dir):
    """Prueba la adición de metadatos GPS"""
    print("\n=== Test: Metadatos GPS ===")
    
    # Crear una imagen de prueba
    test_image_path = os.path.join(output_dir, "test_gps.jpg")
    img = Image.new('RGB', (100, 100), color='white')
    img.save(test_image_path)
    
    # Función para convertir coordenadas
    def convert_to_degrees(value):
        d = int(value)
        m = int((value - d) * 60)
        s = (value - d - m / 60) * 3600
        return ((d, 1), (m, 1), (int(s * 100), 100))
    
    # Agregar GPS
    lat, lon, alt = 40.416775, -3.703790, 650
    
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    
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
    
    # Verificar que se guardó
    exif_data = piexif.load(test_image_path)
    has_gps = "GPS" in exif_data and len(exif_data["GPS"]) > 0
    
    print(f"✓ GPS metadata agregado: {has_gps}")
    print(f"✓ Latitud: {lat}, Longitud: {lon}, Altitud: {alt}m")
    return has_gps

def test_json_gps_loading():
    """Prueba la carga de datos GPS desde JSON"""
    print("\n=== Test: Carga de GPS desde JSON ===")
    
    # Crear un archivo JSON de prueba
    gps_data = {
        "latitude": 40.416775,
        "longitude": -3.703790,
        "altitude": 650,
        "description": "Test location"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(gps_data, f)
        json_path = f.name
    
    # Cargar y verificar
    with open(json_path, 'r') as f:
        loaded_data = json.load(f)
    
    os.unlink(json_path)
    
    is_valid = all(key in loaded_data for key in ['latitude', 'longitude'])
    print(f"✓ JSON cargado correctamente: {is_valid}")
    print(f"✓ Coordenadas: ({loaded_data['latitude']}, {loaded_data['longitude']})")
    return is_valid

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("="*50)
    print("EJECUTANDO TESTS DEL EXTRACTOR DE FRAMES")
    print("="*50)
    
    # Crear directorio temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, "test_video.mp4")
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Crear video de prueba
        create_test_video(video_path)
        
        # Ejecutar tests
        results = []
        results.append(("Video Reading", test_video_reading(video_path)))
        results.append(("Frame Extraction", test_frame_extraction(video_path, output_dir)))
        results.append(("GPS Metadata", test_gps_metadata(output_dir)))
        results.append(("JSON GPS Loading", test_json_gps_loading()))
        
        # Resumen
        print("\n" + "="*50)
        print("RESUMEN DE TESTS")
        print("="*50)
        for name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {name}")
        
        all_passed = all(r[1] for r in results)
        print("\n" + ("="*50))
        if all_passed:
            print("✓ TODOS LOS TESTS PASARON")
        else:
            print("✗ ALGUNOS TESTS FALLARON")
        print("="*50)
        
        return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
