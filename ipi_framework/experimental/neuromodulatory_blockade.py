"""
Neuromodulatory blockade simulation for IPI framework validation.

Implements propranolol effect modeling on P3b amplitude, selective emotional
stimulus processing impairment, and early ERP preservation validation.

This module supports Priority 2 core mechanism validation by testing the
prediction that noradrenergic blockade selectively impairs ignition-related
neural signatures while preserving early sensory processing.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy import stats

from ..core.data_models import PharmacologicalCondition, NeuralSignatures
from ..neural.erp_analysis import ERPComponents, P3bMetrics


@dataclass
class NeuromodulatorEffect:
    """Model of neuromodulator effects on neural processing."""
    # P3b modulation
    p3b_amplitude_reduction: float = 0.0  # Fractional reduction (0-1)
    p3b_latency_shift: float = 0.0  # ms
    
    # Emotional selectivity
    emotional_selectivity: float = 1.0  # Multiplier for emotional vs neutral
    
    # Early ERP preservation
    early_component_preservation: float = 1.0  # 1.0 = fully preserved
    
    # Gamma synchrony effects
    gamma_power_reduction: float = 0.0  # Fractional reduction
    
    # Precision modulation
    intero_precision_reduction: float = 0.0  # Fractional reduction
    extero_precision_change: float = 0.0  # Fractional change
    
    # Metadata
    drug_name: str = ""
    mechanism: str = ""  # e.g., "beta-adrenergic_blockade"
    

@dataclass
class BlockadeSimulationResult:
    """Results from neuromodulatory blockade simulation."""
    # Condition comparison
    baseline_p3b: float
    blockade_p3b: float
    p3b_reduction_percent: float
    
    # Emotional selectivity
    emotional_baseline_p3b: float
    emotional_blockade_p3b: float
    neutral_baseline_p3b: float
    neutral_blockade_p3b: float
    emotional_selectivity_index: float  # (emotional_reduction - neutral_reduction)
    
    # Early ERP preservation
    baseline_n1: float
    blockade_n1: float
    n1_preservation_percent: float
    
    baseline_p1: float
    blockade_p1: float
    p1_preservation_percent: float
    
    # Statistical validation
    p3b_reduction_pvalue: float
    early_preservation_pvalue: float
    emotional_selectivity_pvalue: float
    
    # Effect sizes
    p3b_reduction_cohens_d: float
    emotional_selectivity_cohens_d: float
    
    # Prediction validation
    meets_p3b_reduction_prediction: bool  # 20-40% reduction
    meets_early_preservation_prediction: bool  # <10% change
    meets_emotional_selectivity_prediction: bool  # Emotional > neutral
    
    # Metadata
    n_trials_baseline: int = 0
    n_trials_blockade: int = 0
    drug_condition: Optional[PharmacologicalCondition] = None


class NeuromodulatoryBlockadeSimulator:
    """
    Simulator for neuromodulatory blockade effects on neural signatures.
    
    Implements propranolol (beta-adrenergic blockade) effects based on
    IPI predictions:
    - 20-40% P3b amplitude reduction for emotional stimuli
    - Selective impairment of emotional vs neutral processing
    - Preservation of early sensory ERPs (N1, P1)
    - Reduced long-range gamma synchrony
    """
    
    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize blockade simulator.
        
        Args:
            random_seed: Random seed for reproducibility
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Define propranolol effects based on IPI predictions
        self.propranolol_effects = NeuromodulatorEffect(
            p3b_amplitude_reduction=0.30,  # 30% reduction (within 20-40% range)
            p3b_latency_shift=10.0,  # Slight delay
            emotional_selectivity=2.0,  # 2x stronger effect on emotional
            early_component_preservation=0.98,  # 98% preserved (<10% change)
            gamma_power_reduction=0.25,  # 25% reduction
            intero_precision_reduction=0.35,  # 35% reduction in interoceptive precision
            extero_precision_change=0.05,  # Minimal exteroceptive change
            drug_name="propranolol",
            mechanism="beta-adrenergic_blockade"
        )
    
    def apply_blockade_effect(self,
                             baseline_erp: ERPComponents,
                             stimulus_type: str = "neutral",
                             effect_model: Optional[NeuromodulatorEffect] = None) -> ERPComponents:
        """
        Apply neuromodulatory blockade effects to ERP components.
        
        Args:
            baseline_erp: Baseline ERP components
            stimulus_type: "emotional" or "neutral"
            effect_model: Neuromodulator effect model (default: propranolol)
            
        Returns:
            Modified ERP components under blockade
        """
        if effect_model is None:
            effect_model = self.propranolol_effects
        
        # Determine emotional modulation
        emotional_multiplier = 1.0
        if stimulus_type == "emotional":
            emotional_multiplier = effect_model.emotional_selectivity
        
        # Apply P3b reduction
        p3b_reduction = effect_model.p3b_amplitude_reduction * emotional_multiplier
        blockade_p3b_amplitude = baseline_erp.p3b_amplitude * (1.0 - p3b_reduction)
        blockade_p3b_latency = baseline_erp.p3b_latency + effect_model.p3b_latency_shift
        
        # Preserve early components
        preservation = effect_model.early_component_preservation
        blockade_p1 = baseline_erp.p1_amplitude * preservation
        blockade_n1 = baseline_erp.n1_amplitude * preservation
        blockade_n170 = baseline_erp.n170_amplitude * preservation
        
        # Add realistic noise
        noise_scale = 0.05  # 5% noise
        blockade_p3b_amplitude *= (1.0 + np.random.normal(0, noise_scale))
        blockade_p1 *= (1.0 + np.random.normal(0, noise_scale))
        blockade_n1 *= (1.0 + np.random.normal(0, noise_scale))
        
        return ERPComponents(
            p3b_amplitude=blockade_p3b_amplitude,
            p3b_latency=blockade_p3b_latency,
            p3b_area=baseline_erp.p3b_area * (1.0 - p3b_reduction),
            p1_amplitude=blockade_p1,
            p1_latency=baseline_erp.p1_latency,
            n1_amplitude=blockade_n1,
            n1_latency=baseline_erp.n1_latency,
            n170_amplitude=blockade_n170,
            n170_latency=baseline_erp.n170_latency,
            baseline_mean=baseline_erp.baseline_mean,
            baseline_std=baseline_erp.baseline_std,
            snr=baseline_erp.snr * (1.0 - p3b_reduction * 0.5),
            channel=baseline_erp.channel,
            condition="blockade"
        )
    
    def simulate_blockade_experiment(self,
                                    n_trials_per_condition: int = 40,
                                    baseline_p3b_mean: float = 8.0,
                                    baseline_p3b_std: float = 2.0,
                                    baseline_n1_mean: float = -5.0,
                                    baseline_n1_std: float = 1.5,
                                    baseline_p1_mean: float = 3.0,
                                    baseline_p1_std: float = 1.0) -> BlockadeSimulationResult:
        """
        Simulate complete neuromodulatory blockade experiment.
        
        Args:
            n_trials_per_condition: Number of trials per condition
            baseline_p3b_mean: Mean P3b amplitude in baseline (µV)
            baseline_p3b_std: Std of P3b amplitude
            baseline_n1_mean: Mean N1 amplitude (µV, negative)
            baseline_n1_std: Std of N1 amplitude
            baseline_p1_mean: Mean P1 amplitude (µV)
            baseline_p1_std: Std of P1 amplitude
            
        Returns:
            BlockadeSimulationResult with statistical validation
        """
        # Generate baseline trials
        baseline_emotional_p3b = np.random.normal(
            baseline_p3b_mean * 1.2,  # Emotional stimuli elicit larger P3b
            baseline_p3b_std,
            n_trials_per_condition
        )
        baseline_neutral_p3b = np.random.normal(
            baseline_p3b_mean,
            baseline_p3b_std,
            n_trials_per_condition
        )
        baseline_n1 = np.random.normal(baseline_n1_mean, baseline_n1_std, n_trials_per_condition)
        baseline_p1 = np.random.normal(baseline_p1_mean, baseline_p1_std, n_trials_per_condition)
        
        # Apply blockade effects
        emotional_reduction = self.propranolol_effects.p3b_amplitude_reduction * \
                            self.propranolol_effects.emotional_selectivity
        neutral_reduction = self.propranolol_effects.p3b_amplitude_reduction
        
        blockade_emotional_p3b = baseline_emotional_p3b * (1.0 - emotional_reduction)
        blockade_neutral_p3b = baseline_neutral_p3b * (1.0 - neutral_reduction)
        
        # Early components preserved
        preservation = self.propranolol_effects.early_component_preservation
        blockade_n1 = baseline_n1 * preservation
        blockade_p1 = baseline_p1 * preservation
        
        # Add realistic noise
        noise_scale = 0.05
        blockade_emotional_p3b += np.random.normal(0, baseline_p3b_std * noise_scale, n_trials_per_condition)
        blockade_neutral_p3b += np.random.normal(0, baseline_p3b_std * noise_scale, n_trials_per_condition)
        blockade_n1 += np.random.normal(0, baseline_n1_std * noise_scale, n_trials_per_condition)
        blockade_p1 += np.random.normal(0, baseline_p1_std * noise_scale, n_trials_per_condition)
        
        # Compute statistics
        # P3b reduction (combined emotional + neutral)
        baseline_p3b_all = np.concatenate([baseline_emotional_p3b, baseline_neutral_p3b])
        blockade_p3b_all = np.concatenate([blockade_emotional_p3b, blockade_neutral_p3b])
        
        p3b_reduction_percent = (1.0 - np.mean(blockade_p3b_all) / np.mean(baseline_p3b_all)) * 100
        
        # Statistical tests
        p3b_ttest = stats.ttest_ind(baseline_p3b_all, blockade_p3b_all)
        p3b_reduction_pvalue = p3b_ttest.pvalue
        p3b_cohens_d = (np.mean(baseline_p3b_all) - np.mean(blockade_p3b_all)) / \
                       np.sqrt((np.std(baseline_p3b_all)**2 + np.std(blockade_p3b_all)**2) / 2)
        
        # Early component preservation
        n1_ttest = stats.ttest_ind(baseline_n1, blockade_n1)
        p1_ttest = stats.ttest_ind(baseline_p1, blockade_p1)
        early_preservation_pvalue = max(n1_ttest.pvalue, p1_ttest.pvalue)
        
        n1_preservation_percent = (np.mean(blockade_n1) / np.mean(baseline_n1)) * 100
        p1_preservation_percent = (np.mean(blockade_p1) / np.mean(baseline_p1)) * 100
        
        # Emotional selectivity
        emotional_reduction_percent = (1.0 - np.mean(blockade_emotional_p3b) / np.mean(baseline_emotional_p3b)) * 100
        neutral_reduction_percent = (1.0 - np.mean(blockade_neutral_p3b) / np.mean(baseline_neutral_p3b)) * 100
        emotional_selectivity_index = emotional_reduction_percent - neutral_reduction_percent
        
        # Test if emotional reduction > neutral reduction
        emotional_diff = baseline_emotional_p3b - blockade_emotional_p3b
        neutral_diff = baseline_neutral_p3b - blockade_neutral_p3b
        selectivity_ttest = stats.ttest_ind(emotional_diff, neutral_diff)
        emotional_selectivity_pvalue = selectivity_ttest.pvalue
        emotional_selectivity_cohens_d = (np.mean(emotional_diff) - np.mean(neutral_diff)) / \
                                        np.sqrt((np.std(emotional_diff)**2 + np.std(neutral_diff)**2) / 2)
        
        # Validate predictions
        meets_p3b_reduction = 20.0 <= p3b_reduction_percent <= 40.0 and p3b_reduction_pvalue < 0.01
        meets_early_preservation = abs(100 - n1_preservation_percent) < 10 and \
                                  abs(100 - p1_preservation_percent) < 10 and \
                                  early_preservation_pvalue > 0.05  # No significant change
        meets_emotional_selectivity = emotional_selectivity_index > 0 and \
                                     emotional_selectivity_pvalue < 0.05
        
        return BlockadeSimulationResult(
            baseline_p3b=np.mean(baseline_p3b_all),
            blockade_p3b=np.mean(blockade_p3b_all),
            p3b_reduction_percent=p3b_reduction_percent,
            emotional_baseline_p3b=np.mean(baseline_emotional_p3b),
            emotional_blockade_p3b=np.mean(blockade_emotional_p3b),
            neutral_baseline_p3b=np.mean(baseline_neutral_p3b),
            neutral_blockade_p3b=np.mean(blockade_neutral_p3b),
            emotional_selectivity_index=emotional_selectivity_index,
            baseline_n1=np.mean(baseline_n1),
            blockade_n1=np.mean(blockade_n1),
            n1_preservation_percent=n1_preservation_percent,
            baseline_p1=np.mean(baseline_p1),
            blockade_p1=np.mean(blockade_p1),
            p1_preservation_percent=p1_preservation_percent,
            p3b_reduction_pvalue=p3b_reduction_pvalue,
            early_preservation_pvalue=early_preservation_pvalue,
            emotional_selectivity_pvalue=emotional_selectivity_pvalue,
            p3b_reduction_cohens_d=p3b_cohens_d,
            emotional_selectivity_cohens_d=emotional_selectivity_cohens_d,
            meets_p3b_reduction_prediction=meets_p3b_reduction,
            meets_early_preservation_prediction=meets_early_preservation,
            meets_emotional_selectivity_prediction=meets_emotional_selectivity,
            n_trials_baseline=n_trials_per_condition * 2,
            n_trials_blockade=n_trials_per_condition * 2
        )
    
    def validate_mechanism_specificity(self,
                                      baseline_erps: List[ERPComponents],
                                      blockade_erps: List[ERPComponents]) -> Dict[str, any]:
        """
        Validate that blockade effects are specific to ignition mechanisms.
        
        Tests:
        1. P3b amplitude significantly reduced
        2. Early components (N1, P1) preserved
        3. Reduction specific to late (>250ms) components
        
        Args:
            baseline_erps: List of baseline ERP components
            blockade_erps: List of blockade ERP components
            
        Returns:
            Dictionary with validation results
        """
        # Extract P3b amplitudes
        baseline_p3b = np.array([erp.p3b_amplitude for erp in baseline_erps])
        blockade_p3b = np.array([erp.p3b_amplitude for erp in blockade_erps])
        
        # Extract early components
        baseline_n1 = np.array([erp.n1_amplitude for erp in baseline_erps])
        blockade_n1 = np.array([erp.n1_amplitude for erp in blockade_erps])
        baseline_p1 = np.array([erp.p1_amplitude for erp in baseline_erps])
        blockade_p1 = np.array([erp.p1_amplitude for erp in blockade_erps])
        
        # Statistical tests
        p3b_test = stats.ttest_ind(baseline_p3b, blockade_p3b)
        n1_test = stats.ttest_ind(baseline_n1, blockade_n1)
        p1_test = stats.ttest_ind(baseline_p1, blockade_p1)
        
        # Effect sizes
        p3b_d = (np.mean(baseline_p3b) - np.mean(blockade_p3b)) / \
                np.sqrt((np.std(baseline_p3b)**2 + np.std(blockade_p3b)**2) / 2)
        n1_d = (np.mean(baseline_n1) - np.mean(blockade_n1)) / \
               np.sqrt((np.std(baseline_n1)**2 + np.std(blockade_n1)**2) / 2)
        p1_d = (np.mean(baseline_p1) - np.mean(blockade_p1)) / \
               np.sqrt((np.std(baseline_p1)**2 + np.std(blockade_p1)**2) / 2)
        
        # Validation criteria
        p3b_impaired = p3b_test.pvalue < 0.01 and p3b_d > 0.5
        early_preserved = n1_test.pvalue > 0.05 and p1_test.pvalue > 0.05 and \
                         abs(n1_d) < 0.3 and abs(p1_d) < 0.3
        
        mechanism_specific = p3b_impaired and early_preserved
        
        return {
            'mechanism_specific': mechanism_specific,
            'p3b_impaired': p3b_impaired,
            'early_preserved': early_preserved,
            'p3b_pvalue': p3b_test.pvalue,
            'p3b_cohens_d': p3b_d,
            'n1_pvalue': n1_test.pvalue,
            'n1_cohens_d': n1_d,
            'p1_pvalue': p1_test.pvalue,
            'p1_cohens_d': p1_d,
            'p3b_reduction_percent': (1.0 - np.mean(blockade_p3b) / np.mean(baseline_p3b)) * 100,
            'n1_change_percent': (np.mean(blockade_n1) / np.mean(baseline_n1) - 1.0) * 100,
            'p1_change_percent': (np.mean(blockade_p1) / np.mean(baseline_p1) - 1.0) * 100
        }
    
    def generate_report(self, result: BlockadeSimulationResult) -> str:
        """
        Generate human-readable report of blockade simulation results.
        
        Args:
            result: BlockadeSimulationResult object
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("NEUROMODULATORY BLOCKADE SIMULATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        report.append("P3B AMPLITUDE REDUCTION:")
        report.append(f"  Baseline: {result.baseline_p3b:.2f} µV")
        report.append(f"  Blockade: {result.blockade_p3b:.2f} µV")
        report.append(f"  Reduction: {result.p3b_reduction_percent:.1f}%")
        report.append(f"  p-value: {result.p3b_reduction_pvalue:.4f}")
        report.append(f"  Cohen's d: {result.p3b_reduction_cohens_d:.2f}")
        report.append(f"  Prediction met (20-40% reduction): {result.meets_p3b_reduction_prediction}")
        report.append("")
        
        report.append("EMOTIONAL SELECTIVITY:")
        report.append(f"  Emotional baseline: {result.emotional_baseline_p3b:.2f} µV")
        report.append(f"  Emotional blockade: {result.emotional_blockade_p3b:.2f} µV")
        report.append(f"  Neutral baseline: {result.neutral_baseline_p3b:.2f} µV")
        report.append(f"  Neutral blockade: {result.neutral_blockade_p3b:.2f} µV")
        report.append(f"  Selectivity index: {result.emotional_selectivity_index:.1f}%")
        report.append(f"  p-value: {result.emotional_selectivity_pvalue:.4f}")
        report.append(f"  Cohen's d: {result.emotional_selectivity_cohens_d:.2f}")
        report.append(f"  Prediction met (emotional > neutral): {result.meets_emotional_selectivity_prediction}")
        report.append("")
        
        report.append("EARLY ERP PRESERVATION:")
        report.append(f"  N1 baseline: {result.baseline_n1:.2f} µV")
        report.append(f"  N1 blockade: {result.blockade_n1:.2f} µV")
        report.append(f"  N1 preservation: {result.n1_preservation_percent:.1f}%")
        report.append(f"  P1 baseline: {result.baseline_p1:.2f} µV")
        report.append(f"  P1 blockade: {result.blockade_p1:.2f} µV")
        report.append(f"  P1 preservation: {result.p1_preservation_percent:.1f}%")
        report.append(f"  p-value: {result.early_preservation_pvalue:.4f}")
        report.append(f"  Prediction met (<10% change): {result.meets_early_preservation_prediction}")
        report.append("")
        
        report.append("OVERALL VALIDATION:")
        all_predictions_met = (result.meets_p3b_reduction_prediction and
                              result.meets_early_preservation_prediction and
                              result.meets_emotional_selectivity_prediction)
        report.append(f"  All predictions met: {all_predictions_met}")
        report.append(f"  Sample size: {result.n_trials_baseline} baseline, {result.n_trials_blockade} blockade")
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
