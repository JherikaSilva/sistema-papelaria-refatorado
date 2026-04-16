from django import forms
from cadastro.models import CompraCliente, CompraClienteHasProduto, CadastroPessoaFisica, CadastroPessoaJuridica, Produto

class CompraClienteForm(forms.ModelForm):
    class Meta:
        model = CompraCliente
        fields = ['pagamento_metodo', 'cliente_fisico', 'cliente_juridico', 'frete']
        widgets = {
            'pagamento_metodo': forms.Select(
                choices=[('Credito', 'Cartão de Crédito'), ('Debito', 'Cartão de Débito'), ('Pix', 'Pix'), ('Boleto', 'Boleto'), ('Dinheiro', 'Dinheiro')], 
                attrs={'class': 'form-control'}
            ),
            'frete': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'cliente_fisico': forms.Select(attrs={'class': 'form-control'}),
            'cliente_juridico': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = { 'frete': 'Valor do Frete (Opcional)' }
    
    def clean(self):
        cleaned_data = super().clean()
        cliente_pf = cleaned_data.get('cliente_fisico')
        cliente_pj = cleaned_data.get('cliente_juridico')
        if cliente_pf and cliente_pj:
            raise forms.ValidationError("Selecione apenas um tipo de cliente (Físico ou Jurídico) por compra.")
        if not cliente_pf and not cliente_pj:
            raise forms.ValidationError("Você deve selecionar um cliente para a compra.")
        return cleaned_data


class CompraClienteHasProdutoForm(forms.ModelForm):
    class Meta:
        model = CompraClienteHasProduto
        fields = ['produto', 'quantidade_produto', 'preco_unitario']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'quantidade_produto': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
            'preco_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
        }
        labels = { 'preco_unitario': 'Valor Unitário (R$)' }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'DELETE' in self.fields:
            self.fields['DELETE'].widget = forms.HiddenInput()