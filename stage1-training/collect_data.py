"""
HVAC Fan Data Collector — Serial to CSV Logger
================================================
Reads serial data from ESP32 and saves to a CSV file.

Usage:
    python collect_data.py <label> --port <COM_PORT> [--duration <minutes>]

Examples:
    python collect_data.py normal --port COM5 --duration 20
    python collect_data.py warning --port COM5 --duration 10
    python collect_data.py critical --port COM5 --duration 10

Valid labels: normal, normal_low, warning, critical
"""

import serial
import csv
import time
import argparse
import os
import sys
from datetime import datetime

BAUD_RATE = 115200
VALID_LABELS = ["normal", "normal_low", "warning", "critical"]
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CSV_HEADER = [
    "timestamp_ms", "ax", "ay", "az",
    "gx", "gy", "gz", "current_raw", "label"
]


def list_serial_ports():
    """List available serial ports on the system."""
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("[ERROR] No serial ports found!")
        print("  - Is the ESP32 connected via USB?")
        print("  - Do you have the CP2102/CH340 driver installed?")
        return []
    print("\n[INFO] Available serial ports:")
    for p in ports:
        print(f"  {p.device} — {p.description}")
    return [p.device for p in ports]


def collect_data(port: str, label: str, duration_min: float):
    """Main data collection loop."""

    # Create data directory
    os.makedirs(DATA_DIR, exist_ok=True)

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"raw_{label}_{timestamp}.csv"
    filepath = os.path.join(DATA_DIR, filename)

    duration_sec = duration_min * 60
    sample_count = 0
    error_count = 0

    print(f"\n{'='*60}")
    print(f"  HVAC Fan Data Collector")
    print(f"{'='*60}")
    print(f"  Port:     {port}")
    print(f"  Label:    {label}")
    print(f"  Duration: {duration_min} minutes ({duration_sec:.0f} seconds)")
    print(f"  Output:   {filepath}")
    print(f"  Target:   ~{int(duration_sec * 100):,} samples at 100Hz")
    print(f"{'='*60}\n")

    # Wait for user confirmation
    if label == "normal":
        print("[SETUP] Ensure the fan is running CLEAN with NO weights attached.")
    elif label == "normal_low":
        print("[SETUP] Ensure fan is running clean. Hold cardboard")
        print("        near the intake to partially block airflow.")
    elif label == "warning":
        print("[SETUP] Attach a SMALL weight (~10g) to ONE fan blade edge.")
        print("        Use tape to secure a nut, coins, or blu-tack.")
    elif label == "critical":
        print("[SETUP] Attach a HEAVY weight (~25g) to ONE fan blade edge.")
        print("        Use a bolt, multiple coins, or large blu-tack blob.")

    print(f"\n[READY] Press Enter to start collecting '{label}' data...")
    input()

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=2)
        print(f"[SERIAL] Connected to {port} at {BAUD_RATE} baud")
    except serial.SerialException as e:
        print(f"[ERROR] Cannot open {port}: {e}")
        print("\nTroubleshooting:")
        print("  1. Close Arduino IDE Serial Monitor (it locks the port)")
        print("  2. Check the correct COM port number")
        print("  3. Try unplugging and replugging the USB cable")
        list_serial_ports()
        sys.exit(1)

    # Wait for ESP32 READY signal
    print("[SERIAL] Waiting for ESP32 to send READY signal...")
    ready = False
    for _ in range(50):  # Wait up to 10 seconds
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            print(f"  ESP32: {line}")
            if line == "READY":
                ready = True
                break
        except Exception:
            pass

    if not ready:
        print("[WARNING] Did not receive READY signal, starting anyway...")

    # Open CSV and start collecting
    start_time = time.time()
    last_status_time = start_time

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)

        print(f"\n[COLLECTING] Started! Will run for {duration_min} minutes.")
        print(f"  Press Ctrl+C to stop early.\n")

        try:
            while True:
                elapsed = time.time() - start_time
                if elapsed >= duration_sec:
                    print(f"\n[DONE] Duration reached ({duration_min} min).")
                    break

                try:
                    raw = ser.readline()
                    line = raw.decode("utf-8", errors="ignore").strip()
                except Exception:
                    error_count += 1
                    continue

                # Skip non-data lines (progress messages, init messages)
                if not line.startswith("DATA:"):
                    continue

                # Parse: DATA:ts,ax,ay,az,gx,gy,gz,current_raw
                try:
                    parts = line[5:].split(",")
                    if len(parts) != 8:
                        error_count += 1
                        continue

                    # Validate that values are numeric
                    float(parts[1])  # Quick check on ax
                    float(parts[6])  # Quick check on gz
                    int(parts[7])    # Quick check on current_raw

                    writer.writerow(parts + [label])
                    sample_count += 1

                except (ValueError, IndexError):
                    error_count += 1
                    continue

                # Status update every 5 seconds
                now = time.time()
                if now - last_status_time >= 5.0:
                    remaining = duration_sec - elapsed
                    rate = sample_count / elapsed if elapsed > 0 else 0
                    print(
                        f"  [{elapsed:6.1f}s] "
                        f"Samples: {sample_count:>8,} | "
                        f"Rate: {rate:.1f} Hz | "
                        f"Errors: {error_count} | "
                        f"Remaining: {remaining:.0f}s"
                    )
                    last_status_time = now
                    f.flush()

        except KeyboardInterrupt:
            print(f"\n[STOPPED] User interrupted after {time.time() - start_time:.1f}s")

    ser.close()

    # Summary
    elapsed_total = time.time() - start_time
    file_size = os.path.getsize(filepath)
    print(f"\n{'='*60}")
    print(f"  Collection Complete!")
    print(f"{'='*60}")
    print(f"  File:     {filepath}")
    print(f"  Samples:  {sample_count:,}")
    print(f"  Duration: {elapsed_total:.1f} seconds")
    print(f"  Avg Rate: {sample_count / elapsed_total:.1f} Hz")
    print(f"  Errors:   {error_count}")
    print(f"  File Size:{file_size / 1024:.1f} KB")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Collect sensor data from ESP32 for HVAC fan ML training"
    )
    parser.add_argument(
        "label",
        choices=VALID_LABELS,
        help="Data label: normal, normal_low, warning, critical"
    )
    parser.add_argument(
        "--port", "-p",
        required=True,
        help="Serial port (e.g., COM5 on Windows, /dev/ttyUSB0 on Linux)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=10,
        help="Collection duration in minutes (default: 10)"
    )
    parser.add_argument(
        "--list-ports",
        action="store_true",
        help="List available serial ports and exit"
    )

    args = parser.parse_args()

    if args.list_ports:
        list_serial_ports()
        sys.exit(0)

    collect_data(args.port, args.label, args.duration)


if __name__ == "__main__":
    main()
