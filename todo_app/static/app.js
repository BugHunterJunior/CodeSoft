/* Taskr frontend script
   - theme toggle
   - due date highlights
   - shortcuts
   - flash cleanup
*/

"use strict";

/* Theme init */
(function () {
  const savedTheme = localStorage.getItem("taskr-theme") || "light";
  document.documentElement.dataset.theme = savedTheme;
})();

document.addEventListener("DOMContentLoaded", function () {

  /* Theme toggle */
  const themeBtn = document.getElementById("theme-toggle");

  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      const curr = document.documentElement.dataset.theme;
      const next = curr === "dark" ? "light" : "dark";

      document.documentElement.dataset.theme = next;
      localStorage.setItem("taskr-theme", next);
    });
  }

  /* Due date logic */
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const cards = document.querySelectorAll(".task-card");

  cards.forEach(function (card) {
    const dueStr = card.dataset.due;
    if (!dueStr) return;

    const dueDate = new Date(dueStr + "T00:00:00");
    const done = card.classList.contains("is-complete");
    if (done) return;

    const overdueEl = card.querySelector(".badge-overdue");
    const todayEl   = card.querySelector(".badge-today");

    if (dueDate < today) {
      card.classList.add("is-overdue");
      if (overdueEl) overdueEl.style.display = "inline-flex";
    } 
    else if (dueDate.getTime() === today.getTime()) {
      card.classList.add("is-due-today");
      if (todayEl) todayEl.style.display = "inline-flex";
    }
  });

  /* Shortcuts */
  document.addEventListener("keydown", function (e) {

    const el = document.activeElement;
    const isInput = el && (
      el.tagName === "INPUT" ||
      el.tagName === "TEXTAREA" ||
      el.tagName === "SELECT"
    );

    // Ctrl+D → theme
    if (e.ctrlKey && e.key === "d") {
      e.preventDefault();
      if (themeBtn) themeBtn.click();
      return;
    }

    // Ctrl+F → focus search
    if (e.ctrlKey && e.key === "f") {
      const searchBox = document.getElementById("search-input");
      if (searchBox) {
        e.preventDefault();
        searchBox.focus();
        searchBox.select();
      }
      return;
    }

    // Enter → quick add
    if (e.key === "Enter" && !e.ctrlKey && !e.shiftKey) {
      const quickInput = document.getElementById("quick-title");

      if (el === quickInput) {
        e.preventDefault();
        const form = quickInput.closest("form");
        if (form) form.submit();
      }
    }

    // Escape → blur
    if (e.key === "Escape" && isInput) {
      el.blur();
    }
  });

  /* Flash auto hide */
  setTimeout(function () {
    const box = document.getElementById("flash-container");

    if (box) {
      box.style.transition = "opacity 0.4s ease, max-height 0.4s ease";
      box.style.opacity = "0";

      setTimeout(function () {
        box.remove();
      }, 400);
    }
  }, 4000);

  /* Quick add expand */
  const quickInput = document.getElementById("quick-title");
  const metaBox = document.querySelector(".quick-add-meta");

  if (quickInput && metaBox) {
    metaBox.style.display = "none";

    quickInput.addEventListener("focus", function () {
      metaBox.style.display = "flex";
    });

    document.addEventListener("click", function (e) {
      const wrapper = document.querySelector(".add-card");

      if (wrapper && !wrapper.contains(e.target)) {
        if (!quickInput.value.trim()) {
          metaBox.style.display = "none";
        }
      }
    });
  }

  /* Toggle complete (AJAX) */
  const toggleForms = document.querySelectorAll(".toggle-form");

  toggleForms.forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      fetch(form.action, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin"
      })
      .then(res => res.json())
      .then(data => {

        const card = form.closest(".task-card");
        const circle = form.querySelector(".toggle-circle");

        if (data.is_complete) {
          card.classList.add("is-complete");
          circle.textContent = "✓";
        } else {
          card.classList.remove("is-complete", "is-overdue", "is-due-today");
          circle.textContent = "";

          const dueStr = card.dataset.due;
          if (dueStr) {
            const due = new Date(dueStr + "T00:00:00");

            if (due < today) {
              card.classList.add("is-overdue");
            } else if (due.getTime() === today.getTime()) {
              card.classList.add("is-due-today");
            }
          }
        }

      })
      .catch(function () {
        form.submit(); // fallback
      });

    });
  });

});