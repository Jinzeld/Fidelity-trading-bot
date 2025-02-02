import sqlite3
import os
import csv
import re
from fidelityAPI import FidelityAutomation
from helper import *
from dotenv import load_dotenv


def main():
    """Main function to run the automation"""
    try:
        # Delete old variable in environment
        if os.getenv("FIDELITY"):
            os.environ.pop("FIDELITY")
            
        # Initialize .env file
        load_dotenv()
        
        # Import Fidelity account
        if not os.getenv("FIDELITY"):
            raise Exception("Fidelity credentials not found in .env file")

        accounts = os.environ["FIDELITY"].strip().split(",")
        
        # Check credentials format
        for account in accounts:
            creds = account.split(':')
            if len(creds) < 3:
                raise Exception("Error: Incomplete credentials. Format should be username:password:totp_secret")

        print("\nWelcome to Fidelity Automation!")
        
        for account in accounts:
            creds = account.split(':')
            # Print partial username for identification
            quarter = round(len(creds[0]) * 0.25) + 2
            print(f"\nProcessing account: {creds[0][:quarter]}...")

            # Initialize action list
            action_list = []
            
            while True:
                # Get user actions
                action_list = get_user_actions(action_list)
                
                if not action_list:
                    continue
                    
                # Initialize browser if we have actions to perform
                if action_list and action_list[-1] == '7':
                    print("\nExiting program...")
                    break
                
                if action_list:
                    try:
                        # Create browser instance
                        browser = FidelityAutomation(
                            headless=False,
                            save_state=False,
                        )
                        
                        # Login
                        step_1, step_2 = browser.login(
                            username=creds[0],
                            password=creds[1],
                            totp_secret=creds[2] if len(creds) > 2 else None,
                            save_device=False,
                        )
                        
                        if step_1 and step_2:
                            print(f"\nSuccessfully logged in as: {creds[0][:31]}...")
                            
                            # Execute the actions
                            execute_user_action(action_list, browser)
                            
                        else:
                            print("\nLogin failed!")
                            
                    except Exception as e:
                        print(f"\nError during execution: {str(e)}")
                        
                    finally:
                        # Always try to close the browser
                        try:
                            browser.close_browser()
                        except:
                            pass
                
                
            # Ask if user wants to continue to next account
            if len(accounts) > 1:
                cont = input("\nContinue to next account? (y/n): ")
                if cont.lower() != 'y':
                    break

        print("\nThank you for using Fidelity Automation!")

    except Exception as e:
        print(f"\nError: {str(e)}")
        return

if __name__ == "__main__":
    main()



