from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, Q, F, Case, When, Value, CharField
from django.utils import timezone
import json

# Importe seus modelos
from cadastro.models.clientes import CadastroPessoaFisica
from cadastro.models.vendas import CompraCliente, CompraClienteHasProduto, DadosGraficos

class Command(BaseCommand):
    help = 'Atualiza os dados dos gráficos para o dashboard, salvando-os no banco de dados.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando a atualização dos dados dos gráficos...")

        # --- 1. APROXIMAÇÃO DE ANIVERSÁRIOS (Clientes PF no mês atual) ---
        mes_atual = timezone.now().month
        aniversariantes_qs = CadastroPessoaFisica.objects.filter(
            data_de_nascimento__month=mes_atual
        ).order_by('data_de_nascimento__day')

        lista_aniversarios_combinada = list(zip(
            [a.data_de_nascimento.strftime("%d/%m") for a in aniversariantes_qs],
            [a.nome_completo for a in aniversariantes_qs]
        ))

        chart_aniversarios = {
            'total_mes': aniversariantes_qs.count(),
            'lista_combinada': lista_aniversarios_combinada,
        }
        DadosGraficos.objects.update_or_create(
            nome_grafico='aniversarios',
            defaults={'dados_json': chart_aniversarios}
        )
        self.stdout.write(self.style.SUCCESS('✓ Gráfico de Aniversários atualizado.'))

        # --- 2. TENDÊNCIA DE COMPRAS POR CATEGORIAS (Linha/Evolução)

        # 1. Busca todos os itens de venda com data e categoria (CORRIGIDO)
        itens_venda = CompraClienteHasProduto.objects.select_related('compra_cliente', 'produto').prefetch_related('produto__categorias').all()

        # 2. Prepara as estruturas de dados
        vendas_por_data_e_categoria = {}
        datas_unicas = set()
        categorias_unicas = set()

        # 3. Organiza os dados em um dicionário aninhado
        for item in itens_venda:
            data_str = item.compra_cliente.data.strftime('%Y-%m-%d')
            categoria = item.produto.categorias.first() # Pega a primeira categoria do produto
            
            if not categoria:
                continue # Ignora produtos sem categoria

            datas_unicas.add(data_str)
            categorias_unicas.add(categoria.nome_da_categoria)
            
            if data_str not in vendas_por_data_e_categoria:
                vendas_por_data_e_categoria[data_str] = {}
            
            if categoria.nome_da_categoria not in vendas_por_data_e_categoria[data_str]:
                vendas_por_data_e_categoria[data_str][categoria.nome_da_categoria] = 0
            
            vendas_por_data_e_categoria[data_str][categoria.nome_da_categoria] += 1

        # 4. Ordena as datas para o gráfico
        labels = sorted(list(datas_unicas))

        # 5. Monta a estrutura de 'datasets' para o Chart.js
        cores = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        datasets = []
        for i, categoria_nome in enumerate(sorted(list(categorias_unicas))):
            dados_categoria = []
            for data in labels:
                dados_categoria.append(vendas_por_data_e_categoria.get(data, {}).get(categoria_nome, 0))
            
            datasets.append({
                'label': categoria_nome,
                'data': dados_categoria,
                'borderColor': cores[i % len(cores)],
                'fill': False,
                'tension': 0.1
            })

        chart_tendencia = {
            'labels': labels,
            'datasets': datasets
        }

        DadosGraficos.objects.update_or_create(
            nome_grafico='tendencia',
            defaults={'dados_json': chart_tendencia}
        )
        self.stdout.write(self.style.SUCCESS('✓ Gráfico de Tendência (corrigido) atualizado.'))

        # --- 3. SEPARAÇÃO DAS COMPRAS POR CATEGORIAS (Pizza/Share) ---
        compras_por_cat = CompraClienteHasProduto.objects.values(
            'produto__categorias__nome_da_categoria'
        ).annotate(qtd=Count('id')).order_by('-qtd')

        chart_pizza_categorias = {
            'labels': [c['produto__categorias__nome_da_categoria'] for c in compras_por_cat],
            'valores': [c['qtd'] for c in compras_por_cat]
        }
        DadosGraficos.objects.update_or_create(
            nome_grafico='pizza_categorias',
            defaults={'dados_json': chart_pizza_categorias}
        )
        self.stdout.write(self.style.SUCCESS('✓ Gráfico de Pizza (Categorias) atualizado.'))

        # --- 4. FREQUÊNCIA DE COMPRAS POR CLIENTE (Qtd de vezes que comprou) ---
        # Usando Case/When para unificar PF e PJ
        freq_clientes = CompraCliente.objects.annotate(
            nome_cliente=Case(
                When(cliente_fisico__isnull=False, then=F('cliente_fisico__nome_completo')),
                When(cliente_juridico__isnull=False, then=F('cliente_juridico__razao_social')),
                default=Value('Cliente não identificado'),
                output_field=CharField(),
            )
        ).values('nome_cliente').annotate(freq=Count('id')).order_by('-freq')

        chart_frequencia_cliente = {
            'labels': [f['nome_cliente'] for f in freq_clientes],
            'valores': [f['freq'] for f in freq_clientes]
        }
        DadosGraficos.objects.update_or_create(
            nome_grafico='frequencia_cliente',
            defaults={'dados_json': chart_frequencia_cliente}
        )
        self.stdout.write(self.style.SUCCESS('✓ Gráfico de Frequência de Clientes atualizado.'))

        # --- 5. VOLUME DE GASTOS POR CLIENTE (Total em R$) ---
        # Usando Case/When para unificar PF e PJ
        gastos_clientes = CompraCliente.objects.annotate(
            nome_cliente=Case(
                When(cliente_fisico__isnull=False, then=F('cliente_fisico__nome_completo')),
                When(cliente_juridico__isnull=False, then=F('cliente_juridico__razao_social')),
                default=Value('Cliente não identificado'),
                output_field=CharField(),
            )
        ).values('nome_cliente').annotate(total=Sum('preco_total')).order_by('-total')

        chart_gastos_cliente = {
            'labels': [g['nome_cliente'] for g in gastos_clientes],
            'valores': [float(g['total']) for g in gastos_clientes]
        }
        DadosGraficos.objects.update_or_create(
            nome_grafico='gastos_cliente',
            defaults={'dados_json': chart_gastos_cliente}
        )
        self.stdout.write(self.style.SUCCESS('✓ Gráfico de Gastos por Cliente atualizado.'))

        # --- 6. PRODUTOS QUE MAIS VENDEM (Barras) - COM TRATAMENTO DE OUTLIERS ---

        # 1. Pega todos os produtos com suas quantidades vendidas
        ranking_todos_produtos = CompraClienteHasProduto.objects.values(
            'produto__nome_do_produto'
        ).annotate(total_qtd=Sum('quantidade_produto')).order_by('-total_qtd')

        # 2. Separa os 10 primeiros e o resto
        top_10_produtos = list(ranking_todos_produtos[:10])
        outros_produtos = list(ranking_todos_produtos[10:])

        # 3. Calcula o total da categoria "Outros"
        total_outros = sum(p['total_qtd'] for p in outros_produtos)

        # 4. Monta os dados finais para o gráfico
        labels = [p['produto__nome_do_produto'] for p in top_10_produtos]
        valores = [p['total_qtd'] for p in top_10_produtos]

        # 5. Adiciona a categoria "Outros" se ela tiver algum valor
        if total_outros > 0:
            labels.append('Outros')
            valores.append(total_outros)

        chart_produtos_mais_vendidos = {
            'labels': labels,
            'valores': valores
        }

        DadosGraficos.objects.update_or_create(
            nome_grafico='produtos_mais_vendidos',
            defaults={'dados_json': chart_produtos_mais_vendidos}
        )
        self.stdout.write(self.style.SUCCESS('✓ Gráfico de Produtos Mais Vendidos (com tratamento de outliers) atualizado.'))
