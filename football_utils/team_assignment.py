import cv2
import numpy as np
from sklearn.cluster import KMeans

def extract_team_colors(frame, detections):
    """
    Extract dominant colors from player bounding boxes.
    detections: list of detection dictionaries from YOLO.
    Returns a list of color features.
    """
    colors = []
    for det in detections:
        # Only consider players (assume class 'person')
        if det['name'] == 'person':
            xmin, ymin, xmax, ymax = int(det['xmin']), int(det['ymin']), int(det['xmax']), int(det['ymax'])
            player_roi = frame[ymin:ymax, xmin:xmax]
            # Resize to speed up computation and reshape for clustering.
            roi_small = cv2.resize(player_roi, (50, 50))
            roi_reshaped = roi_small.reshape(-1, 3)
            colors.append(roi_reshaped)
    return colors

def assign_teams(frame, detections, n_clusters=2):
    """
    Use KMeans clustering on extracted colors to assign players to teams.
    Returns a dictionary mapping detection id to team label.
    """
    colors = extract_team_colors(frame, detections)
    if len(colors) == 0:
        return {}
    # Combine all color pixels from all players.
    all_colors = np.vstack(colors)
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(all_colors)
    # For demonstration, we assign teams randomly to each detection.
    team_assignments = {}
    for i, det in enumerate(detections):
        if det['name'] == 'person':
            # In practice, you would compute the dominant color in the ROI and then predict its team.
            team_assignments[i] = kmeans.labels_[i % len(kmeans.labels_)]
    return team_assignments
