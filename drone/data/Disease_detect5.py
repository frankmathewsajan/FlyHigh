import cv2
from ultralytics import YOLO
from pymavlink import mavutil
import folium
import os

# Dictionary to store disease classes, corresponding colors, and medicines
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

def get_gps_coordinates(connection):
    """Get GPS coordinates from Mission Planner"""
    msg = connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    if msg:
        latitude = msg.lat / 1e7  # Convert microdegrees to degrees
        longitude = msg.lon / 1e7
        return latitude, longitude
    return None, None

def add_marker_to_map(map_obj, lat, lon, disease, color):
    """Add a marker to the map"""
    medicine = DISEASE_INFO[disease]["medicine"]
    popup_text = f"Disease: {disease}<br>Medicine: {medicine}"
    folium.Marker(
        location=[lat, lon],
        popup=popup_text,
        icon=folium.Icon(color=color)
    ).add_to(map_obj)

def process_detection(results, frame):
    """Process YOLO detection results"""
    detected = []
    try:
        # Create a copy of the frame for annotations
        annotated_frame = frame.copy()
        
        # Get all detections
        for result in results[0].boxes:
            # Extract class ID and confidence
            class_id = int(result.cls.item())
            confidence = float(result.conf.item())
            
            # Get disease name from model's names dictionary
            disease = results[0].names[class_id]
            
            # Only process detections with confidence > 0.7 (70%)
            if disease in DISEASE_INFO and confidence > 0.7:
                detected.append({
                    "disease": disease,
                    "confidence": confidence
                })
                
                # Draw only high-confidence detections
                box = result.xyxy[0].cpu().numpy()  # Get box coordinates
                x1, y1, x2, y2 = map(int, box[:4])
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"{disease} {confidence:.2f}", 
                           (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
        return detected, annotated_frame
    except Exception as e:
        print(f"Error processing detection: {e}")
        return [], frame

def main():
    # Create a map object
    map_obj = folium.Map(location=[0, 0], zoom_start=2)  # Initial map at (0, 0)

    try:
        # Connect to Mission Planner
        print("Connecting to Mission Planner...")
        connection = mavutil.mavlink_connection('tcp:127.0.0.1:5760')
        connection.wait_heartbeat()
        print("Connected to Mission Planner.")

        # Choose the model
        a = int(input("Which model you want to use? (1 for paddy, 2 for groundnuts): "))
        model_path = "PaddyDet.pt" if a == 1 else "GroundnutDet.pt"

        # Load the YOLO model
        model = YOLO(model_path)
        print(f"Model loaded successfully: {model_path}")
        print("Note: Only showing detections with confidence > 70%")

        # Initialize the webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Could not open webcam")

        print("Starting live detection. Press 'q' to exit.")
        detected_diseases = []

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Perform inference
            results = model(frame, device='cpu')
            
            # Process detections
            new_detections, annotated_frame = process_detection(results, frame)
            
            # Display the frame
            cv2.imshow('Disease Detection (>70% confidence)', annotated_frame)

            # Process each detection
            for detection in new_detections:
                disease = detection["disease"]
                
                # Get GPS coordinates
                lat, lon = get_gps_coordinates(connection)
                if lat is not None and lon is not None:
                    print(f"Detected {disease} at GPS: ({lat}, {lon}) with confidence: {detection['confidence']:.2f}")

                    # Add marker to map
                    color = DISEASE_INFO[disease]["color"]
                    add_marker_to_map(map_obj, lat, lon, disease, color)

                    # Add to detected diseases list
                    detected_diseases.append({
                        "disease": disease,
                        "lat": lat,
                        "lon": lon,
                        "confidence": detection["confidence"]
                    })

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Save the map to an HTML file
        map_path = "detection_map.html"
        map_obj.save(map_path)
        print(f"\nMap saved as {map_path}. Open this file to view detections.")

        # Print medicines for detected diseases
        if detected_diseases:
            print("\nDetected Diseases and Recommended Medicines (>70% confidence):")
            for detection in detected_diseases:
                disease = detection["disease"]
                lat = detection["lat"]
                lon = detection["lon"]
                confidence = detection["confidence"]
                medicine = DISEASE_INFO[disease]["medicine"]
                print(f"\nDisease: {disease}")
                print(f"Location: ({lat}, {lon})")
                print(f"Confidence: {confidence:.2f}")
                print(f"Recommended Medicine: {medicine}")
        else:
            print("\nNo detections with confidence > 70% were found.")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Release resources
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
