from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cvs', views.CVViewSet, basename='cv')
router.register(r'templates', views.TemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
    
    # CV Versions nested routes
    path('cvs/<int:cv_pk>/versions/', views.CVVersionViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('cvs/<int:cv_pk>/versions/<int:pk>/', views.CVVersionViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
    path('cvs/<int:cv_pk>/versions/<int:pk>/restore/', views.CVVersionViewSet.as_view({
        'post': 'restore'
    })),
    
    # CV Applications nested routes
    path('cvs/<int:cv_pk>/applications/', views.CVApplicationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('cvs/<int:cv_pk>/applications/<int:pk>/', views.CVApplicationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
    path('cvs/<int:cv_pk>/applications/<int:pk>/update_status/', views.CVApplicationViewSet.as_view({
        'post': 'update_status'
    })),
    path('cvs/<int:cv_pk>/applications/<int:pk>/add_note/', views.CVApplicationViewSet.as_view({
        'post': 'add_note'
    })),
    
    # CV Statistics
    path('stats/', views.CVStatsViewSet.as_view({'get': 'list'}), name='cv-stats'),
]