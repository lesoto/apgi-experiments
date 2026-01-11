"""
Example Data Generator for APGI Framework
Creates realistic sample datasets for testing neural simulators and analysis tools.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import json
from datetime import datetime, timedelta


class ExampleDataGenerator:
    """Generate realistic example data for APGI framework testing."""

    def __init__(self, output_dir: str = "examples/data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sampling_rate = 1000  # Hz
        self.duration = 60  # seconds

    def generate_eeg_data(self, n_channels=8, n_subjects=3):
        """Generate realistic EEG data with multiple channels and subjects."""

        for subject_id in range(1, n_subjects + 1):
            # Time vector
            t = np.linspace(0, self.duration, self.sampling_rate * self.duration)

            # Channel names (standard 10-20 system)
            channel_names = ["Fz", "Cz", "Pz", "Oz", "F3", "F4", "P3", "P4"][
                :n_channels
            ]

            # Generate realistic EEG signals
            data = np.zeros((n_channels, len(t)))

            for i, channel in enumerate(channel_names):
                # Base signal with different frequencies for each channel
                freq = 8 + i * 2  # Alpha to beta range
                signal = 5 * np.sin(2 * np.pi * freq * t)

                # Add some noise
                noise = np.random.normal(0, 2, len(t))

                # Add some slow waves
                slow_wave = 2 * np.sin(2 * np.pi * 0.5 * t)

                # Add occasional spikes (simulating artifacts)
                spike_times = np.random.choice(len(t), size=5, replace=False)
                for spike_time in spike_times:
                    signal[spike_time : spike_time + 10] += np.random.normal(
                        0, 20, min(10, len(t) - spike_time)
                    )

                data[i] = signal + noise + slow_wave

            # Create DataFrame
            df_data = {"timestamp": t}
            for i, channel in enumerate(channel_names):
                df_data[f"channel_{channel}"] = data[i]
            df_data["subject_id"] = f"subject_{subject_id:03d}"

            df = pd.DataFrame(df_data)

            # Save to CSV
            filename = self.output_dir / "eeg" / f"subject_{subject_id:03d}_eeg.csv"
            df.to_csv(filename, index=False)

            # Create metadata
            metadata = {
                "subject_id": f"subject_{subject_id:03d}",
                "recording_date": datetime.now().isoformat(),
                "sampling_rate": self.sampling_rate,
                "duration": self.duration,
                "channels": channel_names,
                "n_samples": len(t),
                "data_type": "EEG",
                "units": "microvolts",
                "reference": "common_average",
                "filter_settings": {"highpass": 0.1, "lowpass": 100, "notch": 50},
            }

            metadata_file = (
                self.output_dir / "eeg" / f"subject_{subject_id:03d}_metadata.json"
            )
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

    def generate_pupillometry_data(self, n_subjects=3):
        """Generate realistic pupillometry data."""

        for subject_id in range(1, n_subjects + 1):
            # Time vector (lower sampling rate for pupillometry)
            sampling_rate = 250  # Hz
            t = np.linspace(0, self.duration, sampling_rate * self.duration)

            # Generate realistic pupil diameter data
            # Base pupil size around 3-4mm with variations
            base_diameter = 3.5
            pupil_left = base_diameter + 0.5 * np.sin(
                2 * np.pi * 0.1 * t
            )  # Slow variations
            pupil_right = base_diameter + 0.5 * np.sin(2 * np.pi * 0.1 * t + np.pi / 4)

            # Add noise
            pupil_left += np.random.normal(0, 0.1, len(t))
            pupil_right += np.random.normal(0, 0.1, len(t))

            # Add pupil dilation events (simulating responses)
            dilation_times = np.random.choice(len(t), size=10, replace=False)
            for dilation_time in dilation_times:
                duration = np.random.randint(20, 50)
                end_time = min(dilation_time + duration, len(t))
                amplitude = np.random.uniform(0.5, 1.5)
                pupil_left[dilation_time:end_time] += amplitude * np.exp(
                    -0.1 * np.arange(end_time - dilation_time)
                )
                pupil_right[dilation_time:end_time] += amplitude * np.exp(
                    -0.1 * np.arange(end_time - dilation_time)
                )

            # Ensure positive values
            pupil_left = np.maximum(pupil_left, 1.0)
            pupil_right = np.maximum(pupil_right, 1.0)

            # Create DataFrame
            df = pd.DataFrame(
                {
                    "timestamp": t,
                    "pupil_diameter_left": pupil_left,
                    "pupil_diameter_right": pupil_right,
                    "subject_id": f"subject_{subject_id:03d}",
                }
            )

            # Save to CSV
            filename = (
                self.output_dir / "pupillometry" / f"subject_{subject_id:03d}_pupil.csv"
            )
            df.to_csv(filename, index=False)

            # Create metadata
            metadata = {
                "subject_id": f"subject_{subject_id:03d}",
                "recording_date": datetime.now().isoformat(),
                "sampling_rate": sampling_rate,
                "duration": self.duration,
                "n_samples": len(t),
                "data_type": "Pupillometry",
                "units": "millimeters",
                "eye_tracker": "simulated",
                "calibration": "automatic",
            }

            metadata_file = (
                self.output_dir
                / "pupillometry"
                / f"subject_{subject_id:03d}_metadata.json"
            )
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

    def generate_cardiac_data(self, n_subjects=3):
        """Generate realistic cardiac data (heart rate and HRV)."""

        for subject_id in range(1, n_subjects + 1):
            # Time vector
            sampling_rate = 4  # Hz (typical for HRV analysis)
            t = np.linspace(0, self.duration, sampling_rate * self.duration)

            # Generate realistic heart rate data
            # Base heart rate around 70 bpm with variations
            base_hr = 70
            heart_rate = base_hr + 5 * np.sin(2 * np.pi * 0.05 * t)  # Slow variations

            # Add respiratory sinus arrhythmia
            resp_rate = 0.2  # Hz (12 breaths per minute)
            heart_rate += 3 * np.sin(2 * np.pi * resp_rate * t)

            # Add noise
            heart_rate += np.random.normal(0, 2, len(t))

            # Ensure reasonable heart rate range
            heart_rate = np.clip(heart_rate, 50, 100)

            # Calculate HRV (simplified RMSSD)
            rr_intervals = 60000 / heart_rate  # Convert to milliseconds
            hrv = np.zeros_like(heart_rate)
            for i in range(1, len(rr_intervals)):
                hrv[i] = abs(rr_intervals[i] - rr_intervals[i - 1])

            # Smooth HRV
            window_size = 4
            hrv_smooth = np.convolve(
                hrv, np.ones(window_size) / window_size, mode="same"
            )

            # Create DataFrame
            df = pd.DataFrame(
                {
                    "timestamp": t,
                    "heart_rate": heart_rate,
                    "hrv_rmssd": hrv_smooth,
                    "subject_id": f"subject_{subject_id:03d}",
                }
            )

            # Save to CSV
            filename = (
                self.output_dir / "cardiac" / f"subject_{subject_id:03d}_cardiac.csv"
            )
            df.to_csv(filename, index=False)

            # Create metadata
            metadata = {
                "subject_id": f"subject_{subject_id:03d}",
                "recording_date": datetime.now().isoformat(),
                "sampling_rate": sampling_rate,
                "duration": self.duration,
                "n_samples": len(t),
                "data_type": "Cardiac",
                "heart_rate_units": "bpm",
                "hrv_units": "milliseconds",
                "measurement_method": "ECG_simulated",
            }

            metadata_file = (
                self.output_dir / "cardiac" / f"subject_{subject_id:03d}_metadata.json"
            )
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

    def generate_behavioral_data(self, n_subjects=3):
        """Generate behavioral task data."""

        for subject_id in range(1, n_subjects + 1):
            # Simulate a simple reaction time task
            n_trials = 100

            # Generate trial data
            trial_numbers = np.arange(1, n_trials + 1)
            reaction_times = np.random.normal(300, 50, n_trials)  # ms
            reaction_times = np.maximum(reaction_times, 100)  # Minimum RT

            # Add some attentional lapses (slow responses)
            lapse_trials = np.random.choice(n_trials, size=10, replace=False)
            reaction_times[lapse_trials] += np.random.normal(
                500, 100, len(lapse_trials)
            )

            # Response accuracy (mostly correct with some errors)
            accuracy = np.random.choice([1, 0], size=n_trials, p=[0.9, 0.1])

            # Stimulus conditions
            conditions = np.random.choice(["easy", "medium", "hard"], size=n_trials)

            # Trial timestamps
            trial_onset = np.cumsum(np.random.exponential(2, n_trials))  # Variable ITI

            # Create DataFrame
            df = pd.DataFrame(
                {
                    "trial_number": trial_numbers,
                    "trial_onset": trial_onset,
                    "reaction_time": reaction_times,
                    "accuracy": accuracy,
                    "condition": conditions,
                    "subject_id": f"subject_{subject_id:03d}",
                }
            )

            # Save to CSV
            filename = (
                self.output_dir
                / "behavioral"
                / f"subject_{subject_id:03d}_behavioral.csv"
            )
            df.to_csv(filename, index=False)

            # Create metadata
            metadata = {
                "subject_id": f"subject_{subject_id:03d}",
                "experiment_date": datetime.now().isoformat(),
                "n_trials": n_trials,
                "data_type": "Behavioral",
                "task_type": "reaction_time",
                "reaction_time_units": "milliseconds",
                "conditions": ["easy", "medium", "hard"],
            }

            metadata_file = (
                self.output_dir
                / "behavioral"
                / f"subject_{subject_id:03d}_metadata.json"
            )
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

    def generate_all_data(self):
        """Generate all example datasets."""
        print("Generating example EEG data...")
        self.generate_eeg_data()

        print("Generating example pupillometry data...")
        self.generate_pupillometry_data()

        print("Generating example cardiac data...")
        self.generate_cardiac_data()

        print("Generating example behavioral data...")
        self.generate_behavioral_data()

        # Create a master README for the data
        readme_content = """# Example Data for APGI Framework

This directory contains sample datasets for testing the APGI framework components.

## Data Structure

### EEG Data (`examples/data/eeg/`)
- Multi-channel EEG recordings
- Sampling rate: 1000 Hz
- Duration: 60 seconds per recording
- Channels: Fz, Cz, Pz, Oz, F3, F4, P3, P4
- Format: CSV files with metadata JSON files

### Pupillometry Data (`examples/data/pupillometry/`)
- Binocular pupil diameter measurements
- Sampling rate: 250 Hz
- Duration: 60 seconds per recording
- Units: millimeters
- Format: CSV files with metadata JSON files

### Cardiac Data (`examples/data/cardiac/`)
- Heart rate and heart rate variability
- Sampling rate: 4 Hz
- Duration: 60 seconds per recording
- Heart rate units: bpm
- HRV units: milliseconds (RMSSD)
- Format: CSV files with metadata JSON files

### Behavioral Data (`examples/data/behavioral/`)
- Reaction time task performance
- 100 trials per subject
- Reaction time units: milliseconds
- Conditions: easy, medium, hard
- Format: CSV files with metadata JSON files

## Usage

```python
from apgi_framework.data import load_example_data

# Load EEG data
eeg_data = load_example_data('eeg', subject_id='subject_001')

# Load pupillometry data
pupil_data = load_example_data('pupillometry', subject_id='subject_001')

# Load cardiac data
cardiac_data = load_example_data('cardiac', subject_id='subject_001')

# Load behavioral data
behavioral_data = load_example_data('behavioral', subject_id='subject_001')
```

## Data Quality

All data is simulated but designed to be realistic for:
- Testing analysis pipelines
- Developing new features
- Demonstrating framework capabilities
- Educational purposes

## Subjects

The dataset includes 3 simulated subjects:
- subject_001
- subject_002  
- subject_003

Each subject has complete data for all modalities.
"""

        readme_file = self.output_dir / "README.md"
        with open(readme_file, "w") as f:
            f.write(readme_content)

        print(f"Example data generated successfully in {self.output_dir}")


if __name__ == "__main__":
    generator = ExampleDataGenerator()
    generator.generate_all_data()
