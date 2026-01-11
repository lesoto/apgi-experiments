"""
Generate Additional Example Datasets for APGI Framework

This script creates additional example datasets to enhance the testing
and development capabilities of the APGI Framework.
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List
import matplotlib.pyplot as plt


class DatasetGenerator:
    """
    Generate realistic example datasets for APGI Framework testing.
    """

    def __init__(self, output_dir: str = None):
        """
        Initialize the dataset generator.

        Args:
            output_dir: Directory to save generated datasets
        """
        if output_dir is None:
            self.output_dir = Path(__file__).parent / "data"
        else:
            self.output_dir = Path(output_dir)

        # Create subdirectories
        for subdir in ["eeg", "pupillometry", "cardiac", "behavioral", "multimodal"]:
            (self.output_dir / subdir).mkdir(parents=True, exist_ok=True)

    def generate_multimodal_dataset(
        self, subject_id: str = "multimodal_001"
    ) -> Dict[str, Any]:
        """
        Generate a synchronized multimodal dataset.

        Args:
            subject_id: Subject identifier

        Returns:
            Dictionary with multimodal data
        """
        np.random.seed(hash(subject_id) % 2**32)  # Reproducible per subject

        # Common parameters
        duration_seconds = 120  # 2 minutes
        eeg_sr = 1000
        pupil_sr = 250
        cardiac_sr = 4

        # Time arrays
        eeg_time = np.arange(0, duration_seconds, 1 / eeg_sr)
        pupil_time = np.arange(0, duration_seconds, 1 / pupil_sr)
        cardiac_time = np.arange(0, duration_seconds, 1 / cardiac_sr)

        # Generate EEG data with event-related potentials
        eeg_channels = ["Fz", "Cz", "Pz"]
        eeg_data = {}

        for channel in eeg_channels:
            # Background oscillations
            signal = (
                0.5 * np.sin(2 * np.pi * 10 * eeg_time)  # Alpha
                + 0.3 * np.sin(2 * np.pi * 20 * eeg_time)  # Beta
                + 0.2 * np.sin(2 * np.pi * 5 * eeg_time)  # Theta
            )

            # Add some event-related potentials (simulated P300)
            for event_time in [30, 60, 90]:  # Events at 30s, 60s, 90s
                event_idx = int(event_time * eeg_sr)
                if event_idx < len(signal):
                    # P300-like response
                    p300 = 5 * np.exp(-((np.arange(-100, 400) / 100) ** 2))
                    end_idx = min(event_idx + 500, len(signal))
                    actual_p300 = p300[: end_idx - event_idx]
                    signal[event_idx:end_idx] += actual_p300

            # Add noise
            signal += 0.5 * np.random.randn(len(signal))
            eeg_data[f"channel_{channel}"] = signal

        eeg_data["timestamp"] = eeg_time
        eeg_data["subject_id"] = subject_id
        eeg_df = pd.DataFrame(eeg_data)

        # Generate pupillometry data with task-evoked responses
        pupil_data = {
            "timestamp": pupil_time,
            "pupil_diameter_left": 3.0 + 0.5 * np.sin(2 * np.pi * 0.1 * pupil_time),
            "pupil_diameter_right": 3.0
            + 0.5 * np.sin(2 * np.pi * 0.1 * pupil_time + np.pi / 4),
            "subject_id": subject_id,
        }

        # Add task-evoked dilation events
        for event_time in [30, 60, 90]:
            event_idx = int(event_time * pupil_sr)
            if event_idx < len(pupil_time):
                dilation = 1.5 * np.exp(-((np.arange(-50, 200) / 50) ** 2))
                end_idx = min(event_idx + 250, len(pupil_data["pupil_diameter_left"]))
                actual_dilation = dilation[: end_idx - event_idx]
                pupil_data["pupil_diameter_left"][event_idx:end_idx] += actual_dilation
                pupil_data["pupil_diameter_right"][event_idx:end_idx] += actual_dilation

        # Add noise
        pupil_data["pupil_diameter_left"] += 0.1 * np.random.randn(len(pupil_time))
        pupil_data["pupil_diameter_right"] += 0.1 * np.random.randn(len(pupil_time))
        pupil_df = pd.DataFrame(pupil_data)

        # Generate cardiac data with variability
        base_hr = 70 + 5 * np.sin(2 * np.pi * 0.05 * cardiac_time)  # Slow variation
        heart_rate = base_hr + 2 * np.random.randn(len(cardiac_time))
        heart_rate = np.clip(heart_rate, 50, 100)  # Physiological range

        # HRV calculation (simplified)
        hrv = (
            45
            + 10 * np.sin(2 * np.pi * 0.1 * cardiac_time)
            + 5 * np.random.randn(len(cardiac_time))
        )
        hrv = np.clip(hrv, 20, 80)

        cardiac_data = {
            "timestamp": cardiac_time,
            "heart_rate": heart_rate,
            "hrv": hrv,
            "subject_id": subject_id,
        }
        cardiac_df = pd.DataFrame(cardiac_data)

        # Generate behavioral data for the same session
        n_trials = 120
        conditions = np.random.choice(
            ["easy", "medium", "hard"], n_trials, p=[0.4, 0.4, 0.2]
        )

        # Reaction times depend on condition
        rt_means = {"easy": 400, "medium": 550, "hard": 750}
        rt_stds = {"easy": 80, "medium": 100, "hard": 150}

        reaction_times = []
        correct = []

        for condition in conditions:
            rt = np.random.normal(rt_means[condition], rt_stds[condition])
            rt = max(200, rt)  # Minimum physiological limit
            reaction_times.append(rt)

            # Accuracy depends on condition
            if condition == "easy":
                correct.append(np.random.random() > 0.05)  # 95% accuracy
            elif condition == "medium":
                correct.append(np.random.random() > 0.15)  # 85% accuracy
            else:  # hard
                correct.append(np.random.random() > 0.30)  # 70% accuracy

        behavioral_data = {
            "trial_number": range(1, n_trials + 1),
            "condition": conditions,
            "reaction_time": reaction_times,
            "correct": correct,
            "subject_id": subject_id,
        }
        behavioral_df = pd.DataFrame(behavioral_data)

        # Create metadata
        metadata = {
            "subject_id": subject_id,
            "modality": "multimodal",
            "duration_seconds": duration_seconds,
            "eeg": {
                "sampling_rate": eeg_sr,
                "channels": eeg_channels,
                "n_samples": len(eeg_df),
            },
            "pupillometry": {"sampling_rate": pupil_sr, "n_samples": len(pupil_df)},
            "cardiac": {"sampling_rate": cardiac_sr, "n_samples": len(cardiac_df)},
            "behavioral": {
                "n_trials": n_trials,
                "conditions": list(conditions),
                "accuracy": np.mean(correct) * 100,
            },
            "events": [
                {"time": 30, "type": "stimulus", "description": "First stimulus"},
                {"time": 60, "type": "stimulus", "description": "Second stimulus"},
                {"time": 90, "type": "stimulus", "description": "Third stimulus"},
            ],
            "synchronized": True,
            "synthetic": True,
        }

        return {
            "eeg": eeg_df,
            "pupillometry": pupil_df,
            "cardiac": cardiac_df,
            "behavioral": behavioral_df,
            "metadata": metadata,
        }

    def generate_pathological_dataset(
        self, subject_id: str = "pathological_001"
    ) -> Dict[str, Any]:
        """
        Generate a dataset with simulated pathological patterns.

        Args:
            subject_id: Subject identifier

        Returns:
            Dictionary with pathological data
        """
        np.random.seed(hash(subject_id) % 2**32)

        duration_seconds = 60
        sampling_rate = 1000
        n_samples = duration_seconds * sampling_rate
        time = np.arange(0, duration_seconds, 1 / sampling_rate)

        # EEG with epileptiform activity
        eeg_data = {}
        channels = ["Fz", "Cz", "Pz"]

        for channel in channels:
            # Background activity
            signal = 0.5 * np.sin(2 * np.pi * 10 * time)

            # Add spike-and-wave discharges (epileptiform)
            for spike_time in [15, 35, 55]:
                spike_idx = int(spike_time * sampling_rate)
                if spike_idx < len(signal):
                    # Spike-and-wave complex
                    spike_wave = np.zeros(300)  # 300ms duration
                    spike_wave[50:100] = 10  # Sharp spike
                    spike_wave[100:300] = 3 * np.sin(
                        2 * np.pi * 3 * np.arange(200)
                    )  # Slow wave

                    end_idx = min(spike_idx + 300, len(signal))
                    signal[spike_idx:end_idx] += spike_wave[: end_idx - spike_idx]

            # Add noise
            signal += 0.3 * np.random.randn(len(signal))
            eeg_data[f"channel_{channel}"] = signal

        eeg_data["timestamp"] = time
        eeg_data["subject_id"] = subject_id
        eeg_df = pd.DataFrame(eeg_data)

        # Pupillometry with abnormal patterns
        pupil_data = {
            "timestamp": time[::4],  # Downsample to 250 Hz
            "pupil_diameter_left": np.zeros(len(time[::4])),
            "pupil_diameter_right": np.zeros(len(time[::4])),
            "subject_id": subject_id,
        }

        # Base pupil diameter with hippus (small oscillations)
        base_pupil = 3.0 + 0.2 * np.sin(2 * np.pi * 2 * time[::4])
        pupil_data["pupil_diameter_left"] = base_pupil + 0.1 * np.random.randn(
            len(base_pupil)
        )
        pupil_data["pupil_diameter_right"] = base_pupil + 0.1 * np.random.randn(
            len(base_pupil)
        )

        # Add abnormal dilation episode
        dilation_start = int(25 * 250)  # 25 seconds, 250 Hz
        dilation_end = int(35 * 250)  # 35 seconds
        pupil_data["pupil_diameter_left"][dilation_start:dilation_end] += 2.0
        pupil_data["pupil_diameter_right"][dilation_start:dilation_end] += 2.0

        pupil_df = pd.DataFrame(pupil_data)

        # Cardiac with arrhythmia
        cardiac_time = np.arange(0, duration_seconds, 0.25)  # 4 Hz
        base_hr = 75 + 5 * np.sin(2 * np.pi * 0.1 * cardiac_time)

        # Add arrhythmic episodes
        heart_rate = base_hr.copy()
        arrhythmia_start = int(20 * 4)  # 20 seconds, 4 Hz
        arrhythmia_end = int(30 * 4)  # 30 seconds
        heart_rate[arrhythmia_start:arrhythmia_end] = 120 + 20 * np.random.randn(
            arrhythmia_end - arrhythmia_start
        )

        heart_rate = np.clip(heart_rate, 40, 180)

        # HRV calculation
        hrv = (
            40
            + 15 * np.sin(2 * np.pi * 0.2 * cardiac_time)
            + 10 * np.random.randn(len(cardiac_time))
        )
        hrv[arrhythmia_start:arrhythmia_end] = 20 + 5 * np.random.randn(
            arrhythmia_end - arrhythmia_start
        )
        hrv = np.clip(hrv, 10, 100)

        cardiac_data = {
            "timestamp": cardiac_time,
            "heart_rate": heart_rate,
            "hrv": hrv,
            "subject_id": subject_id,
        }
        cardiac_df = pd.DataFrame(cardiac_data)

        # Metadata with pathological annotations
        metadata = {
            "subject_id": subject_id,
            "modality": "pathological",
            "duration_seconds": duration_seconds,
            "eeg": {
                "sampling_rate": sampling_rate,
                "channels": channels,
                "abnormalities": [
                    {"time": 15, "type": "spike_and_wave", "duration": 0.3},
                    {"time": 35, "type": "spike_and_wave", "duration": 0.3},
                    {"time": 55, "type": "spike_and_wave", "duration": 0.3},
                ],
            },
            "pupillometry": {
                "sampling_rate": 250,
                "abnormalities": [
                    {"time": 25, "type": "abnormal_dilation", "duration": 10.0}
                ],
            },
            "cardiac": {
                "sampling_rate": 4,
                "abnormalities": [
                    {"time": 20, "type": "tachycardia", "duration": 10.0}
                ],
            },
            "synthetic": True,
            "notes": "Simulated pathological patterns for testing detection algorithms",
        }

        return {
            "eeg": eeg_df,
            "pupillometry": pupil_df,
            "cardiac": cardiac_df,
            "metadata": metadata,
        }

    def save_dataset(
        self, dataset: Dict[str, Any], dataset_type: str = "multimodal"
    ) -> None:
        """
        Save dataset to appropriate files.

        Args:
            dataset: Dataset dictionary
            dataset_type: Type of dataset ('multimodal', 'pathological')
        """
        subject_id = dataset["metadata"]["subject_id"]

        # Save each modality
        for modality, df in dataset.items():
            if modality == "metadata":
                continue

            modality_dir = self.output_dir / dataset_type / modality
            modality_dir.mkdir(parents=True, exist_ok=True)

            # Save data
            data_file = modality_dir / f"{subject_id}_{modality}.csv"
            df.to_csv(data_file, index=False)

            # Save metadata
            metadata_file = modality_dir / f"{subject_id}_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(dataset["metadata"], f, indent=2)

            print(f"Saved {modality} data for {subject_id} to {data_file}")

    def generate_all_datasets(self) -> None:
        """
        Generate all example datasets.
        """
        print("Generating multimodal datasets...")
        for i in range(3):
            subject_id = f"multimodal_{i+1:03d}"
            dataset = self.generate_multimodal_dataset(subject_id)
            self.save_dataset(dataset, "multimodal")

        print("Generating pathological datasets...")
        for i in range(2):
            subject_id = f"pathological_{i+1:03d}"
            dataset = self.generate_pathological_dataset(subject_id)
            self.save_dataset(dataset, "pathological")

        print("Dataset generation complete!")


if __name__ == "__main__":
    generator = DatasetGenerator()
    generator.generate_all_datasets()
