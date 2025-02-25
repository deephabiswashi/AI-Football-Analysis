import cv2
import os
import time
import numpy as np
from football_utils.detection import detect_objects
from football_utils.tracking import calculate_optical_flow, apply_perspective_transform
from football_utils.team_assignment import assign_teams
from football_utils.llm_inference import classify_output


def process_video(input_video_path, output_folder):
    cap = cv2.VideoCapture(input_video_path)
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    output_video_path = os.path.join(output_folder, f"output_{int(time.time())}.mp4")
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        out.release()
        return None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Object Detection
        detections = detect_objects(frame)
        
        # 2. Team Assignment (using KMeans on color features)
        team_assignments = assign_teams(frame, detections)
        
        # 3. Optical Flow (if needed for camera movement)
        flow = calculate_optical_flow(prev_frame, frame)
        
        # 4. Perspective Transformation (example: identity transform here)
        # In practice, define src_points and dst_points based on your camera calibration.
        src_points =  np.float32([[0,0], [width,0], [width,height], [0,height]])
        dst_points = np.float32([[0,0], [width,0], [width,height], [0,height]])
        transformed_frame = apply_perspective_transform(frame, src_points, dst_points)
        
        # 5. Overlay detections and team assignments on frame.
        for i, det in enumerate(detections):
            xmin, ymin, xmax, ymax = int(det['xmin']), int(det['ymin']), int(det['xmax']), int(det['ymax'])
            label = det['name']
            # Add team information if available.
            if label == "person" and i in team_assignments:
                label += f" | Team {team_assignments[i]}"
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Write the processed frame to the output video.
        out.write(frame)
        prev_frame = frame.copy()
    
    cap.release()
    out.release()
    
    # 6. After processing video, you can generate a summary and run LLM classification.
    summary_text = "Analysis complete. Player detection, team assignment, and movement tracking executed."
    classification = classify_output(summary_text)
    # If classification is something like [{'label': 'POSITIVE', 'score': 0.9998}], parse it:
    if classification and isinstance(classification, list):
        label = classification[0].get('label', 'N/A')
        score = classification[0].get('score', 0.0)
        classification_str = f"Label: {label}, Score: {score:.4f}"
    else:
        classification_str = str(classification)  # fallback
    print("LLM Classification:", classification)
    
    return output_video_path,classification_str
