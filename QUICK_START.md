# DeHashed API - Quick Start Guide

## 📦 Installation

```bash
cd /Users/slouissaint/tools
pip install -r dehashed_requirements.txt
```

## 🔑 Set Your API Key

### macOS/Linux:
```bash
export DEHASHED_API_KEY='your-api-key-here'
```

### Make it permanent (add to ~/.zshrc or ~/.bashrc):
```bash
echo "export DEHASHED_API_KEY='your-api-key-here'" >> ~/.zshrc
source ~/.zshrc
```

## 🚀 Quick Usage Examples

### Using the Python Library

```python
from dehashed_api import DeHashedClient, save_results_to_csv, save_results_to_file

# Initialize and search
with DeHashedClient() as client:
    # Search for compromised emails
    results = client.search("email:user@example.com")
    print(results)
    
    # Save results to CSV for easy analysis
    results = client.search("domain:example.com")
    save_results_to_csv(results, "results.csv")
    
    # Save results to JSON
    save_results_to_file(results, "results.json")
    
    # Check password hash (FREE!)
    results = client.search_password("5f4dcc3b5aa765d61d8327deb882cf99")
    
    # WHOIS lookup
    whois = client.whois_search("example.com")
    
    # Create monitoring task
    task = client.monitoring_create_task("email", "monitor@example.com", ["email"])
```

### Using the Command Line Interface

```bash
# Email search
python dehashed_cli.py search "email:user@example.com"

# Username search
python dehashed_cli.py search "username:admin"

# Phone search
python dehashed_cli.py search "phone:+1234567890"

# Domain search
python dehashed_cli.py search "domain:example.com"

# IP address search
python dehashed_cli.py search "ip_address:192.168.1.1"

# Name search
python dehashed_cli.py search "name:John Doe"

# VIN search
python dehashed_cli.py search "vin:1HGBH41JXMN109186"

# Address search
python dehashed_cli.py search "address:123 Main St"

# Company search
python dehashed_cli.py search "company:Acme Corp"

# Social media search
python dehashed_cli.py search "social:username123"

# Password search
python dehashed_cli.py search "password:password123"

# Cryptocurrency address
python dehashed_cli.py search "cryptocurrency_address:0xabc..."

# URL search
python dehashed_cli.py search "url:example.com"

# Combined searches
python dehashed_cli.py search "email:admin@example.com AND domain:example.com"

# With wildcard
python dehashed_cli.py search "username:admin*" --wildcard

# With deduplication
python dehashed_cli.py search "password:password123" --dedupe

# Save to JSON file
python dehashed_cli.py search "domain:example.com" --output results.json

# Save to CSV file for easy analysis in Excel/Google Sheets
python dehashed_cli.py search "domain:example.com" --output results.csv

# Fetch ALL results automatically (handles pagination)
python dehashed_cli.py search "domain:example.com" --output results.csv --fetch-all

# Explicitly specify output format
python dehashed_cli.py search "email:admin@example.com" --output data.txt --format csv

# Search with options
python dehashed_cli.py search "username:admin*" --wildcard --output results.json

# Check password hash (FREE!)
python dehashed_cli.py search-password 5f4dcc3b5aa765d61d8327deb882cf99

# Create monitoring task
python dehashed_cli.py monitoring create-task email monitor@example.com --channels email,webhook

# View monitoring tasks
python dehashed_cli.py monitoring get-tasks

# WHOIS lookup
python dehashed_cli.py whois lookup example.com

# Reverse WHOIS
python dehashed_cli.py whois reverse --email admin@example.com

# Subdomain scan
python dehashed_cli.py whois subdomain example.com

# Check account balance
python dehashed_cli.py balance
```

## 📄 Handling Large Result Sets (Pagination)

By default, the DeHashed API returns a maximum of 10,000 results per page. If your search has more results, you need to handle pagination.

### Automatic Pagination (CLI)

The easiest way is to use the `--fetch-all` flag:

```bash
# This will automatically fetch ALL pages of results
python dehashed_cli.py search "domain:large-company.com" --output results.csv --fetch-all
```

**What happens:**
- Makes initial request to check total results
- Calculates how many pages are needed
- Automatically fetches each page
- Combines all results into one file
- Shows progress for each page

**Example output:**
```
Total results: 35000
Fetching all pages (page size: 10000)...
Fetching page 2/4...
Fetching page 3/4...
Fetching page 4/4...
Fetched 35000 total entries
Results saved to results.csv
Total entries exported: 35000
```

### Manual Pagination (Python Library)

If you're using the Python library directly:

```python
from dehashed_api import DeHashedClient

with DeHashedClient() as client:
    all_entries = []
    page = 1
    
    while True:
        results = client.search("domain:example.com", page=page, size=10000)
        entries = results.get('entries', [])
        
        if not entries:
            break
            
        all_entries.extend(entries)
        print(f"Fetched page {page}, total so far: {len(all_entries)}")
        
        # Check if we got all results
        if len(all_entries) >= results.get('total', 0):
            break
            
        page += 1
    
    print(f"Total entries: {len(all_entries)}")
```

### ⚠️ Important Warnings

**Credit Usage**: Each page of results consumes API credits. Always check your balance first:

```bash
python dehashed_cli.py balance
```

**API Hard Limit**: The DeHashed API has a **maximum limit of 10,000 results** per query. If your search returns more than 10,000 results, you can only retrieve the first 10,000. The `--fetch-all` flag will warn you about this limitation.

**Example with limit:**
```bash
$ python dehashed_cli.py search "domain:large-company.com" --output results.csv --fetch-all

Total results: 15000

⚠️  WARNING: DeHashed API has a maximum pagination limit of 10,000 results.
   Your query has 15000 results, but only the first 10,000 can be retrieved.
   Consider narrowing your search query to get more specific results.

Fetching all pages (page size: 10000)...
Fetched 10000 total entries
Results saved to results.csv
```

**To get more results, narrow your search:**
```bash
# Instead of broad search:
python dehashed_cli.py search "domain:example.com"  # Might have >10k results

# Try more specific searches:
python dehashed_cli.py search "domain:example.com AND email:*admin*" --wildcard
python dehashed_cli.py search "domain:example.com AND username:john*" --wildcard
```

## 🎯 Common Use Cases

### 1. Check if Your Email is Compromised

```python
from dehashed_api import DeHashedClient

with DeHashedClient() as client:
    results = client.search("email:youremail@example.com")
    
    if results.get('entries'):
        print(f"⚠️  Found {len(results['entries'])} compromised records!")
        for entry in results['entries']:
            print(f"  - Database: {entry.get('database_name')}")
            print(f"  - Password: {entry.get('password')}")
    else:
        print("✅ No compromised records found")
```

### 2. Monitor Multiple Emails

```python
from dehashed_api import DeHashedClient

emails = ["user1@example.com", "user2@example.com"]

with DeHashedClient() as client:
    for email in emails:
        task = client.monitoring_create_task("email", email, ["email"])
        print(f"✅ Monitoring {email}")
```

### 3. Domain Intelligence Gathering

```python
from dehashed_api import DeHashedClient, save_results_to_file

with DeHashedClient() as client:
    domain = "example.com"
    
    # Get all info
    intel = {
        'credentials': client.search(f"domain:{domain}"),
        'whois': client.whois_search(domain),
        'subdomains': client.whois_subdomain_scan(domain)
    }
    
    save_results_to_file(intel, f"{domain}_intel.json")
    print(f"✅ Intelligence saved to {domain}_intel.json")
```

### 4. Bulk Password Hash Checking (FREE!)

```python
from dehashed_api import DeHashedClient
import hashlib

passwords_to_check = ["password123", "admin", "qwerty"]

with DeHashedClient() as client:
    for password in passwords_to_check:
        hash_value = hashlib.md5(password.encode()).hexdigest()
        results = client.search_password(hash_value)
        
        if results.get('entries'):
            print(f"⚠️  '{password}' is COMPROMISED!")
        else:
            print(f"✅ '{password}' not found in breaches")
```

## 📚 Available API Methods

### Search API
- `search()` - General search
- `search_password()` - Password hash search (FREE)

### Monitoring API
- `monitoring_create_task()` - Create monitoring task
- `monitoring_update_task()` - Update task
- `monitoring_update_task_status()` - Enable/disable task
- `monitoring_delete_task()` - Delete task
- `monitoring_get_tasks()` - List all tasks
- `monitoring_get_task()` - Get specific task
- `monitoring_get_reports()` - List reports
- `monitoring_get_report()` - Get specific report
- `monitoring_get_channels()` - List notification channels
- `monitoring_update_channel()` - Configure notifications
- `monitoring_delete_channel()` - Remove notification channel

### WHOIS API
- `whois_search()` - Domain WHOIS lookup
- `whois_history()` - Historical WHOIS data
- `whois_reverse()` - Reverse WHOIS by registrant
- `whois_ip()` - IP WHOIS lookup
- `whois_mx()` - Find domains by MX server
- `whois_ns()` - Find domains by nameserver
- `whois_subdomain_scan()` - Discover subdomains

### Utilities
- `get_balance()` - Check account credits
- `pretty_print_results()` - Format output
- `save_results_to_file()` - Export to JSON
- `save_results_to_csv()` - Export to CSV (great for Excel/data analysis!)

## 🔍 Search Query Syntax

```python
# Email search
client.search("email:user@example.com")

# Username search
client.search("username:admin")

# Domain search
client.search("domain:example.com")

# IP address
client.search("ip_address:192.168.1.1")

# Name
client.search('name:"John Doe"')

# Phone
client.search("phone:+1234567890")

# Combine queries
client.search("email:admin@example.com AND domain:example.com")

# Wildcard search
client.search("username:admin*", wildcard=True)

# Password search
client.search("password:password123")

# VIN search
client.search("vin:1HGBH41JXMN109186")
```

## 💡 Pro Tips

1. **Password searches are FREE** - Use `search_password()` as much as you want!
2. **Know the 10,000 limit** - DeHashed API limits each query to 10,000 results max. Narrow broad searches!
3. **Use automatic pagination** - Add `--fetch-all` flag to automatically get all available results (up to 10K)
4. **Monitor credits** - Large queries with `--fetch-all` can consume multiple pages worth of credits
5. **Enable deduplication** - Use `de_dupe=True` or `--dedupe` to remove duplicate entries
6. **Narrow broad searches** - Use wildcards and specific filters to work within the 10K limit
7. **Monitor proactively** - Set up monitoring tasks for important assets
8. **Save results** - Use `save_results_to_file()` for JSON or `save_results_to_csv()` for CSV format
9. **CSV for analysis** - Export to CSV for easy analysis in Excel, Google Sheets, or pandas
10. **Check balance first** - Run `python dehashed_cli.py balance` before large queries

## ⚠️ Important Notes

- Always store your API key securely
- Never commit API keys to version control
- Only monitor assets you own or have permission to monitor
- Respect rate limits and terms of service
- Use responsibly and ethically

## 📖 Full Documentation

For complete documentation, see: `DeHashed_README.md`

## 🆘 Help

```bash
# Get CLI help
python dehashed_cli.py --help

# Get command-specific help
python dehashed_cli.py search --help
python dehashed_cli.py whois --help
```

## 📝 Example Scripts Location

All files are in: `/Users/slouissaint/tools/`
- `dehashed_api.py` - Main Python library
- `dehashed_cli.py` - Command-line interface
- `dehashed_requirements.txt` - Dependencies
- `DeHashed_README.md` - Full documentation
- `QUICK_START.md` - This file

---

**Ready to start!** 🎉

Set your API key and try:
```bash
python dehashed_cli.py balance
```

