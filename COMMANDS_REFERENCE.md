# DocWN Data Seeding Commands - Quick Reference

## 🚀 Quick Start

### 1. Clear Database and Seed Fresh Data
```bash
python manage.py clear_data_sql --confirm
python manage.py seed_data --users 30 --novels 50
```

### 2. View Current Data Statistics
```bash
python manage.py show_data
```

### 3. Setup User Groups and Permissions
```bash
python manage.py setup_groups
```

## 📋 Available Commands

### `seed_data` - Generate Test Data
```bash
python manage.py seed_data [options]
```
**Options:**
- `--users N` - Number of users (default: 50)
- `--authors N` - Number of authors (default: 20)  
- `--artists N` - Number of artists (default: 15)
- `--tags N` - Number of tags (default: 30)
- `--novels N` - Number of novels (default: 100)
- `--chapters-per-novel N` - Average chapters per novel (default: 10)
- `--clear` - Clear existing data first

**Examples:**
```bash
## Data Seeding Commands

### Basic Commands

```bash
# Seed with default data (small dataset)
python manage.py seed_data

# Clear existing data and seed with fresh data
python manage.py seed_data --clear

# Display current database statistics
python manage.py show_data

# Clear all data (SQL-based for foreign key constraints)
python manage.py clear_data_sql
```

### Large Dataset for Pagination Testing

The seed command supports various parameters for creating huge datasets to test pagination performance:

#### Moderate Dataset (Good for general testing)
```bash
python manage.py seed_data --clear --users 500 --authors 100 --artists 50 --tags 50 --novels 1000 --chapters-per-novel 20
```

#### Large Dataset (Stress testing)
```bash
python manage.py seed_data --clear --users 2000 --authors 300 --artists 100 --tags 100 --novels 5000 --chapters-per-novel 50
```

#### Huge Dataset (Performance testing)
```bash
python manage.py seed_data --clear --users 5000 --authors 500 --artists 200 --tags 150 --novels 10000 --chapters-per-novel 100
```

### Custom Configuration

```bash
python manage.py seed_data --clear 
  --users 1000 
  --authors 200 
  --artists 100 
  --tags 80 
  --novels 2000 
  --chapters-per-novel 30
```

### Parameters

- `--users`: Number of users to create (default: 50)
- `--authors`: Number of authors to create (default: 20)
- `--artists`: Number of artists to create (default: 15)
- `--tags`: Number of tags/genres to create (default: 30)
- `--novels`: Number of novels to create (default: 100)
- `--chapters-per-novel`: Average chapters per novel (default: 15)
- `--clear`: Clear all existing data before seeding
```

### `clear_data_sql` - Clear Database
```bash
python manage.py clear_data_sql --confirm
```
**Safety:** Requires `--confirm` to prevent accidents  
**Note:** Preserves superuser accounts

### `show_data` - Display Statistics
```bash
python manage.py show_data
```
**Shows:**
- User/content/interaction statistics
- Sample credentials
- Top novels and authors
- Popular tags
- Data quality indicators
- Access URLs

### `setup_groups` - Configure Permissions
```bash
python manage.py setup_groups [--reset]
```
**Options:**
- `--reset` - Reset all groups before creating

## 🔑 Default Credentials

### Admin Account
- **Email:** admin@test.com
- **Username:** admin  
- **Password:** admin123456
- **Role:** Website Admin

### Fixed Test User Accounts (for easier testing)
All users have password: **password123**

| Username | Email | Display Name | Role | Description |
|----------|-------|--------------|------|-------------|
| reader1 | reader1@test.com | Nguyễn Văn An | USER | Yêu thích fantasy và adventure |
| reader2 | reader2@test.com | Trần Thị Bình | USER | Sinh viên văn học, đam mê romance |
| moderator1 | mod1@test.com | Lê Minh Cường | ADMIN | Quản trị viên với 5 năm kinh nghiệm |
| writer1 | writer1@test.com | Phạm Thu Hà | USER | Tác giả trẻ chuyên viết truyện tình cảm |
| bookworm | bookworm@test.com | Hoàng Văn Đức | USER | Đọc giả lâu năm, đã đọc 1000+ cuốn |
| student1 | student1@test.com | Võ Thị Mai | USER | Sinh viên thích light novel Nhật |
| teacher1 | teacher1@test.com | Ngô Thanh Sơn | ADMIN | Giáo viên văn học |
| otaku | otaku@test.com | Đặng Minh Tuấn | USER | Fan anime/manga, dịch light novel |

## 📊 Generated Data Overview

### Users (Fixed for easier testing)
- ✅ 8 predefined user personas with realistic profiles
- ✅ Mix of regular users and admins
- ✅ Vietnamese names and detailed descriptions
- ✅ Specific interests and backgrounds

### Content (Enhanced with rich formatting)
- ✅ Vietnamese literature classics
- ✅ International bestsellers  
- ✅ Rich HTML formatted chapter content
- ✅ Realistic dialogue and narrative structure

### Chapter Content Features
- ✅ **Rich HTML formatting** with headers, paragraphs, lists
- ✅ **Vietnamese narrative style** with dialogue and descriptions
- ✅ **Story progression** (opening, middle, ending content)
- ✅ **Interactive elements** like blockquotes and styled text
- ✅ **Author notes** and chapter separators
- ✅ **Realistic word counts** (2000-8000 words per chapter)

### Structure
- ✅ Authors (Vietnamese + International)
- ✅ Artists with biographical info
- ✅ Genre tags (English + Vietnamese)
- ✅ Volumes and chapters
- ✅ Content chunks for pagination

### Interactions
- ✅ Reviews with 1-5 star ratings
- ✅ Comments with reply threads
- ✅ Favorite novel collections
- ✅ Reading history tracking

## 🌐 Access URLs

### Frontend
- **Home:** `/`
- **Novels:** `/novels/`
- **Login:** `/accounts/login/`
- **Register:** `/accounts/register/`

### Admin
- **Admin Panel:** `/admin/`
- **Users:** `/admin/accounts/user/`
- **Novels:** `/admin/novels/novel/`
- **Reviews:** `/admin/interactions/review/`

## 🔧 Development Workflow

### Initial Setup
```bash
# Setup environment
python manage.py migrate
python manage.py setup_groups

# Seed data
python manage.py seed_data

# Start server  
python manage.py runserver
```

### Reset and Reseed
```bash
# Clear everything
python manage.py clear_data_sql --confirm

# Seed fresh data
python manage.py seed_data --users 50 --novels 100

# Check results
python manage.py show_data
```

### Testing Different Datasets
```bash
# Small dataset for testing
python manage.py clear_data_sql --confirm
python manage.py seed_data --users 10 --novels 20

# Large dataset for performance testing  
python manage.py clear_data_sql --confirm
python manage.py seed_data --users 200 --novels 500

# Minimal dataset
python manage.py clear_data_sql --confirm
python manage.py seed_data --users 5 --novels 10 --chapters-per-novel 3
```

## ⚡ Performance Tips

### For Large Datasets
- Use smaller chunk sizes for chapters
- Consider running seeding in background
- Monitor database performance

### For Development
- Use smaller datasets (10-20 novels)
- Clear and reseed frequently
- Use consistent test credentials

## 🔍 Data Quality Checks

Run `show_data` to verify:
- ✅ Users have profiles
- ✅ Novels have content (chapters)
- ✅ Realistic interaction ratios
- ✅ Proper approval status distribution

## 🚨 Troubleshooting

### Foreign Key Errors
Use `clear_data_sql` instead of `clear_data` for MySQL

### Slug Duplicates  
Fixed in current version - novels created individually

### Performance Issues
Reduce dataset size for development:
```bash
python manage.py seed_data --users 20 --novels 30
```

---

**Last Updated:** August 28, 2025  
**Commands Location:** `novels/management/commands/`  
**Documentation:** `DATA_SEEDING_GUIDE.md`
