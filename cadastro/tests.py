from django.test import TestCase, Client
from django.urls import resolve, reverse, Resolver404
from django.contrib.auth.models import User
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils import timezone
from django.db.models.deletion import ProtectedError
from django.urls.exceptions import Resolver404
from cadastro.models.clientes import CadastroPessoaFisica, CadastroPessoaJuridica
from .models import CadastroPessoaFisica, CadastroPessoaJuridica
from cadastro.models.produtos import CategoriaProduto, Produto
from cadastro.models.vendas import CompraCliente, CompraClienteHasProduto
from cadastro.forms.clientes import CadastroPessoaFisicaForm, CadastroPessoaJuridicaForm
from cadastro.forms.produtos import ProdutoForm, CategoriaProdutoForm
from cadastro.forms.vendas import CompraClienteForm, CompraClienteHasProdutoForm
from datetime import date, timedelta
from django.db import IntegrityError
import json
from .models import CadastroPessoaFisica, DadosGraficos
from cadastro import views
from cadastro.models import CategoriaProduto, CadastroPessoaFisica


class Testmodel(TestCase):
    
    def setUp(self):
        pass
        
    #Teste 1.1 - Cadastro de Pessoas Físicas
    def test_criar_cliente_pf_com_sucesso(self):
        cliente = CadastroPessoaFisica.objects.create(
            nome_completo="João da Silva",
            cpf="12345678901",
            data_de_nascimento="1990-05-20",
            email="joao@email.com",
            telefone="11999999999"
        )
        self.assertEqual(cliente.nome_completo, "João da Silva")
        self.assertEqual(cliente.cpf, "12345678901")
        self.assertTrue(cliente.id_cliente_pf) # Verifica se o ID foi criado
    
    def test_cpf_unico(self):
        CadastroPessoaFisica.objects.create(nome_completo="Cliente 1", cpf="11111111111")
        with self.assertRaises(IntegrityError):
            CadastroPessoaFisica.objects.create(nome_completo="Cliente 2", cpf="11111111111")

    def test_str_retorna_nome_completo(self):
        """Testa que o método __str__ retorna o nome_completo."""
        cliente = CadastroPessoaFisica.objects.create(
            nome_completo="Maria Souza",
            cpf="98765432100"
        )
        self.assertEqual(str(cliente), "Maria Souza")

    def test_str_retorna_nome_completo(self):
        """Testa que o método __str__ retorna o nome_completo."""
        cliente = CadastroPessoaFisica.objects.create(
            nome_completo="Maria Souza",
            cpf="98765432100"
        )
        self.assertEqual(str(cliente), "Maria Souza")

    def test_criar_pf_apenas_campos_obrigatorios(self):
        """Testa a criação de um PF apenas com os campos obrigatórios."""
        cliente = CadastroPessoaFisica.objects.create(
            nome_completo="Carlos",
            cpf="55555555555"
        )
        self.assertEqual(cliente.nome_completo, "Carlos")
        self.assertIsNone(cliente.data_de_nascimento)
        self.assertIsNone(cliente.email)

    #Teste 1.2 - 
    
    #Teste 1.3 - Categoria Produto

    def test_criacao_com_dados_validos(self):
        categoria = CategoriaProduto.objects.create(
            nome_da_categoria="Garrafa térmica",
            descricao_da_categoria="Bazar"
        )
        self.assertIsNotNone(categoria.id_categoria_produto)
        self.assertEqual(categoria.nome_da_categoria, "Garrafa térmica")

    def test_nome_da_categoria_unico(self):
        CategoriaProduto.objects.create(nome_da_categoria="Livros")
        with self.assertRaises(IntegrityError):
            CategoriaProduto.objects.create(nome_da_categoria="Livros")

    def test_str_retorna_nome(self):
        categoria = CategoriaProduto.objects.create(nome_da_categoria="Canetas")
        self.assertEqual(str(categoria), "Canetas")

    def test_ordenacao_padrao(self):
        CategoriaProduto.objects.create(nome_da_categoria="Caneta")
        CategoriaProduto.objects.create(nome_da_categoria="Apontador")
        CategoriaProduto.objects.create(nome_da_categoria="Borracha")
        categorias = CategoriaProduto.objects.all()
        self.assertEqual(categorias[0].nome_da_categoria, "Apontador")
        self.assertEqual(categorias[1].nome_da_categoria, "Borracha")
        self.assertEqual(categorias[2].nome_da_categoria, "Caneta")

# 3.2 - Cadastro_cliente

class CadastroClienteViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.force_login(self.user) # Faz login com esse usuário

        self.url_fisica = reverse('cadastro_cliente', args=['fisica'])
        self.url_juridica = reverse('cadastro_cliente', args=['juridica'])

    def test_get_renderiza_form_pf(self):
        response = self.client.get(self.url_fisica)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CadastroPessoaFisicaForm)
        self.assertEqual(response.context['tipo'], 'fisica')
        self.assertIn('Pessoa Física', response.context['titulo'])

    def test_get_renderiza_form_pj(self):
        response = self.client.get(self.url_juridica)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CadastroPessoaJuridicaForm)
        self.assertEqual(response.context['tipo'], 'juridica')
        self.assertIn('Pessoa Juridica', response.context['titulo'])


    def test_post_valido_cria_pf(self):
        qtd_antes = CadastroPessoaFisica.objects.count()

        dados_validos = {
            'nome_completo': 'João da Silva',
            'cpf': '12345678901', # 11 dígitos limpos
            'data_de_nascimento': '1995-05-20',
            'email': 'joao@exemplo.com',
            'telefone': '(21) 99999-9999',
            'cep': '20000000',
            'logradouro': 'Rua A',
            'complemento_endereco': 'Apto 1',
            'bairro': 'Centro',
            'cidade': 'Rio de Janeiro',
            'estado': 'RJ'
        }

        response = self.client.post(self.url_fisica, data=dados_validos)

        qtd_depois = CadastroPessoaFisica.objects.count()
        self.assertEqual(qtd_depois, qtd_antes + 1)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['mensagem_sucesso'])
        self.assertIn('cadastrado com sucesso', response.context['mensagem_sucesso'])

    def test_post_invalido_nao_cria_pf(self):
        qtd_antes = CadastroPessoaFisica.objects.count()

        dados_invalidos = {
            'nome_completo': '', # Obrigatório vazio
            'cpf': '123', # CPF muito curto
            'data_de_nascimento': '2050-01-01', # Data no futuro
            'email': 'joao',
            'telefone': '2222',
            'cep': '20000',
            'logradouro': 'Rua A',
            'bairro': 'Centro',
            'cidade': 'Rio de Janeiro',
            'estado': 'RJ'
        }

        response = self.client.post(self.url_fisica, data=dados_invalidos)

        qtd_depois = CadastroPessoaFisica.objects.count()
        self.assertEqual(qtd_depois, qtd_antes)

        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(response.context['form'].errors)


    #Teste 1.4 - Produtos
    def test_criacao_com_dados_validos(self):
        """Testa a criação com dados validos"""
        produto = Produto.objects.create(
            nome_do_produto = "Fichario"
        )

        produto.categorias.add(self.cat_caderno)
        self.assertEqual(produto.nome_do_produto, "Fichario")
        self.assertIn(self.cat_caderno, produto.categorias.all())

    def test_nome_do_produto_unico(self):
        """Testa se o nome do produto é unico"""
        Produto.objects.create(
            nome_do_produto = "Post-it"
        )

        with self.assertRaises(IntegrityError):
            Produto.objects.create(
                nome_do_produto = "Post-it"
            )
        
    def test_associacao_multiplas_categorias(self):
        """Associar um produto a multiplas categorias e verificar a associaçao"""
        produto = Produto.objects.create(
            nome_do_produto = "Folha de Fichario"
            )

        produto.categorias.add(self.cat_caderno, self.cat_papeis)
        self.assertEqual(produto.categorias.count(), 2)
        self.assertIn(self.cat_caderno, produto.categorias.all())
        self.assertIn(self.cat_caderno, produto.categorias.all())

    def test_related_name_categorias(self):

        prod1 = Produto.objects.create(nome_do_produto = "nota adesiva")
        prod2 = Produto.objects.create(nome_do_produto = "Cartao raspadinha")

        prod1.categorias.add(self.cat_papeis)
        prod2.categorias.add(self.cat_papeis)

        produtos_da_categoria = self.cat_papeis.produtos.all()

        self.assertEqual(produtos_da_categoria.count(), 2)
        self.assertIn(prod1, produtos_da_categoria)
        self.assertIn(prod2, produtos_da_categoria)

    def test_ordenacao_padrao(self):
        """Testa a ordenaçao padrao"""
        Produto.objects.create(nome_do_produto = "Caderno")
        Produto.objects.create(nome_do_produto = "Fichario")
        Produto.objects.create(nome_do_produto = "Folha")

        todos_produtos = Produto.objects.all()

        self.assertEqual(todos_produtos[0].nome_do_produto, "Caderno")
        self.assertEqual(todos_produtos[1].nome_do_produto, "Fichario")
        self.assertEqual(todos_produtos[2].nome_do_produto, "Folha")
        
    #Teste 1.5 - Cadastro Vendas
    def test_criar_venda_para_pf(self):
        """Testa a criação de uma venda vinculada a um Cliente PF."""
        cliente_pf = CadastroPessoaFisica.objects.create(nome_completo="Ana", cpf="22222222222")
        venda = CompraCliente.objects.create(
            cliente_fisico=cliente_pf,
            preco_total=150.00,
            pagamento_metodo="Cartão"
        )
        self.assertEqual(venda.cliente_fisico, cliente_pf)
        self.assertIsNone(venda.cliente_juridico)

    def test_criar_venda_para_pj(self):
        """Testa a criação de uma venda vinculada a um Cliente PJ."""
        cliente_pj = CadastroPessoaJuridica.objects.create(razao_social="Empresa X", cnpj="33333333333333")
        venda = CompraCliente.objects.create(
            cliente_juridico=cliente_pj,
            preco_total=500.00,
            pagamento_metodo="Boleto"
        )
        self.assertEqual(venda.cliente_juridico, cliente_pj)
        self.assertIsNone(venda.cliente_fisico)

    def test_data_preenchida_automaticamente(self):
        """Testa se o campo 'data' é preenchido com a data atual na criação."""
        venda = CompraCliente.objects.create(preco_total=50.00, pagamento_metodo="Dinheiro")
        self.assertIsNotNone(venda.data)
        self.assertEqual(venda.data, timezone.now().date())

    def test_on_delete_set_null(self):
        """Testa se a venda permanece com cliente nulo ao deletar o cliente."""
        cliente_pf = CadastroPessoaFisica.objects.create(nome_completo="Pedro", cpf="44444444444")
        venda = CompraCliente.objects.create(cliente_fisico=cliente_pf, preco_total=100.00, pagamento_metodo="Pix")
        
        # Deleta o cliente
        cliente_pf.delete()
        
        # Busca a venda novamente do banco de dados
        venda_atualizada = CompraCliente.objects.get(id=venda.id)
        self.assertIsNone(venda_atualizada.cliente_fisico)
        self.assertEqual(venda_atualizada.preco_total, 100.00) # A venda em si não foi afetada

    def test_criar_com_e_sem_frete(self):
        """Testa a criação de vendas com e sem valor de frete."""
        venda_com_frete = CompraCliente.objects.create(preco_total=100.00, frete=10.00, pagamento_metodo="Cartão")
        venda_sem_frete = CompraCliente.objects.create(preco_total=50.00, pagamento_metodo="Dinheiro")
        
        self.assertEqual(venda_com_frete.frete, 10.00)
        self.assertIsNone(venda_sem_frete.frete)        
    
        #Teste 1.6 - 

class FormTests(TestCase):

    #Teste 2.1 - CadastroPessoaFisicaForm e CadastroPessoaJuridicaForm    
    def test_form_pf_valido(self):
        """Testa a validação do formulário PF com dados corretos."""
        form_data = {
            'nome_completo': 'Teste Validado',
            'cpf': '12312312312',
            'data_de_nascimento': '1995-10-15',
            'email': 'valido@email.com'
        }
        form = CadastroPessoaFisicaForm(data=form_data)
        
        # Verificação final
        self.assertTrue(form.is_valid(), f"O formulário deveria ser válido. Erros: {form.errors}")

    def test_form_pf_campos_obrigatorios_vazios(self):
        """Testa a invalidação do formulário PF sem nome ou CPF."""
        # Sem nome
        form_data_sem_nome = {'cpf': '12312312312'}
        form = CadastroPessoaFisicaForm(data=form_data_sem_nome)
        self.assertFalse(form.is_valid())
        self.assertIn('nome_completo', form.errors)

        # Sem CPF
        form_data_sem_cpf = {'nome_completo': 'Nome Sem CPF'}
        form = CadastroPessoaFisicaForm(data=form_data_sem_cpf)
        self.assertFalse(form.is_valid())
        self.assertIn('cpf', form.errors)

    def test_form_pf_cpf_duplicado(self):
        """Testa a invalidação do formulário com um CPF já existente."""
        # Cria um cliente no banco para simular a duplicidade
        CadastroPessoaFisica.objects.create(nome_completo="Cliente Original", cpf="11122233344")
        
        # Tenta criar um novo formulário com o mesmo CPF
        form_data = {
            'nome_completo': 'Cliente Duplicado',
            'cpf': '11122233344'
        }
        form = CadastroPessoaFisicaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cpf', form.errors) # O erro deve estar no campo 'cpf'

#Teste 2.2 - ProdutoForm
class ProdutoFormTests(TestCase):
    """Testes para o ProdutoForm."""

    def setUp(self):
        """Cria uma categoria para ser usada nos testes."""
        self.categoria = CategoriaProduto.objects.create(nome_da_categoria="Categoria Teste")

    def test_produto_form_valido(self):
        """Testar validação com dados corretos (pelo menos uma categoria selecionada)."""
        form_data = {
            'nome_do_produto': 'Caneta Bic',
            'categorias': [self.categoria.id_categoria_produto] # Muitos-para-muitos usa uma lista de IDs
        }
        form = ProdutoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_produto_form_sem_categoria(self):
        """Testar o método clean() para garantir que falha se nenhuma categoria for selecionada."""
        form_data = {
            'nome_do_produto': 'Produto Sem Categoria',
            'categorias': [] # Lista vazia de categorias
        }
        form = ProdutoForm(data=form_data)
        self.assertFalse(form.is_valid())
        # O erro do clean() global aparece em '__all__'
        self.assertIn('Você deve selecionar pelo menos uma categoria para este produto.', form.errors['__all__'])

    def test_produto_form_nome_duplicado(self):
        """Testar invalidação com nome de produto duplicado."""
        # Cria o produto do teste com o mesmo formato que o form usa pra armazenagem dos dados (maiúsculas)
        Produto.objects.create(nome_do_produto="LÁPIS DE COR")
        
        # Tenta criar um novo formulário com o mesmo nome (que será transformado para maiúsculas)
        form_data = {
            'nome_do_produto': 'Lápis de Cor', # Pode ser em minúsculas
            'categorias': [self.categoria.id_categoria_produto]
        }
        form = ProdutoForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('nome_do_produto', form.errors)



    #Teste 2.3 - Categoria Produto Form
    def test_validacao_com_dados_corretos(self):
        """"Testar validacao com dados corretos"""
        form_data = { 
            'nome_da_categoria' : 'Cadernos',
            'descricao_da_categoria' : 'secao dos cadernos'
        }

        form = CategoriaProdutoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_nome_da_categoria(self):
        """"Evitar nomes em branco ou com apenas espaços"""
        form_data = {
            'nome_da_categoria' : '    ',
            'descricao_da_categoria' : 'qualquer descricao'
        }

        form = CategoriaProdutoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nome_da_categoria', form.errors)

    def test_invalidacao_nome_duplicado(self):
        """"Testar invalidacao com nome de categoria repetida"""
        CategoriaProduto.objects.create(
            nome_da_categoria = 'Cadernos',
            descricao_da_categoria = 'secao dos cadernos'
        )

        dados_duplicados = {
            'nome_da_categoria' :  'Cadernos',
            'descricao_da_categoria' : 'Outra descricao'
        }

        form = CategoriaProdutoForm(data=dados_duplicados)
        self.assertFalse(form.is_valid())
        self.assertIn('nome_da_categoria', form.errors)


    #Teste 2.4 - CompraClienteForm e CompraClienteHasProdutoForm
class VendaFormTests(TestCase):

    def setUp(self):
        # Criação de dados básicos necessários para os formulários
        self.cliente_pf = CadastroPessoaFisica.objects.create(
            nome_completo="Cliente Teste",
            cpf="12345678901"
        )
        self.categoria = CategoriaProduto.objects.create(
            nome_da_categoria="Escritório"
        )
        self.produto = Produto.objects.create(nome_do_produto="Caneta")
        self.produto.categorias.add(self.categoria)
        
        self.venda = CompraCliente.objects.create(
            cliente_fisico=self.cliente_pf,
            preco_total=100.00,
            pagamento_metodo="Dinheiro"
        )

    def test_compra_cliente_form_valido(self):
        
        form_data = {
            'cliente_fisico': self.cliente_pf.id_cliente_pf,
            'pagamento_metodo': 'Cartão de Crédito',
            'preco_total': '150.00'
        }
        form = CompraClienteForm(data=form_data)
        self.assertTrue(form.is_valid(), f"O formulário deveria ser válido. Erros: {form.errors}")

    def test_compra_cliente_has_produto_form_valido(self):
        
        form_data = {
            'venda': self.venda.id,
            'produto': self.produto.id_produto,
            'quantidade_produto': 2,
            'preco_unitario': 10.50
        }
        form = CompraClienteHasProdutoForm(data=form_data)
        self.assertTrue(form.is_valid(), f"O formulário deveria ser válido. Erros: {form.errors}")

    def test_compra_cliente_has_produto_form_invalido_campos_vazios(self):
        
        # Teste sem quantidade
        form_data = {
            'venda': self.venda.id,
            'produto': self.produto.id_produto,
            'quantidade_produto': '', 
            'preco_unitario': '10.00'
        }
        form = CompraClienteHasProdutoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade_produto', form.errors)

    def test_compra_cliente_form_invalido_preco_total_vazio(self):
       
        form_data = {
            'cliente_fisico': self.cliente_pf.id_cliente_pf,
            'pagamento_metodo': 'Pix',
            'preco_total': '' # Campo obrigatório vazio
        }
        form = CompraClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Verifica se o erro está no campo preco_total (assumindo que é required no form)
        self.assertIn('preco_total', form.errors)

class ViewCadastroVendaTests(TestCase):
    """Testes para a view de cadastro de vendas."""

    def setUp(self):
        """Configura o ambiente de teste: cria um usuário logado e dados base."""
        self.usuario = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        
        self.cliente_pf = CadastroPessoaFisica.objects.create(nome_completo="Cliente Teste", cpf="99888776655")
        
        self.categoria = CategoriaProduto.objects.create(nome_da_categoria="Categoria Teste")
        self.produto1 = Produto.objects.create(nome_do_produto="Produto A")
        self.produto1.categorias.add(self.categoria)
        self.produto2 = Produto.objects.create(nome_do_produto="Produto B")
        self.produto2.categorias.add(self.categoria)

    def test_cadastro_venda_get_renderiza_formularios(self):
        """GET: Testa se o formulário de venda e o formset de itens são renderizados."""
        url = reverse('cadastro_venda')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadastro/vendas/form.html')
        self.assertIn('form', response.context)
        self.assertIn('formset', response.context)

    def test_cadastro_venda_post_sucesso(self):
        """POST: Testa a criação de uma venda com 2 itens, cálculo e redirecionamento."""
        url = reverse('cadastro_venda')
        data = {
            # Dados do formulário principal (CompraCliente)
            'cliente_fisico': self.cliente_pf.id_cliente_pf,
            'pagamento_metodo': 'Cartão de Crédito',
            'frete': '15.50',
            
            # Dados do FormSet (itens da venda)
            'compraclientehasproduto_set-TOTAL_FORMS': '2',
            'compraclientehasproduto_set-INITIAL_FORMS': '0',
            'compraclientehasproduto_set-MIN_NUM_FORMS': '0',
            'compraclientehasproduto_set-MAX_NUM_FORMS': '1000',
            
            # Item 1
            'compraclientehasproduto_set-0-produto': self.produto1.id_produto,
            'compraclientehasproduto_set-0-quantidade_produto': '2',
            'compraclientehasproduto_set-0-preco_unitario': '10.00',
            
            # Item 2
            'compraclientehasproduto_set-1-produto': self.produto2.id_produto,
            'compraclientehasproduto_set-1-quantidade_produto': '1',
            'compraclientehasproduto_set-1-preco_unitario': '25.00',
        }
        
        response = self.client.post(url, data)
        
        # Verificações
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('lista_vendas'))
        
        self.assertEqual(CompraCliente.objects.count(), 1)
        self.assertEqual(CompraClienteHasProduto.objects.count(), 2)
        
        venda = CompraCliente.objects.first()
        # Cálculo esperado: (2 * 10.00) + (1 * 25.00) + 15.50 (frete) = 20.00 + 25.00 + 15.50 = 60.50
        self.assertEqual(float(venda.preco_total), 60.50)

    def test_cadastro_venda_post_falha_form_invalido(self):
        """POST (Falha): Testa que um formulário principal inválido não salva nada."""
        url = reverse('cadastro_venda')
        data = {
            # Dados inválidos (faltando método de pagamento)
            'cliente_fisico': self.cliente_pf.id_cliente_pf,
            'frete': '10.00',
            
            # Dados do FormSet (válidos, mas não devem ser salvos)
            'compraclientehasproduto_set-TOTAL_FORMS': '1',
            'compraclientehasproduto_set-INITIAL_FORMS': '0',
            'compraclientehasproduto_set-0-produto': self.produto1.id_produto,
            'compraclientehasproduto_set-0-quantidade_produto': '1',
            'compraclientehasproduto_set-0-preco_unitario': '10.00',
        }
        
        response = self.client.post(url, data)
        
        # A página deve ser reexibida (status 200), não redirecionada
        self.assertEqual(response.status_code, 200)
        # Nenhum objeto deve ter sido criado no banco
        self.assertEqual(CompraCliente.objects.count(), 0)
        self.assertEqual(CompraClienteHasProduto.objects.count(), 0)

    def test_cadastro_venda_post_falha_formset_invalido(self):
        """POST (Falha): Testa que um formset inválido não salva nada."""
        url = reverse('cadastro_venda')
        data = {
            # Dados do formulário principal (válidos)
            'cliente_fisico': self.cliente_pf.id_cliente_pf,
            'pagamento_metodo': 'Dinheiro',
            
            # Dados do FormSet (inválidos, faltando o produto)
            'compraclientehasproduto_set-TOTAL_FORMS': '1',
            'compraclientehasproduto_set-INITIAL_FORMS': '0',
            'compraclientehasproduto_set-0-quantidade_produto': '1',
            'compraclientehasproduto_set-0-preco_unitario': '10.00',
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CompraCliente.objects.count(), 0)
        self.assertEqual(CompraClienteHasProduto.objects.count(), 0)
    
    #Teste 3.1 - Geral (Aplicar a todas as views, exceto index) 
class TestAcessoGeralViews(TestCase):
  

    def setUp(self):
        self.usuario = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        
        # Lista de URLs para testar (excluindo index conforme solicitado)
        self.urls = [
            reverse('dashboard'),
            reverse('cadastro_cliente_pf'),
            reverse('cadastro_cliente_pj'),
            reverse('cadastro_produto'),
            reverse('cadastro_categoria'),
            reverse('cadastro_venda'),
            reverse('lista_clientes'),
            reverse('lista_produtos'),
            reverse('lista_vendas'),
            reverse('graficos'),
        ]

    def test_usuario_nao_logado_redirecionado(self):
        
        for url in self.urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                # Verifica se houve redirecionamento (302)
                self.assertEqual(response.status_code, 302)
                # Verifica se redireciona para a página de login
                self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_usuario_logado_recebe_status_200(self):
       
        self.client.login(username='testuser', password='12345')
        for url in self.urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200) 


    #Teste 3.2 - Cadastro de cliente


class CadastroClienteViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.force_login(self.user) # Faz login com esse usuário

        self.url_fisica = reverse('cadastro_cliente', args=['fisica'])
        self.url_juridica = reverse('cadastro_cliente', args=['juridica'])

    def test_get_renderiza_form_pf(self):
        response = self.client.get(self.url_fisica)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CadastroPessoaFisicaForm)
        self.assertEqual(response.context['tipo'], 'fisica')
        self.assertIn('Pessoa Física', response.context['titulo'])

    def test_get_renderiza_form_pj(self):
        response = self.client.get(self.url_juridica)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CadastroPessoaJuridicaForm)
        self.assertEqual(response.context['tipo'], 'juridica')
        self.assertIn('Pessoa Juridica', response.context['titulo'])


    def test_post_valido_cria_pf(self):
        qtd_antes = CadastroPessoaFisica.objects.count()

        dados_validos = {
            'nome_completo': 'João da Silva',
            'cpf': '12345678901', # 11 dígitos limpos
            'data_de_nascimento': '1995-05-20',
            'email': 'joao@exemplo.com',
            'telefone': '(21) 99999-9999',
            'cep': '20000000',
            'logradouro': 'Rua A',
            'complemento_endereco': 'Apto 1',
            'bairro': 'Centro',
            'cidade': 'Rio de Janeiro',
            'estado': 'RJ'
        }

        response = self.client.post(self.url_fisica, data=dados_validos)

        qtd_depois = CadastroPessoaFisica.objects.count()
        self.assertEqual(qtd_depois, qtd_antes + 1)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['mensagem_sucesso'])
        self.assertIn('cadastrado com sucesso', response.context['mensagem_sucesso'])

    def test_post_invalido_nao_cria_pf(self):
        qtd_antes = CadastroPessoaFisica.objects.count()

        dados_invalidos = {
            'nome_completo': '', # Obrigatório vazio
            'cpf': '123', # CPF muito curto
            'data_de_nascimento': '2050-01-01', # Data no futuro
            'email': 'joao',
            'telefone': '2222',
            'cep': '20000',
            'logradouro': 'Rua A',
            'bairro': 'Centro',
            'cidade': 'Rio de Janeiro',
            'estado': 'RJ'
        }

        response = self.client.post(self.url_fisica, data=dados_invalidos)

        qtd_depois = CadastroPessoaFisica.objects.count()
        self.assertEqual(qtd_depois, qtd_antes)

        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(response.context['form'].errors)


    #Teste 3.3 - Cadastro_produto, cadastro_categoria
class TestCadastroProdutoECategoria(TestCase):
    

    def setUp(self):
        self.usuario = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')


    def test_cadastro_produto_get_renderiza_form(self):
        
        url = reverse('cadastro_produto')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ProdutoForm)

    def test_cadastro_produto_post_valido_cria_objeto(self):
        
        url = reverse('cadastro_produto')
        cat = CategoriaProduto.objects.create(nome_da_categoria="Livros")
        
        data = {
            'nome_do_produto': 'Caderno novo',
            'categorias': [cat.id_categoria_produto]
        }
        
        count_antes = Produto.objects.count()
        response = self.client.post(url, data)
        count_depois = Produto.objects.count()
        
        # Verifica criação
        self.assertEqual(count_depois, count_antes + 1)
        # Verifica se redirecionou (status 302) 
        # Nota: Se sua view atual renderiza 200 ao salvar, altere para 200.
        self.assertEqual(response.status_code, 302)

    def test_cadastro_produto_post_invalido_nao_cria(self):
    
        url = reverse('cadastro_produto')
        data = {
            'nome_do_produto': '', # Inválido
            'categorias': []
        }
        count_antes = Produto.objects.count()
        response = self.client.post(url, data)
        count_depois = Produto.objects.count()
        
        self.assertEqual(count_depois, count_antes)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)


    def test_cadastro_categoria_get_renderiza_form(self):
       
        url = reverse('cadastro_categoria')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CategoriaProdutoForm)

    def test_cadastro_categoria_post_valido_cria_objeto(self):
       
        url = reverse('cadastro_categoria')
        data = {
            'nome_da_categoria': 'Informática',
            'descricao_da_categoria': 'Eletrônicos'
        }
        
        count_antes = CategoriaProduto.objects.count()
        response = self.client.post(url, data)
        count_depois = CategoriaProduto.objects.count()
        
        self.assertEqual(count_depois, count_antes + 1)
        self.assertEqual(response.status_code, 302)

    def test_cadastro_categoria_post_invalido_nao_cria(self):
        
        url = reverse('cadastro_categoria')
        data = {
            'nome_da_categoria': '', # Inválido
        }
        count_antes = CategoriaProduto.objects.count()
        response = self.client.post(url, data)
        count_depois = CategoriaProduto.objects.count()
        
        self.assertEqual(count_depois, count_antes)
        self.assertTrue(response.context['form'].errors)


    #Teste 3.4 -

    #Teste 3.5 - Editar_* (categoria, produto, venda) 
class TestEditarViews(TestCase):
    

    def setUp(self):
        self.usuario = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        
        # Criação de dados base
        self.cat = CategoriaProduto.objects.create(nome_da_categoria="Categoria Original")
        self.prod = Produto.objects.create(nome_do_produto="Produto Original")
        self.prod.categorias.add(self.cat)
        self.cliente = CadastroPessoaFisica.objects.create(nome_completo="Cliente", cpf="00000000000")
        
        self.venda = CompraCliente.objects.create(
            cliente_fisico=self.cliente, 
            preco_total=50.00, 
            pagamento_metodo="Dinheiro"
        )
        self.item_venda = CompraClienteHasProduto.objects.create(
            venda=self.venda, 
            produto=self.prod, 
            quantidade_produto=1, 
            preco_unitario=50.00
        )

    
    def test_editar_categoria_get_carrega_dados(self):
       
        url = reverse('editar_categoria', args=[self.cat.id_categoria_produto])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance.nome_da_categoria, "Categoria Original")

    def test_editar_categoria_post_valido_atualiza(self):
       
        url = reverse('editar_categoria', args=[self.cat.id_categoria_produto])
        data = {'nome_da_categoria': 'Categoria Alterada', 'descricao_da_categoria': 'Nova desc'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('lista_produtos'))
        
        self.cat.refresh_from_db()
        self.assertEqual(self.cat.nome_da_categoria, 'Categoria Alterada')

    def test_editar_categoria_post_invalido_nao_atualiza(self):
        
        url = reverse('editar_categoria', args=[self.cat.id_categoria_produto])
        data = {'nome_da_categoria': ''} 
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.cat.refresh_from_db()
        self.assertEqual(self.cat.nome_da_categoria, 'Categoria Original')

    def test_editar_categoria_get_404(self):
        
        url = reverse('editar_categoria', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    
    def test_editar_produto_get_carrega_dados(self):
        
        url = reverse('editar_produto', args=[self.prod.id_produto])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance.nome_do_produto, "Produto Original")

    def test_editar_produto_post_valido_atualiza(self):
        
        url = reverse('editar_produto', args=[self.prod.id_produto])
        data = {'nome_do_produto': 'Produto Alterado', 'categorias': [self.cat.id_categoria_produto]}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.nome_do_produto, 'Produto Alterado')

    def test_editar_produto_post_invalido_nao_atualiza(self):
        
        url = reverse('editar_produto', args=[self.prod.id_produto])
        data = {'nome_do_produto': '', 'categorias': []}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.nome_do_produto, 'Produto Original')

    def test_editar_produto_get_404(self):
        
        url = reverse('editar_produto', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

   
    def test_editar_venda_get_carrega_itens(self):
        
        url = reverse('editar_venda', args=[self.venda.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        itens = response.context.get('itens_venda')
        self.assertIsNotNone(itens)
        self.assertEqual(len(itens), 1)
        self.assertEqual(itens[0]['produto_nome'], 'Produto Original')

    def test_editar_venda_post_nao_altera_itens(self):
        
        # O views.py não salva o formset no POST, então os itens devem permanecer inalterados
        url = reverse('editar_venda', args=[self.venda.id])
        data = {
            'cliente_fisico': self.cliente.id_cliente_pf,
            'pagamento_metodo': 'Cartão',
            'preco_total': 200.00
        }
        
        qtd_item_antes = self.item_venda.quantidade_produto
        
        self.client.post(url, data)
        
        # Recarrega o item do banco para verificar
        item_atualizado = CompraClienteHasProduto.objects.get(id=self.item_venda.id)
        self.assertEqual(item_atualizado.quantidade_produto, qtd_item_antes)
        self.assertEqual(item_atualizado.produto.nome_do_produto, "Produto Original")

    def test_editar_venda_post_valido_atualiza_dados_principais(self):
        
        url = reverse('editar_venda', args=[self.venda.id])
        data = {
            'cliente_fisico': self.cliente.id_cliente_pf,
            'pagamento_metodo': 'Cartão de Crédito',
            'preco_total': 999.00
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        self.venda.refresh_from_db()
        self.assertEqual(self.venda.pagamento_metodo, 'Cartão de Crédito')

    def test_editar_venda_post_invalido_nao_atualiza(self):
        
        url = reverse('editar_venda', args=[self.venda.id])
        data = {
            'cliente_fisico': self.cliente.id_cliente_pf,
            'pagamento_metodo': '',
            'preco_total': ''
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.venda.refresh_from_db()
        self.assertEqual(self.venda.pagamento_metodo, 'Dinheiro')

    def test_editar_venda_get_404(self):
        
        url = reverse('editar_venda', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    #Teste 3.6 - 

class ListaViewsTestCase(TestCase):

    def setUp(self):
       
        # 1. Configuração de Usuário e Login
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')

        # 2. Criar Dados para lista_clientes
        self.pf = CadastroPessoaFisica.objects.create(
            nome_completo="Ana Silva",
            cpf="12345678900",
            email="ana@teste.com",
            telefone="11999999999"
        )
        self.pj = CadastroPessoaJuridica.objects.create(
            razao_social="Papelaria",
            cnpj="12345678000199",
            email="contato@beta.com",
            telefone="11988888888"
        )

        # 3. Criar Dados para lista_produtos
        self.cat = CategoriaProduto.objects.create(
            nome_da_categoria="Cadernos",
            descricao_da_categoria="Seção de cadernos"
        )
        self.produto = Produto.objects.create(
            nome_do_produto="Fichario"
        )
        self.produto.categorias.add(self.cat)

        # 4. Criar Dados para lista_vendas
        self.venda = CompraCliente.objects.create(
            cliente_fisico=self.pf,
            data=timezone.now(),
            preco_total=200.00,
            pagamento_metodo="Cartão"
        )
        # Cria item da venda
        self.item_venda = CompraClienteHasProduto.objects.create(
            compra_cliente=self.venda,
            produto=self.produto,
            quantidade_produto=2,
            preco_unitario=50.00
        )

    def test_status_code(self):
        """
        ( ) GET: Verificar se o status é 200.
        Testa se as 3 listas respondem corretamente (Status 200).
        """
        response_clientes = self.client.get(reverse('lista_clientes'))
        self.assertEqual(response_clientes.status_code, 200)

        response_produtos = self.client.get(reverse('lista_produtos'))
        self.assertEqual(response_produtos.status_code, 200)

        response_vendas = self.client.get(reverse('lista_vendas'))
        self.assertEqual(response_vendas.status_code, 200)

    def test_lista_clientes_unificada_e_ordenada(self):
        """
        ( ) lista_clientes: Verificar se a lista unificada (PF+PJ) está correta e ordenada.
        A view ordena pelo campo 'nome' (que é nome_completo para PF e razao_social para PJ).
        'Ana Silva' deve vir antes de 'Papelaria'.
        """
        response = self.client.get(reverse('lista_clientes'))
        clientes = response.context['clientes']

        # Verifica se trouxe ambos os clientes
        self.assertEqual(len(clientes), 2)

        # Verifica ordenação (Ana antes de Papelaria)
        self.assertEqual(clientes[0]['nome'], 'Ana Silva')
        self.assertEqual(clientes[0]['tipo'], 'PF')
        self.assertEqual(clientes[0]['documento'], 'CPF: 12345678900')

        self.assertEqual(clientes[1]['nome'], 'Papelaria')
        self.assertEqual(clientes[1]['tipo'], 'PJ')

    def test_lista_produtos_contexto(self):
        """
        ( ) lista_produtos: Verificar se as categorias e produtos são passados para o template.
        """
        response = self.client.get(reverse('lista_produtos'))
        
        # Verifica se as chaves existem no contexto
        self.assertIn('categorias', response.context)
        self.assertIn('produtos', response.context)

        # Verifica os dados
        categorias = response.context['categorias']
        produtos = response.context['produtos']

        self.assertEqual(categorias.count(), 1)
        self.assertEqual(produtos.count(), 1)
        self.assertEqual(produtos[0].nome_do_produto, 'Fichario')

    def test_lista_vendas_calculos(self):
        """
        ( ) lista_vendas: Verificar se os dados da venda (cliente, total) e os itens com 
        subtotais são calculados corretamente no contexto.
        """
        response = self.client.get(reverse('lista_vendas'))
        vendas = response.context['vendas']

        # Deve ter 1 venda
        self.assertEqual(len(vendas), 1)

        venda_no_contexto = vendas[0]

        # Verifica dados básicos da venda
        self.assertEqual(venda_no_contexto['cliente_nome'], 'Ana Silva')
        self.assertEqual(venda_no_contexto['preco_total'], 200.00)

        # Verifica os itens e o cálculo do subtotal feito na view
        itens = venda_no_contexto['itens']
        self.assertEqual(len(itens), 1)

        # A view faz: quantidade * preco_unitario (2 * 50 = 100)
        self.assertEqual(itens[0]['subtotal'], 100.00)
        self.assertEqual(itens[0]['produto_nome'], 'Fichario')


# 3.7. Gráficos
class GraficosViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='123')
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse('graficos')
        self.hoje = date.today()
        self.mes_atual = self.hoje.month
        self.ano_atual = self.hoje.year
        
        self.pf_mes_atual = CadastroPessoaFisica.objects.create(
            nome_completo="Carlos Aniversariante",
            cpf='11122233344',
            data_de_nascimento=date(self.ano_atual - 25, self.mes_atual, 15), # 15 do mês atual
            email='carlos@teste.com'
        )
     
        self.pf_outro_mes = CadastroPessoaFisica.objects.create(
            nome_completo="Maria Outubro",
            cpf='44455566677',
            data_de_nascimento=date(self.ano_atual - 30, 10, 10), # 10 de Outubro (ou qualquer mês != hoje)
            email='maria@teste.com'
        )

        self.dados_pizza = {
            'labels': ['Eletrônicos', 'Roupas'],
            'data': [30, 70]
        }
        DadosGraficos.objects.create(
            nome_grafico='pizza_categorias',
            dados_json=self.dados_pizza
        )

        self.dados_freq = {
            'top_clientes': ['João', 'Maria']
        }
        DadosGraficos.objects.create(
            nome_grafico='frequencia_cliente',
            dados_json=self.dados_freq
        )

        self.dados_gastos = {
            'total_gasto': 15000.50
        }
        DadosGraficos.objects.create(
            nome_grafico='gastos_cliente',
            dados_json=self.dados_gastos
        )

        self.dados_tendencia = {
            'meses': ['Jan', 'Fev'], 'vendas': [100, 200]
        }
        DadosGraficos.objects.create(
            nome_grafico='tendencia',
            dados_json=self.dados_tendencia
        )

    def test_graficos_get_e_contexto_completo(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, "A página deve carregar com sucesso")

        dados_aniversarios = response.context['chart_aniversarios']
        
        self.assertEqual(dados_aniversarios['total_mes'], 1, "Deve contar apenas 1 aniversariante no mês atual")
        
        lista_combinada = dados_aniversarios['lista_combinada'] # Formato: [(dia, nome), ...]
        nomes_na_lista = [nome for dia, nome in lista_combinada]
        
        self.assertIn("Carlos Aniversariante", nomes_na_lista, "Carlos (mes atual) deve estar na lista")
        self.assertNotIn("Maria Outubro", nomes_na_lista, "Maria (mes diferente) não deve estar na lista")
        
        contexto_json_str = response.context['context_json']
        dados_completos = json.loads(contexto_json_str)

        pizza_data = dados_completos.get('chart_pizza_categorias')
        self.assertIsNotNone(pizza_data, "O gráfico pizza deve ter dados")
        self.assertEqual(pizza_data, self.dados_pizza, "Os dados do pizza devem corresponder ao DB")

        freq_data = dados_completos.get('chart_frequencia_cliente')
        self.assertIsNotNone(freq_data, "O gráfico de frequência deve ter dados")
        self.assertEqual(freq_data, self.dados_freq)

        gastos_data = dados_completos.get('chart_gastos_cliente')
        self.assertIsNotNone(gastos_data, "O gráfico de gastos deve ter dados")
        self.assertEqual(gastos_data, self.dados_gastos)

        tendencia_data = dados_completos.get('chart_tendencia')
        self.assertIsNotNone(tendencia_data, "O gráfico de tendência deve ter dados")
        self.assertEqual(tendencia_data, self.dados_tendencia)

# 3.8. dashboard e index

class CadastroClienteViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='123')
        self.client = Client()
        self.client.force_login(self.user)

        self.url_fisica = reverse('cadastro_cliente_pf')
        self.url_juridica = reverse('cadastro_cliente_pj')

    def test_get_renderiza_form_pf(self):
        response = self.client.get(self.url_fisica)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CadastroPessoaFisicaForm)

        self.assertEqual(response.context['tipo'], 'fisica')
        self.assertIn('Pessoa Física', response.context['titulo'])

    def test_get_renderiza_form_pj(self):

# 4. Testes no urls.py

class CadastroUrlsTest(TestCase):
    
    def test_root_url_resolves_to_index_view(self):
        url = reverse('index')
        self.assertEqual(resolve(url).func, views.index)

    def test_dashboard_url_resolves_to_dashboard_view(self):
        url = reverse('dashboard')
        self.assertEqual(resolve(url).func, views.dashboard)

    def test_cadastro_produto_url_resolves(self):
        url = reverse('cadastro_produto')
        self.assertEqual(resolve(url).func, views.cadastro_produto)

    def test_cadastro_categoria_url_resolves(self):
        url = reverse('cadastro_categoria')
        self.assertEqual(resolve(url).func, views.cadastro_categoria)

    def test_lista_clientes_url_resolves(self):
        url = reverse('lista_clientes')
        self.assertEqual(resolve(url).func, views.lista_clientes)
        
    def test_lista_produtos_url_resolves(self):
        url = reverse('lista_produtos')
        self.assertEqual(resolve(url).func, views.lista_produtos)

    def test_lista_vendas_url_resolves(self):
        url = reverse('lista_vendas')
        self.assertEqual(resolve(url).func, views.lista_vendas)

    def test_graficos_url_resolves(self):
        url = reverse('graficos')
        self.assertEqual(resolve(url).func, views.graficos)

    def test_atualizar_graficos_url_resolves(self):
        url = reverse('atualizar_graficos')
        self.assertEqual(resolve(url).func, views.atualizar_graficos_view)
    
    def test_cadastro_cliente_pf_resolves_with_correct_kwargs(self):
        url = reverse('cadastro_cliente_pf')
        match = resolve(url)
        self.assertEqual(match.func, views.cadastro_cliente)
        self.assertEqual(match.kwargs, {'tipo': 'fisica'})

    def test_cadastro_cliente_pj_resolves_with_correct_kwargs(self):
        url = reverse('cadastro_cliente_pj')
        match = resolve(url)
        self.assertEqual(match.func, views.cadastro_cliente)
        self.assertEqual(match.kwargs, {'tipo': 'juridica'})

    def test_editar_categoria_url_resolves_with_pk(self):
        url = reverse('editar_categoria', kwargs={'pk': 1})
        match = resolve(url)
        self.assertEqual(match.func, views.editar_categoria)
        self.assertEqual(match.kwargs, {'pk': 1})

    def test_editar_produto_url_resolves_with_pk(self):
        url = reverse('editar_produto', kwargs={'pk': 1})
        match = resolve(url)
        self.assertEqual(match.func, views.editar_produto)
        self.assertEqual(match.kwargs, {'pk': 1})

    def test_editar_venda_url_resolves_with_pk(self):
        url = reverse('editar_venda', kwargs={'pk': 1})
        match = resolve(url)
        self.assertEqual(match.func, views.editar_venda)
        self.assertEqual(match.kwargs, {'pk': 1})

    def test_editar_cliente_pf_url_resolves(self):
        url = reverse('editar_cliente_pf', kwargs={'pk': 1})
        match = resolve(url)
        self.assertEqual(match.func, views.editar_cliente)

        expected = {'tipo': 'fisica', 'pk': 1}
        self.assertEqual(match.kwargs, expected)

    def test_editar_cliente_pj_url_resolves(self):
        url = reverse('editar_cliente_pj', kwargs={'pk': 1})
        match = resolve(url)
        self.assertEqual(match.func, views.editar_cliente)
        expected = {'tipo': 'juridica', 'pk': 1}
        self.assertEqual(match.kwargs, expected)
    
    def test_url_inexistente_retorna_404(self):
        with self.assertRaises(Resolver404):
            resolve('/rota-que-nao-existe-na-app/')        
    