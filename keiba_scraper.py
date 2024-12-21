"""
How To Use
1. yearにほしい年を入力する。
2. 実行する。
3. 以上！
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def scrape_race_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None, None
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="race_table_01 nk_tb_common")
    if not table:
        return None, soup

    headers = [header.get_text(strip=True).replace('\n', '') for header in table.find("tr").find_all("th")]
    rows = []
    for row in table.find_all("tr")[1:]:
        cols = [col.get_text(strip=True) for col in row.find_all("td")]
        rows.append(cols)

    return pd.DataFrame(rows, columns=headers), soup

def append_payback(payback_table):
    payback_info = []
    if payback_table:
        for row in payback_table.find_all("tr"):
            cols = [col.get_text(strip=True) for col in row.find_all("td")]
            payback_info.append(cols)
    return payback_info

def scrape_year_races(year):
    base_url = "https://db.netkeiba.com/race/"
    all_race_data = []
    all_payback_data = []

    l = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
    for w in l:
        for z in range(6):
            for y in range(11):
                if y < 9:
                    day_url_prefix = f"{year}{w}0{z+1}0{y+1}"
                else:
                    day_url_prefix = f"{year}{w}0{z+1}{y+1}"

                empty_day_counter = 0

                for x in range(12):
                    if x < 9:
                        race_url = f"{base_url}{day_url_prefix}0{x+1}"
                    else:
                        race_url = f"{base_url}{day_url_prefix}{x+1}"

                    # 重い槍
                    time.sleep(0.5)

                    race_data, soup = scrape_race_data(race_url)
                    if race_data is None or race_data.empty:
                        empty_day_counter += 1
                        continue

                    payback_table = soup.find("table", summary="払い戻し")
                    payback_info = append_payback(payback_table)

                    all_race_data.append(race_data)
                    all_payback_data.append(payback_info)

                    print(f"Scraped: {race_url}")

                if empty_day_counter == 12:
                    break
    return all_race_data, all_payback_data

year = "2020"
race_data, payback_data = scrape_year_races(year)

with pd.ExcelWriter(f"./{year}_race_data.xlsx", engine="xlsxwriter") as writer:
    for idx, df in enumerate(race_data):
        df.to_excel(writer, sheet_name=f"Race_{idx+1}", index=False)
    payback_df = pd.DataFrame(payback_data)
    payback_df.to_excel(writer, sheet_name="Payback", index=False)
    
print("終わり！")
