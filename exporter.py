import csv
import os
from datetime import datetime

import tracker


EXPORT_FOLDER = "exports"


def ensure_export_folder():
    os.makedirs(EXPORT_FOLDER, exist_ok=True)


def export_stats_to_csv():
    ensure_export_folder()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(EXPORT_FOLDER, f"keyrecord_export_{timestamp}.csv")

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["category", "input", "count"])

        for key, count in tracker.stats["keyboard"].items():
            writer.writerow(["keyboard", key, count])

        for button, count in tracker.stats["mouse"].items():
            writer.writerow(["mouse", button, count])

    return file_path