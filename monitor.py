"""Monitor de evidências públicas do portal Implanta, com recorte por exercício."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import html
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

BASE = 'https://coren-go.implanta.net.br/portaltransparencia/'
API = BASE + 'internal-api/'
ROOT = Path(__file__).resolve().parent


def normalizar(texto):
    texto = re.sub(r'<[^>]+>', ' ', html.unescape(str(texto or '')))
    texto = unicodedata.normalize('NFD', texto.upper())
    return ' '.join(''.join(c for c in texto if unicodedata.category(c) != 'Mn').split())


def anos(texto):
    return set(re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)', str(texto)))


def corresponde(termos, texto):
    texto = normalizar(texto)
    return any(re.search(r'(?<!\w)' + re.escape(normalizar(t)) + r'(?!\w)', texto) for t in termos)


def get_json(caminho):
    req = Request(API + caminho, headers={'Accept': 'application/json', 'User-Agent': 'CorenGO-MonitorTransparencia/2.0'})
    with urlopen(req, timeout=45) as resposta:
        envelope = json.load(resposta)
    if not isinstance(envelope, dict) or 'data' not in envelope or envelope.get('status', {}).get('success') is not True:
        raise ValueError('Resposta inesperada da API pública; coleta não validada.')
    return envelope['data']


def percorrer_menu(itens, ano, caminho=()):
    """Mantém pais navegáveis e filhos; elimina ramos exclusivos de outros anos."""
    for item in itens:
        label = str(item.get('label', '')).strip()
        encontrados = anos(label)
        # Intervalos, como PPA 2025-2027, também podem abranger o exercício.
        intervalo = re.search(r'((?:19|20)\d{2})\s*[-–/]\s*((?:19|20)\d{2})', label)
        vigente = intervalo and int(intervalo[1]) <= ano <= int(intervalo[2])
        if encontrados and str(ano) not in encontrados and not vigente:
            continue
        atual = caminho + (label,)
        url = item.get('url') or ''
        if url and url != '#':
            yield {'caminho': list(atual), 'url_original': url}
        yield from percorrer_menu(item.get('children') or [], ano, atual)


ROTAS = {
    'publico/listas': ('listas-arquivos', 'idListaArquivo'),
    'publico/conteudos': ('conteudos', 'idConteudo'),
    'publico/linksexternos': ('links-externos', 'idLinkExterno'),
}
RELATORIOS = {
    'publico/orcamentofinancas': 'orcamento-financas',
    'publico/licitacoescontratos': 'licitacoes-contratos',
    'publico/diversos': 'diversos',
}


def resolver_url(original):
    fragmento = urlsplit(original).fragment
    rota, _, query = fragmento.partition('?')
    params = parse_qs(query)
    tipo, campo = ROTAS.get(rota.lower(), (None, None))
    identificador = params.get('id', [''])[0]
    if tipo and re.fullmatch(r'[0-9a-fA-F-]{36}', identificador):
        filtro = {campo: identificador}
        if tipo == 'listas-arquivos':
            filtro['list'] = 'true'
        return tipo, BASE + tipo + '/' + identificador, tipo + '?' + urlencode(filtro)
    if rota.lower() in RELATORIOS:
        return 'relatorio', BASE + 'relatorios/' + RELATORIOS[rota.lower()] + ('?' + query if query else ''), None
    if original.startswith(('https://', 'http://')):
        return 'externo', original, None
    return 'desconhecido', BASE + '#' + fragmento, None


def coletar_fonte(fonte):
    tipo, url, endpoint = resolver_url(fonte['url_original'])
    resultado = dict(fonte, tipo=tipo, url=url, estado='ok', registros=[])
    if not endpoint:
        resultado.update(estado='manual', motivo='Relatório interativo ou destino externo: selecionar 2026 e conferir o conteúdo.')
        return resultado
    try:
        dados = get_json(endpoint)
        if tipo == 'listas-arquivos':
            if not isinstance(dados, list):
                raise ValueError('Formato da lista de arquivos alterado.')
            for item in dados:
                anexo = item.get('anexo') or {}
                if not isinstance(item.get('nome'), str) or not isinstance(anexo, dict):
                    raise ValueError('Registro de arquivo em formato inesperado.')
                resultado['registros'].append({
                    'titulo': item['nome'], 'descricao': item.get('descricao') or '',
                    'arquivo': anexo.get('nome') or '', 'anexo_id': anexo.get('id') or '',
                    'data_upload': item.get('dataUpload') or '',
                })
        elif tipo == 'conteudos':
            if not isinstance(dados, dict) or 'texto' not in dados:
                raise ValueError('Formato do conteúdo alterado.')
            texto = normalizar(dados.get('texto'))
            if texto and not corresponde(['EM CONSTRUCAO', 'EM ATUALIZACAO', 'EM BREVE'], texto):
                resultado['registros'] = [{'titulo': dados.get('titulo') or '', 'descricao': texto, 'arquivo': '', 'data_upload': ''}]
            else:
                resultado['motivo'] = 'Conteúdo vazio ou em construção.'
        else:
            if not isinstance(dados, dict) or 'linkExterno' not in dados:
                raise ValueError('Formato do link externo alterado.')
            destino = dados.get('linkExterno') or ''
            resultado.update(estado='manual', motivo='Link cadastrado; conteúdo e exercício do destino requerem verificação.', destino=destino)
    except Exception as erro:
        resultado.update(estado='erro', motivo=f'{type(erro).__name__}: {erro}')
    return resultado


# Informações permanentes não precisam conter o ano no título.
# Sua vigência material ainda depende de revisão humana.
PERMANENTES = {
    'Organograma', 'Competências / Regimento Interno',
    'Endereço / Horário / Prazo para prestação de serviços',
    'Contatos dos empregados', 'Plano de Cargos e Salários / Acordo Coletivo',
    'e-SIC', 'Cartilha da CGU', 'Perguntas Frequentes', 'Catálogo de Dados Abertos / PDA',
}


def permanente(item, termos):
    return item['obrigacao_pdf'] in PERMANENTES or termos in [['PLENARIO'], ['DIRETORIA'], ['LEIS'], ['RESOLUCOES', 'RESOLUCAO']]


def evidencias(fonte, ano, fixo=False):
    aceitos, incertos = [], []
    ano_ramo = str(ano) in anos(' / '.join(fonte['caminho']))
    for registro in fonte['registros']:
        if fonte['tipo'] == 'listas-arquivos' and not registro.get('anexo_id'):
            incertos.append(registro)
            continue
        # Data de upload NÃO determina o exercício do documento.
        texto = ' '.join(registro.get(k, '') for k in ('titulo', 'descricao', 'arquivo'))
        referencia = anos(texto)
        if fixo or str(ano) in referencia or (ano_ramo and not referencia):
            aceitos.append(registro)
        elif not referencia:
            incertos.append(registro)
    return aceitos, incertos


def avaliar(item, fontes, ano):
    componentes = []
    menus = {normalizar(item['menu'])}
    if item['obrigacao_pdf'] == 'Auxílio Representação':
        menus.add('GESTAO DE PESSOAS')
    if item['obrigacao_pdf'] == 'Relatório Ouvidoria':
        menus.add('RELATORIOS')
    for termos in item['componentes']:
        candidatos = [f for f in fontes if normalizar(f['caminho'][0]) in menus and corresponde(termos, ' / '.join(f['caminho'][1:]))]
        provas, pendencias, erros = [], [], []
        for f in candidatos:
            base = {'caminho': ' > '.join(f['caminho']), 'url': f['url']}
            if f['estado'] != 'ok':
                (erros if f['estado'] == 'erro' else pendencias).append(dict(base, motivo=f['motivo']))
                continue
            aceitos, incertos = evidencias(f, ano, permanente(item, termos))
            if aceitos:
                provas.append(dict(base, registros=aceitos, permanente=permanente(item, termos)))
            if incertos:
                pendencias.append(dict(base, motivo='Há registros sem exercício identificável ou sem anexo confirmado.'))
        if provas:
            status = 'localizado'
        elif erros:
            status = 'erro'
        elif pendencias:
            status = 'manual'
        else:
            status = 'nao_identificado'
        componentes.append({'termos': termos, 'status': status, 'evidencias': provas, 'pendencias': pendencias, 'erros': erros,
                            'fontes_consultadas': [f['url'] for f in candidatos]})
    estados = [c['status'] for c in componentes]
    if all(e == 'localizado' for e in estados):
        status = 'localizado'
    elif 'localizado' in estados:
        status = 'parcial'
    elif 'erro' in estados:
        status = 'erro'
    elif 'manual' in estados:
        status = 'manual'
    else:
        status = 'nao_identificado'
    return dict(item, status=status, componentes=componentes)


def executar(ano=2026):
    itens = get_json('menu')
    if not isinstance(itens, list) or len(itens) < 5 or not any(normalizar(x.get('label')) == 'INSTITUCIONAL' for x in itens):
        raise ValueError('Menu incompleto ou em formato inesperado. Resultado anterior preservado.')
    fontes = list(percorrer_menu(itens, ano))
    if len(fontes) < 20:
        raise ValueError('Menu sem seções suficientes. Resultado anterior preservado.')
    # Consulta cada URL uma vez, preservando todos os caminhos em que ela aparece.
    unicos = {f['url_original']: f for f in fontes}
    with ThreadPoolExecutor(max_workers=4) as pool:
        dados = dict(zip(unicos, pool.map(coletar_fonte, unicos.values())))
    coletadas = [dict(dados[f['url_original']], caminho=f['caminho']) for f in fontes]
    acessiveis = [f for f in coletadas if f['tipo'] in ('listas-arquivos', 'conteudos', 'links-externos')]
    if not any(f['estado'] != 'erro' for f in acessiveis):
        raise ValueError('Todas as consultas falharam. Resultado anterior preservado.')
    obrigacoes = json.loads((ROOT / 'obrigacoes.json').read_text(encoding='utf-8'))
    return {
        'ano': ano, 'verificado_em': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat(),
        'portal': BASE + '#publico/inicio', 'fontes': coletadas,
        'resultados': [avaliar(item, coletadas, ano) for item in obrigacoes],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ano', type=int, default=2026)
    parser.add_argument('--saida', default='resultado.json')
    args = parser.parse_args()
    if not 2000 <= args.ano <= 2100:
        parser.error('Exercício inválido.')
    resultado = executar(args.ano)
    destino = Path(args.saida)
    temporario = destino.with_suffix('.tmp')
    temporario.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')
    temporario.replace(destino)
    print(f'Exercício {args.ano}: {len(resultado["fontes"])} seções consultadas.')


if __name__ == '__main__':
    main()
