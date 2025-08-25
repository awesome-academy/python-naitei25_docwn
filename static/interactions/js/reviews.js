class NovelReviews {
    constructor(novelSlug) {
        this.novelSlug = novelSlug;
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMore = true;
        this.currentFilters = {
            rating: '',
            sort: '-created_at'
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadReviews(true);
    }
    
    bindEvents() {
        // Rating filter change
        $('#rating-filter').on('change', (e) => {
            this.currentFilters.rating = e.target.value;
            this.resetAndLoad();
        });
        
        // Sort filter change
        $('#sort-filter').on('change', (e) => {
            this.currentFilters.sort = e.target.value;
            this.resetAndLoad();
        });
        
        // Load more button
        $('#load-more-reviews').on('click', () => {
            this.loadMoreReviews();
        });
    }
    
    resetAndLoad() {
        this.currentPage = 1;
        this.hasMore = true;
        $('#reviews-list').empty();
        $('.load-more-container').hide();
        $('.reviews-empty').hide();
        this.loadReviews(true);
    }
    
    async loadReviews(isInitial = false) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading(isInitial);
        
        try {
            const response = await fetch(this.buildUrl());
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.renderReviews(data, isInitial);
            
        } catch (error) {
            console.error('Error loading reviews:', error);
            this.showError();
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    async loadMoreReviews() {
        if (!this.hasMore || this.isLoading) return;
        
        this.currentPage++;
        await this.loadReviews();
    }
    
    buildUrl() {
        const params = new URLSearchParams({
            page: this.currentPage,
            rating: this.currentFilters.rating,
            sort: this.currentFilters.sort
        });
        
        return `/interactions/ajax/${this.novelSlug}/reviews/?${params.toString()}`;
    }
    
    showLoading(isInitial) {
        if (isInitial) {
            $('.reviews-loading').show();
        } else {
            $('#load-more-reviews').prop('disabled', true).html(`
                <div class="loading-spinner" style="width: 12px; height: 12px; margin-right: 6px; display: inline-block;"></div>
                ${gettext('Đang tải...')}
            `);
        }
    }
    
    hideLoading() {
        $('.reviews-loading').hide();
        $('#load-more-reviews').prop('disabled', false).html(`
            <i class="fas fa-chevron-down"></i>
            ${gettext('Tải thêm đánh giá')}
        `);
    }
    
    renderReviews(data, isInitial) {
        const reviewsHtml = data.reviews.map(review => this.renderReview(review)).join('');
        
        if (isInitial) {
            $('#reviews-list').html(reviewsHtml);
        } else {
            $('#reviews-list').append(reviewsHtml);
        }
        
        // Update pagination state
        this.hasMore = data.has_next;
        
        if (this.hasMore) {
            $('.load-more-container').show();
        } else {
            $('.load-more-container').hide();
        }
        
        // Show empty state if no reviews
        if (data.reviews.length === 0 && isInitial) {
            $('.reviews-list').hide();
            $('.reviews-empty').show();
        } else {
            $('.reviews-empty').hide();
            $('.reviews-list').show();
        }
        
        // Update review count
        $('.review-count').text(`(${data.total_reviews})`);
    }
    
    renderReview(review) {
        const starsHtml = this.renderStars(review.rating);
        
        return `
            <div class="review-item">
                <div class="review-header">
                    <div class="review-user">
                        <div class="user-avatar" style="background-image: url('${review.user.avatar_url}');"></div>
                        <div class="user-info">
                            <h4>${this.escapeHtml(review.user.username)}</h4>
                            <div class="review-date">${this.formatDate(review.created_at)}</div>
                        </div>
                    </div>
                    <div class="review-rating">
                        ${starsHtml}
                    </div>
                </div>
                <div class="review-content">
                    ${this.formatContent(review.content)}
                </div>
            </div>
        `;
    }
    
    renderStars(rating) {
        let starsHtml = '';
        for (let i = 1; i <= 5; i++) {
            const filled = i <= rating ? 'filled' : '';
            starsHtml += `<i class="fas fa-star ${filled}"></i>`;
        }
        return starsHtml;
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = now - date;
        const diffMinutes = Math.floor(diffTime / (1000 * 60));
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMinutes < 1) {
            return gettext('Vừa xong');
        } else if (diffMinutes < 60) {
            return gettext('%s phút trước').replace('%s', diffMinutes);
        } else if (diffHours < 24) {
            return gettext('%s giờ trước').replace('%s', diffHours);
        } else if (diffDays === 1) {
            return gettext('Hôm qua');
        } else if (diffDays < 7) {
            return gettext('%s ngày trước').replace('%s', diffDays);
        } else if (diffDays < 30) {
            const weeks = Math.floor(diffDays / 7);
            return gettext('%s tuần trước').replace('%s', weeks);
        } else {
            return date.toLocaleDateString('vi-VN');
        }
    }
    
    formatContent(content) {
        if (!content) return '';
        
        // Convert line breaks to paragraphs
        const paragraphs = content.split('\n\n').filter(p => p.trim());
        return paragraphs.map(p => `<p>${this.escapeHtml(p.trim())}</p>`).join('');
    }
    
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }
    
    showError() {
        $('#reviews-list').html(`
            <div class="reviews-error" style="text-align: center; padding: 30px; color: #dc3545;">
                <i class="fas fa-exclamation-triangle" style="font-size: 20px; margin-bottom: 8px;"></i>
                <p>${gettext('Không thể tải đánh giá. Vui lòng thử lại sau.')}</p>
            </div>
        `);
    }
}

// Initialize when document is ready
$(document).ready(function() {
    // Get novel slug from the current URL or a data attribute
    const novelSlug = window.location.pathname.split('/')[2]; // Adjust based on your URL structure
    
    if (novelSlug && $('.reviews-section').length > 0) {
        new NovelReviews(novelSlug);
    }
});
