#!/usr/bin/env python3
"""
Spell Recognizer Module
=======================
Machine learning-based gesture recognition for Harry Potter spells.

Uses a Support Vector Machine (SVM) classifier trained on normalized
gesture paths to recognize spell patterns. Gestures are preprocessed
to be scale, rotation, and position invariant.

Supported Spells (matching Universal Orlando):
- Alohomora (clockwise circle) - Unlocking charm
- Lumos (upward flick) - Light spell
- Nox (downward flick) - Extinguish light
- Incendio (upward diagonal wave) - Fire spell
- Aguamenti (S-curve) - Water spell
- Wingardium Leviosa (swish and flick) - Levitation
- Arresto Momentum (horizontal sweep) - Slowing charm
- Revelio (counter-clockwise circle) - Revealing charm
"""

import numpy as np
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import pickle
import os
import logging
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import json

logger = logging.getLogger(__name__)


@dataclass
class Spell:
    """Represents a recognized spell."""
    name: str
    incantation: str
    confidence: float
    description: str = ""
    color: str = "#FFFFFF"  # For display theming
    
    # ========================================================================
    # PHASE 2 PLACEHOLDER: Duel attributes
    # ========================================================================
    # power: int = 50  # Base power for dueling (0-100)
    # spell_type: str = "neutral"  # attack, defense, neutral
    # counter_spells: List[str] = None  # Spells this counters
    # ========================================================================


# Default spell definitions
DEFAULT_SPELLS = {
    "alohomora": Spell(
        name="Alohomora",
        incantation="Ah-LOH-ho-MOR-ah",
        confidence=0.0,
        description="The Unlocking Charm - opens locked doors and windows",
        color="#FFD700"
    ),
    "lumos": Spell(
        name="Lumos",
        incantation="LOO-mos",
        confidence=0.0,
        description="Wand-Lighting Charm - illuminates the wand tip",
        color="#FFFACD"
    ),
    "nox": Spell(
        name="Nox",
        incantation="NOCKS",
        confidence=0.0,
        description="Counter-charm to Lumos - extinguishes light",
        color="#2F4F4F"
    ),
    "incendio": Spell(
        name="Incendio",
        incantation="in-SEN-dee-oh",
        confidence=0.0,
        description="Fire-Making Spell - produces flames",
        color="#FF4500"
    ),
    "aguamenti": Spell(
        name="Aguamenti",
        incantation="AH-gwah-MEN-tee",
        confidence=0.0,
        description="Water-Making Spell - produces water",
        color="#4169E1"
    ),
    "wingardium_leviosa": Spell(
        name="Wingardium Leviosa",
        incantation="win-GAR-dee-um lev-ee-OH-sa",
        confidence=0.0,
        description="Levitation Charm - makes objects float",
        color="#9370DB"
    ),
    "arresto_momentum": Spell(
        name="Arresto Momentum",
        incantation="ah-REST-oh mo-MEN-tum",
        confidence=0.0,
        description="Slowing Charm - decreases velocity",
        color="#87CEEB"
    ),
    "revelio": Spell(
        name="Revelio",
        incantation="reh-VEL-ee-oh",
        confidence=0.0,
        description="Revealing Charm - reveals hidden objects",
        color="#DA70D6"
    ),
}


class SpellRecognizer:
    """
    Recognizes spell gestures using machine learning.
    
    The recognition pipeline:
    1. Normalize gesture path (scale, position, resample)
    2. Extract features (angles, distances, curvature)
    3. Classify using trained SVM model
    4. Return spell if confidence exceeds threshold
    
    Attributes:
        model_path: Path to trained model file
        spells_config: Dictionary of spell definitions
        min_confidence: Minimum confidence for valid recognition
    """
    
    def __init__(
        self,
        model_path: str = "models/spell_classifier.pkl",
        spells_config: Dict[str, Any] = None,
        min_confidence: float = 0.7,
        num_resample_points: int = 32
    ):
        self.model_path = model_path
        self.spells = spells_config or DEFAULT_SPELLS
        self.min_confidence = min_confidence
        self.num_resample_points = num_resample_points
        
        # Load or create model
        self.model: Optional[SVC] = None
        self.scaler: Optional[StandardScaler] = None
        self.label_map: Dict[int, str] = {}
        
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load trained model or create new one with default gestures."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.scaler = data['scaler']
                    self.label_map = data['label_map']
                logger.info(f"Loaded model from {self.model_path}")
                return
            except Exception as e:
                logger.warning(f"Failed to load model: {e}")
        
        # Create default model with template gestures
        logger.info("Creating default model with template gestures")
        self._create_default_model()
    
    def _create_default_model(self):
        """Create a model trained on template gesture shapes."""
        # Template gestures (simplified representations)
        templates = {
            "alohomora": self._generate_circle(clockwise=True),
            "revelio": self._generate_circle(clockwise=False),
            "lumos": self._generate_vertical_flick(direction="up"),
            "nox": self._generate_vertical_flick(direction="down"),
            "incendio": self._generate_diagonal_wave(),
            "aguamenti": self._generate_s_curve(),
            "wingardium_leviosa": self._generate_swish_flick(),
            "arresto_momentum": self._generate_horizontal_sweep(),
        }
        
        # Generate training data with variations
        X = []
        y = []
        
        for spell_name, template in templates.items():
            # Add original and variations
            for _ in range(20):  # 20 variations per spell
                varied = self._add_variation(template)
                features = self._extract_features(varied)
                X.append(features)
                y.append(spell_name)
        
        X = np.array(X)
        y = np.array(y)
        
        # Create label mapping
        unique_labels = np.unique(y)
        self.label_map = {i: label for i, label in enumerate(unique_labels)}
        reverse_map = {v: k for k, v in self.label_map.items()}
        y_encoded = np.array([reverse_map[label] for label in y])
        
        # Train model
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = SVC(kernel='rbf', probability=True, C=10, gamma='scale')
        self.model.fit(X_scaled, y_encoded)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path) if os.path.dirname(self.model_path) else '.', exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'label_map': self.label_map
            }, f)
        
        logger.info(f"Created and saved default model to {self.model_path}")
    
    def _generate_circle(self, clockwise: bool = True, points: int = 32) -> np.ndarray:
        """Generate a circular gesture template."""
        angles = np.linspace(0, 2 * np.pi, points)
        if not clockwise:
            angles = angles[::-1]
        x = np.cos(angles)
        y = np.sin(angles)
        return np.column_stack([x, y])
    
    def _generate_vertical_flick(self, direction: str = "up", points: int = 32) -> np.ndarray:
        """Generate a vertical flick gesture."""
        t = np.linspace(0, 1, points)
        x = np.sin(t * np.pi * 0.3)  # Slight curve
        y = t if direction == "up" else 1 - t
        return np.column_stack([x, y])
    
    def _generate_diagonal_wave(self, points: int = 32) -> np.ndarray:
        """Generate diagonal wave pattern for Incendio."""
        t = np.linspace(0, 1, points)
        x = t + 0.2 * np.sin(t * 3 * np.pi)
        y = t
        return np.column_stack([x, y])
    
    def _generate_s_curve(self, points: int = 32) -> np.ndarray:
        """Generate S-curve for Aguamenti."""
        t = np.linspace(0, 1, points)
        x = np.sin(t * 2 * np.pi)
        y = t
        return np.column_stack([x, y])
    
    def _generate_swish_flick(self, points: int = 32) -> np.ndarray:
        """Generate swish and flick for Wingardium Leviosa."""
        # First half: horizontal swish
        t1 = np.linspace(0, 0.5, points // 2)
        x1 = t1 * 2
        y1 = 0.2 * np.sin(t1 * 2 * np.pi)
        
        # Second half: upward flick
        t2 = np.linspace(0.5, 1, points // 2)
        x2 = 1 + 0.3 * (t2 - 0.5)
        y2 = (t2 - 0.5) * 2
        
        x = np.concatenate([x1, x2])
        y = np.concatenate([y1, y2])
        return np.column_stack([x, y])
    
    def _generate_horizontal_sweep(self, points: int = 32) -> np.ndarray:
        """Generate horizontal sweep for Arresto Momentum."""
        t = np.linspace(0, 1, points)
        x = t
        y = 0.1 * np.sin(t * np.pi)  # Slight arc
        return np.column_stack([x, y])
    
    def _add_variation(self, template: np.ndarray, noise_scale: float = 0.1) -> np.ndarray:
        """Add random variation to a template gesture."""
        # Add noise
        noise = np.random.randn(*template.shape) * noise_scale
        varied = template + noise
        
        # Random rotation
        angle = np.random.uniform(-0.2, 0.2)
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        rotation = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        varied = varied @ rotation.T
        
        # Random scale
        scale = np.random.uniform(0.8, 1.2)
        varied *= scale
        
        return varied
    
    def _normalize_gesture(self, points: List) -> np.ndarray:
        """
        Normalize a gesture path for recognition.
        
        Steps:
        1. Convert to numpy array
        2. Resample to fixed number of points
        3. Center on origin
        4. Scale to unit size
        """
        # Extract x, y coordinates
        coords = np.array([(p.x, p.y) for p in points])
        
        if len(coords) < 3:
            return None
        
        # Resample to fixed number of points
        resampled = self._resample_path(coords, self.num_resample_points)
        
        # Center on origin
        centroid = np.mean(resampled, axis=0)
        centered = resampled - centroid
        
        # Scale to unit size
        max_dist = np.max(np.abs(centered))
        if max_dist > 0:
            normalized = centered / max_dist
        else:
            normalized = centered
        
        return normalized
    
    def _resample_path(self, points: np.ndarray, num_points: int) -> np.ndarray:
        """Resample path to have exactly num_points evenly spaced points."""
        # Calculate cumulative distance along path
        diffs = np.diff(points, axis=0)
        segment_lengths = np.sqrt(np.sum(diffs ** 2, axis=1))
        cumulative_length = np.concatenate([[0], np.cumsum(segment_lengths)])
        total_length = cumulative_length[-1]
        
        if total_length == 0:
            return np.tile(points[0], (num_points, 1))
        
        # Generate evenly spaced points along path
        target_lengths = np.linspace(0, total_length, num_points)
        
        resampled = np.zeros((num_points, 2))
        for i, target in enumerate(target_lengths):
            # Find segment containing this target length
            idx = np.searchsorted(cumulative_length, target) - 1
            idx = max(0, min(idx, len(points) - 2))
            
            # Interpolate within segment
            segment_start = cumulative_length[idx]
            segment_length = segment_lengths[idx] if idx < len(segment_lengths) else 0
            
            if segment_length > 0:
                t = (target - segment_start) / segment_length
            else:
                t = 0
            
            resampled[i] = points[idx] + t * (points[idx + 1] - points[idx])
        
        return resampled
    
    def _extract_features(self, normalized: np.ndarray) -> np.ndarray:
        """
        Extract feature vector from normalized gesture.
        
        Features include:
        - Flattened coordinates (2N features)
        - Segment angles (N-1 features)
        - Curvature estimates (N-2 features)
        - Bounding box aspect ratio (1 feature)
        - Total path length (1 feature)
        """
        features = []
        
        # Flattened coordinates
        features.extend(normalized.flatten())
        
        # Segment angles
        diffs = np.diff(normalized, axis=0)
        angles = np.arctan2(diffs[:, 1], diffs[:, 0])
        features.extend(angles)
        
        # Curvature (change in angle)
        if len(angles) > 1:
            curvature = np.diff(angles)
            # Normalize angle differences to [-pi, pi]
            curvature = np.arctan2(np.sin(curvature), np.cos(curvature))
            features.extend(curvature)
        
        # Bounding box aspect ratio
        x_range = np.max(normalized[:, 0]) - np.min(normalized[:, 0])
        y_range = np.max(normalized[:, 1]) - np.min(normalized[:, 1])
        aspect_ratio = x_range / (y_range + 1e-6)
        features.append(aspect_ratio)
        
        # Total path length
        path_length = np.sum(np.sqrt(np.sum(diffs ** 2, axis=1)))
        features.append(path_length)
        
        return np.array(features)
    
    def recognize(self, points: List) -> Optional[Spell]:
        """
        Recognize a spell from a list of tracking points.
        
        Args:
            points: List of TrackingPoint objects forming the gesture
        
        Returns:
            Spell object if recognized with sufficient confidence, else None
        """
        if self.model is None:
            logger.warning("No model loaded")
            return None
        
        # Normalize gesture
        normalized = self._normalize_gesture(points)
        if normalized is None:
            return None
        
        # Extract features
        features = self._extract_features(normalized)
        
        # Ensure feature vector matches training
        expected_features = self.scaler.n_features_in_
        if len(features) != expected_features:
            logger.warning(f"Feature mismatch: got {len(features)}, expected {expected_features}")
            # Pad or truncate
            if len(features) < expected_features:
                features = np.pad(features, (0, expected_features - len(features)))
            else:
                features = features[:expected_features]
        
        # Scale features
        features_scaled = self.scaler.transform([features])
        
        # Predict
        probabilities = self.model.predict_proba(features_scaled)[0]
        predicted_class = np.argmax(probabilities)
        confidence = probabilities[predicted_class]
        
        if confidence < self.min_confidence:
            logger.debug(f"Low confidence: {confidence:.2f} for {self.label_map.get(predicted_class)}")
            return None
        
        spell_name = self.label_map.get(predicted_class)
        if spell_name not in self.spells:
            logger.warning(f"Unknown spell: {spell_name}")
            return None
        
        # Return spell with confidence
        spell = Spell(
            name=self.spells[spell_name].name,
            incantation=self.spells[spell_name].incantation,
            confidence=float(confidence),
            description=self.spells[spell_name].description,
            color=self.spells[spell_name].color
        )
        
        return spell
    
    def train_custom_spell(self, name: str, examples: List[List], incantation: str = ""):
        """
        Train a new custom spell from examples.
        
        Args:
            name: Name of the new spell
            examples: List of gesture examples (each is list of TrackingPoints)
            incantation: Pronunciation guide
        """
        # ====================================================================
        # PHASE 2 PLACEHOLDER: Custom spell training
        # ====================================================================
        # This would allow users to define their own spells
        # Implementation would:
        # 1. Extract features from all examples
        # 2. Add to training data
        # 3. Retrain model
        # 4. Save updated model
        pass


# ============================================================================
# PHASE 2 PLACEHOLDER: Duel Resolution System
# ============================================================================
# class DuelResolver:
#     """
#     Resolves spell duels in two-player mode.
#     
#     Uses a rock-paper-scissors style mechanic with spell types:
#     - Attack spells beat Neutral spells
#     - Defense spells beat Attack spells
#     - Neutral spells beat Defense spells
#     
#     Ties are resolved by casting speed and confidence.
#     """
#     
#     SPELL_TYPES = {
#         "incendio": "attack",
#         "aguamenti": "attack",
#         "arresto_momentum": "defense",
#         "wingardium_leviosa": "defense",
#         "alohomora": "neutral",
#         "revelio": "neutral",
#         "lumos": "neutral",
#         "nox": "neutral",
#     }
#     
#     def resolve(self, spell1: Spell, spell2: Spell) -> Dict[str, Any]:
#         """Resolve a duel between two spells."""
#         type1 = self.SPELL_TYPES.get(spell1.name.lower(), "neutral")
#         type2 = self.SPELL_TYPES.get(spell2.name.lower(), "neutral")
#         
#         # Determine winner
#         if type1 == type2:
#             # Tie - higher confidence wins
#             winner = 1 if spell1.confidence > spell2.confidence else 2
#         elif (type1, type2) in [("attack", "neutral"), ("defense", "attack"), ("neutral", "defense")]:
#             winner = 1
#         else:
#             winner = 2
#         
#         return {
#             "winner": winner,
#             "spell1": spell1,
#             "spell2": spell2,
#             "type1": type1,
#             "type2": type2,
#         }
# ============================================================================
