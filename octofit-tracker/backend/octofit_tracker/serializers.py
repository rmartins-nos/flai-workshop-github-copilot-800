from rest_framework import serializers
from .models import User, Team, Activity, Leaderboard, Workout


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    password = serializers.CharField(write_only=True, required=False)
    teams_count = serializers.SerializerMethodField()
    activities_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'profile_picture', 'bio', 'fitness_level', 'total_points',
            'password', 'teams_count', 'activities_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_points', 'created_at', 'updated_at']

    def get_teams_count(self, obj):
        return obj.teams.count()

    def get_activities_count(self, obj):
        return obj.activities.count()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Convert ObjectId to string if present"""
        representation = super().to_representation(instance)
        if hasattr(instance, '_id'):
            representation['id'] = str(instance._id)
        return representation


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model"""
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.IntegerField(write_only=True, required=False)
    members = UserSerializer(many=True, read_only=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'created_by', 'created_by_id',
            'members', 'member_ids', 'members_count', 'total_points',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_points', 'created_at', 'updated_at']

    def get_members_count(self, obj):
        return obj.members.count()

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        team = Team.objects.create(**validated_data)
        if member_ids:
            team.members.set(User.objects.filter(id__in=member_ids))
        return team

    def update(self, instance, validated_data):
        member_ids = validated_data.pop('member_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if member_ids is not None:
            instance.members.set(User.objects.filter(id__in=member_ids))
        return instance

    def to_representation(self, instance):
        """Convert ObjectId to string if present"""
        representation = super().to_representation(instance)
        if hasattr(instance, '_id'):
            representation['id'] = str(instance._id)
        return representation


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activity model"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Activity
        fields = [
            'id', 'user', 'user_id', 'username', 'activity_type',
            'duration', 'distance', 'calories_burned', 'points_earned',
            'notes', 'date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'points_earned', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """Convert ObjectId to string if present"""
        representation = super().to_representation(instance)
        if hasattr(instance, '_id'):
            representation['id'] = str(instance._id)
        return representation


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for Leaderboard model"""
    user = UserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    entity_name = serializers.SerializerMethodField()
    entity_type = serializers.SerializerMethodField()

    class Meta:
        model = Leaderboard
        fields = [
            'id', 'user', 'team', 'entity_name', 'entity_type',
            'period', 'rank', 'points', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_entity_name(self, obj):
        if obj.user:
            return obj.user.username
        elif obj.team:
            return obj.team.name
        return None

    def get_entity_type(self, obj):
        if obj.user:
            return 'user'
        elif obj.team:
            return 'team'
        return None

    def to_representation(self, instance):
        """Convert ObjectId to string if present"""
        representation = super().to_representation(instance)
        if hasattr(instance, '_id'):
            representation['id'] = str(instance._id)
        return representation


class WorkoutSerializer(serializers.ModelSerializer):
    """Serializer for Workout model"""
    exercises_count = serializers.SerializerMethodField()

    class Meta:
        model = Workout
        fields = [
            'id', 'name', 'description', 'difficulty_level', 'category',
            'duration', 'exercises', 'exercises_count', 'equipment_needed',
            'target_muscles', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_exercises_count(self, obj):
        if isinstance(obj.exercises, list):
            return len(obj.exercises)
        return 0

    def to_representation(self, instance):
        """Convert ObjectId to string if present"""
        representation = super().to_representation(instance)
        if hasattr(instance, '_id'):
            representation['id'] = str(instance._id)
        return representation
