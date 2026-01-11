"""
APGI Framework Tutorial

This tutorial demonstrates the basic and advanced features of the APGI Framework.
Run this script to learn how to use the framework for data analysis.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


def main():
    """Main tutorial function."""
    print("🎯 APGI Framework Tutorial")
    print("=" * 50)

    # 1. Setup and Installation
    print("\n1. Setup and Installation")
    print("-" * 25)

    try:
        from apgi_framework.analysis import AnalysisEngine
        from apgi_framework.data import load_example_data

        print("✅ APGI Framework imported successfully!")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure the framework is properly installed.")
        return

    # Import standard libraries
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    print("📊 Libraries ready for analysis!")

    # 2. Loading Data
    print("\n2. Loading Data")
    print("-" * 15)

    try:
        # Load example EEG data
        eeg_data = load_example_data("eeg", "subject_001")
        print("✅ EEG data loaded successfully!")
        print(f"   Shape: {eeg_data['data'].shape}")
        print(f"   Sampling rate: {eeg_data['metadata']['sampling_rate']} Hz")

        # Load example behavioral data
        behavioral_data = load_example_data("behavioral", "subject_001")
        print("✅ Behavioral data loaded successfully!")
        print(f"   Shape: {behavioral_data['data'].shape}")
        print(f"   Conditions: {behavioral_data['data']['condition'].unique()}")

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return

    # 3. Basic Analysis
    print("\n3. Basic Analysis")
    print("-" * 15)

    try:
        # Initialize the analysis engine
        engine = AnalysisEngine()

        # Get the behavioral DataFrame
        behav_df = behavioral_data["data"]

        # Descriptive analysis
        desc_params = {
            "variables": ["reaction_time", "correct"],
            "group_by": "condition",
        }

        desc_result = engine.analyze(
            data=behav_df, analysis_type="descriptive", parameters=desc_params
        )

        print("✅ Descriptive analysis completed!")
        print("📈 Descriptive Statistics:")

        for var, stats in desc_result.statistics.items():
            print(f"\n   {var}:")
            for stat, value in stats.items():
                print(f"     {stat}: {value:.3f}")

        # Comparative analysis
        comp_params = {
            "dependent_variable": "reaction_time",
            "group_variable": "condition",
            "test_type": "anova",
        }

        comp_result = engine.analyze(
            data=behav_df, analysis_type="comparative", parameters=comp_params
        )

        print("\n✅ Comparative analysis completed!")
        print("🔬 Comparative Statistics:")

        if "F_statistic" in comp_result.statistics:
            print(f"   F-statistic: {comp_result.statistics['F_statistic']:.3f}")
        if "p_value" in comp_result.p_values:
            print(f"   p-value: {comp_result.p_values['p_value']:.3f}")

    except Exception as e:
        print(f"❌ Error in analysis: {e}")

    # 4. Visualization
    print("\n4. Visualization")
    print("-" * 15)

    try:
        # Set up plotting
        plt.style.use("default")
        sns.set_palette("husl")

        # Create a simple visualization
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle("APGI Framework Tutorial - Analysis Summary", fontsize=16)

        # Plot 1: Reaction time box plot
        behav_df.boxplot(column="reaction_time", by="condition", ax=axes[0])
        axes[0].set_title("Reaction Time by Condition")
        axes[0].set_xlabel("Condition")
        axes[0].set_ylabel("Reaction Time (ms)")

        # Plot 2: Accuracy by condition
        accuracy_by_condition = behav_df.groupby("condition")["correct"].mean()
        axes[1].bar(accuracy_by_condition.index, accuracy_by_condition.values)
        axes[1].set_title("Accuracy by Condition")
        axes[1].set_xlabel("Condition")
        axes[1].set_ylabel("Accuracy")

        plt.tight_layout()

        # Save the plot
        output_dir = os.path.join(os.path.dirname(__file__), "..", "figures")
        os.makedirs(output_dir, exist_ok=True)
        plot_path = os.path.join(output_dir, "tutorial_summary.png")
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.show()

        print(f"✅ Visualization created and saved to {plot_path}")

    except Exception as e:
        print(f"❌ Error creating visualization: {e}")

    # 5. Export Results
    print("\n5. Export Results")
    print("-" * 15)

    try:
        import json

        # Create results dictionary
        results = {
            "descriptive_stats": (
                desc_result.statistics if "desc_result" in locals() else None
            ),
            "comparative_stats": (
                comp_result.statistics if "comp_result" in locals() else None
            ),
            "data_summary": {
                "behavioral_data_shape": behav_df.shape,
                "conditions": behav_df["condition"].unique().tolist(),
            },
        }

        # Convert numpy arrays to lists for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {key: convert_numpy(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj

        results_serializable = convert_numpy(results)

        # Save results
        output_path = os.path.join(os.path.dirname(__file__), "..", "results")
        os.makedirs(output_path, exist_ok=True)
        results_path = os.path.join(output_path, "tutorial_results.json")

        with open(results_path, "w") as f:
            json.dump(results_serializable, f, indent=2)

        print(f"✅ Results exported to {results_path}")

    except Exception as e:
        print(f"❌ Error exporting results: {e}")

    # Tutorial Complete
    print("\n🎉 Tutorial Complete!")
    print("=" * 50)
    print("\n✅ What You've Accomplished:")
    print("   1. Setup: Successfully imported the APGI Framework")
    print("   2. Data Loading: Loaded example datasets")
    print("   3. Basic Analysis: Performed statistical analyses")
    print("   4. Visualization: Created plots and figures")
    print("   5. Export: Saved results for later use")

    print("\n🚀 Next Steps:")
    print("   - Explore the GUI: python -m apgi_gui")
    print("   - Try different data: Load your own datasets")
    print("   - Advanced models: Explore Bayesian modeling")
    print("   - Documentation: Read the full user guide")

    print("\n📚 Additional Resources:")
    print("   - User Guide: docs/user_guide.md")
    print("   - API Reference: docs/api/")
    print("   - Examples: examples/")
    print("   - GitHub: Report issues and contribute")

    print("\nHappy analyzing with the APGI Framework! 🎯")


if __name__ == "__main__":
    main()
