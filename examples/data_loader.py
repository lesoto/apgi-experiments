"""
Example Data Loader for APGI Framework

This module provides utilities to load and manage example datasets
for testing, development, and educational purposes.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, Union
import numpy as np


class ExampleDataLoader:
    """
    Utility class for loading example datasets.
    """

    def __init__(self, data_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the data loader.

        Args:
            data_dir: Path to the example data directory
        """
        if data_dir is None:
            # Default to examples/data relative to this file
            self.data_dir = Path(__file__).parent / "data"
        else:
            self.data_dir = Path(data_dir)

        self.available_modalities = ["eeg", "pupillometry", "cardiac", "behavioral"]
        self.available_subjects = ["subject_001", "subject_002", "subject_003"]

    def list_available_data(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available example data.

        Returns:
            Dictionary with available data information
        """
        available = {}

        for modality in self.available_modalities:
            modality_dir = self.data_dir / modality
            if modality_dir.exists():
                # Find all subject files
                subject_files = list(modality_dir.glob("*_*.csv"))
                subjects = [f.stem.split("_")[0] for f in subject_files]

                available[modality] = {
                    "subjects": subjects,
                    "data_files": [f.name for f in subject_files],
                    "metadata_files": [
                        f.name for f in modality_dir.glob("*_metadata.json")
                    ],
                }

        return available

    def load_data(
        self, modality: str, subject_id: str = "subject_001"
    ) -> Dict[str, Any]:
        """
        Load example data for a specific modality and subject.

        Args:
            modality: Type of data to load ('eeg', 'pupillometry', 'cardiac', 'behavioral')
            subject_id: Subject identifier

        Returns:
            Dictionary containing data and metadata
        """
        if modality not in self.available_modalities:
            raise ValueError(
                f"Unknown modality: {modality}. Available: {self.available_modalities}"
            )

        if subject_id not in self.available_subjects:
            raise ValueError(
                f"Unknown subject: {subject_id}. Available: {self.available_subjects}"
            )

        # Construct file paths
        data_file = self.data_dir / modality / f"{subject_id}_{modality}.csv"
        metadata_file = self.data_dir / modality / f"{subject_id}_metadata.json"

        if not data_file.exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")

        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        # Load data
        data = pd.read_csv(data_file)

        # Load metadata
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        return {
            "data": data,
            "metadata": metadata,
            "subject_id": subject_id,
            "modality": modality,
            "data_file": str(data_file),
            "metadata_file": str(metadata_file),
        }

    def load_all_subjects(self, modality: str) -> Dict[str, Dict[str, Any]]:
        """
        Load data for all subjects in a modality.

        Args:
            modality: Type of data to load

        Returns:
            Dictionary with subject IDs as keys and data dictionaries as values
        """
        all_data = {}

        for subject_id in self.available_subjects:
            try:
                all_data[subject_id] = self.load_data(modality, subject_id)
            except FileNotFoundError:
                print(f"Warning: Data not found for {subject_id} in {modality}")
                continue

        return all_data

    def get_data_summary(
        self, modality: str, subject_id: str = "subject_001"
    ) -> Dict[str, Any]:
        """
        Get a summary of the data without loading the full dataset.

        Args:
            modality: Type of data
            subject_id: Subject identifier

        Returns:
            Dictionary with data summary information
        """
        data_info = self.load_data(modality, subject_id)
        data = data_info["data"]
        metadata = data_info["metadata"]

        summary = {
            "subject_id": subject_id,
            "modality": modality,
            "shape": data.shape,
            "columns": list(data.columns),
            "dtypes": data.dtypes.to_dict(),
            "missing_values": data.isnull().sum().to_dict(),
            "metadata": metadata,
        }

        # Add modality-specific summaries
        if modality == "eeg":
            summary.update(
                {
                    "sampling_rate": metadata.get("sampling_rate"),
                    "duration_seconds": len(data) / metadata.get("sampling_rate", 1000),
                    "channels": [
                        col for col in data.columns if col.startswith("channel_")
                    ],
                }
            )
        elif modality == "pupillometry":
            summary.update(
                {
                    "sampling_rate": metadata.get("sampling_rate"),
                    "duration_seconds": len(data) / metadata.get("sampling_rate", 250),
                    "pupil_columns": [col for col in data.columns if "pupil" in col],
                }
            )
        elif modality == "cardiac":
            summary.update(
                {
                    "sampling_rate": metadata.get("sampling_rate"),
                    "duration_seconds": len(data) / metadata.get("sampling_rate", 4),
                    "heart_rate_range": [
                        data["heart_rate"].min(),
                        data["heart_rate"].max(),
                    ],
                    "hrv_range": [data["hrv"].min(), data["hrv"].max()],
                }
            )
        elif modality == "behavioral":
            summary.update(
                {
                    "total_trials": len(data),
                    "conditions": data["condition"].unique().tolist(),
                    "rt_range": [
                        data["reaction_time"].min(),
                        data["reaction_time"].max(),
                    ],
                    "accuracy": (data["correct"].sum() / len(data)) * 100,
                }
            )

        return summary

    def create_synthetic_dataset(
        self,
        modality: str,
        n_subjects: int = 3,
        duration_seconds: int = 60,
        noise_level: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Create a synthetic dataset for testing purposes.

        Args:
            modality: Type of data to generate
            n_subjects: Number of subjects to generate
            duration_seconds: Duration of each recording in seconds
            noise_level: Level of noise to add (0.0 to 1.0)

        Returns:
            Dictionary with synthetic data information
        """
        np.random.seed(42)  # For reproducibility

        synthetic_data = {}

        if modality == "eeg":
            sampling_rate = 1000
            n_samples = duration_seconds * sampling_rate
            channels = ["Fz", "Cz", "Pz", "Oz", "F3", "F4", "P3", "P4"]

            for subj_idx in range(n_subjects):
                subject_id = f"synthetic_subject_{subj_idx+1:03d}"

                # Generate realistic EEG-like signals
                data = {}
                for channel in channels:
                    # Base signal with alpha, beta, theta components
                    t = np.linspace(0, duration_seconds, n_samples)
                    signal = (
                        0.5 * np.sin(2 * np.pi * 10 * t)  # Alpha
                        + 0.3 * np.sin(2 * np.pi * 20 * t)  # Beta
                        + 0.2 * np.sin(2 * np.pi * 5 * t)  # Theta
                    )

                    # Add noise
                    signal += noise_level * np.random.randn(n_samples)
                    data[f"channel_{channel}"] = signal

                data["timestamp"] = np.arange(n_samples) / sampling_rate
                data["subject_id"] = subject_id

                df = pd.DataFrame(data)

                metadata = {
                    "subject_id": subject_id,
                    "modality": "eeg",
                    "sampling_rate": sampling_rate,
                    "duration_seconds": duration_seconds,
                    "channels": channels,
                    "synthetic": True,
                    "noise_level": noise_level,
                }

                synthetic_data[subject_id] = {"data": df, "metadata": metadata}

        # Similar implementations for other modalities...

        return synthetic_data

    def export_data(
        self, data_dict: Dict[str, Any], output_dir: Union[str, Path]
    ) -> None:
        """
        Export data dictionary to files.

        Args:
            data_dict: Data dictionary from load_data()
            output_dir: Directory to save files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        subject_id = data_dict["subject_id"]
        modality = data_dict["modality"]

        # Save data
        data_file = output_dir / f"{subject_id}_{modality}.csv"
        data_dict["data"].to_csv(data_file, index=False)

        # Save metadata
        metadata_file = output_dir / f"{subject_id}_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(data_dict["metadata"], f, indent=2)

        print(f"Exported {modality} data for {subject_id} to {output_dir}")


# Convenience function for quick access
def load_example_data(modality: str, subject_id: str = "subject_001") -> Dict[str, Any]:
    """
    Quick access function to load example data.

    Args:
        modality: Type of data to load
        subject_id: Subject identifier

    Returns:
        Dictionary containing data and metadata
    """
    loader = ExampleDataLoader()
    return loader.load_data(modality, subject_id)


def list_example_data() -> Dict[str, Dict[str, Any]]:
    """
    List all available example data.

    Returns:
        Dictionary with available data information
    """
    loader = ExampleDataLoader()
    return loader.list_available_data()


if __name__ == "__main__":
    # Example usage
    print("Available example data:")
    available = list_example_data()
    for modality, info in available.items():
        print(f"  {modality}: {len(info['subjects'])} subjects")

    # Load and display summary
    loader = ExampleDataLoader()
    summary = loader.get_data_summary("eeg", "subject_001")
    print(f"\nEEG data summary: {summary}")
