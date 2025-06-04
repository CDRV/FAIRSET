import json
from typing import Any, Dict, List, Optional

import numpy as np

from analysis.configs import DATA, FILTERS
from analysis.data.datatypes import Age, Image, Keypoint, Person, Sex, Skintone
from analysis.data.locations import KEYPOINTS


class DataLoader:
    def __init__(self):
        self._removed_images = []
        if DATA.get("exclude_images_file") is not None:
            self._removed_images = list(np.loadtxt(DATA["exclude_images_file"], dtype=str))

        if DATA.get("annotations_file") is None:
            raise Exception("Annotations file is not specified in the DATA config. Please check the configuration.")
        self._annotations: List[Image] = []
        self._load_annotations()

        if DATA.get("estimations_file") is None:
            raise Exception("Estimation file is not specified in the DATA config. Please check the configuration.")
        self._estimations: Dict[str, Dict[int, Dict[int, Keypoint]]] = {}
        self._load_estimations()

        self._location_errors: Dict[int, list | np.ndarray] = {kp: [] for kp in KEYPOINTS.keys()}
        self._extract_location_errors()
        self._statistical_biases: Dict[int, tuple] = {
            kp_id: (np.median(errors[:, 0]), np.median(errors[:, 1]))
            for kp_id, errors in self._location_errors.items()
            if len(errors) > 0
        }

        self._error_indexes: Dict[str, Dict[Any, list | np.ndarray]] = {
            "location": {kp: [] for kp in KEYPOINTS.keys()},
            "age": {kp: {age: [] for age in Age if age != Age.NotAvailable} for kp in KEYPOINTS.keys()},
            "sex": {kp: {sex: [] for sex in Sex if sex != Sex.NotAvailable} for kp in KEYPOINTS.keys()},
            "skintone": {
                kp: {skintone: [] for skintone in Skintone if skintone != Skintone.NotAvailable}
                for kp in KEYPOINTS.keys()
            },
            "expressions": {kp: {True: [], False: []} for kp in KEYPOINTS.keys()},
            "lighting": {kp: {True: [], False: []} for kp in KEYPOINTS.keys()},
            "occlusion": {kp: {True: [], False: []} for kp in KEYPOINTS.keys()},
        }
        self._error_indexes["age"]["all"] = {age: [] for age in Age if age != Age.NotAvailable}
        self._error_indexes["skintone"]["all"] = {
            skintone: [] for skintone in Skintone if skintone != Skintone.NotAvailable
        }
        self._error_indexes["sex"]["all"] = {sex: [] for sex in Sex if sex != Sex.NotAvailable}
        self._error_indexes["occlusion"]["all"] = {True: [], False: []}
        self._error_indexes["lighting"]["all"] = {True: [], False: []}
        self._error_indexes["expressions"]["all"] = {True: [], False: []}
        self._preprocess_errors()

    def _load_annotations(self):
        with open(DATA["annotations_file"], "r") as file:
            annotations_dict = json.load(file)
        for image_name, metadata in annotations_dict.items():
            if image_name not in self._removed_images:
                persons = []
                person_data: dict
                for person_id, person_data in metadata["persons"].items():
                    keypoints = [
                        Keypoint(kp_data["x"], kp_data["y"], int(kp_id))
                        for kp_id, kp_data in person_data["keypoints"].items()
                    ]
                    persons.append(
                        Person(
                            int(person_id),
                            keypoints,
                            Skintone.from_label(person_data["skintone"]),
                            Age.from_label(person_data["age"]),
                            Sex.from_label(person_data["sex"]),
                            person_data.get("occlusion"),
                            person_data.get("lighting"),
                            person_data.get("expression"),
                        )
                    )
                self._annotations.append(Image(image_name, persons, metadata["width"], metadata["height"]))

    def _load_estimations(self):
        with open(DATA["estimations_file"], "r") as file:
            estimations_dict = json.load(file)
            for image_name, metadata in estimations_dict.items():
                if image_name not in self._removed_images:
                    self._estimations[image_name] = {}
                    for person_id, keypoints in metadata.items():
                        self._estimations[image_name][int(person_id)] = {
                            int(kp_id): Keypoint(kp_data["x"], kp_data["y"], int(kp_id))
                            for kp_id, kp_data in keypoints.items()
                        }

    def _preprocess_errors(self):
        for image in self._annotations:
            if image.name in self._estimations:
                for person in image.persons:
                    if (
                        person.id in self._estimations.get(image.name, {})
                        and person.iod
                        and person.iod > FILTERS.get("min_iod", -1)
                    ):
                        estimations = self._estimations.get(image.name, {})[person.id]
                        for keypoint in person.keypoints:
                            if keypoint.id in estimations:
                                if FILTERS.get("remove_statistical_bias", True):
                                    estimation = estimations[keypoint.id]
                                    dx = (estimation.x - keypoint.x) / person.iod
                                    dy = (estimation.y - keypoint.y) / person.iod
                                    nme = np.sqrt(
                                        (dx - self._statistical_biases[keypoint.id][0]) ** 2
                                        + (dy - self._statistical_biases[keypoint.id][1]) ** 2
                                    )
                                else:
                                    nme = keypoint.distance(estimations[keypoint.id]) / person.iod
                                if nme < FILTERS.get("max_nme", -1) or FILTERS.get("max_nme", -1) == -1:
                                    self._error_indexes["location"][keypoint.id].append(nme)
                                    if person.age != Age.NotAvailable:
                                        self._error_indexes["age"][keypoint.id][person.age].append(nme)
                                        self._error_indexes["age"]["all"][person.age].append(nme)
                                    if person.skintone != Skintone.NotAvailable:
                                        self._error_indexes["skintone"][keypoint.id][person.skintone].append(nme)
                                        self._error_indexes["skintone"]["all"][person.skintone].append(nme)
                                    if person.sex != Sex.NotAvailable:
                                        self._error_indexes["sex"][keypoint.id][person.sex].append(nme)
                                        self._error_indexes["sex"]["all"][person.sex].append(nme)
                                    if person.occlusion is not None:
                                        self._error_indexes["occlusion"][keypoint.id][person.occlusion].append(nme)
                                        self._error_indexes["occlusion"]["all"][person.occlusion].append(nme)
                                    if person.lighting is not None:
                                        self._error_indexes["lighting"][keypoint.id][person.lighting].append(nme)
                                        self._error_indexes["lighting"]["all"][person.lighting].append(nme)
                                    if person.expression is not None:
                                        self._error_indexes["expressions"][keypoint.id][person.expression].append(nme)
                                        self._error_indexes["expressions"]["all"][person.expression].append(nme)

        for factor, data in self._error_indexes.items():
            for keypoint_id, kp_data in data.items():
                if factor == "location":
                    data[keypoint_id] = np.array(kp_data)
                else:
                    for group, nmes in kp_data.items():
                        data[keypoint_id][group] = np.array(nmes)

    def _extract_location_errors(self) -> Dict[str, Dict[Any, float]]:
        for image in self._annotations:
            if image.name not in self._estimations:
                print(f"Image {image.name} not found in estimations.")
                continue
            for person in image.persons:
                if person.id not in self._estimations.get(image.name, {}):
                    print(f"Person {person.id} not found in estimations for image {image.name}.")
                    continue

                if person.iod is None or person.iod < FILTERS.get("min_iod", -1):
                    print(
                        f"Person {person.id} was removed from the analysis because of a small or missing iod in image {image.name}."
                    )
                    continue
                estimations = self._estimations.get(image.name, {}).get(person.id, {})

                for keypoint in person.keypoints:
                    if keypoint.id in estimations:
                        estimation = estimations[keypoint.id]
                        dx = (estimation.x - keypoint.x) / person.iod
                        dy = (estimation.y - keypoint.y) / person.iod
                        self._location_errors[keypoint.id].append((dx, dy))

        for kp_id, nmes in self._location_errors.items():
            self._location_errors[kp_id] = np.array(nmes)

    def get_errors_by_factor(self, factor: str, kp_id: Optional[int] = None) -> np.ndarray:
        if kp_id is not None:
            return np.array(
                [
                    error
                    for kp_data in self._error_indexes[factor].values()
                    for kp_errors in kp_data.values()
                    for error in kp_errors
                    if len(kp_errors) > 0
                ]
            )
        return np.array(
            [
                error
                for kp_id, kp_errors in self._error_indexes[factor].items()
                for error in kp_errors
                if len(kp_errors) > 0 and kp_id != "all"
            ]
        )

    def get_errors_by_group(self, factor: str, group: Any, kp_id: Optional[int] = None) -> np.ndarray:
        if kp_id is not None:
            return self._error_indexes[factor][kp_id][group]
        return np.array(
            [
                nme
                for kp_errors, kp_id in self._error_indexes[factor].items()
                if group in kp_errors
                for nme in kp_errors[group]
                if kp_id != "all"
            ]
        )

    def get_all_group_errors(self, factor: str) -> Dict[str, np.ndarray]:
        return self._error_indexes[factor]["all"]

    def get_group_error_by_keypoint_dict(self, factor: str, group: str):
        return {kp_id: self._error_indexes[factor][kp_id][group] for kp_id in self._error_indexes[factor].keys()}

    def get_errors_by_location(self, keypoint_id: int) -> np.ndarray:
        return self._error_indexes["location"][keypoint_id]

    def get_keypoint_ids(self) -> List[int]:
        return list(k for k, v in self._error_indexes["location"].items() if len(v) > 0)

    def get_all_errors(self) -> Dict[str, Dict[int, np.ndarray]]:
        return [error for errors in self._error_indexes["location"].values() for error in errors if len(errors) > 0]
