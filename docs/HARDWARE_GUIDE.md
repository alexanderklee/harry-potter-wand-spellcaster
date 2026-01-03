# Hardware Assembly Guide

## Bill of Materials (BOM)

### Essential Components

| Qty | Component | Specifications | Example Product | Est. Cost |
|-----|-----------|---------------|-----------------|-----------|
| 1 | Raspberry Pi | Zero 2 W, 3B+, or 4 | Official retailers | $15-55 |
| 1 | Pi NoIR Camera | V2 or V3, No IR filter | Pi NoIR Camera V2 | $25 |
| 1 | Camera Cable | 15-pin FFC (Zero needs adapter) | Standard or Zero adapter | $3-5 |
| 6 | IR LEDs | 850nm, 5mm, 20-50mA | Chanzon 850nm IR LED | $5/pack |
| 6 | Resistors | 100Ω, 1/4W | Standard carbon film | $1 |
| 1 | MicroSD Card | 16GB+ Class 10 | SanDisk Ultra | $8 |
| 1 | Power Supply | 5V 2.5A+ USB | Official Pi PSU | $8 |
| 1 | Wand | Universal Interactive | From Universal Orlando | $65 |

### Display Options (Choose One)

| Option | Component | Notes | Cost |
|--------|-----------|-------|------|
| A | HDMI Monitor | Any HDMI display you have | $0-50 |
| B | SSD1306 OLED | 128x64, I2C, 0.96" | $8 |
| C | ST7789 TFT | 240x240, SPI, 1.3" | $12 |
| D | Headless | No display, logging only | $0 |

### Optional but Recommended

| Qty | Component | Purpose | Cost |
|-----|-----------|---------|------|
| 1 | Heatsink kit | Prevents thermal throttling | $3 |
| 1 | Case | Protection and mounting | $5-15 |
| 1 | IR LED module | Pre-built alternative to loose LEDs | $8 |
| 1 | Protoboard | Cleaner LED wiring | $2 |

---

## IR LED Circuit Design

### Theory

The Universal wand's tip is **retroreflective** - it bounces light back toward its source. We illuminate it with invisible IR light (850nm wavelength) and detect the reflection with a NoIR camera.

**Key parameters:**
- LED forward voltage: ~1.2-1.5V (typical for IR LEDs)
- LED forward current: 20-50mA (we'll target 30mA)
- Supply voltage: 5V from Pi
- Resistor calculation: R = (Vsupply - Vforward) / Iforward
  - R = (5V - 1.3V) / 0.030A = 123Ω → Use 100Ω (gives ~37mA, safe)

### Circuit Schematic

```
                          IR LED ARRAY CIRCUIT
    ════════════════════════════════════════════════════════════════

    5V Rail (Pi Pin 2 or 4)
         │
         │
         ├───────┬───────┬───────┬───────┬───────┬───────┐
         │       │       │       │       │       │       │
         │      ┌┴┐     ┌┴┐     ┌┴┐     ┌┴┐     ┌┴┐     ┌┴┐
         │      │ │     │ │     │ │     │ │     │ │     │ │
         │      │ │100Ω │ │100Ω │ │100Ω │ │100Ω │ │100Ω │ │100Ω
         │      │ │     │ │     │ │     │ │     │ │     │ │
         │      └┬┘     └┬┘     └┬┘     └┬┘     └┬┘     └┬┘
         │       │       │       │       │       │       │
         │       ▼       ▼       ▼       ▼       ▼       ▼
         │      ─┬─     ─┬─     ─┬─     ─┬─     ─┬─     ─┬─
         │      \ /     \ /     \ /     \ /     \ /     \ /
         │      ─┴─     ─┴─     ─┴─     ─┴─     ─┴─     ─┴─
         │       │       │       │       │       │       │
         │       │       │       │       │       │       │
         └───────┴───────┴───────┴───────┴───────┴───────┴───────┐
                                                                  │
    GND Rail (Pi Pin 6, 9, 14, 20, 25, 30, 34, or 39) ◄───────────┘


    LED Symbol Guide:
    ─┬─
    \ /  = LED (arrow shows current flow direction)
    ─┴─
     │
     ▼
    (shorter leg / flat side of LED = cathode = connects to GND)
```

### Soldering Instructions

**Tools needed:**
- Soldering iron (25-40W)
- Solder (60/40 or lead-free)
- Wire cutters
- Heat shrink tubing (optional)
- Protoboard or perfboard (optional)

**Step-by-step:**

1. **Identify LED polarity**
   - Longer leg = Anode (+)
   - Shorter leg or flat side of lens = Cathode (-)

2. **Attach resistors to LEDs**
   ```
   For each LED:
   
   [Resistor] ─── [Anode (+)] LED [Cathode (-)] ─── 
   
   Wrap resistor leg around anode leg, solder
   ```

3. **Connect in parallel**
   ```
   All resistor ends → tie together → connect to 5V
   All cathode ends → tie together → connect to GND
   ```

4. **Create LED ring mount**
   - Cut a small circle of cardboard/3D print a ring
   - Poke 6 holes evenly spaced
   - Insert LEDs pointing forward (same direction as camera)
   - Center hole for camera lens

### Pre-built Alternative

If you prefer not to solder, use a pre-built IR illuminator:

**Options:**
- "IR Illuminator Ring" for CCTV cameras (~$8)
- "48 LED IR Illuminator Board" (~$5)
- Ensure it's 850nm (not 940nm which is harder for cameras to see)

---

## Camera Assembly

### Pi Camera Connection

**Standard Raspberry Pi (3B+, 4):**

```
    ┌─────────────────────────────────────────┐
    │                                         │
    │     USB   USB   ETH    HDMI   HDMI      │
    │     ┌─┐   ┌─┐   ┌──┐   ┌───┐  ┌───┐    │
    │     └─┘   └─┘   └──┘   └───┘  └───┘    │
    │                                         │
    │  ┌───────────────────────────────────┐  │
    │  │                                   │  │
    │  │           CAMERA PORT             │  │
    │  │     (lift black tab, insert       │  │
    │  │      cable, press tab down)       │  │
    │  │                                   │  │
    │  └───────────────────────────────────┘  │
    │          ▲                              │
    │          │                              │
    │     Blue/silver side of ribbon          │
    │     faces toward HDMI ports             │
    │                                         │
    └─────────────────────────────────────────┘
```

**Raspberry Pi Zero (needs adapter cable):**

```
    Standard Pi Camera         Pi Zero Adapter Cable         Pi Zero
    (22-pin connector)         (22-pin to 15-pin)       (15-pin connector)
          │                          │                        │
          ▼                          ▼                        ▼
    ┌───────────┐              ┌───────────┐            ┌───────────┐
    │  ░░░░░░░  │───cable──────│  ░░░░░░░  │───cable────│   ░░░░░   │
    │  camera   │              │  adapter  │            │  Pi Zero  │
    └───────────┘              └───────────┘            └───────────┘
```

### Camera + IR LED Ring Assembly

**3D Print Option:**

If you have a 3D printer, print a camera mount with IR LED holes:
- Search Thingiverse for "Pi camera IR ring mount"
- Or design your own with camera center hole + 6 LED holes around it

**DIY Cardboard Option:**

```
    1. Cut cardboard circle (~5cm diameter)
    
    2. Mark camera center and 6 LED positions:
    
              ○
           ○     ○
              □      ← Camera here
           ○     ○
              ○
    
    3. Cut/punch holes:
       - Center: match camera lens size (~8mm)
       - LEDs: match LED size (~5mm)
    
    4. Insert components:
       - Camera lens through center (or mount behind)
       - LEDs in surrounding holes, all pointing forward
```

---

## Display Wiring

### Option A: HDMI Monitor

No wiring needed - just connect HDMI cable!

### Option B: SSD1306 OLED (I2C)

```
    OLED Display          Raspberry Pi
    ════════════          ════════════

    VCC  ●─────────────── Pin 1  (3.3V)
    GND  ●─────────────── Pin 6  (GND)
    SCL  ●─────────────── Pin 5  (GPIO3/SCL)
    SDA  ●─────────────── Pin 3  (GPIO2/SDA)


    Physical connection:

    OLED Module:              Pi GPIO Header:
    ┌─────────────┐           ┌─────────────────────┐
    │             │           │ 3V3 (1)   (2) 5V    │
    │  ┌───────┐  │           │ SDA (3)   (4) 5V    │◄── IR LED 5V
    │  │DISPLAY│  │           │ SCL (5)   (6) GND   │◄── IR LED GND
    │  └───────┘  │           │     (7)   (8)       │
    │             │           │ GND (9)   (10)      │
    │ VCC GND SCL SDA         │     ...             │
    │  │   │   │   │          └─────────────────────┘
    └──┼───┼───┼───┼──┘
       │   │   │   │
       │   │   │   └──────────────────┘
       │   │   └─────────────────┘
       │   └────────────────┘
       └───────────────┘
```

**Enable I2C:**
```bash
sudo raspi-config
# Interface Options → I2C → Enable

# Verify OLED is detected:
sudo i2cdetect -y 1
# Should show "3c" at address 0x3C
```

### Option C: ST7789 TFT (SPI)

```
    TFT Display           Raspberry Pi
    ═══════════           ════════════

    VCC  ●─────────────── Pin 17 (3.3V)
    GND  ●─────────────── Pin 20 (GND)
    SCL  ●─────────────── Pin 23 (GPIO11/SCLK)
    SDA  ●─────────────── Pin 19 (GPIO10/MOSI)
    RES  ●─────────────── Pin 22 (GPIO25)
    DC   ●─────────────── Pin 18 (GPIO24)
    CS   ●─────────────── Pin 24 (GPIO8/CE0)
    BLK  ●─────────────── Pin 12 (GPIO18) or 3.3V for always-on
```

**Enable SPI:**
```bash
sudo raspi-config
# Interface Options → SPI → Enable
```

---

## Complete Wiring Summary

### GPIO Pinout Reference

```
    ┌─────────────────────────────────────────────────────────────┐
    │                    RASPBERRY PI GPIO                        │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │   Function        Pin                 Pin        Function   │
    │   ─────────       ───                 ───        ─────────  │
    │                                                             │
    │   3.3V Power      (1)  ●───────●  (2)  5V Power ◄── IR LED │
    │   I2C SDA (OLED)  (3)  ●───────●  (4)  5V Power             │
    │   I2C SCL (OLED)  (5)  ●───────●  (6)  Ground  ◄── IR LED  │
    │   GPIO 4          (7)  ●───────●  (8)  UART TX              │
    │   Ground          (9)  ●───────●  (10) UART RX              │
    │   GPIO 17         (11) ●───────●  (12) GPIO 18 (TFT BLK)    │
    │   GPIO 27         (13) ●───────●  (14) Ground               │
    │   GPIO 22         (15) ●───────●  (16) GPIO 23              │
    │   3.3V Power      (17) ●───────●  (18) GPIO 24 (TFT DC)     │
    │   SPI MOSI (TFT)  (19) ●───────●  (20) Ground               │
    │   SPI MISO        (21) ●───────●  (22) GPIO 25 (TFT RES)    │
    │   SPI SCLK (TFT)  (23) ●───────●  (24) SPI CE0 (TFT CS)     │
    │   Ground          (25) ●───────●  (26) SPI CE1              │
    │   ...             ...              ...  ...                  │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘

    ◄── marks pins used by this project
```

### Connection Checklist

- [ ] Camera ribbon cable connected (blue side toward HDMI)
- [ ] IR LEDs connected: 5V → Resistors → LED anodes, LED cathodes → GND
- [ ] Display connected (I2C or SPI depending on type)
- [ ] Power supply connected (5V 2.5A minimum)

---

## Physical Mounting

### Recommended Positioning

```
    TOP VIEW - CASTING AREA
    ════════════════════════

                          Wall/Shelf
                             │
    ┌────────────────────────┴────────────────────────┐
    │                                                 │
    │                  ┌─────────┐                    │
    │                  │ Camera  │                    │
    │                  │ + LEDs  │                    │
    │                  │   ▼     │                    │
    │                  └────┬────┘                    │
    │                       │                         │
    │                       │  30-100cm               │
    │                       │                         │
    │                       │                         │
    │                  ┌────▼────┐                    │
    │                  │  WAND   │                    │
    │                  │ CASTING │                    │
    │                  │  ZONE   │                    │
    │                  └─────────┘                    │
    │                                                 │
    │                    User                         │
    │                   stands                        │
    │                    here                         │
    │                                                 │
    └─────────────────────────────────────────────────┘


    SIDE VIEW
    ═════════

    Camera+LEDs
        │
        ▼    Angled slightly downward
       ┌──╲
       │   ╲
       │    ╲
       │     ╲
       │      ◯  ← Wand casting zone
       │         
    ───┴─────────────  Floor/Table
    
    Mounting height: ~1-1.5m
    Angle: ~10-20° downward
```

### Enclosure Ideas

**Simple box enclosure:**
```
    ┌─────────────────────────┐
    │  ╔═══════════════════╗  │
    │  ║   ○ ○   CAM   ○ ○ ║  │  ← Front: camera window + LED holes
    │  ║   ○ ○         ○ ○ ║  │
    │  ╚═══════════════════╝  │
    │                         │
    │    ┌───────────────┐    │
    │    │     OLED      │    │  ← Display visible through window
    │    └───────────────┘    │
    │                         │
    └─────────────────────────┘
```

---

## Testing Each Component

### Test 1: Camera

```bash
# Take a test photo
libcamera-still -o test.jpg

# View it (if desktop environment)
gpicview test.jpg
```

### Test 2: IR LEDs

```bash
# IR is invisible to human eyes but phone cameras can see it!
# 1. Power on the Pi
# 2. Open your phone's camera
# 3. Point at IR LEDs
# 4. You should see purple/pink glow
```

### Test 3: OLED Display

```bash
# Install test dependencies
pip3 install luma.oled

# Run test
python3 -c "
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

img = Image.new('1', (128, 64), 0)
draw = ImageDraw.Draw(img)
draw.text((10, 25), 'Hello Wizard!', fill=1)
device.display(img)
"
```

### Test 4: Full System

```bash
cd wand-spellcaster/src
python3 main.py --debug --calibrate
```

---

## Troubleshooting Hardware

| Symptom | Possible Cause | Solution |
|---------|---------------|----------|
| Camera not detected | Loose ribbon cable | Reseat cable, blue side toward HDMI |
| No IR illumination | LED wiring wrong | Check polarity, verify with phone camera |
| LEDs dim | Resistor value too high | Use 100Ω or lower |
| OLED blank | I2C not enabled | `sudo raspi-config` → I2C → Enable |
| OLED shows wrong content | Wrong I2C address | Run `i2cdetect -y 1`, update code if not 0x3C |
| Pi not booting | Insufficient power | Use official 5V 2.5A+ supply |
| Pi throttling | Overheating | Add heatsinks, improve ventilation |

---

## Next Steps

Once hardware is assembled and tested:

1. Run calibration: `python3 main.py --calibrate`
2. Adjust IR threshold until only wand tip is detected
3. Practice spell gestures
4. Enjoy your home spell-casting station! 🪄
