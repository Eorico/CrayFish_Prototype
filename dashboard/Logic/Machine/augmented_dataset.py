import os
import cv2
import numpy as np
from pathlib import Path
import random

class ImageAugmentor:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.emotions = ["Angry", "Happy", "Sad"]
        self.augmented_path = os.path.join(dataset_path, "dataset")
        
        # Create augmented directory
        os.makedirs(self.augmented_path, exist_ok=True)
        for emotion in self.emotions:
            os.makedirs(os.path.join(self.augmented_path, emotion), exist_ok=True)
    
    def rotate_image(self, image, angle):
        """Rotate image by given angle"""
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR)
        return rotated
    
    def adjust_brightness(self, image, factor):
        """Adjust image brightness"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv = hsv.astype(np.float32)
        hsv[:, :, 2] = hsv[:, :, 2] * factor
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        hsv = hsv.astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    def adjust_contrast(self, image, factor):
        """Adjust image contrast"""
        mean = np.mean(image, axis=(0, 1))
        adjusted = (image - mean) * factor + mean
        return np.clip(adjusted, 0, 255).astype(np.uint8)
    
    def add_gaussian_blur(self, image, kernel_size=3):
        """Add Gaussian blur"""
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    
    def add_gaussian_noise(self, image):
        """Add Gaussian noise"""
        row, col, ch = image.shape
        mean = 0
        var = 10
        sigma = var ** 0.5
        gauss = np.random.normal(mean, sigma, (row, col, ch))
        gauss = gauss.reshape(row, col, ch)
        noisy = image + gauss
        return np.clip(noisy, 0, 255).astype(np.uint8)
    
    def shift_image(self, image, x_shift, y_shift):
        """Shift image horizontally and vertically"""
        height, width = image.shape[:2]
        translation_matrix = np.float32([[1, 0, x_shift], [0, 1, y_shift]])
        shifted = cv2.warpAffine(image, translation_matrix, (width, height))
        return shifted
    
    def zoom_image(self, image, zoom_factor):
        """Zoom in/out of image"""
        height, width = image.shape[:2]
        # Calculate new dimensions
        new_height, new_width = int(height * zoom_factor), int(width * zoom_factor)
        
        # Resize image
        zoomed = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        
        # Crop or pad to original size
        if zoom_factor > 1.0:
            # If zoomed in, take center crop
            start_y = (new_height - height) // 2
            start_x = (new_width - width) // 2
            zoomed = zoomed[start_y:start_y + height, start_x:start_x + width]
        else:
            # If zoomed out, pad with black
            pad_y = (height - new_height) // 2
            pad_x = (width - new_width) // 2
            zoomed = cv2.copyMakeBorder(zoomed, pad_y, pad_y, pad_x, pad_x, 
                                      cv2.BORDER_CONSTANT, value=[0, 0, 0])
            # If dimensions don't match exactly, resize to original
            if zoomed.shape[:2] != (height, width):
                zoomed = cv2.resize(zoomed, (width, height))
        
        return zoomed
    
    def flip_image(self, image, flip_type):
        """Flip image horizontally, vertically, or both"""
        if flip_type == 'horizontal':
            return cv2.flip(image, 1)
        elif flip_type == 'vertical':
            return cv2.flip(image, 0)
        else:  # both
            return cv2.flip(image, -1)
    
    def elastic_transform(self, image, alpha=100, sigma=10):
        """Elastic deformation of images"""
        random_state = np.random.RandomState(None)
        shape = image.shape[:2]
        
        dx = random_state.rand(*shape) * 2 - 1
        dy = random_state.rand(*shape) * 2 - 1
        
        dx = cv2.GaussianBlur(dx, (0, 0), sigma) * alpha
        dy = cv2.GaussianBlur(dy, (0, 0), sigma) * alpha
        
        x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
        indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))
        
        transformed = cv2.remap(image, indices[1].astype(np.float32), 
                               indices[0].astype(np.float32), 
                               cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return transformed
    
    def apply_augmentations(self, image, num_variations=10):
        """Apply multiple augmentations to create variations"""
        augmented_images = []
        
        # Always keep original
        augmented_images.append(image)
        
        # Define augmentation parameters
        augmentations = [
            # Rotation variations
            lambda img: self.rotate_image(img, random.uniform(-15, 15)),
            lambda img: self.rotate_image(img, random.uniform(-10, 10)),
            
            # Brightness variations
            lambda img: self.adjust_brightness(img, random.uniform(0.7, 1.3)),
            lambda img: self.adjust_brightness(img, random.uniform(0.8, 1.2)),
            
            # Contrast variations
            lambda img: self.adjust_contrast(img, random.uniform(0.8, 1.2)),
            
            # Blur variations
            lambda img: self.add_gaussian_blur(img, random.choice([3, 5])),
            
            # Noise variations
            lambda img: self.add_gaussian_noise(img),
            
            # Shift variations
            lambda img: self.shift_image(img, random.randint(-10, 10), random.randint(-10, 10)),
            lambda img: self.shift_image(img, random.randint(-5, 5), random.randint(-5, 5)),
            
            # Zoom variations
            lambda img: self.zoom_image(img, random.uniform(0.9, 1.1)),
            lambda img: self.zoom_image(img, random.uniform(0.95, 1.05)),
            
            # Flip variations
            lambda img: self.flip_image(img, 'horizontal'),
            
            # Elastic transform
            lambda img: self.elastic_transform(img, alpha=50, sigma=5),
        ]
        
        # Apply random augmentations
        for _ in range(num_variations - 1):
            aug_img = image.copy()
            
            # Apply 1-3 random augmentations to each variation
            num_augs = random.randint(1, 3)
            selected_augs = random.sample(augmentations, num_augs)
            
            for aug_func in selected_augs:
                try:
                    aug_img = aug_func(aug_img)
                except Exception as e:
                    # If augmentation fails, use the previous version
                    continue
            
            augmented_images.append(aug_img)
        
        return augmented_images
    
    def augment_dataset(self, variations_per_image=15):
        """Augment the entire dataset"""
        print(f"[INFO] Starting dataset augmentation...")
        print(f"[INFO] Source: {self.dataset_path}")
        print(f"[INFO] Target: {self.augmented_path}")
        print(f"[INFO] Creating {variations_per_image} variations per image")
        
        total_original = 0
        total_augmented = 0
        
        for emotion in self.emotions:
            emotion_path = os.path.join(self.dataset_path, emotion)
            augmented_emotion_path = os.path.join(self.augmented_path, emotion)
            
            if not os.path.exists(emotion_path):
                print(f"[WARNING] Emotion folder not found: {emotion_path}")
                continue
            
            image_files = [f for f in os.listdir(emotion_path) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            
            print(f"\n[INFO] Processing {emotion}: {len(image_files)} images")
            
            emotion_original = 0
            emotion_augmented = 0
            
            for i, image_file in enumerate(image_files):
                image_path = os.path.join(emotion_path, image_file)
                
                # Load image
                image = cv2.imread(image_path)
                if image is None:
                    print(f"[WARNING] Could not load image: {image_path}")
                    continue
                
                # Create variations
                variations = self.apply_augmentations(image, variations_per_image)
                
                # Save original and variations
                for j, variation in enumerate(variations):
                    if j == 0:
                        # Original image
                        filename = f"original_{image_file}"
                        emotion_original += 1
                    else:
                        # Augmented variation
                        name, ext = os.path.splitext(image_file)
                        filename = f"aug_{name}_var{j}{ext}"
                        emotion_augmented += 1
                    
                    save_path = os.path.join(augmented_emotion_path, filename)
                    cv2.imwrite(save_path, variation)
                
                if (i + 1) % 5 == 0:
                    print(f"  Processed {i + 1}/{len(image_files)} images")
            
            total_original += emotion_original
            total_augmented += emotion_augmented
            
            print(f"  ✓ {emotion}: {emotion_original} originals + {emotion_augmented} augmented = {emotion_original + emotion_augmented} total")
        
        print(f"\n[SUMMARY] Dataset augmentation complete!")
        print(f"  Original images: {total_original}")
        print(f"  Augmented images: {total_augmented}")
        print(f"  Total images: {total_original + total_augmented}")
        print(f"  Augmented dataset saved to: {self.augmented_path}")
        
        return total_original, total_augmented

def main():
    # Configuration
    DATASET_PATH = "dashboard/Logic/Machine/dataset"
    VARIATIONS_PER_IMAGE = 15  # Adjust this number based on your needs
    
    # Check if dataset exists
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Dataset path not found: {DATASET_PATH}")
        return
    
    # Initialize augmentor
    augmentor = ImageAugmentor(DATASET_PATH)
    
    # Run augmentation
    original_count, augmented_count = augmentor.augment_dataset(VARIATIONS_PER_IMAGE)
    
    # Calculate new dataset size
    new_total = original_count + augmented_count
    print(f"\n[STATISTICS]")
    print(f"  Original dataset size: {original_count} images")
    print(f"  New augmented dataset size: {new_total} images")
    print(f"  Increase: {((new_total - original_count) / original_count * 100):.1f}%")
    print(f"  Average per emotion: ~{new_total // 3} images")

if __name__ == "__main__":
    main()