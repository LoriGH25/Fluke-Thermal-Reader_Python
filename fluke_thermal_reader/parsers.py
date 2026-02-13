"""
Parser for Fluke thermal files (.is2 format).

This module provides a clean implementation for reading Fluke .is2 thermal image files.

"""

import os
import shutil
import struct
import numpy as np
import json
from zipfile import ZipFile
from typing import Dict, Any
from struct import unpack
from .utilities import UnitConversion, calc_equation


class IS2Parser:
    """
    Parser for .is2 files (Fluke thermal format).
    
    This class handles the extraction and analysis of thermal data
    from Fluke .is2 files, including metadata, calibration and images.
    """
    
    def __init__(self):
        """Initialize the parser with a temporary directory."""
        self.temp_dir = 'temp_fluke_reader'
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a .is2 file and return a dictionary with all extracted data.
        
        Args:
            file_path: Path to the .is2 file
            
        Returns:
            Dict: Dictionary containing all thermal data, metadata and images
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract the ZIP file
        with ZipFile(file_path, 'r') as zipObj:
            zipObj.extractall(self.temp_dir)
        
        try:
            ir = {}
            ir['FileName'] = os.path.split(file_path)[1]
            
            # Read camera info (try both old and new format)
            self._read_camera_info(ir)
            
            # Read all information from ImageProperties.json (if available)
            self._read_image_properties(ir)
            
            # Read calibration data
            self._read_calibration_data(ir)
            
            # Read IR image info for additional parameters
            self._read_ir_image_info(ir)
            
            # Read IR thermal data
            self._read_ir_data(ir)
            
            # Read thumbnail
            self._read_thumbnail(ir)
            
            # Read visible image
            self._read_photo(ir)
            
            return ir
            
        finally:
            # Clean up temporary directory
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    def _read_camera_info(self, ir: Dict[str, Any]):
        """Read camera information from CameraInfo.gpbenc"""
        try:
            camera_info_path = os.path.join(self.temp_dir, 'CameraInfo.gpbenc')
            if os.path.exists(camera_info_path):
                with open(camera_info_path, 'r', encoding='latin-1') as f:
                    camera_info = f.read()
                
                # Extract camera information
                if len(camera_info) >= 124:
                    ir['CameraManufacturer'] = str(camera_info[76:94]).strip()
                    ir['CameraModel'] = str(camera_info[97:103]).strip()
                    ir['EngineSerial'] = str(camera_info[104:112]).strip()
                    ir['CameraSerial'] = str(camera_info[115:124]).strip()
        except Exception:
            # If CameraInfo.gpbenc fails, values will be set from ImageProperties.json
            pass
    
    def _read_image_properties(self, ir: Dict[str, Any]):
        """Read all properties from ImageProperties.json."""
        try:
            imageprops_path = os.path.join(self.temp_dir, 'ImageProperties.json')
            if os.path.exists(imageprops_path):
                # Try different encodings
                for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
                    try:
                        with open(imageprops_path, 'r', encoding=encoding) as f:
                            props = json.load(f)
                        break
                    except:
                        continue
                else:
                    raise Exception("Could not decode ImageProperties.json with any encoding")
                
                # Camera information (overrides CameraInfo.gpbenc if present)
                if 'IRPROP_THERMAL_IMAGER_MAKE' in props:
                    ir['CameraManufacturer'] = props.get('IRPROP_THERMAL_IMAGER_MAKE', 'Unknown')
                if 'IRPROP_THERMAL_IMAGER_MODEL' in props:
                    ir['CameraModel'] = props.get('IRPROP_THERMAL_IMAGER_MODEL', 'Unknown').strip('"')
                if 'IRPROP_THERMAL_IMAGER_SN' in props:
                    ir['CameraSerial'] = props.get('IRPROP_THERMAL_IMAGER_SN', 'Unknown').strip('"')
                    if 'EngineSerial' not in ir:
                        ir['EngineSerial'] = ir['CameraSerial']
                
                ir['IRLenses'] = props.get('IRPROP_THERMAL_IMAGER_IR_LENSES', '').strip('"')
                ir['IRLensesSerial'] = props.get('IRPROP_THERMAL_IMAGER_IR_LENSES_SN', '').strip('"')
                ir['CalibrationDate'] = props.get('IRPROP_THERMAL_IMAGER_CALIBRATION_DATE', '').strip('"')
                
                # Image dimensions
                ir['IRWidth'] = int(props.get('IRPROP_IR_SENSOR_WIDTH', 640))
                ir['IRHeight'] = int(props.get('IRPROP_IR_SENSOR_HEIGHT', 480))
                ir['VLWidth'] = int(props.get('IRPROP_VL_SENSOR_WIDTH', 640))
                ir['VLHeight'] = int(props.get('IRPROP_VL_SENSOR_HEIGHT', 480))
                
                # Set size for compatibility
                ir['size'] = [ir['IRWidth'], ir['IRHeight']]
                
                # Capture information
                ir['CaptureDateTime'] = props.get('IRPROP_THERMAL_IMAGE_CAPTURE_DATE_TIME', '')
                
                # Temperature information
                ir['MinTemp'] = float(props.get('IRPROP_THERMAL_IMAGE_MIN_TEMP_C', 0))
                ir['MaxTemp'] = float(props.get('IRPROP_THERMAL_IMAGE_MAX_TEMP_C', 0))
                ir['AvgTemp'] = float(props.get('IRPROP_THERMAL_IMAGE_AVG_TEMP_C', 0))
                ir['CenterTemp'] = float(props.get('IRPROP_THERMAL_IMAGE_CENTER_POINT_TEMP_C', 0))
                ir['BackgroundTemp'] = float(props.get('IRPROP_THERMAL_IMAGE_BG_TEMP_C', 0))
                ir['Emissivity'] = float(props.get('IRPROP_THERMAL_IMAGE_EMISSIVITY', 0.95))
                                
                # Transmission if present
                tr_val = props.get('IRPROP_THERMAL_IMAGE_TRANSMISSIVITY', None)
                if tr_val is not None:
                    try:
                        ir['transmission'] = float(tr_val)
                    except Exception:
                        pass
                
                # Additional properties
                ir['Title'] = props.get('IRPROP_THERMAL_IMAGE_TITLE', '').strip('"')
                ir['Comments'] = props.get('IRPROP_THERMAL_IMAGE_COMMENTS', '').strip('"')
                ir['ContainsAnnotations'] = props.get('IRPROP_THERMAL_IMAGE_CONTAINS_ANNOTATIONS', 'False') == 'True'
                ir['ContainsAudio'] = props.get('IRPROP_THERMAL_IMAGE_CONTAINS_AUDIO', 'False') == 'True'
                ir['ContainsCNXReadings'] = props.get('IRPROP_THERMAL_IMAGE_CONTAINS_CNX_READINGS', 'False') == 'True'
        except Exception as e:
            # If ImageProperties.json doesn't exist or fails, continue with other methods
            pass
    
    def _read_calibration_data(self, ir: Dict[str, Any]):
        """
        Read calibration data and build conversion lookup table.
        
        Finds calibration curves using magic bytes pattern (74, 25, 13) in CalibrationData.gpbenc
        and builds a LUT for count->temperature conversion.
        
        CRITICAL: Each file has multiple sets of calibration curves for different temperature ranges.
        The 'range' value (cal_data[18]) indicates which set to use. We need to select
        the correct set based on the range value and the coefficient magnitudes.
        """
        try:
            cal_data = np.fromfile(os.path.join(self.temp_dir, 'CalibrationData.gpbenc'), dtype=np.uint8)
            ir['range'] = int(cal_data[18])  # Auto 1 or 2, maybe more?
            ir['conversion'] = {}
            for i in range(len(cal_data)):
                # Every part of the conversion function starts with this 3 bytes
                if cal_data[i] == 74 and cal_data[i + 1] == 25 and cal_data[i + 2] == 13:
                    curve_part = cal_data[i + 3:i + 27]
                    temp_range = np.array([unpack('<f', curve_part[:4])[0], unpack('<f', curve_part[5:9])[0]])
                    if temp_range[0] >= -180:
                        equation_variables = {'a': unpack('<f', curve_part[20:24])[0],
                                            'b': unpack('<f', curve_part[15:19])[0],
                                            'c': unpack('<f', curve_part[10:14])[0]}
                        data_range = calc_equation(
                            [equation_variables['a'], equation_variables['b'], equation_variables['c']],
                            temp_range)
                        data_range_int = [int(data_range[0]) + (data_range[0] % 1 > 0),
                                        int(data_range[1]) + (data_range[1] % 1 > 0)]
                        for j in range(data_range_int[0], data_range_int[1]):
                            # Fluke uses a quadratic function with temperature as input, and IR-data as output. We want
                            # data as input and temperature as output, so the abc-equation is used.
                            ir['conversion'][j] = ((-equation_variables['b']
                                                        + np.sqrt(equation_variables['b'] ** 2 - 4
                                                                * equation_variables['a']
                                                                * (equation_variables['c'] - j)))
                                                        / (2 * equation_variables['a']))
            if not ir['conversion']:
                raise Exception("No calibration coefficients found in CalibrationData.gpbenc")
                
        except Exception as e:
            raise Exception(f"Cannot read calibration data: {e}")
    
    def _read_ir_image_info(self, ir: Dict[str, Any]):
        """
        Read IR image information for additional parameters.
        
        Note: For newer Fluke files, ImageProperties.json is more reliable.
        IRImageInfo.gpbenc offsets may vary between camera models.
        """
        ir_image_info = np.fromfile(os.path.join(self.temp_dir, 'Images', 'Main', 'IRImageInfo.gpbenc'), dtype=np.uint8)
        transmission = unpack('<f', ir_image_info[43:47])[0]
        emissivity = unpack('<f', ir_image_info[33:37])[0]
        backgroundtemperature = unpack('<f', ir_image_info[38:42])[0]
        
        if "Emissivity" not in ir:
            ir['Emissivity'] = emissivity
        if 'Transmission' not in ir:
            ir['Transmission'] = transmission if (0 < transmission <= 1) else 1.0
        if "BackgroundTemp" not in ir:
            ir['BackgroundTemp'] = backgroundtemperature
            
    def _read_ir_data(self, ir: Dict[str, Any]):
        """
        Read IR thermal data and convert to temperature.
        
        1. Read IR.data as uint16
        2. Get dimensions from ImageProperties.json or from d[192], d[193] in IR.data
        3. Thermal data starts at offset = height (size[1])
        4. Convert counts to temperature using LUT
        5. Apply emissivity and reflected-background correction formula
        """
        ir_data_path = os.path.join(self.temp_dir, 'Images', 'Main', 'IR.data')
        
        
        d = np.fromfile(ir_data_path, dtype=np.uint16)
               
        # Get dimensions: prefer ImageProperties.json, else read from IR.data header
        if 'size' not in ir or ir['size'] is None or ir['size'][0] == 0 or ir['size'][1] == 0:
            # Read width/height from IR.data (bytes 192-193)
            if len(d) > 193:
                width_from_data = int(d[192])
                height_from_data = int(d[193])
                if width_from_data > 0 and height_from_data > 0:
                    ir['size'] = [width_from_data, height_from_data]
        
        # Ensure we have valid dimensions
        if 'size' not in ir or ir['size'] is None or ir['size'][0] == 0 or ir['size'][1] == 0:
            raise Exception("Could not determine image dimensions")
        
        raw_temp = []
        # Data offset = height (size[0])
        offset = ir['size'][0]
        n_pixels = ir['size'][0] * ir['size'][1]
        conv = ir['conversion']
        eps = max(1e-6, min(1.0, ir.get('Emissivity', ir.get('emissivity', 0.95))))
        tau = max(1e-6, min(1.0, ir.get('Transmission', ir.get('transmission', 1.0))))
        tbg4 = UnitConversion.c2k(ir.get('BackgroundTemp', ir.get('backgroundtemperature', 20.0))) ** 4
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
            treal = UnitConversion.k2c(x ** 0.25)
            raw_temp.append(treal)        
        
        ir['data'] = np.reshape(np.array(raw_temp, dtype=float), (ir['size'][1], ir['size'][0])) 
        
        
    
    def _read_thumbnail(self, ir: Dict[str, Any]):
        """Read the thumbnail path (image loading is optional)."""
        try:
            thumbnails_dir = os.path.join(self.temp_dir, 'Thumbnails')
            if os.path.exists(thumbnails_dir):
                thumbnails_list = [each for each in os.listdir(thumbnails_dir) if each.endswith('.jpg')]
                if thumbnails_list:
                    # Return the path to the thumbnail instead of loading it
                    ir['thumbnail_path'] = os.path.join(thumbnails_dir, thumbnails_list[0])
                    ir['thumbnail'] = None  # Set to None to indicate it needs to be loaded separately
                else:
                    ir['thumbnail_path'] = None
                    ir['thumbnail'] = None
            else:
                ir['thumbnail_path'] = None
                ir['thumbnail'] = None
        except Exception as e:
            ir['thumbnail_path'] = None
            ir['thumbnail'] = None
    
    def _read_photo(self, ir: Dict[str, Any]):
        """Read the visible image path (image loading is optional)."""
        try:
            images_dir = os.path.join(self.temp_dir, 'Images', 'Main')
            if os.path.exists(images_dir):
                image = ''
                maxsize = 0
                for each in os.listdir(images_dir):
                    if each.endswith('.jpg'):
                        # Take the biggest image, the smaller image is cropped from the bigger one
                        filesize = os.path.getsize(os.path.join(images_dir, each))
                        if filesize > maxsize:
                            image = each
                            maxsize = filesize
                if image:
                    # Return the path to the photo instead of loading it
                    ir['photo_path'] = os.path.join(images_dir, image)
                    ir['photo'] = None  # Set to None to indicate it needs to be loaded separately
                else:
                    ir['photo_path'] = None
                    ir['photo'] = None
            else:
                ir['photo_path'] = None
                ir['photo'] = None
        except Exception as e:
            ir['photo_path'] = None
            ir['photo'] = None


class IS3Parser:
    """Parser for .is3 files (Fluke thermal format for video)."""
    
    def __init__(self):
        self.temp_dir = 'temp'
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a .is3 file and return a dictionary with all extracted data.
        
        Args:
            file_path: Path to the .is3 file
            
        Returns:
            Dict: Dictionary containing all thermal data
        """
        # For now, .is3 support is not implemented
        # This is a placeholder for future development
        raise NotImplementedError(".is3 format support is not yet implemented")
