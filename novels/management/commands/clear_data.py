from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import Group

from accounts.models import User, UserProfile
from novels.models import (
    Novel, Author, Artist, Tag, Volume, Chapter, Chunk, 
    Favorite, ReadingHistory
)
from interactions.models import Review, Comment

class Command(BaseCommand):
    help = 'Clear all data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data'
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR(
                    'This command will delete ALL data from the database. '
                    'Use --confirm to proceed.'
                )
            )
            return

        self.stdout.write('Clearing all data from database...')
        
        with transaction.atomic():
            # Clear in correct order to avoid foreign key constraints
            
            # First, clear many-to-many relationships to avoid constraint issues
            self.stdout.write('Clearing many-to-many relationships...')
            for novel in Novel.objects.all():
                novel.tags.clear()
            
            # Clear interactions (comments might have parent relationships)
            self.stdout.write('Clearing interactions...')
            Comment.objects.filter(parent_comment__isnull=False).delete()  # Delete replies first
            Comment.objects.all().delete()  # Then delete parent comments
            Review.objects.all().delete()
            
            # Clear novel relationships
            self.stdout.write('Clearing novel relationships...')
            ReadingHistory.objects.all().delete()
            Favorite.objects.all().delete()
            
            # Clear novel content (deepest first)
            self.stdout.write('Clearing novel content...')
            Chunk.objects.all().delete()
            Chapter.objects.all().delete()
            Volume.objects.all().delete()
            Novel.objects.all().delete()
            
            # Clear supporting data
            self.stdout.write('Clearing supporting data...')
            Tag.objects.all().delete()
            Artist.objects.all().delete()
            Author.objects.all().delete()
            
            # Clear user data (keep superusers)
            self.stdout.write('Clearing user data...')
            UserProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            
            # Groups (optional - uncomment if you want to clear groups too)
            # Group.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully cleared all data from database!')
        )
        self.stdout.write(
            self.style.WARNING('Note: Superuser accounts were preserved.')
        )
