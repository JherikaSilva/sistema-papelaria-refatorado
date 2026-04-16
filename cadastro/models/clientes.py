from django.db import models
from django.core.validators import MinValueValidator
from datetime import date

#Classe para dados em comum entre PF e PJ
class PessoaBase(models.Model):
    telefone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    logradouro = models.CharField(max_length=100, blank=True, null=True)
    complemento_endereco = models.CharField(max_length=40, blank=True, null=True)
    bairro = models.CharField(max_length=30, blank=True, null=True)
    cidade = models.CharField(max_length=32, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=8, blank=True, null=True)

    class Meta: #Essa classe indica ao django para não criar a tabela da classe PessoaBase
        abstract = True


class CadastroPessoaFisica(PessoaBase):
    id_cliente_pf = models.AutoField(primary_key=True) 
    cpf = models.CharField(max_length=11, unique=True)
    nome_completo = models.CharField(max_length=100)
    data_de_nascimento = models.DateField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(limit_value=date(1900, 1, 1), message="A data de nascimento não pode ser anterior a 1900.")]
    )
    
    def __str__(self):
        return self.nome_completo


class CadastroPessoaJuridica(PessoaBase):
    id_cliente_pj = models.AutoField(primary_key=True)
    cnpj = models.CharField(max_length=14, unique=True)
    razao_social = models.CharField(max_length=100)
    nome_fantasia = models.CharField(max_length=100, blank=True, null=True)
    inscricao_estadual = models.CharField(max_length=14, blank=True, null=True)
    inscricao_municipal = models.CharField(max_length=14, blank=True, null=True)
    porte_empresa = models.CharField(max_length=6, blank=True, null=True)
    cod_natureza_juridica = models.CharField(max_length=50, blank=True, null=True)
    cod_atividade_economica = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.razao_social
