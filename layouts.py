import json
import os
from dataclasses import dataclass
from enum import Enum


LAYOUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "layouts")


class LayoutId(Enum):
    ISO_ES = "iso_es"
    ANSI_US = "ansi_us"
    AZERTY_FR = "azerty_fr"


@dataclass(frozen=True)
class KeyboardLayout:
    layout_id: LayoutId
    name: str
    physical: str
    right_alt_label: str
    numpad_decimal: str
    function_labels: dict
    nav_labels: dict
    rows: dict

    @property
    def is_iso(self):
        return self.physical == "iso"


def _load_layout(layout_id):
    path = os.path.join(LAYOUTS_DIR, f"{layout_id.value}.json")

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return KeyboardLayout(
        layout_id=layout_id,
        name=data["name"],
        physical=data["physical"],
        right_alt_label=data["right_alt_label"],
        numpad_decimal=data["numpad_decimal"],
        function_labels=data["function_labels"],
        nav_labels=data["nav_labels"],
        rows=data["rows"],
    )


LAYOUTS_BY_NAME = {
    layout.name: layout
    for layout in (_load_layout(layout_id) for layout_id in LayoutId)
}


def available_names():
    return list(LAYOUTS_BY_NAME.keys())


def get_layout(name):
    return LAYOUTS_BY_NAME.get(name) or next(iter(LAYOUTS_BY_NAME.values()))
