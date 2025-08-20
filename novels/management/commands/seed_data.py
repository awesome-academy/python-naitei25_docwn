"""
Django management command to generate seed data for the novel application
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

from accounts.models import UserProfile
from novels.models import (
    Author, Artist, Tag, Novel, Volume, Chapter, Chunk, Chapter
)
from novels.utils.chunk_manager import ChunkManager
from interactions.models import Comment, Review
from interactions.models import Comment, Review
from constants import (
    UserRole, Gender, ProgressStatus, ApprovalStatus
)

User = get_user_model()
fake = Faker(['en_US', 'vi_VN'])


class Command(BaseCommand):
    help = 'Generate comprehensive seed data for the novel application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of users to create (default: 20)'
        )
        parser.add_argument(
            '--authors',
            type=int,
            default=15,
            help='Number of authors to create (default: 15)'
        )
        parser.add_argument(
            '--artists',
            type=int,
            default=10,
            help='Number of artists to create (default: 10)'
        )
        parser.add_argument(
            '--tags',
            type=int,
            default=25,
            help='Number of tags to create (default: 25)'
        )
        parser.add_argument(
            '--novels',
            type=int,
            default=30,
            help='Number of novels to create (default: 30)'
        )
        parser.add_argument(
            '--volumes-per-novel',
            type=int,
            default=3,
            help='Average number of volumes per novel (default: 3)'
        )
        parser.add_argument(
            '--chapters-per-volume',
            type=int,
            default=10,
            help='Average number of chapters per volume (default: 10)'
        )
        parser.add_argument(
            '--comments',
            type=int,
            default=100,
            help='Number of comments to create (default: 100)'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=50,
            help='Number of reviews to create (default: 50)'
        )
        parser.add_argument(
            '--with-content',
            action='store_true',
            help='Generate realistic content for chapters (takes longer)'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write("Starting seed data generation...")
        self.create_user_groups()
        # Extract options
        user_count = options['users']
        author_count = options['authors'] 
        artist_count = options['artists']
        tag_count = options['tags']
        novel_count = options['novels']
        volumes_per_novel = options['volumes_per_novel']
        chapters_per_volume = options['chapters_per_volume']
        comment_count = options['comments']
        review_count = options['reviews']
        with_content = options['with_content']
        
        try:
            # Create basic data
            self.create_users(user_count)
            self.create_authors(author_count)
            self.create_artists(artist_count) 
            self.create_tags(tag_count)
            
            # Create novels with volumes, chapters, and chunks
            novels = self.create_novels(novel_count, volumes_per_novel, chapters_per_volume, with_content)
            
            # Create interactions
            users = list(User.objects.all())
            self.create_comments(comment_count, users, novels)
            self.create_reviews(review_count, users, novels)
            
            self.stdout.write(
                self.style.SUCCESS("Seed data generation completed successfully!")
            )
            
            # Display login credentials for testing
            self.stdout.write("\n" + "="*50)
            self.stdout.write(self.style.WARNING("TEST LOGIN CREDENTIALS:"))
            self.stdout.write("="*50)
            self.stdout.write("Admin Account:")
            self.stdout.write("  Email: admin@test.com")
            self.stdout.write("  Password: admin123")
            self.stdout.write("\nRegular Users:")
            self.stdout.write("  Email: user1@test.com, user2@test.com, etc.")
            self.stdout.write("  Password: 123456 (for all users)")
            self.stdout.write("="*50 + "\n")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error during seed data generation: {e}")
            )
            raise

    def create_user_groups(self):
        """Create user groups if they don't exist"""
        groups = ['Users', 'Authors', 'Admins']
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)

    def create_users(self, count):
        """Create random users with profiles"""
        users = []
        users_group = Group.objects.get(name='Users')
        
        # Include existing users in the list
        existing_users = list(User.objects.all())
        users.extend(existing_users)
        
        # Create a known admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                email='admin@test.com',
                username='admin',
                password='admin123',
                role=UserRole.WEBSITE_ADMIN.value,
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            admin_user.groups.add(users_group)
            
            # Create admin profile
            UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'display_name': 'Administrator',
                    'description': 'System Administrator Account',
                    'interest': 'Managing the platform',
                    'birthday': fake.date_of_birth(minimum_age=25, maximum_age=45),
                    'gender': Gender.MALE.value
                }
            )
            users.append(admin_user)
            self.stdout.write(f"Created admin user: admin@test.com / admin123")
        
        for i in range(count):
            # Create predictable usernames and emails for testing
            username = f"user{i+1}"
            email = f"user{i+1}@test.com"
            
            # Ensure unique username and email
            counter = 1
            base_username = username
            base_email = email
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            counter = 1
            while User.objects.filter(email=email).exists():
                email = f"user{i+1}_{counter}@test.com"
                counter += 1
            
            user = User.objects.create_user(
                email=email,
                username=username,
                password='123456',  # Simple, known password
                role=random.choice([UserRole.USER.value, UserRole.WEBSITE_ADMIN.value]),
                is_active=True
            )
            user.groups.add(users_group)
            
            # Create user profile
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'display_name': fake.name(),
                    'description': fake.text(max_nb_chars=200),
                    'interest': fake.text(max_nb_chars=100),
                    'birthday': fake.date_of_birth(minimum_age=16, maximum_age=80),
                    'gender': random.choice([choice[0] for choice in Gender.choices()])
                }
            )
            users.append(user)
            self.stdout.write(f"Created user: {email} / 123456")
        
        return users

    def create_authors(self, count):
        """Create random authors"""
        authors = []
        for i in range(count):
            name = fake.name()
            # Ensure unique name
            attempt = 0
            while Author.objects.filter(name=name).exists() and attempt < 50:
                name = fake.name()
                attempt += 1
            
            if attempt >= 50:
                name = f"{fake.name()} {fake.random_int(1000, 9999)}"
            
            author = Author.objects.create(
                name=name,
                pen_name=fake.name() if random.choice([True, False]) else None,
                description=fake.text(max_nb_chars=500),
                birthday=fake.date_of_birth(minimum_age=25, maximum_age=85),
                deathday=fake.date_of_birth(minimum_age=50, maximum_age=90) if random.choice([True, False, False]) else None,
                gender=random.choice([choice[0] for choice in Gender.choices()]),
                country=fake.country(),
                image_url=fake.image_url() if random.choice([True, False]) else None
            )
            authors.append(author)
        
        return authors

    def create_artists(self, count):
        """Create random artists"""
        artists = []
        for i in range(count):
            name = fake.name()
            # Ensure unique name
            attempt = 0
            while Artist.objects.filter(name=name).exists() and attempt < 50:
                name = fake.name()
                attempt += 1
                
            if attempt >= 50:
                name = f"{fake.name()} {fake.random_int(1000, 9999)}"
            
            artist = Artist.objects.create(
                name=name,
                pen_name=fake.name() if random.choice([True, False]) else None,
                description=fake.text(max_nb_chars=500),
                birthday=fake.date_of_birth(minimum_age=20, maximum_age=70),
                gender=random.choice([choice[0] for choice in Gender.choices()]),
                country=fake.country(),
                image_url=fake.image_url() if random.choice([True, False]) else None
            )
            artists.append(artist)
        
        return artists

    def create_tags(self, count):
        """Create random tags"""
        tag_names = [
            'Fantasy', 'Romance', 'Mystery', 'Thriller', 'Science Fiction',
            'Horror', 'Adventure', 'Comedy', 'Drama', 'Action',
            'Historical', 'Contemporary', 'Young Adult', 'Adult',
            'School Life', 'Slice of Life', 'Supernatural', 'Magic',
            'Martial Arts', 'Cultivation', 'System', 'Reincarnation',
            'Time Travel', 'Virtual Reality', 'Gaming'
        ]
        
        tags = []
        for i in range(min(count, len(tag_names))):
            tag_name = tag_names[i]
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={
                    'slug': slugify(tag_name),
                    'description': f"Stories related to {tag_name.lower()}"
                }
            )
            tags.append(tag)
        
        # If we need more tags, generate random ones
        for i in range(len(tag_names), count):
            tag_name = fake.word().title()
            # Ensure unique name
            while Tag.objects.filter(name=tag_name).exists():
                tag_name = fake.word().title()
            
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={
                    'slug': slugify(tag_name),
                    'description': fake.sentence()
                }
            )
            tags.append(tag)
        
        return tags

    def create_novels(self, count, volumes_per_novel, chapters_per_volume, with_content=True):
        """Create novels with volumes and chapters"""
        novels = []
        
        # Get existing authors, artists, and tags
        authors = list(Author.objects.all())
        artists = list(Artist.objects.all())
        tags = list(Tag.objects.all())
        
        self.stdout.write(f"Creating {count} novels...")
        
        for i in range(count):
            # Create novel in its own transaction to get the ID
            with transaction.atomic():
                novel = Novel.objects.create(
                    name=fake.sentence(nb_words=random.randint(2, 6)).rstrip('.'),
                    summary=fake.paragraph(nb_sentences=5),
                    progress_status=random.choice(['o', 'c', 's']),  # ongoing, completed, suspend
                    approval_status=random.choice(['d', 'p', 'a']),  # draft, pending, approved
                    author=random.choice(authors),
                    artist=random.choice(artists) if random.choice([True, False]) else None,
                    view_count=random.randint(0, 10000),
                    rating_avg=random.uniform(3.0, 5.0),
                    word_count=random.randint(1000, 100000),
                    favorite_count=random.randint(0, 1000),
                    is_anonymous=random.choice([True, False])
                )
                
                # Add random tags
                novel_tags = random.sample(tags, random.randint(2, 5))
                novel.tags.set(novel_tags)
                novels.append(novel)
            
            # Create volumes and chapters in separate transactions
            volume_count = random.randint(1, volumes_per_novel * 2)
            for vol_num in range(1, volume_count + 1):
                with transaction.atomic():
                    try:
                        volume = Volume.objects.create(
                            novel=novel,
                            name=f"Volume {vol_num}",
                            position=vol_num
                        )
                        self.stdout.write(f"Created volume: {volume.name} with ID: {volume.id}")
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Failed to create volume {vol_num}: {e}")
                        )
                        continue
                
                # Create chapters for this volume  
                chapter_count = random.randint(chapters_per_volume // 2, chapters_per_volume * 2)
                self.stdout.write(f"Creating {chapter_count} chapters for volume {volume.name}")
                for chap_num in range(1, chapter_count + 1):
                    chapter_title = f"Chapter {chap_num}: {fake.sentence(nb_words=4)}"
                    
                    if with_content:
                        # Generate realistic chapter content with HTML formatting
                        content = self.generate_chapter_content()
                    else:
                        content = f"<p>{fake.text(max_nb_chars=500)}</p>"
                    
                    # Create each chapter in its own transaction to get the ID
                    with transaction.atomic():
                        try:
                            chapter = Chapter.objects.create(
                                volume=volume,
                                title=chapter_title,
                                # Let the model generate the slug automatically
                                position=chap_num,
                                word_count=len(content.split()),
                                view_count=random.randint(0, 1000),
                                approved=random.choice([True, False]),
                                is_hidden=random.choice([True, False, False, False])  # Mostly not hidden
                            )
                            self.stdout.write(f"Created chapter: {chapter.title} with ID: {chapter.id}")
                            
                            # Now we can create chunks immediately since chapter has an ID
                            if with_content and chapter.id:
                                chunk_manager = ChunkManager()
                                try:
                                    chunks_created = chunk_manager.create_chunks_for_chapter(chapter, content)
                                    self.stdout.write(f"Created {chunks_created} chunks for {chapter.title}")
                                except Exception as e:
                                    self.stdout.write(
                                        self.style.WARNING(f"Could not create chunks for {chapter.title}: {e}")
                                    )
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"Failed to create chapter {chapter_title}: {e}")
                            )
        
        return novels

    def generate_chapter_content(self):
        """Generate realistic chapter content with HTML formatting"""
        paragraphs = []
        paragraph_count = random.randint(5, 15)
        
        for _ in range(paragraph_count):
            paragraph = fake.paragraph(nb_sentences=random.randint(3, 8))
            
            # Add some formatting randomly
            if random.choice([True, False]):
                # Add emphasis to some words
                words = paragraph.split()
                if len(words) > 3:
                    emphasis_word = random.choice(words[1:-1])
                    if random.choice([True, False]):
                        paragraph = paragraph.replace(emphasis_word, f"<strong>{emphasis_word}</strong>", 1)
                    else:
                        paragraph = paragraph.replace(emphasis_word, f"<em>{emphasis_word}</em>", 1)
            
            paragraphs.append(f"<p>{paragraph}</p>")
        
        # Occasionally add headers or dialogue
        if random.choice([True, False]):
            header = f"<h3>{fake.sentence(nb_words=3)}</h3>"
            insert_pos = random.randint(1, len(paragraphs) - 1)
            paragraphs.insert(insert_pos, header)
        
        return "\n".join(paragraphs)

    def create_comments(self, count, users, novels):
        """Create random comments"""
        for i in range(count):
            user = random.choice(users)
            novel = random.choice(novels)
            
            # 20% chance of being a reply to an existing comment
            parent_comment = None
            if random.random() < 0.2:
                existing_comments = Comment.objects.filter(novel=novel, parent_comment=None)
                if existing_comments.exists():
                    parent_comment = random.choice(existing_comments)
            
            Comment.objects.create(
                user=user,
                novel=novel,
                content=fake.text(max_nb_chars=300),
                parent_comment=parent_comment,
                like_count=random.randint(0, 50)
            )

    def create_reviews(self, count, users, novels):
        """Create random reviews"""
        created_reviews = set()
        
        for i in range(count):
            # Ensure unique user-novel combinations for reviews
            attempts = 0
            while attempts < 100:  # Prevent infinite loop
                user = random.choice(users)
                novel = random.choice(novels)
                
                if (user.id, novel.id) not in created_reviews:
                    Review.objects.create(
                        user=user,
                        novel=novel,
                        rating=random.randint(1, 5),
                        content=fake.text(max_nb_chars=500)
                    )
                    created_reviews.add((user.id, novel.id))
                    break
                
                attempts += 1
    
    def create_chunks_for_chapters(self):
        """Create chunks for all chapters after the main transaction is complete"""
        
        chunk_count = 0
        for chapter_id, content in self._chapters_to_chunk:
            try:
                # Get the chapter by ID to ensure it's fresh from the database
                chapter = Chapter.objects.get(id=chapter_id)
                
                # Create a single chunk with the full content for simplicity during seed generation
                Chunk.objects.create(
                    chapter=chapter,
                    position=1,
                    content=content,
                    word_count=len(content.split())
                )
                chunk_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Warning: Could not create chunks for chapter ID {chapter_id}: {e}")
                )
        
        self.stdout.write(f"Created {chunk_count} chunks")
