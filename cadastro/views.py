from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms.produtos import ProdutoForm, CategoriaProdutoForm
from .forms.clientes import CadastroPessoaFisicaForm, CadastroPessoaJuridicaForm
from .forms.vendas import CompraClienteForm, CompraClienteHasProdutoForm
from .models import CategoriaProduto, CadastroPessoaFisica, CompraCliente, CompraClienteHasProduto, CadastroPessoaJuridica, Produto, DadosGraficos
from django.db.models import Sum, Count
from django.utils import timezone
from django.forms.formsets import formset_factory
from django.forms import inlineformset_factory
from django.contrib import messages
from django.core.management import call_command
import pandas as pd
from django.db import transaction
from .forms.importacao import UploadFileForm
from datetime import date
import json
from io import BytesIO

# View da página inicial.
def index(request):
    return render(request, 'cadastro/index.html') 

# View da página de criação de cadastros de cliente, produto, categoria e venda.
@login_required
def cadastro_cliente(request, tipo):
    # Inicializa a variável com uma string vazia no início
    mensagem_sucesso = '' 
    
    if tipo == 'juridica':
        form_class = CadastroPessoaJuridicaForm
        titulo = 'Novo Cliente (Pessoa Juridica)'
    else: 
        form_class = CadastroPessoaFisicaForm
        titulo = 'Novo Cliente (Pessoa Física)'
    
    mensagem_sucesso = None

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            if tipo == 'juridica':
                mensagem_sucesso = "Cliente Pessoa Juridica cadastrado com sucesso"
            else:
                mensagem_sucesso = 'Cliente cadastrado com sucesso!'
            form = form_class()
    
    else:
        form = form_class()

    context = {
        'form': form,
        'titulo': titulo,
        'mensagem_sucesso': mensagem_sucesso,
        'tipo' : tipo
    }

    return render(request, "cadastro/form.html", context)


@login_required    
def cadastro_produto(request):
    # Verifica se existe pelo menos uma categoria no banco de dados
    existe_categoria = CategoriaProduto.objects.exists()

    mensagem_sucesso = None

    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto_cadastrado = form.save()
            mensagem_sucesso = f'Produto {produto_cadastrado.nome_do_produto} cadastrado com sucesso!'
            form = ProdutoForm()
    else:
        form = ProdutoForm()

    context = { 
        'form': form,
        'mensagem_sucesso': mensagem_sucesso,
        'existe_categoria': existe_categoria,
        'titulo': 'Novo Produto'
    }

    return render(request, "cadastro/form.html", context)

@login_required    
def cadastro_categoria(request):

    mensagem_sucesso = None

    if request.method == 'POST':
        form = CategoriaProdutoForm(request.POST)
        if form.is_valid():
            categoria_cadastrada = form.save()
            mensagem_sucesso = f'Categoria {categoria_cadastrada.nome_da_categoria} cadastrada com sucesso!'
            form = CategoriaProdutoForm()
    else:
        form = CategoriaProdutoForm()

    context = {
        'form': form,
        'mensagem_sucesso' : mensagem_sucesso,
        'titulo': 'Nova Categoria'
    }

    return render(request, "cadastro/form.html", context)

@login_required    
def cadastro_venda(request):
    # Cria um FormSet "inline" para os itens da venda
    ItemVendaFormSet = inlineformset_factory(
        CompraCliente, 
        CompraClienteHasProduto, 
        form=CompraClienteHasProdutoForm, 
        extra=1,  # Número de formulários de item em branco para começar
        can_delete=True # Permite deletar itens
    )

    if request.method == 'POST':
        # Pega os dados do POST para ambos os formulários
        form = CompraClienteForm(request.POST)
        formset = ItemVendaFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # 1. Salva o formulário principal da venda, mas ainda não commita no banco
            venda = form.save(commit=False)
            
            # 2. Calcula o total dos itens
            total_itens = 0
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE'):
                    total_itens += item_form.cleaned_data['quantidade_produto'] * item_form.cleaned_data['preco_unitario']
            
            # 3. Adiciona o frete (se houver) e salva o total na venda
            venda.preco_total = total_itens + (venda.frete or 0)
            venda.save() # Agora sim, commita no banco
            
            # 4. Salva o formset, associando os itens à venda que acabou de ser salva
            formset.instance = venda
            formset.save()
            
            # Redireciona para a página de lista de vendas após o sucesso
            return redirect('lista_vendas')
    else:
        # Se for GET, cria formulários em branco
        form = CompraClienteForm()
        formset = ItemVendaFormSet()

    context = {
        'form': form,
        'formset': formset,
        'titulo': 'Registrar Nova Venda'
    }


    return render(request, 'cadastro/vendas/form.html', context)

# View da página de gráficos.
# Em cadastro/views.py

import json  # <--- 1. Adicione esta importação no topo do arquivo

# ... outras importações

@login_required
def graficos(request):
    #Lógica para gráfico de aniversariantes.
    hoje = date.today()
    mes_atual = hoje.month

    # Filtra os aniversariantes do mês atual (Pessoa Física).
    aniversariantes_pf = CadastroPessoaFisica.objects.filter(
        data_de_nascimento__month=mes_atual
    ).order_by('data_de_nascimento__day')

    # Combinar e ordenar a lista de aniversariantes.
    lista_aniversariantes = []
    for pf in aniversariantes_pf:
        lista_aniversariantes.append({
            'dia': pf.data_de_nascimento.day,
            'nome': pf.nome_completo
        })

    # Ordena a lista final pelo dia do mês.
    lista_aniversariantes.sort(key=lambda x: x['dia'])

    # Prepara o dicionário de dados do gráfico de aniversariantes.
    dados_aniversarios = {
        'total_mes': len(lista_aniversariantes),
        'lista_combinada': [(item['dia'], item['nome']) for item in lista_aniversariantes]
    }


    dados_brutos = {dado.nome_grafico: dado.dados_json for dado in DadosGraficos.objects.all()}

    context_dict = {
        'chart_aniversarios': dados_aniversarios,
        'chart_pizza_categorias': dados_brutos.get('pizza_categorias', {}),
        'chart_frequencia_cliente': dados_brutos.get('frequencia_cliente', {}),
        'chart_gastos_cliente': dados_brutos.get('gastos_cliente', {}),
        'chart_produtos_mais_vendidos': dados_brutos.get('produtos_mais_vendidos', {}),
        'chart_tendencia': dados_brutos.get('tendencia', {}),
    }

    # Converte o dicionário inteiro para uma string JSON
    context_json = json.dumps(context_dict)

    # Passa tanto o JSON para os gráficos JS quanto o dicionário de aniversariantes para o template
    return render(request, 'cadastro/graficos.html', {
        'context_json': context_json,
        'chart_aniversarios': dados_aniversarios # Passa separado para o template
        })



@login_required
def dashboard(request):
    return render(request, 'cadastro/dashboard.html')

@login_required
def lista_clientes(request):
    """
    Busca e une a lista de clientes PF e PJ para exibir em uma única tabela.
    """
    # Busca todos os clientes PF e PJ no banco de dados
    clientes_pf = CadastroPessoaFisica.objects.all().order_by('nome_completo')
    clientes_pj = CadastroPessoaJuridica.objects.all().order_by('razao_social')


    lista_unificada = []

    for cliente in clientes_pf:
        lista_unificada.append({
            'nome': cliente.nome_completo,
            'documento': f"CPF: {cliente.cpf}",
            'email': cliente.email,
            'telefone': cliente.telefone,
            'tipo': 'PF',
            'id': cliente.id_cliente_pf,
        })

    for cliente in clientes_pj:
        lista_unificada.append({
            'nome': cliente.razao_social,
            'documento': f"CNPJ: {cliente.cnpj}",
            'email': cliente.email,
            'telefone': cliente.telefone,
            'tipo': 'PJ',
            'id': cliente.id_cliente_pj,
        })
    
    # Ordena a lista unificada pelo nome da empresa/razão social
    lista_unificada.sort(key=lambda x: x['nome'])

    context = {
        'clientes': lista_unificada
    }
    return render(request, 'cadastro/listas/lista_clientes.html', context)

@login_required
def lista_produtos(request):
    """
    Exibe a lista de categorias e produtos para gerenciamento unificado.
    """
    # Busca todas as categorias
    categorias = CategoriaProduto.objects.all().order_by('nome_da_categoria')
    
    produtos = Produto.objects.prefetch_related('categorias').order_by('nome_do_produto')

    context = {
        'categorias': categorias,
        'produtos': produtos
    }
    return render(request, 'cadastro/listas/lista_produtos.html', context)

@login_required
def lista_vendas(request):
    """
    Busca e exibe a lista de todas as vendas, com a opção de expandir para ver os itens.
    """
    # Otimiza a consulta para evitar muitos acessos ao banco
    vendas_queryset = CompraCliente.objects.prefetch_related('compraclientehasproduto_set__produto').order_by('-data')

    vendas_list = []
    for venda in vendas_queryset:
        # Determina o nome e o tipo do cliente (PF ou PJ)
        cliente_nome = "Cliente não identificado"
        cliente_tipo = "N/A"
        if venda.cliente_fisico:
            cliente_nome = venda.cliente_fisico.nome_completo
            cliente_tipo = "PF"
        elif venda.cliente_juridico:
            cliente_nome = venda.cliente_juridico.razao_social
            cliente_tipo = "PJ"
        
        # Monta a lista de itens para cada venda
        itens_venda = []
        for item in venda.compraclientehasproduto_set.all():
            subtotal = item.quantidade_produto * item.preco_unitario
            itens_venda.append({
                'produto_nome': item.produto.nome_do_produto,
                'quantidade': item.quantidade_produto,
                'subtotal': subtotal
            })
        subtotal_itens = venda.preco_total - (venda.frete or 0)

        vendas_list.append({
            'id': venda.id,
            'data': venda.data,
            'cliente_nome': cliente_nome,
            'cliente_tipo': cliente_tipo,
            'preco_total': venda.preco_total,
            'frete': venda.frete,
            'subtotal_itens': subtotal_itens,
            'itens': itens_venda,
            'pagamento_metodo': venda.pagamento_metodo,
        })

    context = {
        'vendas': vendas_list
    }
    return render(request, 'cadastro/listas/lista_vendas.html', context)

@login_required
def editar_categoria(request, pk):
    """
    Edita uma categoria existente.
    """
    # Busca a categoria no banco ou retorna um erro 404 se não encontrar
    categoria = get_object_or_404(CategoriaProduto, pk=pk)

    if request.method == 'POST':
        # Se o formulário for enviado, atualiza os dados
        form = CategoriaProdutoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            # Redireciona de volta para a página de produtos após salvar
            return redirect('lista_produtos')
    else:
        # Se for um GET, mostra o formulário com os dados atuais da categoria
        form = CategoriaProdutoForm(instance=categoria)

    context = {
        'form': form,
        'titulo': 'Editar Categoria'
    }
    return render(request, 'cadastro/form.html', context)

@login_required
def editar_produto(request, pk):
    """
    Edita um produto existente.
    """
    produto = get_object_or_404(Produto, pk=pk)

    if request.method == 'POST':
        # Se o formulário for enviado, atualiza os dados
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            # Redireciona de volta para a página de produtos após salvar
            return redirect('lista_produtos')
    else:
        # Se for um GET, mostra o formulário com os dados atuais do produto
        form = ProdutoForm(instance=produto)

    context = {
        'form': form,
        'titulo': 'Editar Produto'
    }
    return render(request, 'cadastro/form.html', context)

@login_required
def editar_venda(request, pk):
    venda = get_object_or_404(CompraCliente, pk=pk)

    if request.method == 'POST':
        form = CompraClienteForm(request.POST, instance=venda)
        if form.is_valid():
            form.save()
            return redirect('lista_vendas')
    else:
        form = CompraClienteForm(instance=venda)

    # Prepara o FormSet, mas vamos criar uma lista de itens para o template
    ItemVendaFormSet = inlineformset_factory(
        CompraCliente, CompraClienteHasProduto,
        form=CompraClienteHasProdutoForm, extra=0, can_delete=False
    )
    formset = ItemVendaFormSet(instance=venda)

    # Cria uma lista com os itens e seus subtotais já calculados
    itens_venda_com_subtotal = []
    for item in formset:
        subtotal = item.instance.quantidade_produto * item.instance.preco_unitario
        itens_venda_com_subtotal.append({
            'produto_nome': item.instance.produto.nome_do_produto,
            'quantidade': item.instance.quantidade_produto,
            'preco_unitario': item.instance.preco_unitario,
            'subtotal': subtotal
        })

    context = {
        'form': form,
        'itens_venda': itens_venda_com_subtotal, # Passa a nova lista para o template
        'titulo': 'Editar Venda',
        'venda_id': venda.id
    }
    return render(request, 'cadastro/vendas/editar_form.html', context)

@login_required
def atualizar_graficos_view(request):
    """View para ser chamada por um botão, atualizando os dados dos gráficos."""
    try:
        call_command('atualiza_graficos')
        
        messages.success(request, "Gráficos atualizados com sucesso!")
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao atualizar os gráficos: {e}")

    return redirect('graficos')

@login_required
def editar_cliente(request, tipo, pk):
    """
    Edita um cliente existente (Pessoa Física ou Jurídica).
    """
    # 1. Define o modelo e o formulário com base no tipo
    if tipo == 'juridica':
        model_class = CadastroPessoaJuridica
        form_class = CadastroPessoaJuridicaForm
        titulo = 'Editar Cliente (Pessoa Jurídica)'
        url_redirect = 'lista_clientes'
    else: # 'fisica'
        model_class = CadastroPessoaFisica
        form_class = CadastroPessoaFisicaForm
        titulo = 'Editar Cliente (Pessoa Física)'
        url_redirect = 'lista_clientes'

    # 2. Busca o cliente no banco de dados pelo ID (pk)
    cliente = get_object_or_404(model_class, pk=pk)

    if request.method == 'POST':
        # Se o formulário foi enviado, atualiza os dados
        form = form_class(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            # Redireciona para a lista de clientes após salvar
            return redirect(url_redirect)
    else:
        # Se for um GET, mostra o formulário preenchido com os dados atuais
        form = form_class(instance=cliente)

    context = {
        'form': form,
        'titulo': titulo
    }
    # Reaproveitamos o mesmo template de formulário!
    return render(request, "cadastro/form.html", context)


def mapear_colunas(colunas):
    """Mapeia cabeçalhos comuns para os nomes internos: nome, preco, quantidade, categorias."""
    mapeamento = {}
    # Guarda possíveis colunas de preço para decidir depois
    precos_candidatos = []
    
    for col in colunas:
        col_lower = col.lower().strip()
        if any(p in col_lower for p in ['nome', 'produto', 'descricao', 'item', 'nome da']):
            mapeamento['nome'] = col
        elif 'preco' in col_lower or 'preço' in col_lower or 'price' in col_lower:
            precos_candidatos.append(col)
        elif any(p in col_lower for p in ['estoque', 'quantidade', 'qtd', 'stock', 'em estoque']):
            mapeamento['quantidade'] = col
        elif any(p in col_lower for p in ['categoria', 'categ', 'grupo', 'tipo']):
            mapeamento['categorias'] = col
    
    # Decidir coluna de preço: prefere a que NÃO tenha 'promocional' ou 'comparativo'
    for col in precos_candidatos:
        col_lower = col.lower()
        if 'promocional' not in col_lower and 'comparativo' not in col_lower:
            mapeamento['preco'] = col
            break
    # Se não encontrou uma sem promoção, usa a primeira disponível
    if 'preco' not in mapeamento and precos_candidatos:
        mapeamento['preco'] = precos_candidatos[0]
        
    return mapeamento
@login_required
def importar_produtos(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = request.FILES['arquivo']
            try:
                # Leitura robusta do arquivo
                if arquivo.name.endswith('.csv'):
                    conteudo = arquivo.read()
                    try:
                        df = pd.read_csv(BytesIO(conteudo), encoding='utf-8', engine='python', sep=None, on_bad_lines='skip')
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        try:
                            df = pd.read_csv(BytesIO(conteudo), encoding='latin-1', engine='python', sep=None, on_bad_lines='skip')
                        except Exception as e:
                            messages.error(request, f"Erro ao ler o CSV. Detalhes: {e}")
                            return redirect('importar_produtos')
                elif arquivo.name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(arquivo)
                else:
                    messages.error(request, "Formato de arquivo não suportado.")
                    return redirect('importar_produtos')

                # Mapeamento de colunas
                colunas_obrigatorias = {'nome', 'preco', 'quantidade'}
                mapeamento = mapear_colunas(df.columns)
                if not colunas_obrigatorias.issubset(mapeamento.keys()):
                    messages.error(request, f"Colunas obrigatórias não encontradas. Mapeadas: {list(mapeamento.keys())}")
                    return redirect('importar_produtos')

                df.rename(columns={v: k for k, v in mapeamento.items()}, inplace=True)
                df = df[list(mapeamento.keys())]

                produtos_criados = 0
                produtos_atualizados = 0
                linhas_ignoradas = 0

                # Processamento linha a linha (sem transação atômica, para que erros em uma linha não impeçam as outras)
                for index, row in df.iterrows():
                    nome = str(row['nome']).strip() if pd.notna(row['nome']) else ''
                    preco = row['preco']
                    quantidade = row['quantidade']

                    # Validações mínimas
                    if not nome:
                        linhas_ignoradas += 1
                        continue

                    if pd.isna(preco):
                        linhas_ignoradas += 1
                        continue
                    try:
                        preco = float(str(preco).replace(',', '.'))
                        if preco < 0:
                            raise ValueError
                    except (ValueError, TypeError):
                        linhas_ignoradas += 1
                        continue

                    if pd.isna(quantidade):
                        linhas_ignoradas += 1
                        continue
                    try:
                        quantidade = int(float(str(quantidade).replace(',', '.')))
                        if quantidade < 0:
                            raise ValueError
                    except (ValueError, TypeError):
                        linhas_ignoradas += 1
                        continue

                    # Categorias (opcional)
                    categorias_nomes = []
                    if 'categorias' in df.columns:
                        categorias_str = str(row['categorias']) if pd.notna(row['categorias']) else ''
                        categorias_nomes = [c.strip() for c in categorias_str.split(',') if c.strip()]

                    # Cria/atualiza produto
                    produto, created = Produto.objects.update_or_create(
                        nome_do_produto=nome.upper(),
                        defaults={
                            'preco': preco,
                            'quantidade_estoque': quantidade
                        }
                    )
                    if created:
                        produtos_criados += 1
                    else:
                        produtos_atualizados += 1

                    for cat_nome in categorias_nomes:
                        categoria, _ = CategoriaProduto.objects.get_or_create(nome_da_categoria=cat_nome.title())
                        produto.categorias.add(categoria)

                # Feedback final
                msg = f"Importação concluída! {produtos_criados} criados, {produtos_atualizados} atualizados."
                if linhas_ignoradas > 0:
                    msg += f" {linhas_ignoradas} linha(s) ignorada(s) por dados inválidos."
                messages.success(request, msg)
                return redirect('lista_produtos')

            except Exception as e:
                messages.error(request, f"Erro ao processar arquivo: {e}")
                return redirect('importar_produtos')
    else:
        form = UploadFileForm()

    return render(request, 'cadastro/importar_produtos.html', {'form': form})