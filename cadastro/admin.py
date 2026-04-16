from django.contrib import admin
from .models import (CadastroPessoaFisica, CadastroPessoaJuridica, CategoriaProduto, Produto, CompraCliente, CompraClienteHasProduto)

# --- Clientes ---
@admin.register(CadastroPessoaFisica)
class CadastroPessoaFisicaAdmin(admin.ModelAdmin):
    list_display = ('id_cliente_pf', 'nome_completo', 'cpf', 'email', 'telefone')
    search_fields = ('nome_completo', 'cpf', 'email', 'telefone')
    list_filter = ('cidade', 'estado',)

@admin.register(CadastroPessoaJuridica)
class CadastroPessoaJuridicaAdmin(admin.ModelAdmin):
    list_display = ('id_cliente_pj', 'razao_social', 'cnpj', 'nome_fantasia', 'email', 'telefone')
    search_fields = ('razao_social', 'cnpj', 'nome_fantasia', 'telefone')
    list_filter = ('cidade', 'estado', 'porte_empresa',)

# --- Produtos ---
@admin.register(CategoriaProduto)
class CategoriaProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome_da_categoria', 'descricao_da_categoria')
    search_fields = ('nome_da_categoria','descricao_da_categoria')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome_do_produto', 'listar_categorias') 
    search_fields = ('nome_do_produto',)
    list_filter = ('categorias',) 

    def listar_categorias(self, obj):
        """Exibe uma lista com os nomes das categorias de um produto."""
        return ", ".join([c.nome_da_categoria for c in obj.categorias.all()])
    
    listar_categorias.short_description = 'Categorias'

# --- Vendas ---

# Inline: mostra os produtos dentro do admin de CompraCliente
class CompraClienteHasProdutoInline(admin.TabularInline):
    model = CompraClienteHasProduto
    extra = 1 # Quantidade de linhas extras para adicionar novos itens

@admin.register(CompraCliente)
class CompraClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'preco_total', 'pagamento_metodo', 'get_cliente_display')
    list_filter = ('data', 'pagamento_metodo')
    inlines = [CompraClienteHasProdutoInline] # Adiciona a tabela inline aqui

    def get_cliente_display(self, obj):
        # Método auxiliar para mostrar qual cliente (PF ou PJ) está associado
        if obj.cliente_fisico:
            return f"PF: {obj.cliente_fisico.nome_completo}"
        elif obj.cliente_juridico:
            return f"PJ: {obj.cliente_juridico.razao_social}"
        return "N/A"
    get_cliente_display.short_description = 'Cliente'

