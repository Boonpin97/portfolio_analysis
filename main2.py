import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

# File path to your CSV file
file_path = 'data.csv'

# Read the CSV file, skipping metadata rows
df = pd.read_csv(file_path, skiprows=3)
df = df.iloc[::-1]
df['Total (inclusive of fees and/or spread)'] = df['Total (inclusive of fees and/or spread)'].replace('[\$,]', '', regex=True).astype(float)
deposits_row = df[df['Transaction Type'].str.contains(r'^Deposit$', na=False)]
withdraw_row = df[df['Transaction Type'].str.contains(r'^Withdrawal$', na=False)]
funding_row = df[df['Transaction Type'].str.contains(r'^Funding Fees \(24 Hours\)$', case=False, na=False)]
print(deposits_row)
print(withdraw_row)
print(funding_row)
total_deposit = deposits_row['Quantity Transacted'].sum()
total_withdraw = withdraw_row['Quantity Transacted'].sum()
total_base = total_deposit + total_withdraw
total_funding = funding_row['Total (inclusive of fees and/or spread)'].replace('[\$,]', '', regex=True).astype(float).sum()
print(f"Deposited: {total_deposit}")
print(f"Withdrew: {total_withdraw}")
print(f"Base: {total_base}")
print(f"Funding: {total_funding}")

print(df['Total (inclusive of fees and/or spread)'])
df = df.drop(columns=['ID', 'Asset', 'Price Currency','Fees and/or Spread','Notes'])
df = df[~df['Transaction Type'].str.contains(r'Buy|Sell|Advance Trade Buy|Advance Trade Sell|Deposit|Withdrawal|Perpetual Futures Buy|Perpetual Futures Sell|Send|Receive|Funding Fee|Reward Income', case=False, na=False)] 
#df = df[~df['Transaction Type'].str.contains(r'Deposit|Withdrawal|Perpetual Futures Buy|Perpetual Futures Sell|Send|Receive|Convert', case=False, na=False)] 

# Initialize the Price column with NaN
df['Price'] = np.nan

# Conditionally update Price column without overwriting existing values
conditions = [
    # (df['Transaction Type'].str.contains(r'Buy', case=False, na=False)),
    # (df['Transaction Type'].str.contains(r'Sell', case=False, na=False)),
    # (df['Transaction Type'].str.contains(r'Advanced Trade Buy', case=False, na=False)),
    # (df['Transaction Type'].str.contains(r'Advanced Trade Sell', case=False, na=False)),
    (df['Transaction Type'].str.contains(r'Settlements of unrealized P/L \(24 Hours\)', case=False, na=False)),
    (df['Transaction Type'].str.contains(r'Funding Fees \(24 Hours\)', case=False, na=False))
]

values = [
    # -df['Total (inclusive of fees and/or spread)'],       # Buy
    # df['Total (inclusive of fees and/or spread)'],      # Sell
    # -df['Total (inclusive of fees and/or spread)'],       # Advanced Trade Buy
    # df['Total (inclusive of fees and/or spread)'],      # Advanced Trade Sell
    df['Total (inclusive of fees and/or spread)'],       # Settlements of unrealized P/L
    df['Total (inclusive of fees and/or spread)']        # Funding Fees
]

for condition, value in zip(conditions, values):
    df.loc[df['Price'].isna() & condition, 'Price'] = value
df['Cumulative Sum'] = df['Price'].cumsum()
print(df[['Transaction Type','Price']])
df.to_csv('output.csv', index=False)  # Exports without the index column


plt.figure(figsize=(12, 8))
plt.plot(df['Timestamp'], df['Cumulative Sum'] + total_base, marker='o', linestyle='-', label='Cumulative Total')
# index_series = range(len(df))
# plt.plot(index_series, df['Cumulative Sum']+total_base, marker='o', linestyle='--', label='pl_funding')

# Formatting the plot
plt.title('Net Perpetual Futures P/L Settlements vs Timestamp (GMT+8)', fontsize=8)
plt.xlabel('Timestamp (GMT+8)\n', fontsize=10)
plt.ylabel('P/L Settlements (Total)', fontsize=10)
plt.xticks(fontsize=10, rotation=45)
plt.yticks(fontsize=10, rotation=45)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=20))

plt.figtext(0.5, 0.01, f"Deposited:{total_deposit} | Withdrew:{total_withdraw} | Base:{total_base} | Funding:{total_funding}", wrap=True, horizontalalignment='center', fontsize=10)
manager = plt.get_current_fig_manager()
manager.full_screen_toggle()
#Show the plot
plt.show()
