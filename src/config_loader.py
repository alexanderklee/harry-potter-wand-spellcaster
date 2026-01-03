#!/usr/bin/env python3
"""
Configuration Loader Module
===========================
Handles loading and validation of configuration settings.

Configuration can be loaded from:
- YAML files
- Environment variables
- Command line arguments (handled by main.py)
- Defaults
"""

import os
import logging
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """
    Application configuration.
    
    All settings needed to run the Wand Spellcaster system.
    """
    
    # Camera settings
    camera_id: int = 0
    camera_resolution: Tuple[int, int] = (640, 480)
    ir_threshold: int = 200
    min_blob_area: int = 50
    max_blob_area: int = 5000
    
    # Gesture recognition
    min_gesture_points: int = 15
    gesture_timeout_frames: int = 15
    min_confidence: float = 0.7
    model_path: str = "models/spell_classifier.pkl"
    
    # Display settings
    display_type: str = "auto"  # auto, pygame, oled, headless
    display_resolution: Tuple[int, int] = (800, 480)
    theme: str = "default"
    fullscreen: bool = False
    
    # Spell definitions
    spells: Dict[str, Any] = field(default_factory=dict)
    
    # ========================================================================
    # PHASE 2 PLACEHOLDER: Voice settings
    # ========================================================================
    # tts_engine: str = "espeak"  # espeak, pico, festival
    # voice_name: str = "en"
    # speech_rate: int = 150
    # ========================================================================
    
    # ========================================================================
    # PHASE 2 PLACEHOLDER: Multiplayer settings
    # ========================================================================
    # multiplayer_port: int = 5000
    # sync_timeout: float = 5.0
    # duel_countdown: int = 3
    # ========================================================================
    
    @classmethod
    def load(cls, path: str) -> 'Config':
        """
        Load configuration from a YAML file.
        
        Args:
            path: Path to YAML configuration file
            
        Returns:
            Config object with loaded settings
            
        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        import yaml
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        # Parse nested structures
        camera = data.get('camera', {})
        gesture = data.get('gesture', {})
        display = data.get('display', {})
        
        config = cls(
            # Camera
            camera_id=camera.get('id', cls.camera_id),
            camera_resolution=tuple(camera.get('resolution', list(cls.camera_resolution))),
            ir_threshold=camera.get('ir_threshold', cls.ir_threshold),
            min_blob_area=camera.get('min_blob_area', cls.min_blob_area),
            max_blob_area=camera.get('max_blob_area', cls.max_blob_area),
            
            # Gesture
            min_gesture_points=gesture.get('min_points', cls.min_gesture_points),
            gesture_timeout_frames=gesture.get('timeout_frames', cls.gesture_timeout_frames),
            min_confidence=gesture.get('min_confidence', cls.min_confidence),
            model_path=gesture.get('model_path', cls.model_path),
            
            # Display
            display_type=display.get('type', cls.display_type),
            display_resolution=tuple(display.get('resolution', list(cls.display_resolution))),
            theme=display.get('theme', cls.theme),
            fullscreen=display.get('fullscreen', cls.fullscreen),
            
            # Spells
            spells=data.get('spells', {}),
        )
        
        # Override with environment variables
        config._load_env_overrides()
        
        logger.info(f"Loaded configuration from {path}")
        return config
    
    @classmethod
    def defaults(cls) -> 'Config':
        """Return a Config with all default values."""
        return cls()
    
    def _load_env_overrides(self):
        """Override config values from environment variables."""
        env_mappings = {
            'WAND_CAMERA_ID': ('camera_id', int),
            'WAND_IR_THRESHOLD': ('ir_threshold', int),
            'WAND_MIN_CONFIDENCE': ('min_confidence', float),
            'WAND_DISPLAY_TYPE': ('display_type', str),
            'WAND_THEME': ('theme', str),
        }
        
        for env_var, (attr, type_fn) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    setattr(self, attr, type_fn(value))
                    logger.debug(f"Override from env: {attr}={value}")
                except ValueError:
                    logger.warning(f"Invalid value for {env_var}: {value}")
    
    def save(self, path: str):
        """
        Save configuration to a YAML file.
        
        Args:
            path: Path to save configuration
        """
        import yaml
        
        data = {
            'camera': {
                'id': self.camera_id,
                'resolution': list(self.camera_resolution),
                'ir_threshold': self.ir_threshold,
                'min_blob_area': self.min_blob_area,
                'max_blob_area': self.max_blob_area,
            },
            'gesture': {
                'min_points': self.min_gesture_points,
                'timeout_frames': self.gesture_timeout_frames,
                'min_confidence': self.min_confidence,
                'model_path': self.model_path,
            },
            'display': {
                'type': self.display_type,
                'resolution': list(self.display_resolution),
                'theme': self.theme,
                'fullscreen': self.fullscreen,
            },
        }
        
        if self.spells:
            data['spells'] = self.spells
        
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        
        logger.info(f"Saved configuration to {path}")
    
    def validate(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if self.ir_threshold < 0 or self.ir_threshold > 255:
            raise ValueError(f"ir_threshold must be 0-255, got {self.ir_threshold}")
        
        if self.min_confidence < 0 or self.min_confidence > 1:
            raise ValueError(f"min_confidence must be 0-1, got {self.min_confidence}")
        
        if self.min_blob_area >= self.max_blob_area:
            raise ValueError("min_blob_area must be less than max_blob_area")
        
        if self.camera_resolution[0] <= 0 or self.camera_resolution[1] <= 0:
            raise ValueError(f"Invalid camera resolution: {self.camera_resolution}")
        
        return True
