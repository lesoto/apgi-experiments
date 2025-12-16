"""
Tests for clinical modules.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add clinical modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'apgi_framework', 'clinical'))

from disorder_classification import (
    DisorderType, NeuralSignatureProfile, DisorderClassification, ClassificationResult
)
from parameter_extraction import (
    ClinicalParameterExtractor, ClinicalParameters, AssessmentTask
)
from treatment_prediction import (
    TreatmentPredictor, TreatmentPrediction, TreatmentType
)


class TestDisorderClassification:
    """Test disorder classification functionality."""
    
    def test_disorder_type_enum(self):
        """Test disorder type enumeration."""
        assert DisorderType.CONTROL.value == "control"
        assert DisorderType.GAD.value == "generalized_anxiety_disorder"
        assert DisorderType.PANIC.value == "panic_disorder"
        assert DisorderType.SOCIAL_ANXIETY.value == "social_anxiety_disorder"
        assert DisorderType.DEPRESSION.value == "major_depressive_disorder"
        assert DisorderType.PTSD.value == "post_traumatic_stress_disorder"
    
    def test_neural_signature_profile_initialization(self):
        """Test neural signature profile initialization."""
        profile = NeuralSignatureProfile()
        
        # Test default values
        assert profile.p3b_amplitude_extero == 0.0
        assert profile.p3b_amplitude_intero == 0.0
        assert profile.p3b_latency_extero == 350.0
        assert profile.p3b_latency_intero == 350.0
        assert profile.gamma_power_frontal == 0.0
        assert profile.gamma_power_posterior == 0.0
        assert profile.gamma_coherence == 0.0
        assert profile.microstate_duration == 0.0
        assert profile.microstate_transitions == 0.0
        assert profile.pupil_dilation_intero == 0.0
        assert profile.pupil_latency == 0.0
    
    def test_neural_signature_profile_custom_values(self):
        """Test neural signature profile with custom values."""
        profile = NeuralSignatureProfile(
            p3b_amplitude_extero=5.5,
            p3b_amplitude_intero=3.2,
            gamma_power_frontal=1.2,
            gamma_coherence=0.8,
            microstate_duration=120.0
        )
        
        assert profile.p3b_amplitude_extero == 5.5
        assert profile.p3b_amplitude_intero == 3.2
        assert profile.gamma_power_frontal == 1.2
        assert profile.gamma_coherence == 0.8
        assert profile.microstate_duration == 120.0
    
    def test_disorder_classification_initialization(self):
        """Test disorder classification initialization."""
        classifier = DisorderClassification()
        
        assert classifier.classifier_type == "random_forest"
        assert classifier.scaler is not None
        assert classifier.classifier is not None
    
    def test_disorder_classification_different_models(self):
        """Test disorder classification with different model types."""
        # Test Random Forest
        rf_classifier = DisorderClassification(classifier_type="random_forest")
        assert rf_classifier.classifier_type == "random_forest"
        
        # Test Gradient Boosting
        gb_classifier = DisorderClassification(classifier_type="gradient_boosting")
        assert gb_classifier.classifier_type == "gradient_boosting"
        
        # Test SVM
        svm_classifier = DisorderClassification(classifier_type="svm")
        assert svm_classifier.classifier_type == "svm"
    
    def test_feature_extraction_from_profile(self):
        """Test feature extraction from neural signature profile."""
        profile = NeuralSignatureProfile(
            p3b_amplitude_extero=5.5,
            p3b_amplitude_intero=3.2,
            gamma_power_frontal=1.2,
            gamma_coherence=0.8,
            microstate_duration=120.0
        )
        
        classifier = DisorderClassification()
        features = classifier.extract_neural_signature(profile)
        
        assert len(features) > 0
        assert isinstance(features, np.ndarray)
        assert features.dtype == float
    
    def test_data_preparation(self):
        """Test data preparation for training."""
        profiles = [
            NeuralSignatureProfile(p3b_amplitude_extero=5.0, gamma_power_frontal=1.0),
            NeuralSignatureProfile(p3b_amplitude_extero=3.0, gamma_power_frontal=0.5),
            NeuralSignatureProfile(p3b_amplitude_extero=7.0, gamma_power_frontal=1.5),
        ]
        labels = [DisorderType.GAD, DisorderType.CONTROL, DisorderType.PANIC]
        
        classifier = DisorderClassifier()
        X, y = classifier._prepare_data(profiles, labels)
        
        assert X.shape[0] == len(profiles)
        assert len(y) == len(labels)
        assert isinstance(X, np.ndarray)
        assert isinstance(y, np.ndarray)
    
    def test_model_training(self):
        """Test model training with sample data."""
        # Generate sample data
        np.random.seed(42)
        n_samples = 50
        profiles = []
        labels = []
        
        for i in range(n_samples):
            profile = NeuralSignatureProfile(
                p3b_amplitude_extero=np.random.normal(5, 2),
                p3b_amplitude_intero=np.random.normal(3, 1),
                gamma_power_frontal=np.random.normal(1, 0.5),
                gamma_coherence=np.random.normal(0.6, 0.2)
            )
            profiles.append(profile)
            # Assign labels based on some simple rules
            if profile.p3b_amplitude_extero > 6:
                labels.append(DisorderType.GAD)
            elif profile.gamma_power_frontal > 1.2:
                labels.append(DisorderType.PANIC)
            else:
                labels.append(DisorderType.CONTROL)
        
        classifier = DisorderClassifier()
        classifier.train(profiles, labels)
        
        assert classifier.is_trained is True
        assert classifier.scaler is not None
        assert classifier.model is not None
    
    def test_prediction(self):
        """Test disorder prediction."""
        # Train classifier first
        profiles = [
            NeuralSignatureProfile(p3b_amplitude_extero=7.0, gamma_power_frontal=1.5),
            NeuralSignatureProfile(p3b_amplitude_extero=3.0, gamma_power_frontal=0.5),
        ]
        labels = [DisorderType.GAD, DisorderType.CONTROL]
        
        classifier = DisorderClassifier()
        classifier.train(profiles, labels)
        
        # Test prediction
        test_profile = NeuralSignatureProfile(
            p3b_amplitude_extero=6.5,
            gamma_power_frontal=1.3
        )
        
        prediction = classifier.predict(test_profile)
        probabilities = classifier.predict_proba(test_profile)
        
        assert prediction in [DisorderType.GAD, DisorderType.CONTROL, DisorderType.PANIC, 
                           DisorderType.SOCIAL_ANXIETY, DisorderType.DEPRESSION, DisorderType.PTSD]
        assert len(probabilities) == len(DisorderType)
        assert all(0 <= p <= 1 for p in probabilities.values())
        assert abs(sum(probabilities.values()) - 1.0) < 0.01
    
    def test_cross_validation(self):
        """Test cross-validation evaluation."""
        # Generate sample data
        np.random.seed(42)
        profiles = []
        labels = []
        
        for i in range(30):
            profile = NeuralSignatureProfile(
                p3b_amplitude_extero=np.random.normal(5, 2),
                gamma_power_frontal=np.random.normal(1, 0.5)
            )
            profiles.append(profile)
            labels.append(DisorderType.GAD if i % 2 == 0 else DisorderType.CONTROL)
        
        classifier = DisorderClassifier()
        scores = classifier.cross_validate(profiles, labels, cv=3)
        
        assert len(scores) == 3
        assert all(0 <= s <= 1 for s in scores)
        assert np.mean(scores) > 0  # Should have some predictive power


class TestParameterExtraction:
    """Test clinical parameter extraction functionality."""
    
    def test_parameter_extraction_config(self):
        """Test parameter extraction configuration."""
        config = ParameterExtractionConfig()
        
        assert config.window_size_ms == 1000
        assert config.overlap_ms == 500
        assert config.baseline_correction is True
        assert config.artifact_rejection is True
    
    def test_parameter_extraction_config_custom(self):
        """Test parameter extraction configuration with custom values."""
        config = ParameterExtractionConfig(
            window_size_ms=2000,
            overlap_ms=1000,
            baseline_correction=False
        )
        
        assert config.window_size_ms == 2000
        assert config.overlap_ms == 1000
        assert config.baseline_correction is False
    
    def test_clinical_parameter_extractor_initialization(self):
        """Test clinical parameter extractor initialization."""
        extractor = ClinicalParameterExtractor()
        
        assert extractor.config.window_size_ms == 1000
        assert extractor.config.overlap_ms == 500
        assert extractor.config.baseline_correction is True
    
    def test_p3b_amplitude_extraction(self):
        """Test P3b amplitude extraction from simulated data."""
        extractor = ClinicalParameterExtractor()
        
        # Simulate EEG data with P3b component
        sampling_rate = 1000  # Hz
        time_points = np.linspace(0, 1, sampling_rate)
        
        # Create simulated P3b waveform
        eeg_data = np.zeros(sampling_rate)
        p3b_peak_idx = int(350 * sampling_rate / 1000)  # 350ms latency
        eeg_data[p3b_peak_idx-20:p3b_peak_idx+20] = 5.0  # P3b peak
        
        amplitude = extractor._extract_p3b_amplitude(eeg_data, sampling_rate)
        
        assert amplitude > 0
        assert isinstance(amplitude, float)
    
    def test_gamma_power_extraction(self):
        """Test gamma power extraction from simulated data."""
        extractor = ClinicalParameterExtractor()
        
        # Simulate EEG data with gamma activity
        sampling_rate = 1000
        duration = 2.0  # seconds
        t = np.linspace(0, duration, int(sampling_rate * duration))
        
        # Create gamma oscillation (40 Hz)
        gamma_signal = np.sin(2 * np.pi * 40 * t) * 0.5
        eeg_data = gamma_signal + np.random.normal(0, 0.1, len(t))
        
        gamma_power = extractor._extract_gamma_power(eeg_data, sampling_rate)
        
        assert gamma_power > 0
        assert isinstance(gamma_power, float)
    
    def test_microstate_analysis(self):
        """Test microstate analysis parameters."""
        extractor = ClinicalParameterExtractor()
        
        # Simulate microstate transition data
        microstate_sequence = [1, 1, 2, 2, 3, 3, 4, 4, 1, 1, 2, 2]
        sampling_rate = 1000
        
        duration, transitions = extractor._analyze_microstates(microstate_sequence, sampling_rate)
        
        assert duration > 0
        assert transitions > 0
        assert isinstance(duration, float)
        assert isinstance(transitions, float)
    
    def test_pupillometry_extraction(self):
        """Test pupillometry parameter extraction."""
        extractor = ClinicalParameterExtractor()
        
        # Simulate pupil dilation data
        sampling_rate = 1000
        duration = 5.0  # seconds
        t = np.linspace(0, duration, int(sampling_rate * duration))
        
        # Create pupil dilation response
        pupil_data = np.ones(len(t)) * 3.0  # baseline 3mm
        stimulus_idx = int(2.0 * sampling_rate)  # stimulus at 2s
        pupil_data[stimulus_idx:stimulus_idx+500] += 0.5  # dilation response
        
        dilation, latency = extractor._extract_pupil_response(pupil_data, sampling_rate)
        
        assert dilation > 0
        assert latency > 0
        assert isinstance(dilation, float)
        assert isinstance(latency, float)
    
    def test_comprehensive_parameter_extraction(self):
        """Test comprehensive parameter extraction from all modalities."""
        extractor = ClinicalParameterExtractor()
        
        # Simulate multi-modal data
        sampling_rate = 1000
        duration = 2.0
        t = np.linspace(0, duration, int(sampling_rate * duration))
        
        # EEG data with P3b and gamma
        eeg_data = np.random.normal(0, 1, len(t))
        p3b_idx = int(350 * sampling_rate / 1000)
        eeg_data[p3b_idx-20:p3b_idx+20] = 5.0
        
        # Gamma oscillation
        eeg_data += np.sin(2 * np.pi * 40 * t) * 0.5
        
        # Pupil data
        pupil_data = np.ones(len(t)) * 3.0
        pupil_data[int(1.0*sampling_rate):int(1.5*sampling_rate)] += 0.5
        
        # Microstate sequence
        microstates = np.random.choice([1, 2, 3, 4], size=len(t)//100)
        
        profile = extractor.extract_comprehensive_profile(
            eeg_data=eeg_data,
            pupil_data=pupil_data,
            microstate_sequence=microstates,
            sampling_rate=sampling_rate
        )
        
        assert isinstance(profile, NeuralSignatureProfile)
        assert profile.p3b_amplitude_extero > 0
        assert profile.gamma_power_frontal > 0
        assert profile.pupil_dilation_intero > 0


class TestTreatmentPrediction:
    """Test treatment prediction functionality."""
    
    def test_treatment_response_model_initialization(self):
        """Test treatment response model initialization."""
        model = TreatmentResponseModel()
        
        assert model.model_type == "gradient_boosting"
        assert model.is_trained is False
        assert model.feature_importance is None
    
    def test_treatment_predictor_initialization(self):
        """Test treatment predictor initialization."""
        predictor = TreatmentPredictor()
        
        assert predictor.model is not None
        assert predictor.scaler is not None
        assert predictor.response_threshold == 0.5
    
    def test_feature_engineering(self):
        """Test feature engineering for treatment prediction."""
        predictor = TreatmentPredictor()
        
        # Create sample neural profile
        profile = NeuralSignatureProfile(
            p3b_amplitude_extero=5.5,
            p3b_amplitude_intero=3.2,
            gamma_power_frontal=1.2,
            gamma_coherence=0.8,
            microstate_duration=120.0
        )
        
        # Create sample clinical variables
        clinical_vars = {
            'age': 35,
            'severity_score': 8.5,
            'duration_months': 24,
            'comorbidities': 1
        }
        
        features = predictor._engineer_features(profile, clinical_vars)
        
        assert len(features) > 0
        assert isinstance(features, np.ndarray)
        assert features.dtype == float
    
    def test_treatment_response_prediction(self):
        """Test treatment response prediction."""
        predictor = TreatmentPredictor()
        
        # Create sample data for training
        profiles = []
        clinical_vars = []
        responses = []
        
        np.random.seed(42)
        for i in range(30):
            profile = NeuralSignatureProfile(
                p3b_amplitude_extero=np.random.normal(5, 2),
                gamma_power_frontal=np.random.normal(1, 0.5)
            )
            vars_dict = {
                'age': np.random.randint(18, 65),
                'severity_score': np.random.uniform(5, 15),
                'duration_months': np.random.randint(6, 60),
                'comorbidities': np.random.randint(0, 3)
            }
            response = 1 if (profile.p3b_amplitude_extero > 5 and vars_dict['severity_score'] < 10) else 0
            
            profiles.append(profile)
            clinical_vars.append(vars_dict)
            responses.append(response)
        
        # Train model
        predictor.train(profiles, clinical_vars, responses)
        
        # Test prediction
        test_profile = NeuralSignatureProfile(
            p3b_amplitude_extero=6.0,
            gamma_power_frontal=1.3
        )
        test_clinical = {
            'age': 40,
            'severity_score': 7.5,
            'duration_months': 18,
            'comorbidities': 1
        }
        
        prediction = predictor.predict_response(test_profile, test_clinical)
        probability = predictor.predict_probability(test_profile, test_clinical)
        
        assert prediction in [0, 1]
        assert 0 <= probability <= 1
        assert isinstance(prediction, (int, np.integer))
        assert isinstance(probability, (float, np.floating))
    
    def test_treatment_recommendation(self):
        """Test treatment recommendation based on prediction."""
        predictor = TreatmentPredictor()
        
        # Create simple test case
        profile = NeuralSignatureProfile(p3b_amplitude_extero=6.0)
        clinical_vars = {'age': 35, 'severity_score': 8.0}
        
        # Mock the prediction to test recommendation logic
        with patch.object(predictor, 'predict_probability', return_value=0.8):
            recommendation = predictor.recommend_treatment(profile, clinical_vars)
            
            assert 'treatment_type' in recommendation
            assert 'confidence' in recommendation
            assert 'rationale' in recommendation
            assert recommendation['confidence'] == 0.8
    
    def test_model_evaluation(self):
        """Test treatment prediction model evaluation."""
        predictor = TreatmentPredictor()
        
        # Generate sample data
        profiles = []
        clinical_vars = []
        responses = []
        
        np.random.seed(42)
        for i in range(50):
            profile = NeuralSignatureProfile(
                p3b_amplitude_extero=np.random.normal(5, 2)
            )
            vars_dict = {'severity_score': np.random.uniform(5, 15)}
            response = 1 if profile.p3b_amplitude_extero > 5 else 0
            
            profiles.append(profile)
            clinical_vars.append(vars_dict)
            responses.append(response)
        
        # Train and evaluate
        predictor.train(profiles, clinical_vars, responses)
        metrics = predictor.evaluate_model(profiles, clinical_vars, responses)
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert 'auc_score' in metrics
        
        # All metrics should be between 0 and 1
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, (int, float)):
                assert 0 <= metric_value <= 1


class TestClinicalIntegration:
    """Test integration between clinical modules."""
    
    def test_classification_to_treatment_pipeline(self):
        """Test pipeline from disorder classification to treatment prediction."""
        # Create sample neural profile
        profile = NeuralSignatureProfile(
            p3b_amplitude_extero=6.5,
            p3b_amplitude_intero=4.2,
            gamma_power_frontal=1.3,
            gamma_coherence=0.7,
            microstate_duration=110.0
        )
        
        # Classify disorder
        classifier = DisorderClassifier()
        
        # Create minimal training data
        train_profiles = [
            NeuralSignatureProfile(p3b_amplitude_extero=7.0),
            NeuralSignatureProfile(p3b_amplitude_extero=3.0),
        ]
        train_labels = [DisorderType.GAD, DisorderType.CONTROL]
        classifier.train(train_profiles, train_labels)
        
        disorder = classifier.predict(profile)
        
        # Predict treatment response
        predictor = TreatmentPredictor()
        clinical_vars = {
            'age': 35,
            'severity_score': 8.5,
            'duration_months': 24
        }
        
        # Create minimal training data for predictor
        treatment_profiles = [profile, train_profiles[0]]
        treatment_clinical = [clinical_vars, {'age': 30, 'severity_score': 7.0}]
        treatment_responses = [1, 0]
        predictor.train(treatment_profiles, treatment_clinical, treatment_responses)
        
        response_prob = predictor.predict_probability(profile, clinical_vars)
        
        # Should have valid results from both modules
        assert disorder in DisorderType
        assert 0 <= response_prob <= 1
    
    def test_parameter_extraction_to_classification(self):
        """Test pipeline from parameter extraction to disorder classification."""
        extractor = ClinicalParameterExtractor()
        
        # Simulate raw data
        sampling_rate = 1000
        duration = 2.0
        t = np.linspace(0, duration, int(sampling_rate * duration))
        
        eeg_data = np.random.normal(0, 1, len(t))
        eeg_data[int(0.35*sampling_rate):int(0.4*sampling_rate)] = 5.0  # P3b
        
        pupil_data = np.ones(len(t)) * 3.0
        pupil_data[int(1.0*sampling_rate):int(1.5*sampling_rate)] += 0.5
        
        microstates = np.random.choice([1, 2, 3, 4], size=len(t)//100)
        
        # Extract parameters
        profile = extractor.extract_comprehensive_profile(
            eeg_data=eeg_data,
            pupil_data=pupil_data,
            microstate_sequence=microstates,
            sampling_rate=sampling_rate
        )
        
        # Classify using extracted parameters
        classifier = DisorderClassifier()
        
        # Create training data
        train_profiles = [profile, NeuralSignatureProfile()]
        train_labels = [DisorderType.GAD, DisorderType.CONTROL]
        classifier.train(train_profiles, train_labels)
        
        prediction = classifier.predict(profile)
        
        assert isinstance(prediction, DisorderType)
        assert isinstance(profile, NeuralSignatureProfile)


if __name__ == "__main__":
    pytest.main([__file__])
