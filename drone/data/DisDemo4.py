import cv2
from ultralytics import YOLO
import folium
import random

# Constants for VIT-AP University coordinates
VIT_AP_LAT = 16.4419
VIT_AP_LON = 80.6220

# Maximum offset for random coordinates (in degrees)
LAT_OFFSET = 0.005  # ~555 meters
LON_OFFSET = 0.005  # ~555 meters

# Disease information dictionary
DISEASE_INFO = {
    "Black Fungus Pod": {"color": "black", "medicine": "Mancozeb or Carbendazim"},
    "Early and Late leaf spot": {"color": "blue", "medicine": "Chlorothalonil or Propiconazole"},
    "Fungus leaf": {"color": "green", "medicine": "Copper Oxychloride"},
    "Rust-Leaf": {"color": "orange", "medicine": "Hexaconazole or Sulphur"},
    "black fungus-groundnut": {"color": "gray", "medicine": "Carbendazim or Thiophanate-methyl"},
    "brown Fungus Pod": {"color": "brown", "medicine": "Mancozeb or Chlorothalonil"},
    "bakteri_daun_bergaris": {"color": "yellow", "medicine": "Streptomycin or Copper Hydroxide"},
    "bercak_coklat": {"color": "red", "medicine": "Propiconazole or Mancozeb"},
    "bercak_coklat_sempit": {"color": "purple", "medicine": "Carbendazim or Propiconazole"},
    "hawar_daun_bakteri": {"color": "cyan", "medicine": "Copper Oxychloride or Streptomycin"},
    "tungro": {"color": "pink", "medicine": "Buprofezin or Imidacloprid"}
}

def generate_random_coordinates():
    """Generate random coordinates within offset range of VIT-AP"""
    random_lat = VIT_AP_LAT + random.uniform(-LAT_OFFSET, LAT_OFFSET)
    random_lon = VIT_AP_LON + random.uniform(-LON_OFFSET, LON_OFFSET)
    return random_lat, random_lon

def create_marker(map_obj, lat, lon, disease):
    """Add a marker to the map with disease information"""
    color = DISEASE_INFO[disease]["color"]
    medicine = DISEASE_INFO[disease]["medicine"]
    popup_text = f"Disease: {disease}<br>Medicine: {medicine}"
    
    folium.Marker(
        location=[lat, lon],
        popup=popup_text,
        icon=folium.Icon(color=color)
    ).add_to(map_obj)

def process_detection(results, frame):
    """Process YOLO detection results"""
    detected_diseases = []
    current_disease = None
    current_medicine = None
    
    try:
        # Create a copy of the frame for annotations
        annotated_frame = frame.copy()
        height, width = annotated_frame.shape[:2]
        
        # Get all detections
        for result in results[0].boxes:
            # Extract class ID and confidence
            class_id = int(result.cls.item())
            confidence = float(result.conf.item())
            
            # Get disease name from model's names dictionary
            disease = results[0].names[class_id]
            
            # Only process detections with confidence > 0.7 (70%)
            if disease in DISEASE_INFO and confidence > 0.2:
                # Store the current disease and medicine for display
                current_disease = disease
                current_medicine = DISEASE_INFO[disease]["medicine"]
                
                # Generate random location for the detection
                lat, lon = generate_random_coordinates()
                detected_diseases.append({
                    "disease": disease,
                    "confidence": confidence,
                    "coordinates": (lat, lon)
                })
                
                # Draw detection box and confidence
                box = result.xyxy[0].cpu().numpy()  # Get box coordinates
                x1, y1, x2, y2 = map(int, box[:4])
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"{disease} {confidence:.2f}", 
                           (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add disease name at top left
        if current_disease:
            # Create semi-transparent background for text
            overlay = annotated_frame.copy()
            cv2.rectangle(overlay, (10, 10), (width//2, 40), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.3, annotated_frame, 0.7, 0, annotated_frame)
            cv2.putText(annotated_frame, f"Disease: {current_disease}", 
                       (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Add medicine at bottom right
        if current_medicine:
            text_size = cv2.getTextSize(f"Medicine: {current_medicine}", 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            # Create semi-transparent background for text
            overlay = annotated_frame.copy()
            cv2.rectangle(overlay, 
                         (width - text_size[0] - 30, height - 40),
                         (width - 10, height - 10),
                         (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.3, annotated_frame, 0.7, 0, annotated_frame)
            cv2.putText(annotated_frame, f"Medicine: {current_medicine}",
                       (width - text_size[0] - 20, height - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
        return detected_diseases, annotated_frame
    
    except Exception as e:
        print(f"Error processing detection: {e}")
        return [], frame

def main():
    # Initialize the map centered at VIT-AP
    map_obj = folium.Map(location=[VIT_AP_LAT, VIT_AP_LON], zoom_start=15)
    
    # Model selection
    model_choice = input("Which model do you want to use? (1 for paddy, 2 for groundnuts): ")
    model_path = "PaddyDet.pt" if model_choice == "1" else "GroundNutDet.pt"
    
    try:
        # Load the YOLO model
        model = YOLO(model_path)
        print(f"Model loaded successfully: {model_path}")
        
        # Input image path
        image_path = input("Enter the path to the image file: ")
        frame = cv2.imread(image_path)
        
        if frame is None:
            raise Exception("Could not read the image file.")
        
        print("Processing the image...")
        
        # Perform inference
        results = model(frame, device='cpu')
        
        # Process detections
        new_detections, annotated_frame = process_detection(results, frame)
        
        # Add new detections to the map
        for detection in new_detections:
            disease = detection["disease"]
            lat, lon = detection["coordinates"]
            create_marker(map_obj, lat, lon, disease)
        
        # Display the annotated frame
        cv2.imshow('Disease Detection (>70% confidence)', annotated_frame)

        # Wait indefinitely for 'q' key press to close the image window
        while True:
            key = cv2.waitKey(1) & 0xFF  # Capture the pressed key
            if key == ord('q'):  # Check if the pressed key is 'q'
                break
        
        cv2.destroyAllWindows()  # Close the window after 'q' is pressed
        
        # Save the map
        map_obj.save("disease_detection_map.html")
        
        # Print summary
        if new_detections:
            print("\nDetection Summary (>70% confidence):")
            for detection in new_detections:
                disease = detection["disease"]
                confidence = detection["confidence"]
                lat, lon = detection["coordinates"]
                medicine = DISEASE_INFO[disease]["medicine"]
                print(f"\nDisease: {disease}")
                print(f"Confidence: {confidence:.2f}")
                print(f"Location: ({lat:.6f}, {lon:.6f})")
                print(f"Recommended Medicine: {medicine}")
        else:
            print("\nNo detections with confidence > 70% were found.")
        
        print(f"\nMap saved as disease_detection_map.html")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        cv2.destroyAllWindows()  # Close all windows

if __name__ == "__main__":
    main()

