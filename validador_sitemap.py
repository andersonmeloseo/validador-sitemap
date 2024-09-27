# Bibliotecas necessárias:
# requests: Para fazer requisições HTTP
# Comando para instalar: !pip install requests

# xml.etree.ElementTree: Biblioteca padrão do Python, usada para manipular XML
# Não precisa instalar, já faz parte da biblioteca padrão do Python.

# collections.defaultdict: Biblioteca padrão do Python, usada para contagem de ocorrências
# Não precisa instalar, já faz parte da biblioteca padrão do Python.

import requests
import xml.etree.ElementTree as ET
from collections import defaultdict


def is_valid_xml(content):
    """
    Função para validar se o conteúdo é XML.
    """
    try:
        ET.fromstring(content)
        return True
    except ET.ParseError:
        return False


def get_sitemap_urls(sitemap_url):
    """
    Função para obter todas as URLs do sitemap, incluindo URLs aninhadas.
    """
    urls = []
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()  # Verifica se houve erro na requisição
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o sitemap: {e}")
        return []

    # Verifica se o conteúdo recebido é XML válido
    if not is_valid_xml(response.content):
        print(f"Erro: O conteúdo recebido de {sitemap_url} não é um XML válido.")
        return []

    try:
        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()

        # Namespaces comuns para sitemaps
        namespaces = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        # Procurando por URLs no sitemap
        for url in root.findall(".//sitemap:loc", namespaces):
            nested_sitemap_url = url.text.strip()
            if nested_sitemap_url.endswith(
                ".xml"
            ):  # Verifica se a URL é de um sitemap XML
                print(f"Encontrado sitemap aninhado: {nested_sitemap_url}")
                urls += get_sitemap_urls(
                    nested_sitemap_url
                )  # Chamando recursivamente para sitemaps aninhados
            else:
                print(f"Ignorando URL que não é um sitemap: {nested_sitemap_url}")

        # Adicionando URLs encontradas no sitemap
        for url in root.findall(".//sitemap:url/sitemap:loc", namespaces):
            urls.append(url.text.strip())

    except ET.ParseError as e:
        print(f"Erro ao processar o sitemap XML: {e}")

    return urls


def check_url_status(url):
    """
    Função para verificar o status de uma URL.
    """
    try:
        response = requests.get(url, timeout=10)
        return response.status_code
    except requests.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return None


def analyze_sitemap(sitemap_url):
    """
    Função principal para análise do sitemap e verificação das URLs.
    """
    print(f"Iniciando a análise do sitemap: {sitemap_url}")

    urls = get_sitemap_urls(sitemap_url)
    if not urls:
        print("Nenhuma URL encontrada no sitemap.")
        return

    status_code_count = defaultdict(int)
    error_urls = []

    # Verificando o status de cada URL
    for url in urls:
        print(f"Verificando {url}...")
        status_code = check_url_status(url)
        if status_code:
            status_code_count[status_code] += 1
            if status_code != 200:
                error_urls.append((url, status_code))

    # Relatório final
    print("\nRelatório Final:")
    print(f"Total de URLs analisadas: {len(urls)}")
    print(f"Distribuição dos códigos de status HTTP:")

    for code, count in status_code_count.items():
        print(f" - {code}: {count} URLs")

    if error_urls:
        print("\nURLs com erro:")
        for url, code in error_urls:
            print(f" - {url} (Erro: {code})")
    else:
        print("\nNenhum erro encontrado nas URLs.")


# Solicitando a URL do sitemap
if __name__ == "__main__":
    sitemap_url = input("Digite a URL do sitemap: ")
    analyze_sitemap(sitemap_url)
