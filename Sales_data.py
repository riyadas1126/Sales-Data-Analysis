import pandas as pd
import glob
import matplotlib.pyplot as plt
from itertools import combinations
from collections import Counter

# Combine all CSV files
path = './'  # Update to the correct path where files are stored
csv_files = glob.glob(path + "*.csv")
dataframes = [pd.read_csv(file) for file in csv_files]
combined_df = pd.concat(dataframes, ignore_index=True)
combined_df.to_csv('Combined_Sales_2019.csv', index=False)
print("All files combined into 'Combined_Sales_2019.csv'")

# Data Cleaning
combined_df = combined_df.dropna(how="all")  # Remove rows with all NaN values
combined_df = combined_df[~combined_df["Order Date"].str.startswith("Or", na=False)]  # Remove invalid rows

# Convert columns to proper data types
combined_df["Quantity Ordered"] = pd.to_numeric(combined_df["Quantity Ordered"], errors='coerce')
combined_df["Price Each"] = pd.to_numeric(combined_df["Price Each"], errors='coerce')
combined_df["Order Date"] = pd.to_datetime(combined_df["Order Date"], errors='coerce')
combined_df = combined_df.dropna()  # Drop remaining invalid rows

# Add "Month" and "Sales" columns
combined_df["Month"] = combined_df["Order Date"].dt.month
combined_df["Sales"] = combined_df["Quantity Ordered"] * combined_df["Price Each"]

# Add "City" column
def get_city(address):
    return address.split(',')[1].strip()

def get_state(address):
    return address.split(',')[2].split(" ")[1].strip()

combined_df["City"] = combined_df["Purchase Address"].apply(
    lambda x: f"{get_city(x)} ({get_state(x)})"
)

# Analysis and Visualizations

# Q1: Best Month for Sales
monthly_sales = combined_df.groupby("Month").sum()["Sales"]
plt.bar(monthly_sales.index, monthly_sales.values)
plt.xticks(range(1, 13))
plt.xlabel("Month")
plt.ylabel("Sales in USD ($)")
plt.title("Monthly Sales in 2019")
plt.show()

# Q2: City with the Highest Sales
city_sales = combined_df.groupby("City").sum()["Sales"]
plt.bar(city_sales.index, city_sales.values)
plt.xticks(city_sales.index, rotation='vertical', size=8)
plt.xlabel("City")
plt.ylabel("Sales in USD ($)")
plt.title("Sales by City")
plt.show()

# Q3: Optimal Advertising Time
combined_df["Hour"] = combined_df["Order Date"].dt.hour
hourly_sales = combined_df.groupby("Hour").count()["Order ID"]
plt.plot(hourly_sales.index, hourly_sales.values)
plt.xticks(hourly_sales.index)
plt.xlabel("Hour")
plt.ylabel("Number of Orders")
plt.title("Sales by Hour")
plt.grid()
plt.show()

# Q4: Products Most Often Sold Together
duplicated_orders = combined_df[combined_df["Order ID"].duplicated(keep=False)]
duplicated_orders["Grouped"] = duplicated_orders.groupby("Order ID")["Product"].transform(lambda x: ','.join(x))
grouped_products = duplicated_orders[["Order ID", "Grouped"]].drop_duplicates()

product_combinations = Counter()
for row in grouped_products["Grouped"]:
    product_list = row.split(',')
    product_combinations.update(Counter(combinations(product_list, 2)))

# Display the top 10 most common product combinations
for combo, count in product_combinations.most_common(10):
    print(f"{combo}: {count}")

# Q5: Most Sold Product and Pricing Insights
product_sales = combined_df.groupby("Product").sum()["Quantity Ordered"]
product_prices = combined_df.groupby("Product").mean()["Price Each"]

fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.bar(product_sales.index, product_sales.values, label="Quantity Ordered", color="blue")
ax1.set_xlabel("Products")
ax1.set_ylabel("Quantity Ordered", color="blue")
ax1.tick_params(axis='y', labelcolor="blue")
ax1.set_xticks(range(len(product_sales.index)))
ax1.set_xticklabels(product_sales.index, rotation='vertical', size=8)

ax2 = ax1.twinx()
ax2.plot(product_prices.index, product_prices.values, label="Price", color="red")
ax2.set_ylabel("Price ($)", color="red")
ax2.tick_params(axis='y', labelcolor="red")

plt.title("Quantity Ordered vs. Price of Products")
plt.tight_layout()
plt.show()
