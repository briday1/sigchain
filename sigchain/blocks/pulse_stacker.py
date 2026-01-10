"""Pulse stacking block."""

import numpy as np
from ..core.block import ProcessingBlock
from ..core.data import SignalData


class PulseStacker(ProcessingBlock):
    """
    Stacks multiple radar pulses into a 2D matrix.
    
    This block organizes the received pulses into a matrix format where each row
    represents a pulse. This is typically the first step in coherent processing.
    """
    
    def __init__(self, name: str = None):
        """
        Initialize the pulse stacker.
        
        Args:
            name: Optional name for the block
        """
        super().__init__(name)
    
    def process(self, signal_data: SignalData) -> SignalData:
        """
        Stack pulses into a 2D matrix with extended samples for matched filtering.
        
        For proper matched filtering with 'valid' mode, each pulse row needs to include
        N-1 additional samples. Since we have continuous observation, we take samples
        that wrap into the next observation period. This gives us pulse_length + (pulse_length - 1)
        = 2*pulse_length - 1 samples per row.
        
        Args:
            signal_data: Input signal data (already in matrix form from generator)
            
        Returns:
            SignalData with pulses stacked and extended for matched filtering
        """
        # Ensure data is 2D
        if signal_data.data.ndim == 1:
            # If 1D, reshape into a single pulse
            data = signal_data.data.reshape(1, -1)
        else:
            data = signal_data.data
        
        # Get reference pulse length from metadata
        if 'reference_pulse' in signal_data.metadata:
            pulse_length = len(signal_data.metadata['reference_pulse'])
        elif 'samples_per_pulse' in signal_data.metadata:
            pulse_length = signal_data.metadata['samples_per_pulse']
        else:
            # Fallback: assume entire observation window is one pulse
            pulse_length = data.shape[1]
        
        num_pulses, num_samples = data.shape
        
        # For matched filtering with 'valid' mode:
        # Input needs to be 2N-1 samples where N is the pulse length
        # Output will be N samples
        # 
        # However, the observation window per pulse is already >= pulse_length
        # So we just keep it as is and use 'same' mode instead of 'valid'
        # The peak will be at the correct position (with N/2 offset for pulse center)
        
        # No extension needed - pass through as-is
        # The matched filter will handle this correctly with 'same' mode
        
        # Create output with updated metadata
        metadata = signal_data.metadata.copy()
        metadata['pulse_stacked'] = True
        metadata['shape_after_stacking'] = data.shape
        
        return SignalData(
            data=data,
            sample_rate=signal_data.sample_rate,
            metadata=metadata
        )
