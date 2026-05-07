from django.urls import path
from . import views

urlpatterns = [
# Página inicial
    path("", views.index, name="index"), 
    
#Patch para o dashboard de gerenciamento
    path("dashboard/", views.dashboard, name="dashboard"),
# Páginas de cadastro do cliente, produto, categoria e venda.
    path("cadastro_cliente/fisica/", views.cadastro_cliente, {'tipo': 'fisica'}, name="cadastro_cliente_pf"),
    path("cadastro_cliente/juridica/", views.cadastro_cliente, {'tipo': 'juridica'}, name="cadastro_cliente_pj"),
    path("cadastro_produto/", views.cadastro_produto, name="cadastro_produto"),
    path("cadastro_categoria/", views.cadastro_categoria, name="cadastro_categoria"),
    path("produtos/importar/", views.importar_produtos, name="importar_produtos"),
    path("cadastro_venda/", views.cadastro_venda, name="cadastro_venda"),
#Listagens
    path("clientes/", views.lista_clientes, name="lista_clientes"),
    path("produtos/", views.lista_produtos, name="lista_produtos"),
    path("vendas/", views.lista_vendas, name="lista_vendas"),

# Página de gráficos.
    path("marketing/graficos/", views.graficos, name="graficos"),
    path("marketing/graficos/atualizar/", views.atualizar_graficos_view, name="atualizar_graficos"),

# Páginas de edição
# O <int:pk> captura o ID do cliente que será editado.
    path("categorias/editar/<int:pk>/", views.editar_categoria, name="editar_categoria"),
    path("produtos/editar/<int:pk>/", views.editar_produto, name="editar_produto"),
    path("vendas/editar/<int:pk>/", views.editar_venda, name="editar_venda"),
    path("clientes/pf/editar/<int:pk>/", views.editar_cliente, {'tipo': 'fisica'}, name="editar_cliente_pf"),
    path("clientes/pj/editar/<int:pk>/", views.editar_cliente, {'tipo': 'juridica'}, name="editar_cliente_pj"),
]

