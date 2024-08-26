import os

def main():
    google_credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    print(f"GOOGLE_CREDENTIALS_JSON: {google_credentials_json}")

if __name__ == "__main__":
    main()

