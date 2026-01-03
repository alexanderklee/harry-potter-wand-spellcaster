#!/usr/bin/env python3
"""
Spell Manager - Add, Train, and Test Custom Spells
===================================================

This tool allows you to:
1. Record new spell gestures using your wand
2. Add spells from predefined templates
3. Train the recognizer with your custom spells
4. Test recognition accuracy

Usage:
    python spell_manager.py record <spell_name>    # Record a new spell gesture
    python spell_manager.py add <spell_name>       # Add from template library
    python spell_manager.py train                  # Retrain the model
    python spell_manager.py test                   # Test recognition
    python spell_manager.py list                   # List all spells
"""

import os
import sys
import json
import pickle
import argparse
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spell_recognizer import SpellRecognizer, Spell, DEFAULT_SPELLS
from config_loader import Config


# =============================================================================
# TEMPLATE LIBRARY - Predefined gesture patterns you can use
# =============================================================================

GESTURE_TEMPLATES = {
    # Circles and loops
    "circle_cw": {
        "description": "Clockwise circle",
        "generator": "circle",
        "params": {"clockwise": True}
    },
    "circle_ccw": {
        "description": "Counter-clockwise circle",
        "generator": "circle",
        "params": {"clockwise": False}
    },
    "figure_eight": {
        "description": "Figure-8 pattern",
        "generator": "figure_eight",
        "params": {}
    },
    "spiral_in": {
        "description": "Inward spiral",
        "generator": "spiral",
        "params": {"direction": "in"}
    },
    "spiral_out": {
        "description": "Outward spiral",
        "generator": "spiral",
        "params": {"direction": "out"}
    },
    
    # Lines and flicks
    "flick_up": {
        "description": "Quick upward flick",
        "generator": "vertical_flick",
        "params": {"direction": "up"}
    },
    "flick_down": {
        "description": "Quick downward flick",
        "generator": "vertical_flick",
        "params": {"direction": "down"}
    },
    "flick_left": {
        "description": "Quick leftward flick",
        "generator": "horizontal_flick",
        "params": {"direction": "left"}
    },
    "flick_right": {
        "description": "Quick rightward flick",
        "generator": "horizontal_flick",
        "params": {"direction": "right"}
    },
    "diagonal_up_right": {
        "description": "Diagonal line up-right",
        "generator": "diagonal",
        "params": {"direction": "up_right"}
    },
    "diagonal_up_left": {
        "description": "Diagonal line up-left",
        "generator": "diagonal",
        "params": {"direction": "up_left"}
    },
    "diagonal_down_right": {
        "description": "Diagonal line down-right",
        "generator": "diagonal",
        "params": {"direction": "down_right"}
    },
    "diagonal_down_left": {
        "description": "Diagonal line down-left",
        "generator": "diagonal",
        "params": {"direction": "down_left"}
    },
    
    # Waves and curves
    "wave_horizontal": {
        "description": "Horizontal wave pattern",
        "generator": "wave",
        "params": {"orientation": "horizontal"}
    },
    "wave_vertical": {
        "description": "Vertical wave pattern",
        "generator": "wave",
        "params": {"orientation": "vertical"}
    },
    "s_curve": {
        "description": "S-shaped curve",
        "generator": "s_curve",
        "params": {}
    },
    "zigzag": {
        "description": "Zigzag pattern",
        "generator": "zigzag",
        "params": {"peaks": 3}
    },
    
    # Complex patterns
    "swish_flick": {
        "description": "Horizontal swish then upward flick",
        "generator": "swish_flick",
        "params": {}
    },
    "triangle": {
        "description": "Triangle shape",
        "generator": "triangle",
        "params": {}
    },
    "square": {
        "description": "Square shape",
        "generator": "square",
        "params": {}
    },
    "star": {
        "description": "5-pointed star",
        "generator": "star",
        "params": {"points": 5}
    },
    "lightning_bolt": {
        "description": "Lightning bolt shape",
        "generator": "lightning",
        "params": {}
    },
    "heart": {
        "description": "Heart shape",
        "generator": "heart",
        "params": {}
    },
    "infinity": {
        "description": "Infinity symbol",
        "generator": "infinity",
        "params": {}
    },
    "checkmark": {
        "description": "Checkmark shape",
        "generator": "checkmark",
        "params": {}
    },
    "x_mark": {
        "description": "X shape",
        "generator": "x_mark",
        "params": {}
    },
}


# =============================================================================
# SUGGESTED NEW SPELLS - Ready to add
# =============================================================================

SUGGESTED_SPELLS = {
    "stupefy": {
        "name": "Stupefy",
        "incantation": "STOO-puh-fye",
        "description": "Stunning Spell - renders target unconscious",
        "color": "#FF0000",
        "gesture": "lightning_bolt"
    },
    "expelliarmus": {
        "name": "Expelliarmus",
        "incantation": "ex-PELL-ee-AR-mus",
        "description": "Disarming Charm - forces opponent to drop wand",
        "color": "#FF6600",
        "gesture": "diagonal_up_right"
    },
    "protego": {
        "name": "Protego",
        "incantation": "pro-TAY-go",
        "description": "Shield Charm - creates magical barrier",
        "color": "#00BFFF",
        "gesture": "circle_ccw"
    },
    "expecto_patronum": {
        "name": "Expecto Patronum",
        "incantation": "ex-PEK-toh pa-TRO-num",
        "description": "Patronus Charm - summons protective guardian",
        "color": "#FFFFFF",
        "gesture": "spiral_out"
    },
    "accio": {
        "name": "Accio",
        "incantation": "AK-see-oh",
        "description": "Summoning Charm - brings object to caster",
        "color": "#9932CC",
        "gesture": "spiral_in"
    },
    "obliviate": {
        "name": "Obliviate",
        "incantation": "oh-BLI-vee-ate",
        "description": "Memory Charm - erases memories",
        "color": "#4B0082",
        "gesture": "wave_horizontal"
    },
    "petrificus_totalus": {
        "name": "Petrificus Totalus",
        "incantation": "pe-TRI-fi-kus to-TAH-lus",
        "description": "Full Body-Bind Curse - paralyzes target",
        "color": "#808080",
        "gesture": "flick_down"
    },
    "riddikulus": {
        "name": "Riddikulus",
        "incantation": "rih-DIH-kuh-lus",
        "description": "Boggart Banishing Spell - makes fears funny",
        "color": "#FFD700",
        "gesture": "zigzag"
    },
    "reparo": {
        "name": "Reparo",
        "incantation": "reh-PAH-roh",
        "description": "Mending Charm - repairs broken objects",
        "color": "#32CD32",
        "gesture": "circle_cw"
    },
    "finite_incantatem": {
        "name": "Finite Incantatem",
        "incantation": "fi-NEE-tay in-can-TAH-tem",
        "description": "Counter-spell - terminates spell effects",
        "color": "#C0C0C0",
        "gesture": "x_mark"
    },
    "confundo": {
        "name": "Confundo",
        "incantation": "con-FUN-doh",
        "description": "Confundus Charm - causes confusion",
        "color": "#DDA0DD",
        "gesture": "figure_eight"
    },
    "imperio": {
        "name": "Imperio",
        "incantation": "im-PEER-ee-oh",
        "description": "Imperius Curse - controls target (Unforgivable)",
        "color": "#8B0000",
        "gesture": "wave_vertical"
    },
    "crucio": {
        "name": "Crucio",
        "incantation": "KROO-see-oh",
        "description": "Cruciatus Curse - causes pain (Unforgivable)",
        "color": "#8B0000",
        "gesture": "lightning_bolt"
    },
    "avada_kedavra": {
        "name": "Avada Kedavra",
        "incantation": "ah-VAH-dah keh-DAV-rah",
        "description": "Killing Curse (Unforgivable)",
        "color": "#00FF00",
        "gesture": "triangle"
    },
    "sectumsempra": {
        "name": "Sectumsempra",
        "incantation": "sec-tum-SEMP-rah",
        "description": "Slashing curse - causes deep cuts",
        "color": "#8B0000",
        "gesture": "diagonal_down_right"
    },
    "levicorpus": {
        "name": "Levicorpus",
        "incantation": "leh-vee-COR-pus",
        "description": "Dangles target upside down",
        "color": "#9370DB",
        "gesture": "flick_up"
    },
    "muffliato": {
        "name": "Muffliato",
        "incantation": "muf-lee-AH-to",
        "description": "Creates buzzing to prevent eavesdropping",
        "color": "#A9A9A9",
        "gesture": "wave_horizontal"
    },
    "episkey": {
        "name": "Episkey",
        "incantation": "ee-PIS-key",
        "description": "Healing spell for minor injuries",
        "color": "#98FB98",
        "gesture": "checkmark"
    },
    "engorgio": {
        "name": "Engorgio",
        "incantation": "en-GOR-jee-oh",
        "description": "Engorgement Charm - makes things larger",
        "color": "#FF8C00",
        "gesture": "spiral_out"
    },
    "reducio": {
        "name": "Reducio",
        "incantation": "re-DOO-see-oh",
        "description": "Shrinking Charm - makes things smaller",
        "color": "#00CED1",
        "gesture": "spiral_in"
    },
}


class GestureGenerator:
    """Generates gesture point arrays from templates."""
    
    def __init__(self, num_points: int = 32):
        self.num_points = num_points
    
    def generate(self, template_name: str) -> np.ndarray:
        """Generate points for a named template."""
        if template_name not in GESTURE_TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = GESTURE_TEMPLATES[template_name]
        generator_name = template["generator"]
        params = template["params"]
        
        generator_method = getattr(self, f"_gen_{generator_name}", None)
        if generator_method is None:
            raise ValueError(f"Generator not implemented: {generator_name}")
        
        return generator_method(**params)
    
    def _gen_circle(self, clockwise: bool = True) -> np.ndarray:
        angles = np.linspace(0, 2 * np.pi, self.num_points)
        if not clockwise:
            angles = angles[::-1]
        x = np.cos(angles)
        y = np.sin(angles)
        return np.column_stack([x, y])
    
    def _gen_vertical_flick(self, direction: str = "up") -> np.ndarray:
        t = np.linspace(0, 1, self.num_points)
        x = np.sin(t * np.pi * 0.3)
        y = t if direction == "up" else 1 - t
        return np.column_stack([x, y])
    
    def _gen_horizontal_flick(self, direction: str = "right") -> np.ndarray:
        t = np.linspace(0, 1, self.num_points)
        x = t if direction == "right" else 1 - t
        y = np.sin(t * np.pi * 0.3)
        return np.column_stack([x, y])
    
    def _gen_diagonal(self, direction: str = "up_right") -> np.ndarray:
        t = np.linspace(0, 1, self.num_points)
        
        if direction == "up_right":
            x, y = t, t
        elif direction == "up_left":
            x, y = 1 - t, t
        elif direction == "down_right":
            x, y = t, 1 - t
        else:  # down_left
            x, y = 1 - t, 1 - t
        
        # Add slight curve
        x = x + 0.1 * np.sin(t * np.pi)
        return np.column_stack([x, y])
    
    def _gen_wave(self, orientation: str = "horizontal") -> np.ndarray:
        t = np.linspace(0, 1, self.num_points)
        if orientation == "horizontal":
            x = t
            y = 0.3 * np.sin(t * 3 * np.pi)
        else:
            x = 0.3 * np.sin(t * 3 * np.pi)
            y = t
        return np.column_stack([x, y])
    
    def _gen_s_curve(self) -> np.ndarray:
        t = np.linspace(0, 1, self.num_points)
        x = np.sin(t * 2 * np.pi) * 0.5
        y = t
        return np.column_stack([x, y])
    
    def _gen_zigzag(self, peaks: int = 3) -> np.ndarray:
        t = np.linspace(0, 1, self.num_points)
        x = t
        y = 0.5 + 0.4 * np.sign(np.sin(t * peaks * np.pi))
        return np.column_stack([x, y])
    
    def _gen_swish_flick(self) -> np.ndarray:
        # First half: horizontal swish
        t1 = np.linspace(0, 0.5, self.num_points // 2)
        x1 = t1 * 2
        y1 = 0.2 * np.sin(t1 * 2 * np.pi)
        
        # Second half: upward flick
        t2 = np.linspace(0.5, 1, self.num_points // 2)
        x2 = 1 + 0.3 * (t2 - 0.5)
        y2 = (t2 - 0.5) * 2
        
        x = np.concatenate([x1, x2])
        y = np.concatenate([y1, y2])
        return np.column_stack([x, y])
    
    def _gen_figure_eight(self) -> np.ndarray:
        t = np.linspace(0, 2 * np.pi, self.num_points)
        x = np.sin(t)
        y = np.sin(2 * t) / 2
        return np.column_stack([x, y])
    
    def _gen_spiral(self, direction: str = "out") -> np.ndarray:
        t = np.linspace(0, 4 * np.pi, self.num_points)
        r = np.linspace(0.1, 1, self.num_points)
        if direction == "in":
            r = r[::-1]
        x = r * np.cos(t)
        y = r * np.sin(t)
        return np.column_stack([x, y])
    
    def _gen_triangle(self) -> np.ndarray:
        # Three corners of triangle
        corners = np.array([
            [0.5, 1],    # Top
            [0, 0],      # Bottom left
            [1, 0],      # Bottom right
            [0.5, 1],    # Back to top
        ])
        return self._interpolate_corners(corners)
    
    def _gen_square(self) -> np.ndarray:
        corners = np.array([
            [0, 0], [1, 0], [1, 1], [0, 1], [0, 0]
        ])
        return self._interpolate_corners(corners)
    
    def _gen_star(self, points: int = 5) -> np.ndarray:
        angles_outer = np.linspace(0, 2 * np.pi, points + 1)[:-1] - np.pi / 2
        angles_inner = angles_outer + np.pi / points
        
        corners = []
        for i in range(points):
            corners.append([np.cos(angles_outer[i]), np.sin(angles_outer[i])])
            corners.append([0.4 * np.cos(angles_inner[i]), 0.4 * np.sin(angles_inner[i])])
        corners.append(corners[0])
        
        return self._interpolate_corners(np.array(corners))
    
    def _gen_lightning(self) -> np.ndarray:
        corners = np.array([
            [0.3, 1],
            [0.5, 0.6],
            [0.3, 0.6],
            [0.7, 0],
            [0.5, 0.4],
            [0.7, 0.4],
            [0.3, 1],
        ])
        return self._interpolate_corners(corners)
    
    def _gen_heart(self) -> np.ndarray:
        t = np.linspace(0, 2 * np.pi, self.num_points)
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
        # Normalize
        x = (x - x.min()) / (x.max() - x.min())
        y = (y - y.min()) / (y.max() - y.min())
        return np.column_stack([x, y])
    
    def _gen_infinity(self) -> np.ndarray:
        t = np.linspace(0, 2 * np.pi, self.num_points)
        x = np.cos(t)
        y = np.sin(2 * t) / 2
        return np.column_stack([x, y])
    
    def _gen_checkmark(self) -> np.ndarray:
        corners = np.array([
            [0, 0.5],
            [0.3, 0.2],
            [1, 1],
        ])
        return self._interpolate_corners(corners)
    
    def _gen_x_mark(self) -> np.ndarray:
        # Draw X as two strokes
        n = self.num_points // 2
        stroke1 = np.column_stack([
            np.linspace(0, 1, n),
            np.linspace(0, 1, n)
        ])
        stroke2 = np.column_stack([
            np.linspace(1, 0, n),
            np.linspace(0, 1, n)
        ])
        return np.vstack([stroke1, stroke2])
    
    def _interpolate_corners(self, corners: np.ndarray) -> np.ndarray:
        """Interpolate between corners to get smooth path."""
        total_dist = np.sum(np.sqrt(np.sum(np.diff(corners, axis=0)**2, axis=1)))
        points_per_unit = self.num_points / total_dist
        
        result = []
        for i in range(len(corners) - 1):
            start, end = corners[i], corners[i + 1]
            dist = np.sqrt(np.sum((end - start) ** 2))
            n_points = max(2, int(dist * points_per_unit))
            
            for j in range(n_points):
                t = j / n_points
                result.append(start + t * (end - start))
        
        result.append(corners[-1])
        
        # Resample to exact number of points
        result = np.array(result)
        indices = np.linspace(0, len(result) - 1, self.num_points).astype(int)
        return result[indices]


class SpellManager:
    """Manages custom spell definitions and training."""
    
    def __init__(self, config_path: str = "config/custom_spells.json"):
        self.config_path = config_path
        self.custom_spells = self._load_custom_spells()
        self.generator = GestureGenerator()
    
    def _load_custom_spells(self) -> Dict[str, Any]:
        """Load custom spell definitions from JSON."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_custom_spells(self):
        """Save custom spell definitions to JSON."""
        os.makedirs(os.path.dirname(self.config_path) or '.', exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.custom_spells, f, indent=2)
    
    def list_spells(self):
        """List all available spells."""
        print("\n" + "=" * 60)
        print("CURRENT SPELLS (Built-in)")
        print("=" * 60)
        
        for key, spell in DEFAULT_SPELLS.items():
            print(f"  {spell.name:<25} - {spell.description[:40]}...")
        
        if self.custom_spells:
            print("\n" + "=" * 60)
            print("CUSTOM SPELLS")
            print("=" * 60)
            
            for key, spell in self.custom_spells.items():
                print(f"  {spell['name']:<25} - {spell.get('description', 'No description')[:40]}...")
        
        print("\n" + "=" * 60)
        print("AVAILABLE TO ADD (Suggested)")
        print("=" * 60)
        
        for key, spell in SUGGESTED_SPELLS.items():
            if key not in DEFAULT_SPELLS and key not in self.custom_spells:
                print(f"  {spell['name']:<25} [{spell['gesture']}]")
        
        print("\n" + "=" * 60)
        print("GESTURE TEMPLATES")
        print("=" * 60)
        
        for key, template in GESTURE_TEMPLATES.items():
            print(f"  {key:<20} - {template['description']}")
    
    def add_spell(self, spell_key: str, gesture_template: str = None):
        """Add a spell from suggestions or with custom gesture."""
        
        # Check if it's a suggested spell
        if spell_key in SUGGESTED_SPELLS:
            spell_data = SUGGESTED_SPELLS[spell_key].copy()
            gesture = gesture_template or spell_data.pop('gesture', 'circle_cw')
        else:
            # Create custom spell interactively
            print(f"\nCreating new spell: {spell_key}")
            name = input("  Display name: ").strip() or spell_key.replace('_', ' ').title()
            incantation = input("  Incantation (pronunciation): ").strip() or name.upper()
            description = input("  Description: ").strip() or "A custom spell"
            color = input("  Color (hex, e.g. #FF0000): ").strip() or "#FFFFFF"
            
            print("\n  Available gesture templates:")
            for i, (key, template) in enumerate(GESTURE_TEMPLATES.items()):
                print(f"    {i+1}. {key}: {template['description']}")
            
            gesture_choice = input("  Choose gesture (name or number): ").strip()
            
            if gesture_choice.isdigit():
                idx = int(gesture_choice) - 1
                gesture = list(GESTURE_TEMPLATES.keys())[idx]
            else:
                gesture = gesture_choice
            
            spell_data = {
                "name": name,
                "incantation": incantation,
                "description": description,
                "color": color,
            }
        
        # Validate gesture
        if gesture not in GESTURE_TEMPLATES:
            print(f"Error: Unknown gesture template '{gesture}'")
            print("Available templates:", list(GESTURE_TEMPLATES.keys()))
            return False
        
        # Store spell with gesture reference
        spell_data['gesture_template'] = gesture
        self.custom_spells[spell_key] = spell_data
        self._save_custom_spells()
        
        print(f"\n✓ Added spell: {spell_data['name']}")
        print(f"  Gesture: {gesture} ({GESTURE_TEMPLATES[gesture]['description']})")
        print("\nRun 'python spell_manager.py train' to update the model.")
        
        return True
    
    def remove_spell(self, spell_key: str):
        """Remove a custom spell."""
        if spell_key in self.custom_spells:
            del self.custom_spells[spell_key]
            self._save_custom_spells()
            print(f"✓ Removed spell: {spell_key}")
            print("\nRun 'python spell_manager.py train' to update the model.")
            return True
        else:
            print(f"Error: Spell '{spell_key}' not found in custom spells")
            return False
    
    def train_model(self, model_path: str = "models/spell_classifier.pkl"):
        """Retrain the model with all spells including custom ones."""
        from sklearn.svm import SVC
        from sklearn.preprocessing import StandardScaler
        
        print("\nTraining spell recognition model...")
        print("=" * 50)
        
        # Combine default and custom spells
        all_spells = {}
        
        # Add defaults with their templates
        default_templates = {
            "alohomora": "circle_cw",
            "revelio": "circle_ccw",
            "lumos": "flick_up",
            "nox": "flick_down",
            "incendio": "diagonal_up_right",
            "aguamenti": "s_curve",
            "wingardium_leviosa": "swish_flick",
            "arresto_momentum": "wave_horizontal",
        }
        
        for key, template in default_templates.items():
            all_spells[key] = template
            print(f"  + {key}: {template}")
        
        # Add custom spells
        for key, spell_data in self.custom_spells.items():
            template = spell_data.get('gesture_template', 'circle_cw')
            all_spells[key] = template
            print(f"  + {key}: {template} (custom)")
        
        # Generate training data
        print("\nGenerating training data...")
        X = []
        y = []
        
        recognizer = SpellRecognizer.__new__(SpellRecognizer)
        recognizer.num_resample_points = 32
        
        for spell_name, template_name in all_spells.items():
            template = self.generator.generate(template_name)
            
            # Generate variations
            for _ in range(30):  # 30 variations per spell
                varied = self._add_variation(template)
                features = recognizer._extract_features(varied)
                X.append(features)
                y.append(spell_name)
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"  Generated {len(X)} training samples")
        
        # Create label mapping
        unique_labels = np.unique(y)
        label_map = {i: label for i, label in enumerate(unique_labels)}
        reverse_map = {v: k for k, v in label_map.items()}
        y_encoded = np.array([reverse_map[label] for label in y])
        
        # Train
        print("Training SVM classifier...")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = SVC(kernel='rbf', probability=True, C=10, gamma='scale')
        model.fit(X_scaled, y_encoded)
        
        # Save
        os.makedirs(os.path.dirname(model_path) or '.', exist_ok=True)
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'scaler': scaler,
                'label_map': label_map
            }, f)
        
        print(f"\n✓ Model saved to {model_path}")
        print(f"  Total spells: {len(unique_labels)}")
        
        return True
    
    def _add_variation(self, template: np.ndarray, noise_scale: float = 0.1) -> np.ndarray:
        """Add random variation to a template gesture."""
        noise = np.random.randn(*template.shape) * noise_scale
        varied = template + noise
        
        # Random rotation
        angle = np.random.uniform(-0.3, 0.3)
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        rotation = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        varied = varied @ rotation.T
        
        # Random scale
        scale = np.random.uniform(0.7, 1.3)
        varied *= scale
        
        # Normalize
        centroid = np.mean(varied, axis=0)
        varied = varied - centroid
        max_dist = np.max(np.abs(varied))
        if max_dist > 0:
            varied = varied / max_dist
        
        return varied
    
    def record_gesture(self, spell_key: str):
        """Record a custom gesture using the camera."""
        print("\n" + "=" * 50)
        print("GESTURE RECORDING MODE")
        print("=" * 50)
        print(f"\nRecording gesture for: {spell_key}")
        print("\nInstructions:")
        print("  1. Position yourself in front of the camera")
        print("  2. Press SPACE to start recording")
        print("  3. Draw the gesture with your wand")
        print("  4. Press SPACE to stop recording")
        print("  5. Repeat 5 times for better training")
        print("\nPress 'q' to quit without saving")
        
        try:
            from wand_tracker import WandTracker
        except ImportError:
            print("\nError: Could not import wand_tracker.")
            print("Make sure you're running from the project directory.")
            return None
        
        tracker = WandTracker(debug=True)
        recorded_gestures = []
        
        import cv2
        
        recording = False
        current_points = []
        
        print("\nCamera ready. Press SPACE to start recording...")
        
        while len(recorded_gestures) < 5:
            frame = tracker.capture_frame()
            wand_pos = tracker.detect_wand(frame)
            
            # Draw current state
            if wand_pos and recording:
                current_points.append((wand_pos.x, wand_pos.y))
                cv2.circle(frame, (wand_pos.x, wand_pos.y), 5, (0, 255, 0), -1)
            
            # Draw trail
            if len(current_points) > 1:
                pts = np.array(current_points, dtype=np.int32)
                cv2.polylines(frame, [pts], False, (0, 255, 0), 2)
            
            # Status text
            status = f"Recording... ({len(current_points)} points)" if recording else "Ready (SPACE to start)"
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Gestures: {len(recorded_gestures)}/5", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Gesture Recording", frame)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' '):
                if recording:
                    # Stop recording
                    if len(current_points) > 10:
                        recorded_gestures.append(current_points.copy())
                        print(f"  ✓ Recorded gesture {len(recorded_gestures)}/5 ({len(current_points)} points)")
                    else:
                        print("  ✗ Too few points, try again")
                    current_points = []
                    recording = False
                else:
                    # Start recording
                    recording = True
                    current_points = []
            
            elif key == ord('q'):
                break
        
        tracker.release()
        cv2.destroyAllWindows()
        
        if len(recorded_gestures) >= 3:
            print(f"\n✓ Recorded {len(recorded_gestures)} gestures for {spell_key}")
            return recorded_gestures
        else:
            print("\n✗ Not enough gestures recorded")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="Manage spells for Wand Spellcaster",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python spell_manager.py list                    # Show all spells
  python spell_manager.py add stupefy            # Add suggested spell
  python spell_manager.py add my_spell           # Create custom spell
  python spell_manager.py remove my_spell        # Remove custom spell
  python spell_manager.py train                  # Retrain model
  python spell_manager.py record expelliarmus    # Record gesture from camera
        """
    )
    
    parser.add_argument('command', choices=['list', 'add', 'remove', 'train', 'record', 'templates'],
                       help='Command to execute')
    parser.add_argument('spell_name', nargs='?', help='Spell name (for add/remove/record)')
    parser.add_argument('--gesture', '-g', help='Gesture template name (for add)')
    
    args = parser.parse_args()
    
    manager = SpellManager()
    
    if args.command == 'list':
        manager.list_spells()
    
    elif args.command == 'templates':
        print("\nAvailable Gesture Templates:")
        print("=" * 50)
        for key, template in GESTURE_TEMPLATES.items():
            print(f"  {key:<20} - {template['description']}")
    
    elif args.command == 'add':
        if not args.spell_name:
            print("Error: Spell name required")
            print("Usage: python spell_manager.py add <spell_name>")
            return
        manager.add_spell(args.spell_name, args.gesture)
    
    elif args.command == 'remove':
        if not args.spell_name:
            print("Error: Spell name required")
            return
        manager.remove_spell(args.spell_name)
    
    elif args.command == 'train':
        manager.train_model()
    
    elif args.command == 'record':
        if not args.spell_name:
            print("Error: Spell name required")
            return
        manager.record_gesture(args.spell_name)


if __name__ == '__main__':
    main()
