#!/usr/bin/env python3
"""
Quality Scoring System for Beamer Presentations

Calculates objective quality scores (0-100) based on defined rubrics.
Enforces quality gates: 80 (commit), 90 (PR), 95 (excellence).

Usage:
    python scripts/quality_score.py Slides/Lecture01_Topic.tex
    python scripts/quality_score.py Slides/Lecture01_Topic.tex --summary
    python scripts/quality_score.py Slides/*.tex
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import re

# ==============================================================================
# SCORING RUBRIC
# ==============================================================================

BEAMER_RUBRIC = {
    'critical': {
        'compilation_failure': {'points': 100, 'auto_fail': True},
        'undefined_citation': {'points': 15},
        'overfull_hbox': {'points': 10},
        'equation_overflow': {'points': 20},
    },
    'major': {
        'text_overflow': {'points': 5},
        'notation_inconsistency': {'points': 3},
        'missing_figure': {'points': 5},
    },
    'minor': {
        'font_size_reduction': {'points': 1},
        'missing_frame_title': {'points': 1},
    }
}

THRESHOLDS = {
    'commit': 80,
    'pr': 90,
    'excellence': 95
}

# ==============================================================================
# ISSUE DETECTION
# ==============================================================================

class IssueDetector:
    """Detect common issues for quality scoring."""

    @staticmethod
    def check_beamer_compilation(filepath: Path) -> Tuple[bool, str]:
        """Check if Beamer file compiles successfully."""
        try:
            # Run XeLaTeX compilation
            result = subprocess.run(
                ['xelatex', '-interaction=nonstopmode', str(filepath)],
                cwd=filepath.parent,
                capture_output=True,
                text=True,
                timeout=60
            )

            log_file = filepath.with_suffix('.log')
            if not log_file.exists():
                return False, "No .log file generated"

            # Check for fatal errors
            log_content = log_file.read_text(encoding='utf-8', errors='ignore')
            if '! LaTeX Error:' in log_content or '! Emergency stop' in log_content:
                # Extract error message
                error_match = re.search(r'! (.+?)(?:\n|$)', log_content)
                error_msg = error_match.group(1) if error_match else "Compilation failed"
                return False, error_msg

            # Check if PDF was generated
            pdf_file = filepath.with_suffix('.pdf')
            if not pdf_file.exists():
                return False, "PDF not generated"

            return True, "OK"

        except subprocess.TimeoutExpired:
            return False, "Compilation timeout (>60s)"
        except Exception as e:
            return False, f"Compilation error: {str(e)}"

    @staticmethod
    def check_overfull_hbox(log_file: Path) -> List[Dict]:
        """Check for overfull hbox warnings in .log file."""
        if not log_file.exists():
            return []

        issues = []
        log_content = log_file.read_text(encoding='utf-8', errors='ignore')

        # Match: Overfull \hbox (12.34pt too wide) detected at line 123
        pattern = r'Overfull \\hbox \(([0-9.]+)pt too wide\).*?line (\d+)'
        for match in re.finditer(pattern, log_content):
            width = float(match.group(1))
            line = int(match.group(2))
            issues.append({
                'type': 'overfull_hbox',
                'line': line,
                'width': width,
                'severity': 'critical' if width > 10 else 'major'
            })

        return issues

    @staticmethod
    def check_undefined_citations(log_file: Path) -> List[str]:
        """Check for undefined citations in .log file."""
        if not log_file.exists():
            return []

        log_content = log_file.read_text(encoding='utf-8', errors='ignore')

        # Match: LaTeX Warning: Citation `key' on page 5 undefined
        pattern = r"Citation `([^']+)' .* undefined"
        citations = re.findall(pattern, log_content)

        return list(set(citations))  # Remove duplicates

    @staticmethod
    def check_missing_figures(tex_file: Path) -> List[str]:
        """Check for referenced figures that don't exist."""
        content = tex_file.read_text(encoding='utf-8', errors='ignore')

        # Match: \includegraphics{path/to/figure.png}
        pattern = r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}'
        figures = re.findall(pattern, content)

        missing = []
        for fig in figures:
            # Resolve relative path
            fig_path = tex_file.parent / fig
            if not fig_path.exists():
                # Try with common extensions
                found = False
                for ext in ['.png', '.pdf', '.jpg', '.jpeg']:
                    if fig_path.with_suffix(ext).exists():
                        found = True
                        break
                if not found:
                    missing.append(fig)

        return missing

# ==============================================================================
# SCORER
# ==============================================================================

class BeamerScorer:
    """Score a Beamer .tex file."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.log_file = filepath.with_suffix('.log')
        self.issues = {
            'critical': [],
            'major': [],
            'minor': []
        }

    def score(self) -> Dict:
        """Calculate quality score."""
        # 1. Check compilation
        compiles, error_msg = IssueDetector.check_beamer_compilation(self.filepath)
        if not compiles:
            self.issues['critical'].append({
                'type': 'compilation_failure',
                'message': error_msg
            })
            return self._calculate_score()

        # 2. Check overfull hbox
        overfull_issues = IssueDetector.check_overfull_hbox(self.log_file)
        for issue in overfull_issues:
            severity = issue['severity']
            self.issues[severity].append({
                'type': 'overfull_hbox',
                'line': issue['line'],
                'width': issue['width']
            })

        # 3. Check undefined citations
        undefined_cites = IssueDetector.check_undefined_citations(self.log_file)
        for cite in undefined_cites:
            self.issues['critical'].append({
                'type': 'undefined_citation',
                'citation': cite
            })

        # 4. Check missing figures
        missing_figs = IssueDetector.check_missing_figures(self.filepath)
        for fig in missing_figs:
            self.issues['major'].append({
                'type': 'missing_figure',
                'file': fig
            })

        return self._calculate_score()

    def _calculate_score(self) -> Dict:
        """Calculate final score based on issues."""
        deductions = 0
        auto_fail = False

        for severity in ['critical', 'major', 'minor']:
            for issue in self.issues[severity]:
                issue_type = issue['type']
                if issue_type in BEAMER_RUBRIC[severity]:
                    points = BEAMER_RUBRIC[severity][issue_type]['points']
                    deductions += points
                    if BEAMER_RUBRIC[severity][issue_type].get('auto_fail'):
                        auto_fail = True

        score = max(0, 100 - deductions) if not auto_fail else 0

        # Determine gate status
        gate = 'FAIL'
        if score >= THRESHOLDS['excellence']:
            gate = 'EXCELLENCE'
        elif score >= THRESHOLDS['pr']:
            gate = 'PR'
        elif score >= THRESHOLDS['commit']:
            gate = 'COMMIT'

        return {
            'file': str(self.filepath),
            'score': score,
            'gate': gate,
            'deductions': deductions,
            'issues': self.issues,
            'thresholds': THRESHOLDS
        }

# ==============================================================================
# CLI
# ==============================================================================

def format_report(result: Dict, summary: bool = False) -> str:
    """Format scoring result as human-readable report."""
    lines = []

    if summary:
        # One-line summary
        score = result['score']
        gate = result['gate']
        file = Path(result['file']).name
        lines.append(f"{file}: {score}/100 [{gate}]")
    else:
        # Detailed report
        lines.append("=" * 70)
        lines.append(f"Quality Score Report: {result['file']}")
        lines.append("=" * 70)
        lines.append(f"Score: {result['score']}/100")
        lines.append(f"Gate: {result['gate']}")
        lines.append(f"Deductions: -{result['deductions']} points")
        lines.append("")

        # List issues by severity
        for severity in ['critical', 'major', 'minor']:
            issues = result['issues'][severity]
            if issues:
                lines.append(f"{severity.upper()} Issues ({len(issues)}):")
                for issue in issues:
                    issue_type = issue['type']
                    if issue_type == 'compilation_failure':
                        lines.append(f"  - Compilation failed: {issue['message']}")
                    elif issue_type == 'overfull_hbox':
                        lines.append(f"  - Overfull hbox at line {issue['line']} ({issue['width']:.1f}pt too wide)")
                    elif issue_type == 'undefined_citation':
                        lines.append(f"  - Undefined citation: {issue['citation']}")
                    elif issue_type == 'missing_figure':
                        lines.append(f"  - Missing figure: {issue['file']}")
                    else:
                        lines.append(f"  - {issue_type}: {issue}")
                lines.append("")

        # Thresholds
        lines.append("Quality Gates:")
        lines.append(f"  Commit:     {result['thresholds']['commit']}/100")
        lines.append(f"  PR:         {result['thresholds']['pr']}/100")
        lines.append(f"  Excellence: {result['thresholds']['excellence']}/100")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description='Score Beamer .tex files')
    parser.add_argument('files', nargs='+', help='Beamer .tex files to score')
    parser.add_argument('--summary', action='store_true', help='Show one-line summary per file')
    args = parser.parse_args()

    results = []
    for file_pattern in args.files:
        # Support glob patterns
        for filepath in Path('.').glob(file_pattern):
            if filepath.suffix == '.tex':
                scorer = BeamerScorer(filepath)
                result = scorer.score()
                results.append(result)
                print(format_report(result, summary=args.summary))
                if not args.summary:
                    print()

    # Summary statistics
    if len(results) > 1:
        avg_score = sum(r['score'] for r in results) / len(results)
        passed = sum(1 for r in results if r['score'] >= THRESHOLDS['commit'])
        print("=" * 70)
        print(f"Summary: {len(results)} files, avg score {avg_score:.1f}/100, {passed} passed commit gate")

    # Exit code: 0 if all passed commit gate, 1 otherwise
    if all(r['score'] >= THRESHOLDS['commit'] for r in results):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
