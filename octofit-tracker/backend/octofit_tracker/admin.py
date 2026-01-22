from django.contrib import admin
from .models import User, Team, Activity, Leaderboard, Workout


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'fitness_level', 'total_points', 'created_at']
    list_filter = ['fitness_level', 'created_at', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-total_points']
    readonly_fields = ['total_points', 'created_at', 'updated_at', 'last_login', 'date_joined']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'password')
        }),
        ('Profile', {
            'fields': ('profile_picture', 'bio', 'fitness_level')
        }),
        ('Statistics', {
            'fields': ('total_points',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for Team model"""
    list_display = ['name', 'created_by', 'get_members_count', 'total_points', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'created_by__username']
    ordering = ['-total_points']
    readonly_fields = ['total_points', 'created_at', 'updated_at']
    filter_horizontal = ['members']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Members', {
            'fields': ('members',)
        }),
        ('Statistics', {
            'fields': ('total_points',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_members_count(self, obj):
        return obj.members.count()
    get_members_count.short_description = 'Members'


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Admin interface for Activity model"""
    list_display = ['user', 'activity_type', 'duration', 'distance', 'calories_burned', 'points_earned', 'date']
    list_filter = ['activity_type', 'date', 'created_at']
    search_fields = ['user__username', 'activity_type', 'notes']
    ordering = ['-date']
    readonly_fields = ['points_earned', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'activity_type', 'date')
        }),
        ('Details', {
            'fields': ('duration', 'distance', 'calories_burned', 'notes')
        }),
        ('Points', {
            'fields': ('points_earned',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    """Admin interface for Leaderboard model"""
    list_display = ['get_entity_name', 'get_entity_type', 'period', 'rank', 'points', 'updated_at']
    list_filter = ['period', 'updated_at']
    search_fields = ['user__username', 'team__name']
    ordering = ['period', 'rank']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Entity', {
            'fields': ('user', 'team')
        }),
        ('Ranking', {
            'fields': ('period', 'rank', 'points')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_entity_name(self, obj):
        if obj.user:
            return obj.user.username
        elif obj.team:
            return obj.team.name
        return None
    get_entity_name.short_description = 'Entity'
    
    def get_entity_type(self, obj):
        if obj.user:
            return 'User'
        elif obj.team:
            return 'Team'
        return None
    get_entity_type.short_description = 'Type'


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    """Admin interface for Workout model"""
    list_display = ['name', 'difficulty_level', 'category', 'duration', 'get_exercises_count', 'created_at']
    list_filter = ['difficulty_level', 'category', 'created_at']
    search_fields = ['name', 'description', 'category']
    ordering = ['difficulty_level', 'duration']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Classification', {
            'fields': ('difficulty_level', 'category', 'duration')
        }),
        ('Details', {
            'fields': ('exercises', 'equipment_needed', 'target_muscles')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_exercises_count(self, obj):
        if isinstance(obj.exercises, list):
            return len(obj.exercises)
        return 0
    get_exercises_count.short_description = 'Exercises'
