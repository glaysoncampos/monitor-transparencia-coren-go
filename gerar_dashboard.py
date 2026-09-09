import subprocess
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from html import escape


# Executa o monitor que já está funcionando
processo = subprocess.run(
    ["python", "monitor.py"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)

saida = processo.stdout

print(saida)

if processo.returncode != 0:
    print("Erro ao executar monitor.py")
    print(processo.stderr)
    raise SystemExit(1)


# ---------------------------------------------------------
# LÊ O RESUMO GERADO PELO MONITOR
# ---------------------------------------------------------

def pegar_numero(padrao):
    resultado = re.search(padrao, saida)

    if resultado:
        return int(resultado.group(1))

    return 0


total = pegar_numero(
    r"Total de obrigações verificadas:\s*(\d+)"
)

completas = pegar_numero(
    r"Completas:\s*(\d+)"
)

parciais = pegar_numero(
    r"Parciais:\s*(\d+)"
)

ausentes = pegar_numero(
    r"Não identificadas:\s*(\d+)"
)


resultado_conformidade = re.search(
    r"Conformidade integral:\s*([\d.,]+)%",
    saida
)

resultado_ponderado = re.search(
    r"Índice estrutural ponderado:\s*([\d.,]+)%",
    saida
)

conformidade = (
    resultado_conformidade.group(1)
    if resultado_conformidade
    else "0"
)

ponderado = (
    resultado_ponderado.group(1)
    if resultado_ponderado
    else "0"
)


# ---------------------------------------------------------
# IDENTIFICA ITENS PARCIAIS E NÃO IDENTIFICADOS
# ---------------------------------------------------------

linhas = saida.splitlines()

obrigacao_atual = ""
status_atual = ""
detalhe = ""

problemas = []

for linha in linhas:

    linha = linha.strip()

    if linha.startswith("Obrigação:"):
        obrigacao_atual = linha.replace(
            "Obrigação:", ""
        ).strip()

    elif "🟡 PARCIAL" in linha:
        status_atual = "Parcial"
        detalhe = ""

    elif "🔴 NÃO IDENTIFICADO" in linha:
        status_atual = "Não identificado"
        detalhe = ""

    elif linha.startswith("Encontrado:"):
        detalhe = linha

    elif linha.startswith("Faltando:"):

        detalhe_final = (
            detalhe + ". " + linha
            if detalhe
            else linha
        )

        problemas.append({
            "status": "Parcial",
            "obrigacao": obrigacao_atual,
            "resultado": detalhe_final
        })

        status_atual = ""

    elif linha.startswith("Procuramos por:"):

        problemas.append({
            "status": "Não identificado",
            "obrigacao": obrigacao_atual,
            "resultado": linha
        })

        status_atual = ""


# ---------------------------------------------------------
# DATA DA VERIFICAÇÃO
# ---------------------------------------------------------

agora = datetime.now(
    ZoneInfo("America/Sao_Paulo")
)

data_verificacao = agora.strftime(
    "%d/%m/%Y às %H:%M"
)


# ---------------------------------------------------------
# MONTA AS LINHAS DA TABELA
# ---------------------------------------------------------

linhas_tabela = ""

for problema in problemas:

    if problema["status"] == "Parcial":

        classe = "amarelo"
        simbolo = "🟡"
        situacao = "Parcial"

    else:

        classe = "vermelho"
        simbolo = "🔴"
        situacao = "Não identificado"

    resultado = problema["resultado"]

    resultado = resultado.replace(
        "Encontrado:",
        "Encontrado:"
    )

    resultado = resultado.replace(
        "Faltando:",
        "Faltando:"
    )

    resultado = resultado.replace(
        "Procuramos por:",
        "Nenhuma correspondência localizada. Termos pesquisados:"
    )

    linhas_tabela += f"""
    <tr>
        <td class="{classe}">
            {simbolo} {situacao}
        </td>
        <td>
            {escape(problema["obrigacao"])}
        </td>
        <td>
            {escape(resultado)}
        </td>
    </tr>
    """


# ---------------------------------------------------------
# GERA O NOVO INDEX.HTML
# ---------------------------------------------------------

pagina = f"""<!DOCTYPE html>
<html lang="pt-BR">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>
Monitor do Portal da Transparência | Coren-GO
</title>

<style>

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f7fb;
    color: #172033;
}}

header {{
    background: #245b9e;
    color: white;
    padding: 32px 20px;
}}

.container {{
    width: min(1100px, calc(100% - 32px));
    margin: auto;
}}

h1 {{
    margin: 0 0 8px;
}}

main {{
    padding: 28px 0;
}}

.aviso {{
    background: #eef5ff;
    border: 1px solid #cfe1f7;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 24px;
}}

.atualizacao {{
    margin-top: 8px;
    color: #475467;
}}

.cards {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}}

.card {{
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #e4e7ec;
}}

.titulo {{
    font-size: 13px;
    color: #667085;
    text-transform: uppercase;
}}

.numero {{
    margin-top: 8px;
    font-size: 34px;
    font-weight: bold;
}}

.verde {{
    color: #1f9d63;
}}

.amarelo {{
    color: #d9a514;
}}

.vermelho {{
    color: #d64545;
}}

.azul {{
    color: #245b9e;
}}

.conformidade {{
    margin-top: 22px;
    background: white;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #e4e7ec;
}}

table {{
    width: 100%;
    margin-top: 24px;
    border-collapse: collapse;
    background: white;
}}

th, td {{
    padding: 14px;
    border-bottom: 1px solid #e4e7ec;
    text-align: left;
}}

th {{
    background: #f8fafc;
}}

footer {{
    margin-top: 30px;
    text-align: center;
    color: #667085;
    padding: 20px;
}}

@media (max-width: 800px) {{

    .cards {{
        grid-template-columns: repeat(2, 1fr);
    }}

}}

@media (max-width: 500px) {{

    .cards {{
        grid-template-columns: 1fr;
    }}

}}

</style>

</head>

<body>

<header>

<div class="container">

<h1>
Monitor do Portal da Transparência
</h1>

<p>
Coren-GO | Verificação estrutural das obrigações de transparência
</p>

</div>

</header>


<main class="container">

<div class="aviso">

<strong>Escopo atual:</strong>

esta análise verifica automaticamente
se os itens exigidos foram identificados
no Portal da Transparência.

<div class="atualizacao">

<strong>Última verificação automática:</strong>
{data_verificacao}

</div>

</div>


<div class="cards">

<div class="card">

<div class="titulo">
Obrigações verificadas
</div>

<div class="numero azul">
{total}
</div>

</div>


<div class="card">

<div class="titulo">
Completas
</div>

<div class="numero verde">
{completas}
</div>

</div>


<div class="card">

<div class="titulo">
Parciais
</div>

<div class="numero amarelo">
{parciais}
</div>

</div>


<div class="card">

<div class="titulo">
Não identificadas
</div>

<div class="numero vermelho">
{ausentes}
</div>

</div>

</div>


<div class="conformidade">

<div class="titulo">
Conformidade integral
</div>

<div class="numero verde">
{conformidade}%
</div>

<p>
Índice estrutural ponderado:
<strong>{ponderado}%</strong>
</p>

</div>


<h2>
Pontos para verificação
</h2>


<table>

<thead>

<tr>

<th>Situação</th>
<th>Obrigação</th>
<th>Resultado</th>

</tr>

</thead>


<tbody>

{linhas_tabela}

</tbody>

</table>


<footer>

Painel atualizado automaticamente
pelo GitHub Actions

</footer>


</main>

</body>

</html>
"""


with open(
    "index.html",
    "w",
    encoding="utf-8"
) as arquivo:

    arquivo.write(pagina)


print(
    "✅ index.html atualizado automaticamente."
)

print(
    f"✅ Última verificação: {data_verificacao}"
)
