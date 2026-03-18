from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

# ===== CONFIG =====
URL = "https://www.nerdin.com.br/vagas.php?busca=java&filtro_pj=1"

# ===== DRIVER =====
options = webdriver.ChromeOptions()
options.add_argument(r"--user-data-dir=C:\chrome-bot")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# ===== UTILS =====
def esperar():
    time.sleep(random.uniform(2, 4))

# ===== CLICK SEGURO =====
def clicar_seguro(elemento):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
        time.sleep(1)

        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(elemento))
        elemento.click()

    except:
        driver.execute_script("arguments[0].click();", elemento)

# ===== PEGAR LINKS =====
def pegar_links_vagas():
    elementos = driver.find_elements(By.XPATH, "//a[contains(@href,'vaga')]")
    links = []

    for el in elementos:
        href = el.get_attribute("href")
        if href and "vaga" in href:
            links.append(href)

    return list(set(links))

# ===== BOTÃO =====
def encontrar_botao():
    try:
        return driver.find_element(By.XPATH, "//a[contains(@class,'btn-candidatar-vaga')]")
    except:
        return None

# ===== PREENCHER =====
def preencher_formulario():
    elementos = driver.find_elements(By.XPATH, "//input | //textarea | //select")

    for el in elementos:
        try:
            if not el.is_displayed() or not el.is_enabled():
                continue
            nome = (el.get_attribute("name") or "").lower()
            placeholder = (el.get_attribute("placeholder") or "").lower()
            tag = el.tag_name.lower()
            nome = (el.get_attribute("name") or "").lower()
            aria = (el.get_attribute("aria-label") or "").lower()

            texto = f"{nome} {placeholder} {aria}"
            
            if tag in ["input", "textarea"]:
                if el.get_attribute("value"):
                    continue

                el.click()
                esperar()

                if "nome" in nome:
                    el.send_keys("Gustavo Pinheiro Campos")

                elif "email" in nome:
                    el.send_keys("gustavocampos170@gmail.com")

                elif "telefone" in nome:
                    el.send_keys("11963061380")

                elif "cidade" in nome:
                    el.send_keys("São Paulo - SP")

                elif "funcao" in nome:
                    el.send_keys("Desenvolvedor Java")

                elif "salario" in texto or "pretensao" in texto:
                    el.clear()
                    el.send_keys("15000")

                elif "disponibilidade" in nome:
                    el.send_keys("0")

                else:
                    el.send_keys("Sim")

            elif tag == "select":
                try:
                    Select(el).select_by_index(1)
                except:
                    pass

        except Exception as e:
            print("Erro campo:", e)

# ===== PROCESSAR ETAPAS =====
def processar_formulario():
    tentativas = 0

    while tentativas < 10:
        try:
            print("🔄 Preenchendo etapa...")
            preencher_formulario()

            botoes = driver.find_elements(By.XPATH, "//button")

            for botao in botoes:
                texto = (botao.text or "").lower()

                if "próximo" in texto:
                    print("➡️ Próxima etapa")
                    clicar_seguro(botao)
                    esperar()
                    break

                elif "enviar candidatura" in texto:
                    print("🚀 Enviando candidatura")
                    clicar_seguro(botao)
                    esperar()
                    return True

            tentativas += 1

        except Exception as e:
            print("Erro formulário:", e)
            return False

    return False

# ===== APLICAR =====
def aplicar_vaga():
    try:
        botao = encontrar_botao()

        if not botao:
            print("❌ Sem botão de candidatura")
            return

        clicar_seguro(botao)
        esperar()

        processar_formulario()

    except Exception as e:
        print("Erro aplicar:", e)

# ===== LOOP =====
def executar():
    driver.get(URL)
    esperar()

    links = pegar_links_vagas()
    print(f"{len(links)} vagas encontradas")

    for i, link in enumerate(links):
        try:
            print(f"\n🚀 Vaga {i+1}")
            print(link)

            driver.get(link)
            esperar()

            aplicar_vaga()

            driver.get(URL)
            esperar()

        except Exception as e:
            print("Erro:", e)
            driver.get(URL)
            esperar()

# ===== START =====
executar()