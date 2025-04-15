import os
import sys
import json
import logging
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pprint import pprint, pformat
from sample_client import AnalyticsServiceClient

class AnalyticsClientTester:
    """Test harness for the Analytics Service Client"""
    
    def __init__(
        self,
        client: AnalyticsServiceClient = None,
        base_url: str = "http://localhost:8000/api/analytics",
        service_secret: str = "your-service-secret",
        log_level: int = logging.INFO,
        output_dir: str = None
    ):
        # Set up logging
        self.logger = self._setup_logging(log_level)
        
        # Create client if not provided
        self.client = client or AnalyticsServiceClient(
            base_url=base_url,
            service_secret=service_secret,
            retry_attempts=2
        )
        
        self.logger.info(f"Initialized tester with base URL: {self.client.base_url}")
        
        # Test results tracking
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "test_details": []
        }
        
        # Output directory for test results
        self.output_dir = output_dir
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _setup_logging(self, log_level: int) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger("analytics-client-tester")
        logger.setLevel(log_level)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def run_test(self, name: str, test_fn: callable, *args, **kwargs) -> Tuple[bool, Any]:
        """Run a single test and track results"""
        start_time = time.time()
        self.results["total_tests"] += 1
        
        self.logger.info(f"Running test: {name}")
        
        try:
            result = test_fn(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log success
            self.logger.info(f"✅ Test passed in {duration:.2f}s: {name}")
            self.results["passed"] += 1
            
            # Track test details
            self.results["test_details"].append({
                "name": name,
                "status": "passed",
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "result_summary": self._get_result_summary(result)
            })
            
            return True, result
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log failure
            self.logger.error(f"❌ Test failed in {duration:.2f}s: {name}")
            self.logger.error(f"Error: {str(e)}")
            self.results["failed"] += 1
            
            # Track test details
            self.results["test_details"].append({
                "name": name,
                "status": "failed",
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
            
            return False, None
    
    def _get_result_summary(self, result: Any) -> Dict:
        """Generate a summary of the result for reporting"""
        if not isinstance(result, dict):
            return {"data_type": str(type(result)), "summary": str(result)[:100]}
        
        # For dictionary results, provide a summary of key fields
        summary = {
            "success": result.get("success", None),
            "message": result.get("message", None)
        }
        
        # Include some key metrics depending on what's available
        if "completion_rate" in result:
            summary["completion_rate"] = result["completion_rate"]
        if "total_subtasks" in result:
            summary["total_subtasks"] = result["total_subtasks"]
        if "total_estimated_hours" in result:
            summary["total_estimated_hours"] = result["total_estimated_hours"]
        
        return summary
    
    def save_results(self, filename: str = None) -> None:
        """Save test results to a JSON file"""
        if not self.output_dir:
            self.logger.warning("No output directory specified, skipping result save")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analytics_test_results_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Add summary stats
        self.results["summary"] = {
            "pass_rate": (self.results["passed"] / self.results["total_tests"]) * 100 if self.results["total_tests"] > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        self.logger.info(f"Test results saved to: {filepath}")
    
    def print_summary(self) -> None:
        """Print a summary of all test results"""
        print("\n" + "=" * 50)
        print("ANALYTICS CLIENT TEST SUMMARY")
        print("=" * 50)
        print(f"Total tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Skipped: {self.results['skipped']}")
        
        if self.results["total_tests"] > 0:
            pass_rate = (self.results["passed"] / self.results["total_tests"]) * 100
            print(f"Pass rate: {pass_rate:.1f}%")
        
        print("\nTest details:")
        for test in self.results["test_details"]:
            status = "✅ PASS" if test["status"] == "passed" else "❌ FAIL"
            print(f"  {status} - {test['name']} ({test['duration']:.2f}s)")
    
    # Test suites for different analytics types
    
    def test_user_analytics(self, user_id: str, visualize: bool = False) -> None:
        """Test all user analytics endpoints"""
        self.logger.info(f"Running user analytics tests for user: {user_id}")
        
        # Test user progress
        success, progress = self.run_test(
            f"User Progress - {user_id}",
            self.client.get_user_progress,
            user_id=user_id,
            visualize=visualize
        )
        
        if success:
            self.logger.info(f"User progress stats - Completion rate: {progress.get('completion_rate', 'N/A')}%, "
                            f"Tasks: {progress.get('completed_subtasks', 0)}/{progress.get('total_subtasks', 0)}")
        
        # Test user workload
        success, workload = self.run_test(
            f"User Workload - {user_id}",
            self.client.get_user_workload,
            user_id=user_id,
            visualize=visualize
        )
        
        if success:
            self.logger.info(f"User workload stats - Pending tasks: {workload.get('pending_subtasks', 'N/A')}, "
                            f"Est. hours: {workload.get('total_estimated_hours', 'N/A')}")
        
        # Test comprehensive user analytics
        self.run_test(
            f"User Comprehensive - {user_id}",
            self.client.get_user_comprehensive,
            user_id=user_id,
            visualize=visualize
        )
    
    def test_team_analytics(self, team_id: str, project_id: str = None, visualize: bool = False) -> None:
        """Test all team analytics endpoints"""
        self.logger.info(f"Running team analytics tests for team: {team_id}" + 
                       (f" in project: {project_id}" if project_id else ""))
        
        # Test team progress
        success, progress = self.run_test(
            f"Team Progress - {team_id}" + (f" (Project {project_id})" if project_id else ""),
            self.client.get_team_progress,
            team_id=team_id,
            project_id=project_id,
            visualize=visualize
        )
        
        if success:
            self.logger.info(f"Team progress stats - Completion rate: {progress.get('completion_rate', 'N/A')}%, "
                            f"Tasks: {progress.get('completed_subtasks', 0)}/{progress.get('total_subtasks', 0)}")
        
        # Test team workload
        success, workload = self.run_test(
            f"Team Workload - {team_id}" + (f" (Project {project_id})" if project_id else ""),
            self.client.get_team_workload,
            team_id=team_id,
            project_id=project_id,
            visualize=visualize
        )
        
        if success:
            self.logger.info(f"Team workload stats - Pending tasks: {workload.get('pending_subtasks', 'N/A')}, "
                            f"Est. hours: {workload.get('total_estimated_hours', 'N/A')}")
        
        # Test comprehensive team analytics
        self.run_test(
            f"Team Comprehensive - {team_id}" + (f" (Project {project_id})" if project_id else ""),
            self.client.get_team_comprehensive,
            team_id=team_id,
            project_id=project_id,
            visualize=visualize
        )
    
    def test_project_analytics(self, project_id: str, visualize: bool = False) -> None:
        """Test all project analytics endpoints"""
        self.logger.info(f"Running project analytics tests for project: {project_id}")
        
        # Test project progress
        success, progress = self.run_test(
            f"Project Progress - {project_id}",
            self.client.get_project_progress,
            project_id=project_id,
            visualize=visualize
        )
        
        if success:
            self.logger.info(f"Project progress stats - Completion rate: {progress.get('completion_rate', 'N/A')}%, "
                            f"Tasks: {progress.get('completed_subtasks', 0)}/{progress.get('total_subtasks', 0)}")
        
        # Test project workload
        success, workload = self.run_test(
            f"Project Workload - {project_id}",
            self.client.get_project_workload,
            project_id=project_id,
            visualize=visualize
        )
        
        if success:
            self.logger.info(f"Project workload stats - Pending tasks: {workload.get('pending_subtasks', 'N/A')}, "
                            f"Est. hours: {workload.get('total_estimated_hours', 'N/A')}")
        
        # Test comprehensive project analytics
        self.run_test(
            f"Project Comprehensive - {project_id}",
            self.client.get_project_comprehensive,
            project_id=project_id,
            visualize=visualize
        )
    
    def test_all(self, user_id: str, team_id: str, project_id: str, visualize: bool = False) -> None:
        """Run all analytics tests"""
        self.logger.info("Running all analytics tests")
        
        # User analytics
        self.test_user_analytics(user_id, visualize)
        
        # Team analytics
        self.test_team_analytics(team_id, project_id, visualize)
        
        # Project analytics
        self.test_project_analytics(project_id, visualize)
        
        # Cache invalidation test
        self.test_cache_invalidation(user_id)
        
        # Print summary
        self.print_summary()
    
    def test_cache_invalidation(self, user_id: str) -> None:
        """Test the cache invalidation functionality"""
        self.logger.info("Testing cache invalidation")
        
        # First call - should hit the API
        start_time = time.time()
        success1, _ = self.run_test(
            "Cache Test - First call (uncached)",
            self.client.get_user_progress,
            user_id=user_id,
            visualize=False
        )
        first_call_time = time.time() - start_time
        
        # Second call - should be cached and faster
        start_time = time.time()
        success2, _ = self.run_test(
            "Cache Test - Second call (should be cached)",
            self.client.get_user_progress,
            user_id=user_id,
            visualize=False
        )
        second_call_time = time.time() - start_time
        
        # Invalidate cache
        self.client.invalidate_cache()
        self.logger.info("Cache invalidated")
        
        # Third call - should hit API again
        start_time = time.time()
        success3, _ = self.run_test(
            "Cache Test - Third call (after invalidation)",
            self.client.get_user_progress,
            user_id=user_id,
            visualize=False
        )
        third_call_time = time.time() - start_time
        
        # Log results
        if all([success1, success2, success3]):
            self.logger.info(f"Cache test results: "
                           f"First call: {first_call_time:.4f}s, "
                           f"Second call: {second_call_time:.4f}s, "
                           f"After invalidation: {third_call_time:.4f}s")
            
            if second_call_time < first_call_time:
                self.logger.info("✅ Cache is working correctly (second call was faster)")
            else:
                self.logger.warning("⚠️ Cache might not be working optimally (second call was not faster)")


def main():
    """Main function to run the analytics client tester"""
    parser = argparse.ArgumentParser(description='Test Analytics Service Client')
    parser.add_argument('--base-url', default='http://localhost:8000/api/analytics', 
                        help='Base URL for the Analytics service')
    parser.add_argument('--secret', default='your-service-secret',
                        help='Service secret for authentication')
    parser.add_argument('--user-id', default='user-101',
                        help='User ID to use for analytics')
    parser.add_argument('--team-id', default='team-101',
                        help='Team ID to use for analytics')
    parser.add_argument('--project-id', default='project-101',
                        help='Project ID to use for analytics')
    parser.add_argument('--visualize', action='store_true',
                        help='Include visualization data in responses')
    parser.add_argument('--test-type', choices=['all', 'user', 'team', 'project', 'cache'], 
                        default='all', help='Which test types to run')
    parser.add_argument('--output-dir', default=None,
                        help='Directory to save test results')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up the client
    client = AnalyticsServiceClient(
        base_url=args.base_url,
        service_secret=args.secret
    )
    
    # Create tester
    tester = AnalyticsClientTester(
        client=client,
        output_dir=args.output_dir,
        log_level=logging.DEBUG if args.verbose else logging.INFO
    )
    
    # Run requested tests
    if args.test_type == 'all':
        tester.test_all(args.user_id, args.team_id, args.project_id, args.visualize)
    elif args.test_type == 'user':
        tester.test_user_analytics(args.user_id, args.visualize)
        tester.print_summary()
    elif args.test_type == 'team':
        tester.test_team_analytics(args.team_id, args.project_id, args.visualize)
        tester.print_summary()
    elif args.test_type == 'project':
        tester.test_project_analytics(args.project_id, args.visualize)
        tester.print_summary()
    elif args.test_type == 'cache':
        tester.test_cache_invalidation(args.user_id)
        tester.print_summary()
    
    # Save results if output directory was specified
    if args.output_dir:
        tester.save_results()
    
    # Return exit code based on test success
    return 0 if tester.results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


"""
python analytics_client_tester.py --test-type user
python analytics_client_tester.py --test-type team
python analytics_client_tester.py --test-type project

python analytics_client_tester.py --user-id user-102 --team-id team-101 --project-id project-101
python analytics_client_tester.py --visualize
python analytics_client_tester.py --output-dir ./test-results
python analytics_client_tester.py --verbose
python analytics_client_tester.py --base-url http://analytics-service.example.com/api/analytics

"""