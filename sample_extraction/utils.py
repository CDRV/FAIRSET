import json
import os
from typing import List, Optional

import cv2
import numpy as np
from munkres import Munkres

from analysis.configs import DATA
from analysis.data.datatypes import BoundingBox, Keypoint


def display_annotated_image(image: np.ndarray, kps: List[Keypoint], bbox: Optional[BoundingBox] = None):
    if bbox is not None:
        image = bbox.annotate_image(image)  # Green box
    for kp in kps:
        image = kp.annotate_image(image)

    cv2.imshow("Annotated image", image)
    key = cv2.waitKey(0)
    cv2.destroyAllWindows()
    return key


def get_data_path(root):
    return [os.path.join(root, i) for i in sorted(os.listdir(root)) if i.endswith("png") or i.endswith("jpg")]


def get_bbox_from_kps(kps: List[Keypoint], max_width: int, max_height: int):
    kps_xs = [kp.x for kp in kps if kp.x > 0 and kp.x < max_width]
    kps_ys = [kp.y for kp in kps if kp.y > 0 and kp.y < max_height]
    return BoundingBox.from_pt1_pt2_format(min(kps_xs), min(kps_ys), max(kps_xs), max(kps_ys))


def get_average_keypoint(kps: List[Keypoint], new_idx: int = -1) -> Keypoint:
    return Keypoint(int(sum(kp.x for kp in kps) / len(kps)), int(sum(kp.y for kp in kps) / len(kps)), new_idx)


def associate_bboxes_to_annotations(bboxes: List[BoundingBox], annotation_bboxes: List[BoundingBox]) -> List[int]:
    cost_matrix = []
    rel_distances = []
    for estimated_bbox in bboxes:
        row = []
        d_row = []
        for annotation_bbox in annotation_bboxes:
            iou = estimated_bbox.calculate_iou(annotation_bbox)
            row.append(1 - iou)
        cost_matrix.append(row)
        rel_distances.append(d_row)

    if len(cost_matrix) > 0:
        m = Munkres()
        indices = m.compute(cost_matrix)
        return indices, [[1 - cost for cost in row] for row in cost_matrix]


def load_fairset_annotations():
    with open(DATA["annotations_file"], "r") as file:
        annotations_dict = json.load(file)
    fairset_annotations = {}
    for image_name, metadata in annotations_dict.items():
        fairset_annotations[image_name] = {
            int(person_id): {"bbox": None, "keypoints": []} for person_id in metadata["persons"].keys()
        }
        for person_id, person_data in metadata["persons"].items():
            fairset_annotations[image_name][int(person_id)]["keypoints"] = [
                Keypoint(kp_data["x"], kp_data["y"], kp_id) for kp_id, kp_data in person_data["keypoints"].items()
            ]
            bbox_dict = person_data["bbox"]
            fairset_annotations[image_name][int(person_id)]["bbox"] = BoundingBox(bbox_dict["x"], bbox_dict["y"],
                                                                                  bbox_dict["w"], bbox_dict["h"])
    return fairset_annotations
