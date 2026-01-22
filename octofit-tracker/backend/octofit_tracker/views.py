from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import User, Team, Activity, Leaderboard, Workout
from .serializers import (
    UserSerializer, TeamSerializer, ActivitySerializer,
    LeaderboardSerializer, WorkoutSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['total_points', 'created_at', 'username']
    ordering = ['-total_points']

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Get all activities for a user"""
        user = self.get_object()
        activities = Activity.objects.filter(user=user)
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def teams(self, request, pk=None):
        """Get all teams for a user"""
        user = self.get_object()
        teams = user.teams.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get user statistics"""
        user = self.get_object()
        activities = Activity.objects.filter(user=user)
        
        stats = {
            'total_activities': activities.count(),
            'total_points': user.total_points,
            'total_duration': activities.aggregate(Sum('duration'))['duration__sum'] or 0,
            'total_distance': activities.aggregate(Sum('distance'))['distance__sum'] or 0,
            'total_calories': activities.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0,
            'teams_count': user.teams.count(),
        }
        return Response(stats)


class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Team model"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['total_points', 'created_at', 'name']
    ordering = ['-total_points']

    def perform_create(self, serializer):
        """Set the created_by field to the current user"""
        # In production, use request.user
        serializer.save()

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            team.members.add(user)
            return Response({'status': 'member added'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove a member from the team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            team.members.remove(user)
            return Response({'status': 'member removed'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get team statistics"""
        team = self.get_object()
        member_activities = Activity.objects.filter(user__in=team.members.all())
        
        stats = {
            'members_count': team.members.count(),
            'total_points': team.total_points,
            'total_activities': member_activities.count(),
            'total_duration': member_activities.aggregate(Sum('duration'))['duration__sum'] or 0,
            'total_distance': member_activities.aggregate(Sum('distance'))['distance__sum'] or 0,
        }
        return Response(stats)


class ActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for Activity model"""
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['activity_type', 'notes', 'user__username']
    ordering_fields = ['date', 'points_earned', 'duration', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        """Filter activities by query parameters"""
        queryset = Activity.objects.all()
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by activity type
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset

    def perform_create(self, serializer):
        """Set the user field if not provided"""
        # In production, use request.user
        serializer.save()


class LeaderboardViewSet(viewsets.ModelViewSet):
    """ViewSet for Leaderboard model"""
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['rank', 'points']
    ordering = ['rank']

    def get_queryset(self):
        """Filter leaderboard by query parameters"""
        queryset = Leaderboard.objects.all()
        
        # Filter by period
        period = self.request.query_params.get('period', 'all_time')
        queryset = queryset.filter(period=period)
        
        # Filter by type (user or team)
        entity_type = self.request.query_params.get('type')
        if entity_type == 'user':
            queryset = queryset.filter(user__isnull=False)
        elif entity_type == 'team':
            queryset = queryset.filter(team__isnull=False)
        
        return queryset

    @action(detail=False, methods=['post'])
    def update_rankings(self, request):
        """Update leaderboard rankings"""
        period = request.data.get('period', 'all_time')
        
        # Update user rankings
        self._update_user_rankings(period)
        
        # Update team rankings
        self._update_team_rankings(period)
        
        return Response({'status': 'rankings updated'})

    def _update_user_rankings(self, period):
        """Update user rankings for a given period"""
        # Get date range based on period
        end_date = timezone.now()
        if period == 'daily':
            start_date = end_date - timedelta(days=1)
        elif period == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        elif period == 'monthly':
            start_date = end_date - timedelta(days=30)
        else:  # all_time
            start_date = None

        # Calculate points for each user
        users = User.objects.all()
        user_points = []
        
        for user in users:
            activities = Activity.objects.filter(user=user)
            if start_date:
                activities = activities.filter(date__gte=start_date)
            points = activities.aggregate(Sum('points_earned'))['points_earned__sum'] or 0
            user_points.append((user, points))
        
        # Sort by points (descending)
        user_points.sort(key=lambda x: x[1], reverse=True)
        
        # Update or create leaderboard entries
        for rank, (user, points) in enumerate(user_points, start=1):
            Leaderboard.objects.update_or_create(
                user=user,
                period=period,
                defaults={'rank': rank, 'points': points}
            )

    def _update_team_rankings(self, period):
        """Update team rankings for a given period"""
        # Get date range based on period
        end_date = timezone.now()
        if period == 'daily':
            start_date = end_date - timedelta(days=1)
        elif period == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        elif period == 'monthly':
            start_date = end_date - timedelta(days=30)
        else:  # all_time
            start_date = None

        # Calculate points for each team
        teams = Team.objects.all()
        team_points = []
        
        for team in teams:
            activities = Activity.objects.filter(user__in=team.members.all())
            if start_date:
                activities = activities.filter(date__gte=start_date)
            points = activities.aggregate(Sum('points_earned'))['points_earned__sum'] or 0
            team_points.append((team, points))
        
        # Sort by points (descending)
        team_points.sort(key=lambda x: x[1], reverse=True)
        
        # Update or create leaderboard entries
        for rank, (team, points) in enumerate(team_points, start=1):
            Leaderboard.objects.update_or_create(
                team=team,
                period=period,
                defaults={'rank': rank, 'points': points}
            )


class WorkoutViewSet(viewsets.ModelViewSet):
    """ViewSet for Workout model"""
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['difficulty_level', 'duration', 'created_at']
    ordering = ['difficulty_level', 'duration']

    def get_queryset(self):
        """Filter workouts by query parameters"""
        queryset = Workout.objects.all()
        
        # Filter by difficulty level
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by duration
        max_duration = self.request.query_params.get('max_duration')
        if max_duration:
            queryset = queryset.filter(duration__lte=max_duration)
        
        return queryset

    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get personalized workout suggestions based on user fitness level"""
        fitness_level = request.query_params.get('fitness_level', 'beginner')
        category = request.query_params.get('category')
        
        queryset = Workout.objects.filter(difficulty_level=fitness_level)
        if category:
            queryset = queryset.filter(category=category)
        
        # Limit to 5 suggestions
        workouts = queryset[:5]
        serializer = self.get_serializer(workouts, many=True)
        return Response(serializer.data)
