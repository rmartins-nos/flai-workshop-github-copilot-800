"""octofit_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .views import (
    UserViewSet, TeamViewSet, ActivityViewSet,
    LeaderboardViewSet, WorkoutViewSet
)


# Create a router and register viewsets
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')
router.register(r'workouts', WorkoutViewSet, basename='workout')


@api_view(['GET'])
def api_root(request, format=None):
    """
    API Root endpoint that provides links to all available endpoints
    """
    codespace_name = os.environ.get('CODESPACE_NAME')
    if codespace_name:
        base_url = f"https://{codespace_name}-8000.app.github.dev"
    else:
        base_url = "http://localhost:8000"
    
    return Response({
        'message': 'Welcome to OctoFit Tracker API',
        'version': '1.0',
        'endpoints': {
            'users': reverse('user-list', request=request, format=format),
            'teams': reverse('team-list', request=request, format=format),
            'activities': reverse('activity-list', request=request, format=format),
            'leaderboard': reverse('leaderboard-list', request=request, format=format),
            'workouts': reverse('workout-list', request=request, format=format),
            'admin': f"{base_url}/admin/",
        },
        'documentation': {
            'users': {
                'list': 'GET /api/users/',
                'detail': 'GET /api/users/{id}/',
                'create': 'POST /api/users/',
                'update': 'PUT /api/users/{id}/',
                'delete': 'DELETE /api/users/{id}/',
                'activities': 'GET /api/users/{id}/activities/',
                'teams': 'GET /api/users/{id}/teams/',
                'stats': 'GET /api/users/{id}/stats/',
            },
            'teams': {
                'list': 'GET /api/teams/',
                'detail': 'GET /api/teams/{id}/',
                'create': 'POST /api/teams/',
                'update': 'PUT /api/teams/{id}/',
                'delete': 'DELETE /api/teams/{id}/',
                'add_member': 'POST /api/teams/{id}/add_member/',
                'remove_member': 'POST /api/teams/{id}/remove_member/',
                'stats': 'GET /api/teams/{id}/stats/',
            },
            'activities': {
                'list': 'GET /api/activities/',
                'detail': 'GET /api/activities/{id}/',
                'create': 'POST /api/activities/',
                'update': 'PUT /api/activities/{id}/',
                'delete': 'DELETE /api/activities/{id}/',
            },
            'leaderboard': {
                'list': 'GET /api/leaderboard/',
                'detail': 'GET /api/leaderboard/{id}/',
                'update_rankings': 'POST /api/leaderboard/update_rankings/',
            },
            'workouts': {
                'list': 'GET /api/workouts/',
                'detail': 'GET /api/workouts/{id}/',
                'create': 'POST /api/workouts/',
                'update': 'PUT /api/workouts/{id}/',
                'delete': 'DELETE /api/workouts/{id}/',
                'suggestions': 'GET /api/workouts/suggestions/',
            },
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api-root'),
    path('api/', api_root, name='api-root'),
    path('api/', include(router.urls)),
]
