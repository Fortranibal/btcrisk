import json
import time
import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import statistics
import matplotlib.pyplot as plt
from tabulate import tabulate

FOLDER_NAME = 'blockware'
os.makedirs(FOLDER_NAME, exist_ok=True)

DATA_FILE = os.path.join(FOLDER_NAME, 'blockware_miners.json')
CSV_FILE = os.path.join(FOLDER_NAME, 'blockware_miners.csv')
LOG_FILE = os.path.join(FOLDER_NAME, 'last_fetch_log.json')

def scrape_marketplace():
    base_url = "https://marketplace.blockwaresolutions.com"
    marketplace_url = f"{base_url}/marketplace"
   
    print(f"Fetching marketplace page: {marketplace_url}")
    
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument('--ignore-certificate-errors')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(marketplace_url)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="marketplace"]/div[2]/div[2]/table'))
        )
        
        scroll_pause_time = 1
        container = driver.find_element(By.XPATH, '//*[@id="marketplace"]/div[2]/div[2]')
        last_height = driver.execute_script("return arguments[0].scrollHeight", container)
        
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return arguments[0].scrollHeight", container)
            if new_height == last_height:
                break
            last_height = new_height
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_rows = soup.find_all('tr', class_='MuiTableRow-root mui-1uk0056')
        miners = extract_miner_info(table_rows, base_url)
        save_results(miners)
        
    finally:
        driver.quit()

def extract_miner_info(table_rows, base_url):
    miners = []
    for row in table_rows:
        columns = row.find_all('td')
        
        machine_name_full = columns[2].find('a').find('span').text.strip()
        machine_name = machine_name_full.split(' (')[0]
        num_machines = int(machine_name_full.split('(')[1].split(')')[0])
        
        est_revenue = parse_float(columns[4].text.strip().split(' ')[0])
        est_profit = parse_float(columns[5].text.strip().split(' ')[0])
        price = parse_float(columns[6].text.strip().split(' ')[0])
        
        est_revenue /= num_machines
        est_profit /= num_machines
        price /= num_machines
        
        cost = est_revenue - est_profit
        
        hash_rate = columns[3].text.strip()
        if hash_rate != 'N/A':
            hash_rate_value = float(hash_rate.split()[0])
            hash_rate_unit = hash_rate.split()[1]
            hash_rate_per_machine = f"{hash_rate_value / num_machines} {hash_rate_unit}"
        else:
            hash_rate_per_machine = 'N/A'
        
        url = base_url + columns[2].find('a')['href']
        
        miner = {
            'Location': columns[1].text.strip(),
            'MachineName': machine_name,
            'HashRate(24h)': hash_rate_per_machine,
            'EstRevenue(30d)': est_revenue,
            'EstProfit(30d)': est_profit,
            'Price': price,
            'NumMachines': num_machines,
            'Cost': cost,
            'URL': url
        }
        miners.append(miner)
    return miners

def parse_float(value):
    try:
        return float(value.replace(',', ''))
    except ValueError:
        return 0.0

def save_results(miners):
    with open(DATA_FILE, 'w') as f:
        json.dump(miners, f, indent=2)
    print(f"Results saved to {DATA_FILE}")
    
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=miners[0].keys())
        writer.writeheader()
        writer.writerows(miners)
    print(f"Results saved to {CSV_FILE}")
    
    update_fetch_log()

def update_fetch_log():
    log = {'last_fetch': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    with open(LOG_FILE, 'w') as f:
        json.dump(log, f)

def should_fetch():
    if not os.path.exists(LOG_FILE):
        return True
    with open(LOG_FILE, 'r') as f:
        log = json.load(f)
    last_fetch_date = datetime.strptime(log['last_fetch'], '%Y-%m-%d %H:%M:%S')
    return datetime.now().date() != last_fetch_date.date()

def group_miners_by_model(miners):
    grouped_miners = {}
    for miner in miners:
        model = miner['MachineName']
        if model not in grouped_miners:
            grouped_miners[model] = []
        grouped_miners[model].append(miner)
    return grouped_miners

def find_arbitrage_opportunities(grouped_miners):
    opportunities = []
    for model, miners in grouped_miners.items():
        if len(miners) < 2:
            continue

        prices = [miner['Price'] for miner in miners]
        mean_price = statistics.mean(prices)
        
        if len(set(prices)) == 1:
            continue
        
        std_dev = statistics.stdev(prices)

        for miner in miners:
            if std_dev == 0:
                z_score = 0
            else:
                z_score = (miner['Price'] - mean_price) / std_dev
            
            if abs(z_score) > 2 and miner['EstProfit(30d)'] > 0:
                price_to_profit_ratio = miner['Price'] / miner['EstProfit(30d)'] if miner['EstProfit(30d)'] > 0 else float('inf')
                opportunity = {
                    'Model': model,
                    'Price': miner['Price'],
                    'Mean Price': mean_price,
                    'Z-Score': z_score,
                    'Location': miner['Location'],
                    'EstProfit(30d)': miner['EstProfit(30d)'],
                    'HashRate(24h)': miner['HashRate(24h)'],
                    'URL': miner['URL'],
                    'Price-to-Profit Ratio': price_to_profit_ratio
                }
                opportunities.append(opportunity)

    return sorted(opportunities, key=lambda x: abs(x['Z-Score']), reverse=True)

def plot_z_scores(opportunities):
    models = [opp['Model'] for opp in opportunities]
    z_scores = [opp['Z-Score'] for opp in opportunities]
    
    plt.figure(figsize=(12, 6))
    plt.bar(models, z_scores)
    plt.axhline(y=2, color='r', linestyle='--')
    plt.axhline(y=-2, color='r', linestyle='--')
    plt.title('Z-Scores of Arbitrage Opportunities')
    plt.xlabel('Miner Model')
    plt.ylabel('Z-Score')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(FOLDER_NAME, 'z_scores.png'))
    print(f"Z-score plot saved to {os.path.join(FOLDER_NAME, 'z_scores.png')}")

if __name__ == "__main__":
    if should_fetch():
        print("Starting to analyze Blockware Solutions Marketplace...")
        scrape_marketplace()
        print("Script execution completed.")
    
    with open(DATA_FILE, 'r') as f:
        miners = json.load(f)
    
    grouped_miners = group_miners_by_model(miners)
    arbitrage_opportunities = find_arbitrage_opportunities(grouped_miners)

    print("Potential Arbitrage Opportunities:")
    table_data = []
    for opp in arbitrage_opportunities:
        table_data.append([
            opp['Model'],
            f"{opp['Price']:.8f}",
            f"{opp['Mean Price']:.8f}",
            f"{opp['Z-Score']:.2f}",
            opp['Location'],
            f"{opp['EstProfit(30d)']:.8f}",
            opp['HashRate(24h)'],
            f"{opp['Price-to-Profit Ratio']:.2f}",
            opp['URL']
        ])

    headers = ["Model", "Price (BTC)", "Mean Price (BTC)", "Z-Score", "Location", "Est. Profit (30d, BTC)", "Hash Rate (24h)", "Price-to-Profit Ratio", "URL"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    plot_z_scores(arbitrage_opportunities)

    best_model = max(grouped_miners.items(), key=lambda x: statistics.mean([miner['EstProfit(30d)'] for miner in x[1]]))
    best_miner = max(best_model[1], key=lambda x: x['EstProfit(30d)'])
    
    print(f"\nModel with highest average profit potential: {best_model[0]}")
    print(f"Average 30-day profit: {statistics.mean([miner['EstProfit(30d)'] for miner in best_model[1]]):.8f} BTC")
    print(f"Best miner of this model:")
    print(f"  Location: {best_miner['Location']}")
    print(f"  Price: {best_miner['Price']:.8f} BTC")
    print(f"  Estimated 30-day profit: {best_miner['EstProfit(30d)']:.8f} BTC")
    print(f"  Hash Rate (24h): {best_miner['HashRate(24h)']}")
    print(f"  URL: {best_miner['URL']}")

    # Find the miner with the highest absolute Z-score
    highest_zscore_miner = max(arbitrage_opportunities, key=lambda x: abs(x['Z-Score']))
    print(f"\nMiner with the highest absolute Z-Score:")
    print(f"  Model: {highest_zscore_miner['Model']}")
    print(f"  Z-Score: {highest_zscore_miner['Z-Score']:.2f}")
    print(f"  Location: {highest_zscore_miner['Location']}")
    print(f"  Price: {highest_zscore_miner['Price']:.8f} BTC")
    print(f"  Mean Price: {highest_zscore_miner['Mean Price']:.8f} BTC")
    print(f"  Estimated 30-day profit: {highest_zscore_miner['EstProfit(30d)']:.8f} BTC")
    print(f"  Hash Rate (24h): {highest_zscore_miner['HashRate(24h)']}")
    print(f"  URL: {highest_zscore_miner['URL']}")