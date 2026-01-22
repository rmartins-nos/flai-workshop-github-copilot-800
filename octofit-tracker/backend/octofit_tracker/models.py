from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extended user model with fitness tracking fields"""
    profile_picture = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    fitness_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    total_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override the groups and user_permissions fields to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='octofit_user_set',
        related_query_name='octofit_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='octofit_user_set',
        related_query_name='octofit_user',
    )

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class Team(models.Model):
    """Team model for group fitness tracking"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    total_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teams'

    def __str__(self):
        return self.name


class Activity(models.Model):
    """Activity model for tracking workouts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(
        max_length=50,
        choices=[
            ('running', 'Running'),
            ('cycling', 'Cycling'),
            ('swimming', 'Swimming'),
            ('weightlifting', 'Weightlifting'),
            ('yoga', 'Yoga'),
            ('walking', 'Walking'),
            ('other', 'Other'),
        ]
    )
    duration = models.IntegerField(help_text='Duration in minutes')
    distance = models.FloatField(null=True, blank=True, help_text='Distance in kilometers')
    calories_burned = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'activities'
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.date}"

    def save(self, *args, **kwargs):
        # Calculate points based on duration and activity type
        if not self.points_earned:
            base_points = self.duration // 10  # 1 point per 10 minutes
            multiplier = {
                'running': 1.5,
                'cycling': 1.3,
                'swimming': 1.7,
                'weightlifting': 1.4,
                'yoga': 1.0,
                'walking': 0.8,
                'other': 1.0,
            }.get(self.activity_type, 1.0)
            self.points_earned = int(base_points * multiplier)
        
        super().save(*args, **kwargs)
        
        # Update user total points
        user = self.user
        user.total_points = sum(Activity.objects.filter(user=user).values_list('points_earned', flat=True))
        user.save()


class Leaderboard(models.Model):
    """Leaderboard model for tracking rankings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries', null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='leaderboard_entries', null=True, blank=True)
    period = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('all_time', 'All Time'),
        ]
    )
    rank = models.IntegerField()
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leaderboard'
        ordering = ['rank']
        unique_together = [['user', 'period'], ['team', 'period']]

    def __str__(self):
        entity = self.user.username if self.user else self.team.name
        return f"{entity} - {self.period} - Rank {self.rank}"


class Workout(models.Model):
    """Workout model for personalized workout suggestions"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ]
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ('strength', 'Strength Training'),
            ('cardio', 'Cardio'),
            ('flexibility', 'Flexibility'),
            ('balance', 'Balance'),
            ('hiit', 'HIIT'),
        ]
    )
    duration = models.IntegerField(help_text='Estimated duration in minutes')
    exercises = models.JSONField(default=list, help_text='List of exercises in the workout')
    equipment_needed = models.JSONField(default=list, help_text='List of equipment needed')
    target_muscles = models.JSONField(default=list, help_text='Target muscle groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workouts'

    def __str__(self):
        return f"{self.name} ({self.difficulty_level})"
