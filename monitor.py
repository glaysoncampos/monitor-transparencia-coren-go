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

    # ============================================================
    # INSTITUCIONAL
    # ============================================================

    {
        "menu": "INSTITUCIONAL",
        "obrigacao_pdf": "Organograma",
        "componentes": [
            ["ORGANOGRAMA"]
        ],
        "prazo": "Quando houver atualização"
    },

    {
        "menu": "INSTITUCIONAL",
        "obrigacao_pdf": "Competências / Regimento Interno",
        "componentes": [
            ["COMPETENCIAS"],
            ["REGIMENTO INTERNO", "REGIMENTO INTERNO COREN-GO"]
        ],
        "prazo": "Quando houver atualização"
    },

    {
        "menu": "INSTITUCIONAL",
        "obrigacao_pdf": "Endereço / Horário / Prazo para prestação de serviços",
        "componentes": [
            ["CONSELHO REGIONAL", "ENDERECO"],
            ["HORARIO DE ATENDIMENTO"],
            ["PRAZO PARA PRESTACAO DOS SERVICOS"]
        ],
        "prazo": "Quando houver atualização"
    },

    {
        "menu": "INSTITUCIONAL",
        "obrigacao_pdf": "Projetos, Programas e Ações",
        "componentes": [
            ["PROJETOS"],
            ["PROGRAMAS"],
            ["ACOES"]
        ],
        "prazo": "Anual"
    },

    {
        "menu": "INSTITUCIONAL",
        "obrigacao_pdf": "Plenário / Diretoria / Reuniões / Calendário / Atas / Agenda / Pareceres",
        "componentes": [
            ["PLENARIO"],
            ["DIRETORIA"],
            ["CALENDARIO DE REUNIOES", "REUNIOES"],
            ["ATAS DO PLENARIO", "ATAS"],
            ["AGENDA DA PRESIDENTE", "AGENDA"],
            ["PARECERES"]
        ],
        "prazo": "Mensal"
    },

    # ============================================================
    # LEGISLAÇÃO
    # ============================================================

    {
        "menu": "LEGISLAÇÃO",
        "obrigacao_pdf": "Portarias / Resolução / Leis",
        "componentes": [
            ["PORTARIAS"],
            ["RESOLUCOES", "RESOLUCAO"],
            ["LEIS"]
        ],
        "prazo": "Mensal"
    },

    # ============================================================
    # FINANCEIRO
    # ============================================================

    {
        "menu": "FINANCEIRO",
        "obrigacao_pdf": "Demonstrações Contábeis",
        "componentes": [
            ["DEMONSTRACOES CONTABEIS", "BALANCETE"]
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "FINANCEIRO",
        "obrigacao_pdf": "Demonstração de Despesas e Receitas",
        "componentes": [
            ["COMPARATIVO DE RECEITA", "RECEITAS"],
            ["COMPARATIVO DE DESPESAS", "DESPESAS"]
        ],
        "prazo": "Trimestral"
    },

    {
        "menu": "FINANCEIRO",
        "obrigacao_pdf": "Relação de Empenhos",
        "componentes": [
            ["RELACAO DE EMPENHOS", "EMPENHOS"]
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "FINANCEIRO",
        "obrigacao_pdf": "Centro de Custo",
        "componentes": [
            ["CENTRO DE CUSTO", "CENTRO DE CUSTOS"]
        ],
        "prazo": "Mensal"
    },

    # ============================================================
    # RELATÓRIOS
    # ============================================================

    {
        "menu": "RELATÓRIOS",
        "obrigacao_pdf": "Documentos Classificados e Desclassificados",
        "componentes": [
            ["DOCUMENTOS CLASSIFICADOS"],
            ["DOCUMENTOS DESCLASSIFICADOS"]
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "RELATÓRIOS",
        "obrigacao_pdf": "Controle Externo",
        "componentes": [
            ["CONTROLE EXTERNO", "TCU"]
        ],
        "prazo": "Anual"
    },

    {
        "menu": "RELATÓRIOS",
        "obrigacao_pdf": "Controle Interno",
        "componentes": [
            ["CONTROLE INTERNO", "PLANO DE ATIVIDADES DA CONTROLADORIA"]
        ],
        "prazo": "Semestral"
    },

    # ============================================================
    # LICITAÇÕES
    # ============================================================

    {
        "menu": "LICITAÇÕES",
        "obrigacao_pdf": "Licitações / Dispensas e Inexigibilidades",
        "componentes": [
            ["LICITACOES"],
            ["DISPENSA"],
            ["INEXIGIBILIDADE"]
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "LICITAÇÕES",
        "obrigacao_pdf": "Contratos",
        "componentes": [
            ["CONTRATOS"]
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "LICITAÇÕES",
        "obrigacao_pdf": "Convênios",
        "componentes": [
            ["CONVENIOS"]
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "LICITAÇÕES",
        "obrigacao_pdf": "Obras / Aquisições",
        "componentes": [
            ["OBRAS"],
            ["AQUISICOES"]
        ],
        "prazo": "Quando houver"
    },

    # ============================================================
    # VIAGENS
    # ============================================================

    {
        "menu": "VIAGENS",
        "obrigacao_pdf": "Passagens",
        "componentes": [
            ["PASSAGENS"]
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "VIAGENS",
        "obrigacao_pdf": "Diárias",
        "componentes": [
            ["DIARIAS"]
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "VIAGENS",
        "obrigacao_pdf": "Auxílio Representação",
        "componentes": [
            ["AUXILIO REPRESENTACAO"]
        ],
        "prazo": "Mensal"
    },

    # ============================================================
    # GESTÃO DE PESSOAS
    # ============================================================

    {
        "menu": "GESTÃO DE PESSOAS",
        "obrigacao_pdf": "Contatos dos empregados",
        "componentes": [
            ["CONTATOS", "CONTATO PROFISSIONAL"]
        ],
        "prazo": "Quando houver mudança"
    },

    {
        "menu": "GESTÃO DE PESSOAS",
        "obrigacao_pdf": "Plano de Cargos e Salários / Acordo Coletivo",
        "componentes": [
            ["PLANO DE CARGOS", "PLANO DE CARGOS E SALARIOS"],
            ["ACORDO COLETIVO"]
        ],
        "prazo": "Quando houver atualização"
    },

    {
        "menu": "GESTÃO DE PESSOAS",
        "obrigacao_pdf": "Remuneração dos Empregados e Estagiários",
        "componentes": [
            ["REMUNERACAO DE EMPREGADOS", "REMUNERACAO DOS EMPREGADOS"],
            ["ESTAGIARIOS"]
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "GESTÃO DE PESSOAS",
        "obrigacao_pdf": "Jetons",
        "componentes": [
            ["JETON", "JETONS"]
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "GESTÃO DE PESSOAS",
        "obrigacao_pdf": "Pessoal com cargos e currículo",
        "componentes": [
            ["RELACAO DOS EMPREGADOS COM CARGOS", "PESSOAL COM CARGOS"],
            ["CURRICULO"]
        ],
        "prazo": "Quando houver alteração"
    },

    # ============================================================
    # PRESTAÇÃO DE CONTAS
    # ============================================================

    {
        "menu": "PRESTAÇÃO DE CONTAS",
        "obrigacao_pdf": "Relatórios de Gestão",
        "componentes": [
            ["RELATORIO DE GESTAO", "RELATORIOS DE GESTAO"]
        ],
        "prazo": "Anual"
    },

    {
        "menu": "PRESTAÇÃO DE CONTAS",
        "obrigacao_pdf": "Boletim Informativo",
        "componentes": [
            ["BOLETIM INFORMATIVO"]
        ],
        "prazo": "Trimestral"
    },

    # ============================================================
    # PEDIDOS DE INFORMAÇÃO
    # ============================================================

    {
        "menu": "PEDIDOS DE INFORMAÇÃO",
        "obrigacao_pdf": "e-SIC",
        "componentes": [
            ["E-SIC", "ESIC"]
        ],
        "prazo": "Quando houver alteração"
    },

    {
        "menu": "PEDIDOS DE INFORMAÇÃO",
        "obrigacao_pdf": "Cartilha da CGU",
        "componentes": [
            ["CARTILHA DA CGU", "CARTILHA DA CGU PARA ACESSO A INFORMACAO"]
        ],
        "prazo": "Sem prazo definido no anexo"
    },

    {
        "menu": "PEDIDOS DE INFORMAÇÃO",
        "obrigacao_pdf": "Relatório Ouvidoria",
        "componentes": [
            ["OUVIDORIA", "RELATORIO OUVIDORIA", "RELATORIO DA OUVIDORIA"]
        ],
        "prazo": "Mensal"
    },

    {
        "menu": "PEDIDOS DE INFORMAÇÃO",
        "obrigacao_pdf": "Perguntas Frequentes",
        "componentes": [
            ["PERGUNTAS FREQUENTES", "FAQ"]
        ],
        "prazo": "Anual"
    },

    # ============================================================
    # DADOS ABERTOS
    # ============================================================

    {
        "menu": "DADOS ABERTOS",
        "obrigacao_pdf": "Catálogo de Dados Abertos / PDA",
        "componentes": [
            ["PDA", "PLANO DE DADOS ABERTOS"],
            ["CATALOGO DE DADOS ABERTOS", "DADOS ABERTOS"]
        ],
        "prazo": "Quando houver atualização"
    }
]


print("=" * 72)
print("AUDITORIA ESTRUTURAL DO PORTAL DA TRANSPARÊNCIA DO COREN GOIÁS")
print("=" * 72)

try:

    resposta = requests.get(
        URL,
        headers=HEADERS,
        timeout=60
    )

    resposta.raise_for_status()

    print("\n✅ Portal acessado com sucesso.")

    conteudo = normalizar(resposta.text)

    completos = 0
    parciais = 0
    ausentes = 0

    menu_atual = None

    for item in obrigacoes:

        if menu_atual != item["menu"]:

            menu_atual = item["menu"]

            print("\n")
            print("=" * 72)
            print(menu_atual)
            print("=" * 72)

        componentes_encontrados = []
        componentes_ausentes = []

        for componente in item["componentes"]:

            encontrou_componente = False
            termo_encontrado = None

            for termo in componente:

                termo_normalizado = normalizar(termo)

                if termo_normalizado in conteudo:
                    encontrou_componente = True
                    termo_encontrado = termo
                    break

            if encontrou_componente:
                componentes_encontrados.append(termo_encontrado)

            else:
                componentes_ausentes.append(" / ".join(componente))


        total_componentes = len(item["componentes"])
        total_encontrados = len(componentes_encontrados)

        print(f"\nObrigação: {item['obrigacao_pdf']}")
        print(f"Prazo: {item['prazo']}")

        if total_encontrados == total_componentes:

            completos += 1

            print("🟢 COMPLETO")

            print(
                "Componentes encontrados: "
                + ", ".join(componentes_encontrados)
            )

        elif total_encontrados > 0:

            parciais += 1

            print("🟡 PARCIAL")

            print(
                "Encontrado: "
                + ", ".join(componentes_encontrados)
            )

            print(
                "Faltando: "
                + ", ".join(componentes_ausentes)
            )

        else:

            ausentes += 1

            print("🔴 NÃO IDENTIFICADO")

            print(
                "Procuramos por: "
                + ", ".join(componentes_ausentes)
            )


    total = len(obrigacoes)

    percentual_completo = (completos / total) * 100

    percentual_estrutural = (
        (completos + (parciais * 0.5)) / total
    ) * 100


    print("\n")
    print("=" * 72)
    print("RESUMO DA AUDITORIA ESTRUTURAL")
    print("=" * 72)

    print(f"Total de obrigações verificadas: {total}")
    print(f"🟢 Completas: {completos}")
    print(f"🟡 Parciais: {parciais}")
    print(f"🔴 Não identificadas: {ausentes}")

    print(
        f"Conformidade integral: "
        f"{percentual_completo:.1f}%"
    )

    print(
        f"Índice estrutural ponderado: "
        f"{percentual_estrutural:.1f}%"
    )

    print("\nATENÇÃO:")
    print(
        "Este resultado verifica a presença estrutural dos componentes "
        "exigidos pelo PDF."
    )

    print(
        "Ainda não verifica a data da última publicação, "
        "a atualização dos documentos ou o cumprimento dos prazos."
    )


except requests.exceptions.Timeout:

    print(
        "❌ O Portal demorou mais de 60 segundos para responder."
    )


except requests.exceptions.RequestException as erro:

    print("❌ Erro ao acessar o Portal da Transparência.")
    print(erro)
