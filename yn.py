import os
import subprocess
import argparse

def crack_passwords_with_wordlists(hash_file, wordlist_path, output_file, shell_info=False):
    wordlists = []

    # Check if the wordlist path is a file or a directory
    if os.path.isfile(wordlist_path):
        wordlists.append(wordlist_path)  # Add the single file to the list
    elif os.path.isdir(wordlist_path):
        # Recursively collect all wordlist files from the directory and subdirectories
        for root, dirs, files in os.walk(wordlist_path):
            for file in files:
                wordlists.append(os.path.join(root, file))
    else:
        print(f"[!] The path {wordlist_path} is neither a file nor a directory.")
        return

    cracked_passwords = set()  # To store unique cracked passwords

    for wordlist in wordlists:
        print(f"[*] Attempting to crack with wordlist: {wordlist}")

        # Command to run John the Ripper with a specific wordlist
        command = ["john", "--wordlist=" + wordlist, hash_file]

        # Run the command
        try:
            subprocess.run(command, check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"[!] Error cracking with wordlist {wordlist}: {e.stderr.decode()}")

    # Now read the cracked passwords from the John the Ripper output
    print("[*] Extracting cracked passwords...")
    command = ["john", "--show", hash_file]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        output_lines = result.stdout.splitlines()

        # Filter and format the output
        for line in output_lines:
            if ':' in line:  # Ensure the line contains a colon
                parts = line.split(':')
                
                # If shell_info is True, keep everything after the password
                if shell_info:
                    cracked_passwords.add(line.strip())
                # If shell_info is False, only keep {username}:{password}
                else:
                    if len(parts) >= 2:  # Ensure there are at least two parts (username and password)
                        username = parts[0]
                        password = parts[1]
                        cracked_passwords.add(f"{username}:{password}")

    except subprocess.CalledProcessError as e:
        print(f"[!] Error retrieving cracked passwords: {e.stderr.decode()}")

    # Write the cracked passwords to the output file
    with open(output_file, "w") as out_file:
        for entry in cracked_passwords:
            out_file.write(entry + "\n")  # Write each cracked password

    print(f"[*] Cracking complete. Cracked passwords saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate John the Ripper to crack MD5 hashes using a wordlist file or a directory of wordlists.")
    
    parser.add_argument("hash_file", help="Path to the file containing the MD5 hashes")
    parser.add_argument("wordlist_path", help="Path to the wordlist file or directory containing wordlists")
    parser.add_argument("output_file", help="Path to save the cracked passwords")
    parser.add_argument("--shell_info", action="store_true", help="Include extra shell information (e.g., home directory, shell) if present in the John the Ripper output")
    
    args = parser.parse_args()
    
    crack_passwords_with_wordlists(args.hash_file, args.wordlist_path, args.output_file, shell_info=args.shell_info)
