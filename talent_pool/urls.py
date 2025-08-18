from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Define o namespace para o app
app_name = 'talent_pool'

# Configuração do router para API REST
router = DefaultRouter()
router.register(r'talent-pools', views.TalentPoolViewSet)
router.register(r'talents', views.TalentViewSet)
router.register(r'talent-skills', views.TalentSkillViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'talent-tags', views.TalentTagViewSet)
router.register(r'talent-notes', views.TalentNoteViewSet)
router.register(r'saved-searches', views.SavedSearchViewSet)
router.register(r'talent-recommendations', views.TalentRecommendationViewSet)

# URLs para interface web
urlpatterns = [
    # Banco de Talentos - Página Principal
    path('', views.banco_talentos, name='banco_talentos'),
    
    # Bancos de Talentos
    path('talent-pools/', views.talent_pool_list, name='talent_pool_list'),
    path('talent-pools/<int:pk>/', views.talent_pool_detail, name='talent_pool_detail'),
    path('talent-pools/create/', views.talent_pool_create, name='talent_pool_create'),
    path('talent-pools/<int:pk>/edit/', views.talent_pool_edit, name='talent_pool_edit'),
    
    # Talentos
    path('talents/', views.talent_list, name='talent_list'),
    path('talents/<int:pk>/', views.talent_detail, name='talent_detail'),
    path('talents/create/', views.talent_create, name='talent_create'),
    path('talents/create/<int:candidate_id>/', views.talent_create, name='talent_create_for_candidate'),
    path('talents/<int:pk>/edit/', views.talent_edit, name='talent_edit'),
    
    # Habilidades de Talentos
    path('talent-skills/<int:pk>/remove/', views.remove_talent_skill, name='remove_talent_skill'),
    
    # Tags
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/<int:pk>/edit/', views.tag_edit, name='tag_edit'),
    path('talent-tags/<int:pk>/remove/', views.remove_talent_tag, name='remove_talent_tag'),
    
    # Buscas Salvas
    path('saved-searches/', views.saved_search_list, name='saved_search_list'),
    path('saved-searches/<int:pk>/', views.saved_search_detail, name='saved_search_detail'),
    path('saved-searches/<int:pk>/delete/', views.saved_search_delete, name='saved_search_delete'),
    
    # Recomendações
    path('talents/<int:talent_id>/recommend/', views.recommend_talent, name='recommend_talent'),
    path('talents/<int:talent_id>/recommend/<int:vacancy_id>/', views.recommend_talent, name='recommend_talent_for_vacancy'),
    path('recommendations/<int:pk>/update/', views.update_recommendation, name='update_recommendation'),
    
    # API REST
    path('api/', include(router.urls)),
]
