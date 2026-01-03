#!/usr/bin/env python3
"""
Wand Tracker Module
===================
Handles IR camera capture and retroreflective wand tip detection.

The Universal Orlando interactive wands have a retroreflective bead at the tip
that bounces back IR light. We use a NoIR camera surrounded by IR LEDs to
illuminate and track this bright spot.

Detection Pipeline:
1. Capture frame from NoIR camera
2. Convert to grayscale
3. Apply threshold to isolate bright IR reflections
4. Find contours of bright regions
5. Filter by size/shape to identify wand tip
6. Return centroid position
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TrackingPoint:
    """A single tracked position with timestamp."""
    x: int
    y: int
    timestamp: float
    brightness: float = 0.0


class WandTracker:
    """
    Tracks the retroreflective tip of a Harry Potter interactive wand.
    
    Uses OpenCV to process frames from a NoIR (no infrared filter) camera
    and detect the bright IR reflection from the wand tip.
    
    Attributes:
        camera_id: Camera device index or path
        resolution: Tuple of (width, height) for capture
        ir_threshold: Brightness threshold for IR detection (0-255)
        min_blob_area: Minimum contour area to consider as wand tip
        max_blob_area: Maximum contour area to consider as wand tip
    """
    
    def __init__(
        self,
        camera_id: int = 0,
        resolution: Tuple[int, int] = (640, 480),
        ir_threshold: int = 200,
        min_blob_area: int = 50,
        max_blob_area: int = 5000,
        debug: bool = False
    ):
        self.camera_id = camera_id
        self.resolution = resolution
        self.ir_threshold = ir_threshold
        self.min_blob_area = min_blob_area
        self.max_blob_area = max_blob_area
        self.debug = debug
        
        # Initialize camera
        self.cap = None
        self._init_camera()
        
        # Tracking state
        self.last_position: Optional[TrackingPoint] = None
        self.tracking_history: List[TrackingPoint] = []
        
        # Debug windows
        self._debug_windows_created = False
    
    def _init_camera(self):
        """Initialize the camera capture device."""
        logger.info(f"Initializing camera {self.camera_id}...")
        
        # Try PiCamera2 first (preferred for Raspberry Pi)
        try:
            from picamera2 import Picamera2
            self.cap = Picamera2()
            config = self.cap.create_preview_configuration(
                main={"size": self.resolution, "format": "RGB888"}
            )
            self.cap.configure(config)
            self.cap.start()
            self._using_picamera = True
            logger.info("Using PiCamera2")
            return
        except ImportError:
            logger.debug("PiCamera2 not available, trying OpenCV")
        except Exception as e:
            logger.debug(f"PiCamera2 failed: {e}, trying OpenCV")
        
        # Fall back to OpenCV VideoCapture
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera {self.camera_id}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Disable auto-exposure if possible (helps with IR detection)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual mode
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -6)  # Low exposure for IR
        
        self._using_picamera = False
        logger.info("Using OpenCV VideoCapture")
    
    def capture_frame(self) -> np.ndarray:
        """
        Capture a single frame from the camera.
        
        Returns:
            numpy array of shape (H, W, 3) in BGR format
        
        Raises:
            RuntimeError: If frame capture fails
        """
        if self._using_picamera:
            frame = self.cap.capture_array()
            # Convert RGB to BGR for OpenCV compatibility
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Failed to capture frame")
        
        return frame
    
    def detect_wand(self, frame: np.ndarray) -> Optional[TrackingPoint]:
        """
        Detect the wand tip position in a frame.
        
        Args:
            frame: BGR image from camera
        
        Returns:
            TrackingPoint with wand position, or None if not detected
        """
        import time
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Threshold to find bright IR spots
        _, thresh = cv2.threshold(
            blurred, 
            self.ir_threshold, 
            255, 
            cv2.THRESH_BINARY
        )
        
        # Find contours
        contours, _ = cv2.findContours(
            thresh, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours to find wand tip
        best_candidate = None
        best_score = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Size filter
            if area < self.min_blob_area or area > self.max_blob_area:
                continue
            
            # Circularity check (wand tip reflection should be roughly circular)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            if circularity < 0.3:  # Not circular enough
                continue
            
            # Get centroid
            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue
            
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            # Get brightness at centroid
            brightness = gray[cy, cx] if 0 <= cy < gray.shape[0] and 0 <= cx < gray.shape[1] else 0
            
            # Score based on brightness and circularity
            score = brightness * circularity
            
            if score > best_score:
                best_score = score
                best_candidate = TrackingPoint(
                    x=cx,
                    y=cy,
                    timestamp=time.time(),
                    brightness=float(brightness)
                )
        
        # Apply motion prediction if we have history
        if best_candidate is None and self.last_position is not None:
            # Could implement Kalman filter prediction here for smoother tracking
            pass
        
        self.last_position = best_candidate
        return best_candidate
    
    def draw_debug_overlay(
        self, 
        frame: np.ndarray, 
        current_pos: Optional[TrackingPoint],
        gesture_points: List[TrackingPoint]
    ) -> np.ndarray:
        """
        Draw debug visualization on frame.
        
        Args:
            frame: Original BGR frame
            current_pos: Current detected wand position
            gesture_points: List of points in current gesture
        
        Returns:
            Frame with debug overlay drawn
        """
        overlay = frame.copy()
        
        # Draw gesture trail
        if len(gesture_points) > 1:
            points = np.array([(p.x, p.y) for p in gesture_points], dtype=np.int32)
            cv2.polylines(overlay, [points], False, (0, 255, 0), 2)
        
        # Draw current position
        if current_pos:
            cv2.circle(overlay, (current_pos.x, current_pos.y), 10, (0, 0, 255), -1)
            cv2.circle(overlay, (current_pos.x, current_pos.y), 15, (0, 255, 255), 2)
        
        # Draw detection info
        cv2.putText(
            overlay,
            f"Points: {len(gesture_points)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        if current_pos:
            cv2.putText(
                overlay,
                f"Pos: ({current_pos.x}, {current_pos.y})",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
        
        return overlay
    
    def show_debug_window(self, frame: np.ndarray):
        """Show debug windows with detection visualization."""
        if not self._debug_windows_created:
            cv2.namedWindow("Wand Tracker - Raw", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Wand Tracker - Threshold", cv2.WINDOW_NORMAL)
            self._debug_windows_created = True
        
        # Show raw frame
        cv2.imshow("Wand Tracker - Raw", frame)
        
        # Show threshold view
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, self.ir_threshold, 255, cv2.THRESH_BINARY)
        cv2.imshow("Wand Tracker - Threshold", thresh)
        
        cv2.waitKey(1)
    
    def run_calibration(self, display_manager):
        """
        Interactive calibration mode for adjusting IR threshold.
        
        Allows real-time adjustment of detection parameters while
        showing the effect on the video feed.
        """
        logger.info("Entering calibration mode. Press 'q' to exit.")
        
        cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
        cv2.createTrackbar("IR Threshold", "Calibration", self.ir_threshold, 255, lambda x: None)
        cv2.createTrackbar("Min Area", "Calibration", self.min_blob_area, 1000, lambda x: None)
        cv2.createTrackbar("Max Area", "Calibration", self.max_blob_area, 10000, lambda x: None)
        
        while True:
            frame = self.capture_frame()
            
            # Get current trackbar values
            self.ir_threshold = cv2.getTrackbarPos("IR Threshold", "Calibration")
            self.min_blob_area = cv2.getTrackbarPos("Min Area", "Calibration")
            self.max_blob_area = max(cv2.getTrackbarPos("Max Area", "Calibration"), self.min_blob_area + 1)
            
            # Detect wand
            wand_pos = self.detect_wand(frame)
            
            # Create visualization
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, self.ir_threshold, 255, cv2.THRESH_BINARY)
            
            # Convert threshold to 3-channel for overlay
            thresh_color = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
            
            # Draw detection
            if wand_pos:
                cv2.circle(frame, (wand_pos.x, wand_pos.y), 15, (0, 255, 0), 3)
                cv2.putText(
                    frame,
                    "WAND DETECTED",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
            
            # Stack views
            combined = np.hstack([frame, thresh_color])
            
            # Add instructions
            cv2.putText(
                combined,
                "Adjust sliders until wand tip is detected. Press 'q' to save and exit.",
                (10, combined.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )
            
            cv2.imshow("Calibration", combined)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyWindow("Calibration")
        logger.info(f"Calibration saved: threshold={self.ir_threshold}, "
                   f"min_area={self.min_blob_area}, max_area={self.max_blob_area}")
        
        return {
            'ir_threshold': self.ir_threshold,
            'min_blob_area': self.min_blob_area,
            'max_blob_area': self.max_blob_area
        }
    
    def release(self):
        """Release camera resources."""
        if self.cap is not None:
            if self._using_picamera:
                self.cap.stop()
            else:
                self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Camera released")
