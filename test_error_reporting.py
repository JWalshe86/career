from google.cloud import error_reporting
import traceback

# Initialize the client with the path to your service account key
client = error_reporting.Client.from_service_account_json('service-account-file.json')

def simulate_error():
    """Function to simulate an error and report it."""
    try:
        # Simulate an error
        raise ValueError("This is a simulated test error for Google Cloud Error Reporting.")
    except Exception as e:
        # Report the exception to Google Cloud Error Reporting
        client.report_exception()
        print("Error reported to Google Cloud Error Reporting.")

def main():
    """Main function to run the test."""
    print("Running error reporting test...")
    simulate_error()
    print("Test completed.")

if __name__ == "__main__":
    main()

