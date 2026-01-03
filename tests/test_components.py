#!/usr/bin/env python3
"""
Basic tests for Wand Spellcaster components.

Run with: python -m pytest tests/ -v
"""

import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestSpellRecognizer:
    """Tests for the spell recognition system."""
    
    def test_import(self):
        """Test that spell_recognizer can be imported."""
        from spell_recognizer import SpellRecognizer, Spell
        assert SpellRecognizer is not None
        assert Spell is not None
    
    def test_default_spells_exist(self):
        """Test that default spells are defined."""
        from spell_recognizer import DEFAULT_SPELLS
        
        expected_spells = [
            'alohomora', 'lumos', 'nox', 'incendio',
            'aguamenti', 'wingardium_leviosa', 'arresto_momentum', 'revelio'
        ]
        
        for spell in expected_spells:
            assert spell in DEFAULT_SPELLS, f"Missing spell: {spell}"
    
    def test_spell_dataclass(self):
        """Test Spell dataclass creation."""
        from spell_recognizer import Spell
        
        spell = Spell(
            name="Test Spell",
            incantation="TEST-us",
            confidence=0.95,
            description="A test spell",
            color="#FF0000"
        )
        
        assert spell.name == "Test Spell"
        assert spell.confidence == 0.95


class TestConfigLoader:
    """Tests for configuration loading."""
    
    def test_import(self):
        """Test that config_loader can be imported."""
        from config_loader import Config
        assert Config is not None
    
    def test_defaults(self):
        """Test that default configuration is valid."""
        from config_loader import Config
        
        config = Config.defaults()
        assert config.camera_id == 0
        assert config.ir_threshold == 200
        assert config.min_confidence == 0.7
        assert config.display_type == "auto"
    
    def test_validation(self):
        """Test configuration validation."""
        from config_loader import Config
        
        config = Config.defaults()
        assert config.validate() == True
        
        # Test invalid threshold
        config.ir_threshold = 300
        with pytest.raises(ValueError):
            config.validate()


class TestWandTracker:
    """Tests for wand tracking (mocked camera)."""
    
    def test_import(self):
        """Test that wand_tracker can be imported."""
        from wand_tracker import WandTracker, TrackingPoint
        assert WandTracker is not None
        assert TrackingPoint is not None
    
    def test_tracking_point(self):
        """Test TrackingPoint dataclass."""
        from wand_tracker import TrackingPoint
        
        point = TrackingPoint(x=100, y=200, timestamp=1234567890.0, brightness=255.0)
        assert point.x == 100
        assert point.y == 200


class TestDisplayManager:
    """Tests for display management."""
    
    def test_import(self):
        """Test that display_manager can be imported."""
        from display_manager import DisplayManager, Theme, THEMES
        assert DisplayManager is not None
        assert Theme is not None
    
    def test_themes_exist(self):
        """Test that all house themes exist."""
        from display_manager import THEMES
        
        expected_themes = ['default', 'gryffindor', 'slytherin', 'ravenclaw', 'hufflepuff']
        for theme in expected_themes:
            assert theme in THEMES, f"Missing theme: {theme}"


# =============================================================================
# Integration Tests (require hardware - skip if not available)
# =============================================================================

@pytest.mark.skipif(
    not os.path.exists('/dev/video0'),
    reason="No camera available"
)
class TestHardwareIntegration:
    """Tests that require actual hardware."""
    
    def test_camera_capture(self):
        """Test camera can capture frames."""
        from wand_tracker import WandTracker
        
        tracker = WandTracker(camera_id=0)
        frame = tracker.capture_frame()
        
        assert frame is not None
        assert frame.shape[0] > 0  # Has height
        assert frame.shape[1] > 0  # Has width
        
        tracker.release()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
