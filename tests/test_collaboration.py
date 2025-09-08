import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "apps"))
sys.path.append(str(project_root / "packages"))

from backend.services.collaboration import RealTimeCollaboration


def test_visual_comment_coordinates():
    """Test visual comment coordinate generation."""
    coords = RealTimeCollaboration.generate_visual_comment_coordinates(
        x=100.0, y=200.0, image_width=800, image_height=600
    )
    
    assert coords["x_percent"] == 12.5  # 100/800 * 100
    assert abs(coords["y_percent"] - 33.333333333333336) < 0.001  # 200/600 * 100
    assert coords["x_absolute"] == 100.0
    assert coords["y_absolute"] == 200.0
    assert coords["image_width"] == 800
    assert coords["image_height"] == 600


def test_annotation_metadata_design_suggestion():
    """Test annotation metadata creation for design suggestions."""
    metadata = RealTimeCollaboration.create_annotation_metadata(
        "design_suggestion",
        coordinates={"x": 100, "y": 200},
        category="layout",
        priority="high"
    )
    
    assert metadata["annotation_type"] == "design_suggestion"
    assert metadata["suggestion_category"] == "layout"
    assert metadata["priority"] == "high"
    assert "timestamp" in metadata
    assert metadata["coordinates"]["x"] == 100
    assert metadata["coordinates"]["y"] == 200


def test_annotation_metadata_approval():
    """Test annotation metadata creation for approval comments."""
    metadata = RealTimeCollaboration.create_annotation_metadata(
        "approval",
        status="approved",
        level="final"
    )
    
    assert metadata["annotation_type"] == "approval"
    assert metadata["approval_status"] == "approved"
    assert metadata["approval_level"] == "final"
    assert "timestamp" in metadata


def test_annotation_metadata_issue():
    """Test annotation metadata creation for issue comments."""
    metadata = RealTimeCollaboration.create_annotation_metadata(
        "issue",
        severity="high",
        category="color"
    )
    
    assert metadata["annotation_type"] == "issue"
    assert metadata["issue_severity"] == "high"
    assert metadata["issue_category"] == "color"
    assert "timestamp" in metadata


def test_annotation_metadata_general():
    """Test annotation metadata creation for general comments."""
    metadata = RealTimeCollaboration.create_annotation_metadata(
        "general",
        coordinates={"x": 50, "y": 75}
    )
    
    assert metadata["annotation_type"] == "general"
    assert metadata["coordinates"]["x"] == 50
    assert metadata["coordinates"]["y"] == 75
    assert "timestamp" in metadata
    # General type should not have extra fields
    assert "suggestion_category" not in metadata
    assert "approval_status" not in metadata
    assert "issue_severity" not in metadata


def test_coordinate_edge_cases():
    """Test coordinate generation with edge cases."""
    # Test with zero coordinates
    coords = RealTimeCollaboration.generate_visual_comment_coordinates(0, 0, 100, 100)
    assert coords["x_percent"] == 0.0
    assert coords["y_percent"] == 0.0
    
    # Test with maximum coordinates
    coords = RealTimeCollaboration.generate_visual_comment_coordinates(100, 200, 100, 200)
    assert coords["x_percent"] == 100.0
    assert coords["y_percent"] == 100.0
    
    # Test with floating point precision
    coords = RealTimeCollaboration.generate_visual_comment_coordinates(33.33, 66.67, 100, 100)
    assert abs(coords["x_percent"] - 33.33) < 0.01
    assert abs(coords["y_percent"] - 66.67) < 0.01