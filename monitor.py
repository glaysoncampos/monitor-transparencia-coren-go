import requests

url = "https://coren-go.implanta.net.br/portaltransparencia/"

print("Iniciando verificação do Portal da Transparência do Coren Goiás...")

try:
    resposta = requests.get(url, timeout=30)

    if resposta.status_code == 200:
        print("✅ Portal acessado com sucesso.")

        conteudo = resposta.text.upper()

        if "ORGANOGRAMA" in conteudo:
            print("✅ ORGANOGRAMA encontrado no Portal.")
        else:
            print("❌ ORGANOGRAMA não encontrado no conteúdo inicial do Portal.")

    else:
        print(f"❌ Erro ao acessar o Portal. Código: {resposta.status_code}")

except Exception as erro:
    print("❌ Ocorreu um erro ao acessar o Portal.")
    print(erro)
