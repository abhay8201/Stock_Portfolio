import yfinance as yf
import pandas as pd
import json
import os

# Portfolio file for persistence
PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    """Load portfolio data from a JSON file."""
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as file:
            return json.load(file)
    return {"stocks": {}, "total_balance": 0.0}

def save_portfolio(portfolio):
    """Save portfolio data to a JSON file."""
    with open(PORTFOLIO_FILE, "w") as file:
        json.dump(portfolio, file, indent=4)

def fetch_stock_data(stock_symbol):
    """Fetch detailed stock data using Yahoo Finance."""
    try:
        stock = yf.Ticker(stock_symbol)
        # Correct positional access using .iloc
        current_price = stock.history(period="1d")['Close'].iloc[-1]
        return current_price
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {e}")
        return None

def update_total_balance(portfolio):
    """Update the total balance of the portfolio."""
    total_balance = 0.0
    for stock, details in portfolio["stocks"].items():
        current_price = fetch_stock_data(stock)
        if current_price:
            total_balance += details["quantity"] * current_price
    portfolio["total_balance"] = round(total_balance, 2)

def add_stock(portfolio, symbol, quantity):
    """Add a stock to the portfolio."""
    symbol = symbol.upper()
    current_price = fetch_stock_data(symbol)
    
    if not current_price:
        print(f"Failed to fetch data for {symbol}. Stock not added.")
        return

    if symbol in portfolio["stocks"]:
        print(f"{symbol} already exists in your portfolio. Updating quantity.")
        portfolio["stocks"][symbol]['quantity'] += quantity
    else:
        portfolio["stocks"][symbol] = {"quantity": quantity, "purchase_price": current_price}

    print(f"Added {quantity} shares of {symbol} at the current price of ${round(current_price, 2)}.")
    update_total_balance(portfolio)
    save_portfolio(portfolio)

def remove_stock(portfolio, symbol):
    """Remove a stock from the portfolio."""
    symbol = symbol.upper()
    if symbol in portfolio["stocks"]:
        del portfolio["stocks"][symbol]
        print(f"Removed {symbol} from your portfolio.")
        update_total_balance(portfolio)
        save_portfolio(portfolio)
    else:
        print(f"{symbol} is not in your portfolio.")

def view_portfolio(portfolio):
    """View the current portfolio with detailed performance."""
    if not portfolio["stocks"]:
        print("Your portfolio is empty.")
        return

    data = []
    print("\nFetching real-time stock data...")
    for stock, details in portfolio["stocks"].items():
        quantity = details['quantity']
        purchase_price = details['purchase_price']

        current_price = fetch_stock_data(stock)
        if not current_price:
            continue

        current_value = quantity * current_price
        profit_loss = (current_price - purchase_price) * quantity
        profit_loss_percentage = ((current_price - purchase_price) / purchase_price) * 100

        data.append({
            'Stock': stock,
            'Quantity': quantity,
            'Purchase Price': round(purchase_price, 2),
            'Current Price': round(current_price, 2),
            'Current Value': round(current_value, 2),
            'Profit/Loss': round(profit_loss, 2),
            'Profit/Loss (%)': round(profit_loss_percentage, 2),
        })

    # Display the portfolio in a table format
    df = pd.DataFrame(data)
    print("\nPortfolio Performance:")
    print(df)
    print(f"\nTotal Portfolio Value: ${round(portfolio['total_balance'], 2)}")

    # Ask the user if they want to export the data
    export = input("\nDo you want to export the portfolio to a CSV file? (yes/no): ").strip().lower()
    if export == "yes":
        df.to_csv("portfolio_performance.csv", index=False)
        print("Portfolio exported to 'portfolio_performance.csv'.")

def main():
    portfolio = load_portfolio()

    while True:
        print("\nStock Portfolio Tracker")
        print("1. Add Stock")
        print("2. Remove Stock")
        print("3. View Portfolio")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            symbol = input("Enter the stock symbol (e.g., AAPL, MSFT): ").strip().upper()
            try:
                quantity = int(input("Enter the quantity: "))
                add_stock(portfolio, symbol, quantity)
            except ValueError:
                print("Invalid input. Please try again.")
        elif choice == "2":
            symbol = input("Enter the stock symbol to remove: ").strip().upper()
            remove_stock(portfolio, symbol)
        elif choice == "3":
            view_portfolio(portfolio)
        elif choice == "4":
            print("Exiting the tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
