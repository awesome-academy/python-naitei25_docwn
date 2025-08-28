document.addEventListener("click", function (e) {
  if (e.target.closest(".view-more-replies")) {
    const btn = e.target.closest(".view-more-replies");
    const id = btn.dataset.id;
    const replies = document.querySelector(`.extra-replies-${id}`);
    if (replies) {
      if (replies.classList.contains("d-none")) {
        replies.classList.remove("d-none");
        btn.innerHTML = `<i class="fas fa-chevron-up"></i> ${btn.dataset.hideText}`;
      } else {
        replies.classList.add("d-none");
        btn.innerHTML = `<i class="fas fa-chevron-down"></i> ${btn.dataset.showText}`;
      }
    }
  }
});


