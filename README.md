# DeHashed API Python Client

A comprehensive Python client for interacting with the DeHashed API v2.

## Features

This client provides full access to all DeHashed API endpoints:

### 🔍 Search API
- **General Search**: Search across all compromised data
- **Password Search**: Search by password hash (FREE - no credits required)

### 📊 Monitoring API
- **Tasks Management**: Create, update, delete, and retrieve monitoring tasks
- **Reports**: Access monitoring reports and alerts
- **Notification Channels**: Configure webhook and email notifications

### 🌐 WHOIS API
- **Domain Lookup**: Get WHOIS information for domains
- **WHOIS History**: View historical WHOIS records
- **Reverse WHOIS**: Find domains by registrant details
- **IP/MX/NS Lookups**: Reverse lookups for infrastructure
- **Subdomain Scanning**: Discover subdomains

## Installation

1. Install the required dependency:
```bash
pip install -r dehashed_requirements.txt
```

Or manually:
```bash
pip install requests
```

2. Set up your API key as an environment variable:
```bash
export DEHASHED_API_KEY='your-api-key-here'
```

## Quick Start

### Basic Usage

```python
from dehashed_api import DeHashedClient

# Initialize client (uses DEHASHED_API_KEY environment variable)
client = DeHashedClient()

# Or pass API key directly
client = DeHashedClient(api_key="your-api-key-here")

# Perform a search
results = client.search("email:user@example.com")
print(results)

# Clean up
client.close()
```

### Using Context Manager (Recommended)

```python
from dehashed_api import DeHashedClient

with DeHashedClient() as client:
    results = client.search("domain:example.com")
    print(results)
# Session automatically closed
```

## API Methods

### Search Methods

#### `search(query, page=1, size=10000, wildcard=False, regex=False, de_dupe=False)`
Perform a general search query.

**Search Query Syntax:**
- `email:user@example.com` - Search by email
- `username:admin` - Search by username
- `password:password123` - Search by password
- `hash:5f4dcc3b...` - Search by password hash
- `ip_address:192.168.1.1` - Search by IP address
- `name:"John Doe"` - Search by name
- `vin:1HGBH41JXMN109186` - Search by VIN
- `address:"123 Main St"` - Search by address
- `phone:+1234567890` - Search by phone
- `domain:example.com` - Search by domain

**Examples:**
```python
# Basic email search
results = client.search("email:user@example.com")

# Username with wildcard
results = client.search("username:admin*", wildcard=True)

# Domain search with pagination
results = client.search("domain:example.com", page=2, size=100)

# Multiple criteria
results = client.search("email:user@example.com AND domain:example.com")

# Deduplicate results
results = client.search("password:password123", de_dupe=True)
```

#### `search_password(password_hash)`
Search for records by password hash. **FREE - no credits required!**

```python
# MD5 hash example
results = client.search_password("5f4dcc3b5aa765d61d8327deb882cf99")
```

### Monitoring Methods

#### Task Management

```python
# Create a monitoring task
task = client.monitoring_create_task(
    task_type="email",
    value="monitor@example.com",
    channels=["email", "webhook"]
)

# Update a task
updated = client.monitoring_update_task(
    task_id="task-123",
    task_type="email",
    value="newemail@example.com",
    channels=["email"]
)

# Enable/disable a task
client.monitoring_update_task_status("task-123", active=False)

# Delete a task
client.monitoring_delete_task("task-123")

# Get all tasks
tasks = client.monitoring_get_tasks(page=1)

# Get specific task
task = client.monitoring_get_task("task-123")
```

**Task Types:**
- `email` - Monitor email addresses
- `username` - Monitor usernames
- `phone` - Monitor phone numbers
- `ip_address` - Monitor IP addresses
- `address` - Monitor physical addresses
- `name` - Monitor names
- `vin` - Monitor VINs
- `domain` - Monitor domains
- `password` - Monitor passwords

#### Reports

```python
# Get all reports
reports = client.monitoring_get_reports(page=1)

# Get specific report
report = client.monitoring_get_report("report-123")
```

#### Notification Channels

```python
# Get configured channels
channels = client.monitoring_get_channels()

# Configure webhook
client.monitoring_update_channel(
    channel_type="webhook",
    value="https://example.com/webhook"
)

# Configure email
client.monitoring_update_channel(
    channel_type="email",
    value="alerts@example.com"
)

# Delete a channel
client.monitoring_delete_channel("webhook")
```

### WHOIS Methods

```python
# Standard WHOIS lookup
info = client.whois_search("example.com")

# WHOIS history
history = client.whois_history("example.com")

# Reverse WHOIS by email
domains = client.whois_reverse(email="admin@example.com")

# Reverse WHOIS by organization
domains = client.whois_reverse(organization="Example Corp")

# Reverse WHOIS with filters
domains = client.whois_reverse(
    name="John Doe",
    include=["example", "test"],
    exclude=["spam"]
)

# IP WHOIS lookup
info = client.whois_ip("8.8.8.8")

# Find domains using MX server
domains = client.whois_mx("mail.example.com")

# Find domains using nameserver
domains = client.whois_ns("ns1.example.com")

# Subdomain scanning
subdomains = client.whois_subdomain_scan("example.com")
```

### Utility Methods

```python
# Get account balance
balance = client.get_balance()
print(f"Credits remaining: {balance}")

# Pretty print results
from dehashed_api import pretty_print_results
pretty_print_results(results)

# Save results to JSON file
from dehashed_api import save_results_to_file
save_results_to_file(results, "output.json")

# Save results to CSV file (great for data analysis!)
from dehashed_api import save_results_to_csv
save_results_to_csv(results, "output.csv")
```

## Advanced Examples

### Comprehensive Search with Error Handling

```python
from dehashed_api import DeHashedClient, DeHashedAPIError

try:
    with DeHashedClient() as client:
        # Search for compromised credentials
        results = client.search("domain:example.com", size=100)
        
        if results.get('entries'):
            print(f"Found {len(results['entries'])} entries")
            for entry in results['entries']:
                print(f"Email: {entry.get('email')}")
                print(f"Username: {entry.get('username')}")
                print(f"Password: {entry.get('password')}")
                print("---")
        else:
            print("No results found")
            
        # Check balance
        balance = results.get('balance')
        print(f"Credits remaining: {balance}")
        
except DeHashedAPIError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Batch Monitoring Setup

```python
from dehashed_api import DeHashedClient

# List of emails to monitor
emails_to_monitor = [
    "user1@example.com",
    "user2@example.com",
    "user3@example.com"
]

with DeHashedClient() as client:
    # Set up notification webhook
    client.monitoring_update_channel(
        "webhook",
        "https://your-server.com/dehashed-webhook"
    )
    
    # Create monitoring tasks
    for email in emails_to_monitor:
        try:
            task = client.monitoring_create_task(
                task_type="email",
                value=email,
                channels=["webhook", "email"]
            )
            print(f"Created task for {email}: {task.get('id')}")
        except Exception as e:
            print(f"Failed to create task for {email}: {e}")
```

### Domain Intelligence Gathering

```python
from dehashed_api import DeHashedClient, save_results_to_file, save_results_to_csv

def gather_domain_intelligence(domain):
    """Gather comprehensive intelligence on a domain"""
    
    with DeHashedClient() as client:
        results = {}
        
        # 1. Get compromised credentials
        print(f"Searching for compromised credentials...")
        results['credentials'] = client.search(f"domain:{domain}")
        
        # 2. Get WHOIS information
        print(f"Fetching WHOIS data...")
        results['whois'] = client.whois_search(domain)
        
        # 3. Get WHOIS history
        print(f"Fetching WHOIS history...")
        results['whois_history'] = client.whois_history(domain)
        
        # 4. Scan for subdomains
        print(f"Scanning for subdomains...")
        results['subdomains'] = client.whois_subdomain_scan(domain)
        
        # Save all results to JSON
        save_results_to_file(results, f"{domain}_intelligence.json")
        
        # Save credentials to CSV for easy analysis
        if 'credentials' in results:
            save_results_to_csv(results['credentials'], f"{domain}_credentials.csv")
        
        print(f"Intelligence gathering complete for {domain}")
        
        return results

# Usage
intelligence = gather_domain_intelligence("example.com")
```

### Password Hash Checker

```python
from dehashed_api import DeHashedClient
import hashlib

def check_password_compromised(password):
    """Check if a password has been compromised"""
    
    # Calculate MD5 hash
    password_hash = hashlib.md5(password.encode()).hexdigest()
    
    with DeHashedClient() as client:
        results = client.search_password(password_hash)
        
        if results.get('entries'):
            print(f"⚠️  Password IS compromised!")
            print(f"Found in {len(results['entries'])} breach(es)")
            return True
        else:
            print(f"✅ Password not found in known breaches")
            return False

# Usage (remember: password hash search is FREE!)
check_password_compromised("password123")
```

## Response Format

### Search Response
```json
{
  "balance": 950,
  "entries": [
    {
      "id": "123abc",
      "email": "user@example.com",
      "username": "user123",
      "password": "password123",
      "hashed_password": "5f4dcc3b5aa765d61d8327deb882cf99",
      "name": "John Doe",
      "ip_address": "192.168.1.1",
      "database_name": "Example Breach 2023"
    }
  ],
  "total": 1,
  "took": 45
}
```

## Error Handling

```python
from dehashed_api import DeHashedClient, DeHashedAPIError

try:
    with DeHashedClient() as client:
        results = client.search("email:test@test.com")
except DeHashedAPIError as e:
    print(f"API Error: {e}")
    # Handle API-specific errors (auth, rate limits, etc.)
except Exception as e:
    print(f"General Error: {e}")
    # Handle other errors
```

## Command Line Interface (CLI)

The package includes a powerful command-line interface for quick searches:

### Basic CLI Usage

```bash
# Simple search
python3 dehashed_cli.py search "domain:example.com"

# Save results to CSV
python3 dehashed_cli.py search "domain:example.com" --output results.csv

# Fetch all results automatically (handles pagination)
python3 dehashed_cli.py search "domain:example.com" --output results.csv --fetch-all

# Search with wildcard
python3 dehashed_cli.py search "username:admin*" --wildcard

# Check balance
python3 dehashed_cli.py balance
```

### Automatic Pagination with --fetch-all

When dealing with large datasets, the API returns results in pages (max 10,000 per page). The `--fetch-all` flag automatically handles pagination:

```bash
# Without --fetch-all: Gets only first 10,000 results
python3 dehashed_cli.py search "domain:large-company.com" --output results.csv

# With --fetch-all: Automatically fetches ALL results across multiple pages
python3 dehashed_cli.py search "domain:large-company.com" --output results.csv --fetch-all
```

**Example output:**
```
Total results: 25000
Fetching all pages (page size: 10000)...
Fetching page 2/3...
Fetching page 3/3...
Fetched 25000 total entries
Results saved to results.csv
Total entries exported: 25000
```

**Important Notes:**
- Each page consumes API credits, so be aware of your usage when using `--fetch-all` on large datasets.
- **API Hard Limit**: The DeHashed API has a maximum limit of 10,000 results that can be retrieved per query. If your search returns more than 10,000 results, only the first 10,000 can be fetched. The CLI will warn you about this and retrieve the maximum available. 
- **No Workaround**: Due to API query format limitations (you cannot combine multiple search fields like `domain:X AND email:Y*`), there is no programmatic workaround to retrieve more than 10,000 results for a single broad query. You would need to manually run multiple separate, narrower queries.

### CLI Help

```bash
# General help
python3 dehashed_cli.py --help

# Command-specific help
python3 dehashed_cli.py search --help
python3 dehashed_cli.py whois --help
```

## Best Practices

1. **Use Environment Variables**: Store your API key in the `DEHASHED_API_KEY` environment variable
2. **Use Context Managers**: Use `with` statement to ensure proper cleanup
3. **Handle Errors**: Always wrap API calls in try-except blocks
4. **Know the 10K Limit**: DeHashed API has a hard limit of 10,000 results per query. Narrow your searches if you need more data
5. **Pagination**: For large result sets (up to 10K), use the `--fetch-all` flag in CLI or implement manual pagination in Python
6. **Monitor Credits**: Large queries with `--fetch-all` can consume multiple pages of credits - check your balance first
7. **Free Password Search**: Use `search_password()` for password hash lookups (it's free!)
8. **Narrow Broad Searches**: If your query returns >10K results, use more specific filters (wildcards, usernames, etc.)
9. **Monitor Responsibly**: Only monitor assets you own or have permission to monitor
10. **Rate Limiting**: Respect API rate limits and implement backoff strategies
11. **Export to CSV**: Use CSV format for easy analysis in Excel, Google Sheets, or data analysis tools

## Environment Setup

### Linux/macOS
```bash
export DEHASHED_API_KEY='your-api-key-here'
```

Add to `~/.bashrc` or `~/.zshrc` for persistence:
```bash
echo "export DEHASHED_API_KEY='your-api-key-here'" >> ~/.bashrc
source ~/.bashrc
```

### Windows (PowerShell)
```powershell
$env:DEHASHED_API_KEY = "your-api-key-here"
```

For persistence, add to PowerShell profile.

### Windows (CMD)
```cmd
set DEHASHED_API_KEY=your-api-key-here
```

## Running the Examples

Run the built-in examples:
```bash
python dehashed_api.py
```

## API Documentation

For full API documentation, visit: https://www.dehashed.com/docs

## License

This client is provided as-is for use with the DeHashed API. Make sure you comply with DeHashed's Terms of Service and applicable laws when using this tool.

## Support

For API-related issues, contact DeHashed support.
For client-related issues, refer to the code comments and examples.

## Security Notes

- Never commit your API key to version control
- Use environment variables for sensitive data
- Implement proper access controls when deploying
- Follow responsible disclosure practices for any discovered vulnerabilities

## Contributing

Feel free to extend this client with additional functionality or improvements!

