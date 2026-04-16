from django.db import models
from .clientes import CadastroPessoaFisica, CadastroPessoaJuridica
from .produtos import Produto

class CompraCliente(models.Model):
    data = models.DateField(auto_now_add=True)
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)
    pagamento_metodo = models.CharField(max_length=20)
    frete = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Deixe em branco caso não tenha frete.")
    
    cliente_fisico = models.ForeignKey(CadastroPessoaFisica, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras_pf')
    cliente_juridico = models.ForeignKey(CadastroPessoaJuridica, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras_pj')
    
    def __str__(self):
        return f"Compra {self.id} | Total: R${self.preco_total}"

class CompraClienteHasProduto(models.Model):
    compra_cliente = models.ForeignKey(CompraCliente, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade_produto = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2) # <-- ESSE CAMPO É ESSENCIAL

    class Meta:
        unique_together = ('compra_cliente', 'produto')
        verbose_name = "Item da Compra"
        verbose_name_plural = "Itens da Compra"

    def __str__(self):
        return f"{self.quantidade_produto}x {self.produto.nome_do_produto} na Compra {self.compra_cliente.id}"

class DadosGraficos(models.Model):
    # Armazena os dados já processados para os gráficos
    nome_grafico = models.CharField(max_length=50)
    dados_json = models.JSONField() # Ideal para armazenar listas e dicionários
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dado para Gráfico"
        verbose_name_plural = "Dados para Gráficos"

    def __str__(self):
        return f"{self.nome_grafico} (Atualizado em {self.atualizado_em.strftime('%d/%m/%Y %H:%M')})"