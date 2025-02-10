# Random degradation
python degrade_performance.py --container webapp --mode random

# CPU stress
python degrade_performance.py --container webapp --mode cpu --duration 120

# Memory stress
python degrade_performance.py --container webapp --mode memory --duration 60

# Network latency
python degrade_performance.py --container webapp --mode network