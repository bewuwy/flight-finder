import requests
import yaml
# import json

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

curr = config['CURRENCY']
airport_from = config['START_AIRPORT']
airport_to = config['END_AIRPORT']

if __name__ == "__main__":
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "*/*",
        "Referer": f"https://www.skyscanner.{config['DOMAIN']}/",
        "DNT": "1",
        "Alt-Used": f"www.skyscanner.{config['DOMAIN']}",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-GPC": "1",
        "TE": "trailers"
    }
    
    m = "{:02d}".format(config['MONTH'])
    url = f"https://www.skyscanner.{config['DOMAIN']}/g/monthviewservice/{config['REGION']}/{curr}/" + \
    f"{config['LOCALE']}/calendar/{airport_from}/{airport_to}/" + \
    f"{config['YEAR']}-{m}/{config['YEAR']}-{m}/"
            
    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        print(f"Error: {r.status_code}")
        print(r.text)
        exit(1)

    r = r.json()

    # traces = r['Traces']
    grid = r['PriceGrids']['Grid']
    
    min_total_price = 10**9
    min_total_price_idx = None
    
    for start_y in range(len(grid)):
        for start_x in range(len(grid[start_y])):
            # print(grid[start_y][start_x])
            
            if "DirectOutbound" not in grid[start_y][start_x]:
                continue
            
            price_start = grid[start_y][start_x]['DirectOutbound']['Price']
            
            for end_y in range(len(grid)):
                for end_x in range(len(grid[end_y])):
                    
                    if end_x <= start_x and end_y <= start_y:
                        continue
                    
                    if "DirectInbound" not in grid[end_y][end_x]:
                        continue
                    
                    price_end = grid[end_y][end_x]['DirectInbound']['Price']
                    
                    total_price = price_start + price_end
                    
                    if total_price < min_total_price:
                        
                        # check if the trip is not too long or too short
                        day_start = start_x + 1
                        day_end = end_y + 1
                        if day_end - day_start < config['MIN_DAYS'] or day_end - day_start > config['MAX_DAYS']:
                            continue
                        
                        min_total_price = total_price
                        min_total_price_idx = (start_y, start_x, end_y, end_x)
    
    day_start = min_total_price_idx[1] + 1
    day_end = min_total_price_idx[2] + 1

    # print out results
    print(f"Trip {airport_from} -> {airport_to} -> {airport_from} in {config['YEAR']}-{m} with {day_end - day_start} days in {airport_to}")
    print(f"Price: {min_total_price} {curr}\n")
    print(f"Start: {config['YEAR']}-{m}-{day_start} from {airport_from}")
    print(f"Return: {config['YEAR']}-{m}-{day_end} from {airport_to}")
