from django.urls import path
from . import views

app_name = 'utils'

urlpatterns = [
    # Rotas para validação de dados
    path('validate/cpf/', views.validate_cpf, name='validate_cpf'),
    path('validate/cnpj/', views.validate_cnpj, name='validate_cnpj'),
    
    # Rotas para obtenção de dados
    path('cep-info/', views.get_cep_info, name='get_cep_info'),
    
    # Rotas para informações do sistema
    path('system-info/', views.system_info, name='system_info'),
    
    # Rotas para exportação e importação de dados
    # Estas rotas são genéricas e devem ser incluídas nas URLs específicas de cada app
    # path('export/<str:model_name>/', views.export_data, name='export_data'),
    # path('import/<str:model_name>/', views.import_data, name='import_data'),
    # path('sample-file/<str:model_name>/', views.generate_sample_file, name='generate_sample_file'),
]
