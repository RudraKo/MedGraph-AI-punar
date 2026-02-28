import cv2
import numpy as np

# Create an empty black image 
img = np.zeros((150, 400, 3), dtype=np.uint8)

# Add some text simulating a medicine box
cv2.putText(
    img, 
    "AM0XIC1LL1N 500", # Severe typo
    (30, 80), 
    cv2.FONT_HERSHEY_SIMPLEX, 
    1.5, 
    (150, 150, 150), # Low contrast grey
    2
)

(h, w) = img.shape[:2]
center = (w // 2, h // 2)

# Rotate by 15 degrees to simulate bad camera angle
M = cv2.getRotationMatrix2D(center, -15, 1.0)
rotated = cv2.warpAffine(img, M, (w, h), borderValue=(0, 0, 0))

# Simulate heavy low-light noise
noise = np.random.randint(0, 80, (150, 400, 3), dtype=np.uint8)
noisy_img = cv2.add(rotated, noise)

# Add a fake contour box to simulate edge of pill packet
cv2.rectangle(noisy_img, (10, 10), (390, 140), (200, 200, 200), 2)

cv2.imwrite("backend/test_rotated.png", noisy_img)
print("Created 'backend/test_rotated.png'")
