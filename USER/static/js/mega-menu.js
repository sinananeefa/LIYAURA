document.addEventListener("DOMContentLoaded", function () {

    var trigger = document.getElementById("megaTrigger");
    var panel = document.getElementById("megaPanel");
    var closeTimer = null;

    function openMega() {
        clearTimeout(closeTimer);
        if (trigger) trigger.classList.add("open");
        if (panel) panel.classList.add("open");
    }
    function scheduleCloseMega() {
        closeTimer = setTimeout(function () {
            if (trigger) trigger.classList.remove("open");
            if (panel) panel.classList.remove("open");
        }, 240);
    }
    function closeMega() {
        clearTimeout(closeTimer);
        if (trigger) trigger.classList.remove("open");
        if (panel) panel.classList.remove("open");
    }

    if (trigger && panel) {
        trigger.addEventListener("mouseenter", openMega);
        trigger.addEventListener("mouseleave", scheduleCloseMega);
        panel.addEventListener("mouseenter", openMega);
        panel.addEventListener("mouseleave", scheduleCloseMega);
        var triggerLink = trigger.querySelector(".mh-trigger-link");
        if (triggerLink) {
            triggerLink.addEventListener("click", function (e) {
                e.preventDefault();
                if (panel.classList.contains("open")) {
                    scheduleCloseMega();
                } else {
                    openMega();
                }
            });
        }
    }

    /* ===== Search overlay ===== */
    var searchToggle = document.getElementById("searchToggle");
    var searchOverlay = document.getElementById("searchOverlay");
    var searchClose = document.getElementById("searchClose");
    var searchInput = document.querySelector(".mh-search-input");

    function openSearch() {
        closeMega();
        if (searchOverlay) searchOverlay.classList.add("open");
        if (searchInput) setTimeout(function () { searchInput.focus(); }, 60);
    }
    function closeSearch() {
        if (searchOverlay) searchOverlay.classList.remove("open");
    }

    var searchBackdrop = document.getElementById("searchBackdrop");
    if (searchToggle) searchToggle.addEventListener("click", openSearch);
    if (searchClose) searchClose.addEventListener("click", closeSearch);
    if (searchBackdrop) searchBackdrop.addEventListener("click", closeSearch);
    if (searchOverlay) {
        searchOverlay.addEventListener("click", function (e) {
            if (e.target === searchOverlay) closeSearch();
        });
    }

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") { closeSearch(); closeMega(); }
    });

    document.addEventListener("click", function (e) {
        if (panel && !panel.contains(e.target) && trigger && !trigger.contains(e.target)) {
            closeMega();
        }
    });

    /* ===== Mobile menu ===== */
    var burger = document.getElementById("mhBurger");
    var mobile = document.getElementById("mhMobile");
    var burgerIcon = burger ? burger.querySelector("i") : null;

    function closeMobile() {
        if (mobile) mobile.classList.remove("open");
        if (burger) burger.classList.remove("open");
        if (burgerIcon) burgerIcon.className = "fa-solid fa-bars";
    }

    if (burger && mobile) {
        burger.addEventListener("click", function (e) {
            e.stopPropagation();
            closeSearch();
            var open = mobile.classList.toggle("open");
            burger.classList.toggle("open", open);
            if (burgerIcon) burgerIcon.className = open ? "fa-solid fa-xmark" : "fa-solid fa-bars";
        });
        mobile.querySelectorAll("nav > a").forEach(function (a) {
            a.addEventListener("click", closeMobile);
        });
    }

    /* ===== Mobile accordions (group + subs) ===== */
    document.querySelectorAll(".mm-group-btn, .mm-sub-btn").forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            var targetId = btn.getAttribute("data-target");
            var target = document.getElementById(targetId);
            var isOpen = btn.classList.toggle("open");
            if (target) target.classList.toggle("open", isOpen);

            var parent = btn.closest(".mm-group, .mm-sub");
            if (parent) {
                parent.parentElement.querySelectorAll(".mm-group-btn, .mm-sub-btn").forEach(function (sib) {
                    if (sib !== btn) {
                        sib.classList.remove("open");
                        var sid = document.getElementById(sib.getAttribute("data-target"));
                        if (sid) sid.classList.remove("open");
                    }
                });
            }
        });
    });

    document.addEventListener("click", function (e) {
        if (mobile && mobile.classList.contains("open") && !mobile.contains(e.target)) {
            if (burger && !burger.contains(e.target)) closeMobile();
        }
    });
});
