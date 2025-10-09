from playwright.sync_api import sync_playwright, Playwright
import pandas as pd
from utils import constants
from time import sleep

def run(playwright: Playwright):
    medications = []
    browser = playwright.firefox.launch(headless=False, slow_mo=1000)
    page = browser.new_page()
    page_number = 1
    
    for i in constants.alphabet:
        print(f"Processando letra: {i}")
        counter = 1
        page.goto("https://consultaremedios.com.br/medicamentos/" + i, timeout=0)
        
        try:
            number_pages = page.get_by_label("page link").get_attribute("href") or "?pagina=1"
            page_number = int(number_pages.split("?pagina=")[-1]) if number_pages else 1
            print(f"Números de páginas: {page_number}")
        except Exception as e:
            print(f"Erro ao determinar o número de páginas para a letra '{i}': {e}")
            page_number = 1
            
        while counter <= page_number:
            
            try:

                possible_selectors = [
                    "ul.grid.grid-cols-1.lg\\:grid-cols-2.gap-x-6.py-6",
                    "ul[class*='grid'][class*='py-6']",
                    "ul.grid"
                ]

                element = None

                for selector in possible_selectors:
                    try:
                        element = page.locator(selector)
                        if element.count() > 0:
                            print(f"Usando seletor: {selector}")
                            break
                    except:
                        continue
                    
                if not element or element.count() == 0:
                    print(f"Não foi possível encontrar a lista para a letra '{i}'")
                    sleep(10)
                    counter += 1
                    print(f"Indo para a próxima página: {counter}")
                    page.goto(f"https://consultaremedios.com.br/medicamentos/{i}?pagina={counter}", timeout=0)
                    continue
                
                # Processar itens
                links = element.locator("li a")
                count = links.count()
                print(f"Total de links encontrados: {count}")

                for j in range(count):
                    try:
                        link = links.nth(j)
                        name = link.get_attribute("title") or link.inner_text().strip()
                        href = link.get_attribute("href")

                        if name and href:
                                medication_data = {
                                    "name": name,
                                    "url": f"https://consultaremedios.com.br{href}",
                                    "letter": i
                                }
                                medications.append(medication_data)
                                print(f"  {j+1}. {name}")

                    except Exception as e:
                            print(f"Erro ao processar link {j}: {e}")
                            continue

            except Exception as e:
                    print(f"Erro ao processar letra '{i}': {e}")
                    continue
            counter += 1
            print(f"Indo para a próxima página: {counter}")
            page.goto(f"https://consultaremedios.com.br/medicamentos/{i}?pagina={counter}", timeout=0)
    
    # Salvar resultados
    if medications:
        df = pd.DataFrame(medications)
        df.to_csv("medicamentos.csv", index=False, encoding='utf-8')
        print(f"\nResumo:")
        print(f"Total de medicamentos: {len(medications)}")
        print(f"Por letra: {df.groupby('letter').size().to_dict()}")
    
    browser.close()

# Função principal
if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)