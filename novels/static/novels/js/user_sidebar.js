// User Sidebar JavaScript with jQuery
function toggleUserSidebar() {
  const $sidebar = $('#userSidebar');
  $sidebar.toggleClass('active');
  
  // Prevent body scrolling when sidebar is open
  $('body').css('overflow', $sidebar.hasClass('active') ? 'hidden' : '');
}

// Close sidebar when clicking outside
$(document).on('click', function(event) {
  const $sidebar = $('#userSidebar');
  const $trigger = $('[onclick="toggleUserSidebar()"]');
  
  if ($sidebar.hasClass('active') && 
      !$sidebar.find('.user-sidebar-content').is(event.target) && 
      !$sidebar.find('.user-sidebar-content').has(event.target).length &&
      !$trigger.is(event.target) && 
      !$trigger.has(event.target).length) {
    toggleUserSidebar();
  }
});

// Close sidebar on escape key
$(document).on('keydown', function(event) {
  if (event.key === 'Escape' && $('#userSidebar').hasClass('active')) {
    toggleUserSidebar();
  }
});
