#!/usr/bin/env python3
"""
DeHashed API Command Line Interface

A simple CLI for interacting with the DeHashed API.
"""

import argparse
import sys
from dehashed_api import DeHashedClient, DeHashedAPIError, pretty_print_results, save_results_to_file, save_results_to_csv


def cmd_search(args):
    """Handle search command"""
    with DeHashedClient(api_key=args.api_key) as client:
        results = client.search(
            query=args.query,
            page=args.page,
            size=args.size,
            wildcard=args.wildcard,
            regex=args.regex,
            de_dupe=args.dedupe
        )
        
        if args.output:
            # Determine format from file extension if not specified
            output_format = args.format
            if not output_format:
                if args.output.endswith('.csv'):
                    output_format = 'csv'
                else:
                    output_format = 'json'
            
            if output_format == 'csv':
                save_results_to_csv(results, args.output)
            else:
                save_results_to_file(results, args.output)
        else:
            pretty_print_results(results)


def cmd_search_password(args):
    """Handle password search command"""
    with DeHashedClient(api_key=args.api_key) as client:
        results = client.search_password(args.hash)
        
        if args.output:
            # Determine format from file extension if not specified
            output_format = args.format
            if not output_format:
                if args.output.endswith('.csv'):
                    output_format = 'csv'
                else:
                    output_format = 'json'
            
            if output_format == 'csv':
                save_results_to_csv(results, args.output)
            else:
                save_results_to_file(results, args.output)
        else:
            pretty_print_results(results)


def cmd_monitoring_create_task(args):
    """Handle create monitoring task command"""
    with DeHashedClient(api_key=args.api_key) as client:
        channels = args.channels.split(',') if args.channels else None
        task = client.monitoring_create_task(
            task_type=args.type,
            value=args.value,
            channels=channels
        )
        pretty_print_results(task)


def cmd_monitoring_get_tasks(args):
    """Handle get monitoring tasks command"""
    with DeHashedClient(api_key=args.api_key) as client:
        tasks = client.monitoring_get_tasks(page=args.page)
        
        if args.output:
            save_results_to_file(tasks, args.output)
        else:
            pretty_print_results(tasks)


def cmd_monitoring_delete_task(args):
    """Handle delete monitoring task command"""
    with DeHashedClient(api_key=args.api_key) as client:
        result = client.monitoring_delete_task(args.task_id)
        pretty_print_results(result)


def cmd_whois(args):
    """Handle WHOIS command"""
    with DeHashedClient(api_key=args.api_key) as client:
        if args.type == 'lookup':
            results = client.whois_search(args.domain)
        elif args.type == 'history':
            results = client.whois_history(args.domain)
        elif args.type == 'reverse':
            results = client.whois_reverse(
                name=args.name,
                organization=args.organization,
                email=args.email
            )
        elif args.type == 'ip':
            results = client.whois_ip(args.domain)
        elif args.type == 'mx':
            results = client.whois_mx(args.domain)
        elif args.type == 'ns':
            results = client.whois_ns(args.domain)
        elif args.type == 'subdomain':
            results = client.whois_subdomain_scan(args.domain)
        else:
            print(f"Unknown WHOIS type: {args.type}")
            return
        
        if args.output:
            save_results_to_file(results, args.output)
        else:
            pretty_print_results(results)


def cmd_balance(args):
    """Handle balance command"""
    with DeHashedClient(api_key=args.api_key) as client:
        balance = client.get_balance()
        print(f"Account balance: {balance} credits")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='DeHashed API Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for email
  %(prog)s search "email:user@example.com"
  
  # Search with wildcard
  %(prog)s search "username:admin*" --wildcard
  
  # Save search results to CSV
  %(prog)s search "domain:example.com" --output results.csv
  
  # Save search results to JSON (explicit format)
  %(prog)s search "domain:example.com" --output results.json --format json
  
  # Search password hash (FREE)
  %(prog)s search-password 5f4dcc3b5aa765d61d8327deb882cf99
  
  # Create monitoring task
  %(prog)s monitoring create-task email monitor@example.com --channels email,webhook
  
  # Get monitoring tasks
  %(prog)s monitoring get-tasks
  
  # WHOIS lookup
  %(prog)s whois lookup example.com
  
  # Reverse WHOIS
  %(prog)s whois reverse --email admin@example.com
  
  # Subdomain scan
  %(prog)s whois subdomain example.com
  
  # Check balance
  %(prog)s balance
        """
    )
    
    parser.add_argument(
        '--api-key',
        help='DeHashed API key (or set DEHASHED_API_KEY env var)',
        default=None
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Perform a search')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--page', type=int, default=1, help='Page number')
    search_parser.add_argument('--size', type=int, default=10000, help='Results per page')
    search_parser.add_argument('--wildcard', action='store_true', help='Enable wildcard matching')
    search_parser.add_argument('--regex', action='store_true', help='Enable regex matching')
    search_parser.add_argument('--dedupe', action='store_true', help='Remove duplicates')
    search_parser.add_argument('--output', '-o', help='Save to file')
    search_parser.add_argument('--format', '-f', choices=['json', 'csv'], help='Output format (default: auto-detect from file extension)')
    search_parser.set_defaults(func=cmd_search)
    
    # Search password command
    search_pwd_parser = subparsers.add_parser('search-password', help='Search by password hash (FREE)')
    search_pwd_parser.add_argument('hash', help='Password hash')
    search_pwd_parser.add_argument('--output', '-o', help='Save to file')
    search_pwd_parser.add_argument('--format', '-f', choices=['json', 'csv'], help='Output format (default: auto-detect from file extension)')
    search_pwd_parser.set_defaults(func=cmd_search_password)
    
    # Monitoring commands
    monitoring_parser = subparsers.add_parser('monitoring', help='Monitoring commands')
    monitoring_subparsers = monitoring_parser.add_subparsers(dest='monitoring_command')
    
    # Create task
    create_task_parser = monitoring_subparsers.add_parser('create-task', help='Create monitoring task')
    create_task_parser.add_argument('type', help='Task type (email, username, phone, etc.)')
    create_task_parser.add_argument('value', help='Value to monitor')
    create_task_parser.add_argument('--channels', help='Notification channels (comma-separated)')
    create_task_parser.set_defaults(func=cmd_monitoring_create_task)
    
    # Get tasks
    get_tasks_parser = monitoring_subparsers.add_parser('get-tasks', help='Get monitoring tasks')
    get_tasks_parser.add_argument('--page', type=int, default=1, help='Page number')
    get_tasks_parser.add_argument('--output', '-o', help='Save to file')
    get_tasks_parser.set_defaults(func=cmd_monitoring_get_tasks)
    
    # Delete task
    delete_task_parser = monitoring_subparsers.add_parser('delete-task', help='Delete monitoring task')
    delete_task_parser.add_argument('task_id', help='Task ID to delete')
    delete_task_parser.set_defaults(func=cmd_monitoring_delete_task)
    
    # WHOIS commands
    whois_parser = subparsers.add_parser('whois', help='WHOIS commands')
    whois_parser.add_argument('type', choices=['lookup', 'history', 'reverse', 'ip', 'mx', 'ns', 'subdomain'],
                              help='WHOIS operation type')
    whois_parser.add_argument('domain', nargs='?', help='Domain or IP address')
    whois_parser.add_argument('--name', help='Name for reverse WHOIS')
    whois_parser.add_argument('--organization', help='Organization for reverse WHOIS')
    whois_parser.add_argument('--email', help='Email for reverse WHOIS')
    whois_parser.add_argument('--output', '-o', help='Save to file')
    whois_parser.set_defaults(func=cmd_whois)
    
    # Balance command
    balance_parser = subparsers.add_parser('balance', help='Check account balance')
    balance_parser.set_defaults(func=cmd_balance)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except DeHashedAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except AttributeError:
        parser.print_help()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted by user")
        sys.exit(130)


if __name__ == '__main__':
    main()

