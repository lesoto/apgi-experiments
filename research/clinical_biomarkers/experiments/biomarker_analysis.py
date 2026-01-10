"""
Clinical biomarkers analysis module for APGI Framework.

Implements comprehensive biomarker identification and validation for clinical
applications in mental health and neurological disorders.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
import numpy as np
from scipy import stats, signal
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.decomposition import PCA
import logging

from ..exceptions import ValidationError, SimulationError
from ..logging.standardized_logging import get_logger

logger = get_logger("clinical_biomarkers")


class ClinicalCondition(Enum):
    """Clinical conditions for biomarker analysis."""
    
    HEALTHY_CONTROL = "healthy_control"
    GENERALIZED_ANXIETY = "generalized_anxiety_disorder"
    PANIC_DISORDER = "panic_disorder"
    SOCIAL_ANXIETY = "social_anxiety_disorder"
    MAJOR_DEPRESSION = "major_depressive_disorder"
    PTSD = "post_traumatic_stress_disorder"
    SCHIZOPHRENIA = "schizophrenia"
    BIPOLAR_DISORDER = "bipolar_disorder"
    ADHD = "attention_deficit_hyperactivity_disorder"
    AUTISM_SPECTRUM = "autism_spectrum_disorder"
    ALZHEIMERS = "alzheimers_disease"
    PARKINSONS = "parkinsons_disease"


class BiomarkerType(Enum):
    """Types of clinical biomarkers."""
    
    NEURAL_SIGNATURE = "neural_signature"
    HEART_RATE_VARIABILITY = "heart_rate_variability"
    PUPILLOMETRY = "pupillometry"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    COGNITIVE_PERFORMANCE = "cognitive_performance"
    METABOLIC_MARKER = "metabolic_marker"
    GENETIC_MARKER = "genetic_marker"
    NEUROIMAGING = "neuroimaging"


class BiomarkerCategory(Enum):
    """Categories of biomarkers based on clinical utility."""
    
    DIAGNOSTIC = "diagnostic"
    PROGNOSTIC = "prognostic"
    PREDICTIVE = "predictive"
    MONITORING = "monitoring"
    SCREENING = "screening"


@dataclass
class BiomarkerFeature:
    """Individual biomarker feature with statistical properties."""
    
    name: str
    value: float
    reference_range: Tuple[float, float]
    clinical_significance: float  # 0-1 scale
    reliability: float  # Test-retest reliability
    validity: float  # Construct validity
    
    # Statistical properties
    effect_size: float
    confidence_interval: Tuple[float, float]
    p_value: float
    
    # Clinical interpretation
    interpretation: str
    clinical_actionability: float  # 0-1 scale


@dataclass
class ClinicalBiomarker:
    """Comprehensive clinical biomarker definition."""
    
    name: str
    biomarker_type: BiomarkerType
    category: BiomarkerCategory
    target_conditions: List[ClinicalCondition]
    
    # Biomarker features
    features: List[BiomarkerFeature] = field(default_factory=list)
    
    # Validation metrics
    sensitivity: float = 0.0
    specificity: float = 0.0
    positive_predictive_value: float = 0.0
    negative_predictive_value: float = 0.0
    auc_score: float = 0.0
    
    # Clinical utility
    clinical_validity: float = 0.0  # Overall clinical validity
    clinical_utility: float = 0.0  # Practical utility in clinical setting
    implementation_feasibility: float = 0.0  # Ease of implementation
    
    # Metadata
    description: str = ""
    evidence_level: str = "moderate"  # strong, moderate, limited
    regulatory_status: str = "research"  # approved, investigational, research


@dataclass
class PatientProfile:
    """Patient clinical profile for biomarker analysis."""
    
    patient_id: str
    age: int
    sex: str
    clinical_condition: ClinicalCondition
    severity_score: float  # 0-1 scale
    
    # Neural signatures
    p3b_amplitude_extero: Optional[float] = None
    p3b_amplitude_intero: Optional[float] = None
    p3b_latency_extero: Optional[float] = None
    p3b_latency_intero: Optional[float] = None
    
    # Gamma synchrony
    gamma_power_frontal: Optional[float] = None
    gamma_power_posterior: Optional[float] = None
    gamma_coherence: Optional[float] = None
    
    # Microstate metrics
    microstate_duration: Optional[float] = None
    microstate_transitions: Optional[float] = None
    
    # Pupillometry
    pupil_diameter_intero: Optional[float] = None
    pupil_diameter_extero: Optional[float] = None
    pupil_latency_intero: Optional[float] = None
    pupil_latency_extero: Optional[float] = None
    
    # Cardiac metrics
    hrv_rmssd: Optional[float] = None
    hrv_hf_power: Optional[float] = None
    heart_rate: Optional[float] = None
    
    # Behavioral metrics
    reaction_time: Optional[float] = None
    accuracy: Optional[float] = None
    confidence_rating: Optional[float] = None
    
    # Clinical questionnaires
    anxiety_score: Optional[float] = None
    depression_score: Optional[float] = None
    ptsd_score: Optional[float] = None
    
    # Metadata
    medications: List[str] = field(default_factory=list)
    comorbidities: List[str] = field(default_factory=list)
    treatment_history: List[str] = field(default_factory=list)


class BiomarkerAnalyzer:
    """
    Comprehensive clinical biomarker analysis system.
    
    Provides biomarker identification, validation, and clinical interpretation
    for mental health and neurological disorders.
    """
    
    def __init__(self, significance_threshold: float = 0.05):
        """
        Initialize biomarker analyzer.
        
        Args:
            significance_threshold: Statistical significance threshold for biomarker discovery
        """
        self.significance_threshold = significance_threshold
        self.scaler = StandardScaler()
        self.classifiers = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(random_state=42),
            'svm': SVC(kernel='rbf', probability=True, random_state=42)
        }
        
        # Initialize known biomarkers
        self.biomarkers = self._initialize_known_biomarkers()
        
        logger.info(f"BiomarkerAnalyzer initialized with threshold {significance_threshold}")
    
    def _initialize_known_biomarkers(self) -> Dict[str, ClinicalBiomarker]:
        """Initialize known clinical biomarkers."""
        biomarkers = {}
        
        # P3b amplitude reduction biomarker for depression
        biomarkers['p3b_depression'] = ClinicalBiomarker(
            name="P3b Amplitude Reduction",
            biomarker_type=BiomarkerType.NEURAL_SIGNATURE,
            category=BiomarkerCategory.DIAGNOSTIC,
            target_conditions=[ClinicalCondition.MAJOR_DEPRESSION],
            description="Reduced P3b amplitude associated with major depressive disorder",
            evidence_level="moderate"
        )
        
        # HRV reduction biomarker for anxiety
        biomarkers['hrv_anxiety'] = ClinicalBiomarker(
            name="Heart Rate Variability Reduction",
            biomarker_type=BiomarkerType.HEART_RATE_VARIABILITY,
            category=BiomarkerCategory.MONITORING,
            target_conditions=[ClinicalCondition.GENERALIZED_ANXIETY, ClinicalCondition.PANIC_DISORDER],
            description="Reduced HRV associated with anxiety disorders",
            evidence_level="strong"
        )
        
        # Gamma synchrony biomarker for schizophrenia
        biomarkers['gamma_schizophrenia'] = ClinicalBiomarker(
            name="Gamma Band Synchrony Reduction",
            biomarker_type=BiomarkerType.NEURAL_SIGNATURE,
            category=BiomarkerCategory.DIAGNOSTIC,
            target_conditions=[ClinicalCondition.SCHIZOPHRENIA],
            description="Reduced gamma synchrony in schizophrenia",
            evidence_level="moderate"
        )
        
        # Pupillometry biomarker for ADHD
        biomarkers['pupil_adhd'] = ClinicalBiomarker(
            name="Pupil Dilation Abnormalities",
            biomarker_type=BiomarkerType.PUPILLOMETRY,
            category=BiomarkerCategory.SCREENING,
            target_conditions=[ClinicalCondition.ADHD],
            description="Abnormal pupil dilation patterns in ADHD",
            evidence_level="limited"
        )
        
        return biomarkers
    
    def add_patient_data(self, patient: PatientProfile) -> None:
        """
        Add patient data for biomarker analysis.
        
        Args:
            patient: Patient profile with clinical and neural data
        """
        # Validate patient data
        self._validate_patient_data(patient)
        
        logger.info(f"Added patient {patient.patient_id} with {patient.clinical_condition.value}")
    
    def _validate_patient_data(self, patient: PatientProfile) -> None:
        """Validate patient data completeness."""
        required_fields = ['patient_id', 'age', 'sex', 'clinical_condition']
        
        for field in required_fields:
            if getattr(patient, field) is None:
                raise ValidationError(f"Missing required field: {field}")
        
        if patient.age < 0 or patient.age > 120:
            raise ValidationError(f"Invalid age: {patient.age}")
    
    def discover_biomarkers(self, patients: List[PatientProfile], 
                          target_condition: ClinicalCondition) -> List[ClinicalBiomarker]:
        """
        Discover novel biomarkers for a specific clinical condition.
        
        Args:
            patients: List of patient profiles
            target_condition: Target clinical condition
            
        Returns:
            List of discovered biomarkers
        """
        logger.info(f"Discovering biomarkers for {target_condition.value}")
        
        # Separate cases and controls
        cases = [p for p in patients if p.clinical_condition == target_condition]
        controls = [p for p in patients if p.clinical_condition == ClinicalCondition.HEALTHY_CONTROL]
        
        if len(cases) < 10 or len(controls) < 10:
            raise ValidationError("Insufficient data for biomarker discovery (need at least 10 per group)")
        
        discovered_biomarkers = []
        
        # Analyze different feature types
        feature_analyzers = {
            'neural_signatures': self._analyze_neural_signatures,
            'hrv_features': self._analyze_hrv_features,
            'pupillometry_features': self._analyze_pupillometry_features,
            'behavioral_features': self._analyze_behavioral_features
        }
        
        for feature_type, analyzer in feature_analyzers.items():
            try:
                biomarkers = analyzer(cases, controls, target_condition)
                discovered_biomarkers.extend(biomarkers)
            except Exception as e:
                logger.warning(f"Failed to analyze {feature_type}: {e}")
                continue
        
        logger.info(f"Discovered {len(discovered_biomarkers)} potential biomarkers")
        return discovered_biomarkers
    
    def _analyze_neural_signatures(self, cases: List[PatientProfile], 
                                  controls: List[PatientProfile],
                                  target_condition: ClinicalCondition) -> List[ClinicalBiomarker]:
        """Analyze neural signature features for biomarkers."""
        biomarkers = []
        
        # P3b amplitude analysis
        p3b_features = ['p3b_amplitude_extero', 'p3b_amplitude_intero']
        for feature in p3b_features:
            case_values = [getattr(p, feature) for p in cases if getattr(p, feature) is not None]
            control_values = [getattr(p, feature) for p in controls if getattr(p, feature) is not None]
            
            if len(case_values) >= 5 and len(control_values) >= 5:
                biomarker = self._create_feature_biomarker(
                    feature, case_values, control_values, target_condition,
                    BiomarkerType.NEURAL_SIGNATURE
                )
                if biomarker:
                    biomarkers.append(biomarker)
        
        # Gamma synchrony analysis
        gamma_features = ['gamma_power_frontal', 'gamma_power_posterior', 'gamma_coherence']
        for feature in gamma_features:
            case_values = [getattr(p, feature) for p in cases if getattr(p, feature) is not None]
            control_values = [getattr(p, feature) for p in controls if getattr(p, feature) is not None]
            
            if len(case_values) >= 5 and len(control_values) >= 5:
                biomarker = self._create_feature_biomarker(
                    feature, case_values, control_values, target_condition,
                    BiomarkerType.NEURAL_SIGNATURE
                )
                if biomarker:
                    biomarkers.append(biomarker)
        
        return biomarkers
    
    def _analyze_hrv_features(self, cases: List[PatientProfile], 
                            controls: List[PatientProfile],
                            target_condition: ClinicalCondition) -> List[ClinicalBiomarker]:
        """Analyze HRV features for biomarkers."""
        biomarkers = []
        
        hrv_features = ['hrv_rmssd', 'hrv_hf_power', 'heart_rate']
        for feature in hrv_features:
            case_values = [getattr(p, feature) for p in cases if getattr(p, feature) is not None]
            control_values = [getattr(p, feature) for p in controls if getattr(p, feature) is not None]
            
            if len(case_values) >= 5 and len(control_values) >= 5:
                biomarker = self._create_feature_biomarker(
                    feature, case_values, control_values, target_condition,
                    BiomarkerType.HEART_RATE_VARIABILITY
                )
                if biomarker:
                    biomarkers.append(biomarker)
        
        return biomarkers
    
    def _analyze_pupillometry_features(self, cases: List[PatientProfile], 
                                     controls: List[PatientProfile],
                                     target_condition: ClinicalCondition) -> List[ClinicalBiomarker]:
        """Analyze pupillometry features for biomarkers."""
        biomarkers = []
        
        pupil_features = ['pupil_diameter_intero', 'pupil_diameter_extero', 
                         'pupil_latency_intero', 'pupil_latency_extero']
        for feature in pupil_features:
            case_values = [getattr(p, feature) for p in cases if getattr(p, feature) is not None]
            control_values = [getattr(p, feature) for p in controls if getattr(p, feature) is not None]
            
            if len(case_values) >= 5 and len(control_values) >= 5:
                biomarker = self._create_feature_biomarker(
                    feature, case_values, control_values, target_condition,
                    BiomarkerType.PUPILLOMETRY
                )
                if biomarker:
                    biomarkers.append(biomarker)
        
        return biomarkers
    
    def _analyze_behavioral_features(self, cases: List[PatientProfile], 
                                   controls: List[PatientProfile],
                                   target_condition: ClinicalCondition) -> List[ClinicalBiomarker]:
        """Analyze behavioral features for biomarkers."""
        biomarkers = []
        
        behavioral_features = ['reaction_time', 'accuracy', 'confidence_rating']
        for feature in behavioral_features:
            case_values = [getattr(p, feature) for p in cases if getattr(p, feature) is not None]
            control_values = [getattr(p, feature) for p in controls if getattr(p, feature) is not None]
            
            if len(case_values) >= 5 and len(control_values) >= 5:
                biomarker = self._create_feature_biomarker(
                    feature, case_values, control_values, target_condition,
                    BiomarkerType.BEHAVIORAL_PATTERN
                )
                if biomarker:
                    biomarkers.append(biomarker)
        
        return biomarkers
    
    def _create_feature_biomarker(self, feature_name: str, case_values: List[float], 
                                control_values: List[float], target_condition: ClinicalCondition,
                                biomarker_type: BiomarkerType) -> Optional[ClinicalBiomarker]:
        """Create a biomarker from feature analysis."""
        # Statistical test
        t_stat, p_value = stats.ttest_ind(case_values, control_values)
        
        if p_value > self.significance_threshold:
            return None
        
        # Effect size
        pooled_std = np.sqrt(((len(case_values) - 1) * np.var(case_values, ddof=1) + 
                             (len(control_values) - 1) * np.var(control_values, ddof=1)) / 
                            (len(case_values) + len(control_values) - 2))
        
        effect_size = (np.mean(case_values) - np.mean(control_values)) / pooled_std if pooled_std > 0 else 0
        
        # Confidence interval
        se = pooled_std * np.sqrt(1/len(case_values) + 1/len(control_values))
        mean_diff = np.mean(case_values) - np.mean(control_values)
        ci_lower = mean_diff - 1.96 * se
        ci_upper = mean_diff + 1.96 * se
        
        # Reference range (from controls)
        reference_range = (np.percentile(control_values, 2.5), np.percentile(control_values, 97.5))
        
        # Create biomarker feature
        biomarker_feature = BiomarkerFeature(
            name=feature_name,
            value=np.mean(case_values),
            reference_range=reference_range,
            clinical_significance=min(1.0, abs(effect_size) / 0.8),  # Normalize to 0-1
            reliability=0.8,  # Default reliability
            validity=0.8,  # Default validity
            effect_size=effect_size,
            confidence_interval=(ci_lower, ci_upper),
            p_value=p_value,
            interpretation=self._interpret_feature(feature_name, effect_size),
            clinical_actionability=min(1.0, abs(effect_size) / 0.5)
        )
        
        # Create biomarker
        biomarker = ClinicalBiomarker(
            name=f"{feature_name.replace('_', ' ').title()} Biomarker",
            biomarker_type=biomarker_type,
            category=BiomarkerCategory.DIAGNOSTIC,
            target_conditions=[target_condition],
            features=[biomarker_feature],
            description=f"Abnormal {feature_name.replace('_', ' ')} in {target_condition.value}",
            evidence_level="moderate" if p_value < 0.01 else "limited"
        )
        
        return biomarker
    
    def _interpret_feature(self, feature_name: str, effect_size: float) -> str:
        """Generate clinical interpretation for a feature."""
        direction = "elevated" if effect_size > 0 else "reduced"
        magnitude = "large" if abs(effect_size) > 0.8 else "moderate" if abs(effect_size) > 0.5 else "small"
        
        feature_display = feature_name.replace('_', ' ').replace('p3b', 'P3b').replace('hrv', 'HRV')
        
        return f"{magnitude} {direction} {feature_display} compared to healthy controls"
    
    def validate_biomarker(self, biomarker: ClinicalBiomarker, 
                          validation_patients: List[PatientProfile]) -> ClinicalBiomarker:
        """
        Validate a biomarker on independent patient data.
        
        Args:
            biomarker: Biomarker to validate
            validation_patients: Independent patient cohort for validation
            
        Returns:
            Updated biomarker with validation metrics
        """
        logger.info(f"Validating biomarker: {biomarker.name}")
        
        # Extract features for validation
        X, y = self._extract_features_for_validation(biomarker, validation_patients)
        
        if len(X) < 20:
            logger.warning("Insufficient validation data")
            return biomarker
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, stratify=y, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Test multiple classifiers
        best_classifier = None
        best_score = 0
        
        for name, classifier in self.classifiers.items():
            # Cross-validation
            cv_scores = cross_val_score(classifier, X_train_scaled, y_train, cv=5)
            mean_score = np.mean(cv_scores)
            
            if mean_score > best_score:
                best_score = mean_score
                best_classifier = name
        
        # Train best classifier and evaluate
        best_clf = self.classifiers[best_classifier]
        best_clf.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = best_clf.predict(X_test_scaled)
        y_prob = best_clf.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0
        
        try:
            auc = roc_auc_score(y_test, y_prob)
        except ValueError:
            auc = 0.5
        
        # Update biomarker
        biomarker.sensitivity = sensitivity
        biomarker.specificity = specificity
        biomarker.positive_predictive_value = ppv
        biomarker.negative_predictive_value = npv
        biomarker.auc_score = auc
        
        # Calculate clinical validity
        biomarker.clinical_validity = (sensitivity + specificity) / 2
        biomarker.clinical_utility = auc * 0.8 + (sensitivity + specificity) / 2 * 0.2
        biomarker.implementation_feasibility = min(1.0, len(biomarker.features) / 5)
        
        logger.info(f"Validation completed: AUC={auc:.3f}, Sensitivity={sensitivity:.3f}, Specificity={specificity:.3f}")
        
        return biomarker
    
    def _extract_features_for_validation(self, biomarker: ClinicalBiomarker, 
                                       patients: List[PatientProfile]) -> Tuple[np.ndarray, np.ndarray]:
        """Extract features for biomarker validation."""
        features = []
        labels = []
        
        for patient in patients:
            patient_features = []
            
            for feature in biomarker.features:
                value = getattr(patient, feature.name, None)
                if value is not None:
                    patient_features.append(value)
                else:
                    # Skip patient if missing critical feature
                    patient_features = None
                    break
            
            if patient_features is not None:
                features.append(patient_features)
                # Binary label: 1 for target condition, 0 for control
                label = 1 if patient.clinical_condition in biomarker.target_conditions else 0
                labels.append(label)
        
        return np.array(features), np.array(labels)
    
    def classify_patients(self, patients: List[PatientProfile], 
                         biomarker: ClinicalBiomarker) -> Dict[str, Dict[str, Any]]:
        """
        Classify patients using a specific biomarker.
        
        Args:
            patients: Patients to classify
            biomarker: Biomarker to use for classification
            
        Returns:
            Dictionary mapping patient IDs to classification results
        """
        logger.info(f"Classifying {len(patients)} patients using {biomarker.name}")
        
        # Extract features
        X, patient_ids = self._extract_features_for_classification(biomarker, patients)
        
        if len(X) == 0:
            logger.warning("No valid features for classification")
            return {}
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Use best classifier from validation
        classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Train on known cases (would use training data in production)
        # For now, use unsupervised approach
        predictions = classifier.fit(X_scaled).predict(X_scaled)
        probabilities = classifier.predict_proba(X_scaled)[:, 1]
        
        results = {}
        for i, patient_id in enumerate(patient_ids):
            results[patient_id] = {
                'predicted_condition': biomarker.target_conditions[0].value if predictions[i] == 1 else 'healthy_control',
                'probability': float(probabilities[i]),
                'confidence': float(max(probabilities[i], 1 - probabilities[i])),
                'biomarker_score': float(np.mean(X[i])),
                'features_used': [f.name for f in biomarker.features]
            }
        
        return results
    
    def _extract_features_for_classification(self, biomarker: ClinicalBiomarker, 
                                           patients: List[PatientProfile]) -> Tuple[np.ndarray, List[str]]:
        """Extract features for patient classification."""
        features = []
        valid_patient_ids = []
        
        for patient in patients:
            patient_features = []
            
            for biomarker_feature in biomarker.features:
                value = getattr(patient, biomarker_feature.name, None)
                if value is not None:
                    patient_features.append(value)
                else:
                    # Use imputation for missing values
                    patient_features.append(0.0)
            
            features.append(patient_features)
            valid_patient_ids.append(patient.patient_id)
        
        return np.array(features), valid_patient_ids
    
    def generate_biomarker_report(self, biomarkers: List[ClinicalBiomarker]) -> str:
        """
        Generate comprehensive biomarker analysis report.
        
        Args:
            biomarkers: List of biomarkers to include in report
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("Clinical Biomarker Analysis Report")
        report.append("=" * 50)
        report.append("")
        
        # Summary
        report.append("## SUMMARY")
        report.append(f"Total biomarkers analyzed: {len(biomarkers)}")
        
        # Categorize by performance
        high_performance = [b for b in biomarkers if b.auc_score >= 0.8]
        moderate_performance = [b for b in biomarkers if 0.7 <= b.auc_score < 0.8]
        low_performance = [b for b in biomarkers if b.auc_score < 0.7]
        
        report.append(f"High performance (AUC ≥ 0.8): {len(high_performance)}")
        report.append(f"Moderate performance (0.7 ≤ AUC < 0.8): {len(moderate_performance)}")
        report.append(f"Low performance (AUC < 0.7): {len(low_performance)}")
        report.append("")
        
        # Detailed biomarker information
        for biomarker in biomarkers:
            report.append(f"## {biomarker.name}")
            report.append(f"Type: {biomarker.biomarker_type.value}")
            report.append(f"Category: {biomarker.category.value}")
            report.append(f"Target conditions: {', '.join([c.value for c in biomarker.target_conditions])}")
            report.append(f"Description: {biomarker.description}")
            report.append(f"Evidence level: {biomarker.evidence_level}")
            report.append("")
            
            # Performance metrics
            report.append("### Performance Metrics")
            report.append(f"AUC Score: {biomarker.auc_score:.3f}")
            report.append(f"Sensitivity: {biomarker.sensitivity:.3f}")
            report.append(f"Specificity: {biomarker.specificity:.3f}")
            report.append(f"Positive Predictive Value: {biomarker.positive_predictive_value:.3f}")
            report.append(f"Negative Predictive Value: {biomarker.negative_predictive_value:.3f}")
            report.append("")
            
            # Clinical utility
            report.append("### Clinical Utility")
            report.append(f"Clinical Validity: {biomarker.clinical_validity:.3f}")
            report.append(f"Clinical Utility: {biomarker.clinical_utility:.3f}")
            report.append(f"Implementation Feasibility: {biomarker.implementation_feasibility:.3f}")
            report.append("")
            
            # Features
            if biomarker.features:
                report.append("### Biomarker Features")
                for feature in biomarker.features:
                    report.append(f"- {feature.name}: {feature.interpretation}")
                    report.append(f"  Effect size: {feature.effect_size:.3f} (p={feature.p_value:.3f})")
                    report.append(f"  Clinical significance: {feature.clinical_significance:.3f}")
                report.append("")
            
            report.append("---")
            report.append("")
        
        return "\n".join(report)


# Factory function for easy instantiation
def create_biomarker_analyzer(significance_threshold: float = 0.05) -> BiomarkerAnalyzer:
    """
    Create a biomarker analyzer with default settings.
    
    Args:
        significance_threshold: Statistical significance threshold
        
    Returns:
        Configured BiomarkerAnalyzer instance
    """
    return BiomarkerAnalyzer(significance_threshold=significance_threshold)
