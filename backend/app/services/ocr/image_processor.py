import cv2
import numpy as np

class ImageProcessor:
    """
    Handles OpenCV preprocessing to optimize images (medicine strips/boxes)
    for Tesseract OCR extraction with high robustness against noise and skew.
    """

    @staticmethod
    def _apply_clahe(gray_img: np.ndarray) -> np.ndarray:
        """
        Applies Contrast Limited Adaptive Histogram Equalization.
        Locally enhances contrast in poorly lit patches commonly found 
        on reflective pill boxes without heavily amplifying background noise.
        """
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray_img)

    @staticmethod
    def _auto_rotate(image: np.ndarray) -> np.ndarray:
        """
        Detects primary text skew angle using contours and applies an affine 
        transformation to correct the rotation to a horizontal baseline.
        """
        # Create a working copy for finding contours
        working_img = cv2.bitwise_not(image.copy())
        
        # Dilate to connect text components into solid blocks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        dilated = cv2.dilate(working_img, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return image

        # Find the largest contour which we assume represents the main text block
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Calculate minimum bounding rectangle and its angle
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[-1]
        
        # Standardize the angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        # Ignore negligible skew
        if abs(angle) < 1.0:
            return image
            
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        
        # Calculate rotation matrix and apply affine transformation
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        # Use cv2.BORDER_REPLICATE to avoid introducing black/white stark borders
        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated

    @staticmethod
    def _extract_text_region(image: np.ndarray) -> np.ndarray:
        """
        Filters contours by aspect ratio isolating the text block 
        and cropping out surrounding background noise.
        """
        working_img = cv2.bitwise_not(image.copy())
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5))
        dilated = cv2.dilate(working_img, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return image
            
        # Find the contour with the largest area that matches a text-like aspect ratio (W > H)
        best_contour = None
        max_area = 0
        
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            aspect_ratio = w / float(h)
            
            # Text lines generally have an aspect ratio > 2
            if aspect_ratio > 1.5 and area > max_area:
                max_area = area
                best_contour = c
                
        if best_contour is None:
            return image
            
        x, y, w, h = cv2.boundingRect(best_contour)
        
        # Add a 5% margin to avoid clipping character edges
        margin_x = int(w * 0.05)
        margin_y = int(h * 0.05)
        
        img_h, img_w = image.shape[:2]
        
        y1 = max(0, y - margin_y)
        y2 = min(img_h, y + h + margin_y)
        x1 = max(0, x - margin_x)
        x2 = min(img_w, x + w + margin_x)
        
        return image[y1:y2, x1:x2]

    @staticmethod
    def preprocess_for_ocr(image_bytes: bytes) -> np.ndarray:
        """
        Executes a deterministic pipeline of OpenCV operations optimized
        for printed drug packaging text.
        
        Args:
            image_bytes: Raw bytes from the uploaded image.
            
        Returns:
            np.ndarray: A preprocessed, binarized 8-bit single channel image.
        """
        # 1. Image Validation and Loading
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image file or format.")

        # 2. Resize Normalization
        img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

        # 3. Grayscale Conversion
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 4. Contrast Enhancement (CLAHE)
        # Prevents washout from camera flash on glossy medicine boxes
        enhanced_gray = ImageProcessor._apply_clahe(gray)

        # 5. Gaussian Blur
        blurred = cv2.GaussianBlur(enhanced_gray, (5, 5), 0)

        # 6. Adaptive Thresholding
        binary = cv2.adaptiveThreshold(
            blurred, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 
            11, 
            2
        )

        # 7. Morphological Operations (Noise Removal)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        processed_img = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        # 8. Auto-Rotation Correction
        # Needs to happen on the binarized image for contour detection
        rotated_img = ImageProcessor._auto_rotate(processed_img)
        
        # 9. Text Region Cropping
        # Crops away non-text structural noise like box edges
        cropped_img = ImageProcessor._extract_text_region(rotated_img)

        # 10. Invert the image back: Tesseract expects black text on white background
        final_img = cv2.bitwise_not(cropped_img)

        return final_img
