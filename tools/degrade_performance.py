import docker
import random
import time
import argparse

class ContainerDegrader:
    def __init__(self, container_name):
        self.client = docker.from_env()
        self.container_name = container_name
        
    def cpu_stress(self, cpu_load=80, duration=60):
        """Simulate CPU stress"""
        container = self.client.containers.get(self.container_name)
        # Calculate CPU cores based on load
        cores = max(1, int((cpu_load * container.attrs['HostConfig']['NanoCpus']) / (100 * 1e9)))
        container.exec_run(f"stress-ng --cpu {cores} --timeout {duration}s", detach=True)
        
    def memory_stress(self, memory_mb=100, duration=60):
        """Simulate memory pressure"""
        container = self.client.containers.get(self.container_name)
        container.exec_run(f"stress-ng --vm 1 --vm-bytes {memory_mb}M --timeout {duration}s", detach=True)
        
    def network_latency(self, delay_ms=100):
        """Add network latency"""
        container = self.client.containers.get(self.container_name)
        container.exec_run(f"tc qdisc add dev eth0 root netem delay {delay_ms}ms")
        
    def random_degradation(self, duration=300):
        """Apply random degradation patterns"""
        while True:
            choice = random.choice(['cpu', 'memory'])
            if choice == 'cpu':
                self.cpu_stress(cpu_load=random.randint(70, 90), duration=30)
            else:
                self.memory_stress(memory_mb=random.randint(50, 200), duration=30)
            time.sleep(duration)

def main():
    parser = argparse.ArgumentParser(description='Container Performance Degradation Tool')
    parser.add_argument('--container', default='webapp', help='Container name')
    parser.add_argument('--mode', choices=['cpu', 'memory', 'network', 'random'], 
                      default='random', help='Degradation mode')
    parser.add_argument('--duration', type=int, default=300, 
                      help='Duration in seconds')
    
    args = parser.parse_args()
    
    degrader = ContainerDegrader(args.container)
    
    if args.mode == 'cpu':
        degrader.cpu_stress(duration=args.duration)
    elif args.mode == 'memory':
        degrader.memory_stress(duration=args.duration)
    elif args.mode == 'network':
        degrader.network_latency()
    else:
        degrader.random_degradation(duration=args.duration)

if __name__ == "__main__":
    main()