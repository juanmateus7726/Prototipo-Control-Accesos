import cv2
import numpy as np
import os
import base64
from PIL import Image
import io
from django.conf import settings
from django.core.files.base import ContentFile

class OpenCVFaceRecognitionSystem:
    def __init__(self):
        # Inicializar detectores de OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Inicializar reconocedor LBPH (Local Binary Patterns Histograms)
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Configuraciones
        self.confidence_threshold = 80  # Menor valor = más estricto
        self.face_size = (200, 200)  # Tamaño estándar para las caras
        self.trained = False
        
        # Datos de entrenamiento
        self.known_faces = []
        self.known_labels = []
        self.known_names = {}  # label -> nombre
        self.known_ids = {}    # label -> user_id
        
    def detect_faces(self, image):
        """
        Detecta rostros en una imagen usando Haar Cascades
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return faces, gray
    
    def extract_face_features(self, image, face_rect):
        """
        Extrae características del rostro usando LBPH
        """
        x, y, w, h = face_rect
        face_roi = image[y:y+h, x:x+w]
        
        # Redimensionar a tamaño estándar
        face_resized = cv2.resize(face_roi, self.face_size)
        
        # Ecualización del histograma para mejorar contraste
        face_equalized = cv2.equalizeHist(face_resized)
        
        return face_equalized
    
    def encode_face_from_base64(self, base64_image):
        """
        Procesa una imagen en base64 y extrae características faciales
        """
        try:
            # Decodificar base64
            image_data = base64.b64decode(base64_image.split(',')[1])
            image = Image.open(io.BytesIO(image_data))
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convertir PIL a numpy array para OpenCV
            image_np = np.array(image)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            
            # Detectar rostros
            faces, gray = self.detect_faces(image_bgr)
            
            if len(faces) == 0:
                return None, "No se detectó ningún rostro en la imagen"
            
            if len(faces) > 1:
                return None, "Se detectaron múltiples rostros. Use una imagen con un solo rostro"
            
            # Extraer características del primer rostro detectado
            face_features = self.extract_face_features(gray, faces[0])
            
            return face_features, "Rostro procesado exitosamente"
            
        except Exception as e:
            return None, f"Error al procesar la imagen: {str(e)}"
    
    def save_face_encoding(self, face_features):
        """
        Convierte las características faciales a string para guardar en BD
        """
        if face_features is not None:
            # Serializar la matriz numpy a base64
            face_bytes = face_features.tobytes()
            face_shape = face_features.shape
            encoding_data = {
                'data': base64.b64encode(face_bytes).decode('utf-8'),
                'shape': face_shape,
                'dtype': str(face_features.dtype)
            }
            return str(encoding_data)
        return None
    
    def load_face_encoding(self, encoding_str):
        """
        Convierte string de BD de vuelta a matriz numpy
        """
        try:
            if encoding_str:
                encoding_data = eval(encoding_str)  # Convertir string a dict
                face_bytes = base64.b64decode(encoding_data['data'])
                face_array = np.frombuffer(face_bytes, dtype=encoding_data['dtype'])
                face_features = face_array.reshape(encoding_data['shape'])
                return face_features
            return None
        except Exception as e:
            print(f"Error al cargar codificación: {e}")
            return None
    
    def load_known_faces(self, usuarios):
        """
        Carga todas las caras conocidas y entrena el reconocedor
        """
        self.known_faces = []
        self.known_labels = []
        self.known_names = {}
        self.known_ids = {}
        
        label = 0
        for usuario in usuarios:
            if usuario.face_encoding and usuario.face_registered:
                face_features = self.load_face_encoding(usuario.face_encoding)
                if face_features is not None:
                    self.known_faces.append(face_features)
                    self.known_labels.append(label)
                    self.known_names[label] = usuario.nombre
                    self.known_ids[label] = usuario.id
                    label += 1
        
        # Entrenar el reconocedor si hay caras
        if len(self.known_faces) > 0:
            self.face_recognizer.train(self.known_faces, np.array(self.known_labels))
            self.trained = True
            return True
        
        self.trained = False
        return False
    
    def recognize_face_from_base64(self, base64_image, usuarios):
        """
        Reconoce un rostro desde una imagen en base64
        """
        try:
            # Cargar y entrenar con caras conocidas
            if not self.load_known_faces(usuarios):
                return None, None, "No hay rostros registrados en el sistema"
            
            # Procesar imagen de entrada
            face_features, message = self.encode_face_from_base64(base64_image)
            
            if face_features is None:
                return None, None, message
            
            # Realizar predicción
            label, confidence = self.face_recognizer.predict(face_features)
            
            # Verificar confianza (menor valor = mejor match)
            if confidence < self.confidence_threshold:
                user_id = self.known_ids.get(label)
                user_name = self.known_names.get(label)
                
                # Convertir confianza a porcentaje (invertido porque menor es mejor)
                confidence_percent = max(0, 100 - confidence)
                
                return user_id, confidence_percent, f"¡Bienvenido {user_name}! Acceso autorizado"
            else:
                return None, None, "Rostro no reconocido. Acceso denegado"
                
        except Exception as e:
            return None, None, f"Error en el reconocimiento: {str(e)}"
    
    def save_face_image_from_base64(self, base64_image, filename):
        """
        Guarda una imagen desde base64 en el sistema de archivos
        """
        try:
            # Decodificar base64
            format_part, imgstr = base64_image.split(';base64,')
            ext = format_part.split('/')[-1]
            
            # Crear archivo
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f"{filename}.{ext}"
            )
            
            return data
            
        except Exception as e:
            print(f"Error al guardar imagen: {e}")
            return None
    
    def verify_face_quality(self, base64_image):
        """
        Verifica la calidad del rostro capturado
        """
        try:
            # Decodificar imagen
            image_data = base64.b64decode(base64_image.split(',')[1])
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            image_np = np.array(image)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            
            # Detectar rostros y ojos
            faces, gray = self.detect_faces(image_bgr)
            
            if len(faces) == 0:
                return False, "No se detectó ningún rostro"
            
            if len(faces) > 1:
                return False, "Se detectaron múltiples rostros"
            
            # Verificar si hay ojos (mejora la calidad del reconocimiento)
            x, y, w, h = faces[0]
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            
            if len(eyes) < 2:
                return False, "Rostro de baja calidad - asegúrese de que ambos ojos sean visibles"
            
            # Verificar tamaño mínimo del rostro
            if w < 100 or h < 100:
                return False, "Rostro muy pequeño - acérquese más a la cámara"
            
            return True, "Rostro de buena calidad detectado"
            
        except Exception as e:
            return False, f"Error verificando calidad: {str(e)}"

# Instancia global del sistema
opencv_face_system = OpenCVFaceRecognitionSystem()