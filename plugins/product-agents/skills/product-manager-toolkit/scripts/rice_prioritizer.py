#!/usr/bin/env python3
"""
RICE Prioritization Framework
Calculates RICE scores for feature prioritization

RICE = (Reach x Impact x Confidence) / Effort

--- Local customization (2026-07-20) ---
Effort is split into two independently-scored dimensions instead of one:

  - engineering_effort: coding/implementation work. This is delegated to
    Claude Code, not done by the founder personally, so it is weighted
    LIGHTLY in the final score (ENGINEERING_EFFORT_WEIGHT, default 0.5 —
    "about fifty percent of what you'd usually weigh it").
  - personal_effort: decisions, approvals, signups, anything that
    consumes the founder's own time/attention. This is the founder's
    genuinely scarce resource, so it stays at NORMAL/full weight
    (PERSONAL_EFFORT_WEIGHT, default 1.0 — same as classic RICE's Effort
    term).

This means a feature can score well despite being a large build (cheap:
Claude Code's time) while still scoring poorly if it requires a lot of
founder attention (expensive: the founder's time) — and vice versa. The
report output makes explicit which of the two is the "binding
constraint" on each feature's score, so a low rank can be correctly
read as "this needs too much of my personal time" rather than
mis-read as "this is too much engineering work" (or the reverse).
"""

import json
import csv
from typing import List, Dict, Tuple
import argparse

# How heavily each effort dimension counts against a feature's score.
# 1.0 = full/normal weight (classic RICE behavior). 0.5 = half weight.
ENGINEERING_EFFORT_WEIGHT = 0.5
PERSONAL_EFFORT_WEIGHT = 1.0


class RICECalculator:
    """Calculate RICE scores for feature prioritization"""

    def __init__(self):
        self.impact_map = {
            'massive': 3.0,
            'high': 2.0,
            'medium': 1.0,
            'low': 0.5,
            'minimal': 0.25
        }

        self.confidence_map = {
            'high': 100,
            'medium': 80,
            'low': 50
        }

        # Same xs..xl fibonacci-ish scale for both effort dimensions, but
        # they measure different things and different people's time:
        #   engineering_effort -> person-months of build work (Claude Code's time)
        #   personal_effort    -> hours of founder decisions/approvals/attention
        self.engineering_effort_map = {
            'xl': 13,
            'l': 8,
            'm': 5,
            's': 3,
            'xs': 1
        }

        self.personal_effort_map = {
            'xl': 13,
            'l': 8,
            'm': 5,
            's': 3,
            'xs': 1
        }

    def calculate_rice(self, reach: int, impact: str, confidence: str,
                        engineering_effort: str, personal_effort: str) -> Dict:
        """
        Calculate RICE score with the effort dimension split in two.

        Args:
            reach: Number of users/customers affected per quarter
            impact: massive/high/medium/low/minimal
            confidence: high/medium/low (percentage)
            engineering_effort: xl/l/m/s/xs (person-months of build work)
            personal_effort: xl/l/m/s/xs (hours of founder time: decisions,
                approvals, signups, review)

        Returns a dict with the final rice_score plus the raw component
        scores, so callers can explain *why* a score landed where it did.
        """
        impact_score = self.impact_map.get(impact.lower(), 1.0)
        confidence_score = self.confidence_map.get(confidence.lower(), 50) / 100
        eng_score = self.engineering_effort_map.get(engineering_effort.lower(), 5)
        personal_score = self.personal_effort_map.get(personal_effort.lower(), 5)

        if eng_score == 0 or personal_score == 0:
            return {'rice_score': 0, 'engineering_effort_score': eng_score,
                    'personal_effort_score': personal_score,
                    'engineering_divisor': 0, 'personal_divisor': 0,
                    'binding_constraint': 'n/a'}

        # Each dimension's contribution to the divisor is dampened by its
        # own weight. weight=1.0 behaves exactly like classic RICE's
        # Effort term; weight=0.5 makes that dimension count for roughly
        # half as much (sqrt-like dampening on that dimension only).
        engineering_divisor = eng_score ** ENGINEERING_EFFORT_WEIGHT
        personal_divisor = personal_score ** PERSONAL_EFFORT_WEIGHT
        combined_effort_divisor = engineering_divisor * personal_divisor

        rice_score = (reach * impact_score * confidence_score) / combined_effort_divisor

        # Which dimension is actually suppressing this feature's score
        # more? Compare each dimension's divisor contribution directly.
        if personal_divisor > engineering_divisor * 1.15:
            binding_constraint = 'personal_time'
        elif engineering_divisor > personal_divisor * 1.15:
            binding_constraint = 'build_time'
        else:
            binding_constraint = 'balanced'

        return {
            'rice_score': round(rice_score, 2),
            'engineering_effort_score': eng_score,
            'personal_effort_score': personal_score,
            'engineering_divisor': round(engineering_divisor, 2),
            'personal_divisor': round(personal_divisor, 2),
            'binding_constraint': binding_constraint
        }

    def prioritize_features(self, features: List[Dict]) -> List[Dict]:
        """
        Calculate RICE scores and rank features

        Args:
            features: List of feature dictionaries with RICE components
        """
        for feature in features:
            result = self.calculate_rice(
                feature.get('reach', 0),
                feature.get('impact', 'medium'),
                feature.get('confidence', 'medium'),
                feature.get('engineering_effort', 'm'),
                feature.get('personal_effort', 'm')
            )
            feature['rice_score'] = result['rice_score']
            feature['engineering_effort_score'] = result['engineering_effort_score']
            feature['personal_effort_score'] = result['personal_effort_score']
            feature['binding_constraint'] = result['binding_constraint']

        # Sort by RICE score descending
        return sorted(features, key=lambda x: x['rice_score'], reverse=True)

    def analyze_portfolio(self, features: List[Dict]) -> Dict:
        """
        Analyze the feature portfolio for balance and insights
        """
        if not features:
            return {}

        total_engineering_effort = sum(
            self.engineering_effort_map.get(f.get('engineering_effort', 'm').lower(), 5)
            for f in features
        )
        total_personal_effort = sum(
            self.personal_effort_map.get(f.get('personal_effort', 'm').lower(), 5)
            for f in features
        )

        total_reach = sum(f.get('reach', 0) for f in features)

        engineering_effort_distribution = {}
        personal_effort_distribution = {}
        impact_distribution = {}

        for feature in features:
            eng_effort = feature.get('engineering_effort', 'm').lower()
            personal_effort = feature.get('personal_effort', 'm').lower()
            impact = feature.get('impact', 'medium').lower()

            engineering_effort_distribution[eng_effort] = engineering_effort_distribution.get(eng_effort, 0) + 1
            personal_effort_distribution[personal_effort] = personal_effort_distribution.get(personal_effort, 0) + 1
            impact_distribution[impact] = impact_distribution.get(impact, 0) + 1

        # Quick wins: high impact, cheap on BOTH dimensions
        quick_wins = [
            f for f in features
            if f.get('impact', '').lower() in ['massive', 'high']
            and f.get('engineering_effort', '').lower() in ['xs', 's']
            and f.get('personal_effort', '').lower() in ['xs', 's']
        ]

        # Big bets: high impact, expensive on BOTH dimensions
        big_bets = [
            f for f in features
            if f.get('impact', '').lower() in ['massive', 'high']
            and f.get('engineering_effort', '').lower() in ['l', 'xl']
            and f.get('personal_effort', '').lower() in ['l', 'xl']
        ]

        # Founder-time-blocked: good idea, held back specifically by
        # personal effort rather than build effort. This is the set the
        # founder should look at differently from "hard to build."
        personal_time_blocked = [
            f for f in features
            if f.get('impact', '').lower() in ['massive', 'high']
            and f.get('binding_constraint') == 'personal_time'
        ]

        return {
            'total_features': len(features),
            'total_engineering_effort_months': total_engineering_effort,
            'total_personal_effort_hours': total_personal_effort,
            'total_reach': total_reach,
            'average_rice': round(sum(f['rice_score'] for f in features) / len(features), 2),
            'engineering_effort_distribution': engineering_effort_distribution,
            'personal_effort_distribution': personal_effort_distribution,
            'impact_distribution': impact_distribution,
            'quick_wins': len(quick_wins),
            'big_bets': len(big_bets),
            'quick_wins_list': quick_wins[:3],  # Top 3 quick wins
            'big_bets_list': big_bets[:3],  # Top 3 big bets
            'personal_time_blocked': len(personal_time_blocked),
            'personal_time_blocked_list': personal_time_blocked[:5]
        }

    def generate_roadmap(self, features: List[Dict], team_capacity: int = 10,
                          personal_capacity: int = 20) -> List[Dict]:
        """
        Generate a quarterly roadmap based on team capacity

        Args:
            features: Prioritized feature list
            team_capacity: Engineering person-months available per quarter
                (Claude Code's build capacity — usually generous)
            personal_capacity: Founder hours available per quarter for
                decisions/approvals/signups (usually the tighter constraint)
        """
        quarters = []
        current_quarter = {
            'quarter': 1,
            'features': [],
            'engineering_capacity_used': 0,
            'engineering_capacity_available': team_capacity,
            'personal_capacity_used': 0,
            'personal_capacity_available': personal_capacity
        }

        for feature in features:
            eng_effort = self.engineering_effort_map.get(feature.get('engineering_effort', 'm').lower(), 5)
            personal_effort = self.personal_effort_map.get(feature.get('personal_effort', 'm').lower(), 5)

            fits_engineering = current_quarter['engineering_capacity_used'] + eng_effort <= team_capacity
            fits_personal = current_quarter['personal_capacity_used'] + personal_effort <= personal_capacity

            if fits_engineering and fits_personal:
                current_quarter['features'].append(feature)
                current_quarter['engineering_capacity_used'] += eng_effort
                current_quarter['personal_capacity_used'] += personal_effort
            else:
                # Move to next quarter. Record which constraint filled up.
                current_quarter['engineering_capacity_available'] = team_capacity - current_quarter['engineering_capacity_used']
                current_quarter['personal_capacity_available'] = personal_capacity - current_quarter['personal_capacity_used']
                current_quarter['filled_by'] = (
                    'personal_time' if not fits_personal and fits_engineering
                    else 'build_time' if fits_personal and not fits_engineering
                    else 'both'
                )
                quarters.append(current_quarter)

                current_quarter = {
                    'quarter': len(quarters) + 1,
                    'features': [feature],
                    'engineering_capacity_used': eng_effort,
                    'engineering_capacity_available': team_capacity - eng_effort,
                    'personal_capacity_used': personal_effort,
                    'personal_capacity_available': personal_capacity - personal_effort
                }

        if current_quarter['features']:
            current_quarter['engineering_capacity_available'] = team_capacity - current_quarter['engineering_capacity_used']
            current_quarter['personal_capacity_available'] = personal_capacity - current_quarter['personal_capacity_used']
            current_quarter['filled_by'] = 'end_of_list'
            quarters.append(current_quarter)

        return quarters


def format_output(features: List[Dict], analysis: Dict, roadmap: List[Dict]) -> str:
    """Format the results for display"""
    output = ["=" * 60]
    output.append("RICE PRIORITIZATION RESULTS (engineering/personal effort split)")
    output.append("=" * 60)

    # Top prioritized features
    output.append("\n📊 TOP PRIORITIZED FEATURES\n")
    constraint_label = {
        'build_time': 'limited by BUILD time',
        'personal_time': 'limited by YOUR time',
        'balanced': 'balanced',
        'n/a': 'n/a'
    }
    for i, feature in enumerate(features[:10], 1):
        output.append(f"{i}. {feature.get('name', 'Unnamed')}")
        output.append(f"   RICE Score: {feature['rice_score']}  "
                       f"({constraint_label.get(feature.get('binding_constraint'), 'n/a')})")
        output.append(f"   Reach: {feature.get('reach', 0)} | Impact: {feature.get('impact', 'medium')} | "
                       f"Confidence: {feature.get('confidence', 'medium')}")
        output.append(f"   Engineering effort: {feature.get('engineering_effort', 'm')} (weight {ENGINEERING_EFFORT_WEIGHT}) | "
                       f"Personal effort: {feature.get('personal_effort', 'm')} (weight {PERSONAL_EFFORT_WEIGHT})")
        output.append("")

    # Portfolio analysis
    output.append("\n📈 PORTFOLIO ANALYSIS\n")
    output.append(f"Total Features: {analysis.get('total_features', 0)}")
    output.append(f"Total Engineering Effort: {analysis.get('total_engineering_effort_months', 0)} person-months (Claude Code's time)")
    output.append(f"Total Personal Effort: {analysis.get('total_personal_effort_hours', 0)} hours (your time)")
    output.append(f"Total Reach: {analysis.get('total_reach', 0):,} users")
    output.append(f"Average RICE Score: {analysis.get('average_rice', 0)}")

    output.append(f"\n🎯 Quick Wins (cheap on both dimensions): {analysis.get('quick_wins', 0)} features")
    for qw in analysis.get('quick_wins_list', []):
        output.append(f"   • {qw.get('name', 'Unnamed')} (RICE: {qw['rice_score']})")

    output.append(f"\n🚀 Big Bets (expensive on both dimensions): {analysis.get('big_bets', 0)} features")
    for bb in analysis.get('big_bets_list', []):
        output.append(f"   • {bb.get('name', 'Unnamed')} (RICE: {bb['rice_score']})")

    output.append(f"\n⏳ High-impact but YOUR-TIME-blocked (not a build problem): "
                   f"{analysis.get('personal_time_blocked', 0)} features")
    for pb in analysis.get('personal_time_blocked_list', []):
        output.append(f"   • {pb.get('name', 'Unnamed')} (RICE: {pb['rice_score']}, "
                       f"personal effort: {pb.get('personal_effort', 'm')})")

    # Roadmap
    output.append("\n\n📅 SUGGESTED ROADMAP\n")
    for quarter in roadmap:
        eng_used = quarter['engineering_capacity_used']
        eng_total = eng_used + quarter['engineering_capacity_available']
        personal_used = quarter['personal_capacity_used']
        personal_total = personal_used + quarter['personal_capacity_available']
        output.append(f"\nQ{quarter['quarter']} - Engineering: {eng_used}/{eng_total} person-months | "
                       f"Your time: {personal_used}/{personal_total} hours "
                       f"(quarter filled by: {quarter.get('filled_by', '?')})")
        for feature in quarter['features']:
            output.append(f"   • {feature.get('name', 'Unnamed')} (RICE: {feature['rice_score']})")

    return "\n".join(output)


def load_features_from_csv(filepath: str) -> List[Dict]:
    """Load features from CSV file. Expects engineering_effort and
    personal_effort as two separate columns (not a single 'effort' column)."""
    features = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            feature = {
                'name': row.get('name', ''),
                'reach': int(row.get('reach', 0)),
                'impact': row.get('impact', 'medium'),
                'confidence': row.get('confidence', 'medium'),
                'engineering_effort': row.get('engineering_effort', row.get('effort', 'm')),
                'personal_effort': row.get('personal_effort', 'm'),
                'description': row.get('description', '')
            }
            features.append(feature)
    return features


def create_sample_csv(filepath: str):
    """Create a sample CSV file for testing"""
    sample_features = [
        ['name', 'reach', 'impact', 'confidence', 'engineering_effort', 'personal_effort', 'description'],
        ['User Dashboard Redesign', '5000', 'high', 'high', 'l', 's', 'Complete redesign of user dashboard'],
        ['Mobile Push Notifications', '10000', 'massive', 'medium', 'm', 'xs', 'Add push notification support'],
        ['Dark Mode', '8000', 'medium', 'high', 's', 'xs', 'Implement dark mode theme'],
        ['API Rate Limiting', '2000', 'low', 'high', 'xs', 'xs', 'Add rate limiting to API'],
        ['Social Login', '12000', 'high', 'medium', 'm', 'l', 'Add Google/Facebook login (vendor account setup)'],
        ['Export to PDF', '3000', 'medium', 'low', 's', 'xs', 'Export reports as PDF'],
        ['Team Collaboration', '4000', 'massive', 'low', 'xl', 'm', 'Real-time collaboration features'],
        ['Search Improvements', '15000', 'high', 'high', 'm', 'xs', 'Enhance search functionality'],
        ['Onboarding Flow', '20000', 'massive', 'high', 's', 'xs', 'Improve new user onboarding'],
        ['Payment Processor Integration', '6000', 'high', 'medium', 'l', 'xl', 'New payment provider — needs underwriting approval, account setup'],
    ]

    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sample_features)

    print(f"Sample CSV created at: {filepath}")


def main():
    parser = argparse.ArgumentParser(description='RICE Framework for Feature Prioritization '
                                                   '(engineering/personal effort split)')
    parser.add_argument('input', nargs='?', help='CSV file with features or "sample" to create sample')
    parser.add_argument('--capacity', type=int, default=10,
                         help='Engineering capacity per quarter (person-months, Claude Code time)')
    parser.add_argument('--personal-capacity', type=int, default=20,
                         help='Personal capacity per quarter (hours of founder decisions/approvals/attention)')
    parser.add_argument('--output', choices=['text', 'json', 'csv'], default='text', help='Output format')

    args = parser.parse_args()

    # Create sample if requested
    if args.input == 'sample':
        create_sample_csv('sample_features.csv')
        return

    # Use sample data if no input provided
    if not args.input:
        features = [
            {'name': 'User Dashboard', 'reach': 5000, 'impact': 'high', 'confidence': 'high',
             'engineering_effort': 'l', 'personal_effort': 's'},
            {'name': 'Push Notifications', 'reach': 10000, 'impact': 'massive', 'confidence': 'medium',
             'engineering_effort': 'm', 'personal_effort': 'xs'},
            {'name': 'Dark Mode', 'reach': 8000, 'impact': 'medium', 'confidence': 'high',
             'engineering_effort': 's', 'personal_effort': 'xs'},
            {'name': 'API Rate Limiting', 'reach': 2000, 'impact': 'low', 'confidence': 'high',
             'engineering_effort': 'xs', 'personal_effort': 'xs'},
            {'name': 'Social Login', 'reach': 12000, 'impact': 'high', 'confidence': 'medium',
             'engineering_effort': 'm', 'personal_effort': 'l'},
        ]
    else:
        features = load_features_from_csv(args.input)

    # Calculate RICE scores
    calculator = RICECalculator()
    prioritized = calculator.prioritize_features(features)
    analysis = calculator.analyze_portfolio(prioritized)
    roadmap = calculator.generate_roadmap(prioritized, args.capacity, args.personal_capacity)

    # Output results
    if args.output == 'json':
        result = {
            'features': prioritized,
            'analysis': analysis,
            'roadmap': roadmap
        }
        print(json.dumps(result, indent=2))
    elif args.output == 'csv':
        # Output prioritized features as CSV
        if prioritized:
            keys = prioritized[0].keys()
            print(','.join(keys))
            for feature in prioritized:
                print(','.join(str(feature.get(k, '')) for k in keys))
    else:
        print(format_output(prioritized, analysis, roadmap))


if __name__ == "__main__":
    main()
