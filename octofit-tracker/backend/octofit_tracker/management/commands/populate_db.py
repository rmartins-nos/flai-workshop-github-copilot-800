from django.core.management.base import BaseCommand
from pymongo import MongoClient
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Populate the octofit_db database with test data'

    def handle(self, *args, **options):
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['octofit_db']

        self.stdout.write(self.style.SUCCESS('Connected to octofit_db database'))

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        db.users.delete_many({})
        db.teams.delete_many({})
        db.activities.delete_many({})
        db.leaderboard.delete_many({})
        db.workouts.delete_many({})
        self.stdout.write(self.style.SUCCESS('Existing data cleared'))

        # Create unique index on email field for users
        db.users.create_index([("email", 1)], unique=True)
        self.stdout.write(self.style.SUCCESS('Created unique index on email field'))

        # Create teams
        teams = [
            {
                "name": "Team Marvel",
                "description": "Earth's Mightiest Heroes",
                "created_at": datetime.now(),
                "members": []
            },
            {
                "name": "Team DC",
                "description": "Justice League United",
                "created_at": datetime.now(),
                "members": []
            }
        ]
        
        team_result = db.teams.insert_many(teams)
        team_ids = {teams[i]["name"]: team_result.inserted_ids[i] for i in range(len(teams))}
        self.stdout.write(self.style.SUCCESS(f'Created {len(teams)} teams'))

        # Create users (superheroes)
        marvel_heroes = [
            {"name": "Iron Man", "email": "tony.stark@marvel.com", "team": "Team Marvel", "alias": "Tony Stark"},
            {"name": "Captain America", "email": "steve.rogers@marvel.com", "team": "Team Marvel", "alias": "Steve Rogers"},
            {"name": "Thor", "email": "thor.odinson@marvel.com", "team": "Team Marvel", "alias": "Thor Odinson"},
            {"name": "Black Widow", "email": "natasha.romanoff@marvel.com", "team": "Team Marvel", "alias": "Natasha Romanoff"},
            {"name": "Hulk", "email": "bruce.banner@marvel.com", "team": "Team Marvel", "alias": "Bruce Banner"},
            {"name": "Spider-Man", "email": "peter.parker@marvel.com", "team": "Team Marvel", "alias": "Peter Parker"},
        ]

        dc_heroes = [
            {"name": "Batman", "email": "bruce.wayne@dc.com", "team": "Team DC", "alias": "Bruce Wayne"},
            {"name": "Superman", "email": "clark.kent@dc.com", "team": "Team DC", "alias": "Clark Kent"},
            {"name": "Wonder Woman", "email": "diana.prince@dc.com", "team": "Team DC", "alias": "Diana Prince"},
            {"name": "The Flash", "email": "barry.allen@dc.com", "team": "Team DC", "alias": "Barry Allen"},
            {"name": "Aquaman", "email": "arthur.curry@dc.com", "team": "Team DC", "alias": "Arthur Curry"},
            {"name": "Green Lantern", "email": "hal.jordan@dc.com", "team": "Team DC", "alias": "Hal Jordan"},
        ]

        all_heroes = marvel_heroes + dc_heroes
        users = []
        
        for hero in all_heroes:
            user = {
                "name": hero["name"],
                "email": hero["email"],
                "alias": hero["alias"],
                "team_id": str(team_ids[hero["team"]]),
                "team_name": hero["team"],
                "total_points": random.randint(100, 1000),
                "created_at": datetime.now(),
                "profile": {
                    "avatar": f"avatar_{hero['name'].lower().replace(' ', '_')}.png",
                    "bio": f"Hero from {hero['team']}"
                }
            }
            users.append(user)
        
        user_result = db.users.insert_many(users)
        user_ids = list(user_result.inserted_ids)
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))

        # Update teams with member references
        marvel_user_ids = [str(user_ids[i]) for i in range(len(marvel_heroes))]
        dc_user_ids = [str(user_ids[i]) for i in range(len(marvel_heroes), len(all_heroes))]
        
        db.teams.update_one(
            {"name": "Team Marvel"},
            {"$set": {"members": marvel_user_ids}}
        )
        db.teams.update_one(
            {"name": "Team DC"},
            {"$set": {"members": dc_user_ids}}
        )

        # Create activities
        activity_types = ["Running", "Cycling", "Swimming", "Weightlifting", "Yoga", "Boxing"]
        activities = []
        
        for i, user_id in enumerate(user_ids):
            for _ in range(random.randint(5, 15)):
                activity_type = random.choice(activity_types)
                activities.append({
                    "user_id": str(user_id),
                    "user_name": users[i]["name"],
                    "activity_type": activity_type,
                    "duration": random.randint(20, 120),  # minutes
                    "distance": round(random.uniform(1.0, 20.0), 2) if activity_type in ["Running", "Cycling", "Swimming"] else None,
                    "calories": random.randint(100, 800),
                    "points": random.randint(10, 100),
                    "date": datetime.now() - timedelta(days=random.randint(0, 30)),
                    "notes": f"{activity_type} session completed"
                })
        
        db.activities.insert_many(activities)
        self.stdout.write(self.style.SUCCESS(f'Created {len(activities)} activities'))

        # Create leaderboard entries
        leaderboard = []
        for i, user in enumerate(users):
            leaderboard.append({
                "user_id": str(user_ids[i]),
                "user_name": user["name"],
                "team_id": user["team_id"],
                "team_name": user["team_name"],
                "total_points": user["total_points"],
                "rank": i + 1,
                "last_updated": datetime.now()
            })
        
        # Sort by points descending and update ranks
        leaderboard.sort(key=lambda x: x["total_points"], reverse=True)
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1
        
        db.leaderboard.insert_many(leaderboard)
        self.stdout.write(self.style.SUCCESS(f'Created {len(leaderboard)} leaderboard entries'))

        # Create workout suggestions
        workouts = [
            {
                "name": "Superhero Strength Training",
                "description": "Build strength like a superhero",
                "difficulty": "Advanced",
                "duration": 60,
                "category": "Strength",
                "exercises": [
                    {"name": "Bench Press", "sets": 4, "reps": 10},
                    {"name": "Squats", "sets": 4, "reps": 12},
                    {"name": "Deadlifts", "sets": 3, "reps": 8},
                    {"name": "Pull-ups", "sets": 3, "reps": 10}
                ],
                "created_at": datetime.now()
            },
            {
                "name": "Speed Training",
                "description": "Improve your speed and agility",
                "difficulty": "Intermediate",
                "duration": 45,
                "category": "Cardio",
                "exercises": [
                    {"name": "Sprint Intervals", "sets": 6, "duration": "30 seconds"},
                    {"name": "High Knees", "sets": 3, "reps": 20},
                    {"name": "Burpees", "sets": 3, "reps": 15},
                    {"name": "Jump Rope", "sets": 3, "duration": "2 minutes"}
                ],
                "created_at": datetime.now()
            },
            {
                "name": "Flexibility Flow",
                "description": "Improve flexibility and recovery",
                "difficulty": "Beginner",
                "duration": 30,
                "category": "Flexibility",
                "exercises": [
                    {"name": "Cat-Cow Stretch", "sets": 3, "reps": 10},
                    {"name": "Downward Dog", "sets": 3, "duration": "30 seconds"},
                    {"name": "Pigeon Pose", "sets": 2, "duration": "1 minute per side"},
                    {"name": "Seated Forward Fold", "sets": 3, "duration": "45 seconds"}
                ],
                "created_at": datetime.now()
            },
            {
                "name": "Hero Endurance",
                "description": "Build endurance for long missions",
                "difficulty": "Intermediate",
                "duration": 75,
                "category": "Endurance",
                "exercises": [
                    {"name": "Steady State Run", "sets": 1, "duration": "30 minutes"},
                    {"name": "Cycling", "sets": 1, "duration": "20 minutes"},
                    {"name": "Rowing", "sets": 1, "duration": "15 minutes"},
                    {"name": "Cool Down Walk", "sets": 1, "duration": "10 minutes"}
                ],
                "created_at": datetime.now()
            }
        ]
        
        db.workouts.insert_many(workouts)
        self.stdout.write(self.style.SUCCESS(f'Created {len(workouts)} workout suggestions'))

        # Final summary
        self.stdout.write(self.style.SUCCESS('\n=== Database Population Complete ==='))
        self.stdout.write(self.style.SUCCESS(f'Teams: {db.teams.count_documents({})}'))
        self.stdout.write(self.style.SUCCESS(f'Users: {db.users.count_documents({})}'))
        self.stdout.write(self.style.SUCCESS(f'Activities: {db.activities.count_documents({})}'))
        self.stdout.write(self.style.SUCCESS(f'Leaderboard entries: {db.leaderboard.count_documents({})}'))
        self.stdout.write(self.style.SUCCESS(f'Workouts: {db.workouts.count_documents({})}'))
        
        client.close()
