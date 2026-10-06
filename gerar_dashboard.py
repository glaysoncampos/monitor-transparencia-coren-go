"""Gera painel somente após uma coleta válida; não interpreta stdout."""
import argparse
from collections import Counter
from datetime import datetime
from html import escape
import json
from pathlib import Path
from monitor import executar

STATUS = {
    'localizado': ('Evidência localizada', 'verde'),
    'parcial': ('Parcial', 'amarelo'),
    'nao_identificado': ('Não identificado na coleta', 'vermelho'),
    'manual': ('Verificação manual', 'azul'),
    'erro': ('Falha de coleta', 'cinza'),
}


def link(url, texto):
    if not url.startswith(('https://', 'http://')):
        return escape(texto)
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(texto)}</a>'


def renderizar(dados):
    contagem = Counter(r['status'] for r in dados['resultados'])
    total = len(dados['resultados'])
    linhas = []
    for item in dados['resultados']:
        detalhes = []
        for componente in item['componentes']:
            rotulo, cor = STATUS[componente['status']]
            trecho = f'<p><strong>{escape(" / ".join(componente["termos"]))}</strong>: <span class="{cor}">{rotulo}</span></p>'
            for prova in componente['evidencias']:
                trecho += '<p>' + link(prova['url'], prova['caminho']) + '</p><ul>'
                for registro in prova['registros']:
                    data = ('; upload: ' + registro['data_upload']) if registro.get('data_upload') else ''
                    trecho += '<li>' + escape(registro['titulo'] + data) + '</li>'
                trecho += '</ul>'
                if prova['permanente']:
                    trecho += '<p class="nota">Informação permanente localizada. Vigência material não validada.</p>'
            for pendencia in componente['pendencias'] + componente['erros']:
                trecho += '<p>' + link(pendencia['url'], pendencia['caminho']) + ': ' + escape(pendencia['motivo']) + '</p>'
            if componente['status'] == 'nao_identificado':
                trecho += '<p>Não foi localizada evidência correspondente no recorte da coleta. Isso não comprova descumprimento.</p>'
                for url in componente['fontes_consultadas']:
                    trecho += '<p>' + link(url, 'Conferir seção consultada') + '</p>'
            detalhes.append(trecho)
        label, cor = STATUS[item['status']]
        linhas.append(f'<tr><td class="{cor}">{label}</td><td><strong>{escape(item["obrigacao_pdf"])}</strong><p class="nota">{escape(item["menu"])}</p></td><td><details><summary>Ver componentes e evidências</summary>{"".join(detalhes)}</details></td></tr>')
    cards = f'<div class="card"><span>Obrigações</span><b>{total}</b></div>'
    for chave, (label, cor) in STATUS.items():
        cards += f'<div class="card"><span>{label}</span><b class="{cor}">{contagem[chave]}</b></div>'
    cobertura = f'{100 * contagem["localizado"] / total:.1f}'.replace('.', ',') if total else '0'
    data = datetime.fromisoformat(dados['verificado_em']).strftime('%d/%m/%Y às %H:%M')
    erros = sum(f['estado'] == 'erro' for f in dados['fontes'])
    aviso_erro = f'<p class="vermelho">Coleta incompleta: {erros} seções apresentaram falha. Consulte os detalhes antes de usar os resultados.</p>' if erros else ''
    fontes = ''.join('<li>' + link(f['url'], ' > '.join(f['caminho'])) + ': ' + escape({'ok':'consulta realizada', 'manual':'verificação manual necessária', 'erro':'falha de coleta'}[f['estado']]) + '</li>' for f in dados['fontes'])
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Monitor da Transparência {dados['ano']} | Coren-GO</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;font-family:Arial,sans-serif;background:#f4f7fb;color:#172033;line-height:1.5}}header{{background:#245b9e;color:white;padding:28px 0}}.container{{width:min(1200px,calc(100% - 32px));margin:auto}}h1{{margin:0;font-size:clamp(24px,4vw,36px)}}main{{padding:24px 0}}.aviso,.card,.indice{{padding:20px;border:1px solid #dce5ef;border-radius:14px;background:white}}.aviso{{background:#eef5ff;margin-bottom:20px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}.card span{{font-size:13px;color:#55657a;text-transform:uppercase}}.card b{{display:block;font-size:32px}}.verde{{color:#147044}}.amarelo{{color:#8a6200}}.vermelho{{color:#b92335}}.azul{{color:#245b9e}}.cinza,.nota{{color:#596577}}.nota{{font-size:13px}}.indice{{margin-top:20px}}.indice b{{font-size:30px;color:#245b9e}}.tabela{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;background:white;margin:20px 0}}th,td{{text-align:left;padding:16px;border-bottom:1px solid #e4e7ec;vertical-align:top}}th{{background:#edf2f8}}td:first-child{{min-width:135px}}td:nth-child(2){{min-width:230px}}td:nth-child(3){{width:52%;min-width:250px}}a{{color:#145ca4;overflow-wrap:anywhere}}summary{{cursor:pointer;color:#145ca4;font-weight:bold}}details p{{margin:10px 0}}li{{margin-bottom:6px}}footer{{padding:20px 0;color:#596577}}@media(max-width:600px){{.cards{{grid-template-columns:repeat(2,1fr)}}.card{{padding:14px}}}}@media print{{header{{background:white;color:black}}details> *{{display:block!important}}.tabela{{overflow:visible}}}}
</style></head><body><header><div class="container"><h1>Monitor do Portal da Transparência</h1><p>Coren-GO | Exercício {dados['ano']}</p></div></header>
<main class="container"><div class="aviso"><strong>Escopo da verificação</strong><p>Consulta dos menus e do conteúdo das seções do portal. Documentos periódicos são selecionados pelo exercício {dados['ano']}, identificado no título, na descrição ou no ramo do menu. A data de upload não substitui o exercício.</p><p>Informações permanentes são apresentadas separadamente nos detalhes. PDFs não são auditados internamente. Links externos e relatórios interativos sem validação são encaminhados para verificação manual.</p><p>Última coleta: <strong>{data} (Brasília)</strong>. {link(dados['portal'], 'Abrir portal oficial')}</p>{aviso_erro}</div>
<div class="cards">{cards}</div><div class="indice"><span>Cobertura de evidências de todos os componentes</span><br><b>{cobertura}%</b><p>{contagem['localizado']} de {total} obrigações com evidência localizada para todos os componentes. Este indicador não certifica conformidade jurídica, conteúdo dos anexos ou cumprimento de prazos.</p></div>
<h2>Obrigações e evidências</h2><div class="tabela"><table><thead><tr><th>Situação</th><th>Obrigação</th><th>Resultado da coleta</th></tr></thead><tbody>{''.join(linhas)}</tbody></table></div>
<details><summary>Seções consultadas ({len(dados['fontes'])})</summary><ul>{fontes}</ul></details>
<footer>Matriz de 32 obrigações preservada do projeto original. Prazos e base normativa exigem validação da Controladoria. Atualização automática pelo GitHub Actions.</footer></main></body></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ano', type=int, default=2026)
    parser.add_argument('--dados', help='JSON de uma coleta existente; não consulta a internet.')
    args = parser.parse_args()
    if not 2000 <= args.ano <= 2100:
        parser.error('Exercício inválido.')
    dados = json.loads(Path(args.dados).read_text(encoding='utf-8')) if args.dados else executar(args.ano)
    pagina = renderizar(dados)
    # Nada é sobrescrito se a coleta ou a renderização falhar.
    Path('index.html.tmp').write_text(pagina, encoding='utf-8')
    Path('index.html.tmp').replace('index.html')
    print(f'Painel atualizado: exercício {dados["ano"]}, {len(dados["resultados"])} obrigações.')


if __name__ == '__main__':
    main()
