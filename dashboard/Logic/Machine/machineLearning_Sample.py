from PyQt5.QtWidgets import QMainWindow as MAIN, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from Designer_Files.ui.tracker import Ui_Tracker as TRACKER_UI
import sys, cv2, numpy as np, joblib
from skimage.feature import hog
import os
import time

class DetectionThread(QThread):
    frameReady = pyqtSignal(object)
    emotionDetected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None
        self.last_emotion = "Unknown"
        self.emotion_confidence = 0
        self.stable_emotion_count = 0
        self.required_stable_frames = 3  # Require 3 consistent predictions
        
        # Load model and scaler with error handling
        try:
            self.model = joblib.load("dashboard/Logic/Machine/model/svm_emotion_model.pkl")
            self.scaler = joblib.load("dashboard/Logic/Machine/scaler/scaler.pkl")
            self.emotions = ["Angry", "Happy", "Sad"]
            print("[INFO] Model and scaler loaded successfully")
        except Exception as e:
            print(f"[ERROR] Could not load model or scaler: {e}")
            self.model = None
            self.scaler = None
            self.emotions = ["Unknown"]
        
        # Try multiple cascade classifiers for better detection
        self.face_cascades = []
        
        # Primary: Use DNN-based face detector (more accurate)
        try:
            protoPath = "dashboard/Logic/Machine/xml/deploy.prototxt"
            modelPath = "dashboard/Logic/Machine/xml/res10_300x300_ssd_iter_140000_fp16.caffemodel"
            if os.path.exists(protoPath) and os.path.exists(modelPath):
                self.dnn_net = cv2.dnn.readNetFromCaffe(protoPath, modelPath)
                self.use_dnn = True
                print("[INFO] Loaded DNN face detector")
            else:
                self.use_dnn = False
                print("[INFO] Using Haar cascades (DNN not available)")
        except:
            self.use_dnn = False
        
        # Fallback: Haar cascades
        cascade_paths = [
            "dashboard/Logic/Machine/xml/haarcascade_frontalface_default.xml",
            "dashboard/Logic/Machine/xml/haarcascade_frontalface_alt.xml",
            "dashboard/Logic/Machine/xml/haarcascade_frontalface_alt2.xml"
        ]
        
        for path in cascade_paths:
            if os.path.exists(path):
                cascade = cv2.CascadeClassifier(path)
                if not cascade.empty():
                    self.face_cascades.append(cascade)
                    print(f"[INFO] Loaded cascade: {path}")
        
        if not self.face_cascades and not self.use_dnn:
            print("[ERROR] No face detectors available")

    def start_camera(self):
        """Start the camera"""
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            # Set camera resolution for better quality
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.cap.isOpened():
                print("[ERROR] Could not open camera")
                return False
        
        self.running = True
        if not self.isRunning():
            self.start()
        print("[INFO] Camera started")
        return True

    def stop_camera(self):
        """Stop the camera"""
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        print("[INFO] Camera stopped")
    
    def detect_faces_dnn(self, frame):
        """Use DNN for more accurate face detection"""
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                    (300, 300), (104.0, 177.0, 123.0))
        self.dnn_net.setInput(blob)
        detections = self.dnn_net.forward()
        
        faces = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:  # Confidence threshold
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                # Ensure bounding boxes are within frame dimensions
                startX, startY = max(0, startX), max(0, startY)
                endX, endY = min(w - 1, endX), min(h - 1, endY)
                faces.append((startX, startY, endX - startX, endY - startY))
        
        return faces
    
    def detect_faces_haar(self, gray):
        """Use multiple Haar cascades for better detection"""
        all_faces = []
        
        for cascade in self.face_cascades:
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,  # More sensitive scaling
                minNeighbors=6,   # Require more neighbors for better accuracy
                minSize=(50, 50), # Larger minimum size for better quality
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            all_faces.extend(faces)
        
        # Remove duplicate faces using non-maximum suppression
        if len(all_faces) > 0:
            # Convert to (x, y, w, h) format and apply NMS
            boxes = []
            for (x, y, w, h) in all_faces:
                boxes.append([x, y, x + w, y + h])
            
            # Simple NMS - keep largest face
            if boxes:
                areas = [(box[2] - box[0]) * (box[3] - box[1]) for box in boxes]
                largest_idx = np.argmax(areas)
                x1, y1, x2, y2 = boxes[largest_idx]
                return [(x1, y1, x2 - x1, y2 - y1)]
        
        return []
        
    def extractFeatures(self, face):
        """Extract HOG features from face ROI with preprocessing"""
        try:
            # Apply preprocessing for better feature extraction
            resized = cv2.resize(face, (48, 48))
            
            # Apply histogram equalization for better contrast
            equalized = cv2.equalizeHist(resized)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(equalized, (3, 3), 0)
            
            features = hog(blurred, pixels_per_cell=(8, 8), cells_per_block=(2, 2), 
                          orientations=9, feature_vector=True)
            
            if self.scaler:
                scaled = self.scaler.transform([features])
                return scaled
            return [features]
        except Exception as e:
            print(f"[ERROR] Feature extraction failed: {e}")
            return None
    
    def get_emotion_confidence(self, features):
        """Get confidence score for emotion prediction"""
        if self.model and hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features)[0]
            confidence = np.max(probabilities)
            return confidence, probabilities
        return 0.5, None

    def run(self):
        frame_count = 0
        while self.running:
            if self.cap is None or not self.cap.isOpened():
                break
                
            ret, frame = self.cap.read()
            if not ret:
                print("[WARNING] Could not read frame from camera")
                continue
            
            # Flip for mirror effect
            frame = cv2.flip(frame, 1)
            frame_count += 1

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces using best available method
            faces = []
            if self.use_dnn:
                faces = self.detect_faces_dnn(frame)
            elif self.face_cascades:
                faces = self.detect_faces_haar(gray)
            
            emotion_text = "No Face"
            current_confidence = 0
            
            for (x, y, w, h) in faces:
                # Ensure face is large enough for good detection
                if w < 80 or h < 80:  # Minimum face size
                    continue
                    
                # Extract face ROI with padding
                padding = 10
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(frame.shape[1], x + w + padding)
                y2 = min(frame.shape[0], y + h + padding)
                
                roi = gray[y1:y2, x1:x2]
                
                # Only process if we have a valid model and good ROI
                if self.model is not None and roi.size > 0:
                    features = self.extractFeatures(roi)
                    if features is not None:
                        try:
                            pred = self.model.predict(features)[0]
                            confidence, probabilities = self.get_emotion_confidence(features)
                            current_confidence = confidence
                            
                            # Only update emotion if confidence is good
                            if confidence > 0.6:  # Confidence threshold
                                proposed_emotion = self.emotions[int(pred)]
                                
                                # Stability check - require multiple consistent predictions
                                if proposed_emotion == self.last_emotion:
                                    self.stable_emotion_count += 1
                                else:
                                    self.stable_emotion_count = 1
                                    self.last_emotion = proposed_emotion
                                
                                # Only emit emotion if stable for required frames
                                if self.stable_emotion_count >= self.required_stable_frames:
                                    emotion_text = proposed_emotion
                                else:
                                    emotion_text = "Analyzing..."
                            else:
                                emotion_text = "Low Confidence"
                                self.stable_emotion_count = 0
                                
                        except Exception as e:
                            print(f"[ERROR] Prediction failed: {e}")
                            emotion_text = "Unknown"
                else:
                    emotion_text = "Face Detected"
                
                # Draw rectangle with confidence-based color
                color = (0, 255, 0)  # Green - high confidence
                if current_confidence < 0.6:
                    color = (0, 255, 255)  # Yellow - medium confidence
                if emotion_text == "Low Confidence":
                    color = (0, 165, 255)  # Orange - low confidence
                
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                
                # Display emotion and confidence
                label = f"{emotion_text} ({current_confidence:.2f})"
                cv2.putText(frame, label, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Emit the detected emotion
                self.emotionDetected.emit(emotion_text)
                break  # Process only the first face for now
            
            # If no faces detected, emit "No Face"
            if len(faces) == 0:
                self.emotionDetected.emit("No Face")
                self.stable_emotion_count = 0
            
            # Emit the frame for display
            self.frameReady.emit(frame)
            
            # Small delay to prevent overwhelming the system
            self.msleep(30)

    def stop(self):
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.wait()

# Rest of the MachineLearning class remains the same...
class MachineLearning(MAIN, TRACKER_UI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Detection thread
        self.detector = DetectionThread()
        self.detector.frameReady.connect(self.updateFrame)
        self.detector.emotionDetected.connect(self.updateStatus)
        
        # Camera state
        self.camera_active = False
        
        # Add camera control buttons using absolute positioning
        self.add_camera_controls()
        
        # Initial state - camera off
        self.VideoLabel.setText("Camera Off\nClick 'Start Camera' to begin")
        self.VideoLabel.setStyleSheet("color: gray; font-size: 16px; background-color: black;")
        self.VideoLabel.setAlignment(Qt.AlignCenter)

    def add_camera_controls(self):
        """Add camera control buttons using absolute positioning"""
        # Create buttons with absolute positioning
        self.start_btn = QPushButton("Start Camera", self)
        self.stop_btn = QPushButton("Stop Camera", self)
        
        # Position buttons at the top (adjust coordinates as needed)
        self.start_btn.setGeometry(10, 625, 120, 30)
        self.stop_btn.setGeometry(140, 625, 120, 30)
        
        # Style buttons
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        # Connect signals
        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)
        
        # Initially disable stop button
        self.stop_btn.setEnabled(False)

    def start_camera(self):
        """Start camera detection"""
        if not self.camera_active:
            success = self.detector.start_camera()
            if success:
                self.camera_active = True
                self.notifier.setText("CAMERA ACTIVE - DETECTING...")
                self.notifier.setStyleSheet("color: green; font-size: 14px;")
                
                # Update button states
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                
                print("[INFO] Camera started successfully")
            else:
                self.notifier.setText("CAMERA ERROR - CHECK CAMERA")
                self.notifier.setStyleSheet("color: red; font-size: 14px;")
                print("[ERROR] Failed to start camera")

    def stop_camera(self):
        """Stop camera detection"""
        if self.camera_active:
            self.detector.stop_camera()
            self.camera_active = False
            
            # Clear the video label
            self.VideoLabel.clear()
            self.VideoLabel.setText("Camera Off\nClick 'Start Camera' to begin")
            self.VideoLabel.setStyleSheet("color: gray; font-size: 16px; background-color: black;")
            self.VideoLabel.setAlignment(Qt.AlignCenter)
            
            self.notifier.setStyleSheet("color: orange; font-size: 14px;")
            
            # Update button states
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            
            print("[INFO] Camera stopped")

    def updateFrame(self, frame):
        """Update the video display with new frame"""
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            
            # Scale pixmap to fit the label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(self.VideoLabel.width(), self.VideoLabel.height(),
                                        Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.VideoLabel.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"[ERROR] Frame update failed: {e}")

    def updateStatus(self, emotion):
        """Update the status label with detection results"""
        if not self.camera_active:
            return
            
        if emotion == "No Face":
            self.notifier.setText("NO FACE DETECTED :(")
            self.notifier.setStyleSheet("color: red; font-size: 14px;")
        elif emotion in ["Angry", "Happy", "Sad"]:
            self.notifier.setText(f"EMOTION: {emotion.upper()}!")
            if emotion == "Happy":
                self.notifier.setStyleSheet("color: green; font-size: 14px;")
            elif emotion == "Angry":
                self.notifier.setStyleSheet("color: orange; font-size: 14px;")
            else:  # Sad
                self.notifier.setStyleSheet("color: blue; font-size: 14px;")
        elif emotion == "Analyzing...":
            self.notifier.setText("ANALYZING EMOTION...")
            self.notifier.setStyleSheet("color: yellow; font-size: 14px;")
        elif emotion == "Low Confidence":
            self.notifier.setText("LOW CONFIDENCE - MOVE CLOSER")
            self.notifier.setStyleSheet("color: orange; font-size: 14px;")
        else:
            self.notifier.setText("FACE DETECTED - ANALYZING...")
            self.notifier.setStyleSheet("color: yellow; font-size: 14px;")

    def closeEvent(self, event):
        """Clean up when application closes"""
        print("[INFO] Closing application...")
        self.detector.stop_camera()
        if self.detector.isRunning():
            self.detector.quit()
            self.detector.wait(1000)
        event.accept()

    def OpenWindow(self):
        """Method to open this window (for integration with your dashboard)"""
        self.show()
        # Ensure camera is stopped when window opens
        self.stop_camera()

# -------------------- Run Application --------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MachineLearning()
    window.show()
    
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"[ERROR] Application crashed: {e}")