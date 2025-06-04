import json
from typing import List, Tuple

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.python import Image
from mediapipe.tasks.python.components.containers.landmark import (
    Landmark, NormalizedLandmark)
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import (FaceLandmarker,
                                           FaceLandmarkerOptions, RunningMode)

from analysis.configs import MEDIAPIPE
from analysis.data.datatypes import BoundingBox, Keypoint
from sample_extraction.utils import (associate_bboxes_to_annotations,
                                     display_annotated_image,
                                     get_average_keypoint, get_bbox_from_kps,
                                     get_data_path, load_fairset_annotations)

KEYPOINT_MAPPING = {
    0: [285, 336],
    1: [293, 334, 282, 283],
    2: [276, 300],
    3: [55, 107],
    4: [63, 105, 53, 52],
    5: [46, 70],
    6: [362],
    7: [263],
    8: [385, 387],
    9: [380, 373],
    10: [133],
    11: [33],
    12: [158, 160],
    13: [144, 153],
    14: [454],
    15: [288],
    16: [234],
    17: [58],
    18: [152],
    19: [168],
    20: [4],
    21: [306],
    22: [269],
    23: [405],
    24: [0],
    25: [13],
    26: [14],
    27: [17],
    28: [76],
    29: [39],
    30: [181],
    31: [],
    32: [],
    33: [],
}


def mediapipe_results_to_2d_keypoints(
    mp_landmarks: List[NormalizedLandmark], max_width: int, max_height: int
) -> List[Keypoint]:
    keypoints: List[Keypoint] = []
    for i, landmark in enumerate(mp_landmarks):
        keypoints.append(Keypoint(id=i, x=int(max_width * landmark.x), y=int(max_height * landmark.y)))
    return keypoints


def estimate(frame: np.ndarray, landmarker):
    mp_image = Image(image_format=mp.ImageFormat.SRGB, data=frame)
    mp_result = landmarker.detect(mp_image)
    results: List[Tuple[BoundingBox, List[Keypoint]]] = []

    for mp_kps in mp_result.face_landmarks:
        kps = mediapipe_results_to_2d_keypoints(mp_kps, frame.shape[1], frame.shape[0])
        bbox = get_bbox_from_kps(kps, frame.shape[1], frame.shape[0])
        results.append((bbox, kps))
    return results


if __name__ == "__main__":
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MEDIAPIPE["model_path"]),
        running_mode=RunningMode.IMAGE, num_faces=10)
    landmarker = FaceLandmarker.create_from_options(options)

    images = get_data_path(MEDIAPIPE["images_folder"])
    annotations = load_fairset_annotations()

    results = {}

    for i in range(len(images)):
        if images[i].split("/")[-1] not in annotations:
            continue

        print(i, images[i])
        im = cv2.imread(images[i])
        cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

        results[images[i].split("/")[-1]] = {}

        estimations = estimate(im, landmarker)
        if not len(estimations):
            print(f"No estimations were found for image {images[i]}")
            continue
        images_annotations: dict = annotations[images[i].split("/")[-1]]

        association_indices, ious = associate_bboxes_to_annotations(
            [bbox for bbox, _ in estimations], [annotation["bbox"] for annotation in images_annotations.values()]
        )
        for row, col in association_indices:
            kps = []
            for custom_idx, mp_indices in KEYPOINT_MAPPING.items():
                if len(mp_indices):
                    kps.append(
                        get_average_keypoint([kp for kp in estimations[row][1] if kp.id in mp_indices], custom_idx)
                    )

            association_accepted = ious[row][col] > MEDIAPIPE.get("min_iou", 0.4)
            if not association_accepted:
                display_image = list(images_annotations.values())[col]["bbox"].annotate_image(np.array(im), (0, 255, 0))
                key = display_annotated_image(display_image, kps, estimations[row][0])
                if key == ord("a"):
                    association_accepted = True

            if association_accepted:
                results[images[i].split("/")[-1]][list(images_annotations.keys())[col]] = {
                    kp.id: {"x": kp.x, "y": kp.y} for kp in kps
                }
            else:
                print(
                    f"Association for image {images[i]} and annotation {list(images_annotations.keys())[col]} was rejected."
                )

    with open(MEDIAPIPE["output_file"], "w") as file:
        json.dump(results, file, indent=4)
