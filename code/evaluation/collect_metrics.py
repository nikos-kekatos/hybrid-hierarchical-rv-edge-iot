#!/usr/bin/env python3
"""
Metrics Collection Script
Parses logs from hierarchical RV system and extracts metrics for paper evaluation
"""

import json
import sys
from collections import defaultdict, Counter


class MetricsCollector:
    """Collect metrics from log files"""

    def __init__(self):
        self.events = []
        self.alerts = []
        self.incidents = []

        self.stats = {
            'total_events': 0,
            'total_alerts': 0,
            'total_incidents': 0,
            'alerts_by_type': Counter(),
            'incidents_by_type': Counter(),
            'incidents_by_property': Counter(),
            'devices_seen': set(),
            'attack_devices': set(),
        }

        self.latencies = {
            'alert_to_incident': [],
        }

    def parse_events_log(self, filepath):
        """Parse events.log"""
        print(f"Parsing events from: {filepath}")
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    if line.strip() and line.strip().startswith('{'):
                        try:
                            event = json.loads(line)
                            self.events.append(event)
                            self.stats['total_events'] += 1
                            self.stats['devices_seen'].add(event.get('actor', 'unknown'))
                        except: pass
        except FileNotFoundError:
            print(f"  WARNING: {filepath} not found")
        print(f"  Collected {len(self.events)} events")

    def parse_alerts_log(self, filepath):
        """Parse alerts.log"""
        print(f"Parsing alerts from: {filepath}")
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    if line.strip() and line.strip().startswith('{'):
                        try:
                            alert = json.loads(line)
                            self.alerts.append(alert)
                            self.stats['total_alerts'] += 1
                            alert_type = alert.get('type', 'unknown')
                            self.stats['alerts_by_type'][alert_type] += 1
                            if alert_type != 'safe_tx':
                                self.stats['attack_devices'].add(alert.get('device', 'unknown'))
                        except: pass
        except FileNotFoundError:
            print(f"  WARNING: {filepath} not found")
        print(f"  Collected {len(self.alerts)} alerts")

    def parse_incidents_log(self, filepath):
        """Parse incidents.log"""
        print(f"Parsing incidents from: {filepath}")
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    if line.strip() and line.strip().startswith('{'):
                        try:
                            incident = json.loads(line)
                            self.incidents.append(incident)
                            self.stats['total_incidents'] += 1
                            self.stats['incidents_by_type'][incident.get('type', 'unknown')] += 1
                            self.stats['incidents_by_property'][incident.get('property', 'unknown')] += 1
                        except: pass
        except FileNotFoundError:
            print(f"  WARNING: {filepath} not found")
        print(f"  Collected {len(self.incidents)} incidents")

    def calculate_latencies(self):
        """Calculate detection latencies"""
        print("\nCalculating latencies...")
        self.alerts.sort(key=lambda x: x.get('timestamp', 0))
        self.incidents.sort(key=lambda x: x.get('timestamp', 0))

        for incident in self.incidents:
            incident_time = incident.get('timestamp', 0)
            incident_device = incident.get('device')
            relevant_alerts = [a for a in self.alerts
                             if a.get('device') == incident_device
                             and a.get('timestamp', 0) <= incident_time]
            if relevant_alerts:
                latest_alert = max(relevant_alerts, key=lambda x: x.get('timestamp', 0))
                latency = incident_time - latest_alert.get('timestamp', 0)
                self.latencies['alert_to_incident'].append(latency)

    def generate_summary(self):
        """Generate summary statistics"""
        from datetime import datetime
        return {
            'timestamp': datetime.now().isoformat(),
            'overview': {
                'total_events': self.stats['total_events'],
                'total_alerts': self.stats['total_alerts'],
                'total_incidents': self.stats['total_incidents'],
                'unique_devices': len(self.stats['devices_seen']),
                'attack_devices': len(self.stats['attack_devices']),
            },
            'alerts': {'by_type': dict(self.stats['alerts_by_type'])},
            'incidents': {
                'by_type': dict(self.stats['incidents_by_type']),
                'by_property': dict(self.stats['incidents_by_property']),
            },
            'latencies': {
                'alert_to_incident': {
                    'count': len(self.latencies['alert_to_incident']),
                    'mean': sum(self.latencies['alert_to_incident']) / len(self.latencies['alert_to_incident'])
                           if self.latencies['alert_to_incident'] else 0,
                    'min': min(self.latencies['alert_to_incident']) if self.latencies['alert_to_incident'] else 0,
                    'max': max(self.latencies['alert_to_incident']) if self.latencies['alert_to_incident'] else 0,
                }
            }
        }

    def print_summary(self):
        """Print summary"""
        print("\n" + "="*60)
        print("METRICS SUMMARY")
        print("="*60)
        print(f"\nEvents:    {self.stats['total_events']}")
        print(f"Alerts:    {self.stats['total_alerts']}")
        print(f"Incidents: {self.stats['total_incidents']}")
        print(f"Devices:   {len(self.stats['devices_seen'])} total, {len(self.stats['attack_devices'])} attacking")

        print("\nAlerts by type:")
        for alert_type, count in self.stats['alerts_by_type'].most_common():
            print(f"  {alert_type:20s}: {count:4d}")

        print("\nIncidents by property:")
        for prop, count in self.stats['incidents_by_property'].most_common():
            print(f"  {prop:10s}: {count:4d}")

        if self.latencies['alert_to_incident']:
            lat = self.latencies['alert_to_incident']
            print(f"\nLatency (alert → incident):")
            print(f"  Mean: {sum(lat)/len(lat):.2f}s")


def main():
    import argparse, os
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-dir', default='./shared_data')
    parser.add_argument('--output', default='./results/metrics.json')
    args = parser.parse_args()

    collector = MetricsCollector()
    collector.parse_events_log(f"{args.log_dir}/events.log")
    collector.parse_alerts_log(f"{args.log_dir}/alerts.log")
    collector.parse_incidents_log(f"{args.log_dir}/incidents.log")
    collector.calculate_latencies()

    summary = collector.generate_summary()
    collector.print_summary()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nMetrics saved to: {args.output}")


if __name__ == "__main__":
    main()
