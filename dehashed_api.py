#!/usr/bin/env python3
"""
DeHashed API Client
A comprehensive Python client for interacting with the DeHashed API.

Features:
- Search API (general search and password search)
- Monitoring API (tasks, reports, notification channels)
- WHOIS API (domain lookup, reverse lookups, subdomain scanning)

Author: Generated for DeHashed API v2
"""

import os
import json
import csv
import requests
from typing import Optional, Dict, List, Union, Any
from dataclasses import dataclass


@dataclass
class DeHashedConfig:
    """Configuration for DeHashed API client"""
    api_key: str
    base_url: str = "https://api.dehashed.com/v2"
    timeout: int = 30


class DeHashedAPIError(Exception):
    """Custom exception for DeHashed API errors"""
    pass


class DeHashedClient:
    """Main client class for interacting with the DeHashed API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DeHashed API client
        
        Args:
            api_key: Your DeHashed API key. If not provided, will try to read from
                    DEHASHED_API_KEY environment variable
        """
        if api_key is None:
            api_key = os.environ.get('DEHASHED_API_KEY')
            if api_key is None:
                raise DeHashedAPIError(
                    "API key must be provided or set in DEHASHED_API_KEY environment variable"
                )
        
        self.config = DeHashedConfig(api_key=api_key)
        self.session = requests.Session()
        self.session.headers.update({
            'Dehashed-Api-Key': self.config.api_key,
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a POST request to the DeHashed API
        
        Args:
            endpoint: API endpoint (e.g., '/search')
            data: JSON data to send in the request body
            
        Returns:
            Response data as dictionary
            
        Raises:
            DeHashedAPIError: If the request fails
        """
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            response = self.session.post(
                url,
                json=data if data else {},
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Try to get more details from the error response
            error_msg = f"API request failed: {str(e)}"
            try:
                error_details = e.response.json()
                if 'message' in error_details:
                    error_msg = f"API Error: {error_details['message']}"
                elif 'error' in error_details:
                    error_msg = f"API Error: {error_details['error']}"
            except:
                pass
            raise DeHashedAPIError(error_msg)
        except requests.exceptions.RequestException as e:
            raise DeHashedAPIError(f"API request failed: {str(e)}")
    
    # ==================== SEARCH API ====================
    
    def search(
        self,
        query: str,
        page: int = 1,
        size: int = 10000,
        wildcard: bool = False,
        regex: bool = False,
        de_dupe: bool = False
    ) -> Dict[str, Any]:
        """
        Perform a general search query
        
        Args:
            query: Search query (e.g., "email:example@example.com")
            page: Page number for pagination (default: 1)
            size: Number of results per page (default: 10000)
            wildcard: Enable wildcard matching (default: False)
            regex: Enable regex matching (default: False)
            de_dupe: Remove duplicate entries (default: False)
            
        Returns:
            Search results with entries and metadata
            
        Example:
            results = client.search("email:user@example.com")
            results = client.search("username:admin", wildcard=True)
            results = client.search("domain:example.com", page=2, size=100)
        """
        data = {
            "query": query,
            "page": page,
            "size": size,
            "wildcard": wildcard,
            "regex": regex,
            "de_dupe": de_dupe
        }
        return self._make_request("/search", data)
    
    def search_password(self, password_hash: str) -> Dict[str, Any]:
        """
        Search for records by password hash (FREE - no credits required)
        
        Args:
            password_hash: Password hash to search for
            
        Returns:
            Records associated with the password hash
            
        Example:
            results = client.search_password("5f4dcc3b5aa765d61d8327deb882cf99")
        """
        data = {"hash": password_hash}
        return self._make_request("/search-password", data)
    
    # ==================== MONITORING API - TASKS ====================
    
    def monitoring_create_task(
        self,
        task_type: str,
        value: str,
        channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new monitoring task
        
        Args:
            task_type: Type of task (email, username, phone, ip_address, address, 
                      name, vin, domain, password)
            value: Value to monitor
            channels: List of notification channel types (e.g., ["email", "webhook"])
            
        Returns:
            Created task information
            
        Example:
            task = client.monitoring_create_task("email", "monitor@example.com", ["email"])
        """
        data = {
            "type": task_type,
            "value": value
        }
        if channels:
            data["channels"] = channels
        return self._make_request("/monitoring/create-task", data)
    
    def monitoring_update_task(
        self,
        task_id: str,
        task_type: str,
        value: str,
        channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing monitoring task
        
        Args:
            task_id: ID of the task to update
            task_type: Type of task
            value: New value to monitor
            channels: Updated list of notification channels
            
        Returns:
            Updated task information
            
        Example:
            task = client.monitoring_update_task(
                "task-id-123", 
                "email", 
                "newemail@example.com",
                ["email", "webhook"]
            )
        """
        data = {
            "id": task_id,
            "type": task_type,
            "value": value
        }
        if channels:
            data["channels"] = channels
        return self._make_request("/monitoring/update-task", data)
    
    def monitoring_update_task_status(
        self,
        task_id: str,
        active: bool
    ) -> Dict[str, Any]:
        """
        Update the active status of a monitoring task
        
        Args:
            task_id: ID of the task to update
            active: Whether the task should be active
            
        Returns:
            Updated task information
            
        Example:
            client.monitoring_update_task_status("task-id-123", False)
        """
        data = {
            "id": task_id,
            "active": active
        }
        return self._make_request("/monitoring/update-task", data)
    
    def monitoring_delete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Delete a monitoring task
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            Deletion confirmation
            
        Example:
            client.monitoring_delete_task("task-id-123")
        """
        data = {"id": task_id}
        return self._make_request("/monitoring/delete-task", data)
    
    def monitoring_get_tasks(self, page: int = 1) -> Dict[str, Any]:
        """
        Retrieve a list of monitoring tasks
        
        Args:
            page: Page number for pagination (default: 1)
            
        Returns:
            List of monitoring tasks
            
        Example:
            tasks = client.monitoring_get_tasks()
        """
        data = {"page": page}
        return self._make_request("/monitoring/get-tasks", data)
    
    def monitoring_get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve details of a specific monitoring task
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Task details
            
        Example:
            task = client.monitoring_get_task("task-id-123")
        """
        data = {"id": task_id}
        return self._make_request("/monitoring/get-task", data)
    
    # ==================== MONITORING API - REPORTS ====================
    
    def monitoring_get_reports(self, page: int = 1) -> Dict[str, Any]:
        """
        Retrieve a list of monitoring reports
        
        Args:
            page: Page number for pagination (default: 1)
            
        Returns:
            List of monitoring reports
            
        Example:
            reports = client.monitoring_get_reports()
        """
        data = {"page": page}
        return self._make_request("/monitoring/get-reports", data)
    
    def monitoring_get_report(self, report_id: str) -> Dict[str, Any]:
        """
        Retrieve details of a specific monitoring report
        
        Args:
            report_id: ID of the report to retrieve
            
        Returns:
            Report details
            
        Example:
            report = client.monitoring_get_report("report-id-123")
        """
        data = {"id": report_id}
        return self._make_request("/monitoring/get-report", data)
    
    # ==================== MONITORING API - NOTIFICATION CHANNELS ====================
    
    def monitoring_get_channels(self) -> Dict[str, Any]:
        """
        Retrieve notification channels
        
        Returns:
            List of notification channels
            
        Example:
            channels = client.monitoring_get_channels()
        """
        return self._make_request("/monitoring/get-channels", {})
    
    def monitoring_update_channel(
        self,
        channel_type: str,
        value: str
    ) -> Dict[str, Any]:
        """
        Update a notification channel
        
        Args:
            channel_type: Type of channel (webhook or email)
            value: Channel value (URL for webhook, email address for email)
            
        Returns:
            Updated channel information
            
        Example:
            client.monitoring_update_channel("webhook", "https://example.com/webhook")
            client.monitoring_update_channel("email", "notifications@example.com")
        """
        data = {
            "type": channel_type,
            "value": value
        }
        return self._make_request("/monitoring/update-channel", data)
    
    def monitoring_delete_channel(self, channel_type: str) -> Dict[str, Any]:
        """
        Delete a notification channel
        
        Args:
            channel_type: Type of channel to delete (webhook or email)
            
        Returns:
            Deletion confirmation
            
        Example:
            client.monitoring_delete_channel("webhook")
        """
        data = {"channel": channel_type}
        return self._make_request("/monitoring/delete-channel", data)
    
    # ==================== WHOIS API ====================
    
    def whois_search(self, domain: str) -> Dict[str, Any]:
        """
        Look up WHOIS information for a domain
        
        Args:
            domain: Domain name to look up
            
        Returns:
            WHOIS information for the domain
            
        Example:
            info = client.whois_search("example.com")
        """
        data = {
            "search_type": "whois",
            "domain": domain
        }
        return self._make_request("/whois/search", data)
    
    def whois_history(self, domain: str) -> Dict[str, Any]:
        """
        Look up WHOIS history for a domain
        
        Args:
            domain: Domain name to look up
            
        Returns:
            Historical WHOIS records for the domain
            
        Example:
            history = client.whois_history("example.com")
        """
        data = {
            "search_type": "whois-history",
            "domain": domain
        }
        return self._make_request("/whois/search", data)
    
    def whois_reverse(
        self,
        name: Optional[str] = None,
        organization: Optional[str] = None,
        email: Optional[str] = None,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform reverse WHOIS lookup based on parameters
        
        Args:
            name: Registrant name
            organization: Organization name
            email: Registrant email
            include: List of strings that must be present in results
            exclude: List of strings to exclude from results
            
        Returns:
            Domains matching the reverse WHOIS criteria
            
        Example:
            domains = client.whois_reverse(email="admin@example.com")
            domains = client.whois_reverse(
                organization="Example Corp",
                include=["example", "test"]
            )
        """
        data: Dict[str, Any] = {"search_type": "reverse-whois"}
        
        if name:
            data["name"] = name
        if organization:
            data["organization"] = organization
        if email:
            data["email"] = email
        if include:
            data["include"] = include
        if exclude:
            data["exclude"] = exclude
        
        return self._make_request("/whois/search", data)
    
    def whois_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Look up WHOIS information for an IP address
        
        Args:
            ip_address: IP address to look up
            
        Returns:
            WHOIS information for the IP address
            
        Example:
            info = client.whois_ip("8.8.8.8")
        """
        data = {
            "search_type": "reverse-ip",
            "domain": ip_address
        }
        return self._make_request("/whois/search", data)
    
    def whois_mx(self, mx_server: str) -> Dict[str, Any]:
        """
        Look up domains using a specific MX server
        
        Args:
            mx_server: MX server address
            
        Returns:
            Domains using the specified MX server
            
        Example:
            domains = client.whois_mx("mail.example.com")
        """
        data = {
            "search_type": "reverse-mx",
            "domain": mx_server
        }
        return self._make_request("/whois/search", data)
    
    def whois_ns(self, ns_server: str) -> Dict[str, Any]:
        """
        Look up domains using a specific nameserver
        
        Args:
            ns_server: Nameserver address
            
        Returns:
            Domains using the specified nameserver
            
        Example:
            domains = client.whois_ns("ns1.example.com")
        """
        data = {
            "search_type": "reverse-ns",
            "domain": ns_server
        }
        return self._make_request("/whois/search", data)
    
    def whois_subdomain_scan(self, domain: str) -> Dict[str, Any]:
        """
        Scan for subdomains of a domain using WHOIS data
        
        Args:
            domain: Base domain to scan
            
        Returns:
            List of discovered subdomains
            
        Example:
            subdomains = client.whois_subdomain_scan("example.com")
        """
        data = {
            "search_type": "subdomain-scan",
            "domain": domain
        }
        return self._make_request("/whois/search", data)
    
    # ==================== UTILITY METHODS ====================
    
    def get_balance(self) -> Optional[int]:
        """
        Get account balance from a search response
        Note: Balance is returned in search API responses
        
        Returns:
            Balance if available in last response, None otherwise
        """
        # The balance is returned in the response of search queries
        # This is a helper method to extract it
        try:
            response = self.search("email:test@test.com", size=1)
            return response.get("balance")
        except Exception:
            return None
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# ==================== HELPER FUNCTIONS ====================

def pretty_print_results(results: Dict[str, Any], indent: int = 2):
    """
    Pretty print API results
    
    Args:
        results: API response dictionary
        indent: JSON indentation level
    """
    print(json.dumps(results, indent=indent))


def save_results_to_file(results: Dict[str, Any], filename: str):
    """
    Save API results to a JSON file
    
    Args:
        results: API response dictionary
        filename: Output filename
    """
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {filename}")


def save_results_to_csv(results: Dict[str, Any], filename: str):
    """
    Save search API results to a CSV file
    
    Args:
        results: API response dictionary (must contain 'entries' key)
        filename: Output filename
        
    Note:
        This function is designed for search results. It will flatten the entries
        and handle array fields by joining them with semicolons.
    """
    if 'entries' not in results or not results['entries']:
        print("No entries found in results to export to CSV")
        return
    
    entries = results['entries']
    
    # Collect all possible field names from all entries
    fieldnames = set()
    for entry in entries:
        fieldnames.update(entry.keys())
    
    # Sort fieldnames for consistent output, with 'id' and 'database_name' first
    priority_fields = ['id', 'database_name']
    sorted_fields = priority_fields + sorted([f for f in fieldnames if f not in priority_fields and f != 'raw_record'])
    
    # Add raw_record last if it exists
    if 'raw_record' in fieldnames:
        sorted_fields.append('raw_record')
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sorted_fields)
        writer.writeheader()
        
        for entry in entries:
            # Flatten the entry - convert lists to semicolon-separated strings
            flattened = {}
            for key in sorted_fields:
                if key in entry:
                    value = entry[key]
                    if isinstance(value, list):
                        # Join list items with semicolon
                        flattened[key] = '; '.join(str(v) for v in value)
                    elif isinstance(value, dict):
                        # Convert dict to JSON string
                        flattened[key] = json.dumps(value)
                    else:
                        flattened[key] = value
                else:
                    flattened[key] = ''
            
            writer.writerow(flattened)
    
    print(f"Results saved to {filename}")
    print(f"Total entries exported: {len(entries)}")


# ==================== EXAMPLE USAGE ====================

def example_usage():
    """Example usage of the DeHashed API client"""
    
    # Initialize client (reads API key from environment variable DEHASHED_API_KEY)
    # Or pass it directly: client = DeHashedClient(api_key="your-api-key-here")
    
    try:
        with DeHashedClient() as client:
            
            # Example 1: Basic search
            print("\n=== Example 1: Email Search ===")
            results = client.search("email:example@example.com")
            pretty_print_results(results)
            
            # Example 2: Password hash search (FREE)
            print("\n=== Example 2: Password Hash Search ===")
            results = client.search_password("5f4dcc3b5aa765d61d8327deb882cf99")
            pretty_print_results(results)
            
            # Example 3: Create monitoring task
            print("\n=== Example 3: Create Monitoring Task ===")
            task = client.monitoring_create_task(
                "email",
                "monitor@example.com",
                ["email"]
            )
            pretty_print_results(task)
            
            # Example 4: Get monitoring tasks
            print("\n=== Example 4: Get Monitoring Tasks ===")
            tasks = client.monitoring_get_tasks()
            pretty_print_results(tasks)
            
            # Example 5: WHOIS lookup
            print("\n=== Example 5: WHOIS Lookup ===")
            whois_info = client.whois_search("example.com")
            pretty_print_results(whois_info)
            
            # Example 6: Reverse WHOIS
            print("\n=== Example 6: Reverse WHOIS ===")
            domains = client.whois_reverse(email="admin@example.com")
            pretty_print_results(domains)
            
            # Example 7: Subdomain scan
            print("\n=== Example 7: Subdomain Scan ===")
            subdomains = client.whois_subdomain_scan("example.com")
            pretty_print_results(subdomains)
            
            # Example 8: Get account balance
            print("\n=== Example 8: Get Balance ===")
            balance = client.get_balance()
            print(f"Account balance: {balance}")
            
    except DeHashedAPIError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Check if API key is set
    if not os.environ.get('DEHASHED_API_KEY'):
        print("WARNING: DEHASHED_API_KEY environment variable not set!")
        print("Set it with: export DEHASHED_API_KEY='your-api-key-here'")
        print("\nOr initialize the client directly:")
        print("client = DeHashedClient(api_key='your-api-key-here')")
    else:
        example_usage()

