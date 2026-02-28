import cv2
import numpy as np

# Create an empty black image
img = np.zeros((100, 300, 3), dtype=np.uint8)

# Add some text simulating a medicine box
cv2.putText(
    img, 
    "WARFARN 5MG", # Intentional typo to test fuzzy matching 
    (10, 60), 
    cv2.FONT_HERSHEY_SIMPLEX, 
    1.5, 
    (255, 255, 255), 
    3
)

# Simulate low-light noise
noise = np.random.randint(0, 50, (100, 300, 3), dtype=np.uint8)
noisy_img = cv2.add(img, noise)

# Save the test image
cv2.imwrite("backend/test_medicine.png", noisy_img)
print("Created dummy medicine image 'backend/test_medicine.png'")
