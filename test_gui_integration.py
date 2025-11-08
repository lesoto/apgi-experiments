"""
Test script to verify GUI integration with falsification test controllers.
"""

import sys
import traceback

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from ipi_falsification_gui import IPIFalsificationGUI
        print("✓ GUI module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import GUI module: {e}")
        traceback.print_exc()
        return False
    
    try:
        from ipi_framework.falsification.primary_falsification_test import PrimaryFalsificationTest
        print("✓ PrimaryFalsificationTest imported successfully")
    except Exception as e:
        print(f"✗ Failed to import PrimaryFalsificationTest: {e}")
        traceback.print_exc()
        return False
    
    try:
        from ipi_framework.falsification.consciousness_without_ignition_test import ConsciousnessWithoutIgnitionTest
        print("✓ ConsciousnessWithoutIgnitionTest imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ConsciousnessWithoutIgnitionTest: {e}")
        traceback.print_exc()
        return False
    
    try:
        from ipi_framework.falsification.threshold_insensitivity_test import ThresholdInsensitivityTest
        print("✓ ThresholdInsensitivityTest imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ThresholdInsensitivityTest: {e}")
        traceback.print_exc()
        return False
    
    try:
        from ipi_framework.falsification.soma_bias_test import SomaBiasTest
        print("✓ SomaBiasTest imported successfully")
    except Exception as e:
        print(f"✗ Failed to import SomaBiasTest: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_controller_initialization():
    """Test that test controllers can be initialized."""
    print("\nTesting controller initialization...")
    
    try:
        from ipi_framework.falsification.primary_falsification_test import PrimaryFalsificationTest
        controller = PrimaryFalsificationTest()
        print("✓ PrimaryFalsificationTest initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize PrimaryFalsificationTest: {e}")
        traceback.print_exc()
        return False
    
    try:
        from ipi_framework.falsification.consciousness_without_ignition_test import ConsciousnessWithoutIgnitionTest
        controller = ConsciousnessWithoutIgnitionTest()
        print("✓ ConsciousnessWithoutIgnitionTest initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize ConsciousnessWithoutIgnitionTest: {e}")
        traceback.print_exc()
        return False
    
    try:
        from ipi_framework.falsification.threshold_insensitivity_test import ThresholdInsensitivityTest
        controller = ThresholdInsensitivityTest()
        print("✓ ThresholdInsensitivityTest initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize ThresholdInsensitivityTest: {e}")
        traceback.print_exc()
        return False
    
    try:
        from ipi_framework.falsification.soma_bias_test import SomaBiasTest
        controller = SomaBiasTest()
        print("✓ SomaBiasTest initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize SomaBiasTest: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_gui_creation():
    """Test that GUI can be created (without running mainloop)."""
    print("\nTesting GUI creation...")
    
    try:
        from ipi_falsification_gui import IPIFalsificationGUI
        
        # Create GUI instance but don't run mainloop
        app = IPIFalsificationGUI()
        print("✓ GUI created successfully")
        
        # Check that test panels exist
        expected_panels = ["Primary", "Consciousness Without Ignition", "Threshold Insensitivity", "Soma-Bias"]
        for panel_name in expected_panels:
            if panel_name in app.test_panels:
                print(f"✓ {panel_name} panel exists")
            else:
                print(f"✗ {panel_name} panel missing")
                return False
        
        # Destroy the GUI
        app.destroy()
        print("✓ GUI destroyed successfully")
        
        return True
    except Exception as e:
        print(f"✗ Failed to create GUI: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("IPI Falsification GUI Integration Tests")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
        print("\n✗ Import tests FAILED")
    else:
        print("\n✓ Import tests PASSED")
    
    # Test controller initialization
    if not test_controller_initialization():
        all_passed = False
        print("\n✗ Controller initialization tests FAILED")
    else:
        print("\n✓ Controller initialization tests PASSED")
    
    # Test GUI creation
    if not test_gui_creation():
        all_passed = False
        print("\n✗ GUI creation tests FAILED")
    else:
        print("\n✓ GUI creation tests PASSED")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return 0
    else:
        print("SOME TESTS FAILED ✗")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
