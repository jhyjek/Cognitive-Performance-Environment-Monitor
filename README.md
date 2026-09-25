# Cognitive Performance Environment Monitor

A real-time embedded IoT system that monitors indoor air quality (eCO₂) and ambient
noise, giving occupants immediate visual and auditory feedback when conditions may
be hurting focus and productivity, and logging the data to the cloud for remote
tracking.

Built for CS 4432 (Sensors & IoT) at the University of Minnesota Duluth.

**Team:** Abdullah Sahto, Jacob Hyjek

## Overview

Research links elevated indoor CO₂ levels and excessive noise to measurable drops
in focus and problem-solving performance, but these conditions are invisible to
the people affected by them. This device continuously samples both, classifies the
environment as **safe / warning / critical**, and provides:

- A color-coded RGB LED (traffic-light style)
- An audible buzzer alert for degraded conditions
- A live status readout on a 16x2 LCD
- Remote logging to a ThingSpeak dashboard for tracking trends over time

## Hardware

| Component | Purpose |
|---|---|
| Raspberry Pi 5 | Main controller, runs all logic locally |
| CCS811 | eCO₂ / TVOC air-quality sensor (I²C) |
| MAX4466 (via PCF8591 ADC) | Ambient sound level sensor |
| RGB LED (traffic-light module) | Visual status indicator |
| Buzzer module | Audible alert |
| LCD1602 (I²C) | Live sensor readout and status display |

## How It Works

1. The Pi polls the CCS811 (eCO₂) and the sound sensor (via the PCF8591 ADC) at
   regular intervals.
2. A threshold-based classifier compares both readings against safe/warning
   thresholds and determines an overall status: `GREEN`, `YELLOW`, or `RED`.
3. The status drives the RGB LED and buzzer, and updates the LCD with live
   readings.
4. Every 60 seconds, the current readings and status are pushed to a ThingSpeak
   channel for remote monitoring and historical tracking.
5. Hardware initialization is wrapped in error handling so the system degrades
   gracefully (e.g., continues running sensor logic even if the LCD fails to
   initialize) rather than crashing outright.

## Setup

### Requirements

- Raspberry Pi 5 (or any Pi with I²C enabled)
- Python 3.9+
- I²C enabled via `raspi-config`

### Installation

```bash
git clone https://github.com/<your-username>/cognitive-environment-monitor.git
cd cognitive-environment-monitor
pip install -r requirements.txt
cp .env.example .env   # then add your own ThingSpeak API key
python monitor.py
```

### Configuration

Wiring, thresholds, and LCD settings live in `config.py`. Adjust GPIO pin numbers
and threshold values there to match your own build.

Your ThingSpeak Write API Key should be set as an environment variable
(`THINGSPEAK_API_KEY`) rather than hardcoded. See `.env.example`.

## Alert Thresholds

| Status | Condition |
|---|---|
| 🟢 Green | eCO₂ and noise both within safe range |
| 🟡 Yellow | Either reading enters the warning range |
| 🔴 Red | Either reading exceeds the critical threshold |

## Ethical Considerations

The sound sensor measures ambient decibel level only. It does not record or
process intelligible audio, and no raw audio is ever stored or transmitted. The
system is designed purely as an environmental health indicator, not as a
surveillance tool, and this purpose is communicated clearly to anyone using the
device.

## Future Improvements

- Replace fixed thresholds with a calibration routine per room
- Add a small web dashboard instead of relying solely on ThingSpeak
- Log historical data locally for offline analysis

## License

MIT
