from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.contrib.auth.models import Group

from accounts.models import User, UserProfile
from novels.models import (
    Novel, Author, Artist, Tag, Volume, Chapter, Chunk, 
    Favorite, ReadingHistory
)
from interactions.models import Review, Comment

class Command(BaseCommand):
    help = 'Clear all data from the database using SQL approach to handle foreign key constraints'

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

        self.stdout.write('Clearing all data from database using SQL approach...')
        
        with transaction.atomic():
            cursor = connection.cursor()
            
            try:
                # Disable foreign key checks for MySQL
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                
                # Get all tables except django system tables
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                
                # Tables to clear (in order)
                tables_to_clear = [
                    'interactions_comment',
                    'interactions_review', 
                    'interactions_notification',
                    'interactions_report',
                    'novels_readinghistory',
                    'novels_favorite',
                    'novels_chunk',
                    'novels_chapter',
                    'novels_volume',
                    'novels_novel_tags',
                    'novels_novel',
                    'novels_tag',
                    'novels_artist',
                    'novels_author',
                    'accounts_userprofile',
                    'social_auth_usersocialauth',
                    'django_admin_log',
                ]
                
                # Clear tables
                for table in tables_to_clear:
                    try:
                        cursor.execute(f"DELETE FROM {table};")
                        self.stdout.write(f'Cleared table: {table}')
                    except Exception as e:
                        self.stdout.write(f'Could not clear {table}: {e}')
                
                # Clear users but keep superusers
                cursor.execute("DELETE FROM accounts_user WHERE is_superuser = 0;")
                self.stdout.write('Cleared non-superuser accounts')
                
                # Re-enable foreign key checks
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                
            except Exception as e:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  # Re-enable even on error
                raise e
        
        self.stdout.write(
            self.style.SUCCESS('Successfully cleared all data from database!')
        )
        self.stdout.write(
            self.style.WARNING('Note: Superuser accounts were preserved.')
        )
