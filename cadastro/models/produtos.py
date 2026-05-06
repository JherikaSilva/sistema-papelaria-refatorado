
from django.db import models

class CategoriaProduto(models.Model):
    id_categoria_produto = models.AutoField(primary_key=True)
    nome_da_categoria = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    descricao_da_categoria = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição")
    
    class Meta:
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"
        ordering = ["nome_da_categoria"]

    def __str__(self):
        return self.nome_da_categoria

class Produto(models.Model):
    id_produto = models.AutoField(primary_key=True)
    nome_do_produto = models.CharField(max_length=200, unique=True, verbose_name="Nome do Produto")
    categorias = models.ManyToManyField(CategoriaProduto, related_name='produtos', verbose_name="Categorias")
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Unitário (R$)")
    quantidade_estoque = models.PositiveIntegerField(default=0, verbose_name="Quantidade em Estoque")
    
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome_do_produto']
    
    def __str__(self):
        return self.nome_do_produto

    def save(self, *args, **kwargs):
        # Normaliza o nome para maiúsculas antes de salvar
        self.nome_do_produto = self.nome_do_produto.upper()
        super().save(*args, **kwargs)