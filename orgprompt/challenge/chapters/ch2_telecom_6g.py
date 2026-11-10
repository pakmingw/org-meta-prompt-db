"""Chapter 2: 6G Sub-Terahertz Physical Layer & O-RAN Edge Network Architecture."""

from typing import Any, Dict, Optional


def render_chapter_2(context: Optional[Dict[str, Any]] = None) -> str:
    """Renders Chapter 2 of the Master Grand Challenge Solution Dossier (~700 words)."""
    return """# Chapter 2: 6G Sub-Terahertz Physical Layer & O-RAN Edge Network Architecture

## 2.1 Spectrum Allocation & 140 GHz D-Band Link Budget Calculations

To achieve deterministic sub-millisecond physical layer transport for sovereign financial telemetry and consensus state exchange, the network architecture leverages the sub-terahertz radio spectrum, specifically the upper D-Band operating between 130 GHz and 175 GHz. The primary operational channel is centered at $f_c = 140.0\\text{ GHz}$ with an aggregated contiguous RF bandwidth of $B = 2.0\\text{ GHz}$. At this frequency, molecular atmospheric absorption, dominated by the $2_0 - 3_{-2}$ rotational water vapor resonance line at 183 GHz, imposes an attenuation of approximately $\\gamma_{\\text{atm}} = 0.4\\text{ dB/km}$ in dry air, surging to $\\gamma_{\\text{rain}} = 12.5\\text{ dB/km}$ during severe precipitation events ($R = 50\\text{ mm/hr}$).

The free-space path loss (FSPL) governed by the Friis transmission formula across a link distance of $d = 250\\text{ meters}$ between adjacent sovereign edge datacenters is given by:

$$\\text{FSPL}(d, f) = 20 \\log_{10}(d) + 20 \\log_{10}(f) + 20 \\log_{10}\\left(\\frac{4\\pi}{c}\\right) = 20 \\log_{10}(250) + 20 \\log_{10}(1.4 \\times 10^{11}) - 147.55 = 123.32\\text{ dB}$$

To ensure an operating link margin exceeding $8.5\\text{ dB}$ under torrential downpours, the RF front-end integrates high-efficiency Gallium Nitride on Silicon-Carbide (GaN-on-SiC) power amplifiers delivering $+30.0\\text{ dBm}$ (1.0 Watt) of saturated transmit power coupled with massive phased arrays.

| Parameter | Value | Unit | Specification & Operational Notes |
|---|---|---|---|
| Carrier Frequency ($f_c$) | 140.0 | GHz | 3GPP Release 19 Sub-THz D-Band Allocation |
| Channel Bandwidth ($B$) | 2.0 | GHz | Contiguous single-carrier / CP-OFDM wideband |
| Transmit Output Power ($P_{tx}$) | +30.0 | dBm | GaN-on-SiC high-electron-mobility transistor (HEMT) |
| Tx Antenna Gain ($G_{tx}$) | +42.0 | dBi | 1024-element ($32 \\times 32$) dielectric resonator phased array |
| Effective Isotropic Radiated Power (EIRP) | +72.0 | dBm | Bore-sight peak radiated power |
| Path Distance ($d$) | 250.0 | m | Inter-datacenter sovereign edge baseline link |
| Free Space Path Loss (FSPL) | -123.32 | dB | Calculated Friis path loss at 140 GHz |
| Atmospheric & Rain Attenuation ($A_{\\text{env}}$) | -3.18 | dB | Worst-case tropical rain fade ($50\\text{ mm/hr}$ over 250m) |
| Rx Antenna Gain ($G_{rx}$) | +42.0 | dBi | Symmetric 1024-element planar receiving array |
| Received Signal Power ($P_{rx}$) | -12.50 | dBm | Total intercepted carrier power at LNA input |
| Receiver Noise Figure ($NF$) | 7.0 | dB | Low-noise amplifier using Indium Phosphide (InP) HEMT |
| Thermal Noise Floor ($N_0 B$) | -80.98 | dBm | $k_B T B$ with $T = 290\\text{ K}$, $B = 2.0\\text{ GHz}$ |
| Effective Signal-to-Noise Ratio (SNR) | +61.48 | dB | Unprecedented link margin supporting 1024-QAM |

## 2.2 Massive MIMO Phased Array Topologies & Beam Management

Overcoming the severe propagation loss of sub-terahertz frequencies necessitates Extreme Massive MIMO (E-MIMO). The RF front-end features a 1024-element active planar antenna array structured in a $32 \\times 32$ grid with inter-element spacing of $\\lambda / 2 = 1.07\\text{ mm}$. The array architecture adopts a hybrid analog-digital beamforming topology, wherein 64 independent digital transceivers interface with sub-arrays of 16 analog phase-shifted elements via low-loss Silicon-Germanium (SiGe) BiCMOS beamforming integrated circuits.

Beam management utilizes fast hierarchical codebook sweeping. Initial coarse beam acquisition requires four 62.5-microsecond slots ($250\\,\\mu\\text{s}$), after which an active Kalman-filter tracking loop monitors channel state information (CSI) with a tracking latency of $\\tau_{\\text{track}} \\le 8.5\\,\\mu\\text{s}$. This sub-10-microsecond beam realignment ensures that mechanical building sway, thermal expansion, or atmospheric turbulence never degrades the received SNR below the modulation threshold.

## 2.3 O-RAN Split-7.2x Deterministic MAC Scheduling & eCPRI Transport

The radio access network strictly conforms to the Open RAN (O-RAN) Alliance standard utilizing the Split-7.2x lower-layer split. In this partitioning, the Radio Unit (O-RU) executes Fast Fourier Transforms (FFTs), cyclic prefix removal, and digital beamforming, while the Distributed Unit (O-DU) executes deterministic MAC scheduling, rate matching, and Hybrid ARQ (HARQ) management.

The front-haul link between O-RU and O-DU utilizes dual 100 Gbps Ethernet interfaces running the eCPRI protocol over IEEE 802.1CM Time-Sensitive Networking (TSN). Time synchronization is enforced via the IEEE 1588 PTP v2.1 Telecom Profile (ITU-T G.8275.1), achieving inter-node clock synchronization accuracy within $\\pm 12\\text{ nanoseconds}$, eliminating packet jitter and enabling strict priority preemption for ultra-reliable low-latency financial telemetry packets.

## 2.4 URLLC Physical Numerology & Microsecond Frame Structure

The physical layer adopts CP-OFDM with an extended 3GPP numerology parameter $\\mu = 4$. Under this configuration, the subcarrier spacing (SCS) expands to:

$$\\Delta f = 15 \\times 2^4 = 240\\text{ kHz}$$

A standard radio slot consisting of 14 OFDM symbols spans exactly $62.5\\,\\mu\\text{s}$. To guarantee sub-100-microsecond transmission latencies, the O-DU implements mini-slot puncturing: critical BFT consensus quorum attestations and RTGS escrow commit packets are formatted into 2-symbol mini-slots ($8.92\\,\\mu\\text{s}$ duration), which preemptively puncture standard background traffic without waiting for slot boundaries. Hardware-accelerated Low-Density Parity-Check (LDPC) decoder coprocessors achieve a Block Error Rate (BLER) of $\\text{BLER} < 10^{-6}$ on the initial transmission, completely obviating latency-inducing retransmission timeouts.
"""
