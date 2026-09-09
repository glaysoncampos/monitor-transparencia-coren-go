import requests

url = "https://coren-go.implanta.net.br/portaltransparencia/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/152.0.0.0 Safari/537.36"
    )
}

print("Iniciando verificação do Portal da Transparência do Coren Goiás...")

try:
    resposta = requests.get(
        url,
        headers=headers,
        timeout=60
    )

    if resposta.status_code == 200:
        print("✅ Portal acessado com sucesso.")

        conteudo = resposta.text.upper()

        if "ORGANOGRAMA" in conteudo:
            print("✅ ORGANOGRAMA encontrado no Portal.")
        else:
            print("❌ ORGANOGRAMA não encontrado no conteúdo inicial do Portal.")

    else:
        print(f"❌ Erro ao acessar o Portal. Código: {resposta.status_code}")

except requests.exceptions.Timeout:
    print("❌ O Portal demorou mais de 60 segundos para responder.")

except requests.exceptions.RequestException as erro:
    print("❌ Erro de conexão com o Portal.")
    print(erro)
