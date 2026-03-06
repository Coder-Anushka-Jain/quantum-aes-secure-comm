"""
Photon Number Splitting (PNS) Attack Implementation

This module simulates Eve's PNS attack on weak coherent pulse BB84.
Eve exploits multi-photon pulses by splitting and storing photons.

Attack Strategy:
- For n ≥ 2 photons: Eve splits one photon, stores it, sends rest to Bob
- For n = 1 photon: Eve cannot perform PNS (may block or forward)
- After basis reconciliation: Eve measures stored photons in correct basis
"""

import numpy as np
from typing import Dict, List, Tuple, Optional


class PNSAttack:
    """
    Photon Number Splitting Attack Simulator.
    
    Eve exploits the Poisson distribution of weak coherent pulses
    to gain information without introducing detectable errors.
    """
    
    def __init__(
        self,
        mu_signal: float = 0.5,
        mu_decoy: float = 0.1,
        mu_vacuum: float = 0.0,
        channel_loss: float = 0.1,
        detector_efficiency: float = 0.5,
        eve_storage_efficiency: float = 0.9
    ):
        """
        Initialize PNS attack parameters.
        
        Args:
            mu_signal: Mean photon number for signal pulses
            mu_decoy: Mean photon number for decoy pulses
            mu_vacuum: Mean photon number for vacuum pulses (should be 0)
            channel_loss: Channel transmission probability
            detector_efficiency: Bob's detector efficiency
            eve_storage_efficiency: Eve's quantum memory efficiency
        """
        self.mu_signal = mu_signal
        self.mu_decoy = mu_decoy
        self.mu_vacuum = mu_vacuum
        self.channel_loss = channel_loss
        self.detector_efficiency = detector_efficiency
        self.eve_storage_efficiency = eve_storage_efficiency
        
        # Attack statistics
        self.total_pulses = 0
        self.multi_photon_pulses = 0
        self.single_photon_pulses = 0
        self.vacuum_pulses = 0
        self.eve_stored_photons = 0
        self.eve_successful_measurements = 0
        
    def sample_photon_number(self, mu: float) -> int:
        """
        Sample photon number from Poisson distribution.
        
        P(n) = (μ^n * e^(-μ)) / n!
        
        Args:
            mu: Mean photon number
        
        Returns:
            Number of photons in the pulse
        """
        return np.random.poisson(mu)
    
    def pns_intercept(
        self,
        photon_number: int,
        alice_bit: int,
        alice_basis: int,
        pulse_type: str = 'signal'
    ) -> Tuple[int, bool, Optional[Dict]]:
        """
        Perform PNS attack on a single pulse.
        
        Args:
            photon_number: Number of photons in the pulse
            alice_bit: Alice's bit value
            alice_basis: Alice's basis choice
            pulse_type: 'signal', 'decoy', or 'vacuum'
        
        Returns:
            Tuple of:
                - photons_to_bob: Number of photons sent to Bob
                - eve_stored: Whether Eve stored a photon
                - stored_info: Information about stored photon (if any)
        """
        self.total_pulses += 1
        
        if photon_number == 0:
            # Vacuum pulse - nothing to intercept
            self.vacuum_pulses += 1
            return 0, False, None
        
        elif photon_number == 1:
            # Single photon - Eve cannot split (may choose to block or forward)
            self.single_photon_pulses += 1
            # In standard PNS, Eve forwards single-photon pulses
            return 1, False, None
        
        else:
            # Multi-photon pulse - Eve can perform PNS
            self.multi_photon_pulses += 1
            
            # Eve splits one photon and stores it
            photons_to_bob = photon_number - 1
            
            # Eve's storage success probability
            storage_success = np.random.random() < self.eve_storage_efficiency
            
            if storage_success:
                self.eve_stored_photons += 1
                stored_info = {
                    'bit': alice_bit,
                    'basis': alice_basis,
                    'pulse_type': pulse_type
                }
                return photons_to_bob, True, stored_info
            else:
                # Storage failed - photon lost
                return photons_to_bob, False, None
    
    def eve_measure_stored_photons(
        self,
        stored_photons: List[Dict],
        announced_bases: np.ndarray
    ) -> Dict:
        """
        Eve measures stored photons after basis reconciliation.
        
        Args:
            stored_photons: List of stored photon information
            announced_bases: Bases announced during reconciliation
        
        Returns:
            Dictionary with Eve's measurement results and information gain
        """
        eve_information = []
        
        for i, stored in enumerate(stored_photons):
            if stored is None:
                eve_information.append(None)
                continue
            
            # Eve now knows the correct basis
            correct_basis = stored['basis']
            alice_bit = stored['bit']
            
            # Eve measures in the correct basis
            # This gives perfect information for multi-photon pulses
            eve_bit = alice_bit
            
            self.eve_successful_measurements += 1
            
            eve_information.append({
                'bit': eve_bit,
                'basis': correct_basis,
                'pulse_type': stored['pulse_type']
            })
        
        return {
            'eve_bits': eve_information,
            'information_gain': self.eve_successful_measurements / max(self.total_pulses, 1),
            'multi_photon_fraction': self.multi_photon_pulses / max(self.total_pulses, 1)
        }
    
    def compute_detection_rates(
        self,
        photons_sent_to_bob: List[int],
        pulse_types: List[str]
    ) -> Dict:
        """
        Compute detection rates for different pulse types.
        
        This is crucial for decoy-state analysis to detect PNS attacks.
        
        Args:
            photons_sent_to_bob: List of photon numbers sent to Bob
            pulse_types: List of pulse types ('signal', 'decoy', 'vacuum')
        
        Returns:
            Detection rates and statistics
        """
        # Group by pulse type
        signal_photons = []
        decoy_photons = []
        vacuum_photons = []
        
        for n_photons, p_type in zip(photons_sent_to_bob, pulse_types):
            if p_type == 'signal':
                signal_photons.append(n_photons)
            elif p_type == 'decoy':
                decoy_photons.append(n_photons)
            elif p_type == 'vacuum':
                vacuum_photons.append(n_photons)
        
        # Compute detection rates
        # Detection probability: 1 - (1 - η)^n where η is detector efficiency
        signal_detections = sum([
            1 if np.random.random() < (1 - (1 - self.detector_efficiency)**n) else 0
            for n in signal_photons if n > 0
        ])
        
        decoy_detections = sum([
            1 if np.random.random() < (1 - (1 - self.detector_efficiency)**n) else 0
            for n in decoy_photons if n > 0
        ])
        
        vacuum_detections = sum([
            1 if np.random.random() < (1 - (1 - self.detector_efficiency)**n) else 0
            for n in vacuum_photons if n > 0
        ])
        
        return {
            'signal_detection_rate': signal_detections / max(len(signal_photons), 1),
            'decoy_detection_rate': decoy_detections / max(len(decoy_photons), 1),
            'vacuum_detection_rate': vacuum_detections / max(len(vacuum_photons), 1),
            'signal_pulses': len(signal_photons),
            'decoy_pulses': len(decoy_photons),
            'vacuum_pulses': len(vacuum_photons)
        }
    
    def get_attack_statistics(self) -> Dict:
        """
        Get comprehensive attack statistics.
        
        Returns:
            Dictionary with attack metrics
        """
        return {
            'total_pulses': self.total_pulses,
            'vacuum_pulses': self.vacuum_pulses,
            'single_photon_pulses': self.single_photon_pulses,
            'multi_photon_pulses': self.multi_photon_pulses,
            'eve_stored_photons': self.eve_stored_photons,
            'eve_successful_measurements': self.eve_successful_measurements,
            'multi_photon_fraction': self.multi_photon_pulses / max(self.total_pulses, 1),
            'storage_success_rate': self.eve_stored_photons / max(self.multi_photon_pulses, 1),
            'eve_information_gain': self.eve_successful_measurements / max(self.total_pulses, 1)
        }
    
    def reset_statistics(self):
        """Reset attack statistics."""
        self.total_pulses = 0
        self.multi_photon_pulses = 0
        self.single_photon_pulses = 0
        self.vacuum_pulses = 0
        self.eve_stored_photons = 0
        self.eve_successful_measurements = 0


def run_bb84_with_pns_attack(
    num_pulses: int,
    signal_prob: float = 0.7,
    decoy_prob: float = 0.2,
    vacuum_prob: float = 0.1,
    mu_signal: float = 0.5,
    mu_decoy: float = 0.1,
    channel_loss: float = 0.1,
    detector_efficiency: float = 0.5
) -> Dict:
    """
    Run BB84 protocol with PNS attack.
    
    Args:
        num_pulses: Total number of pulses to send
        signal_prob: Probability of sending signal pulse
        decoy_prob: Probability of sending decoy pulse
        vacuum_prob: Probability of sending vacuum pulse
        mu_signal: Mean photon number for signal
        mu_decoy: Mean photon number for decoy
        channel_loss: Channel transmission probability
        detector_efficiency: Bob's detector efficiency
    
    Returns:
        Dictionary with protocol results and PNS attack analysis
    """
    # Initialize PNS attack
    pns = PNSAttack(
        mu_signal=mu_signal,
        mu_decoy=mu_decoy,
        mu_vacuum=0.0,
        channel_loss=channel_loss,
        detector_efficiency=detector_efficiency
    )
    
    # Alice's preparation
    alice_bits = np.random.randint(0, 2, num_pulses)
    alice_bases = np.random.randint(0, 2, num_pulses)
    
    # Pulse type selection
    pulse_types = np.random.choice(
        ['signal', 'decoy', 'vacuum'],
        size=num_pulses,
        p=[signal_prob, decoy_prob, vacuum_prob]
    )
    
    # Photon number sampling
    photon_numbers = []
    for pulse_type in pulse_types:
        if pulse_type == 'signal':
            n = pns.sample_photon_number(mu_signal)
        elif pulse_type == 'decoy':
            n = pns.sample_photon_number(mu_decoy)
        else:  # vacuum
            n = 0
        photon_numbers.append(n)
    
    # Eve's PNS attack
    photons_to_bob = []
    eve_stored = []
    stored_photon_info = []
    
    for n, bit, basis, p_type in zip(photon_numbers, alice_bits, alice_bases, pulse_types):
        n_bob, stored, info = pns.pns_intercept(n, bit, basis, p_type)
        photons_to_bob.append(n_bob)
        eve_stored.append(stored)
        stored_photon_info.append(info)
    
    # Bob's measurement
    bob_bases = np.random.randint(0, 2, num_pulses)
    bob_detections = []
    bob_bits = []
    
    for n, alice_basis, bob_basis, alice_bit in zip(
        photons_to_bob, alice_bases, bob_bases, alice_bits
    ):
        # Detection probability
        detect_prob = 1 - (1 - detector_efficiency)**n if n > 0 else 0
        detected = np.random.random() < detect_prob
        
        if detected:
            # Bob measures
            if alice_basis == bob_basis:
                # Matching bases - deterministic
                bob_bit = alice_bit
            else:
                # Non-matching bases - random
                bob_bit = np.random.randint(0, 2)
            bob_bits.append(bob_bit)
        else:
            bob_bits.append(None)
        
        bob_detections.append(detected)
    
    # Basis reconciliation
    matching_bases = alice_bases == bob_bases
    detected_and_matching = [
        det and match for det, match in zip(bob_detections, matching_bases)
    ]
    
    # Extract sifted key
    alice_sifted = alice_bits[detected_and_matching]
    bob_sifted = np.array([
        bob_bits[i] for i in range(num_pulses) if detected_and_matching[i]
    ])
    
    # Compute QBER
    if len(alice_sifted) > 0:
        errors = np.sum(alice_sifted != bob_sifted)
        qber = errors / len(alice_sifted)
    else:
        qber = 0.0
    
    # Eve measures stored photons after basis announcement
    eve_results = pns.eve_measure_stored_photons(stored_photon_info, alice_bases)
    
    # Detection rate analysis
    detection_stats = pns.compute_detection_rates(photons_to_bob, pulse_types)
    
    # Get attack statistics
    attack_stats = pns.get_attack_statistics()
    
    return {
        'qber': qber,
        'alice_key': alice_sifted.tolist(),
        'bob_key': bob_sifted.tolist(),
        'key_length': len(alice_sifted),
        'total_pulses': num_pulses,
        'detection_stats': detection_stats,
        'eve_results': eve_results,
        'attack_stats': attack_stats,
        'photon_number_distribution': {
            'mean': np.mean(photon_numbers),
            'std': np.std(photon_numbers),
            'multi_photon_fraction': attack_stats['multi_photon_fraction']
        }
    }