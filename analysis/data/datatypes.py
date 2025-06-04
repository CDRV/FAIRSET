import json
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

from analysis.data.locations import KEYPOINTS


class DiscreteFactorEnum(Enum):
    @classmethod
    def from_label(cls, label: str):
        pass

    # TODO why not use a property here?
    @classmethod
    def get_property_str(cls) -> str:
        pass

    @property
    def color(self) -> Tuple[float, float, float]:
        pass

    @property
    def figure_label(self) -> str:
        pass


class Sex(DiscreteFactorEnum):
    Male = auto()
    Female = auto()
    NotAvailable = auto()

    @classmethod
    def from_label(cls, label: str):
        try:
            if label.lower() == "male":
                return cls.Male
            elif label.lower() == "female":
                return cls.Female
            return cls.NotAvailable
        except Exception as e:
            return cls.NotAvailable

    @classmethod
    def get_property_str(cls) -> str:
        return "sex"

    @property
    def color(self):
        colors = {
            Sex.Male: (0.3, 0.5, 0.7),
            Sex.Female: (0.7, 0.4, 0.3),
            Sex.NotAvailable: (0.5, 0.5, 0.5)
        }
        return colors[self]

    @property
    def property_str(self) -> str:
        return "sex"

    @property
    def figure_label(self) -> str:
        labels = {
            Sex.Male: "Male",
            Sex.Female: "Female",
        }
        return labels[self]


class Age(DiscreteFactorEnum):
    Senior = auto()
    Adult = auto()
    YoungAdult = auto()
    Child = auto()
    NotAvailable = auto()

    @classmethod
    def from_label(cls, label: str):
        if label in ["senior", "Senior"]:
            return cls.Senior
        elif label in ["middle_aged", "Middleage", "Adult"]:
            return cls.Adult
        elif label in ["young", "YoungAdult"]:
            return cls.YoungAdult
        elif label == "Child":
            return cls.Child
        return cls.NotAvailable

    @classmethod
    def get_property_str(cls) -> str:
        return "age"

    @property
    def color(self):
        colors = {
            Age.Senior: (0.7, 0.4, 0.3),
            Age.Adult: (0.3, 0.6, 0.4),
            Age.YoungAdult: (0.3, 0.5, 0.7),
            Age.Child: (0.9, 0.7, 0.5),
            Age.NotAvailable: (0.6, 0.6, 0.6),
        }
        return colors[self]

    @property
    def reference_image(self) -> str:
        image_names = {
            Age.Senior: "0d248d3d-e10c-4441-8346-5a5fe5a390b9.png",
            Age.Adult: "fda54d27-0704-43a1-a4d3-a08fdb0f1ed3.png",
            Age.YoungAdult: "19e76b7b-6849-4f30-b64c-6f2f85a5e724.png",
            Age.Child: "3468207f-fbec-4aa2-b36d-7018d08a38be.png",
        }
        return image_names[self]

    @property
    def figure_label(self) -> str:
        labels = {
            Age.Senior: "Seniors",
            Age.Adult: "Adults",
            Age.YoungAdult: "Young adults",
            Age.Child: "Children",
        }
        return labels[self]


class Skintone(DiscreteFactorEnum):
    Type1 = 1
    Type2 = 2
    Type3 = 3
    Type4 = 4
    Type5 = 5
    Type6 = 6
    NotAvailable = 0

    @classmethod
    def from_label(cls, label: str):
        label_map = {
            "1": cls.Type1,
            "2": cls.Type2,
            "3": cls.Type3,
            "4": cls.Type4,
            "5": cls.Type5,
            "6": cls.Type6
        }
        return label_map.get(label, cls.NotAvailable)

    @classmethod
    def get_property_str(cls) -> str:
        return "skintone"

    @property
    def color(self):
        colors = {
            Skintone.Type1: (1.0, 0.894, 0.831),
            Skintone.Type2: (0.957, 0.8, 0.682),
            Skintone.Type3: (0.831, 0.643, 0.514),
            Skintone.Type4: (0.678, 0.514, 0.4),
            Skintone.Type5: (0.514, 0.353, 0.251),
            Skintone.Type6: (0.322, 0.224, 0.176),
        }
        return colors[self]

    @property
    def figure_label(self) -> str:
        labels = {
            Skintone.Type1: "Type 1",
            Skintone.Type2: "Type 2",
            Skintone.Type3: "Type 3",
            Skintone.Type4: "Type 4",
            Skintone.Type5: "Type 5",
            Skintone.Type6: "Type 6",
        }
        return labels[self]


@dataclass
class Keypoint:
    x: int
    y: int
    id: int

    def annotate_image(
        self,
        image: np.ndarray,
        kp_color: Tuple[int, int, int] = (0, 0, 255),
        id_color: Tuple[int, int, int] = (0, 0, 0),
    ):
        image = cv2.circle(image, (self.x, self.y), 5, kp_color, -1)
        image = cv2.putText(image, str(self.id), (self.x + 10, self.y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, id_color, 1)
        return image

    def distance(self, kp: "Keypoint") -> float:
        return np.sqrt((self.x - kp.x) ** 2 + (self.y - kp.y) ** 2)


@dataclass
class Person:
    id: int
    keypoints: List[Keypoint]
    skintone: Skintone
    age: Age
    sex: Sex
    occlusion: Optional[bool] = None
    lighting: Optional[bool] = None
    expression: Optional[bool] = None

    @property
    def iod(self) -> Optional[int]:
        left_eye = self.get_keypoint(7)
        right_eye = self.get_keypoint(11)
        if left_eye and right_eye:
            return left_eye.distance(right_eye)
        return None

    def get_centroid(self) -> Keypoint:
        x = sum(kp.x for kp in self.keypoints) // len(self.keypoints)
        y = sum(kp.y for kp in self.keypoints) // len(self.keypoints)
        return x, y

    def get_keypoint(self, kp_id: int) -> Optional[Keypoint]:
        return next((kp for kp in self.keypoints if kp.id == kp_id), None)

    def get_all_keypoints_by_id(self, kp_id: int) -> List[Keypoint]:
        return [kp for kp in self.keypoints if kp.id == kp_id]

    def get_json_format(self):
        return {self.id: [kp.get_json_format() for kp in self.keypoints]}

    def annotate_person(self, image: np.ndarray):
        for kp in self.keypoints:
            image = kp.annotate_image(image)
        return image


@dataclass
class Image:
    name: str
    persons: List[Person]
    width: int
    height: int

    def get_person(self, person_id: int) -> Optional[Person]:
        return next((p for p in self.persons if p.id == person_id), None)

    def get_persons_json(self):
        persons_dict = {}
        for person in self.persons:
            persons_dict.update(person.get_json_format())
        return json.dumps(persons_dict)


@dataclass
class BoundingBox:
    x: int
    y: int
    w: int
    h: int

    @property
    def center(self) -> Tuple[int, int]:
        return self.x + self.w // 2, self.y + self.h // 2

    @classmethod
    def from_pt1_pt2_format(cls, x1: int, y1: int, x2: int, y2: int):
        return cls(x1, y1, x2 - x1, y2 - y1)

    def switch_axes(self):
        self.w, self.h = self.h, self.w

    def annotate_image(self, image: np.ndarray, color: Tuple[int, int, int] = (255, 0, 0)):
        return cv2.rectangle(image, (self.x, self.y), (self.x + self.w, self.y + self.h), color, 2)

    def get_intersection(self, bbox: "BoundingBox"):
        x1 = max(self.x, bbox.x)
        y1 = max(self.y, bbox.y)
        x2 = min(self.x + self.w, bbox.x + bbox.w)
        y2 = min(self.y + self.h, bbox.y + bbox.h)
        return x1, y1, x2, y2

    def calculate_iou(self, bbox: "BoundingBox"):
        x1, y1, x2, y2 = self.get_intersection(bbox)
        intersection = max(0, x2 - x1) * max(0, y2 - y1)

        bbox1_area = self.w * self.h
        bbox2_area = bbox.w * bbox.h

        union = bbox1_area + bbox2_area - intersection
        return intersection / union


@dataclass
class Estimation:
    image_name: str
    person_id: int
    keypoints: List[Keypoint]

    def get_keypoint(self, kp_id: int) -> Optional[Keypoint]:
        return next((kp for kp in self.keypoints if kp.id == kp_id), None)

    def annotate_person(self, image: np.ndarray):
        for kp in self.keypoints:
            image = kp.annotate_image(image, (255, 0, 0))
        return image


FACTORS = {
    "location": [kp_id for kp_id in KEYPOINTS.keys()],  # Assuming 68 keypoints for location
    "age": [age for age in Age if age != Age.NotAvailable],
    "sex": [sex for sex in Sex if sex != Sex.NotAvailable],
    "skintone": [skintone for skintone in Skintone if skintone != Skintone.NotAvailable],
    "expressions": [True, False],
    "lighting": [True, False],
    "occlusion": [True, False],
}
