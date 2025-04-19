#!/usr/bin/env python
import unittest
import os
import sys
import time
import subprocess
from pathlib import Path

def run_tests():
    """Run all test cases for the microservices."""
    print("=" * 50)
    print("Task Manager Microservices Test Suite")
    print("=" * 50)
    print("\nChecking if services are running...")
    
    # Check if services are running by pinging health endpoints
    services = [
        {"name": "User Management", "url": "http://127.0.0.1:8001/health"},
        {"name": "Project Management", "url": "http://127.0.0.1:8002/health"},
        {"name": "Analytics", "url": "http://127.0.0.1:8003/health"},
        {"name": "Notification", "url": "http://127.0.0.1:8004/api/v1/notifications/health"}
    ]
    
    import requests
    all_running = True
    for service in services:
        try:
            response = requests.get(service["url"], timeout=2)
            if response.status_code == 200:
                print(f"✅ {service['name']} Service is running.")
            else:
                print(f"❌ {service['name']} Service returned status code {response.status_code}.")
                all_running = False
        except requests.exceptions.RequestException:
            print(f"❌ {service['name']} Service is not running or not responding.")
            all_running = False
    
    if not all_running:
        print("\nNot all services are running. Would you like to:")
        print("1. Start all services and continue")
        print("2. Continue anyway (tests might fail)")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            # Start services using the start_services.py script
            print("\nStarting all services...")
            start_proc = subprocess.Popen([sys.executable, "start_services.py"], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT)
            time.sleep(10)  # Give services time to start
            print("Services should be starting, continuing with tests...")
        elif choice == "3":
            print("Exiting.")
            sys.exit(0)
        # If choice is 2 or anything else, just continue
    
    # Discover and run tests
    print("\nRunning tests...")
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Create a results directory if it doesn't exist
    results_dir = Path("test_results")
    results_dir.mkdir(exist_ok=True)
    
    # Run tests with TextTestRunner
    result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Report summary
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    print(f"Total tests run: {result.testsRun}")
    print(f"Tests passed: {result.testsRun - (len(result.failures) + len(result.errors))}")
    print(f"Tests failed: {len(result.failures)}")
    print(f"Test errors: {len(result.errors)}")
    print("=" * 50)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests()) 