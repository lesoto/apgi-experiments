"""
Neural signature simulators for APGI Framework falsification testing.

This package provides simulators for various neural signatures associated with
consciousness, including P3b ERP, gamma-band synchrony, BOLD activation, and
Perturbational Complexity Index (PCI).
"""

from .p3b_simulator import P3bSimulator, P3bSignature
from .gamma_simulator import GammaSimulator, GammaSignature, GammaResult, BrainRegion as GammaBrainRegion
from .bold_simulator import BOLDSimulator, BOLDSignature, BOLDResult, BrainRegion as BOLDBrainRegion
from .pci_calculator import PCICalculator, PCISignature
from .signature_validator import (
    SignatureValidator, 
    CombinedSignature, 
    ConsciousnessLevel, 
    SignatureType
)

__all__ = [
    # P3b ERP simulator
    'P3bSimulator',
    'P3bSignature',
    
    # Gamma-band synchrony simulator
    'GammaSimulator',
    'GammaSignature',
    'GammaResult',
    'GammaBrainRegion',
    
    # BOLD activation simulator
    'BOLDSimulator',
    'BOLDSignature',
    'BOLDResult',
    'BOLDBrainRegion',
    
    # PCI calculator
    'PCICalculator',
    'PCISignature',
    
    # Signature validation and combination
    'SignatureValidator',
    'CombinedSignature',
    'ConsciousnessLevel',
    'SignatureType'
]