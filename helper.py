from fidelityAPI import FidelityAutomation
import os
import re

def print_menu():
    """Prints the main menu with categories"""
    print("\n" + "="*60)
    print("                     FIDELITY AUTOMATION MENU")
    print("="*60 + "\n")
    print("1. Account Management")
    print("2. Transfer Operations")
    print("3. Trading Operations")
    print("4. Account Information")
    print("5. Quick Actions")
    print("6. Pause Browser")  # Added pause option
    print("7. Exit")
    print("Enter a number to select category: ", end="")


def print_account_management():
    """Prints account management submenu"""
    print("\n" + "-"*40)
    print("ACCOUNT MANAGEMENT")
    print("-"*40)
    print("1. Create New Account")
    print("2. Nickname Account")
    print("3. Enable Penny Stock Trading")
    print("4. Enable All Penny Stock Trading")  # Added new option
    print("5. Back to Main Menu")
    print("Enter a number to select category: ", end="")

def print_transfer_menu():
    """Prints transfer operations submenu"""
    print("\n" + "-"*40)
    print("TRANSFER OPERATIONS")
    print("-"*40)
    print("1. Transfer Between Accounts")
    print("2. Transfer from Source to All Accounts")
    print("3. Transfer from All Accounts to Source")  # Added new option
    print("4. Back to Main Menu")
    print("Enter a number to select category: ", end="")

def print_trading_menu():
    """Prints trading operations submenu"""
    print("\n" + "-"*40)
    print("TRADING OPERATIONS")
    print("-"*40)
    print("1. Buy Stock")
    print("2. Sell Stock")
    print("3. Buy/Sell in All Accounts")
    print("4. Back to Main Menu")
    print("Enter a number to select category: ", end="")

def print_account_info():
    """Prints account information submenu"""
    print("\n" + "-"*40)
    print("ACCOUNT INFORMATION")
    print("-"*40)
    print("1. List Account Positions")
    print("2. Get List of Accounts")
    print("3. Back to Main Menu")
    print("Enter a number to select category: ", end="")

def print_quick_actions():
    """Prints quick actions submenu"""
    print("\n" + "-"*40)
    print("QUICK ACTIONS")
    print("-"*40)
    print("1. The Big Three (Roth)")
    print("2. The Big Three (Brokerage)")
    print("3. Back to Main Menu")
    print("Enter a number to select category: ", end="")


def get_source_account():
    """Get source account from environment variables"""
    if os.getenv("FIDELITY"):
        creds = os.environ["FIDELITY"].strip().split(",")[0].split(":")  
        return creds[3] if len(creds) > 3 else None
    return None

def execute_bulk_transaction(browser: FidelityAutomation, action: str, stock: str, quantity: float) -> bool:
    """
        Execute buy/sell transactions across all eligible accounts.
        
        Parameters
        ----------
        browser : FidelityAutomation
            The browser instance
        action : str
            'buy' or 'sell'
        stock : str
            Stock symbol to trade
        quantity : float
            Quantity to trade per account
            
        Returns
        -------
        bool
            True if all transactions were successful
    """
    # Get list of accounts first
    accounts = browser.get_list_of_accounts()
    if not accounts:
        print("No accounts found")
        return False
        
    success_count = 0
    fail_count = 0
    
    # Show summary before executing
    print(f"\nExecuting {action.upper()} orders:")
    print(f"Stock: {stock}")
    print(f"Quantity per account: {quantity}")
    print("\nProcessing accounts:")
    
    # Process each account
    for acc_num, acc_info in accounts.items():
        print(f"\nAccount {acc_num} ({acc_info['nickname']}):")
        success, error = browser.transaction(
            stock=stock,
            quantity=quantity,
            action=action,
            account=acc_num,
            dry=False
        )
        
        if success:
            print(f"✓ Success")
            success_count += 1
        else:
            print(f"✗ Failed: {error}")
            fail_count += 1
    
    # Print summary
    print(f"\nTransaction Summary:")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    
    return fail_count == 0

def get_user_actions(action_list: list = None)  -> list:
  
    """
    Prints the menu options and records the sequence of choices in a list.
    If a list is provided, it will append to that list.

    Returns
    -------
    action_list (list)
        List of choices from the user
    """

    if action_list is None:
        action_list = []

    # Get source account once at the start
    source_account = get_source_account()
    if source_account:
        print(f"\nUsing source account: {source_account}")

    while True:
        print_menu()
        main_choice = input().strip()

        if main_choice == '1':  # Account Management
            while True:
                print_account_management()
                sub_choice = input().strip()
                
                if sub_choice == '1':  # Create New Account
                    account_type = input("\nEnter account type (roth/brokerage): ").lower()
                    if account_type in ['roth', 'brokerage']:
                        action_list.extend(['1', account_type])
                        return action_list
                
                elif sub_choice == '2':  # Nickname Account
                    account_num = input("\nEnter account number: ")
                    nickname = input("Enter new nickname: ")
                    action_list.extend(['6', account_num, nickname])
                    return action_list
                
                elif sub_choice == '3':  # Enable Penny Stock
                    account = input("\nEnter account number: ")
                    action_list.extend(['3', account])
                    return action_list
                
                elif sub_choice == '4':  # Enable All Penny Stock   
                    action_list.extend(['enable_all'])
                    return action_list
                
                elif sub_choice == '5':  # Back
                    break

        elif main_choice == '2':  # Transfer Operations
            while True:
                print_transfer_menu()
                sub_choice = input().strip()
                
                if sub_choice == '1':  # Transfer Between Accounts

                    # # Call the function directly, passing the browser instance
                    # accounts = browser.print_account_list()
                    # if not accounts:
                    #     continue

                    if source_account:
                        source = source_account
                    else:
                        source = input("\nEnter source account: ")
                    dest = input("Enter destination account: ")
                    try:
                        amount = float(input("Enter transfer amount: $"))
                        if amount <= 0:
                            print("Amount must be greater than 0")
                            continue
                        action_list.extend(['2', source, dest, str(amount)])
                        return action_list
                    except ValueError:
                        print("Please enter a valid number")
                
                elif sub_choice == '2':  # Transfer from Source to All
                    if source_account:
                        source = source_account
                    else:
                        source = input("\nEnter source account: ")
                    try:
                        amount = float(input("Enter amount per account: $"))
                        if amount <= 0:
                            print("Amount must be greater than 0")
                            continue
                        confirm = input(f"\nConfirm transfer of ${amount} from each eligible account to {source}? (y/n): ")
                        if confirm.lower() == 'y':
                            action_list.extend(['source_to_all', source, str(amount)])
                            return action_list
                    except ValueError:
                        print("Please enter a valid number")
                
                # In get_user_actions(), modify the transfer section:
                elif sub_choice == '3':  # Transfer from All to Source
                    if source_account:
                        source = source_account
                    else:
                        source = input("\nEnter destination account: ")
                    try:
                        amount = float(input("Enter amount to transfer from each account: $"))
                        if amount <= 0:
                            print("Amount must be greater than 0")
                            continue
                        confirm = input(f"\nConfirm transfer of ${amount} from each eligible account to {source}? (y/n): ")
                        if confirm.lower() == 'y':
                            action_list.extend(['all_to_source', source, str(amount)])
                            return action_list
                    except ValueError:
                        print("Please enter a valid number")
                
                elif sub_choice == '4':  # Back
                    break

        elif main_choice == '3':  # Trading Operations
            action = input("\nEnter action (buy/sell): ").lower()
            if action not in ['buy', 'sell']:
                print("Invalid action. Please enter 'buy' or 'sell'")
                continue
            
            stock = input("Enter stock symbol: ").upper()
            try:
                quantity = float(input(f"Enter quantity to {action} per account: "))
                if quantity <= 0:
                    print("Quantity must be greater than 0")
                    continue
                
                confirm = input(f"\nConfirm bulk {action} of {quantity} shares of {stock} in all eligible accounts? (y/n): ")
                if confirm.lower() == 'y':
                    action_list.extend(['bulk_trade', action, stock, str(quantity)])
                    return action_list
            except ValueError:
                print("Please enter a valid number")


        elif main_choice == '4':  # Account Information
            while True:
                print_account_info()
                sub_choice = input().strip()
                
                if sub_choice == '1':  # List Positions
                    action_list.append('4')
                    return action_list
                
                elif sub_choice == '2':  # List Accounts
                    action_list.append('5')
                    return action_list
                
                elif sub_choice == '3':  # Back
                    break

        elif main_choice == '5':  # Quick Actions
            while True:
                print_quick_actions()
                sub_choice = input().strip()
                
                if sub_choice == '1':  # Big Three Roth
                    action_list.append('123R')
                    return action_list
                
                elif sub_choice == '2':  # Big Three Brokerage
                    action_list.append('123B')
                    return action_list
                
                elif sub_choice == '3':  # Back
                    break

        elif main_choice == '6':  # Pause Browser
            action_list.append('pause')
            return action_list

        elif main_choice == '7':  # Exit
            action_list.append('7')
            return action_list
        
        else:
            print("\nInvalid option!!!")

def execute_user_action(action_list: list, browser: FidelityAutomation, index: int = 0) -> int:

    """
    Executes all actions in the action_list until a '6' is encountered.
    Increments index as it is used in the list.
    No validation of index and list is used. Ensure list ends with a '6'

    Returns
    -------
    index (int)
        The index of the next item in the list after the first '6' encountered
    """
        
    """Execute the user selected actions"""
    while index < len(action_list) and action_list[index] != '7':
        if action_list[index] == '1':  # Create new account
            browser.open_account(action_list[index + 1])
            index += 2
            
        elif action_list[index] == '2':  # Transfer between accounts
            browser.transfer_acc_to_acc(
                action_list[index + 1],
                action_list[index + 2],
                float(action_list[index + 3])
            )
            index += 4
            
        elif action_list[index] == '3':  # Enable penny stock
            browser.enable_pennystock_trading(action_list[index + 1])
            index += 2

        elif action_list[index] == 'enable_all':  # Enable all penny stock
            browser.enable_all_pennystock_trading()
            index += 1
            
        elif action_list[index] == '4':  # List positions
            browser.summary_holdings()
            index += 1
            
        elif action_list[index] == '5':  # List accounts
            browser.get_list_of_accounts()
            index += 1
            
        elif action_list[index] == '6':  # Nickname account
            browser.nickname_account(action_list[index + 1], action_list[index + 2])
            index += 3
            
        elif action_list[index] == 'source_to_all':  # Transfer from all accounts
            browser.transfer_from_source_to_all_acc(
                action_list[index + 1],  # source account
                float(action_list[index + 2])  # amount
            )
            index += 3

        elif action_list[index] == 'all_to_source':  # Transfer from all accounts to source
            browser.transfer_from_all_to_source(
                action_list[index + 1],  # destination account
                float(action_list[index + 2])  # amount
            )
            index += 3
            
        elif action_list[index] == 'bulk_trade':  # Bulk trading
            execute_bulk_transaction(
                browser=browser,
                action=action_list[index + 1],
                stock=action_list[index + 2],
                quantity=float(action_list[index + 3])
            )
            index += 4
            
        elif action_list[index] in ['123R', '123B']:  # Big Three
            # Determine account type
            acc_type = 'roth' if action_list[index] == '123R' else 'brokerage'
            regex_str = '^\d{9}$' if acc_type == 'roth' else 'Z\d{8}$'
            
            # Ask about transfer
            choice_xfr = input("Transfer money? (y/n)\n").lower()
            while choice_xfr not in ['y', 'n']:
                choice_xfr = input("Transfer money? (y/n)\n").lower()
            
            # Get transfer amount if needed
            transfer_amount = None
            if choice_xfr == 'y':
                while True:
                    try:
                        transfer_amount = float(input("How much to transfer?\n"))
                        break
                    except ValueError:
                        print("Please enter a valid number")
            
            # Get current accounts list if Roth
            if acc_type == 'roth':
                browser.get_list_of_accounts()
            
            # Open the account
            print(f"\nOpening new {acc_type} account...")
            if not browser.open_account(type=acc_type):
                print("Failed to open account")
                index += 1
                continue
            
            # Transfer money if requested
            if choice_xfr == 'y' and transfer_amount and transfer_amount > 0:
                print(f"\nTransferring ${transfer_amount} to new account...")
                browser.transfer_acc_to_acc(
                    source_account=browser.source_account,
                    destination_account=browser.new_account_number,
                    transfer_amount=transfer_amount
                )
            
            # Enable penny stock trading
            print("\nEnabling penny stock trading...")
            browser.enable_pennystock_trading(account=browser.new_account_number)
            
            # Nickname the account
            print("\nSetting account nickname...")
            counter = 0
            regular_name = None
            
            # Find highest numbered account of this type
            for key in browser.account_dict:
                # Check if account matches the type we just created
                match = re.search(regex_str, key)
                # Look for number in existing nicknames
                nickname_number = re.search('\d{1,}', str(browser.account_dict[key]['nickname']))
                
                if match and nickname_number:
                    # Update counter if we find a higher number
                    if counter <= int(nickname_number.group(0)):
                        counter = int(nickname_number.group(0)) + 1
                        # Get the base name (without number)
                        name_match = re.search('[^\d]+', browser.account_dict[key]['nickname'])
                        if name_match:
                            regular_name = name_match.group(0)
            
            # Set the nickname
            if regular_name is not None:
                new_nickname = regular_name + str(counter)
                browser.nickname_account(
                    account_number=browser.new_account_number,
                    nickname=new_nickname
                )
                print(f"Account nicknamed as: {new_nickname}")
            
            print("\nBig three process completed!")
            index += 1
    
        elif action_list[index] == 'pause':
            print("\nBrowser paused. Press Enter in the browser's debug console to continue...")
            browser.page.pause()
            index += 1
        
        else:
            index += 1
            
    return index
