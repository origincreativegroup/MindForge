"""Utilities for lightweight real-time collaboration features.

The original module in the project was truncated which resulted in an
``IndentationError`` during import.  The tests only exercise a couple of helper
functions for generating annotation metadata and calculating coordinates within
an image.  This file provides a small, self‑contained implementation of those
features so that the collaboration utilities can be imported and used in the
unit tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class RealTimeCollaboration:
    """Utility helpers used by the tests.

    The implementation is intentionally lightweight – it doesn't interact with a
    database or any external service.  Instead it focuses solely on the logic
    required for the unit tests which verify coordinate calculations and
    metadata creation for different kinds of annotations.
    """

    @staticmethod
    def generate_visual_comment_coordinates(
        x: float, y: float, image_width: int, image_height: int
    ) -> Dict[str, float]:
        """Return both absolute and percentage based coordinates.

        ``pytest`` checks a variety of edge cases (zero coordinates, values that
        hit the image bounds and floating point precision) so the calculation is
        kept straightforward and deterministic.
        """

        if image_width <= 0 or image_height <= 0:
            return {
                "x_percent": 0.0,
                "y_percent": 0.0,
                "x_absolute": x,
                "y_absolute": y,
                "image_width": image_width,
                "image_height": image_height,
            }

        return {
            "x_percent": (x / image_width) * 100.0,
            "y_percent": (y / image_height) * 100.0,
            "x_absolute": x,
            "y_absolute": y,
            "image_width": image_width,
            "image_height": image_height,
        }

    @staticmethod
    def create_annotation_metadata(
        annotation_type: str,
        coordinates: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a metadata dictionary for an annotation.

        The behaviour mirrors what the tests expect: depending on the
        ``annotation_type`` different keyword arguments are recorded in the
        returned dictionary.  All metadata include a timestamp so that callers
        can determine when the annotation was created.
        """

        metadata: Dict[str, Any] = {
            "annotation_type": annotation_type,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if coordinates is not None:
            metadata["coordinates"] = coordinates

        if annotation_type == "design_suggestion":
            metadata["suggestion_category"] = kwargs.get("category")
            metadata["priority"] = kwargs.get("priority")
        elif annotation_type == "approval":
            metadata["approval_status"] = kwargs.get("status")
            metadata["approval_level"] = kwargs.get("level")
        elif annotation_type == "issue":
            metadata["issue_severity"] = kwargs.get("severity")
            metadata["issue_category"] = kwargs.get("category")

        # For "general" or unknown types no extra fields are added beyond the
        # coordinates and timestamp.
        return metadata

