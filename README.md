# 🪄 Wand Spellcaster

A Raspberry Pi-based spell detection system that recognizes gestures from Universal Orlando interactive Harry Potter wands and displays the detected spell on screen.

![Phase](https://img.shields.io/badge/Phase-1%20(Single%20Player)-blue)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red)
![Python](https://img.shields.io/badge/Python-3.9+-green)

## 📖 Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Hardware Requirements](#hardware-requirements)
- [Wiring Guide](#wiring-guide)
- [Software Installation](#software-installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Supported Spells](#supported-spells)
- [Troubleshooting](#troubleshooting)
- [Future Phases](#future-phases)

---

## Overview

This project lets you use your Universal Orlando interactive wand at home! Wave your wand, and the system will:

1. Track the wand tip using an infrared camera
2. Recognize the gesture pattern using machine learning
3. Display the detected spell on a connected screen

**What makes this different from other projects?**

- Uses the **actual Universal wands** (with retroreflective tips), not the Noble Collection remote wands
- **True gesture recognition** - distinguishes between different spells based on the pattern you draw
- **Cost-effective** - runs on a Raspberry Pi Zero 2 W (~$15)
- **Expandable** - designed with Phase 2 (voice + multiplayer) in mind

---

## How It Works

### The Science Behind Universal's Wands

Universal Orlando's interactive wands have a **retroreflective bead** at the tip. This bead bounces infrared light directly back to its source (like road signs at night). The park's spell locations have:

1. IR LED illuminators that flood the area with invisible infrared light
2. IR cameras that see the bright reflection from wand tips
3. Computer vision software that tracks the wand movement
4. Pattern matching to recognize which spell was cast

**We replicate this system at home:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     SYSTEM ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐                                               │
│   │  IR LEDs    │ ──── Infrared light ────┐                     │
│   │  (850nm)    │                         │                     │
│   └─────────────┘                         ▼                     │
│                                    ┌─────────────┐              │
│                                    │    WAND     │              │
│                                    │ (retroflec- │              │
│                                    │  tive tip)  │              │
│                                    └─────────────┘              │
│                                           │                     │
│                              IR reflection│                     │
│                                           ▼                     │
│   ┌─────────────┐                  ┌─────────────┐              │
│   │ NoIR Camera │ ◄─── captures ───│  Bright     │              │
│   │ (no IR      │                  │  Spot       │              │
│   │  filter)    │                  └─────────────┘              │
│   └──────┬──────┘                                               │
│          │                                                      │
│          │ Video frames                                         │
│          ▼                                                      │
│   ┌─────────────────────────────────────────────────────┐       │
│   │              RASPBERRY PI                           │       │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │       │
│   │  │   OpenCV    │  │  Scikit-    │  │   Pygame/   │  │       │
│   │  │   Blob      │─▶│  Learn SVM  │─▶│   OLED      │  │       │
│   │  │  Detection  │  │  Classifier │  │  Display    │  │       │
│   │  └─────────────┘  └─────────────┘  └─────────────┘  │       │
│   │                                                     │       │
│   │    Tracks wand     Recognizes      Shows spell      │       │
│   │    position        gesture         name             │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Software Pipeline

```
┌──────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW                                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │ Camera  │───▶│ Wand    │───▶│ Gesture │───▶│ Spell   │            │
│  │ Capture │    │ Tracker │    │ Buffer  │    │ Recog.  │            │
│  └─────────┘    └─────────┘    └─────────┘    └────┬────┘            │
│       │              │              │              │                 │
│       │              │              │              │                 │
│  30 FPS         Blob detect    Accumulate    ML classify             │
│  BGR frames     & centroid     points        SVM model               │
│                                                   │                  │
│                                                   ▼                  │
│                                            ┌─────────────┐           │
│                                            │  Display    │           │
│                                            │  Manager    │           │
│                                            └─────────────┘           │
│                                                   │                  │
│                              ┌────────────────────┼───────────┐      │
│                              │                    │           │      │
│                              ▼                    ▼           ▼      │
│                         ┌────────┐          ┌────────┐  ┌────────┐   │
│                         │ HDMI   │          │  OLED  │  │Headless│   │
│                         │ Screen │          │ Screen │  │  Logs  │   │
│                         └────────┘          └────────┘  └────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Hardware Requirements

### Minimum Setup (~$60-80)

| Component | Model | Estimated Cost | Notes |
|-----------|-------|----------------|-------|
| **Raspberry Pi** | Zero 2 W | ~$15 | Or Pi 3B+/4 if you have one |
| **NoIR Camera** | Pi Camera V2 NoIR | ~$25 | Must be NoIR (no IR filter) |
| **IR LEDs** | 850nm IR LEDs (x6) | ~$5 | Or IR LED ring module |
| **Display** | SSD1306 OLED 128x64 | ~$8 | Or use HDMI monitor |
| **Resistors** | 100Ω (x6) | ~$1 | For IR LEDs |
| **Power** | 5V 2.5A PSU | ~$8 | Official Pi power supply |
| **Storage** | 16GB+ microSD | ~$8 | Class 10 recommended |
| **Wand** | Universal Interactive Wand | ~$65 | From Universal Orlando/Hollywood |

### Optional Upgrades

| Component | Purpose | Cost |
|-----------|---------|------|
| Pi 4 (4GB) | Faster processing | ~$55 |
| 2.8" TFT Display | Larger color screen | ~$15 |
| 3D printed case | Clean enclosure | ~$5-10 |
| Heatsinks | Prevent throttling | ~$3 |

---

## Wiring Guide

### IR LED Circuit

The IR LEDs illuminate the wand tip. We'll wire 6 LEDs in parallel with current-limiting resistors.

```
                    WIRING DIAGRAM
    ═══════════════════════════════════════════════════════

    Raspberry Pi GPIO                    IR LED Array
    ─────────────────                    ────────────

                                         ┌─────────────────────┐
    Pin 2 (5V) ●────────────────────────▶│        5V           │
                                         │                     │
                                         │   ┌──[100Ω]──(LED)──┤
                                         │   │                 │
                                         │   ├──[100Ω]──(LED)──┤
                                         │   │                 │
                                         │   ├──[100Ω]──(LED)──┤
                                         │   │                 │
                                         │   ├──[100Ω]──(LED)──┤
                                         │   │                 │
                                         │   ├──[100Ω]──(LED)──┤
                                         │   │                 │
                                         │   └──[100Ω]──(LED)──┤
                                         │                     │
    Pin 6 (GND) ●───────────────────────▶│        GND         │
                                         │                     │
                                         └─────────────────────┘

    LED Symbol:   ──►|──   (Anode ► Cathode)
                     ↑
                 Longer leg

    NOTES:
    • 850nm IR LEDs (not visible to human eye)
    • 100Ω resistors limit current to ~30mA per LED
    • Arrange LEDs in a ring around the camera
    • LEDs should point in same direction as camera
```

### Camera Connection

```
    Pi Camera Connection (15-pin FFC Cable)
    ════════════════════════════════════════

    ┌─────────────────────────────────────┐
    │         Raspberry Pi                │
    │                                     │
    │   ┌─────────────────────────────┐   │
    │   │ CAMERA  (lift tab, insert,  │   │
    │   │  PORT    push tab down)     │   │
    │   └─────────────────────────────┘   │
    │                 │                   │
    └─────────────────│───────────────────┘
                      │
                      │  15-pin ribbon cable
                      │  (blue side faces HDMI port)
                      │
    ┌─────────────────│───────────────────┐
    │                 │                   │
    │   ┌─────────────────────────────┐   │
    │   │         CAMERA              │   │
    │   │    ┌─────────────────┐      │   │
    │   │    │  ●  NoIR Lens   │      │   │
    │   │    └─────────────────┘      │   │
    │   └─────────────────────────────┘   │
    │                                     │
    │         Pi NoIR Camera V2           │
    └─────────────────────────────────────┘

    For Pi Zero: Use camera adapter cable (standard→mini)
```

### OLED Display (I2C)

```
    SSD1306 OLED Display Connection
    ════════════════════════════════

    Raspberry Pi                    OLED Display
    ────────────                    ────────────
                                    
    Pin 1  (3.3V)  ●───────────────▶ VCC
    Pin 3  (SDA)   ●───────────────▶ SDA
    Pin 5  (SCL)   ●───────────────▶ SCL
    Pin 9  (GND)   ●───────────────▶ GND


    ┌──────────────────────────────────────────┐
    │            GPIO PINOUT REFERENCE         │
    ├──────────────────────────────────────────┤
    │                                          │
    │     3V3  (1) (2)  5V                     │
    │    SDA   (3) (4)  5V    ◄── IR LEDs      │
    │    SCL   (5) (6)  GND   ◄── IR LEDs      │
    │    GP4   (7) (8)  TXD                    │
    │    GND   (9) (10) RXD                    │
    │   GP17  (11) (12) GP18                   │
    │   GP27  (13) (14) GND                    │
    │   GP22  (15) (16) GP23                   │
    │    3V3  (17) (18) GP24                   │
    │   MOSI  (19) (20) GND                    │
    │   MISO  (21) (22) GP25                   │
    │   SCLK  (23) (24) CE0                    │
    │    GND  (25) (26) CE1                    │
    │                                          │
    └──────────────────────────────────────────┘
```

### Complete Physical Assembly

```
    ASSEMBLED VIEW (Top-Down)
    ═════════════════════════

              IR LED Ring
            ┌─────────────┐
            │  ●   ●   ●  │
            │             │
            │ ●  ┌───┐  ● │  ◄── IR LEDs surround camera
            │    │CAM│    │
            │ ●  └───┘  ● │
            │             │
            │  ●   ●   ●  │
            └──────┬──────┘
                   │
                   │ Ribbon cable
                   │
            ┌──────┴──────┐
            │             │
            │  Raspberry  │
            │     Pi      │
            │             │
            │  ┌──────┐   │
            │  │ OLED │   │  ◄── Display shows spell name
            │  └──────┘   │
            └─────────────┘


    SIDE VIEW
    ═════════

    Camera + IR LEDs    Pi + Display
         │                  │
         ▼                  ▼
    ┌─────────┐        ┌─────────┐
    │ ● CAM ● │========│ Pi    ○ │
    │ ●     ● │        │ ┌────┐  │
    └─────────┘        │ │OLED│  │
         │             │ └────┘  │
         │             └─────────┘
         │                  │
         └──────────────────┘
           Mount 30-50cm from
           casting area
```

---

## Software Installation

### 1. Prepare Raspberry Pi OS

```bash
# Download and flash Raspberry Pi OS Lite (64-bit) to SD card
# Use Raspberry Pi Imager: https://www.raspberrypi.com/software/

# Enable SSH and set WiFi during imaging, or:
sudo raspi-config
# → Interface Options → SSH → Enable
# → Interface Options → Camera → Enable
# → Interface Options → I2C → Enable (for OLED)
```

### 2. Clone and Install

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    python3-pip \
    python3-opencv \
    python3-numpy \
    python3-pygame \
    libatlas-base-dev \
    i2c-tools

# For Pi Camera support
sudo apt install -y python3-picamera2

# Clone this repository
git clone https://github.com/yourusername/wand-spellcaster.git
cd wand-spellcaster

# Install Python dependencies
pip3 install -r requirements.txt

# Create models directory
mkdir -p models
```

### 3. Test Camera

```bash
# Test camera is working
libcamera-hello --timeout 5000

# If you see video output, camera is working!
# NoIR cameras will show a slightly purple tint in normal light
```

### 4. Test IR LEDs

```bash
# Your phone camera can see IR light!
# Power on the Pi, point your phone at the IR LEDs
# You should see a purple/pink glow through the phone screen
```

---

## Usage

### Basic Usage

```bash
cd wand-spellcaster/src

# Run with auto-detected display
python3 main.py

# Run in debug mode (shows camera feed and tracking)
python3 main.py --debug

# Run calibration to set IR threshold
python3 main.py --calibrate
```

### Calibration Mode

First-time setup requires calibration:

```bash
python3 main.py --calibrate
```

1. Point your wand at the camera from ~1 meter away
2. Adjust the "IR Threshold" slider until only the wand tip is highlighted
3. Adjust "Min Area" and "Max Area" if needed
4. Press 'Q' to save and exit

### Casting Spells

1. Stand 30-100cm from the camera
2. Point your wand at the camera
3. Draw the spell pattern in the air (see [Supported Spells](#supported-spells))
4. Hold still briefly when finished
5. The detected spell appears on screen!

---

## Configuration

Edit `config/settings.yaml` to customize:

```yaml
camera:
  ir_threshold: 200    # Increase if getting false detections
  
gesture:
  min_confidence: 0.7  # Decrease if spells aren't being recognized
  
display:
  theme: gryffindor    # gryffindor, slytherin, ravenclaw, hufflepuff
```

### Environment Variables

```bash
export WAND_IR_THRESHOLD=180
export WAND_DISPLAY_TYPE=pygame
export WAND_THEME=slytherin
```

---

## Supported Spells

Draw these patterns with your wand:

| Spell | Pattern | Description |
|-------|---------|-------------|
| **Alohomora** | ↻ (clockwise circle) | Unlocking Charm |
| **Revelio** | ↺ (counter-clockwise circle) | Revealing Charm |
| **Lumos** | ↑ (upward flick) | Wand-Lighting Charm |
| **Nox** | ↓ (downward flick) | Counter to Lumos |
| **Incendio** | ↗ (diagonal wave up) | Fire-Making Spell |
| **Aguamenti** | ~ (S-curve) | Water-Making Spell |
| **Wingardium Leviosa** | → then ↑ (swish and flick) | Levitation Charm |
| **Arresto Momentum** | ← → (horizontal sweep) | Slowing Charm |

```
    SPELL PATTERNS REFERENCE
    ════════════════════════

    Alohomora          Revelio           Lumos            Nox
       ╭───╮            ╭───╮              │                │
      │     │          │     │             │                │
      │  ●  │ CW       │  ●  │ CCW         ●                ▼
      │     │          │     │             │                │
       ╰───╯            ╰───╯              ▲                ●

    Incendio        Aguamenti      Wingardium        Arresto
                                    Leviosa          Momentum
        ●               ╭            ───●                    
       ╱               ╱                │            ●───────●
      ╱               ╱                 │
     ╱               ╰╮                 ▲
    ●                  ╲
                        ●
```

---

## Troubleshooting

### Camera Issues

**Problem:** "Failed to open camera"
```bash
# Check camera is detected
vcgencmd get_camera
# Should show: supported=1 detected=1

# Check camera cable is secure (blue side toward HDMI)
# Try rebooting
sudo reboot
```

**Problem:** No wand detection
```bash
# Run calibration mode
python3 main.py --calibrate

# Lower the IR threshold
# Check IR LEDs are working (use phone camera)
# Ensure wand has retroreflective tip (Universal wand, not Noble Collection)
```

### Display Issues

**Problem:** "No display found"
```bash
# For headless operation
python3 main.py  # Will auto-detect and use logging

# For OLED, check I2C
i2cdetect -y 1
# Should show device at address 0x3C

# For pygame/HDMI, ensure X is running
startx
# Then run from the desktop terminal
```

### Recognition Issues

**Problem:** Wrong spells detected
- Increase `min_confidence` in config (e.g., 0.8)
- Practice the spell patterns (see reference above)
- Ensure good lighting (not too much ambient IR)

**Problem:** Spells not recognized
- Decrease `min_confidence` (e.g., 0.6)
- Make larger, clearer gestures
- Ensure wand tip is visible throughout the gesture

---

## Future Phases

### Phase 2: Voice Output (Planned)

```python
# Coming soon - placeholder code already in place
# Will add text-to-speech to announce spell names
```

### Phase 2: Two-Player Duel Mode (Planned)

```
    TWO-PLAYER ARCHITECTURE (PHASE 2)
    ══════════════════════════════════

    ┌─────────────────┐         ┌─────────────────┐
    │   PLAYER 1      │         │   PLAYER 2      │
    │   ┌─────────┐   │  WiFi   │   ┌─────────┐   │
    │   │ Pi + Cam│◄──┼────────►┼──▶│ Pi + Cam│   │
    │   └────┬────┘   │  Sync   │   └────┬────┘   │
    │        │        │         │        │        │
    │   ┌────▼────┐   │         │   ┌────▼────┐   │
    │   │ Display │   │         │   │ Display │   │
    │   └─────────┘   │         │   └─────────┘   │
    └─────────────────┘         └─────────────────┘

    DUEL MECHANICS:
    • Attack beats Neutral
    • Defense beats Attack  
    • Neutral beats Defense
    • Ties resolved by confidence score
```

---

## Project Structure

```
wand-spellcaster/
├── src/
│   ├── main.py              # Application entry point
│   ├── wand_tracker.py      # IR camera and blob detection
│   ├── spell_recognizer.py  # ML gesture recognition
│   ├── display_manager.py   # Screen output handling
│   └── config_loader.py     # Configuration management
├── config/
│   └── settings.yaml        # User configuration
├── models/
│   └── spell_classifier.pkl # Trained ML model (auto-generated)
├── docs/
│   └── (additional documentation)
├── requirements.txt
└── README.md
```

---

## Contributing

Contributions welcome! Areas that need help:

- [ ] Training data for better spell recognition
- [ ] 3D printable enclosure designs
- [ ] Additional display support (e-ink, LED matrix)
- [ ] Phase 2 implementation (voice, multiplayer)

---

## License

MIT License - See LICENSE file for details.

---

## Acknowledgments

- Universal Orlando for creating the amazing interactive wand experience
- The Raspberry Potter project for pioneering home wand detection
- The OpenCV and scikit-learn communities

---

*"It is not our abilities that show what we truly are. It is our choices."* - Albus Dumbledore
