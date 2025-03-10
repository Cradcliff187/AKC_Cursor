#!/usr/bin/env python
import os
import sys
import subprocess
import argparse

def run_tests(args):
    """Run the tests with the specified options."""
    cmd = ['pytest']
    
    # Add verbosity if requested
    if args.verbose:
        cmd.append('-v')
    
    # Add test pattern if provided
    if args.pattern:
        cmd.append(args.pattern)
    
    # Add specific test markers if provided
    if args.markers:
        for marker in args.markers:
            cmd.append(f'-m {marker}')
    
    # Add coverage if requested
    if args.coverage:
        cmd = ['coverage', 'run', '-m'] + cmd
    
    # Run the tests
    result = subprocess.run(cmd, capture_output=not args.verbose)
    
    # Generate coverage report if requested
    if args.coverage:
        if args.html:
            subprocess.run(['coverage', 'html'], check=True)
            print("\nHTML coverage report generated in 'htmlcov' directory.")
        else:
            subprocess.run(['coverage', 'report', '-m'], check=True)
    
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description='Run the test suite with various options.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Run tests with verbose output')
    parser.add_argument('-c', '--coverage', action='store_true', help='Run tests with coverage')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('-m', '--markers', nargs='+', help='Run tests with specific markers (e.g. unit, functional)')
    parser.add_argument('-p', '--pattern', help='Run tests matching the pattern (e.g. "test_invoice")')
    
    args = parser.parse_args()
    
    return run_tests(args)

if __name__ == '__main__':
    sys.exit(main()) 