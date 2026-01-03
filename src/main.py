#!/usr/bin/env python3
"""
Wand Spellcaster - Main Application Entry Point
================================================
A Raspberry Pi-based spell detection system for Universal Orlando interactive wands.

This system uses computer vision to track the retroreflective tip of Harry Potter
interactive wands and recognize spell gestures using machine learning.

Usage:
    python main.py [--debug] [--no-display] [--calibrate]

Author: Your Name
License: MIT
"""

import argparse
import signal
import sys
import logging
from typing import Optional

from wand_tracker import WandTracker
from spell_recognizer import SpellRecognizer
from display_manager import DisplayManager
from config_loader import Config

# ============================================================================
# PHASE 2 PLACEHOLDER: Two-Player Mode Imports
# ============================================================================
# from multiplayer_manager import MultiplayerManager
# from network_sync import NetworkSync
# ============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpellcasterApp:
    """
    Main application controller for the Wand Spellcaster system.
    
    Coordinates between:
    - WandTracker: Captures and tracks wand position via IR camera
    - SpellRecognizer: Identifies spell patterns using ML
    - DisplayManager: Shows detected spells on screen
    
    Future phases will add:
    - VoiceManager: Text-to-speech for spell names
    - MultiplayerManager: Two-player battle mode
    """
    
    def __init__(self, config: Config, debug: bool = False):
        self.config = config
        self.debug = debug
        self.running = False
        
        # Initialize core components
        logger.info("Initializing Wand Spellcaster...")
        
        self.tracker = WandTracker(
            camera_id=config.camera_id,
            resolution=config.camera_resolution,
            ir_threshold=config.ir_threshold,
            debug=debug
        )
        
        self.recognizer = SpellRecognizer(
            model_path=config.model_path,
            spells_config=config.spells,
            min_confidence=config.min_confidence
        )
        
        self.display = DisplayManager(
            display_type=config.display_type,
            resolution=config.display_resolution,
            theme=config.theme
        )
        
        # ====================================================================
        # PHASE 2 PLACEHOLDER: Voice Manager
        # ====================================================================
        # self.voice = VoiceManager(
        #     engine=config.tts_engine,
        #     voice=config.voice_name,
        #     rate=config.speech_rate
        # )
        # ====================================================================
        
        # ====================================================================
        # PHASE 2 PLACEHOLDER: Multiplayer Manager
        # ====================================================================
        # self.multiplayer = None  # Initialized when entering 2P mode
        # self.player_id = 1  # Default to player 1
        # ====================================================================
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Initialization complete!")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def run(self):
        """
        Main application loop.
        
        Flow:
        1. Capture frame from IR camera
        2. Detect and track wand tip position
        3. Accumulate tracking points into gesture path
        4. When gesture complete, recognize spell
        5. Display result on screen
        6. (Phase 2) Speak spell name
        7. (Phase 2) Sync with opponent in 2P mode
        """
        self.running = True
        gesture_points = []
        gesture_timeout = 0
        
        logger.info("Starting spell detection loop...")
        self.display.show_ready_screen()
        
        while self.running:
            try:
                # Step 1: Get frame and detect wand
                frame = self.tracker.capture_frame()
                wand_position = self.tracker.detect_wand(frame)
                
                if wand_position is not None:
                    # Wand detected - accumulate points
                    gesture_points.append(wand_position)
                    gesture_timeout = self.config.gesture_timeout_frames
                    
                    # Show tracking feedback
                    if self.debug:
                        self.tracker.draw_debug_overlay(frame, wand_position, gesture_points)
                    
                    self.display.show_tracking(len(gesture_points))
                    
                elif gesture_points:
                    # Wand not detected - check if gesture is complete
                    gesture_timeout -= 1
                    
                    if gesture_timeout <= 0:
                        # Gesture complete - attempt recognition
                        if len(gesture_points) >= self.config.min_gesture_points:
                            spell = self.recognizer.recognize(gesture_points)
                            
                            if spell:
                                logger.info(f"Spell detected: {spell.name} (confidence: {spell.confidence:.2f})")
                                self.display.show_spell(spell)
                                
                                # ============================================
                                # PHASE 2 PLACEHOLDER: Voice Output
                                # ============================================
                                # self.voice.speak(spell.incantation)
                                # ============================================
                                
                                # ============================================
                                # PHASE 2 PLACEHOLDER: Multiplayer Sync
                                # ============================================
                                # if self.multiplayer:
                                #     self.multiplayer.send_spell(spell)
                                #     opponent_spell = self.multiplayer.get_opponent_spell()
                                #     result = self.multiplayer.resolve_duel(spell, opponent_spell)
                                #     self.display.show_duel_result(result)
                                # ============================================
                            else:
                                logger.debug("Gesture not recognized as a spell")
                                self.display.show_unrecognized()
                        
                        # Reset for next gesture
                        gesture_points = []
                
                # Show debug view if enabled
                if self.debug:
                    self.tracker.show_debug_window(frame)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                if self.debug:
                    raise
        
        self.cleanup()
    
    def calibrate(self):
        """
        Run calibration mode to help user set up IR detection thresholds.
        
        Shows live camera feed with IR detection overlay and allows
        adjustment of threshold values.
        """
        logger.info("Starting calibration mode...")
        self.display.show_calibration_instructions()
        self.tracker.run_calibration(self.display)
        logger.info("Calibration complete!")
    
    # ========================================================================
    # PHASE 2 PLACEHOLDER: Multiplayer Methods
    # ========================================================================
    # def start_multiplayer(self, role: str = 'host', partner_address: str = None):
    #     """
    #     Initialize two-player battle mode.
    #     
    #     Args:
    #         role: 'host' or 'join'
    #         partner_address: IP address of partner device (for 'join' role)
    #     """
    #     from multiplayer_manager import MultiplayerManager
    #     
    #     self.multiplayer = MultiplayerManager(
    #         role=role,
    #         partner_address=partner_address,
    #         on_opponent_spell=self._on_opponent_spell
    #     )
    #     self.multiplayer.connect()
    #     self.player_id = 1 if role == 'host' else 2
    #     logger.info(f"Multiplayer mode started as Player {self.player_id}")
    # 
    # def _on_opponent_spell(self, spell):
    #     """Callback when opponent casts a spell."""
    #     self.display.show_opponent_spell(spell)
    # ========================================================================
    
    def stop(self):
        """Signal the main loop to stop."""
        self.running = False
    
    def cleanup(self):
        """Clean up resources on shutdown."""
        logger.info("Cleaning up resources...")
        self.tracker.release()
        self.display.cleanup()
        
        # ====================================================================
        # PHASE 2 PLACEHOLDER: Cleanup multiplayer
        # ====================================================================
        # if self.multiplayer:
        #     self.multiplayer.disconnect()
        # ====================================================================
        
        logger.info("Cleanup complete. Goodbye!")


def main():
    """Application entry point."""
    parser = argparse.ArgumentParser(
        description='Wand Spellcaster - Harry Potter Interactive Wand Spell Detector'
    )
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug mode with visual overlays'
    )
    parser.add_argument(
        '--calibrate', '-c',
        action='store_true',
        help='Run calibration mode'
    )
    parser.add_argument(
        '--config', '-f',
        type=str,
        default='config/settings.yaml',
        help='Path to configuration file'
    )
    # ========================================================================
    # PHASE 2 PLACEHOLDER: Multiplayer Arguments
    # ========================================================================
    # parser.add_argument(
    #     '--multiplayer', '-m',
    #     choices=['host', 'join'],
    #     help='Start in multiplayer mode as host or join'
    # )
    # parser.add_argument(
    #     '--partner', '-p',
    #     type=str,
    #     help='Partner IP address (required for --multiplayer join)'
    # )
    # ========================================================================
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = Config.load(args.config)
    except FileNotFoundError:
        logger.warning(f"Config file not found: {args.config}, using defaults")
        config = Config.defaults()
    
    # Create and run application
    app = SpellcasterApp(config, debug=args.debug)
    
    if args.calibrate:
        app.calibrate()
    else:
        # ====================================================================
        # PHASE 2 PLACEHOLDER: Start multiplayer if requested
        # ====================================================================
        # if args.multiplayer:
        #     if args.multiplayer == 'join' and not args.partner:
        #         logger.error("--partner IP required when joining multiplayer")
        #         sys.exit(1)
        #     app.start_multiplayer(args.multiplayer, args.partner)
        # ====================================================================
        
        app.run()


if __name__ == '__main__':
    main()
