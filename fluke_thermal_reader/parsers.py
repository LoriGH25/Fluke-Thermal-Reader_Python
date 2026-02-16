"""Parse Fluke .is2 thermal files (ZIP with CameraInfo, IR.data or CalTempDataRex, metadata)."""

import os
import shutil
import struct
import numpy as np
import json
from zipfile import ZipFile
from typing import Dict, Any
from struct import unpack
from .utilities import UnitConversion, calc_equation, scale_uint16_to_temperature, counts_to_temperature_linear
from .camera_profiles import (
    get_camera_profile,
    detect_model_from_camera_info,
    UnsupportedCameraError,
    KEY_ACCEPT_PLACEHOLDER_CAL,
    KEY_PAYLOAD_SIZES_ORDER,
    KEY_THERMAL_DIMENSIONS,
    KEY_CAMERA_INFO_LAYOUT,
    KEY_CAMERA_INFO_ENCODING,
    KEY_CAMERA_INFO_MIN_BYTES,
    KEY_CAMERA_INFO_FILE,
    KEY_IR_IMAGE_INFO_LAYOUT,
    KEY_IR_IMAGE_INFO_MIN_BYTES,
    KEY_IR_IMAGE_INFO_FILE,
    KEY_IR_IMAGE_INFO_TEMP_RANGE,
    KEY_IR_DATA_OFFSET,
)


class IS2Parser:
    """Parse .is2 ZIP: detect model, load profile, read thermal data and metadata."""

    def __init__(self):
        self.temp_dir = "temp_fluke_reader"

    def parse(self, file_path: str) -> Dict[str, Any]:
        """Extract .is2 ZIP and return dict with data, size, metadata, paths."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with ZipFile(file_path, "r") as z:
            z.extractall(self.temp_dir)
        try:
            ir = {"FileName": os.path.basename(file_path)}
            self._detect_camera_model(ir)
            self._resolve_camera_profile(ir)
            self._read_camera_info(ir)
            self._read_image_properties(ir)
            self._read_calibration_data(ir)
            self._read_ir_image_info(ir)
            self._read_ir_data(ir)
            self._read_thumbnail(ir)
            self._read_photo(ir)
            return ir
        finally:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

    def _parse_gpbenc_length_delimited(self, raw: bytes, base_offset: int = 0, recurse: bool = True) -> list:
        """Return (offset, length) for each length-delimited field (wire type 2); recurse into large blocks."""
        result = []
        pos, n = 0, len(raw)

        def read_varint():
            nonlocal pos
            if pos >= n:
                return None
            v, shift = 0, 0
            while pos < n:
                b = raw[pos]
                pos += 1
                v |= (b & 0x7F) << shift
                if (b & 0x80) == 0:
                    return v
                shift += 7
                if shift >= 64:
                    return None
            return None

        while pos < n:
            tag = read_varint()
            if tag is None:
                break
            wt = tag & 7
            if wt == 0:
                read_varint()
            elif wt == 1:
                pos += 8
                if pos > n:
                    break
            elif wt == 2:
                length = read_varint()
                if length is None or pos + length > n:
                    break
                result.append((base_offset + pos, length))
                if recurse and length > 1024 and length < len(raw):
                    sub = raw[pos : pos + length]
                    for t in self._parse_gpbenc_length_delimited(sub, base_offset + pos, True):
                        result.append(t)
                pos += length
            elif wt == 5:
                pos += 4
                if pos > n:
                    break
            else:
                break
        return result

    def _extract_thermal_from_caltempdatarex(self, raw: bytes, payload_sizes_order: list, ir_data_offset: str = None) -> tuple:
        """Extract uint16 thermal from CalTempDataRex; try (w,h) from profile; optional header skip. Returns (arr, w, h) or (None, 0, 0)."""
        sizes = list(payload_sizes_order) if payload_sizes_order else []
        for (blob_start, length) in self._parse_gpbenc_length_delimited(raw):
            for w, h in sizes:
                if length == w * h * 2 and blob_start + length <= len(raw):
                    arr = np.frombuffer(raw[blob_start : blob_start + length], dtype=np.uint16)
                    if arr.size == w * h:
                        return arr, w, h
                # Blob with header: skip first N uint16s (N = height or width from profile)
                if ir_data_offset:
                    skip = h if ir_data_offset == "height" else w
                    blob_len = (skip + w * h) * 2
                    if length == blob_len and blob_start + length <= len(raw):
                        arr = np.frombuffer(
                            raw[blob_start + skip * 2 : blob_start + length], dtype=np.uint16
                        )
                        if arr.size == w * h:
                            return arr, w, h
        for w, h in sizes:
            payload_size = w * h * 2
            if len(raw) >= payload_size:
                arr = np.frombuffer(raw[-payload_size:], dtype=np.uint16)
                return arr, w, h
        return None, 0, 0

    def _detect_camera_model(self, ir: Dict[str, Any]):
        """Set ir['CameraModel'] from CameraInfo.gpbenc (layout or string search)."""
        path = os.path.join(self.temp_dir, "CameraInfo.gpbenc")
        if not os.path.exists(path):
            return
        try:
            with open(path, "rb") as f:
                raw = f.read()
            model = detect_model_from_camera_info(raw)
            if model:
                ir["CameraModel"] = model
        except Exception:
            pass

    def _read_camera_info(self, ir: Dict[str, Any]):
        """Read manufacturer, model, serial from CameraInfo.gpbenc (profile layout)."""
        profile = ir.get("_profile", {})
        camera_info_file = profile.get(KEY_CAMERA_INFO_FILE, 'CameraInfo.gpbenc')
        camera_info_path = os.path.join(self.temp_dir, camera_info_file)
        if not os.path.exists(camera_info_path):
            return
        layout = profile.get(KEY_CAMERA_INFO_LAYOUT)
        min_bytes = profile.get(KEY_CAMERA_INFO_MIN_BYTES, 0)
        encoding = profile.get(KEY_CAMERA_INFO_ENCODING, 'latin-1')
        try:
            with open(camera_info_path, 'rb') as f:
                raw = f.read()
            if len(raw) < min_bytes and layout is not None:
                return
            if layout is None:
                # Binary/protobuf file (e.g. TiS75+): do not read at fixed offsets
                return
            text = raw.decode(encoding, errors="replace")
            for field_name, (start, end) in layout.items():
                if end <= len(text):
                    val = text[start:end].strip()
                    if field_name == "CameraModel":
                        val = val.rstrip("- \t")  # file may have "Ti300-" padding
                    if val:
                        ir[field_name] = val
        except Exception:
            pass

    def _get_prop(self, props: Dict[str, Any], keys: list, default=None):
        """First matching key in props; strip quotes if string."""
        for k in keys:
            if k in props and props[k] is not None:
                v = props[k]
                if isinstance(v, str):
                    v = v.strip('"')
                return v
        return default

    def _read_image_properties(self, ir: Dict[str, Any]):
        """Read dimensions, temps, emissivity from ImageProperties.json or metadata.json."""
        for filename in ("ImageProperties.json", "metadata.json"):
            path = os.path.join(self.temp_dir, filename)
            if not os.path.exists(path):
                continue
            try:
                for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
                    try:
                        with open(path, 'r', encoding=encoding) as f:
                            props = json.load(f)
                        break
                    except Exception:
                        continue
                else:
                    continue
                g = lambda *keys, d=None: self._get_prop(props, list(keys), default=d)
                v = g("IRPROP_THERMAL_IMAGER_MAKE", "ThermalImagerMake", "CameraManufacturer", d="Unknown")
                if v != "Unknown":
                    ir["CameraManufacturer"] = v
                v = g("IRPROP_THERMAL_IMAGER_MODEL", "ThermalImagerModel", "CameraModel", "Model", d="Unknown")
                if v != "Unknown":
                    ir["CameraModel"] = str(v).strip('"')
                v = g("IRPROP_THERMAL_IMAGER_SN", "ThermalImagerSN", "CameraSerial", "SerialNumber", d="Unknown")
                if v != "Unknown":
                    ir["CameraSerial"] = str(v).strip('"')
                    ir.setdefault("EngineSerial", ir["CameraSerial"])
                w = g("IRPROP_IR_SENSOR_WIDTH", "IRWidth", "Width", "ThermalWidth")
                h = g("IRPROP_IR_SENSOR_HEIGHT", "IRHeight", "Height", "ThermalHeight")
                try:
                    ir["IRWidth"] = int(w) if w is not None else 640
                except (TypeError, ValueError):
                    ir["IRWidth"] = 640
                try:
                    ir["IRHeight"] = int(h) if h is not None else 480
                except (TypeError, ValueError):
                    ir["IRHeight"] = 480
                ir["VLWidth"] = int(g("IRPROP_VL_SENSOR_WIDTH", "VLWidth", d=ir["IRWidth"]) or ir["IRWidth"])
                ir["VLHeight"] = int(g("IRPROP_VL_SENSOR_HEIGHT", "VLHeight", d=ir["IRHeight"]) or ir["IRHeight"])
                ir["size"] = [ir["IRWidth"], ir["IRHeight"]]
                ir["CaptureDateTime"] = g("IRPROP_THERMAL_IMAGE_CAPTURE_DATE_TIME", "CaptureDateTime", "DateTime", d="") or ""
                for key, prop_keys, def_val in [
                    ("MinTemp", ["IRPROP_THERMAL_IMAGE_MIN_TEMP_C", "MinTemp", "MinTempC"], 0),
                    ("MaxTemp", ["IRPROP_THERMAL_IMAGE_MAX_TEMP_C", "MaxTemp", "MaxTempC"], 0),
                    ("AvgTemp", ["IRPROP_THERMAL_IMAGE_AVG_TEMP_C", "AvgTemp", "AvgTempC"], 0),
                    ("CenterTemp", ["IRPROP_THERMAL_IMAGE_CENTER_POINT_TEMP_C", "CenterTemp"], 0),
                    ("BackgroundTemp", ["IRPROP_THERMAL_IMAGE_BG_TEMP_C", "BackgroundTemp", "ReflectedTemp", "BgTempC"], 20),
                    ("Emissivity", ["IRPROP_THERMAL_IMAGE_EMISSIVITY", "Emissivity"], 0.95),
                ]:
                    val = g(*prop_keys, d=def_val)
                    try:
                        ir[key] = float(val) if val is not None else def_val
                    except (TypeError, ValueError):
                        ir[key] = def_val
                tr_val = g("IRPROP_THERMAL_IMAGE_TRANSMISSIVITY", "Transmission", "Transmissivity")
                if tr_val is not None:
                    try:
                        ir["transmission"] = float(tr_val)
                    except (TypeError, ValueError):
                        pass
                for k, pk, default in [("IRLenses", ["IRPROP_THERMAL_IMAGER_IR_LENSES", "IRLenses"], ""), ("IRLensesSerial", ["IRPROP_THERMAL_IMAGER_IR_LENSES_SN", "IRLensesSerial"], ""), ("CalibrationDate", ["IRPROP_THERMAL_IMAGER_CALIBRATION_DATE", "CalibrationDate"], ""), ("Title", ["IRPROP_THERMAL_IMAGE_TITLE", "Title"], ""), ("Comments", ["IRPROP_THERMAL_IMAGE_COMMENTS", "Comments"], "")]:
                    ir[k] = g(*pk, d=default) or default
                for k, pk, default in [
                    ("ContainsAnnotations", ["IRPROP_THERMAL_IMAGE_CONTAINS_ANNOTATIONS", "ContainsAnnotations"], False),
                    ("ContainsAudio", ["IRPROP_THERMAL_IMAGE_CONTAINS_AUDIO", "ContainsAudio"], False),
                    ("ContainsCNXReadings", ["IRPROP_THERMAL_IMAGE_CONTAINS_CNX_READINGS", "ContainsCNXReadings"], False),
                ]:
                    v = g(*pk, d=default)
                    ir[k] = v in (True, "True", "true") if v is not None else default
            except Exception:
                pass
            else:
                break
        self._infer_dimensions_from_main_image(ir)

    def _get_main_image_dimensions_hint(self) -> list:
        """(w, h) from main image filename hex stem (e.g. 050003C0 -> 1280x960). Returns [(w,h)] or []."""
        main_dir = os.path.join(self.temp_dir, 'Images', 'Main')
        if not os.path.isdir(main_dir):
            return []
        best = None
        best_size = 0
        for name in os.listdir(main_dir):
            if not name.lower().endswith('.jpg'):
                continue
            stem = os.path.splitext(name)[0]
            if len(stem) != 8:
                continue
            try:
                w_hex = int(stem[:4], 16)
                h_hex = int(stem[4:8], 16)
            except ValueError:
                continue
            if w_hex < 100 or w_hex > 4096 or h_hex < 100 or h_hex > 4096:
                continue
            size = os.path.getsize(os.path.join(main_dir, name))
            if size > best_size:
                best_size = size
                best = (w_hex, h_hex)
        return [best] if best else []

    def _infer_dimensions_from_main_image(self, ir: Dict[str, Any]):
        """Set IR size from main image filename (8-char hex stem) when not already set."""
        if ir.get("IRWidth") and ir.get("IRHeight") and (ir["IRWidth"], ir["IRHeight"]) != (640, 480):
            return
        main_dir = os.path.join(self.temp_dir, 'Images', 'Main')
        if not os.path.isdir(main_dir):
            return
        best_stem = None
        best_size = 0
        for name in os.listdir(main_dir):
            if not name.lower().endswith('.jpg'):
                continue
            stem = os.path.splitext(name)[0]
            if len(stem) != 8:
                continue
            try:
                w_hex = int(stem[:4], 16)
                h_hex = int(stem[4:8], 16)
            except ValueError:
                continue
            if w_hex < 100 or w_hex > 4096 or h_hex < 100 or h_hex > 4096:
                continue
            size = os.path.getsize(os.path.join(main_dir, name))
            if size > best_size:
                best_size = size
                best_stem = (w_hex, h_hex)
        if best_stem is not None:
            ir['IRWidth'] = best_stem[0]
            ir['IRHeight'] = best_stem[1]
            ir['size'] = [best_stem[0], best_stem[1]]
            if 'VLWidth' not in ir or ir.get('VLWidth') in (640, None):
                ir['VLWidth'] = best_stem[0]
            if 'VLHeight' not in ir or ir.get('VLHeight') in (480, None):
                ir['VLHeight'] = best_stem[1]

    def _resolve_camera_profile(self, ir: Dict[str, Any]):
        """Set ir['_profile'] from CameraModel; raise UnsupportedCameraError if unknown."""
        ir_data_path = os.path.join(self.temp_dir, 'Images', 'Main', 'IR.data')
        caltemp_path = os.path.join(self.temp_dir, 'CalTempDataRex.gpbenc')
        has_ir_data = os.path.exists(ir_data_path)
        has_caltempdatarex = os.path.exists(caltemp_path)
        ir['_profile'] = get_camera_profile(
            ir.get('CameraModel'),
            has_ir_data=has_ir_data,
            has_caltempdatarex=has_caltempdatarex,
        )

    def _read_calibration_data(self, ir: Dict[str, Any]):
        """Build count->temperature LUT from CalibrationData.gpbenc (magic 74,25,13). TiS75+ may use placeholder."""
        cal_path = os.path.join(self.temp_dir, 'CalibrationData.gpbenc')
        if not os.path.exists(cal_path):
            raise Exception(
                "CalibrationData.gpbenc not found in this .is2 file. "
                "This camera (e.g. TiS75+) may use a different calibration format not yet supported."
            )
        try:
            cal_data = np.fromfile(cal_path, dtype=np.uint8)
            ir['range'] = int(cal_data[18]) if len(cal_data) > 18 else 0
            ir['conversion'] = {}
            magic = (74, 25, 13)
            for layout in (0, 1):
                if ir['conversion']:
                    break
                for i in range(len(cal_data) - 26):
                    if (cal_data[i], cal_data[i + 1], cal_data[i + 2]) != magic:
                        continue
                    curve_part = cal_data[i + 3:i + 27]
                    if len(curve_part) < 24:
                        continue
                    if layout == 0:
                        temp_range = np.array([unpack('<f', curve_part[:4])[0], unpack('<f', curve_part[5:9])[0]])
                    else:
                        temp_range = np.array([unpack('<f', curve_part[:4])[0], unpack('<f', curve_part[4:8])[0]])
                    if temp_range[0] >= temp_range[1]:
                        continue
                    equation_variables = {'a': unpack('<f', curve_part[20:24])[0],
                                        'b': unpack('<f', curve_part[15:19])[0],
                                        'c': unpack('<f', curve_part[10:14])[0]}
                    if equation_variables['a'] == 0:
                        continue
                    if (equation_variables['a'] == -1.0 and equation_variables['b'] == -1.0 and equation_variables['c'] == -1.0):
                        continue
                    if temp_range[0] == -1.0 and temp_range[1] == -1.0:
                        continue
                    try:
                        data_range = calc_equation(
                            [equation_variables['a'], equation_variables['b'], equation_variables['c']],
                            temp_range)
                        data_range_int = [int(data_range[0]) + (data_range[0] % 1 > 0),
                                        int(data_range[1]) + (data_range[1] % 1 > 0)]
                        if data_range_int[0] >= data_range_int[1]:
                            continue
                        for j in range(data_range_int[0], min(data_range_int[1], data_range_int[0] + 65536)):
                            disc = equation_variables['b'] ** 2 - 4 * equation_variables['a'] * (equation_variables['c'] - j)
                            if disc < 0:
                                continue
                            t_rad = ((-equation_variables['b'] + np.sqrt(disc)) / (2 * equation_variables['a']))
                            if -273.2 <= t_rad <= 3000:
                                ir['conversion'][j] = t_rad
                    except (ValueError, ZeroDivisionError, FloatingPointError):
                        continue
            if not ir['conversion']:
                has_magic = any(
                    (cal_data[i], cal_data[i + 1], cal_data[i + 2]) == magic
                    for i in range(len(cal_data) - 2)
                )
                if not has_magic:
                    raise UnsupportedCameraError(
                        "CalibrationData.gpbenc does not contain the expected format (magic bytes 74,25,13)."
                    )
                try:
                    idx = next(i for i in range(len(cal_data) - 26) if (cal_data[i], cal_data[i + 1], cal_data[i + 2]) == magic)
                    curve_part = cal_data[idx + 3:idx + 27]
                    a, b, c = unpack('<f', curve_part[20:24])[0], unpack('<f', curve_part[15:19])[0], unpack('<f', curve_part[10:14])[0]
                    if a == -1.0 and b == -1.0 and c == -1.0:
                        accept = ir.get('_profile', {}).get(KEY_ACCEPT_PLACEHOLDER_CAL, False)
                        if accept:
                            ir['calibration_placeholder'] = True
                            return
                except StopIteration:
                    pass
                raise UnsupportedCameraError(
                    "No valid calibration curves found in CalibrationData.gpbenc."
                )
        except UnsupportedCameraError:
            raise
        except Exception as e:
            if "CalibrationData.gpbenc" not in str(e) and "calibration" not in str(e).lower():
                raise Exception(f"Cannot read calibration data: {e}") from e
            raise
    
    def _read_ir_image_info(self, ir: Dict[str, Any]):
        """Read emissivity, background temp, transmission, and optional temp range from IRImageInfo.gpbenc."""
        profile = ir.get('_profile', {})
        subpath = profile.get(KEY_IR_IMAGE_INFO_FILE, 'Images/Main/IRImageInfo.gpbenc')
        ir_image_info_path = os.path.join(self.temp_dir, subpath)
        if not os.path.exists(ir_image_info_path):
            return
        try:
            ir_image_info = np.fromfile(ir_image_info_path, dtype=np.uint8)
        except Exception:
            return
        layout = profile.get(KEY_IR_IMAGE_INFO_LAYOUT) or {
            "emissivity": (33, 37), "background_temp": (38, 42), "transmission": (43, 47),
        }
        min_len = profile.get(KEY_IR_IMAGE_INFO_MIN_BYTES, 47)
        if len(ir_image_info) < min_len:
            return
        transmission = unpack('<f', ir_image_info[layout["transmission"][0]:layout["transmission"][1]])[0]
        emissivity = unpack('<f', ir_image_info[layout["emissivity"][0]:layout["emissivity"][1]])[0]
        backgroundtemperature = unpack('<f', ir_image_info[layout["background_temp"][0]:layout["background_temp"][1]])[0]
        if "Emissivity" not in ir:
            ir['Emissivity'] = emissivity
        if 'Transmission' not in ir:
            ir['Transmission'] = transmission if (0 < transmission <= 1) else 1.0
        if "BackgroundTemp" not in ir:
            ir['BackgroundTemp'] = backgroundtemperature
        # 16-bit scaling: read temp range from IRImageInfo when defined in profile (e.g. TiS75+)
        temp_range = profile.get(KEY_IR_IMAGE_INFO_TEMP_RANGE)
        if temp_range and len(temp_range) >= 2:
            (lo_a, lo_b), (hi_a, hi_b) = temp_range[0], temp_range[1]
            if hi_b <= len(ir_image_info) and lo_b <= len(ir_image_info):
                ir['TempRangeMin'] = unpack('<f', ir_image_info[lo_a:lo_b])[0]
                ir['TempRangeMax'] = unpack('<f', ir_image_info[hi_a:hi_b])[0]
            
    def _read_ir_data(self, ir: Dict[str, Any]):
        """Load thermal from IR.data or CalTempDataRex; convert to °C (LUT or scale from range)."""
        ir_data_path = os.path.join(self.temp_dir, 'Images', 'Main', 'IR.data')
        caltemp_path = os.path.join(self.temp_dir, 'CalTempDataRex.gpbenc')

        if os.path.exists(ir_data_path):
            self._read_ir_data_from_ir_data(ir, ir_data_path)
        elif os.path.exists(caltemp_path):
            self._read_ir_data_from_caltempdatarex(ir, caltemp_path)
        else:
            raise UnsupportedCameraError(
                "No thermal payload found: neither Images/Main/IR.data nor CalTempDataRex.gpbenc."
            )

    def _read_ir_data_from_ir_data(self, ir: Dict[str, Any], ir_data_path: str):
        """Read thermal from IR.data (uint16); header skip from profile; fix size if metadata wrong."""
        d = np.fromfile(ir_data_path, dtype=np.uint16)
        if 'size' not in ir or ir['size'] is None or ir['size'][0] == 0 or ir['size'][1] == 0:
            if len(d) > 193:
                w, h = int(d[192]), int(d[193])
                if w > 0 and h > 0:
                    ir['size'] = [w, h]
        if 'size' not in ir or ir['size'] is None or ir['size'][0] == 0 or ir['size'][1] == 0:
            raise Exception("Could not determine image dimensions")
        profile = ir.get('_profile', {})
        offset_key = profile.get(KEY_IR_DATA_OFFSET, "width")
        # Skip header: that many uint16s before the w*h payload (same rule as CalTempDataRex)
        offset = ir['size'][1] if offset_key == "height" else ir['size'][0]
        n_pixels = ir['size'][0] * ir['size'][1]
        conv = ir.get('conversion') or {}
        # Thermal payload is 16-bit (uint16); keep as float for conversion
        raw_slice = d[offset:offset + n_pixels].astype(np.float64)
        n_actual = raw_slice.size
        if n_actual != n_pixels:
            for w in (320, 384, 640, 256, 160):
                if n_actual % w == 0:
                    h = n_actual // w
                    if 1 <= h <= 10000:
                        ir['size'] = [w, h]
                        ir['IRWidth'], ir['IRHeight'] = w, h
                        n_pixels = n_actual
                        break
        if not conv:
            t_lo = ir.get("TempRangeMin")
            t_hi = ir.get('TempRangeMax')
            if t_lo is not None and t_hi is not None and t_lo < t_hi:
                temp = scale_uint16_to_temperature(raw_slice, float(t_lo), float(t_hi))
            else:
                bg = float(ir.get('BackgroundTemp', ir.get('backgroundtemperature', 20.0)))
                t_lo, t_hi = ir.get('MinTemp'), ir.get('MaxTemp')
                if t_lo is not None and t_hi is not None and t_lo < t_hi:
                    t_lo, t_hi = float(t_lo), float(t_hi)
                else:
                    t_lo, t_hi = bg - 20.0, bg + 35.0
                temp = counts_to_temperature_linear(
                    raw_slice, T_min=t_lo, T_max=t_hi, background_temp=bg
                )
            ir['data'] = np.reshape(temp, (ir['size'][1], ir['size'][0]))
            return
        eps = max(1e-6, min(1.0, ir.get('Emissivity', ir.get('emissivity', 0.95))))
        tau = max(1e-6, min(1.0, ir.get('Transmission', ir.get('transmission', 1.0))))
        tbg4 = UnitConversion.c2k(ir.get('BackgroundTemp', ir.get('backgroundtemperature', 20.0))) ** 4
        raw_temp = []
        for i in d[offset:offset + n_pixels]:
            t_rad = conv.get(int(i))
            if t_rad is None:
                raw_temp.append(np.nan)
                continue
            traw4 = UnitConversion.c2k(t_rad) ** 4
            x = (traw4 - (1 - eps) * tbg4) / (tau * eps)
            if x <= 0:
                raw_temp.append(np.nan)
                continue
            raw_temp.append(UnitConversion.k2c(x ** 0.25))
        ir['data'] = np.reshape(np.array(raw_temp, dtype=float), (ir['size'][1], ir['size'][0]))

    def _read_ir_data_from_caltempdatarex(self, ir: Dict[str, Any], caltemp_path: str):
        """Read thermal from CalTempDataRex; dimensions from metadata, filename hint, then profile."""
        with open(caltemp_path, 'rb') as f:
            raw = f.read()
        profile = ir.get('_profile', {})
        payload_order = []
        seen = set()
        def add(dim):
            if dim and dim not in seen:
                seen.add(dim)
                payload_order.append(dim)
        # 1) Already inferred from metadata or main image filename
        if ir.get('size') and len(ir['size']) >= 2:
            add(tuple(ir['size'][:2]))
        if ir.get('IRWidth') and ir.get('IRHeight'):
            add((int(ir['IRWidth']), int(ir['IRHeight'])))
        # 2) Hint from main image filename 
        for dim in self._get_main_image_dimensions_hint():
            add(dim)
        # 3) Profile (per-model dimensions) as fallback
        for dim in (profile.get(KEY_PAYLOAD_SIZES_ORDER) or []):
            add(dim)
        if profile.get(KEY_THERMAL_DIMENSIONS):
            add(profile[KEY_THERMAL_DIMENSIONS])
        ir_data_offset = profile.get(KEY_IR_DATA_OFFSET)
        arr, w, h = self._extract_thermal_from_caltempdatarex(
            raw, payload_order or [], ir_data_offset=ir_data_offset
        )
        if arr is None or w == 0 or h == 0:
            raise UnsupportedCameraError(
                "Could not extract thermal payload from CalTempDataRex.gpbenc: "
                "no matching dimensions from metadata, main image, or profile."
            )
        ir['size'] = [w, h]
        ir['IRWidth'] = w
        ir['IRHeight'] = h
        ir['VLWidth'] = ir.get('VLWidth') or w
        ir['VLHeight'] = ir.get('VLHeight') or h
        counts_2d = np.reshape(arr.astype(np.float64), (h, w))
        t_lo = ir.get("TempRangeMin")
        t_hi = ir.get("TempRangeMax")
        if t_lo is not None and t_hi is not None and t_lo < t_hi:
            ir["data"] = scale_uint16_to_temperature(counts_2d, float(t_lo), float(t_hi))
        else:
            bg = float(ir.get("BackgroundTemp", ir.get("backgroundtemperature", 20.0)))
            t_lo, t_hi = ir.get("MinTemp"), ir.get("MaxTemp")
            if t_lo is not None and t_hi is not None and t_lo < t_hi:
                t_lo, t_hi = float(t_lo), float(t_hi)
            else:
                t_lo, t_hi = bg - 20.0, bg + 35.0
            ir["data"] = counts_to_temperature_linear(
                counts_2d, T_min=t_lo, T_max=t_hi, background_temp=bg
            )
        ir["thermal_source"] = "CalTempDataRex.gpbenc"

    def _read_thumbnail(self, ir: Dict[str, Any]):
        """Set ir['thumbnail_path'] to first JPG in Thumbnails/ if present."""
        try:
            td = os.path.join(self.temp_dir, "Thumbnails")
            jpgs = [f for f in os.listdir(td) if f.lower().endswith(".jpg")] if os.path.isdir(td) else []
            ir["thumbnail_path"] = os.path.join(td, jpgs[0]) if jpgs else None
        except Exception:
            ir["thumbnail_path"] = None

    def _read_photo(self, ir: Dict[str, Any]):
        """Set ir['photo_path'] to largest JPG in Images/Main/ if present."""
        try:
            main = os.path.join(self.temp_dir, "Images", "Main")
            if os.path.isdir(main):
                best = None
                best_size = 0
                for f in os.listdir(main):
                    if f.lower().endswith(".jpg"):
                        p = os.path.join(main, f)
                        if os.path.getsize(p) > best_size:
                            best, best_size = p, os.path.getsize(p)
                ir["photo_path"] = best
            else:
                ir["photo_path"] = None
        except Exception:
            ir["photo_path"] = None


class IS3Parser:
    """Placeholder for .is3 (video) support."""

    def __init__(self):
        self.temp_dir = "temp"

    def parse(self, file_path: str) -> Dict[str, Any]:
        raise NotImplementedError(".is3 format not implemented")
