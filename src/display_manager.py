#!/usr/bin/env python3
"""
Display Manager Module
======================
Handles visual output for the Wand Spellcaster system.

Supports multiple display types:
- HDMI/Desktop: Full pygame-based display
- SSD1306 OLED: Small 128x64 I2C display
- ST7789 TFT: 240x240 SPI display
- Headless: No display (logging only)

The display shows:
- Ready/waiting state
- Tracking feedback (dots accumulating)
- Detected spell name with visual effects
- Error/unrecognized states
"""

import time
import logging
from typing import Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import os

logger = logging.getLogger(__name__)


@dataclass
class Theme:
    """Display color theme."""
    background: Tuple[int, int, int] = (10, 10, 30)  # Dark blue-black
    text_primary: Tuple[int, int, int] = (255, 255, 255)
    text_secondary: Tuple[int, int, int] = (150, 150, 170)
    accent: Tuple[int, int, int] = (255, 215, 0)  # Gold
    success: Tuple[int, int, int] = (50, 205, 50)  # Green
    error: Tuple[int, int, int] = (220, 20, 60)  # Red
    tracking: Tuple[int, int, int] = (100, 149, 237)  # Cornflower blue


# Predefined themes
THEMES = {
    "gryffindor": Theme(
        background=(50, 10, 10),
        accent=(255, 215, 0),
        text_primary=(255, 255, 255),
    ),
    "slytherin": Theme(
        background=(10, 40, 20),
        accent=(192, 192, 192),
        text_primary=(255, 255, 255),
    ),
    "ravenclaw": Theme(
        background=(10, 20, 50),
        accent=(205, 127, 50),
        text_primary=(255, 255, 255),
    ),
    "hufflepuff": Theme(
        background=(40, 30, 10),
        accent=(255, 215, 0),
        text_primary=(0, 0, 0),
    ),
    "default": Theme(),
}


class BaseDisplay(ABC):
    """Abstract base class for display implementations."""
    
    @abstractmethod
    def show_ready_screen(self):
        """Show the ready/waiting state."""
        pass
    
    @abstractmethod
    def show_tracking(self, point_count: int):
        """Show tracking feedback."""
        pass
    
    @abstractmethod
    def show_spell(self, spell):
        """Show detected spell with effects."""
        pass
    
    @abstractmethod
    def show_unrecognized(self):
        """Show unrecognized gesture message."""
        pass
    
    @abstractmethod
    def show_calibration_instructions(self):
        """Show calibration mode instructions."""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Clean up display resources."""
        pass


class HeadlessDisplay(BaseDisplay):
    """Headless display that only logs to console."""
    
    def show_ready_screen(self):
        logger.info("Display: Ready - Wave your wand!")
    
    def show_tracking(self, point_count: int):
        if point_count % 10 == 0:  # Log every 10 points
            logger.debug(f"Display: Tracking... {point_count} points")
    
    def show_spell(self, spell):
        logger.info(f"Display: ✨ {spell.name} ✨ (confidence: {spell.confidence:.1%})")
        logger.info(f"         \"{spell.incantation}\"")
    
    def show_unrecognized(self):
        logger.info("Display: Gesture not recognized")
    
    def show_calibration_instructions(self):
        logger.info("Display: Calibration mode - adjust threshold until wand is detected")
    
    def cleanup(self):
        pass


class PygameDisplay(BaseDisplay):
    """Full desktop display using pygame."""
    
    def __init__(self, resolution: Tuple[int, int], theme: Theme, fullscreen: bool = False):
        self.resolution = resolution
        self.theme = theme
        self.fullscreen = fullscreen
        
        # Initialize pygame
        import pygame
        pygame.init()
        pygame.font.init()
        
        self.pygame = pygame
        
        # Set up display
        flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode(resolution, flags)
        pygame.display.set_caption("Wand Spellcaster")
        
        # Load fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # Animation state
        self.spell_display_time = 0
        self.last_spell = None
        
        logger.info(f"Pygame display initialized at {resolution}")
    
    def _clear(self):
        """Clear screen with background color."""
        self.screen.fill(self.theme.background)
    
    def _center_text(self, text: str, font, color, y_offset: int = 0):
        """Draw centered text."""
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(self.resolution[0] // 2, self.resolution[1] // 2 + y_offset))
        self.screen.blit(surface, rect)
    
    def _update(self):
        """Update display and handle events."""
        self.pygame.display.flip()
        
        # Handle quit events
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                raise SystemExit
            if event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_ESCAPE:
                raise SystemExit
    
    def show_ready_screen(self):
        self._clear()
        
        # Title
        self._center_text("WAND SPELLCASTER", self.font_large, self.theme.accent, -50)
        
        # Subtitle
        self._center_text("Wave your wand to cast a spell", self.font_medium, self.theme.text_secondary, 20)
        
        # Decorative wand icon (simple line)
        cx, cy = self.resolution[0] // 2, self.resolution[1] // 2 + 100
        self.pygame.draw.line(self.screen, self.theme.accent, (cx - 40, cy + 20), (cx + 40, cy - 20), 4)
        self.pygame.draw.circle(self.screen, self.theme.text_primary, (cx + 42, cy - 22), 6)
        
        self._update()
    
    def show_tracking(self, point_count: int):
        self._clear()
        
        # Title
        self._center_text("CASTING...", self.font_large, self.theme.tracking, -30)
        
        # Progress dots
        max_dots = 20
        dots = min(point_count // 3, max_dots)
        dot_str = "●" * dots + "○" * (max_dots - dots)
        self._center_text(dot_str, self.font_small, self.theme.text_secondary, 30)
        
        self._update()
    
    def show_spell(self, spell):
        self._clear()
        
        # Parse spell color
        try:
            color = tuple(int(spell.color[i:i+2], 16) for i in (1, 3, 5))
        except:
            color = self.theme.accent
        
        # Spell name with glow effect (draw multiple times offset)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            text = self.font_large.render(spell.name.upper(), True, self.theme.background)
            rect = text.get_rect(center=(
                self.resolution[0] // 2 + offset[0],
                self.resolution[1] // 2 - 40 + offset[1]
            ))
            self.screen.blit(text, rect)
        
        self._center_text(spell.name.upper(), self.font_large, color, -40)
        
        # Incantation
        self._center_text(f'"{spell.incantation}"', self.font_medium, self.theme.text_secondary, 30)
        
        # Confidence bar
        bar_width = 200
        bar_height = 10
        bar_x = (self.resolution[0] - bar_width) // 2
        bar_y = self.resolution[1] // 2 + 80
        
        self.pygame.draw.rect(self.screen, self.theme.text_secondary, 
                             (bar_x, bar_y, bar_width, bar_height), 1)
        self.pygame.draw.rect(self.screen, self.theme.success,
                             (bar_x, bar_y, int(bar_width * spell.confidence), bar_height))
        
        self._center_text(f"Confidence: {spell.confidence:.0%}", self.font_small, 
                         self.theme.text_secondary, 110)
        
        self._update()
        
        # Hold display for a moment
        time.sleep(2)
    
    def show_unrecognized(self):
        self._clear()
        self._center_text("Spell not recognized", self.font_medium, self.theme.error, -20)
        self._center_text("Try again!", self.font_small, self.theme.text_secondary, 30)
        self._update()
        time.sleep(1)
    
    def show_calibration_instructions(self):
        self._clear()
        self._center_text("CALIBRATION MODE", self.font_large, self.theme.accent, -60)
        self._center_text("Adjust the threshold slider until", self.font_small, self.theme.text_secondary, -10)
        self._center_text("your wand tip is detected", self.font_small, self.theme.text_secondary, 20)
        self._center_text("Press 'Q' to save and exit", self.font_small, self.theme.text_primary, 60)
        self._update()
    
    # ========================================================================
    # PHASE 2 PLACEHOLDER: Multiplayer Display Methods
    # ========================================================================
    # def show_waiting_for_opponent(self):
    #     """Show waiting for opponent to connect."""
    #     self._clear()
    #     self._center_text("Waiting for opponent...", self.font_medium, self.theme.text_secondary, 0)
    #     self._update()
    # 
    # def show_duel_countdown(self, seconds: int):
    #     """Show countdown before duel."""
    #     self._clear()
    #     self._center_text(str(seconds), self.font_large, self.theme.accent, 0)
    #     self._update()
    # 
    # def show_opponent_spell(self, spell):
    #     """Show what spell the opponent cast."""
    #     # Display in corner or split screen
    #     pass
    # 
    # def show_duel_result(self, result: dict):
    #     """Show the result of a duel."""
    #     self._clear()
    #     winner = result['winner']
    #     if winner == self.player_id:
    #         self._center_text("YOU WIN!", self.font_large, self.theme.success, -30)
    #     else:
    #         self._center_text("YOU LOSE!", self.font_large, self.theme.error, -30)
    #     self._update()
    #     time.sleep(2)
    # ========================================================================
    
    def cleanup(self):
        self.pygame.quit()


class OLEDDisplay(BaseDisplay):
    """Small OLED display (SSD1306) via I2C."""
    
    def __init__(self, resolution: Tuple[int, int] = (128, 64)):
        self.resolution = resolution
        
        try:
            from luma.core.interface.serial import i2c
            from luma.oled.device import ssd1306
            from PIL import Image, ImageDraw, ImageFont
            
            serial = i2c(port=1, address=0x3C)
            self.device = ssd1306(serial, width=resolution[0], height=resolution[1])
            self.Image = Image
            self.ImageDraw = ImageDraw
            self.ImageFont = ImageFont
            
            # Load a small font
            try:
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            except:
                self.font = ImageFont.load_default()
                self.font_large = self.font
            
            logger.info("SSD1306 OLED display initialized")
            
        except ImportError:
            logger.error("luma.oled not installed. Run: pip install luma.oled")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OLED: {e}")
            raise
    
    def _create_image(self):
        """Create a new blank image."""
        return self.Image.new('1', self.resolution, 0)
    
    def _show(self, image):
        """Display an image."""
        self.device.display(image)
    
    def show_ready_screen(self):
        img = self._create_image()
        draw = self.ImageDraw.Draw(img)
        draw.text((10, 10), "WAND", font=self.font_large, fill=1)
        draw.text((10, 30), "SPELLCASTER", font=self.font, fill=1)
        draw.text((10, 48), "Wave wand...", font=self.font, fill=1)
        self._show(img)
    
    def show_tracking(self, point_count: int):
        img = self._create_image()
        draw = self.ImageDraw.Draw(img)
        draw.text((10, 20), "Casting...", font=self.font_large, fill=1)
        dots = "." * min(point_count // 5, 10)
        draw.text((10, 45), dots, font=self.font, fill=1)
        self._show(img)
    
    def show_spell(self, spell):
        img = self._create_image()
        draw = self.ImageDraw.Draw(img)
        
        # Truncate long spell names
        name = spell.name[:12] if len(spell.name) > 12 else spell.name
        draw.text((5, 5), name, font=self.font_large, fill=1)
        
        # Show confidence as bar
        bar_width = int(100 * spell.confidence)
        draw.rectangle([10, 35, 10 + bar_width, 45], fill=1)
        draw.rectangle([10, 35, 110, 45], outline=1)
        
        draw.text((10, 50), f"{spell.confidence:.0%}", font=self.font, fill=1)
        
        self._show(img)
        time.sleep(2)
    
    def show_unrecognized(self):
        img = self._create_image()
        draw = self.ImageDraw.Draw(img)
        draw.text((10, 20), "Unknown", font=self.font_large, fill=1)
        draw.text((10, 45), "Try again", font=self.font, fill=1)
        self._show(img)
        time.sleep(1)
    
    def show_calibration_instructions(self):
        img = self._create_image()
        draw = self.ImageDraw.Draw(img)
        draw.text((5, 5), "CALIBRATE", font=self.font_large, fill=1)
        draw.text((5, 25), "Adjust threshold", font=self.font, fill=1)
        draw.text((5, 40), "Q to save", font=self.font, fill=1)
        self._show(img)
    
    def cleanup(self):
        self.device.clear()


class DisplayManager:
    """
    Factory and manager for display implementations.
    
    Automatically selects the appropriate display based on
    available hardware and configuration.
    """
    
    def __init__(
        self,
        display_type: str = "auto",
        resolution: Tuple[int, int] = (800, 480),
        theme: str = "default",
        fullscreen: bool = False
    ):
        self.theme = THEMES.get(theme, THEMES["default"])
        
        if display_type == "auto":
            display_type = self._detect_display_type()
        
        logger.info(f"Initializing {display_type} display")
        
        if display_type == "pygame":
            self.display = PygameDisplay(resolution, self.theme, fullscreen)
        elif display_type == "oled":
            self.display = OLEDDisplay()
        elif display_type == "headless":
            self.display = HeadlessDisplay()
        else:
            logger.warning(f"Unknown display type: {display_type}, using headless")
            self.display = HeadlessDisplay()
    
    def _detect_display_type(self) -> str:
        """Auto-detect available display."""
        # Check for display environment
        if os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
            try:
                import pygame
                return "pygame"
            except ImportError:
                pass
        
        # Check for I2C OLED
        if os.path.exists('/dev/i2c-1'):
            try:
                from luma.oled.device import ssd1306
                return "oled"
            except ImportError:
                pass
        
        return "headless"
    
    # Delegate all methods to the actual display implementation
    def show_ready_screen(self):
        self.display.show_ready_screen()
    
    def show_tracking(self, point_count: int):
        self.display.show_tracking(point_count)
    
    def show_spell(self, spell):
        self.display.show_spell(spell)
    
    def show_unrecognized(self):
        self.display.show_unrecognized()
    
    def show_calibration_instructions(self):
        self.display.show_calibration_instructions()
    
    def cleanup(self):
        self.display.cleanup()
