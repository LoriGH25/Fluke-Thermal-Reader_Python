"""
Parser for Fluke thermal files (.is2 and .is3).
"""

import os
import re
import shutil
import struct
import numpy as np
import json
from zipfile import ZipFile
from typing import Dict, Any


def calc_equation(z, x):
    """
    Calculate a polynomial of degree n-1 using coefficients z.
    
    Args:
        z: List of polynomial coefficients [a0, a1, a2, ...]
        x: Input value for calculation
        
    Returns:
        float: Polynomial result y = a0 + a1*x + a2*x^2 + ...
    """
    k = range(0, len(z))
    m = k[::-1]
    y = 0
    for i in k:
        y += np.multiply(z[i], x ** m[i])
    return y


class IS2Parser:
    """
    Parser for .is2 files (Fluke thermal format).
    
    This class handles the extraction and analysis of thermal data
    from Fluke .is2 files, including metadata, calibration and images.
    """
    
    def __init__(self):
        """Initialize the parser with a temporary directory."""
        self.temp_dir = 'temp'
    
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
            
            # Read all information from ImageProperties.json
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
    
    def _get_fusion_offset(self, camera_model: str = "") -> int:
        """
        Read the fusion offset from PrivateProperties.xml file.
        
        Args:
            camera_model: Camera model for specific rules
            
        Returns:
            int: Correct fusion offset for the camera model
        """
        try:
            private_props_path = os.path.join(self.temp_dir, 'PrivateProperties.xml')
            if not os.path.exists(private_props_path):
                return 0
                
            with open(private_props_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse the OriginalFusionOffset value
            match = re.search(r'"OriginalFusionOffset":"(\d+)@\d+"', content)
            if match:
                offset = int(match.group(1))
                # Different rules for different camera models
                if 'Ti480P' in str(camera_model):
                    final_offset = offset + 80
                elif 'Ti300' in str(camera_model):
                    final_offset = offset-40
                else:
                    final_offset = offset
                return final_offset
            else:
                return 0
        except Exception as e:
            return 0

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
                
                # Camera information
                ir['CameraManufacturer'] = props.get('IRPROP_THERMAL_IMAGER_MAKE', 'Unknown')
                ir['CameraModel'] = props.get('IRPROP_THERMAL_IMAGER_MODEL', 'Unknown').strip('"')
                ir['CameraSerial'] = props.get('IRPROP_THERMAL_IMAGER_SN', 'Unknown').strip('"')
                ir['EngineSerial'] = ir['CameraSerial']  # Use same as camera serial
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
                
                # Additional properties
                ir['Title'] = props.get('IRPROP_THERMAL_IMAGE_TITLE', '').strip('"')
                ir['Comments'] = props.get('IRPROP_THERMAL_IMAGE_COMMENTS', '').strip('"')
                ir['ContainsAnnotations'] = props.get('IRPROP_THERMAL_IMAGE_CONTAINS_ANNOTATIONS', 'False') == 'True'
                ir['ContainsAudio'] = props.get('IRPROP_THERMAL_IMAGE_CONTAINS_AUDIO', 'False') == 'True'
                ir['ContainsCNXReadings'] = props.get('IRPROP_THERMAL_IMAGE_CONTAINS_CNX_READINGS', 'False') == 'True'
                
                
                
            else:
                raise FileNotFoundError("ImageProperties.json not found")
                
        except Exception as e:
            raise Exception(f"Cannot read ImageProperties.json: {e}")
    
    def _read_calibration_data(self, ir: Dict[str, Any]):
        """Read calibration data."""
        try:
            cal_data = np.fromfile(os.path.join(self.temp_dir, 'CalibrationData.gpbenc'), dtype=np.uint8)
            ir['range'] = int(cal_data[18])
            ir['conversion'] = {}
            
            for i in range(len(cal_data)):
                if cal_data[i] == 74 and cal_data[i + 1] == 25 and cal_data[i + 2] == 13:
                    curve_part = cal_data[i + 3:i + 27]
                    temp_range = np.array([struct.unpack('<f', curve_part[:4])[0], 
                                         struct.unpack('<f', curve_part[5:9])[0]])
                    if temp_range[0] >= -180:
                        equation_variables = {'a': struct.unpack('<f', curve_part[20:24])[0],
                                            'b': struct.unpack('<f', curve_part[15:19])[0],
                                            'c': struct.unpack('<f', curve_part[10:14])[0]}
                        data_range = calc_equation(
                            [equation_variables['a'], equation_variables['b'], equation_variables['c']],
                            temp_range)
                        data_range_int = [int(data_range[0]) + (data_range[0] % 1 > 0), 
                                        int(data_range[1]) + (data_range[1] % 1 > 0)]
                        for j in range(data_range_int[0], data_range_int[1]):
                            ir['conversion'][j] = (-equation_variables['b'] + 
                                                np.sqrt(equation_variables['b'] ** 2 - 
                                                       4 * equation_variables['a'] * 
                                                       (equation_variables['c'] - j))) / \
                                               (2 * equation_variables['a'])
        except Exception as e:
            raise Exception(f"Cannot read calibration data: {e}")
    
    def _read_ir_image_info(self, ir: Dict[str, Any]):
        """Read IR image information for additional parameters."""
        try:
            ir_image_info = np.fromfile(os.path.join(self.temp_dir, 'Images', 'Main', 'IRImageInfo.gpbenc'), dtype=np.uint8)
            
            # Read additional parameters if available
            if len(ir_image_info) > 48:
                # These might override the JSON values if they exist
                if 'emissivity' not in ir or ir['emissivity'] == 0:
                    ir['emissivity'] = struct.unpack('<f', ir_image_info[34:38])[0]
                if 'backgroundtemperature' not in ir or ir['backgroundtemperature'] == 0:
                    ir['backgroundtemperature'] = struct.unpack('<f', ir_image_info[39:43])[0]
                if 'transmission' not in ir:
                    ir['transmission'] = struct.unpack('<f', ir_image_info[44:48])[0]
        except Exception as e:
            # Use values from ImageProperties.json if available
            if 'transmission' not in ir:
                ir['transmission'] = 1.0
    
    def _read_ir_data(self, ir: Dict[str, Any]):
        """Read IR thermal data using ONLY JSON information."""
        ir_data_path = os.path.join(self.temp_dir, 'Images', 'Main', 'IR.data')
        if not os.path.exists(ir_data_path):
            ir['data'] = np.array([])
            return
            
        d = np.fromfile(ir_data_path, dtype=np.uint16)
        
        if len(d) < 200:
            ir['data'] = np.array([])
            return
        
        # Use ONLY JSON dimensions - no fallback, no other sources
        width = ir['IRWidth']
        height = ir['IRHeight']
        
        # Use height as offset (from original Fluke method)
        index = height
        raw_temp = []
        
        # Read data
        for i in d[index:index + (width * height)]:
            if i > 0 and i in ir['conversion']:
                # Use Fluke conversion formula
                temp = (ir['conversion'][i] - (2 - ir['transmission'] - ir['emissivity']) * ir['backgroundtemperature']) / (ir['transmission'] * ir['emissivity'])
                raw_temp.append(temp)
            else:
                raw_temp.append(0.0)
        
        if len(raw_temp) > 0:
            # Reshape to [height, width] to match the expected format
            temp_array = np.reshape(raw_temp, [height, width])
            
            # Fix horizontal shift: read OriginalFusionOffset from PrivateProperties.xml
            shift_offset = self._get_fusion_offset(ir.get('CameraModel', ''))
            if shift_offset != 0:
                for row in range(height):
                    # Apply the fusion offset shift in negative direction
                    temp_array[row] = np.roll(temp_array[row], -shift_offset)
            
            ir['data'] = temp_array
        else:
            ir['data'] = np.array([])
    
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