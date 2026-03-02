"""
Camera profile registry for Fluke thermal camera models (.is2).

Each profile defines: file names, byte layouts, offsets, dimensions, and methods,
so the pipeline is standardized by the model read from the file.

To add a new model: add one entry to CAMERA_PROFILES. Detection order and
supported-model list are derived from the dict (key order = detection order;
put more specific model names first).
"""
from typing import Dict, Any, Optional

GITHUB_MESSAGE = (
    " This camera model is not in the registry. Please open an issue or submit a pull request "
    "on the project GitHub repository with your file details or a sample so support can be added."
)


class UnsupportedCameraError(ValueError):
    """Raised when the camera model is not in the registry."""

    def __init__(self, message: str, model: Optional[str] = None):
        self.model = model
        full = message + GITHUB_MESSAGE
        super().__init__(full)


# -----------------------------------------------------------------------------
# Standard keys: files and paths (names inside the ZIP)
# -----------------------------------------------------------------------------
KEY_THERMAL_FILE = "thermal_file"
KEY_CALIBRATION_FILE = "calibration_file"
KEY_CAMERA_INFO_FILE = "camera_info_file"
KEY_METADATA_FILE = "metadata_file"
KEY_IR_IMAGE_INFO_FILE = "ir_image_info_file"

# -----------------------------------------------------------------------------
# CameraInfo.gpbenc layout (byte offset and length per field)
# -----------------------------------------------------------------------------
KEY_CAMERA_INFO_LAYOUT = "camera_info_layout"
KEY_CAMERA_INFO_ENCODING = "camera_info_encoding"
KEY_CAMERA_INFO_MIN_BYTES = "camera_info_min_bytes"
KEY_MODEL_FALLBACK_FROM_PROFILE = "model_fallback_from_profile"

# CameraInfo layout: Latin-1, model string at bytes 97:103
LAYOUT_CAMERA_INFO_LATIN_97_103 = {
    "CameraManufacturer": (76, 94),
    "CameraModel": (97, 103),
    "EngineSerial": (104, 112),
    "CameraSerial": (115, 124),
}

# -----------------------------------------------------------------------------
# IRImageInfo.gpbenc layout (byte ranges for 4-byte LE floats)
# -----------------------------------------------------------------------------
KEY_IR_IMAGE_INFO_LAYOUT = "ir_image_info_layout"
KEY_IR_IMAGE_INFO_MIN_BYTES = "ir_image_info_min_bytes"

# IRImageInfo layout: 4-byte LE floats at 33:47
LAYOUT_IR_IMAGE_INFO_33_47 = {
    "emissivity": (33, 37),
    "background_temp": (38, 42),
    "transmission": (43, 47),
}

# 16-bit raw -> °C scaling from IRImageInfo when no LUT; (temp_min_slice, temp_max_slice) e.g. ((38,42), (33,37))
KEY_IR_IMAGE_INFO_TEMP_RANGE = "ir_image_info_temp_range"

# -----------------------------------------------------------------------------
# Thermal data and calibration
# -----------------------------------------------------------------------------
KEY_THERMAL_SOURCE = "thermal_source"
KEY_THERMAL_DIMENSIONS = "thermal_dimensions"
KEY_IR_DATA_OFFSET = "ir_data_offset"
KEY_IR_DATA_HEADER_DIMS = "ir_data_header_dims"
KEY_CALIBRATION = "calibration"
KEY_ACCEPT_PLACEHOLDER_CAL = "accept_placeholder_cal"
KEY_PAYLOAD_SIZES_ORDER = "payload_sizes_order"

# -----------------------------------------------------------------------------
# Metadata and dimensions
# -----------------------------------------------------------------------------
KEY_METADATA_SOURCE = "metadata_source"
KEY_DIMENSIONS_FROM = "dimensions_from"

# -----------------------------------------------------------------------------
# Profile identification
# -----------------------------------------------------------------------------
KEY_CANONICAL_NAME = "canonical_name"


def _profile_ir_data(canonical_name: str, width: int, height: int) -> Dict[str, Any]:
    """Profile for models that store thermogram in IR.data and metadata in ImageProperties.json."""
    return {
        KEY_CANONICAL_NAME: canonical_name,
        KEY_THERMAL_FILE: "Images/Main/IR.data",
        KEY_CALIBRATION_FILE: "CalibrationData.gpbenc",
        KEY_CAMERA_INFO_FILE: "CameraInfo.gpbenc",
        KEY_METADATA_FILE: "ImageProperties.json",
        KEY_IR_IMAGE_INFO_FILE: "Images/Main/IRImageInfo.gpbenc",
        KEY_CAMERA_INFO_LAYOUT: LAYOUT_CAMERA_INFO_LATIN_97_103,
        KEY_CAMERA_INFO_ENCODING: "latin-1",
        KEY_CAMERA_INFO_MIN_BYTES: 124,
        KEY_MODEL_FALLBACK_FROM_PROFILE: False,
        KEY_IR_IMAGE_INFO_LAYOUT: LAYOUT_IR_IMAGE_INFO_33_47,
        KEY_IR_IMAGE_INFO_MIN_BYTES: 47,
        KEY_THERMAL_SOURCE: "IR.data",
        KEY_THERMAL_DIMENSIONS: (width, height),
        KEY_IR_DATA_OFFSET: "width",
        KEY_IR_DATA_HEADER_DIMS: (192, 193),
        KEY_CALIBRATION: "CalibrationData.gpbenc",
        KEY_ACCEPT_PLACEHOLDER_CAL: False,
        KEY_METADATA_SOURCE: "ImageProperties.json",
        KEY_DIMENSIONS_FROM: "metadata",
        KEY_PAYLOAD_SIZES_ORDER: [(width, height)],
    }


# -----------------------------------------------------------------------------
# Registry: one entry per model. Add new models here.
# Key order = detection order (most specific first so e.g. TiS75+ before Ti300).
# -----------------------------------------------------------------------------
CAMERA_PROFILES: Dict[str, Dict[str, Any]] = {
    "TiS75+": {
        KEY_CANONICAL_NAME: "TiS75+",
        KEY_THERMAL_FILE: "CalTempDataRex.gpbenc",
        KEY_CALIBRATION_FILE: "CalibrationData.gpbenc",
        KEY_CAMERA_INFO_FILE: "CameraInfo.gpbenc",
        KEY_METADATA_FILE: "metadata.json",
        KEY_IR_IMAGE_INFO_FILE: "Images/Main/IRImageInfo.gpbenc",
        KEY_CAMERA_INFO_LAYOUT: None,
        KEY_CAMERA_INFO_ENCODING: "binary",
        KEY_CAMERA_INFO_MIN_BYTES: 0,
        KEY_MODEL_FALLBACK_FROM_PROFILE: True,
        KEY_IR_IMAGE_INFO_LAYOUT: {
            "emissivity": (43, 47),
            "background_temp": (38, 42),
            "transmission": (43, 47),
            "temp_range_min": (38, 42),
            "temp_range_max": (33, 37),
        },
        KEY_IR_IMAGE_INFO_TEMP_RANGE: ((38, 42), (33, 37)),
        KEY_IR_IMAGE_INFO_MIN_BYTES: 47,
        KEY_THERMAL_SOURCE: "CalTempDataRex.gpbenc",
        KEY_THERMAL_DIMENSIONS: (384, 288),
        KEY_IR_DATA_OFFSET: "width",
        KEY_IR_DATA_HEADER_DIMS: (192, 193),
        KEY_CALIBRATION: "placeholder",
        KEY_ACCEPT_PLACEHOLDER_CAL: True,
        KEY_METADATA_SOURCE: "metadata.json",
        KEY_DIMENSIONS_FROM: "fixed",
        KEY_PAYLOAD_SIZES_ORDER: [(384, 288)],
    },
    "Ti480P": _profile_ir_data("Ti480P", 640, 480),
    "Ti300": _profile_ir_data("Ti300", 320, 240),
}

SUPPORTED_MODELS = tuple(CAMERA_PROFILES.keys())
# Detection strings derived from registry keys (same order as CAMERA_PROFILES)
KNOWN_MODEL_STRINGS_BYTES = [m.encode("ascii") for m in CAMERA_PROFILES]


def detect_model_from_camera_info(raw: bytes) -> Optional[str]:
    """
    Detect camera model from CameraInfo.gpbenc. Returns canonical name if in registry,
    else raw model from bytes 97:103 for default classic profile.
    """
    if not raw:
        return None
    # 1) Search for known model strings (works for TiS75+ binary layout)
    for needle in KNOWN_MODEL_STRINGS_BYTES:
        if needle in raw:
            return needle.decode("ascii")
    # 2) Latin layout at 97:103 (Ti300, Ti480P, or unknown)
    if len(raw) >= 103:
        try:
            model_slice = raw[97:103].decode("latin-1", errors="replace").strip().rstrip("- \t")
            for canonical in CAMERA_PROFILES:
                if canonical in model_slice or model_slice in canonical:
                    return canonical
            if model_slice and model_slice.isprintable():
                return model_slice  # unknown but printable, use for default profile
        except Exception:
            pass
    return None


def get_camera_profile(
    camera_model: Optional[str] = None,
    *,
    has_ir_data: Optional[bool] = None,
    has_caltempdatarex: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Return profile for the given model. If model is not in the registry, use default
    classic profile (IR.data, ImageProperties.json, Latin layout) so new/unknown cameras
    that use the same format as Ti300/Ti480P still work. Raise only when file has
    CalTempDataRex but no IR.data and model is unknown.
    """
    model = (camera_model or "").strip().rstrip("- \t")
    if model in ("?", "Unknown", ""):
        model = ""
    profile = None
    for canonical in CAMERA_PROFILES:
        if canonical in model or model.startswith(canonical):
            profile = CAMERA_PROFILES.get(canonical)
            if profile:
                break
    if profile is None:
        # Unknown model: use classic (Ti300/Ti480P-like) default if file has IR.data
        if has_ir_data:
            return dict(_profile_ir_data(model or "Unknown", 320, 240))
        if has_caltempdatarex:
            supported = ", ".join(SUPPORTED_MODELS)
            raise UnsupportedCameraError(
                f"Unknown camera model (file has CalTempDataRex only). Supported: {supported}.",
                model=model or None,
            )
        # No thermal source yet; use default classic, dimensions from file later
        return dict(_profile_ir_data(model or "Unknown", 320, 240))
    return dict(profile)
