import requests
import html
import unicodedata

URL = "https://coren-go.implanta.net.br/portaltransparencia/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/152.0.0.0 Safari/537.36"
    )
}


def normalizar(texto):
    texto = html.unescape(texto)
    texto = texto.upper()

    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    return " ".join(texto.split())


obrigacoes = [

    # INSTITUCIONAL

    {
        "menu": "INSTITUCIONAL",
        "obrigacao_pdf": "Organograma",
        "procurar": ["ORGANOGRAMA"],
        "prazo": "Quando houver atualização"
    },

    {
        "menu": "INSTITUCIONAL",
        "obrigacao_pdf": "Competências / Regimento Interno",
        "procurar": [
            "COMPETENCIAS",
            "REGIMENTO INTERNO",
            "REGIMENTO INTERNO COREN-GO"
        ],
        "prazo": "Quando houver atualização"
    },

    {
        "menu": "INSTITUCIONAL",
        "obrigacao_pdf": "Endereço / Horário / Prazo para prestação de serviços",
        "procurar": [
            "CONSELHO REGIONAL",
            "HORARIO DE ATENDIMENTO",
            "PRAZO PARA PRESTACAO DOS SERVICOS"
        ],
        "prazo": "Quando houver atualização"
    },

    {
        "menu": "INSTITUCIONAL",
        "obrigacao_pdf": "Projetos, Programas e Ações",
        "procurar": [
            "PROJETOS",
            "PROGRAMAS",
            "ACOES"
        ],
        "prazo": "Anual"
    },

    {
        "menu": "INSTITUCIONAL",
        "obrigacao_pdf": "Plenário / Diretoria / Reuniões / Calendário / Atas / Agenda / Pareceres",
        "procurar": [
            "PLENARIO",
            "DIRETORIA",
            "ATAS DO PLENARIO",
            "AGENDA DA PRESIDENTE",
            "PARECERES"
        ],
        "prazo": "Mensal"
    },

    # LEGISLAÇÃO

    {
        "menu": "LEGISLAÇÃO",
        "obrigacao_pdf": "Portarias / Resolução / Leis",
        "procurar": [
            "PORTARIAS",
            "RESOLUCOES",
            "LEIS"
        ],
        "prazo": "Mensal"
    },

    # FINANCEIRO

    {
        "menu": "FINANCEIRO",
        "obrigacao_pdf": "Demonstrações Contábeis",
        "procurar": [
            "DEMONSTRACOES CONTABEIS",
            "BALANCETE",
            "BALANCO FINANCEIRO",
            "BALANCO PATRIMONIAL",
            "BALANCO ORCAMENTARIO"
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "FINANCEIRO",
        "obrigacao_pdf": "Demonstração de Despesas e Receitas",
        "procurar": [
            "DEMONSTRACOES DE DESPESAS E RECEITAS",
            "COMPARATIVO DE RECEITA",
            "COMPARATIVO DE DESPESAS"
        ],
        "prazo": "Trimestral"
    },

    {
        "menu": "FINANCEIRO",
        "obrigacao_pdf": "Relação de Empenhos",
        "procurar": [
            "RELACAO DE EMPENHOS",
            "EMPENHOS"
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "FINANCEIRO",
        "obrigacao_pdf": "Centro de Custo",
        "procurar": [
            "CENTRO DE CUSTO",
            "CENTRO DE CUSTOS"
        ],
        "prazo": "Mensal"
    },

    # RELATÓRIOS

    {
        "menu": "RELATÓRIOS",
        "obrigacao_pdf": "Documentos Classificados e Desclassificados",
        "procurar": [
            "DOCUMENTOS CLASSIFICADOS",
            "DOCUMENTOS DESCLASSIFICADOS"
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "RELATÓRIOS",
        "obrigacao_pdf": "Controle Externo",
        "procurar": [
            "CONTROLE EXTERNO",
            "TCU"
        ],
        "prazo": "Anual"
    },

    {
        "menu": "RELATÓRIOS",
        "obrigacao_pdf": "Controle Interno",
        "procurar": [
            "CONTROLE INTERNO",
            "PLANO DE ATIVIDADES DA CONTROLADORIA"
        ],
        "prazo": "Semestral"
    },

    # LICITAÇÕES

    {
        "menu": "LICITAÇÕES",
        "obrigacao_pdf": "Licitações / Dispensas e Inexigibilidades",
        "procurar": [
            "LICITACOES",
            "DISPENSA",
            "INEXIGIBILIDADE"
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "LICITAÇÕES",
        "obrigacao_pdf": "Contratos",
        "procurar": ["CONTRATOS"],
        "prazo": "Mensal"
    },

    {
        "menu": "LICITAÇÕES",
        "obrigacao_pdf": "Convênios",
        "procurar": ["CONVENIOS"],
        "prazo": "Mensal"
    },

    {
        "menu": "LICITAÇÕES",
        "obrigacao_pdf": "Obras / Aquisições",
        "procurar": [
            "OBRAS",
            "AQUISICOES"
        ],
        "prazo": "Quando houver"
    },

    # VIAGENS

    {
        "menu": "VIAGENS",
        "obrigacao_pdf": "Passagens",
        "procurar": ["PASSAGENS"],
        "prazo": "Mensal"
    },

    {
        "menu": "VIAGENS",
        "obrigacao_pdf": "Diárias",
        "procurar": ["DIARIAS"],
        "prazo": "Mensal"
    },

    {
        "menu": "VIAGENS",
        "obrigacao_pdf": "Auxílio Representação",
        "procurar": ["AUXILIO REPRESENTACAO"],
        "prazo": "Mensal"
    },

    # GESTÃO DE PESSOAS

    {
        "menu": "GESTÃO DE PESSOAS",
        "obrigacao_pdf": "Contatos dos empregados",
        "procurar": [
            "CONTATOS",
            "CONTATO PROFISSIONAL"
        ],
        "prazo": "Quando houver mudança"
    },

    {
        "menu": "GESTÃO DE PESSOAS",
        "obrigacao_pdf": "Plano de Cargos e Salários / Acordo Coletivo",
        "procurar": [
            "PLANO DE CARGOS",
            "PLANO DE CARGOS E SALARIOS",
            "ACORDO COLETIVO"
        ],
        "prazo": "Quando houver atualização"
    },

    {
        "menu": "GESTÃO DE PESSOAS",
        "obrigacao_pdf": "Remuneração dos Empregados e Estagiários",
        "procurar": [
            "REMUNERACAO DE EMPREGADOS",
            "REMUNERACAO DOS EMPREGADOS",
            "ESTAGIARIOS"
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "GESTÃO DE PESSOAS",
        "obrigacao_pdf": "Jetons",
        "procurar": [
            "JETON",
            "JETONS"
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "GESTÃO DE PESSOAS",
        "obrigacao_pdf": "Pessoal com cargos e currículo",
        "procurar": [
            "RELACAO DOS EMPREGADOS COM CARGOS",
            "PESSOAL COM CARGOS",
            "CURRICULO"
        ],
        "prazo": "Quando houver alteração"
    },

    # PRESTAÇÃO DE CONTAS

    {
        "menu": "PRESTAÇÃO DE CONTAS",
        "obrigacao_pdf": "Relatórios de Gestão",
        "procurar": [
            "RELATORIO DE GESTAO",
            "RELATORIOS DE GESTAO"
        ],
        "prazo": "Anual"
    },

    {
        "menu": "PRESTAÇÃO DE CONTAS",
        "obrigacao_pdf": "Boletim Informativo",
        "procurar": ["BOLETIM INFORMATIVO"],
        "prazo": "Trimestral"
    },

    # PEDIDOS DE INFORMAÇÃO

    {
        "menu": "PEDIDOS DE INFORMAÇÃO",
        "obrigacao_pdf": "e-SIC",
        "procurar": [
            "E-SIC",
            "ESIC"
        ],
        "prazo": "Quando houver alteração"
    },

    {
        "menu": "PEDIDOS DE INFORMAÇÃO",
        "obrigacao_pdf": "Cartilha da CGU",
        "procurar": [
            "CARTILHA DA CGU",
            "CARTILHA DA CGU PARA ACESSO A INFORMACAO"
        ],
        "prazo": "Sem prazo definido no anexo"
    },

    {
        "menu": "PEDIDOS DE INFORMAÇÃO",
        "obrigacao_pdf": "Relatório Ouvidoria",
        "procurar": [
            "OUVIDORIA",
            "RELATORIO OUVIDORIA",
            "RELATORIO DA OUVIDORIA"
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "PEDIDOS DE INFORMAÇÃO",
        "obrigacao_pdf": "Perguntas Frequentes",
        "procurar": [
            "PERGUNTAS FREQUENTES",
            "FAQ"
        ],
        "prazo": "Anual"
    },

    # DADOS ABERTOS

    {
        "menu": "DADOS ABERTOS",
        "obrigacao_pdf": "Catálogo de Dados Abertos / PDA",
        "procurar": [
            "DADOS ABERTOS",
            "CATALOGO DE DADOS ABERTOS",
            "PDA",
            "PLANO DE DADOS ABERTOS"
        ],
        "prazo": "Quando houver atualização"
    }
]


print("=" * 70)
print("MONITOR DO PORTAL DA TRANSPARÊNCIA DO COREN GOIÁS")
print("=" * 70)

try:

    resposta = requests.get(
        URL,
        headers=HEADERS,
        timeout=60
    )

    resposta.raise_for_status()

    print("\n✅ Portal acessado com sucesso.\n")

    conteudo = normalizar(resposta.text)

    encontrados = 0
    nao_encontrados = 0

    menu_atual = None

    for item in obrigacoes:

        if menu_atual != item["menu"]:

            menu_atual = item["menu"]

            print("\n")
            print("=" * 70)
            print(menu_atual)
            print("=" * 70)

        termos_encontrados = []

        for termo in item["procurar"]:

            termo_normalizado = normalizar(termo)

            if termo_normalizado in conteudo:
                termos_encontrados.append(termo)

        print(f"\nObrigação: {item['obrigacao_pdf']}")
        print(f"Prazo: {item['prazo']}")

        if termos_encontrados:

            encontrados += 1

            print("✅ IDENTIFICADO NO PORTAL")
            print(
                "Correspondência encontrada: "
                + ", ".join(termos_encontrados)
            )

        else:

            nao_encontrados += 1

            print("❌ NÃO IDENTIFICADO")
            print(
                "Procuramos por: "
                + ", ".join(item["procurar"])
            )


    total = len(obrigacoes)

    percentual = (encontrados / total) * 100

    print("\n")
    print("=" * 70)
    print("RESUMO DA VERIFICAÇÃO")
    print("=" * 70)

    print(f"Total de obrigações verificadas: {total}")
    print(f"✅ Identificadas: {encontrados}")
    print(f"❌ Não identificadas: {nao_encontrados}")
    print(f"Conformidade estrutural inicial: {percentual:.1f}%")

    print("\nIMPORTANTE:")
    print(
        "Esta etapa verifica apenas se a obrigação ou um nome equivalente "
        "foi localizado no Portal."
    )
    print(
        "Ainda não confirma se os documentos estão atualizados "
        "ou dentro do prazo."
    )


except requests.exceptions.Timeout:

    print(
        "❌ O Portal demorou mais de 60 segundos para responder."
    )


except requests.exceptions.RequestException as erro:

    print("❌ Erro ao acessar o Portal da Transparência.")
    print(erro)
