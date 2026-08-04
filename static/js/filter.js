// Фильтр проектов по категориям на главной. Без зависимостей.
(function () {
  const buttons = document.querySelectorAll(".filter__btn");
  const groups = document.querySelectorAll(".project-group");
  if (!buttons.length) return;

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const filter = btn.dataset.filter;

      buttons.forEach((b) => b.classList.toggle("is-active", b === btn));

      groups.forEach((group) => {
        const show = filter === "all" || group.dataset.category === filter;
        group.hidden = !show;
      });
    });
  });
})();
