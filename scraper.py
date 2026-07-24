import os
import re
import time
import random
import requests
import pandas as pd

from bs4 import BeautifulSoup



###############################################################
# CONFIGURATION
###############################################################

BASE_URL = "https://www.gsmarena.com"

OUTPUT_FILE = "media/mobiles_(1).csv"
# Temporary save file (supports resume)
TEMP_FILE = "media/temp_scraped_data.csv"

# Save after every N phones
SAVE_INTERVAL = 25

HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/138.0 Safari/537.36"
}



###############################################################
# UTILITIES
###############################################################

def random_sleep(a=1.5, b=3.5):
    time.sleep(random.uniform(a, b))
###############################################################
# SAVE / LOAD FUNCTIONS
###############################################################

def save_progress(data):

    df = pd.DataFrame(data)

    df.to_csv(TEMP_FILE, index=False)

    print(f"Saved {len(df)} phones.")


def load_progress():

    if os.path.exists(TEMP_FILE):

        df = pd.read_csv(TEMP_FILE)

        print(f"Loaded {len(df)} existing phones.")

        return df.to_dict("records")

    return []

session = requests.Session()
session.headers.update(HEADERS)
def get_soup(url):

    try:

        r = session.get(url, timeout=30)

        r.raise_for_status()

        return BeautifulSoup(r.text, "lxml")

    except Exception:

        return None


###############################################################
# BRANDS TO SCRAPE
###############################################################

BRANDS = {

    "Samsung":
        "https://www.gsmarena.com/samsung-phones-9.php",

    "Apple":
        "https://www.gsmarena.com/apple-phones-48.php",

    "Xiaomi":
        "https://www.gsmarena.com/xiaomi-phones-80.php",

    "Realme":
        "https://www.gsmarena.com/realme-phones-118.php",

    "OnePlus":
        "https://www.gsmarena.com/oneplus-phones-95.php",

    "Motorola":
        "https://www.gsmarena.com/motorola-phones-4.php",

    "Google":
        "https://www.gsmarena.com/google-phones-107.php",

    "Nothing":
        "https://www.gsmarena.com/nothing-phones-128.php",

    "Vivo":
        "https://www.gsmarena.com/vivo-phones-98.php",

    "Oppo":
        "https://www.gsmarena.com/oppo-phones-82.php",

    "Honor":
        "https://www.gsmarena.com/honor-phones-121.php",

    "Huawei":
        "https://www.gsmarena.com/huawei-phones-58.php",

    "Nokia":
        "https://www.gsmarena.com/nokia-phones-1.php",

    "Sony":
        "https://www.gsmarena.com/sony-phones-7.php",

    "Asus":
        "https://www.gsmarena.com/asus-phones-46.php",

    "Lenovo":
        "https://www.gsmarena.com/lenovo-phones-73.php",

    "Tecno":
        "https://www.gsmarena.com/tecno-phones-120.php",

    "Infinix":
        "https://www.gsmarena.com/infinix-phones-119.php",

    "Lava":
        "https://www.gsmarena.com/lava-phones-94.php",

    "Micromax":
        "https://www.gsmarena.com/micromax-phones-66.php",

    "POCO":
        "https://www.gsmarena.com/poco-phones-123.php",

    "iQOO":
        "https://www.gsmarena.com/iqoo-phones-119.php",

    "Redmi":
        "https://www.gsmarena.com/xiaomi-phones-80.php"
}

###############################################################
# GET ALL PHONE LINKS
###############################################################

def get_all_phone_links():

    phone_links = []

    for brand, url in BRANDS.items():

        print(f"\nCollecting {brand} phones...")

        while True:

            soup = get_soup(url)

            if soup is None:
                break

            phones = soup.select("div.makers li a")

            if not phones:
                break

            for phone in phones:

                href = phone.get("href")

                if href:

                    full = BASE_URL + "/" + href

                    phone_links.append(full)

            next_page = soup.find(
                "a",
                class_="pages-next"
            )

            if next_page:

                url = BASE_URL + "/" + next_page["href"]

                random_sleep()

            else:
                break

    phone_links = sorted(set(phone_links))

    print()

    print("Total Phones Found :", len(phone_links))

    return phone_links
###############################################################
# EXTRACT PHONE SPECIFICATIONS
###############################################################

def clean_text(text):
    if text:
        return " ".join(text.split())
    return ""


def extract_first_storage(memory_text):
    """
    Example:
    128GB 8GB RAM, 256GB 12GB RAM
    ->
    RAM/ROM = 8 GB|128 GB
    """

    if not memory_text:
        return ""

    ram = ""
    rom = ""

    ram_match = re.search(r'(\d+)\s*GB\s*RAM', memory_text, re.I)

    if ram_match:
        ram = ram_match.group(1)

    rom_match = re.search(r'(\d+)\s*GB', memory_text)

    if rom_match:
        rom = rom_match.group(1)

    if ram and rom:
        return f"{ram} GB|{rom} GB"

    return ""


def extract_phone_details(phone_url):

    print("Reading:", phone_url)

    soup = get_soup(phone_url)

    if soup is None:
        return None

    specs = {
        "Product Name": "",
        "Rating": "",
        "Rating Info": "",
        "RAM/ROM": "",
        "Display": "",
        "Camera": "",
        "Battery": "",
        "Processor": "",
        "Warranty": "1 Year",
        "Price": "",
        "Original Price": "",
        "Offer": "",
        "Deals": "",
        "Exchangable_amount": ""
    }

    try:
        specs["Product Name"] = clean_text(soup.find("h1").text)
    except:
        pass

    tables = soup.find_all("table")

    for table in tables:

        rows = table.find_all("tr")

        for row in rows:

            try:
                key = row.find("td", class_="ttl").get_text(strip=True)
                value = row.find("td", class_="nfo").get_text(" ", strip=True)
            except:
                continue

            if key == "Internal":
                specs["RAM/ROM"] = extract_first_storage(value)

            elif key == "Size":
                specs["Display"] = value + " Display"

            elif key == "Chipset":
                specs["Processor"] = value + " Processor"

            elif key == "Type" and "mAh" in value:
                specs["Battery"] = value + " Battery"

            elif key in ["Single", "Dual", "Triple", "Quad"]:

                if specs["Camera"] == "":
                    specs["Camera"] = value + " Rear Camera"

            

    specs["Display"] = clean_text(specs["Display"])
    specs["Camera"] = clean_text(specs["Camera"])
    specs["Battery"] = clean_text(specs["Battery"])
    specs["Processor"] = clean_text(specs["Processor"])

    return specs
###############################################################
# CSV HELPERS
###############################################################

CSV_COLUMNS = [
    "Product Name",
    "Rating",
    "Rating Info",
    "RAM/ROM",
    "Display",
    "Camera",
    "Battery",
    "Processor",
    "Warranty",
    "Price",
    "Original Price",
    "Offer",
    "Deals",
    "Exchangable_amount"
]


def load_existing_csv():

    if os.path.exists(OUTPUT_FILE):

        try:

            df = pd.read_csv(OUTPUT_FILE)

            if "Unnamed: 0" in df.columns:
                df = df.drop(columns=["Unnamed: 0"])

            return df

        except Exception:

            return pd.DataFrame(columns=CSV_COLUMNS)

    return pd.DataFrame(columns=CSV_COLUMNS)


def update_dataset(existing_df, phone_data):

    if phone_data is None:
        return existing_df

    product = phone_data["Product Name"].strip()

    if product == "":
        return existing_df

    if product in existing_df["Product Name"].values:

        idx = existing_df[
            existing_df["Product Name"] == product
        ].index[0]

        for col in CSV_COLUMNS:

            if col in phone_data and phone_data[col] != "":

                existing_df.at[idx, col] = phone_data[col]

    else:

        row = {}

        for col in CSV_COLUMNS:

            row[col] = phone_data.get(col, "")

        existing_df = pd.concat(
            [existing_df, pd.DataFrame([row])],
            ignore_index=True
        )

    return existing_df


def save_dataset(df):

    df = df.drop_duplicates(
        subset=["Product Name"],
        keep="last"
    )

    df = df.sort_values(
        by="Product Name"
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n===================================")
    print("CSV Updated Successfully")
    print("Total Phones :", len(df))
    print("Saved To :", OUTPUT_FILE)
    print("===================================\n")

###############################################################
# NORMALIZATION FUNCTIONS
###############################################################

def normalize_display(display):

    if not display:
        return ""

    display = display.replace("inches", "inch")

    if "Display" not in display:
        display += " Display"

    return display


def normalize_battery(battery):

    if not battery:
        return ""

    if "Battery" not in battery:
        battery += " Battery"

    return battery


def normalize_processor(processor):

    if not processor:
        return ""

    if "Processor" not in processor:
        processor += " Processor"

    return processor


def normalize_camera(camera):

    if not camera:
        return ""

    return camera.replace("  ", " ").strip()


def normalize_ram(ram):

    return ram


def normalize_phone(phone):

    phone["Display"] = normalize_display(phone["Display"])
    phone["Battery"] = normalize_battery(phone["Battery"])
    phone["Processor"] = normalize_processor(phone["Processor"])
    phone["Camera"] = normalize_camera(phone["Camera"])
    phone["RAM/ROM"] = normalize_ram(phone["RAM/ROM"])

    return phone
###############################################################
# PRICE LOOKUP
###############################################################

###############################################################
# MERGE WITH EXISTING DATASET
###############################################################

def fetch_price(phone):

    global existing_price_data

    if phone is None:
        return phone

    product = phone["Product Name"].strip().lower()

    if product in existing_price_data:

        old = existing_price_data[product]

        phone["Price"] = old.get("Price", "")
        phone["Original Price"] = old.get("Original Price", "")
        phone["Rating"] = old.get("Rating", "")
        phone["Rating Info"] = old.get("Rating Info", "")
        phone["Offer"] = old.get("Offer", "")
        phone["Deals"] = old.get("Deals", "")
        phone["Exchangable_amount"] = old.get("Exchangable_amount", "")

    else:

        phone["Price"] = "Not Available"
        phone["Original Price"] = ""
        phone["Rating"] = ""
        phone["Rating Info"] = ""
        phone["Offer"] = ""
        phone["Deals"] = ""
        phone["Exchangable_amount"] = ""

    return phone

###############################################################
# MAIN
###############################################################

if __name__ == "__main__":

    print("=" * 60)
    print("Starting Mobile Phone Scraper...")
    print("=" * 60)

    # Load existing dataset
    dataset = load_existing_csv()
###############################################################
# CREATE FAST LOOKUP DICTIONARY
###############################################################

    existing_price_data = {}

    for _, row in dataset.iterrows():

        existing_price_data[
            str(row["Product Name"]).strip().lower()
        ] = row.to_dict()

    print(f"Existing Records : {len(dataset)}")

    # Collect all phone URLs
    phone_links = get_all_phone_links()

    total = len(phone_links)

    print(f"Total Phones To Process : {total}")

    count = 0
    processed = set(dataset["Product Name"].astype(str).str.lower())

    for link in phone_links:

        try:
        
                phone = extract_phone_details(link)
        
                if phone is None:
                    continue
        
                if phone["Product Name"].lower() in processed:
                    print("Already Exists :", phone["Product Name"])
                    continue

                processed.add(phone["Product Name"].lower())
        
                phone = normalize_phone(phone)
        
                phone = fetch_price(phone)
        
                dataset = update_dataset(dataset, phone)
        
                count += 1
        
                if count % SAVE_INTERVAL == 0:

                    print(f"\nSaving after {count} phones...\n")

                    save_dataset(dataset)
        
                random_sleep(1, 2)
        
        except Exception as e:
        
            print("Skipped:", e)
        
    save_dataset(dataset)


    print("=" * 60)
    print("Scraping Completed Successfully.")
    print(f"Final Records : {len(dataset)}")
    print("=" * 60)