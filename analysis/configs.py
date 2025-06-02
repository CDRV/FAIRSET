
DATA = {
    "exclude_images_file": "IGS2025_missing_images.txt",
    "annotations_file": "annotations_IGS2025.json",
    "estimations_file": "mediapipe_estimations.json",
}

FILTERS = {
    "min_iod": 50,  # Set -1 to disable filtering by inter-ocular distance,
    "max_nme": 1,  # Set -1 to disable filtering by NME,
    "remove_statistical_bias": True
}

# Configurations for MediaPipe extraction sample code
MEDIAPIPE = {
    "images_folder": "/home/joli1801/Annotations/mturk_analysis/analysis/assets",  # "assets/FAIRSET",
    "model_path": "face_landmarker.task",
    "min_iou": 0.4,  # Minimum IoU for association,
    "output_file": "MediaPipe.json",
}
