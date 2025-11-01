import os, cv2, numpy as np, joblib
from skimage.feature import hog
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import albumentations as A
from albumentations.pytorch import ToTensorV2

# Configuration
DATA_SET_DIR = "dashboard/Logic/Machine/dataset"
MODEL_PATH = "dashboard/Logic/Machine/model/svm_emotion_model.pkl"
SCALER_PATH = "dashboard/Logic/Machine/scaler/scaler.pkl"
EMOTIONS = ["Angry", "Happy", "Sad"] 
IMAGE_SIZE = (48, 48)

def augment_image(img):
    """Apply data augmentation to create variations of an image"""
    augmentations = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.Rotate(limit=15, p=0.5),
        A.GaussianBlur(blur_limit=3, p=0.3),
        A.RandomBrightnessContrast(p=0.3),
        A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=0.3),
    ])
    
    augmented = augmentations(image=img)
    return augmented['image']

def load_and_extract_features_with_augmentation(augment_factor=5):
    """Load images and create augmented versions"""
    features = []
    labels = []
    
    print("[INFO] Loading images with data augmentation...")
    
    for label, emotion in enumerate(EMOTIONS):
        folder = os.path.join(DATA_SET_DIR, emotion)
        if not os.path.isdir(folder):
            print(f"[WARNING] Folder not found: {folder}")
            continue
        
        print(f"[INFO] Processing {emotion} images...")
        processed_count = 0
        
        for file in os.listdir(folder):
            if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                continue
                
            path = os.path.join(folder, file)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            
            img = cv2.resize(img, IMAGE_SIZE)
            
            # Original image
            try:
                hog_features = hog(img, pixels_per_cell=(8,8), cells_per_block=(2,2), 
                                 orientations=9, feature_vector=True)
                features.append(hog_features)
                labels.append(label)
                processed_count += 1
                
                # Create augmented versions
                for i in range(augment_factor):
                    augmented_img = augment_image(img)
                    aug_hog_features = hog(augmented_img, pixels_per_cell=(8,8), cells_per_block=(2,2), 
                                         orientations=9, feature_vector=True)
                    features.append(aug_hog_features)
                    labels.append(label)
                    processed_count += 1
                    
            except Exception as e:
                print(f"[ERROR] Failed to process {path}: {e}")
                continue
        
        print(f"[INFO] Processed {processed_count} {emotion} images (original + augmented)")
    
    return np.array(features), np.array(labels)

def evaluate_model(model, X_test, y_test, X_train=None, y_train=None):
    """Evaluate model performance"""
    if X_test is not None and y_test is not None:
        y_pred = model.predict(X_test)
        
        print("\n[EVALUATION] Classification Report:")
        print(classification_report(y_test, y_pred, target_names=EMOTIONS))
        
        print("\n[EVALUATION] Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        accuracy = model.score(X_test, y_test)
        print(f"\n[RESULT] Test accuracy: {accuracy * 100:.2f}%")
    else:
        # If no test set, use training accuracy
        accuracy = model.score(X_train, y_train)
        print(f"\n[RESULT] Training accuracy: {accuracy * 100:.2f}%")
    
    return accuracy

def main():
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
    
    # Load and extract features
    features, labels = load_and_extract_features_with_augmentation()
    
    if len(features) == 0:
        print("[ERROR] No features extracted. Check your dataset path and images.")
        return
    
    print(f"[INFO] Loaded {len(features)} samples from dataset.")
    print(f"[INFO] Feature vector shape: {features.shape}")
    
    # Check class distribution
    unique, counts = np.unique(labels, return_counts=True)
    print(f"[INFO] Class distribution: {dict(zip([EMOTIONS[i] for i in unique], counts))}")
    
    # Handle different dataset sizes
    total_samples = len(features)
    
    if total_samples < 10:
        print("[WARNING] Very small dataset. Using entire dataset for training.")
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Train on entire dataset
        print("[INFO] Training SVM model on entire dataset...")
        svm = SVC(kernel="linear", probability=True, random_state=42)
        svm.fit(scaled_features, labels)
        
        # Evaluate on training data
        evaluate_model(svm, None, None, scaled_features, labels)
        
    elif total_samples < 30:
        print("[INFO] Small dataset detected. Using 80-20 split without stratification.")
        
        # Split without stratification for small datasets
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42
        )
        
        print(f"[INFO] Training set: {X_train.shape[0]} samples")
        print(f"[INFO] Test set: {X_test.shape[0]} samples")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        print("[INFO] Training SVM model...")
        svm = SVC(kernel="linear", probability=True, random_state=42)
        svm.fit(X_train_scaled, y_train)
        
        # Evaluate model
        evaluate_model(svm, X_test_scaled, y_test)
        
    else:
        # Normal train-test split for larger datasets
        print("[INFO] Using stratified train-test split.")
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        print(f"[INFO] Training set: {X_train.shape[0]} samples")
        print(f"[INFO] Test set: {X_test.shape[0]} samples")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        print("[INFO] Training SVM model...")
        svm = SVC(kernel="linear", probability=True, random_state=42)
        svm.fit(X_train_scaled, y_train)
        
        # Evaluate model
        evaluate_model(svm, X_test_scaled, y_test)
    
    # Save model and scaler
    joblib.dump(svm, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    
    print(f"[SAVED] Model -> {MODEL_PATH}")
    print(f"[SAVED] Scaler -> {SCALER_PATH}")
    
    # Dataset size recommendations
    print("\n[DATASET ANALYSIS]")
    if total_samples < 50:
        print(f"⚠️  Dataset is small ({total_samples} total images)")
        print("   Recommendations:")
        print(f"   - Aim for 50-100 images per class (currently {total_samples//len(EMOTIONS)} per class)")
        print("   - Consider data augmentation")
        print("   - Results may not generalize well")
    else:
        print(f"✅ Dataset size is adequate ({total_samples} total images)")
    
    print("[DONE] Training complete!")

if __name__ == "__main__":
    main()