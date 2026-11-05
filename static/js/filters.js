const filterForm = document.querySelector("#project-filters");
const searchInput = document.querySelector("#project-search");
const categorySelect = document.querySelector("#project-category");

if (filterForm && searchInput && categorySelect) {
  let searchTimeout;

  searchInput.addEventListener("input", () => {
    window.clearTimeout(searchTimeout);
    searchTimeout = window.setTimeout(() => filterForm.requestSubmit(), 350);
  });

  categorySelect.addEventListener("change", () => {
    window.clearTimeout(searchTimeout);
    filterForm.requestSubmit();
  });
}
