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
    
    # Generate a strong secret key
    secret_key = generate_secret_key()
    
    print(f"\nGenerated SECRET_KEY:")
    print(f"SECRET_KEY={secret_key}")
    
    print(f"\nLength: {len(secret_key)} characters")
    print("This key is cryptographically secure and suitable for production use.")
    
    print("\nUsage instructions:")
    print("1. Copy the SECRET_KEY value above (you can specify the desired length as an argument)")
    print("2. Add it to your .env file:")
    print("   SECRET_KEY=your_generated_key_here")
    print("3. Or set it as an environment variable:")
    print("   export SECRET_KEY='your_generated_key_here'")
    print("4. Make sure to keep this key secret and secure!")
    
    return secret_key

if __name__ == "__main__":
    main()
