#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Video Frame Extractor with GPS Preservation
Extrae fotogramas de videos manteniendo la georeferenciación
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import piexif
import json


class VideoFrameExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Extractor de Fotogramas con GPS")
        self.root.geometry("800x600")
        
        self.video_path = None
        self.video_fps = 0
        self.video_duration = 0
        self.video_total_frames = 0
        self.gps_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Selección de video
        video_frame = ttk.LabelFrame(main_frame, text="Selección de Video", padding="10")
        video_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.video_label = ttk.Label(video_frame, text="No se ha seleccionado ningún video")
        self.video_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        ttk.Button(video_frame, text="Seleccionar Video", command=self.select_video).grid(
            row=0, column=1, padx=5
        )
        
        # Información del video
        info_frame = ttk.LabelFrame(main_frame, text="Información del Video", padding="10")
        info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.info_label = ttk.Label(info_frame, text="")
        self.info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Configuración de extracción - Intervalo de tiempo
        time_frame = ttk.LabelFrame(main_frame, text="Intervalo de Tiempo", padding="10")
        time_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(time_frame, text="Inicio (segundos):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.start_time = tk.StringVar(value="0")
        ttk.Entry(time_frame, textvariable=self.start_time, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(time_frame, text="Fin (segundos):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.end_time = tk.StringVar(value="0")
        ttk.Entry(time_frame, textvariable=self.end_time, width=15).grid(row=0, column=3, padx=5)
        
        # Configuración de extracción - Intervalo de fotogramas
        frame_frame = ttk.LabelFrame(main_frame, text="Intervalo de Fotogramas", padding="10")
        frame_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(frame_frame, text="Extraer cada N fotogramas:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.frame_interval = tk.StringVar(value="30")
        ttk.Entry(frame_frame, textvariable=self.frame_interval, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(frame_frame, text="(ej: 30 = un fotograma cada 30 fotogramas)").grid(
            row=0, column=2, sticky=tk.W, padx=5
        )
        
        # GPS Data
        gps_frame = ttk.LabelFrame(main_frame, text="Datos GPS", padding="10")
        gps_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(gps_frame, text="Cargar Datos GPS (JSON)", command=self.load_gps_data).grid(
            row=0, column=0, padx=5
        )
        
        self.gps_status_label = ttk.Label(gps_frame, text="No se han cargado datos GPS")
        self.gps_status_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Carpeta de salida
        output_frame = ttk.LabelFrame(main_frame, text="Carpeta de Salida", padding="10")
        output_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.output_label = ttk.Label(output_frame, text="No se ha seleccionado carpeta de salida")
        self.output_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        ttk.Button(output_frame, text="Seleccionar Carpeta", command=self.select_output).grid(
            row=0, column=1, padx=5
        )
        
        # Botón de extracción
        ttk.Button(main_frame, text="Extraer Fotogramas", command=self.extract_frames, 
                   style='Accent.TButton').grid(row=6, column=0, columnspan=3, pady=20)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=8, column=0, columnspan=3, sticky=tk.W)
        
    def select_video(self):
        """Selecciona el archivo de video"""
        filename = filedialog.askopenfilename(
            title="Seleccionar Video",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.video_path = filename
            self.video_label.config(text=os.path.basename(filename))
            self.load_video_info()
            
    def load_video_info(self):
        """Carga información del video"""
        try:
            cap = cv2.VideoCapture(self.video_path)
            self.video_fps = cap.get(cv2.CAP_PROP_FPS)
            self.video_total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_duration = self.video_total_frames / self.video_fps if self.video_fps > 0 else 0
            cap.release()
            
            info_text = f"FPS: {self.video_fps:.2f} | Duración: {self.video_duration:.2f}s | Fotogramas totales: {self.video_total_frames}"
            self.info_label.config(text=info_text)
            
            # Actualizar valor por defecto del tiempo final
            self.end_time.set(str(int(self.video_duration)))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar información del video: {str(e)}")
            
    def load_gps_data(self):
        """Carga datos GPS desde un archivo JSON"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo GPS JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    gps_data = json.load(f)
                # Validate required GPS fields
                if not isinstance(gps_data, dict) or 'latitude' not in gps_data or 'longitude' not in gps_data:
                    messagebox.showerror("Error", "El archivo JSON de GPS debe contener los campos 'latitude' y 'longitude'.")
                    return
                self.gps_data = gps_data
                self.gps_status_label.config(text=f"GPS cargado: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar datos GPS: {str(e)}")
                
    def select_output(self):
        """Selecciona la carpeta de salida"""
        folder = filedialog.askdirectory(title="Seleccionar Carpeta de Salida")
        if folder:
            self.output_folder = folder
            self.output_label.config(text=folder)
            
    def convert_to_degrees(self, value):
        """Convierte coordenadas GPS a formato de grados para EXIF"""
        d = int(value)
        m = int((value - d) * 60)
        s = (value - d - m / 60) * 3600
        return ((d, 1), (m, 1), (int(s * 100), 100))
    
    def add_gps_to_image(self, image_path, lat, lon, alt=None):
        """Agrega datos GPS a una imagen"""
        try:
            # Cargar EXIF existente o crear nuevo
            try:
                exif_dict = piexif.load(image_path)
            except piexif.InvalidImageDataError:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            except Exception as e:
                print(f"Error inesperado al cargar EXIF de {image_path}: {str(e)}")
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            
            # Preparar datos GPS
            gps_ifd = {
                piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
                piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
                piexif.GPSIFD.GPSLatitude: self.convert_to_degrees(abs(lat)),
                piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
                piexif.GPSIFD.GPSLongitude: self.convert_to_degrees(abs(lon)),
            }
            
            if alt is not None:
                gps_ifd[piexif.GPSIFD.GPSAltitudeRef] = 0 if alt >= 0 else 1
                gps_ifd[piexif.GPSIFD.GPSAltitude] = (int(abs(alt) * 100), 100)
            
            exif_dict["GPS"] = gps_ifd
            
            # Guardar EXIF en la imagen
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, image_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar GPS a {image_path}: {str(e)}")
            
    def extract_frames(self):
        """Extrae fotogramas del video"""
        # Validaciones
        if not self.video_path:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un video")
            return
            
        if not hasattr(self, 'output_folder'):
            messagebox.showwarning("Advertencia", "Por favor, seleccione una carpeta de salida")
            return
            
        try:
            start = float(self.start_time.get())
            end = float(self.end_time.get())
            interval = int(self.frame_interval.get())
            
            if start < 0 or end > self.video_duration or start >= end:
                messagebox.showerror("Error", "Intervalo de tiempo inválido")
                return
                
            if interval < 1:
                messagebox.showerror("Error", "El intervalo de fotogramas debe ser al menos 1")
                return
                
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos")
            return
            
        # Procesar extracción
        try:
            cap = cv2.VideoCapture(self.video_path)
            
            start_frame = int(start * self.video_fps)
            end_frame = int(end * self.video_fps)
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            extracted_count = 0
            total_to_extract = ((end_frame - start_frame) // interval) + 1
            
            self.progress['maximum'] = total_to_extract
            self.progress['value'] = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                
                if current_frame > end_frame:
                    break
                    
                if (current_frame - start_frame) % interval == 0:
                    # Guardar fotograma
                    timestamp = current_frame / self.video_fps
                    filename = f"frame_{current_frame:06d}_t{timestamp:.2f}s.jpg"
                    filepath = os.path.join(self.output_folder, filename)
                    
                    cv2.imwrite(filepath, frame)
                    
                    # Agregar GPS si está disponible
                    if self.gps_data:
                        lat = self.gps_data.get('latitude', 0)
                        lon = self.gps_data.get('longitude', 0)
                        alt = self.gps_data.get('altitude')
                        self.add_gps_to_image(filepath, lat, lon, alt)
                    
                    extracted_count += 1
                    self.progress['value'] = extracted_count
                    self.status_label.config(
                        text=f"Extrayendo: {extracted_count}/{total_to_extract} fotogramas"
                    )
                    self.root.update()
                
            cap.release()
            
            self.status_label.config(text=f"¡Extracción completada! {extracted_count} fotogramas guardados")
            messagebox.showinfo(
                "Éxito", 
                f"Se han extraído {extracted_count} fotogramas\nGuardados en: {self.output_folder}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la extracción: {str(e)}")
            self.status_label.config(text="Error en la extracción")


def main():
    root = tk.Tk()
    VideoFrameExtractor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
