from playwright.sync_api import sync_playwright, Playwright
import pandas as pd
import os
import re

def run(playwright: Playwright):
    df = pd.read_csv("medicamentos_alternative.csv")
    list_nome = df["name"].tolist()
    list_url = df["url"].tolist()
    
    # Group medications by first letter
    medications_by_letter = {}
    for name, url in zip(list_nome, list_url):
        first_letter = name[0].upper() if name else 'OTHER'
        if not first_letter.isalpha():
            first_letter = 'OTHER'
        
        if first_letter not in medications_by_letter:
            medications_by_letter[first_letter] = {"names": [], "urls": []}
        
        medications_by_letter[first_letter]["names"].append(name)
        medications_by_letter[first_letter]["urls"].append(url)
    
    browser = playwright.firefox.launch(headless=True)
    page = browser.new_page()
    
    # Create output directory if it doesn't exist
    os.makedirs("medications_by_letter", exist_ok=True)
    
    # Process each letter group
    for letter in sorted(medications_by_letter.keys()):
        print(f"\n{'='*60}")
        print(f"Processing medications starting with letter: {letter}")
        print(f"{'='*60}\n")
        
        medications_details = {
            "Name": [],
            "Quantidade na embalagem": [],
            "Dose": [],
            "Preço": [],
            "Codigos de Barras": [],
            "Infos": []
        }
        
        names = medications_by_letter[letter]["names"]
        urls = medications_by_letter[letter]["urls"]
        
        for i, (name, url) in enumerate(zip(names, urls)):
            print(f"[{letter}] Processing {i+1}/{len(names)}: {name}")
            
            try:
                page.goto(url, timeout=0)
                page.wait_for_load_state("networkidle", timeout=0)
                
                # Initialize variables for this medication
                dict_info = {}
                all_barcodes = []
                
                # Get page content
                text_content = page.content()
                tr_content = page.locator("tr").all_inner_texts()
                
                # Look for sequences of 12-14 digits that start with 78 or 789 (Brazilian EAN)
                all_barcodes = re.findall(r'\b(78\d{11,12})\b', text_content)
                
                # Parse table rows into dictionary
                for tr_text in tr_content:
                    # Split by newline or tab - take only first split
                    parts = re.split(r'[\n\t]', tr_text, maxsplit=1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        dict_info[key] = value
        
                # Extract doses if present
                doses_info = ""
                if "Dose" in dict_info:
                    doses_info = dict_info["Dose"]
                    doses_info = re.split(r'[\n\t]', doses_info)
        
                # Extract quantities if present
                quantities_info = ""
                if "Quantidade na embalagem" in dict_info: 
                    quantities_info = dict_info["Quantidade na embalagem"]
                    quantities_info = re.split(r'[\n\t]', quantities_info)
                    
                # Extract price if present
                price_info = ""
                if "Preço Máximo ao Consumidor/SP" in dict_info:
                    price_info = dict_info["Preço Máximo ao Consumidor/SP"]
                    price_info = re.split(r'[\n\t]', price_info)
                    
                # Extract pharmaceutical form if present
                info = ""
                if "Forma Farmacêutica" in dict_info:
                    info = dict_info["Forma Farmacêutica"]
                    info = re.split(r'[\n\t]', info)
                
                # Remove duplicates while preserving order
                all_barcodes = list(dict.fromkeys(all_barcodes))
            
                
                # Join all barcodes with semicolon
                all_barcodes_str = "; ".join(all_barcodes) if all_barcodes else ""
                
                # Append data to results
                medications_details["Name"].append(name)
                medications_details["Quantidade na embalagem"].append(quantities_info)
                medications_details["Dose"].append(doses_info)
                medications_details["Preço"].append(price_info)
                medications_details["Codigos de Barras"].append(all_barcodes_str)
                medications_details["Infos"].append(info)
                
                print(f"   ✓ Found {len(all_barcodes)} barcode(s): {all_barcodes_str}")
                
            except Exception as e:
                print(f"   ✗ Error: {e}")
                # Append error data
                medications_details["Name"].append(name)
                medications_details["Quantidade na embalagem"].append("Error")
                medications_details["Dose"].append("Error")
                medications_details["Preço"].append("Error")
                medications_details["Codigo de Barras"].append("Error")
                medications_details["Infos"].append("Error")
        
        # Save results for this letter
        if medications_details["Name"]:
            df_letter = pd.DataFrame(medications_details)
            output_file = f"medications_by_letter/medications_{letter}.csv"
            df_letter.to_csv(output_file, index=False, encoding='utf-8')
            print(f"\n✓ Saved {len(df_letter)} medications to '{output_file}'")

    browser.close()
    
    # Combine all letter files into one master file
    print(f"\n{'='*60}")
    print("Combining all files into master CSV...")
    print(f"{'='*60}\n")
    
    all_files = []
    for letter in sorted(medications_by_letter.keys()):
        file_path = f"medications_by_letter/medications_{letter}.csv"
        if os.path.exists(file_path):
            all_files.append(pd.read_csv(file_path))
    
    if all_files:
        master_df = pd.concat(all_files, ignore_index=True)
        master_df.to_csv("medications_details_complete.csv", index=False, encoding='utf-8')
        print(f"✓ Master file created: medications_details_complete.csv")
        print(f"✓ Total medications processed: {len(master_df)}")

# Run the scraper
with sync_playwright() as playwright:
    run(playwright)