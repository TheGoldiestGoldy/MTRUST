#!/usr/bin/env python3
"""Validate and summarize genuine isolated-client *whole-frame* elapsed durations.

CSV: timestamp_s,frame_ms[,cpu_pct,gpu_pct,rss_bytes,vram_bytes].
The timestamp is the monotonic capture-clock time in SECONDS (origin arbitrary).
A frame_ms is an elapsed WHOLE frame duration in MILLISECONDS, not an
OpenGL GPU timer or Minecraft render-thread CPU scope. No synthetic results
may be presented as in-game measurements.

Reject rather than drop invalid timestamps, durations or discontinuities.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def nearest_rank(values, percentile):
    ordered = sorted(values)
    if not ordered:
        raise ValueError("No observations")
    return ordered[max(0, math.ceil(percentile * len(ordered)) - 1)]


def finite_number(value, field, row):
    if value is None or str(value).strip() == "":
        raise ValueError(f"row {row}: missing {field}")
    try:
        number = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"row {row}: invalid {field}") from exc
    if not math.isfinite(number):
        raise ValueError(f"row {row}: nonfinite {field}")
    return number


def summarize(rows, warmup_s=0, min_duration_s=1.0, max_gap_s=1.0):
    """Return nearest-rank frame-time percentiles and mean-worst-1%-frame FPS.

    Warmup is measured FROM FIRST timestamp, not Unix epoch/clock zero.
    A timestamp jump > max(max_gap_s, 5 * adjacent frame durations) is invalid:
    this catches dropped capture intervals, but genuine long hangs may survive
    when their frame_ms accounts for the gap. Save raw captures for review.
    CLI requires at least 30 post-warmup seconds by default.
    """
    if not math.isfinite(warmup_s) or warmup_s < 0:
        raise ValueError("warmup_s must be finite and nonnegative")
    if not math.isfinite(min_duration_s) or min_duration_s <= 0:
        raise ValueError("min_duration_s must be finite and positive")
    if not math.isfinite(max_gap_s) or max_gap_s <= 0:
        raise ValueError("max_gap_s must be finite and positive")
    all_readings = []
    previous_time = None
    previous_ms = None
    extras = ("cpu_pct", "gpu_pct", "rss_bytes", "vram_bytes")
    for number, row in enumerate(rows, 1):
        if not isinstance(row, dict) or None in row:
            raise ValueError(f"row {number}: malformed CSV column count")
        time_s = finite_number(row.get("timestamp_s"), "timestamp_s", number)
        frame_ms = finite_number(row.get("frame_ms"), "frame_ms", number)
        if time_s < 0:
            raise ValueError(f"row {number}: negative timestamp_s")
        if frame_ms <= 0:
            raise ValueError(f"row {number}: frame_ms must be positive")
        if previous_time is not None:
            delta = time_s - previous_time
            if delta <= 0:
                raise ValueError(f"row {number}: timestamps must be strictly increasing")
            if delta > max(max_gap_s, 5 * max(previous_ms, frame_ms) / 1000):
                raise ValueError(f"row {number}: capture timestamp gap {delta:.3f}s")
        parsed = {}
        for col in extras:
            raw = row.get(col, "")
            if raw is not None and str(raw).strip():
                value = finite_number(raw, col, number)
                if value < 0:
                    raise ValueError(f"row {number}: negative {col}")
                parsed[col] = value
        all_readings.append((time_s, frame_ms, parsed))
        previous_time, previous_ms = time_s, frame_ms
    if not all_readings:
        raise ValueError("No captured frames")
    start = all_readings[0][0]
    readings = [r for r in all_readings if r[0] - start >= warmup_s]
    if len(readings) < 100:
        raise ValueError("At least 100 post-warmup frames required")
    duration = readings[-1][0] - readings[0][0]
    if duration < min_duration_s:
        raise ValueError(f"Post-warmup duration {duration:.3f}s below {min_duration_s:.3f}s")
    frame_times = [r[1] for r in readings]
    n_worst = max(1, math.ceil(len(frame_times) * 0.01))
    slowest = sorted(frame_times, reverse=True)[:n_worst]
    result = {
        "samples": len(frame_times),
        "capture_duration_seconds": duration,
        "total_capture_seconds": all_readings[-1][0] - start,
        "warmup_seconds_excluded": warmup_s,
        "frame_metric": "whole-frame elapsed ms (not GPU or render-thread CPU time)",
        "timestamp_unit": "monotonic seconds, relative warmup from first sample",
        "frame_ms_median": nearest_rank(frame_times, 0.50),
        "frame_ms_p95": nearest_rank(frame_times, 0.95),
        "frame_ms_p99": nearest_rank(frame_times, 0.99),
        "one_percent_low_fps": 1000 / (sum(slowest) / len(slowest)),
        "one_percent_low_frames": n_worst,
        "method": "Nearest-rank frame time; 1% low FPS = 1000 / arithmetic mean of slowest ceil(1% of frames)",
    }
    for col in extras:
        values = [r[2][col] for r in readings if col in r[2]]
        if values:
            result[col + "_median"] = nearest_rank(values, 0.50)
            result[col + "_samples"] = len(values)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="real isolated-client CSV capture")
    parser.add_argument("--warmup-seconds", type=float, default=30)
    parser.add_argument("--min-measure-seconds", type=float, default=30)
    parser.add_argument("--max-gap-seconds", type=float, default=1.0)
    parser.add_argument("--metadata", type=Path, help="optional matching isolated capture provenance JSON")
    args = parser.parse_args()
    with args.input.open(newline="", encoding="utf-8") as f:
        readings = list(csv.DictReader(f))
    result = summarize(readings, args.warmup_seconds, args.min_measure_seconds, args.max_gap_seconds)
    if args.metadata:
        metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict) or metadata.get("capture_kind") != "whole_frame":
            raise ValueError("Metadata capture_kind must be whole_frame, not GPU or CPU render scopes")
        if metadata.get("timestamp_unit") != "s" or metadata.get("frame_unit") != "ms":
            raise ValueError("Metadata clock units must be timestamp_unit=s and frame_unit=ms")
        result["capture_metadata"] = metadata
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
