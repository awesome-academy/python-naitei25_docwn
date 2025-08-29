from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, UserProfile
from novels.models import (
    Novel, Author, Artist, Tag, Volume, Chapter, Chunk, 
    Favorite, ReadingHistory
)
from interactions.models import Review, Comment

class Command(BaseCommand):
    help = 'Show comprehensive database statistics and sample data'

    def handle(self, *args, **options):
        self.show_statistics()
        self.show_sample_data()

    def show_statistics(self):
        """Display database statistics"""
        self.stdout.write(self.style.SUCCESS('\n=== DATABASE STATISTICS ===\n'))
        
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        verified_users = User.objects.filter(is_email_verified=True).count()
        blocked_users = User.objects.filter(is_blocked=True).count()
        
        self.stdout.write(f'👥 USERS:')
        self.stdout.write(f'  Total Users: {total_users}')
        self.stdout.write(f'  Active Users: {active_users}')
        self.stdout.write(f'  Verified Users: {verified_users}')
        self.stdout.write(f'  Blocked Users: {blocked_users}')
        
        # Content statistics
        total_authors = Author.objects.count()
        total_artists = Artist.objects.count()
        total_tags = Tag.objects.count()
        total_novels = Novel.objects.count()
        approved_novels = Novel.objects.filter(approval_status='a').count()
        total_volumes = Volume.objects.count()
        total_chapters = Chapter.objects.count()
        approved_chapters = Chapter.objects.filter(approved=True).count()
        total_chunks = Chunk.objects.count()
        
        self.stdout.write(f'\n📚 CONTENT:')
        self.stdout.write(f'  Authors: {total_authors}')
        self.stdout.write(f'  Artists: {total_artists}')
        self.stdout.write(f'  Tags: {total_tags}')
        self.stdout.write(f'  Total Novels: {total_novels}')
        self.stdout.write(f'  Approved Novels: {approved_novels}')
        self.stdout.write(f'  Volumes: {total_volumes}')
        self.stdout.write(f'  Total Chapters: {total_chapters}')
        self.stdout.write(f'  Approved Chapters: {approved_chapters}')
        self.stdout.write(f'  Content Chunks: {total_chunks}')
        
        # Interaction statistics
        total_reviews = Review.objects.count()
        active_reviews = Review.objects.filter(is_active=True).count()
        total_comments = Comment.objects.count()
        active_comments = Comment.objects.filter(is_active=True).count()
        parent_comments = Comment.objects.filter(parent_comment__isnull=True).count()
        reply_comments = Comment.objects.filter(parent_comment__isnull=False).count()
        total_favorites = Favorite.objects.count()
        total_reading_history = ReadingHistory.objects.count()
        
        self.stdout.write(f'\n💬 INTERACTIONS:')
        self.stdout.write(f'  Total Reviews: {total_reviews}')
        self.stdout.write(f'  Active Reviews: {active_reviews}')
        self.stdout.write(f'  Total Comments: {total_comments}')
        self.stdout.write(f'    ├─ Parent Comments: {parent_comments}')
        self.stdout.write(f'    └─ Reply Comments: {reply_comments}')
        self.stdout.write(f'  Active Comments: {active_comments}')
        self.stdout.write(f'  Favorites: {total_favorites}')
        self.stdout.write(f'  Reading History Records: {total_reading_history}')
        
        # Average statistics
        if approved_novels > 0:
            avg_rating = Novel.objects.filter(approval_status='a').aggregate(
                avg_rating=Avg('rating_avg')
            )['avg_rating']
            avg_views = Novel.objects.filter(approval_status='a').aggregate(
                avg_views=Avg('view_count')
            )['avg_views']
            
            self.stdout.write(f'\n📊 AVERAGES:')
            self.stdout.write(f'  Average Novel Rating: {avg_rating:.1f}/5.0' if avg_rating else 'N/A')
            self.stdout.write(f'  Average Novel Views: {avg_views:.0f}' if avg_views else 'N/A')

    def show_sample_data(self):
        """Display sample data with credentials"""
        self.stdout.write(self.style.SUCCESS('\n=== SAMPLE DATA & CREDENTIALS ===\n'))
        
        # Superusers
        superusers = User.objects.filter(is_superuser=True)
        if superusers.exists():
            self.stdout.write('🔑 SUPERUSER ACCOUNTS:')
            for user in superusers:
                self.stdout.write(f'  Email: {user.email}')
                self.stdout.write(f'  Username: {user.username}')
                self.stdout.write(f'  Password: admin123456 (if created by seed command)')
                self.stdout.write(f'  Role: {user.role}')
                self.stdout.write('')

        # Sample regular users
        sample_users = User.objects.filter(is_superuser=False, is_active=True)[:5]
        if sample_users.exists():
            self.stdout.write('👤 SAMPLE USER ACCOUNTS:')
            for user in sample_users:
                self.stdout.write(f'  Email: {user.email}')
                self.stdout.write(f'  Username: {user.username}')
                self.stdout.write(f'  Password: password123 (for seeded users)')
                self.stdout.write(f'  Role: {user.role}')
                self.stdout.write(f'  Display Name: {user.profile.display_name if hasattr(user, "profile") else "N/A"}')
                self.stdout.write('')

        # Top novels by views
        top_novels = Novel.objects.filter(approval_status='a').order_by('-view_count')[:5]
        if top_novels.exists():
            self.stdout.write('📖 TOP NOVELS BY VIEWS:')
            for i, novel in enumerate(top_novels, 1):
                self.stdout.write(f'  {i}. {novel.name}')
                self.stdout.write(f'     Author: {novel.author.name if novel.author else "Unknown"}')
                self.stdout.write(f'     Views: {novel.view_count:,}')
                self.stdout.write(f'     Rating: {novel.rating_avg}/5.0')
                self.stdout.write(f'     Status: {novel.get_progress_status_display()}')
                self.stdout.write('')

        # Sample authors
        sample_authors = Author.objects.all()[:5]
        if sample_authors.exists():
            self.stdout.write('✍️ SAMPLE AUTHORS:')
            for author in sample_authors:
                novel_count = author.novels.count()
                self.stdout.write(f'  {author.name}')
                self.stdout.write(f'     Country: {author.country or "Unknown"}')
                self.stdout.write(f'     Novels: {novel_count}')
                self.stdout.write('')

        # Popular tags
        popular_tags = Tag.objects.annotate(
            novel_count=Count('novels')
        ).order_by('-novel_count')[:10]
        
        if popular_tags.exists():
            self.stdout.write('🏷️ POPULAR TAGS:')
            for tag in popular_tags:
                self.stdout.write(f'  {tag.name}: {tag.novel_count} novels')

        # Recent activity
        recent_reviews = Review.objects.filter(is_active=True).order_by('-created_at')[:3]
        if recent_reviews.exists():
            self.stdout.write('\n⭐ RECENT REVIEWS:')
            for review in recent_reviews:
                self.stdout.write(f'  {review.user.username} rated "{review.novel.name}" {review.rating}/5')
                self.stdout.write(f'     "{review.content[:100]}..."')
                self.stdout.write('')

        # Data quality indicators
        self.stdout.write('\n🔍 DATA QUALITY INDICATORS:')
        
        novels_with_chapters = Novel.objects.filter(
            volumes__chapters__isnull=False
        ).distinct().count()
        
        self.stdout.write(f'  Novels with content: {novels_with_chapters}/{Novel.objects.count()}')
        
        users_with_profiles = User.objects.filter(profile__isnull=False).count()
        self.stdout.write(f'  Users with profiles: {users_with_profiles}/{User.objects.count()}')
        
        novels_with_reviews = Novel.objects.filter(reviews__isnull=False).distinct().count()
        self.stdout.write(f'  Novels with reviews: {novels_with_reviews}/{Novel.objects.count()}')

        # Access URLs
        self.stdout.write(self.style.SUCCESS('\n=== ACCESS INFORMATION ===\n'))
        self.stdout.write('🌐 ACCESS URLS:')
        self.stdout.write('  Admin Panel: /admin/')
        self.stdout.write('  User Login: /accounts/login/')
        self.stdout.write('  Home Page: /')
        self.stdout.write('  Novels List: /novels/')
        
        self.stdout.write('\n📋 DEFAULT CREDENTIALS:')
        self.stdout.write('  Admin: admin@docwn.com / admin123456')
        self.stdout.write('  Regular Users: [email from sample list] / password123')
        
        self.stdout.write('\n🔧 MANAGEMENT COMMANDS:')
        self.stdout.write('  Seed data: python manage.py seed_data')
        self.stdout.write('  Clear data: python manage.py clear_data --confirm')
        self.stdout.write('  Show data: python manage.py show_data')
        self.stdout.write('  Setup groups: python manage.py setup_groups')
