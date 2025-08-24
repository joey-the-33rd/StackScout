#!/usr/bin/env python3
"""
Script to generate a strong SECRET_KEY for StackScout authentication.
This key should be used as the SECRET_KEY environment variable.
"""

import secrets
import sys

def generate_secret_key(target_length=32):
    """Generate a cryptographically secure random secret key."""
    byte_length = (target_length * 3) // 4 + 1  # Calculate required byte length
    return secrets.token_urlsafe(byte_length)

def main():
    print("StackScout SECRET_KEY Generator")
    print("=" * 40)
    
    # Parse command line arguments for target length
    target_length = 32  # Default value
    if len(sys.argv) > 1 and sys.argv[1] != "--print":
        try:
            target_length = int(sys.argv[1])
            if target_length < 16:
                print("⚠️  Warning: For security, consider using a longer key (minimum 16 characters recommended)")
        except ValueError:
            print(f"⚠️  Warning: Invalid length argument '{sys.argv[1]}'. Using default length of 32 characters.")
    
    # Generate a strong secret key
    secret_key = generate_secret_key(target_length)
    
    show = "--print" in sys.argv
    if show:
        print(f"\nGenerated SECRET_KEY:")
        print(f"SECRET_KEY={secret_key}")
    else:
        print("\nGenerated a new SECRET_KEY (hidden). Use --print to display it.")
        print("To save directly to your shell (use at your own risk):")
        print("  eval \"$(python generate_secret_key.py --print | sed -n 's/^SECRET_KEY=\\(.*\\)$/export SECRET_KEY=\"\\1\"/p')\"")
    
    print(f"\nLength: {len(secret_key)} characters")
    print("This key is cryptographically secure and suitable for production use.")
    
    print("\nUsage instructions:")
    print("1. Run with --print to display the key then copy it securely.")
    print("2. Add it to your .env file or export it in your shell.")
    
    return secret_key

if __name__ == "__main__":
    main()
