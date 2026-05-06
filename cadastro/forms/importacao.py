from django import forms

class UploadFileForm(forms.Form):
    arquivo = forms.FileField( 
        label='Selecione um arquivo CSV ou Excel',
        help_text='Formatos aceitos: .csv, .xlsx. O arquivo deve conter as colunas: nome, preco, quantidade.'
    )
    
    