from django import forms
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from cadastro.models import CadastroPessoaFisica, CadastroPessoaJuridica
from datetime import date

# --- Listas de Escolha ---
ESTADOS_BRASILEIROS = [
    ('--','Selecione'),
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
    ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
    ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'),
    ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
]

PORTE_EMPRESA = [
    ('--','Selecione'),
    ('MEI', 'Microempreendedor Individual - MEI'), ('ME', 'Microempresa - ME'),
    ('EPP', 'Empresa de Pequeno Porte - EPP'), ('GM', 'Empresa de Médio Porte'),
    ('G', 'Grande Empresa'),
]

# --- Validadores ---
cpf_validator = RegexValidator(
    regex=r'^\d{11}$',
    message="O CPF deve conter exatos 11 números (sem pontos ou traços)."
)

telefone_validator = RegexValidator(
    regex=r'^\(\d{2}\) \d{4,5}-\d{4}$',
    message="O telefone deve estar no formato (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."
)

cnpj_validator = RegexValidator(
    regex=r'^\d{14}$',
    message="O CNPJ deve conter exatos 14 números (sem pontos, traços ou barra)."
)


class CadastroPessoaFisicaForm(forms.ModelForm):

    class Meta:
        model = CadastroPessoaFisica
        fields = (
            'nome_completo', 'cpf', 'data_de_nascimento', 'email', 
            'telefone', 'cep', 'logradouro', 'complemento_endereco', 
            'bairro', 'cidade', 'estado'
        )

        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Somente números'}),
            'data_de_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento_endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(choices=ESTADOS_BRASILEIROS, attrs={'class': 'form-control'}),
        }
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            cpf_digits_only = ''.join(filter(str.isdigit, cpf))
            if len(cpf_digits_only) != 11:
                raise forms.ValidationError("O CPF deve conter exatos 11 números.")
        return cpf_digits_only

    def clean(self):
        cleaned_data = super().clean()
        data_nascimento = cleaned_data.get('data_nascimento')
        if data_nascimento and data_nascimento > timezone.now().date():
            raise forms.ValidationError("A data de nascimento não pode estar no futuro.")
        return cleaned_data



class CadastroPessoaJuridicaForm(forms.ModelForm):
    class Meta:
        model = CadastroPessoaJuridica
        fields = (
            'razao_social', 'nome_fantasia', 'cnpj', 'inscricao_estadual', 
            'inscricao_municipal', 'porte_empresa', 'logradouro', 
            'complemento_endereco', 'bairro', 'cidade', 'estado', 'cep', 
            'telefone', 'email'
        )
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Somente números'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento_endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(choices=ESTADOS_BRASILEIROS, attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'porte_empresa': forms.Select(choices=PORTE_EMPRESA, attrs={'class': 'form-control'}),
        }
    
    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj:
            cnpj_somente_digitos = ''.join(filter(str.isdigit, cnpj))
            if len(cnpj_somente_digitos) != 14:
                raise forms.ValidationError("O CNPJ deve conter exatos 14 números.")
        return cnpj_somente_digitos