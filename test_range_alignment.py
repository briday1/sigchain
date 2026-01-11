#!/usr/bin/env python3
"""Test script to verify range alignment in matched filtering."""

import numpy as np
import sys
sys.path.insert(0, '/workspaces/sigchain')

from sigchain.blocks import LFMGenerator, StackPulses, RangeCompress

# Create a simple test case with zero noise for clarity
gen = LFMGenerator(
    num_pulses=4,
    pulse_duration=10e-6,
    sample_rate=10e6,
    bandwidth=5e6,
    target_delay=20e-6,  # 20 microseconds
    target_doppler=0,
    noise_power=0.0,  # No noise for cleaner test
)

signal = gen.process()
print(f"Target delay: {signal.metadata['target_delay']*1e6:.2f} µs")
print(f"Sample rate: {signal.metadata['sample_rate']/1e6:.1f} MHz")
print(f"Samples per pulse: {signal.metadata['samples_per_pulse']}")
print(f"Delay in samples: {int(signal.metadata['target_delay'] * signal.metadata['sample_rate'])}")

# Stack pulses
stacker = StackPulses()
stacked = stacker.process(signal)

# Apply range compression WITHOUT oversampling first
range_comp = RangeCompress(window=None, oversample_factor=1)
compressed = range_comp(stacked)

# Find peak in first pulse
first_pulse = np.abs(compressed.data[0, :])
peak_idx = np.argmax(first_pulse)
peak_value = first_pulse[peak_idx]

print(f"\nWithout oversampling:")
print(f"Peak at sample: {peak_idx}")
print(f"Peak value: {peak_value:.2f}")

# Calculate range from peak
c = 3e8
peak_range_m = peak_idx / compressed.sample_rate * c / 2
expected_range_m = signal.metadata['target_delay'] * c / 2

print(f"Expected range: {expected_range_m:.2f} m")
print(f"Detected range: {peak_range_m:.2f} m")
print(f"Error: {peak_range_m - expected_range_m:.2f} m")

# Now try with oversampling
range_comp2 = RangeCompress(window=None, oversample_factor=2)
compressed2 = range_comp2(stacked)

first_pulse2 = np.abs(compressed2.data[0, :])
peak_idx2 = np.argmax(first_pulse2)
peak_value2 = first_pulse2[peak_idx2]

print(f"\nWith 2x oversampling:")
print(f"Peak at sample: {peak_idx2}")
print(f"Peak value: {peak_value2:.2f}")
peak_range_m2 = peak_idx2 / compressed2.sample_rate * c / 2
print(f"Detected range: {peak_range_m2:.2f} m")
print(f"Error: {peak_range_m2 - expected_range_m:.2f} m")
