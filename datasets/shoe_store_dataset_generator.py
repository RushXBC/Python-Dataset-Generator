import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Price endings to simulate realistic retail pricing (e.g., 5,995 / 6,990)
suffixes = [0, 25, 50, 75, 90, 95, 99]

# 1. Product Catalog
# Structure: Brand → (Product Name, Base Price, Popularity Score)
raw_data = {
    "Nike": [("Air Force 1", 5895, 10), ("Dunk Low", 6895, 9), ("Air Max 270", 9900, 7), ("Pegasus 40", 8000, 6), ("Jordan 1 Low", 9500, 8)],
    "Adidas": [("Samba OG", 6800, 10), ("Stan Smith", 6000, 8), ("Ultraboost", 9500, 7), ("Gazelle", 5500, 8), ("NMD_R1", 7500, 6)],
    "New Balance": [("530", 6300, 9), ("550", 7500, 8), ("2002R", 9000, 7), ("990v6", 13500, 4), ("327", 5900, 8)],
    "Puma": [("Suede Classic", 5000, 7), ("Palermo", 6200, 8), ("RS-X", 7500, 6), ("Clyde", 6500, 5), ("Mayze", 5800, 6)],
    "ASICS": [("Gel-Kayano 30", 9500, 6), ("Gel-1130", 5500, 9), ("Novablast 4", 7800, 7), ("Gel-Lyte III", 6500, 6), ("GT-2000", 7000, 5)],
    "Converse": [("Chuck Taylor 70", 4500, 9), ("Chuck Taylor All Star", 3500, 10), ("Run Star Hike", 5500, 7), ("Weapon", 6000, 5), ("One Star", 4800, 6)],
    "Vans": [("Old Skool", 4200, 10), ("Slip-On", 3800, 9), ("Sk8-Hi", 4800, 8), ("Authentic", 3800, 8), ("Knu Skool", 5200, 7)],
    "Hoka": [("Clifton 9", 8500, 8), ("Bondi 8", 9200, 7), ("Mach 6", 8200, 6), ("Speedgoat 5", 8800, 7), ("Transport", 8000, 5)],
    "On": [("Cloud 5", 8200, 9), ("Cloudmonster", 9800, 8), ("Cloudsurfer", 9000, 6), ("Cloudtilt", 9500, 5), ("Cloud X", 8500, 6)],
    "Reebok": [("Club C 85", 5200, 9), ("Classic Leather", 5000, 7), ("Nano X4", 7500, 6), ("Instapump Fury", 9800, 4), ("BB 4000 II", 5500, 6)],
    "Under Armour": [("Curry 11", 8900, 7), ("HOVR Phantom", 7800, 6), ("Apparition", 6500, 5), ("Flow Velocity", 8200, 5), ("Project Rock 6", 8500, 6)],
    "Skechers": [("GoWalk", 4200, 9), ("D'Lites", 4500, 7), ("Uno", 4800, 8), ("Arch Fit", 5200, 7), ("Max Cushioning", 5500, 6)],
    "Saucony": [("Endorphin Speed", 8500, 6), ("Ride 17", 7200, 5), ("Shadow 6000", 6500, 7), ("Jazz 81", 5000, 6), ("Peregrine 13", 7500, 5)],
    "Mizuno": [("Wave Rider 27", 7500, 6), ("Wave Sky 7", 8500, 5), ("Wave Prophecy", 12500, 3), ("Sky Medal", 6800, 6), ("Contender", 6200, 5)],
    "Fila": [("Disruptor II", 4500, 6), ("Ray Tracer", 4800, 5), ("Sandblast", 3800, 7), ("Original Fitness", 4200, 6), ("Grant Hill 2", 6500, 4)]
}

# Check if a given date is a Philippine holiday (simplified fixed dates only)
def is_ph_holiday(date):
    return (date.month, date.day) in [(1,1), (11,1), (12,25), (12,30)]

# Randomly selects ~25% of products each year to go on sale
# Discount depends on product popularity
def get_yearly_sale_roster(catalog, year):
    sale_count = int(len(catalog) * 0.25)
    sale_items = random.sample(catalog, sale_count)
    return {
        item["Product"]: (
            random.choice([5, 10]) if item["Pop"] >= 8
            else random.choice([15, 20, 25, 30, 35, 40, 45, 50])
        )
        for item in sale_items
    }

# Defines brand market share distribution per year
# Adjusts trend for newer brands (Hoka, On gaining share after 2024)
def get_yearly_shares(year):
    shares = {"Nike": 0.22, "Adidas": 0.18, "New Balance": 0.12, "Vans": 0.08, "Converse": 0.08, 
              "Skechers": 0.06, "ASICS": 0.05, "On": 0.04, "Hoka": 0.04, "Puma": 0.04, 
              "Reebok": 0.03, "Under Armour": 0.02, "Saucony": 0.01, "Mizuno": 0.01, "Fila": 0.01}
    
    # Shift market share trends starting 2024
    if year >= 2024:
        shares["Hoka"] += 0.04
        shares["On"] += 0.04
        shares["Nike"] -= 0.08

    # Normalize so total = 1
    total = sum(shares.values())
    return {k: v/total for k, v in shares.items()}

# Main dataset generation function
def generate_master_dataset(num_customers=22764):

    # Define simulation date range
    start_date, end_date = datetime(2021, 1, 1), datetime(2025, 12, 31)

    catalog, inventory = [], {}

    # Build product catalog with adjusted prices and initial inventory
    for brand, prods in raw_data.items():
        for name, base_p, pop in prods:
            price = (base_p // 100) * 100 + random.choice(suffixes)
            catalog.append({"Brand": brand, "Product": name, "Unit_Price": price, "Pop": pop})

            # Inventory based on popularity
            inventory[name] = 800 if pop >= 8 else 400 if pop >= 5 else 200

    # Precompute yearly sale items and business growth trend
    sale_rosters = {year: get_yearly_sale_roster(catalog, year) for year in range(2021, 2026)}
    yearly_momentum = {2021: 0.85, 2022: 1.0, 2023: 1.35, 2024: 1.5, 2025: 1.2}

    # Generate customer pool with segment, region, and join eligibility date
    cust_pool = [{
        "pid": i,
        "Segment": random.choices(["Consumer", "SMB", "Corporate"], [0.75, 0.15, 0.10])[0],
        "Region": random.choice(["Luzon", "Visayas", "Mindanao"]),
        "Join_Eligible": start_date + timedelta(days=random.randint(0, (end_date-start_date).days))
    } for i in range(num_customers)]

    cust_df = pd.DataFrame(cust_pool)

    orders = []

    # Queue for restocking items next month
    pending_restocks = []

    current_day = start_date

    # Iterate day-by-day
    while current_day <= end_date:

        # --- RESTOCK LOGIC ---
        # On 1st of month → replenish previously flagged items
        if current_day.day == 1 and pending_restocks:
            for item_name, qty_to_add in pending_restocks:
                inventory[item_name] += qty_to_add
            pending_restocks = []

        # On 25th → mark low-stock items for next month restock
        if current_day.day == 25:
            for c in catalog:
                name = c["Product"]
                if inventory[name] <= 50:
                    pending_restocks.append((name, c["Pop"] * 10))

        # --- STORE CLOSED LOGIC ---
        # Skip Sundays and PH holidays
        if current_day.weekday() == 6 or is_ph_holiday(current_day):
            current_day += timedelta(days=1)
            continue

        m, year = current_day.month, current_day.year
        shares = get_yearly_shares(year)
        current_roster = sale_rosters[year]
        momentum = yearly_momentum.get(year, 1.0)

        # --- DAILY ORDER VOLUME ---
        daily_target = int(random.randint(15, 30) * momentum)

        # Seasonal spikes
        if m in [11, 12]:
            daily_target = int(daily_target * (4.0 if year in [2023, 2024] else 3.2))
        elif m in [5, 6]:
            daily_target = int(daily_target * 2.2)

        # Payday / special dates spikes
        if current_day.day in [15, 30, 31, 14, 25]:
            daily_target = int(daily_target * 2.0)

        # Generate sorted timestamps for realism
        daily_timestamps = sorted([
            current_day.replace(
                hour=random.randint(9, 21),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            for _ in range(daily_target)
        ])

        # --- ORDER GENERATION ---
        for order_time in daily_timestamps:

            # Filter products with available stock
            available = [c for c in catalog if inventory[c["Product"]] > 0]
            if not available:
                break

            # Only customers eligible (joined already)
            eligible = cust_df[cust_df["Join_Eligible"] <= current_day]
            if eligible.empty:
                continue

            p = eligible.sample(n=1).iloc[0]

            # Product selection weighted by brand share and popularity
            prod = random.choices(
                available,
                weights=[shares[c["Brand"]] * c["Pop"] for c in available]
            )[0]

            # Apply discount if product is in sale roster and during sale months
            disc = current_roster.get(prod["Product"], 0) if (m in [11, 12, 5, 6] and prod["Product"] in current_roster) else 0

            # --- QUANTITY LOGIC BASED ON SEGMENT ---
            if p["Segment"] == "Consumer":
                desired_qty = random.choices([1, 2, 3], weights=[0.50, 0.25, 0.25])[0] if (disc > 0 or m in [11, 12]) else random.choices([1, 2], weights=[0.95, 0.05])[0]
            elif p["Segment"] == "SMB":
                desired_qty = random.randint(10, 20) if disc > 15 else random.randint(3, 10)
            else:
                desired_qty = random.randint(30, 50) if disc > 15 else random.randint(10, 25)

            # Prevent overselling (stock constraint)
            actual_qty = min(desired_qty, inventory[prod["Product"]])
            if actual_qty <= 0:
                continue

            # Update inventory
            inventory[prod["Product"]] -= actual_qty

            # Determine stock status after sale
            status = "In Stock" if inventory[prod["Product"]] > 0 else "Out of Stock"
            if actual_qty < desired_qty:
                status = "Partial - Stockout"

            # Record order
            orders.append({
                "pid": p["pid"],
                "Order_Date": order_time,
                "Segment": p["Segment"],
                "Region": p["Region"],
                "Brand": prod["Brand"],
                "Product_Name": prod["Product"],
                "Unit_Price": prod["Unit_Price"],
                "Discount": disc,
                "Discounted_Price": round(prod["Unit_Price"] * (1 - disc/100), 2),
                "Quantity": actual_qty,
                "Stock_Left": inventory[prod["Product"]],
                "Stock_Status": status
            })

        current_day += timedelta(days=1)

    # --- POST-PROCESSING ---
    df = pd.DataFrame(orders).sort_values("Order_Date").reset_index(drop=True)

    # Map internal pid → readable Customer_ID (C000001 format)
    unique_pids = []
    seen = set()
    for pid in df["pid"]:
        if pid not in seen:
            unique_pids.append(pid)
            seen.add(pid)

    pid_to_cid = {pid: f"C{i+1:06d}" for i, pid in enumerate(unique_pids)}
    df["Customer_ID"] = df["pid"].map(pid_to_cid)

    # Add business-ready fields
    df["Order_ID"] = range(1, len(df)+1)
    df["Channel"] = np.where((df["Region"] == "Luzon") & (np.random.rand(len(df)) < 0.75), "Store", "Online")
    df["Total_Sales"] = round(df["Discounted_Price"] * df["Quantity"], 2)

    # Customer join date = first purchase date
    df["Customer_Join_Date"] = df.groupby("Customer_ID")["Order_Date"].transform("min").dt.strftime("%m/%d/%Y")

    # Label first purchase vs repeat
    df["Order_Type"] = np.where(
        df.groupby("Customer_ID")["Order_ID"].rank(method="first") == 1,
        "New Customer",
        "Repeat Customer"
    )

    # Format datetime
    df["Order_Date"] = df["Order_Date"].dt.strftime("%m/%d/%Y %H:%M:%S")

    # Final column order
    cols = ["Order_ID", "Customer_ID", "Order_Date", "Segment", "Region", "Channel", 
            "Brand", "Product_Name", "Unit_Price", "Discount", "Discounted_Price", 
            "Quantity", "Total_Sales", "Stock_Left", "Stock_Status", 
            "Customer_Join_Date", "Order_Type"]

    # Export to CSV
    df[cols].to_csv("shoe_store_closed_sundays.csv", index=False)

    return df[cols]

# Execute dataset generation
final_df = generate_master_dataset()