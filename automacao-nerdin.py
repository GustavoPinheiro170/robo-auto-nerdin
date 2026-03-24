from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import os
import json

# ===== PATHS =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_APLICADAS = os.path.join(BASE_DIR, "vagas_aplicadas.txt")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# ===== PALAVRAS PADRÃO =====
PALAVRAS_CHAVE = [
  "angular", "",  "pleno", "senior", "desenvolvedor", "aws", "cloud" , ".net"
]

# ===== CONFIG =====
def carregar_config():
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

config = carregar_config()

cidade = config.get("cidade", "São Paulo - SP")
modalidade = config.get("modalidade", "pj")
vaga = config.get("vaga", random.choice(config.get("skills", PALAVRAS_CHAVE)))
salario = config.get("salario", "15000")
skills = config.get("skills", "")
nome_usuario = config.get("nome", "Seu Nome")
email_usuario = config.get("email", "email@email.com")
telefone_usuario = config.get("telefone", "11999999999")

# ===== GERAR URL =====
def gerar_url():
    print(f"🔎 Buscando por: {vaga}")
    return f"https://www.nerdin.com.br/vagas.php?busca={random.choice(config.get("vaga", PALAVRAS_CHAVE))}"

# ===== VAGAS APLICADAS =====
def carregar_vagas_aplicadas():
    try:
        with open(ARQUIVO_APLICADAS, "r") as f:
            return set(linha.strip() for linha in f.readlines())
    except FileNotFoundError:
        return set()

def salvar_vaga_aplicada(link):
    vagas = carregar_vagas_aplicadas()
    if link in vagas:
        return

    with open(ARQUIVO_APLICADAS, "a") as f:
        f.write(link + "\n")
    print(f"💾 Salvo: {link}")

# ===== DRIVER =====
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# ⚠️ Se der erro, comente a linha abaixo
options.add_argument(r"--user-data-dir=C:\chrome-bot")

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
            aria = (el.get_attribute("aria-label") or "").lower()
            tag = el.tag_name.lower()

            texto = f"{nome} {placeholder} {aria}"

            if tag in ["input", "textarea"]:
                if el.get_attribute("value"):
                    continue

                el.click()
                esperar()

                if "nome" in texto:
                    el.send_keys(nome_usuario)

                elif "email" in texto:
                    el.send_keys(email_usuario)

                elif "telefone" in texto or "celular" in texto:
                    el.send_keys(telefone_usuario)

                elif "cidade" in texto:
                    el.send_keys(cidade)

                elif "funcao" in texto or "vaga" in texto:
                    el.send_keys(vaga)

                elif "salario" in texto or "pretensao" in texto:
                    el.clear()
                    el.send_keys(str(salario))

                elif "habilidade" in texto or "skill" in texto:
                    el.send_keys(skills)

                elif "disponibilidade" in texto:
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

# ===== PROCESSAR =====
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
            return False

        clicar_seguro(botao)
        esperar()

        return processar_formulario()

    except Exception as e:
        print("Erro aplicar:", e)
        return False

# ===== LOOP =====
def executar():
    url = gerar_url()
    driver.get(url)
    esperar()

    vagas_aplicadas = carregar_vagas_aplicadas()
    links = pegar_links_vagas()

    print(f"{len(links)} vagas encontradas")

    for i, link in enumerate(links):
        if link in vagas_aplicadas:
            print(f"⏭️ Já aplicada: {link}")
            continue

        try:
            print(f"\n🚀 Vaga {i+1}")
            print(link)

            driver.get(link)
            esperar()

            sucesso = aplicar_vaga()

            if sucesso:
                salvar_vaga_aplicada(link)

            driver.get(url)
            esperar()

        except Exception as e:
            print("Erro:", e)
            driver.get(url)
            esperar()

# ===== START =====
executar()