import dns.resolver
import os

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Try to find the hosts file in common locations
POSSIBLE_HOSTS_PATHS = [
    os.path.join(SCRIPT_DIR, 'hosts'),
    os.path.join(SCRIPT_DIR, '..', 'hosts'),
    os.path.join(SCRIPT_DIR, '..', 'systemless-fcm-hosts', 'hosts')
]
HOSTS_FILE_PATH = None
for path in POSSIBLE_HOSTS_PATHS:
    if os.path.exists(path):
        HOSTS_FILE_PATH = path
        break

DNS_SERVER = '8.8.8.8'

def get_domains_from_hosts(file_path):
    """
    Reads the hosts file and extracts a list of domains.
    Assumes the format: IP_ADDRESS DOMAIN
    """
    domains = []
    if not file_path or not os.path.exists(file_path):
        print(f"Error: hosts file not found. Searched in: {POSSIBLE_HOSTS_PATHS}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                # The second part is the domain
                domains.append(parts[1])
    return domains

def resolve_domain(domain):
    """
    Resolves the domain to an A record (IPv4) using the specified DNS server.
    """
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [DNS_SERVER]
    
    try:
        answers = resolver.resolve(domain, 'A')
        # Return the first IP found
        for rdata in answers:
            return rdata.to_text()
    except Exception as e:
        print(f"Error resolving {domain}: {e}")
        return None

def main():
    if not HOSTS_FILE_PATH:
        print(f"Error: Could not find hosts file in any of the expected locations: {POSSIBLE_HOSTS_PATHS}")
        return

    print(f"Reading domains from {HOSTS_FILE_PATH}...")
    domains = get_domains_from_hosts(HOSTS_FILE_PATH)
    
    if not domains:
        print("No domains found or file is empty.")
        return

    print(f"Found {len(domains)} domains. Resolving using {DNS_SERVER}...")
    
    new_hosts_content = []
    
    for domain in domains:
        ip = resolve_domain(domain)
        if ip:
            print(f"Resolved: {domain} -> {ip}")
            # Align output for readability (similar to original file)
            new_hosts_content.append(f"{ip:<15} {domain}")
        else:
            print(f"Failed to resolve: {domain}")
            # Keep the domain but maybe comment it out or leave a placeholder? 
            # For now, let's skip or we could read the original IP.
            # But the goal is to update, so if it fails, maybe we shouldn't output a broken line.
            # Let's just print a warning for now and not include it, or include it with a comment.
            new_hosts_content.append(f"# Failed to resolve: {domain}")

    # Output the result
    print("\n--- New Hosts Content ---\n")
    print("\n".join(new_hosts_content))
    
    # Save to hosts.txt
    output_file = os.path.join(SCRIPT_DIR, 'hosts.txt')
    with open(output_file, 'w', newline='\n', encoding='utf-8') as f:
        f.write("\n".join(new_hosts_content) + "\n")
    print(f"\nSaved to {output_file}")

if __name__ == "__main__":
    main()
