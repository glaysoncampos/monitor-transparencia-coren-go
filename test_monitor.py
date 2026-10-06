import unittest
from unittest.mock import patch
import monitor
from gerar_dashboard import renderizar


class MonitorTests(unittest.TestCase):
    def fonte(self, titulo='Contratos setembro 2026', caminho=None):
        return {'caminho': caminho or ['LICITAÇÕES', 'Contratos', '2026'], 'tipo':'listas-arquivos', 'url':'https://example.org/lista', 'estado':'ok', 'registros':[{'titulo':titulo, 'arquivo':'arquivo.pdf', 'descricao':'', 'anexo_id':'id', 'data_upload':'05/10/2026'}]}

    def test_upload_2026_nao_valida_documento_2025(self):
        self.assertEqual(monitor.evidencias(self.fonte('Contratos 2025'),2026),([],[]))

    def test_ramo_2026_com_titulo_sem_ano(self):
        aceitos, _ = monitor.evidencias(self.fonte('Contratos setembro'),2026)
        self.assertEqual(len(aceitos),1)

    def test_sem_ano_exige_verificacao(self):
        aceitos, incertos = monitor.evidencias(self.fonte('Contratos setembro',['LICITAÇÕES','Contratos']),2026)
        self.assertFalse(aceitos)
        self.assertEqual(len(incertos),1)

    def test_menu_nao_equivale_a_publicacao(self):
        fonte=self.fonte(); fonte['registros']=[]
        item={'menu':'LICITAÇÕES','obrigacao_pdf':'Contratos','componentes':[['CONTRATOS']]}
        self.assertEqual(monitor.avaliar(item,[fonte],2026)['status'],'nao_identificado')

    def test_falha_nao_vira_ausencia(self):
        fonte=self.fonte();fonte.update(estado='erro',motivo='Timeout')
        item={'menu':'LICITAÇÕES','obrigacao_pdf':'Contratos','componentes':[['CONTRATOS']]}
        self.assertEqual(monitor.avaliar(item,[fonte],2026)['status'],'erro')

    def test_menu_preserva_pai_navegavel_e_filtra_anos(self):
        itens=[{'label':'Portarias','url':'#','children':[
            {'label':'2025','url':'https://example.org/2025'},
            {'label':'2026','url':'https://example.org/2026','children':[{'label':'Julho','url':'https://example.org/julho'}]}]}]
        fontes=list(monitor.percorrer_menu(itens,2026))
        self.assertEqual(len(fontes),2)
        self.assertEqual(fontes[-1]['caminho'],['Portarias','2026','Julho'])

    def test_info_permanente_pode_ter_publicacao_anterior(self):
        aceitos,_=monitor.evidencias(self.fonte('Organograma 2024'),2026,fixo=True)
        self.assertEqual(len(aceitos),1)

    def test_sem_anexo_nao_confirma(self):
        fonte=self.fonte();fonte['registros'][0]['anexo_id']=''
        aceitos,incertos=monitor.evidencias(fonte,2026)
        self.assertFalse(aceitos);self.assertTrue(incertos)

    def test_conteudo_em_construcao(self):
        fonte={'caminho':['INSTITUCIONAL','Prazo'],'url_original':'#publico/Conteudos?id=ea5e9acf-a23a-4a7e-86f9-d63d989c5215'}
        with patch('monitor.get_json',return_value={'titulo':'Prazo','texto':'Em constru&ccedil;&atilde;o!'}):
            self.assertFalse(monitor.coletar_fonte(fonte)['registros'])

    def test_falha_menu_interrompe_coleta(self):
        with patch('monitor.get_json',return_value=[]):
            with self.assertRaises(ValueError):monitor.executar(2026)

    def test_link_externo_nao_valida_documento(self):
        fonte={'caminho':['LICITAÇÕES','Licitações'],'url_original':'#publico/LinksExternos?id=688073f1-3331-4543-90dd-8b162936e38b'}
        with patch('monitor.get_json',return_value={'linkExterno':'https://example.org'}):
            self.assertEqual(monitor.coletar_fonte(fonte)['estado'],'manual')

    def test_html_escapado(self):
        fonte=self.fonte('<script>alert(1)</script> Contratos 2026')
        item={'menu':'LICITAÇÕES','obrigacao_pdf':'Contratos','componentes':[['CONTRATOS']]}
        dados={'ano':2026,'verificado_em':'2026-10-05T17:00:00-03:00','portal':monitor.BASE,'fontes':[fonte],'resultados':[monitor.avaliar(item,[fonte],2026)]}
        html=renderizar(dados)
        self.assertNotIn('<script>',html)
        self.assertIn('&lt;script&gt;',html)


if __name__=='__main__':unittest.main()
