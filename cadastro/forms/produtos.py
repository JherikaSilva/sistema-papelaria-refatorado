from django import forms
from django.core.validators import RegexValidator
from cadastro.models import Produto, CategoriaProduto

# --- Validador para o Nome do Produto ---
nome_produto_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9\s\-áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ()]+$',
    message="O nome do produto não pode conter caracteres especiais (exceto hífen e parênteses)."
)

class CategoriaProdutoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProduto
        fields = ('nome_da_categoria', 'descricao_da_categoria')
        widgets = {
            'nome_da_categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Papelaria de Escritório'}),
            'descricao_da_categoria': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva os produtos desta categoria...'}),
        }
        labels = {
            'nome_da_categoria': 'Nome da Categoria',
            'descricao_da_categoria': 'Descrição',
        }
    
    def clean_nome_da_categoria(self):
        """Garante que o nome da categoria não esteja em branco ou apenas com espaços."""
        nome = self.cleaned_data.get('nome_da_categoria')
        if nome and nome.strip() == '':
            raise forms.ValidationError("O nome da categoria não pode estar em branco.")
        return nome.strip().title() # Salva com a primeira letra maiúscula

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ('nome_do_produto', 'categorias')
        widgets = {
            'nome_do_produto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Caneta BIC Cristal'}),
            
            # --- MUDANÇA AQUI ---
            # Remova o 'attrs' do widget de categorias.
            # Ele ficará apenas como CheckboxSelectMultiple().
            'categorias': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'nome_do_produto': 'Nome do Produto',
            'categorias': 'Categorias',
        }
    
    def clean_nome_do_produto(self):
        """Limpa e formata o nome do produto."""
        nome = self.cleaned_data.get('nome_do_produto')
        if nome:
            return nome.strip().upper() # Salva em maiúsculas e sem espaços nas extremidades
        return nome

    def clean(self):
        """Validação para garantir que pelo menos uma categoria seja selecionada."""
        cleaned_data = super().clean()
        categorias = cleaned_data.get('categorias')
        if not categorias:
            raise forms.ValidationError("Você deve selecionar pelo menos uma categoria para este produto.")
        return cleaned_data