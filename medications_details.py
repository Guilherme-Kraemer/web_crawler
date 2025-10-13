from playwright.sync_api import sync_playwright, Playwright
import pandas as pd
import os
import re
from multiprocessing import Process

def run_letter(letter, names, urls):
    """Process medications for a specific letter"""
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=True)
        context = browser.new_context()
        context_request = context.request
        page = context.new_page()
        
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
        
        for i, (name, url) in enumerate(zip(names, urls)):
            print(f"[{letter}] Processing {i+1}/{len(names)}: {name}")
            
            try:
                r = context_request.delete(url, max_redirects=0)
                print(f"   Code:{r.status}")
                try:
                    page.goto(url, wait_until='networkidle', timeout=0)
                except Exception as e:
                    pass

                dict_info = {}
                all_barcodes = []

                text_content = page.content()
                tr_content = page.locator("tr").all_inner_texts()

                all_barcodes = re.findall(r'\b(78\d{11,12})\b', text_content)

                for tr_text in tr_content:
                    parts = re.split(r'[\n\t]', tr_text, maxsplit=1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        dict_info[key] = value

                doses_info = []
                if "Dose" in dict_info:
                    doses_info = dict_info["Dose"]
                    doses_info = re.split(r'[\n\t]', doses_info)

                quantities_info = []
                if "Quantidade na embalagem" in dict_info: 
                    quantities_info = dict_info["Quantidade na embalagem"]
                    quantities_info = re.split(r'[\n\t]', quantities_info)

                price_info = []
                if "Preço Máximo ao Consumidor/SP" in dict_info:
                    price_info = dict_info["Preço Máximo ao Consumidor/SP"]
                    price_info = re.split(r'[\n\t]', price_info)

                info = []
                if "Forma Farmacêutica" in dict_info:
                    info = dict_info["Forma Farmacêutica"]
                    info = re.split(r'[\n\t]', info)

                # Remove duplicatas mantendo a ordem
                all_barcodes = list(dict.fromkeys(all_barcodes))
                
                # Determina quantas linhas criar (baseado no número de códigos de barras)
                num_entries = len(all_barcodes) if all_barcodes else 1
                
                # Cria uma entrada para cada código de barras
                for j in range(num_entries):
                    
                    # Nome (sempre repete)
                    medications_details["Name"].append(name)
                    
                    # Quantidade (pega o índice correspondente se existir)
                    if quantities_info and j < len(quantities_info):
                        medications_details["Quantidade na embalagem"].append(quantities_info[j])
                    else:
                        medications_details["Quantidade na embalagem"].append("")
                    
                    # Dose (pega o índice correspondente se existir)
                    if doses_info and j < len(doses_info):
                        medications_details["Dose"].append(doses_info[j])
                    else:
                        medications_details["Dose"].append("")
                    
                    # Preço (pega o índice correspondente se existir)
                    if price_info and j < len(price_info):
                        medications_details["Preço"].append(price_info[j])
                    else:
                        medications_details["Preço"].append("")
                        
                    # Código de barras
                    if all_barcodes:
                        medications_details["Codigos de Barras"].append(all_barcodes[j])
                    else:
                        medications_details["Codigos de Barras"].append("")
                    
                    # Infos (pega o índice correspondente se existir)
                    if info and j < len(info):
                        medications_details["Infos"].append(info[j])
                    else:
                        medications_details["Infos"].append("")
                
                print(f"   ✓ Found {len(all_barcodes)} barcode(s) - Created {num_entries} entries")

            except Exception as e:
                print(f"   ✗ Error: {str(e)[:50]}")
                
                medications_details["Name"].append(name)
                medications_details["Quantidade na embalagem"].append("Error")
                medications_details["Dose"].append("Error")
                medications_details["Preço"].append("Error")
                medications_details["Codigos de Barras"].append("Error")
                medications_details["Infos"].append("Error")
        
        # Save results for this letter
        if medications_details["Name"]:
            df_letter = pd.DataFrame(medications_details)
            output_file = f"medications_by_letter/medications_{letter}.csv"
            df_letter.to_csv(output_file, index=False, encoding='utf-8')
            print(f"\n✓ Saved {len(df_letter)} medications to '{output_file}'")

        browser.close()

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
    
    os.makedirs("medications_by_letter", exist_ok=True)
    
    # Start parallel processes for each letter
    processes = []
    for letter in sorted(medications_by_letter.keys()):
        names = medications_by_letter[letter]["names"]
        urls = medications_by_letter[letter]["urls"]
        
        process = Process(target=run_letter, args=(letter, names, urls))
        process.start()
        processes.append(process)
    
    # Wait for all processes to complete
    for process in processes:
        process.join()
    
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
if __name__ == '__main__':
    with sync_playwright() as playwright:
        run(playwright)