"""
Optical Fiber Channel Model for QKD

This module models realistic channel conditions including:
- Distance-dependent transmittance
- Background noise (dark counts)
- Detector inefficiency
- Distance-based attenuation
"""

import numpy as np
from typing import Dict, Tuple


class FiberChannel:
    """
    Optical fiber channel model for realistic QKD simulation.
    
    Models:
    - Attenuation: η(L) = η0 × 10^(-α·L/10)
    - Dark counts: Poisson background noise
    - Detector inefficiency
    """
    
    def __init__(
        self,
        distance_km: float = 50.0,
        fiber_loss_db_per_km: float = 0.2,
        detector_efficiency: float = 0.5,
        dark_count_rate: float = 1e-6,
        detector_dead_time: float = 0.0
    ):
        """
        Initialize fiber channel model.
        
        Args:
            distance_km: Fiber distance in kilometers
            fiber_loss_db_per_km: Attenuation coefficient (typical: 0.2 dB/km @ 1550nm)
            detector_efficiency: Detector quantum efficiency (0-1)
            dark_count_rate: Dark count probability per gate
            detector_dead_time: Detector dead time (not implemented yet)
        """
        self.distance_km = distance_km
        self.fiber_loss_db_per_km = fiber_loss_db_per_km
        self.detector_efficiency = detector_efficiency
        self.dark_count_rate = dark_count_rate
        self.detector_dead_time = detector_dead_time
        
        # Compute channel transmittance
        self.transmittance = self._compute_transmittance()
    
    def _compute_transmittance(self) -> float:
        """
        Compute channel transmittance based on distance.
        
        Formula: η(L) = 10^(-α·L/10)
        
        Returns:
            Channel transmittance (0-1)
        """
        total_loss_db = self.fiber_loss_db_per_km * self.distance_km
        transmittance = 10 ** (-total_loss_db / 10)
        return transmittance
    
    def apply_channel_loss(self, n_photons: int) -> int:
        """
        Apply channel loss to photon number.
        
        Each photon has probability η of surviving transmission.
        
        Args:
            n_photons: Number of photons entering the channel
        
        Returns:
            Number of photons surviving transmission
        """
        if n_photons == 0:
            return 0
        
        # Each photon survives with probability = transmittance
        surviving_photons = np.random.binomial(n_photons, self.transmittance)
        return surviving_photons
    
    def detect_photons(self, n_photons: int) -> Tuple[bool, bool]:
        """
        Model photon detection with detector inefficiency and dark counts.
        
        Args:
            n_photons: Number of photons arriving at detector
        
        Returns:
            Tuple of (detected, is_dark_count)
        """
        # Dark count event
        dark_count = np.random.random() < self.dark_count_rate
        
        if n_photons == 0:
            # Only dark counts can trigger detection
            return dark_count, dark_count
        
        # Detection probability: 1 - (1 - η_det)^n
        detection_prob = 1 - (1 - self.detector_efficiency) ** n_photons
        photon_detected = np.random.random() < detection_prob
        
        # Total detection: photon OR dark count
        detected = photon_detected or dark_count
        
        return detected, dark_count
    
    def get_parameters(self) -> Dict:
        """Get channel parameters."""
        return {
            'distance_km': self.distance_km,
            'fiber_loss_db_per_km': self.fiber_loss_db_per_km,
            'total_loss_db': self.fiber_loss_db_per_km * self.distance_km,
            'transmittance': self.transmittance,
            'detector_efficiency': self.detector_efficiency,
            'dark_count_rate': self.dark_count_rate,
            'effective_efficiency': self.transmittance * self.detector_efficiency
        }
    
    @staticmethod
    def distance_to_transmittance(distance_km: float, loss_db_per_km: float = 0.2) -> float:
        """
        Convert distance to transmittance.
        
        Args:
            distance_km: Distance in km
            loss_db_per_km: Fiber loss coefficient
        
        Returns:
            Transmittance
        """
        return 10 ** (-loss_db_per_km * distance_km / 10)
    
    @staticmethod
    def transmittance_to_distance(transmittance: float, loss_db_per_km: float = 0.2) -> float:
        """
        Convert transmittance to approximate distance.
        
        Args:
            transmittance: Channel transmittance
            loss_db_per_km: Fiber loss coefficient
        
        Returns:
            Approximate distance in km
        """
        if transmittance <= 0 or transmittance > 1:
            return 0.0
        loss_db = -10 * np.log10(transmittance)
        return loss_db / loss_db_per_km


def compute_key_rate_with_channel(
    qber: float,
    detections: int,
    sent_pulses: int,
    mu: float,
    f: float,
    channel: FiberChannel
) -> Dict:
    """
    Compute key rate accounting for channel parameters.
    
    Args:
        qber: Quantum bit error rate
        detections: Number of detections
        sent_pulses: Total pulses sent
        mu: Mean photon number
        f: Error correction efficiency
        channel: FiberChannel object
    
    Returns:
        Dictionary with key rate and channel info
    """
    from .key_rate_calculator import compute_secret_key_rate
    
    # Compute gain (accounting for channel)
    if sent_pulses > 0:
        Q_mu = detections / sent_pulses
    else:
        Q_mu = 0.0
    
    # Compute key rate
    key_rate = compute_secret_key_rate(
        qber=qber,
        detections=detections,
        sent_pulses=sent_pulses,
        mu=mu,
        f=f
    )
    
    # Channel parameters
    channel_params = channel.get_parameters()
    
    return {
        'key_rate': key_rate,
        'Q_mu': Q_mu,
        'distance_km': channel_params['distance_km'],
        'transmittance': channel_params['transmittance'],
        'effective_efficiency': channel_params['effective_efficiency'],
        'qber': qber
    }