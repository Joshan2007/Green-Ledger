"""
GreenLedger - Feature Mapping & Preprocessing Layer
Maps raw Windows system telemetry to the ML training & inference feature schema.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

# Core features selected for the regression model
BASE_MODEL_FEATURES = [
    "cpu_utilization",
    "memory_usage",
    "disk_io",
    "network_latency",
    "process_count",
    "thread_count",
    "context_switches",
    "temperature",
    "uptime"
]

ENGINEERED_FEATURES = [
    "cpu_memory_ratio",
    "process_thread_ratio",
    "resource_pressure",
    "cpu_temp_interaction"
]

ALL_MODEL_FEATURES = BASE_MODEL_FEATURES + ENGINEERED_FEATURES


def compute_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes derived interaction features proven to improve power regression stability.
    """
    df_engineered = df.copy()
    
    # 1. CPU to Memory ratio (identifies compute-heavy vs memory-bound workloads)
    df_engineered["cpu_memory_ratio"] = df_engineered["cpu_utilization"] / (df_engineered["memory_usage"] + 1e-5)
    
    # 2. Average threads per process
    df_engineered["process_thread_ratio"] = df_engineered["thread_count"] / (df_engineered["process_count"] + 1e-5)
    
    # 3. Normalized resource pressure score (0-100 scale)
    clamped_disk = np.clip(df_engineered["disk_io"], 0.0, 100.0)
    df_engineered["resource_pressure"] = (
        (df_engineered["cpu_utilization"] * 0.50) + 
        (df_engineered["memory_usage"] * 0.35) + 
        (clamped_disk * 0.15)
    )
    
    # 4. CPU x Temperature thermal interaction
    df_engineered["cpu_temp_interaction"] = (df_engineered["cpu_utilization"] * df_engineered["temperature"]) / 100.0
    
    return df_engineered


def map_telemetry_to_features(telemetry: Dict[str, Any]) -> Tuple[Dict[str, float], List[str]]:
    """
    Takes a raw telemetry dictionary from the Windows collector (or demo generator)
    and maps it to the strictly ordered ML feature schema.
    Returns:
        (mapped_features_dict, list_of_warnings)
    """
    warnings = []
    mapped = {}
    
    # cpu_utilization
    cpu = telemetry.get("cpu_utilization")
    if cpu is None:
        cpu = 15.0
        warnings.append("cpu_utilization missing; defaulted to 15.0%")
    mapped["cpu_utilization"] = float(np.clip(cpu, 0.0, 100.0))
    
    # memory_usage
    mem = telemetry.get("memory_usage")
    if mem is None:
        mem = 50.0
        warnings.append("memory_usage missing; defaulted to 50.0%")
    mapped["memory_usage"] = float(np.clip(mem, 0.0, 100.0))
    
    # disk_io
    disk = telemetry.get("disk_io")
    if disk is None:
        disk = 5.0
        warnings.append("disk_io missing; defaulted to 5.0 MB/s")
    mapped["disk_io"] = float(max(0.0, disk))
    
    # network_latency
    latency = telemetry.get("network_latency")
    if latency is None:
        latency = 25.0
        warnings.append("network_latency missing; defaulted to 25.0 ms")
    mapped["network_latency"] = float(max(0.5, latency))
    
    # process_count
    proc = telemetry.get("process_count")
    if proc is None:
        proc = 150
        warnings.append("process_count missing; defaulted to 150")
    mapped["process_count"] = float(max(1, proc))
    
    # thread_count
    threads = telemetry.get("thread_count")
    if threads is None:
        threads = mapped["process_count"] * 14
        warnings.append("thread_count missing; estimated from process_count * 14")
    mapped["thread_count"] = float(max(1, threads))
    
    # context_switches
    ctx = telemetry.get("context_switches")
    if ctx is None:
        ctx = mapped["cpu_utilization"] * 150 + mapped["process_count"] * 25
        warnings.append("context_switches missing; estimated from CPU and processes")
    mapped["context_switches"] = float(max(10, ctx))
    
    # temperature
    temp = telemetry.get("temperature")
    if temp is None:
        # Transparently estimate thermal response based on CPU baseline
        temp = 42.0 + (mapped["cpu_utilization"] * 0.35)
        warnings.append("hardware temperature sensor unavailable; estimated thermal state from CPU load")
    mapped["temperature"] = float(np.clip(temp, 25.0, 105.0))
    
    # uptime
    uptime = telemetry.get("uptime")
    if uptime is None:
        uptime = 4.0
        warnings.append("uptime missing; defaulted to 4.0 hours")
    mapped["uptime"] = float(max(0.01, uptime))
    
    # Compute derived interaction features
    mapped["cpu_memory_ratio"] = mapped["cpu_utilization"] / (mapped["memory_usage"] + 1e-5)
    mapped["process_thread_ratio"] = mapped["thread_count"] / (mapped["process_count"] + 1e-5)
    clamped_disk = min(100.0, mapped["disk_io"])
    mapped["resource_pressure"] = (
        (mapped["cpu_utilization"] * 0.50) + 
        (mapped["memory_usage"] * 0.35) + 
        (clamped_disk * 0.15)
    )
    mapped["cpu_temp_interaction"] = (mapped["cpu_utilization"] * mapped["temperature"]) / 100.0
    
    return mapped, warnings
