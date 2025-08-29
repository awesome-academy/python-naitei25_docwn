from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db import transaction
from django.conf import settings
import random
from datetime import date, timedelta
from faker import Faker

from accounts.models import User, UserProfile
from novels.models import (
    Novel, Author, Artist, Tag, Volume, Chapter, Chunk, 
    Favorite, ReadingHistory
)
from interactions.models import Review, Comment
from constants import (
    UserRole, Gender, ProgressStatus, ApprovalStatus,
    MIN_RATE, MAX_RATE
)

class Command(BaseCommand):
    help = 'Seed the database with comprehensive test data'

    def __init__(self):
        super().__init__()
        self.fake = Faker(['en_US', 'vi_VN'])
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create'
        )
        parser.add_argument(
            '--authors',
            type=int,
            default=20,
            help='Number of authors to create'
        )
        parser.add_argument(
            '--artists',
            type=int,
            default=15,
            help='Number of artists to create'
        )
        parser.add_argument(
            '--tags',
            type=int,
            default=30,
            help='Number of tags to create'
        )
        parser.add_argument(
            '--novels',
            type=int,
            default=100,
            help='Number of novels to create'
        )
        parser.add_argument(
            '--chapters-per-novel',
            type=int,
            default=10,
            help='Average number of chapters per novel'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
            
        with transaction.atomic():
            self.create_superuser()
            self.create_users(options['users'])
            self.create_authors(options['authors'])
            self.create_artists(options['artists'])
            self.create_tags(options['tags'])
            self.create_novels(options['novels'])
            self.create_volumes_and_chapters(options['chapters_per_novel'])
            self.create_interactions()
            self.calculate_novel_ratings()
            self.calculate_word_counts()
            
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with test data!')
        )

    def clear_data(self):
        """Clear existing data"""
        self.stdout.write('Clearing existing data...')
        
        # Clear in correct order to avoid foreign key constraints
        Comment.objects.all().delete()
        Review.objects.all().delete()
        ReadingHistory.objects.all().delete()
        Favorite.objects.all().delete()
        Chunk.objects.all().delete()
        Chapter.objects.all().delete()
        Volume.objects.all().delete()
        Novel.objects.all().delete()
        Tag.objects.all().delete()
        Artist.objects.all().delete()
        Author.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.SUCCESS('Data cleared successfully!'))

    def create_superuser(self):
        """Create a superuser if it doesn't exist"""
        if not User.objects.filter(is_superuser=True).exists():
            user = User.objects.create_superuser(
                email='admin@docwn.com',
                username='admin',
                password='admin123456'
            )
            self.stdout.write(f'Created superuser: {user.email}')

    def create_users(self, count):
        """Create regular users with fixed information for easier testing"""
        self.stdout.write(f'Creating {count} users...')
        
        # Fixed user data for consistent testing
        user_data = [
            {
                'username': 'reader1', 'email': 'reader1@test.com', 'display_name': 'Nguyễn Văn An',
                'gender': Gender.MALE.value, 'age': 25, 'role': UserRole.USER.value,
                'description': 'Yêu thích đọc tiểu thuyết fantasy và adventure. Thường xuyên bình luận và đánh giá các tác phẩm.',
                'interest': 'Fantasy, Adventure, Light Novel, Manga'
            },
            {
                'username': 'reader2', 'email': 'reader2@test.com', 'display_name': 'Trần Thị Bình',
                'gender': Gender.FEMALE.value, 'age': 22, 'role': UserRole.USER.value,
                'description': 'Sinh viên văn học, đam mê những câu chuyện tình cảm và drama.',
                'interest': 'Romance, Drama, Historical Fiction'
            },
            {
                'username': 'moderator1', 'email': 'mod1@test.com', 'display_name': 'Lê Minh Cường',
                'gender': Gender.MALE.value, 'age': 30, 'role': UserRole.WEBSITE_ADMIN.value,
                'description': 'Quản trị viên trang web, có kinh nghiệm 5 năm trong việc kiểm duyệt nội dung.',
                'interest': 'All genres, Content moderation'
            },
            {
                'username': 'writer1', 'email': 'writer1@test.com', 'display_name': 'Phạm Thu Hà',
                'gender': Gender.FEMALE.value, 'age': 28, 'role': UserRole.USER.value,
                'description': 'Tác giả trẻ, chuyên viết truyện ngắn và tiểu thuyết tình cảm.',
                'interest': 'Romance, Slice of Life, Writing'
            },
            {
                'username': 'bookworm', 'email': 'bookworm@test.com', 'display_name': 'Hoàng Văn Đức',
                'gender': Gender.MALE.value, 'age': 35, 'role': UserRole.USER.value,
                'description': 'Đọc giả lâu năm, có sở thích sưu tập và review sách. Đã đọc hơn 1000 cuốn sách.',
                'interest': 'Mystery, Thriller, Science Fiction, Classic Literature'
            },
            {
                'username': 'student1', 'email': 'student1@test.com', 'display_name': 'Võ Thị Mai',
                'gender': Gender.FEMALE.value, 'age': 19, 'role': UserRole.USER.value,
                'description': 'Sinh viên năm 2, thích đọc light novel và manga Nhật Bản.',
                'interest': 'Light Novel, Manga, School Life, Comedy'
            },
            {
                'username': 'teacher1', 'email': 'teacher1@test.com', 'display_name': 'Ngô Thanh Sơn',
                'gender': Gender.MALE.value, 'age': 40, 'role': UserRole.WEBSITE_ADMIN.value,
                'description': 'Giáo viên văn học, quan tâm đến việc phát triển văn học trẻ.',
                'interest': 'Educational, Historical, Biography, Vietnamese Literature'
            },
            {
                'username': 'otaku', 'email': 'otaku@test.com', 'display_name': 'Đặng Minh Tuấn',
                'gender': Gender.MALE.value, 'age': 24, 'role': UserRole.USER.value,
                'description': 'Fan cuồng anime và manga, thường dịch light novel từ tiếng Nhật.',
                'interest': 'Light Novel, Anime, Manga, Fantasy, Isekai'
            }
        ]
        
        # Create base users, cycling through the fixed data
        created_users = []
        for i in range(count):
            data = user_data[i % len(user_data)]
            username = data['username'] if i < len(user_data) else f"{data['username']}{i+1}"
            email = data['email'] if i < len(user_data) else f"{data['username']}{i+1}@test.com"
            
            user = User(
                email=email,
                username=username,
                role=data['role'],
                is_active=random.choice([True, True, True, False]),  # 75% active
                is_blocked=random.choice([False, False, False, False, True]),  # 20% blocked
                is_email_verified=random.choice([True, True, True, False]),  # 75% verified
                date_joined=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
            )
            user.set_password('password123')
            created_users.append(user)
        
        User.objects.bulk_create(created_users)
        
        # Create profiles for users
        profiles = []
        all_users = list(User.objects.filter(is_superuser=False))
        for i, user in enumerate(all_users):
            data = user_data[i % len(user_data)]
            profile = UserProfile(
                user=user,
                display_name=data['display_name'],
                gender=data['gender'],
                birthday=date.today() - timedelta(days=365 * data['age']),
                avatar_url=f"https://i.pravatar.cc/300?u={user.username}",
                description=data['description'],
                interest=data['interest']
            )
            profiles.append(profile)
        
        UserProfile.objects.bulk_create(profiles)
        self.stdout.write(self.style.SUCCESS(f'Created {count} users with profiles'))

    def create_authors(self, count):
        """Create authors"""
        self.stdout.write(f'Creating {count} authors...')
        
        vietnamese_authors = [
            'Nguyễn Nhật Ánh', 'Tô Hoài', 'Vũ Trọng Phung', 'Nam Cao', 'Ngô Tất Tố',
            'Hồ Chí Minh', 'Xuân Diệu', 'Huy Cận', 'Chế Lan Viên', 'Tố Hữu'
        ]
        
        international_authors = [
            'Haruki Murakami', 'Paulo Coelho', 'J.K. Rowling', 'Stephen King',
            'Agatha Christie', 'Gabriel García Márquez', 'Leo Tolstoy', 'Jane Austen'
        ]
        
        # Track used names to ensure uniqueness
        used_names = set()
        authors = []
        
        for i in range(count):
            if i < len(vietnamese_authors):
                name = vietnamese_authors[i]
                country = 'Việt Nam'
            elif i < len(vietnamese_authors) + len(international_authors):
                name = international_authors[i - len(vietnamese_authors)]
                country = self.fake.country()
            else:
                # Generate unique names for remaining authors
                attempts = 0
                while attempts < 100:  # Prevent infinite loop
                    name = self.fake.name()
                    if name not in used_names:
                        break
                    attempts += 1
                else:
                    # If we can't find a unique name, append a number
                    name = f"{self.fake.name()} {i}"
                
                country = self.fake.country()
            
            # Ensure this name is unique
            if name in used_names:
                name = f"{name} {i}"
            
            used_names.add(name)
            
            author = Author(
                name=name,
                pen_name=self.fake.name() if random.choice([True, False]) else None,
                description=self.fake.text(max_nb_chars=500),
                birthday=self.fake.date_of_birth(minimum_age=20, maximum_age=90),
                gender=random.choice([g.value for g in Gender]),
                country=country,
                image_url=f"https://picsum.photos/400/600?random={i+100}"
            )
            authors.append(author)
        
        Author.objects.bulk_create(authors)
        self.stdout.write(self.style.SUCCESS(f'Created {count} authors'))

    def create_artists(self, count):
        """Create artists"""
        self.stdout.write(f'Creating {count} artists...')
        
        # Track used names to ensure uniqueness
        used_names = set()
        artists = []
        
        for i in range(count):
            # Generate unique names
            attempts = 0
            while attempts < 100:  # Prevent infinite loop
                name = self.fake.name()
                if name not in used_names:
                    break
                attempts += 1
            else:
                # If we can't find a unique name, append a number
                name = f"{self.fake.name()} {i}"
            
            used_names.add(name)
            
            artist = Artist(
                name=name,
                pen_name=self.fake.name() if random.choice([True, False]) else None,
                description=self.fake.text(max_nb_chars=300),
                birthday=self.fake.date_of_birth(minimum_age=18, maximum_age=70),
                gender=random.choice([g.value for g in Gender]),
                country=self.fake.country(),
                image_url=f"https://picsum.photos/400/600?random={i+200}"
            )
            artists.append(artist)
        
        Artist.objects.bulk_create(artists)
        self.stdout.write(self.style.SUCCESS(f'Created {count} artists'))

    def create_tags(self, count):
        """Create tags"""
        self.stdout.write(f'Creating {count} tags...')
        
        tag_names = [
            'Fantasy', 'Romance', 'Adventure', 'Mystery', 'Thriller', 'Crime',
            'Sci-Fi', 'Action', 'Drama', 'Comedy', 'Slice of Life', 'Historical',
            'Biography', 'Horror', 'Supernatural', 'Magic', 'Martial Arts',
            'School Life', 'Workplace', 'Family', 'Friendship', 'Coming of Age',
            'War', 'Politics', 'Philosophy', 'Psychology', 'Tragedy', 'Satire',
            'Xuyên không', 'Tu tiên', 'Huyền huyễn', 'Đô thị', 'Lịch sử',
            'Quân sự', 'Kinh doanh', 'Tình cảm', 'Học đường', 'Trinh thám'
        ]
        
        tags = []
        used_names = set()
        
        # First, use predefined names
        for i, name in enumerate(tag_names[:count]):
            slug = name.lower().replace(' ', '-').replace('ă', 'a').replace('ê', 'e').replace('ô', 'o').replace('ư', 'u').replace('â', 'a').replace('đ', 'd').replace('ù', 'u').replace('ữ', 'u').replace('ệ', 'e').replace('ị', 'i').replace('ọ', 'o').replace('ợ', 'o').replace('ồ', 'o').replace('ố', 'o').replace('ộ', 'o').replace('ờ', 'o').replace('ở', 'o').replace('ỡ', 'o').replace('ự', 'u').replace('ừ', 'u').replace('ử', 'u').replace('ữ', 'u').replace('ủ', 'u').replace('ũ', 'u').replace('ú', 'u').replace('ù', 'u').replace('ì', 'i').replace('í', 'i').replace('ĩ', 'i').replace('ỉ', 'i').replace('ị', 'i').replace('è', 'e').replace('é', 'e').replace('ẽ', 'e').replace('ẻ', 'e').replace('ẹ', 'e').replace('à', 'a').replace('á', 'a').replace('ã', 'a').replace('ả', 'a').replace('ạ', 'a').replace('ằ', 'a').replace('ắ', 'a').replace('ẵ', 'a').replace('ẳ', 'a').replace('ặ', 'a')
            tag = Tag(
                name=name,
                slug=slug,
                description=self.fake.text(max_nb_chars=100)
            )
            tags.append(tag)
            used_names.add(name)
        
        # If we need more tags than predefined, generate additional ones
        if count > len(tag_names):
            for i in range(len(tag_names), count):
                attempts = 0
                while attempts < 100:
                    name = self.fake.word().capitalize()
                    if name not in used_names:
                        break
                    attempts += 1
                else:
                    name = f"Tag {i}"
                
                used_names.add(name)
                slug = name.lower().replace(' ', '-')
                
                tag = Tag(
                    name=name,
                    slug=slug,
                    description=self.fake.text(max_nb_chars=100)
                )
                tags.append(tag)
        
        Tag.objects.bulk_create(tags)
        self.stdout.write(self.style.SUCCESS(f'Created {count} tags'))

    def create_novels(self, count):
        """Create novels"""
        self.stdout.write(f'Creating {count} novels...')
        
        novel_titles = [
            'Tôi Thấy Hoa Vàng Trên Cỏ Xanh', 'Mắt Biếc', 'Tuổi Thơ Dữ Dội',
            'Cho Tôi Xin Một Vé Đi Tuổi Thơ', 'Cô Gái Đến Từ Hôm Qua',
            'Totto-chan Cô Bé Bên Cửa Sổ', 'Nhà Giả Kim', 'Đắc Nhân Tâm',
            'Sapiens: Lược Sử Loài Người', 'Yuval Noah Harari',
            'The Chronicles of Narnia', 'Harry Potter and the Philosopher Stone',
            'The Lord of the Rings', 'A Song of Ice and Fire', 'The Hobbit',
            'Pride and Prejudice', '1984', 'To Kill a Mockingbird',
            'The Great Gatsby', 'One Hundred Years of Solitude'
        ]
        
        authors = list(Author.objects.all())
        artists = list(Artist.objects.all())
        tags = list(Tag.objects.all())
        users = list(User.objects.filter(is_active=True))
        
        # Create novels one by one to handle slug generation
        created_count = 0
        for i in range(count):
            if i < len(novel_titles):
                name = novel_titles[i]
            else:
                name = f"{self.fake.catch_phrase()} {i+1}"
            
            # Create novel object without slug first
            novel = Novel(
                name=name,
                summary=self.fake.text(max_nb_chars=1000),
                author=random.choice(authors) if authors else None,
                artist=random.choice(artists) if artists and random.choice([True, False]) else None,
                image_url=f"https://picsum.photos/400/600?random={i+300}",
                progress_status=random.choice([s.value for s in ProgressStatus]),
                approval_status=random.choice([
                    ApprovalStatus.APPROVED.value,
                    ApprovalStatus.APPROVED.value,
                    ApprovalStatus.APPROVED.value,
                    ApprovalStatus.PENDING.value,
                    ApprovalStatus.DRAFT.value
                ]),
                other_names=self.fake.sentence() if random.choice([True, False]) else None,
                view_count=random.randint(0, 50000),
                favorite_count=random.randint(0, 5000),
                rating_avg=0.0,  # Will be calculated from reviews
                word_count=0,    # Will be calculated from chapters
                created_by=random.choice(users) if users else None,
                is_anonymous=random.choice([False, False, False, True]),
                created_at=self.fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
            )
            
            try:
                # Save individual novel to trigger slug generation
                novel.save()
                created_count += 1
                
                # Assign tags to this novel
                if tags:
                    novel_tags = random.sample(tags, k=random.randint(1, min(5, len(tags))))
                    novel.tags.set(novel_tags)
                    
            except Exception as e:
                self.stdout.write(f'Error creating novel {name}: {e}')
        
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} novels'))

    def create_volumes_and_chapters(self, avg_chapters_per_novel):
        """Create volumes and chapters for novels with rich formatted content"""
        self.stdout.write('Creating volumes and chapters...')
        
        novels = Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value)
        chapter_counter = 1  # Global counter for unique chapter titles
        
        for novel in novels:
            # Create 1-3 volumes per novel
            volume_count = random.randint(1, 3)
            
            for vol_num in range(1, volume_count + 1):
                volume = Volume.objects.create(
                    novel=novel,
                    name=f"Tập {vol_num}",
                    position=vol_num
                )
                
                # Create chapters for this volume
                chapter_count = random.randint(max(1, min(3, avg_chapters_per_novel)), max(avg_chapters_per_novel, 5))
                
                for chap_num in range(1, chapter_count + 1):
                    chapter = Chapter.objects.create(
                        volume=volume,
                        title=f"Chương {chap_num}: {self.get_chapter_title()} #{chapter_counter}",
                        position=chap_num,
                        word_count=0,  # Will be calculated from chunks
                        view_count=random.randint(0, novel.view_count),
                        approved=random.choice([True, True, True, False]),
                        is_hidden=random.choice([False, False, False, True])
                    )
                    chapter_counter += 1
                    
                    # Create chunks with rich formatted content
                    chunk_count = random.randint(3, 6)
                    for chunk_num in range(1, chunk_count + 1):
                        content = self.generate_rich_chapter_content(chunk_num, chunk_count)
                        Chunk.objects.create(
                            chapter=chapter,
                            position=chunk_num,
                            content=content,
                            word_count=len(content.split())
                        )
        
        self.stdout.write(self.style.SUCCESS('Created volumes and chapters'))

    def get_chapter_title(self):
        """Generate realistic chapter titles"""
        titles = [
            "Khởi đầu của cuộc phiêu lưu",
            "Cuộc gặp gỡ định mệnh", 
            "Bí mật được hé lộ",
            "Thử thách đầu tiên",
            "Người bạn đồng hành",
            "Kẻ thù xuất hiện",
            "Quyết định khó khăn",
            "Trận chiến quyết định", 
            "Sự thật bất ngờ",
            "Hy sinh cao cả",
            "Chiến thắng tạm thời",
            "Những điều chưa biết",
            "Sức mạnh mới",
            "Hành trình tiếp theo",
            "Kết thúc và khởi đầu",
            "Người thầy bí ẩn",
            "Tình bạn đẹp",
            "Cái giá của sự nổi tiếng",
            "Bài học đầu đời",
            "Giấc mơ thành hiện thực",
            "Nỗi đau của chia ly",
            "Niềm vui bất ngờ",
            "Thử nghiệm nguy hiểm",
            "Tình yêu đầu đời",
            "Sự phản bội",
            "Tha thứ và quên lãng",
            "Tìm kiếm bản thân",
            "Hồi ức về quá khứ",
            "Tương lai mơ hồ",
            "Đêm dài khó ngủ",
            "Buổi sáng tỉnh giấc",
            "Dưới ánh trăng",
            "Giữa cơn mưa",
            "Nắng sau mưa",
            "Những bước chân cuối",
            "Câu chuyện mới bắt đầu"
        ]
        # Add random number to make it more unique
        base_title = random.choice(titles)
        suffix = random.choice(["", f" ({random.randint(1, 5)})", f" - Phần {random.randint(1, 3)}", ""])
        return base_title + suffix

    def generate_rich_chapter_content(self, chunk_num, total_chunks):
        """Generate rich formatted content for chapters"""
        
        # Story content templates with HTML formatting
        story_openings = [
            """<h3>Chương mở đầu</h3>
            <p>Ánh nắng buổi sáng len lỏi qua khung cửa sổ, đánh thức tôi khỏi giấc ngủ sâu. Hôm nay là một ngày đặc biệt, dù tôi vẫn chưa biết điều gì đang chờ đợi phía trước.</p>
            
            <p><strong>"Có lẽ mình nên bắt đầu từ đây,"</strong> tôi nghĩ thầm, nhìn ra ngoài khu vườn nhỏ sau nhà. Những cánh hoa anh đào đang rơi từng cánh một, tạo nên một khung cảnh thật lãng mạn.</p>
            
            <blockquote>
            <p><em>"Cuộc đời không phải là những gì xảy ra với bạn, mà là cách bạn phản ứng với những gì xảy ra."</em> - Câu nói mà mẹ tôi thường nhắc nhở.</p>
            </blockquote>""",
            
            """<p>Thành phố về đêm luôn có một vẻ đẹp riêng. Những ánh đèn neon lung linh, tiếng còi xe hòa quyện với tiếng cười nói của người qua đường. Tôi đi bộ trên phố, cảm nhận từng nhịp đập của trái tim mình.</p>
            
            <p><em>Liệu mình có đưa ra quyết định đúng đắn?</em> Câu hỏi này cứ lẽo đẽo trong đầu tôi suốt cả tuần qua.</p>
            
            <h4>Hồi tưởng</h4>
            <p>Tôi nhớ lại ngày đó, khi mọi thứ bắt đầu thay đổi. Đó là một buổi chiều mưa, tôi đang ngồi trong quán café quen thuộc thì gặp <strong>cô ấy</strong>...</p>""",
            
            """<h3>Cuộc đối thoại quan trọng</h3>
            <p>Căn phòng im lặng đến kỳ lạ. Chỉ có tiếng kim đồng hồ trên tường tích tắc đều đặn, như đang đếm ngược thời gian cho quyết định quan trọng nhất trong cuộc đời tôi.</p>
            
            <p><strong>"Anh đã suy nghĩ kỹ chưa?"</strong> giọng nói ấm áp ấy vang lên, làm tôi giật mình.</p>
            
            <p>Tôi quay lại, nhìn vào đôi mắt đầy trông chờ kia. <em>"Em biết không, có những quyết định mà một khi đã đưa ra thì không thể quay lại được nữa."</em></p>
            
            <ul>
            <li>Tôi có thể chọn con đường an toàn, ở lại thành phố này</li>
            <li>Hoặc dám mạo hiểm, bước vào cuộc phiêu lưu mới</li>
            <li>Cả hai lựa chọn đều có cái giá riêng của nó</li>
            </ul>"""
        ]
        
        story_middles = [
            """<p>Hành trình không hề dễ dàng như tôi tưởng tượng. Mỗi bước chân đi qua đều để lại dấu ấn sâu đậm trong lòng. Những thử thách liên tiếp ập đến, thử sự kiên trì và lòng dũng cảm của tôi.</p>
            
            <h4>Những bài học quý giá</h4>
            <p>Từ những người bạn mới gặp, tôi học được rằng:</p>
            <ol>
            <li><strong>Sự kiên nhẫn</strong> là chìa khóa của mọi thành công</li>
            <li><em>Lòng tin</em> có thể di chuyển cả những座núi cao nhất</li>
            <li>Đôi khi, <u>buông bỏ</u> cũng là một hình thức của sự dũng cảm</li>
            </ol>
            
            <blockquote>
            <p><em>"Trong cuộc sống, không có gì là tình cờ. Mọi cuộc gặp gỡ đều có ý nghĩa riêng của nó."</em></p>
            </blockquote>""",
            
            """<p>Cơn mưa bắt đầu rơi, từng giọt một rồi thành những hàng nước dài trên kính cửa sổ. Tôi ngồi bên cạnh, quan sát thế giới bên ngoài qua lớp kính mờ ấy.</p>
            
            <p><strong>Có những khoảnh khắc trong đời</strong>, chúng ta cần dừng lại và suy ngẫm về những gì đã qua. Tôi nghĩ về hành trình vừa rồi, về những người đã gặp, những điều đã học được.</p>
            
            <h4>Điểm chuyển mình</h4>
            <p>Chính lúc này, tôi nhận ra mình đã thay đổi rất nhiều. Không còn là cô gái ngại ngùng, hay chàng trai thiếu tự tin ngày nào. Tôi đã trưởng thành qua từng thử thách.</p>
            
            <p style="text-align: center;"><em>"Đôi khi ta phải đi rất xa mới nhận ra mình đã có sẵn những gì mình tìm kiếm."</em></p>"""
        ]
        
        story_endings = [
            """<h3>Hồi kết</h3>
            <p>Mặt trời đã lặn sau những dãy núi xa, để lại bầu trời với sắc cam rực rỡ. Tôi đứng trên đỉnh đồi, nhìn xuống thung lũng bên dưới - nơi hành trình của tôi bắt đầu.</p>
            
            <p><strong>Cuối cùng thì tôi cũng hiểu ra:</strong> không phải đích đến mà chính hành trình mới là điều quan trọng nhất. Những người tôi gặp, những bài học tôi học được, tất cả đều là kho báu vô giá.</p>
            
            <blockquote>
            <p><em>"Mỗi kết thúc đều là một khởi đầu mới. Và mỗi khởi đầu đều mang trong mình vô vàn khả năng."</em></p>
            </blockquote>
            
            <p>Tôi mỉm cười, quay lưng lại với quá khứ và bước về phía trước. Ngày mai sẽ là một ngày mới, với những cơ hội mới, những thử thách mới.</p>
            
            <p style="text-align: right;"><strong><em>- Hết chương -</em></strong></p>""",
            
            """<p>Giờ phút chia tay cuối cùng cũng đến. Dù biết trước điều này, nhưng khi nó thực sự xảy ra, trái tim tôi vẫn thắt lại.</p>
            
            <p><strong>"Chúng ta sẽ gặp lại nhau, phải không?"</strong> câu hỏi ấy vọng lên trong không gian tĩnh lặng.</p>
            
            <p>Tôi gật đầu, dù biết rằng có những cuộc chia ly chính là để không bao giờ gặp lại. Nhưng đó không phải là điều quan trọng. Quan trọng là những kỷ niệm đẹp mà chúng tôi đã cùng tạo ra.</p>
            
            <h4>Lời tạm biệt</h4>
            <p>Những bước chân cuối cùng trên con đường quen thuộc. Những âm thanh cuối cùng của một giai đoạn trong cuộc đời. Tôi không quay lại, vì biết rằng phía trước còn rất nhiều điều đang chờ đợi.</p>
            
            <p><em>Đây không phải là kết thúc, mà chỉ là dấu chấm hết của một chương. Cuốn sách cuộc đời vẫn còn rất nhiều trang trắng để viết tiếp...</em></p>"""
        ]
        
        # Choose content based on chunk position
        if chunk_num == 1:
            content = random.choice(story_openings)
        elif chunk_num == total_chunks:
            content = random.choice(story_endings)
        else:
            content = random.choice(story_middles)
        
        # Add some additional formatting elements
        additional_elements = [
            """<hr>
            <p style="font-style: italic; color: #666;">~ Ghi chú từ tác giả: Đây là một đoạn quan trọng trong câu chuyện ~</p>
            <hr>""",
            
            """<div style="border-left: 3px solid #007cba; padding-left: 15px; margin: 20px 0;">
            <p><strong>Suy ngẫm:</strong> Đôi khi những điều đơn giản nhất lại mang ý nghĩa sâu sắc nhất.</p>
            </div>""",
            
            """<p style="text-align: center; font-size: 18px; margin: 25px 0;">
            <strong>***</strong>
            </p>"""
        ]
        
        # Randomly add additional elements
        if random.choice([True, False]):
            content += "\n\n" + random.choice(additional_elements)
        
        return content

    def create_interactions(self):
        """Create reviews, comments, favorites, and reading history"""
        self.stdout.write('Creating interactions...')
        
        users = list(User.objects.filter(is_active=True))
        novels = list(Novel.objects.filter(approval_status=ApprovalStatus.APPROVED.value))
        chapters = list(Chapter.objects.filter(approved=True, is_hidden=False))
        
        if not users or not novels:
            self.stdout.write('No users or novels to create interactions for')
            return
        
        # Create reviews with realistic content
        self.stdout.write('Creating reviews...')
        reviews = []
        
        # Realistic review templates based on ratings
        review_templates = {
            5: [
                "Masterpiece! Tuyệt tác không thể bỏ qua. Cốt truyện hấp dẫn, nhân vật sâu sắc, văn phong xuất sắc. Đọc xong chỉ muốn đọc lại ngay.",
                "10/10! Truyện hay nhất mình từng đọc. Plot twist liên tục, character development tuyệt vời, không thể đoán trước được kết thúc.",
                "Xuất sắc từ đầu đến cuối! Tác giả có tài kể chuyện đặc biệt. Mọi chi tiết đều có ý nghĩa, không có phần nào thừa thãi.",
                "Đỉnh cao của thể loại này! Worldbuilding chi tiết, nhân vật sinh động, cảm xúc được truyền tải mạnh mẽ. Recommend 100%!"
            ],
            4: [
                "Truyện rất hay! Có một vài điểm nhỏ chưa hoàn hảo nhưng nhìn chung rất đáng đọc. Cốt truyện hấp dẫn và nhân vật được phát triển tốt.",
                "Good job! Mình thích cách tác giả xây dựng thế giới và nhân vật. Một số phần hơi dài nhưng vẫn giữ được sự hứng thú.",
                "Chất lượng cao! Plot interesting, character relatable. Có thể cải thiện thêm về pacing nhưng overall rất tốt.",
                "Đáng đọc! Nội dung phong phú, văn phong mượt mà. Chờ đợi những chapter tiếp theo từ tác giả."
            ],
            3: [
                "Ổn! Truyện có điểm hay nhưng cũng có những phần chưa thực sự thuyết phục. Average nhưng vẫn đọc được.",
                "Bình thường. Cốt truyện có potential nhưng development hơi chậm. Có thể cải thiện thêm về character depth.",
                "So-so. Có những moment hay nhưng cũng có phần boring. Mong tác giả sẽ improve ở những chapter sau.",
                "Decent. Không xuất sắc nhưng cũng không tệ. Phù hợp cho việc giải trí nhẹ nhàng."
            ],
            2: [
                "Hơi thất vọng. Cốt truyện có tiềm năng nhưng execution chưa tốt. Nhiều plot hole và character inconsistency.",
                "Chưa được. Pacing quá nhanh, character development yếu. Cần improve nhiều về storytelling.",
                "Below average. Có vài ý tưởng hay nhưng cách triển khai chưa thuyết phục. Dialogue cũng hơi gượng.",
                "Tạm được. Đọc để giết thời gian thôi, không có gì đặc biệt. Plot predictable và character flat."
            ],
            1: [
                "Rất thất vọng. Plot hole nhiều, character không consistent, pacing rất tệ. Không recommend.",
                "Poor quality. Cốt truyện lộn xộn, nhân vật stereotypical, văn phong chưa mature. Cần cải thiện nhiều.",
                "Tệ. Boring từ đầu đến cuối, không có điểm nào attractive. Waste of time.",
                "Not good. Nhiều lỗi logic, character development zero, plot rất weak. Skip đi."
            ]
        }
        
        # Create more reviews per novel for better rating calculation
        for _ in range(min(500, len(users) * 5)):  # Increased review count
            user = random.choice(users)
            novel = random.choice(novels)
            
            # Avoid duplicate reviews
            if not Review.objects.filter(user=user, novel=novel).exists():
                # Generate rating with realistic distribution (more 3-4 stars, fewer 1-5 stars)
                rating_weights = [0.05, 0.15, 0.35, 0.35, 0.10]  # 1-star to 5-star probability
                rating = random.choices(range(1, 6), weights=rating_weights)[0]
                
                # Choose realistic content based on rating
                content_choices = review_templates[rating]
                if random.choice([True, False]):  # 50% use template, 50% generate
                    content = random.choice(content_choices)
                else:
                    content = self.fake.text(max_nb_chars=400)
                
                review = Review(
                    user=user,
                    novel=novel,
                    rating=rating,
                    content=content,
                    created_at=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
                    is_active=random.choice([True, True, True, True, False])  # Higher active rate
                )
                reviews.append(review)
        
        Review.objects.bulk_create(reviews, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Created {len(reviews)} reviews'))
        
        # Create comments
        comments = []
        
        # Predefined realistic comment templates
        comment_templates = [
            "Truyện hay quá! Tôi đã đọc hết một ngày. Cốt truyện rất hấp dẫn và nhân vật được xây dựng rất tốt.",
            "Mình thích phong cách viết của tác giả. Cách mô tả chi tiết và cảm xúc rất chân thực.",
            "Chapter mới nhất thật sự bất ngờ! Không ngờ cốt truyện lại có twist như vậy.",
            "Đang chờ update chapter tiếp theo. Hi vọng tác giả sẽ ra chương mới sớm.",
            "Nhân vật chính ngày càng mature hơn qua từng chapter. Character development rất tốt.",
            "Worldbuilding trong truyện này thật ấn tượng. Tác giả đã xây dựng một thế giới rất chi tiết.",
            "Tôi khóc khi đọc phần này. Cảm xúc được truyền tải rất mạnh mẽ.",
            "Romance trong truyện này cute quá! Chemistry giữa các nhân vật rất tự nhiên.",
            "Plot twist cuối chapter khiến tôi phải đọc lại từ đầu. Quá xuất sắc!",
            "Mình recommend truyện này cho ai thích thể loại fantasy. Đáng đọc lắm!",
            "Tác giả có tài kể chuyện thật sự. Từng câu từng chữ đều có ý nghĩa.",
            "Đọc xong chỉ muốn binge read tiếp. Truyện này addictive quá!",
            "Fight scene được mô tả rất hay ho và sinh động. Có thể hình dung được từng động tác.",
            "Mystery trong truyện này khiến tôi phải suy đoán liên tục. Rất thú vị!",
            "Dialogue giữa các nhân vật rất natural. Không bị gượng gạo hay cứng nhắc."
        ]
        
        for _ in range(min(500, len(users) * 5)):
            user = random.choice(users)
            novel = random.choice(novels)
            
            # Use realistic comment or generate one
            if random.choice([True, False]):
                content = random.choice(comment_templates)
            else:
                content = self.fake.text(max_nb_chars=300)
            
            comment = Comment(
                user=user,
                novel=novel,
                content=content,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
                like_count=random.randint(0, 50),
                is_reported=random.choice([False, False, False, True]),
                is_active=random.choice([True, True, True, False])
            )
            comments.append(comment)
        
        Comment.objects.bulk_create(comments)
        
        # Create comment replies (nested comments)
        self.stdout.write('Creating comment replies...')
        parent_comments = list(Comment.objects.filter(parent_comment__isnull=True, is_active=True))
        
        if parent_comments:
            replies = []
            
            # Realistic reply templates
            reply_templates = [
                "Đồng ý với bạn! Mình cũng nghĩ vậy.",
                "Cảm ơn bạn đã chia sẻ. Mình có cùng cảm nhận.",
                "Ý kiến hay đấy! Mình chưa nghĩ tới điều này.",
                "Tôi có góc nhìn hơi khác một chút...",
                "Chính xác! Bạn nói đúng những gì tôi đang nghĩ.",
                "Thanks for sharing! Mình sẽ thử đọc theo cách bạn gợi ý.",
                "Mình thích cách bạn phân tích nhân vật này.",
                "Haha, tôi cũng từng có reaction tương tự!",
                "Wow, bạn để ý kỹ thật! Mình chưa chú ý tới detail này.",
                "Spoiler cảnh báo! Nhưng mình đồng ý với bạn về twist này.",
                "Bạn đọc nhanh quá! Mình vẫn còn đang ở chapter trước.",
                "Exactly! Đây là lý do tại sao tôi yêu thích series này.",
                "Mình nghĩ tác giả sẽ reveal thêm ở những chapter sau.",
                "Bạn có recommend truyện nào tương tự không?",
                "Cảm ơn bạn! Comment của bạn giúp mình hiểu sâu hơn."
            ]
            
            for _ in range(min(200, len(parent_comments) * 2)):  # Create up to 2 replies per parent comment on average
                parent_comment = random.choice(parent_comments)
                user = random.choice(users)
                
                # Generate reply content that references the parent
                if random.choice([True, False, False]):  # 33% chance for @mention
                    reply_content = f"@{parent_comment.user.username if parent_comment.user else 'Ẩn danh'} " + random.choice(reply_templates)
                else:
                    if random.choice([True, False]):  # 50% realistic, 50% generated
                        reply_content = random.choice(reply_templates)
                    else:
                        reply_starters = [
                            "Tôi đồng ý với bạn. ",
                            "Mình có ý kiến khác. ",
                            "Cảm ơn bạn đã chia sẻ. ",
                            "Thật thú vị! ",
                            "Quan điểm hay đấy. ",
                            "Mình nghĩ rằng ",
                        ]
                        reply_content = random.choice(reply_starters) + self.fake.text(max_nb_chars=150)
                
                # Create reply with a later timestamp than parent
                min_date = parent_comment.created_at
                max_date = timezone.now()
                
                reply = Comment(
                    user=user,
                    novel=parent_comment.novel,
                    parent_comment=parent_comment,
                    content=reply_content,
                    created_at=self.fake.date_time_between(start_date=min_date, end_date=max_date, tzinfo=timezone.get_current_timezone()),
                    like_count=random.randint(0, 25),  # Replies typically get fewer likes
                    is_reported=random.choice([False, False, False, False, True]),  # Lower report rate for replies
                    is_active=random.choice([True, True, True, True, False])  # Higher active rate for replies
                )
                replies.append(reply)
            
            Comment.objects.bulk_create(replies)
            self.stdout.write(self.style.SUCCESS(f'Created {len(replies)} comment replies'))
            
            # Create some nested replies (replies to replies)
            first_level_replies = list(Comment.objects.filter(
                parent_comment__isnull=False, 
                is_active=True
            ))
            
            if first_level_replies:
                nested_replies = []
                for _ in range(min(50, len(first_level_replies) // 2)):  # Create fewer nested replies
                    parent_reply = random.choice(first_level_replies)
                    user = random.choice(users)
                    
                    # Generate nested reply content
                    nested_starters = [
                        f"@{parent_reply.user.username if parent_reply.user else 'Ẩn danh'} ",
                        "Cảm ơn bạn đã phản hồi! ",
                        "Mình hiểu ý bạn. ",
                        "Đúng vậy! ",
                        "Có lý đấy. ",
                    ]
                    
                    nested_content = random.choice(nested_starters) + self.fake.text(max_nb_chars=150)
                    
                    # Ensure nested reply is after the parent reply
                    min_date = parent_reply.created_at
                    max_date = timezone.now()
                    
                    nested_reply = Comment(
                        user=user,
                        novel=parent_reply.novel,
                        parent_comment=parent_reply.parent_comment,  # Link to the original parent, not the reply
                        content=nested_content,
                        created_at=self.fake.date_time_between(start_date=min_date, end_date=max_date, tzinfo=timezone.get_current_timezone()),
                        like_count=random.randint(0, 15),  # Even fewer likes for nested replies
                        is_reported=False,  # Rarely reported
                        is_active=True  # Almost always active
                    )
                    nested_replies.append(nested_reply)
                
                if nested_replies:
                    Comment.objects.bulk_create(nested_replies)
                    self.stdout.write(self.style.SUCCESS(f'Created {len(nested_replies)} nested replies'))
        
        # Create favorites
        favorites = []
        for user in users:
            # Each user favorites 1-10 novels
            user_novels = random.sample(novels, k=random.randint(1, min(10, len(novels))))
            for novel in user_novels:
                favorite = Favorite(
                    user=user,
                    novel=novel,
                    created_at=self.fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
                )
                favorites.append(favorite)
        
        Favorite.objects.bulk_create(favorites, ignore_conflicts=True)
        
        # Create reading history
        if chapters:
            histories = []
            for user in users:
                # Each user reads some chapters
                user_chapters = random.sample(chapters, k=random.randint(1, min(20, len(chapters))))
                for chapter in user_chapters:
                    history = ReadingHistory(
                        user=user,
                        chapter=chapter,
                        novel=chapter.novel,
                        read_at=self.fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone()),
                        reading_progress=round(random.uniform(0.1, 1.0), 2)
                    )
                    histories.append(history)
            
            ReadingHistory.objects.bulk_create(histories, ignore_conflicts=True)
        
        self.stdout.write(self.style.SUCCESS('Created interactions'))

    def calculate_novel_ratings(self):
        """Calculate novel ratings based on actual reviews"""
        self.stdout.write('Calculating novel ratings from reviews...')
        
        from django.db.models import Avg, Count
        
        novels = Novel.objects.all()
        updated_count = 0
        
        for novel in novels:
            # Get active reviews for this novel
            reviews = novel.reviews.filter(is_active=True)
            
            if reviews.exists():
                # Calculate average rating
                avg_data = reviews.aggregate(
                    avg_rating=Avg('rating'),
                    review_count=Count('id')
                )
                
                novel.rating_avg = round(avg_data['avg_rating'], 1)
                novel.save(update_fields=['rating_avg'])
                updated_count += 1
            else:
                # No reviews yet, set to 0 or a default value
                novel.rating_avg = 0.0
                novel.save(update_fields=['rating_avg'])
        
        self.stdout.write(self.style.SUCCESS(f'Updated ratings for {updated_count} novels'))

    def calculate_word_counts(self):
        """Calculate word counts for novels, chapters, and chunks"""
        self.stdout.write('Calculating word counts from content...')
        
        # Update chunk word counts
        chunks = Chunk.objects.all()
        for chunk in chunks:
            if chunk.content:
                # Count words in HTML content (strip HTML tags for accurate count)
                import re
                text_content = re.sub('<[^<]+?>', '', chunk.content)
                word_count = len(text_content.split())
                chunk.word_count = word_count
                chunk.save(update_fields=['word_count'])
        
        # Update chapter word counts (sum from chunks)
        chapters = Chapter.objects.all()
        for chapter in chapters:
            total_words = sum(chunk.word_count for chunk in chapter.chunks.all())
            chapter.word_count = total_words
            chapter.save(update_fields=['word_count'])
        
        # Update novel word counts (sum from chapters through volumes)
        novels = Novel.objects.all()
        for novel in novels:
            total_words = 0
            for volume in novel.volumes.all():
                for chapter in volume.chapters.all():
                    total_words += chapter.word_count
            novel.word_count = total_words
            novel.save(update_fields=['word_count'])
        
        self.stdout.write(self.style.SUCCESS(f'Updated word counts for {chunks.count()} chunks, {chapters.count()} chapters, {novels.count()} novels'))
