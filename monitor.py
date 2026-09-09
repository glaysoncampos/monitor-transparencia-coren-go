import requests

url = "https://coren-go.implanta.net.br/portaltransparencia/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/152.0.0.0 Safari/537.36"
    )
}

itens = [
    {
        "nome": "ORGANOGRAMA",
        "prazo": "Quando houver atualização"
    },
    {
        "nome": "COMPETÊNCIAS",
        "prazo": "Quando houver atualização"
    },
    {
        "nome": "PROJETOS",
        "prazo": "Anual"
    }
]

print("Iniciando verificação do Portal da Transparência do Coren Goiás...")

try:
    resposta = requests.get(
        url,
        headers=headers,
        timeout=60
    )

    if resposta.status_code == 200:
        print("✅ Portal acessado com sucesso.\n")

        conteudo = resposta.text.upper()

        for item in itens:
            nome = item["nome"]
            prazo = item["prazo"]

            print(f"Verificando: {nome}")

            if nome in conteudo:
                print("✅ Item encontrado no Portal.")
            else:
                print("❌ Item não encontrado no Portal.")

            print(f"Prazo previsto: {prazo}")
            print("-----------------------------")

    else:
        print(f"❌ Erro ao acessar o Portal. Código: {resposta.status_code}")

except requests.exceptions.Timeout:
    print("❌ O Portal demorou mais de 60 segundos para responder.")

except requests.exceptions.RequestException as erro:
    print("❌ Erro de conexão com o Portal.")
    print(erro)
