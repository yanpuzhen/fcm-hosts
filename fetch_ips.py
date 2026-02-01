import dns.resolver
import os
import sys
import socket

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

DNS_SERVERS = [
    '8.8.8.8',      # Google
    '1.1.1.1',      # Cloudflare
    '223.5.5.5',    # AliDNS
    '119.29.29.29'  # DNSPod
]

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

def check_connectivity(ip, port=443, timeout=3):
    """
    Checks if a TCP connection can be established to the IP on the specified port.
    Returns True if successful, False otherwise.
    """
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False

def resolve_domain(domain):
    """
    Resolves the domain to A records (IPv4) using multiple DNS servers and checks for connectivity.
    Returns the first working IP found.
    """
    candidate_ips = []
    seen_ips = set()

    for dns_server in DNS_SERVERS:
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            # Set a short timeout for DNS queries to speed up the process
            resolver.lifetime = 2
            resolver.timeout = 2
            
            answers = resolver.resolve(domain, 'A')
            for rdata in answers:
                ip = rdata.to_text()
                if ip not in seen_ips:
                    candidate_ips.append(ip)
                    seen_ips.add(ip)
        except Exception:
            # Ignore errors from individual DNS servers (timeout, nxdomain, etc.)
            continue
    
    if not candidate_ips:
        print(f"Warning: No IPs found for {domain} from any DNS server.")
        return None

    # Check connectivity for candidates
    for ip in candidate_ips:
        if check_connectivity(ip):
            print(f"  [+] Working IP for {domain}: {ip}")
            return ip
        else:
            print(f"  [-] IP {ip} failed connectivity check.")
            
    print(f"Warning: No IPs for {domain} passed connectivity check (tried {len(candidate_ips)} candidates).")
    return None

def main():
    if not HOSTS_FILE_PATH:
        print(f"Error: Could not find hosts file in any of the expected locations: {POSSIBLE_HOSTS_PATHS}")
        sys.exit(1)

    print(f"Reading domains from {HOSTS_FILE_PATH}...")
    domains = get_domains_from_hosts(HOSTS_FILE_PATH)
    
    if not domains:
        print("No domains found or file is empty.")
        sys.exit(1)

    print(f"Found {len(domains)} domains. Resolving using multiple DNS servers: {DNS_SERVERS}...")
    
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
