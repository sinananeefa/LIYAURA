document.addEventListener("DOMContentLoaded", function () {

    /* ===== Navbar: shadow and compaction on scroll ===== */
    var nav = document.querySelector(".mega-header");
    function onNavScroll() {
        if (nav) {
            if (window.scrollY > 30) {
                nav.classList.add("scrolled");
            } else {
                nav.classList.remove("scrolled");
            }
        }
    }
    window.addEventListener("scroll", onNavScroll, { passive: true });
    onNavScroll();

    /* ===== Subtle Cinematic Parallax on Hero ===== */
    var ticking = false;
    window.addEventListener("scroll", function () {
        if (!ticking) {
            window.requestAnimationFrame(function () {
                var scrolled = window.scrollY;
                if (scrolled < 850) {
                    var activeSlide = document.querySelector(".hero-slide.active .hero-bg");
                    if (activeSlide) {
                        activeSlide.style.transform = "translate3d(0, " + (scrolled * 0.12) + "px, 0)";
                    }
                }
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });

    /* ===== Hero slider ===== */
    var slides = document.querySelectorAll(".hero-slide");
    var dots = document.querySelectorAll(".hero-dot");
    if (slides.length) {
        var current = 0;
        var timer = null;

        function goTo(index) {
            slides[current].classList.remove("active");
            if (dots[current]) dots[current].classList.remove("active");
            current = (index + slides.length) % slides.length;
            slides[current].classList.add("active");
            if (dots[current]) dots[current].classList.add("active");

            var bg = slides[current].querySelector(".hero-bg");
            if (bg) {
                bg.style.animation = "none";
                void bg.offsetWidth;
                bg.style.animation = "";
                bg.style.transform = "translate3d(0, 0, 0)";
            }
        }

        dots.forEach(function (dot, i) {
            dot.addEventListener("click", function () {
                goTo(i);
                restart();
            });
        });

        function restart() {
            clearInterval(timer);
            timer = setInterval(function () { goTo(current + 1); }, 6500);
        }
        restart();
    }

    /* ===== Interactive Occasion Showcase Switcher ===== */
    var occTabs = document.querySelectorAll(".occ-tab");
    var occSlides = document.querySelectorAll(".occ-feature-slide");
    var occRail = document.getElementById("occRail");
    var occRailPrev = document.getElementById("occRailPrev");
    var occRailNext = document.getElementById("occRailNext");

    function setActiveOccasion(targetId) {
        occTabs.forEach(function (tab) {
            if (tab.getAttribute("data-target") === targetId) {
                tab.classList.add("active");
            } else {
                tab.classList.remove("active");
            }
        });

        occSlides.forEach(function (slide) {
            if (slide.id === targetId) {
                slide.classList.add("active");
            } else {
                slide.classList.remove("active");
            }
        });
    }

    occTabs.forEach(function (tab) {
        var targetId = tab.getAttribute("data-target");
        tab.addEventListener("click", function () {
            setActiveOccasion(targetId);
        });
        tab.addEventListener("mouseenter", function () {
            setActiveOccasion(targetId);
        });
    });

    if (occRailPrev && occRail) {
        occRailPrev.addEventListener("click", function () {
            occRail.scrollBy({ top: -140, behavior: "smooth" });
        });
    }
    if (occRailNext && occRail) {
        occRailNext.addEventListener("click", function () {
            occRail.scrollBy({ top: 140, behavior: "smooth" });
        });
    }

    /* ===== How LIYAURA Works Progress Flow ===== */
    var howSection = document.querySelector(".how-works-section");
    var howProgressFill = document.getElementById("howProgressFill");
    var stepCards = document.querySelectorAll(".how-flow-wrap .step-card");
    if (howSection && "IntersectionObserver" in window) {
        var howObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    if (howProgressFill) howProgressFill.style.width = "100%";
                    stepCards.forEach(function (card, index) {
                        setTimeout(function () {
                            card.classList.add("active-step");
                        }, (index + 1) * 220);
                    });
                }
            });
        }, { threshold: 0.25 });
        howObserver.observe(howSection);
    }

    /* ===== Reveal on scroll ===== */
    var revealEls = document.querySelectorAll(".reveal");
    if ("IntersectionObserver" in window && revealEls.length) {
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("in");
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.01, rootMargin: "0px 0px 80px 0px" });
        revealEls.forEach(function (el) { io.observe(el); });

        // Immediate reveal for elements currently in or near viewport / hash target
        if (window.location.hash) {
            try {
                var hashTarget = document.querySelector(window.location.hash);
                if (hashTarget) {
                    hashTarget.classList.add("in");
                    hashTarget.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("in"); });
                }
            } catch (err) {}
        }
    } else {
        revealEls.forEach(function (el) { el.classList.add("in"); });
    }

    /* ===== Carousels (Trending Track horizontal scroll) ===== */
    document.querySelectorAll("[data-carousel-prev]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var track = document.getElementById(btn.getAttribute("data-carousel-prev"));
            if (track) track.scrollBy({ left: -340, behavior: "smooth" });
        });
    });
    document.querySelectorAll("[data-carousel-next]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var track = document.getElementById(btn.getAttribute("data-carousel-next"));
            if (track) track.scrollBy({ left: 340, behavior: "smooth" });
        });
    });

    /* ===== Toast Notification System ===== */
    var toast = document.createElement("div");
    toast.className = "liyaura-toast";
    toast.innerHTML = '<div class="toast-icon"><i class="fa-solid fa-check"></i></div><span class="toast-text"></span>';
    document.body.appendChild(toast);
    var toastTimer = null;

    window.showLiyauraToast = function (message, iconClass) {
        var textEl = toast.querySelector(".toast-text");
        var iconEl = toast.querySelector(".toast-icon i");
        if (textEl) textEl.textContent = message || "Action completed";
        if (iconEl && iconClass) iconEl.className = iconClass;
        toast.classList.add("show");
        clearTimeout(toastTimer);
        toastTimer = setTimeout(function () {
            toast.classList.remove("show");
        }, 3200);
    };

    /* ===== Product card: wishlist heart with bounce & toast ===== */
    document.querySelectorAll(".pc-wish").forEach(function (w) {
        w.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            w.classList.add("anim-bounce");
            setTimeout(function () { w.classList.remove("anim-bounce"); }, 600);

            var url = w.getAttribute("data-url");
            if (url) {
                fetch(url, { method: "GET", headers: { "X-Requested-With": "XMLHttpRequest" } })
                    .then(function () {
                        w.classList.toggle("saved");
                        var isSaved = w.classList.contains("saved");
                        window.showLiyauraToast(isSaved ? "Saved to your wishlist" : "Removed from wishlist", isSaved ? "fa-solid fa-heart" : "fa-regular fa-heart");
                    })
                    .catch(function () {
                        window.location.href = url;
                    });
            }
        });
    });



    /* ===== PDP: gallery ===== */
    window.changeImage = function (src, el) {
        var main = document.getElementById("mainImage");
        if (main) main.src = src;
        document.querySelectorAll(".pdp-thumb").forEach(function (t) { t.classList.remove("active"); });
        if (el) el.classList.add("active");
    };

    /* ===== PDP: size pills ===== */
    var sizeRow = document.getElementById("sizeRow");
    var sizeInput = document.getElementById("sizeInput");
    if (sizeRow && sizeInput) {
        sizeRow.querySelectorAll(".size-pill").forEach(function (pill) {
            pill.addEventListener("click", function () {
                sizeRow.querySelectorAll(".size-pill").forEach(function (p) { p.classList.remove("selected"); });
                pill.classList.add("selected");
                sizeInput.value = pill.getAttribute("data-size");
            });
        });
    }

    /* ===== PDP: quantity stepper ===== */
    var qtyRow = document.getElementById("qtyRow");
    var qtyValue = document.getElementById("qtyValue");
    var qtyInput = document.getElementById("qtyInput");
    if (qtyRow && qtyValue && qtyInput) {
        var maxUnits = (typeof productQty !== "undefined" && productQty > 0) ? productQty : 5;
        qtyRow.querySelectorAll("button[data-step]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var step = parseInt(btn.getAttribute("data-step"), 10) || 0;
                var val = parseInt(qtyValue.textContent, 10) || 1;
                val = Math.max(1, Math.min(maxUnits, val + step));
                qtyValue.textContent = val;
                qtyInput.value = val;
                checkAvailability();
            });
        });
    }

    /* ===== PDP: rental dates + availability ===== */
    var rentalStart = document.getElementById("rentalStart");
    var rentalDays = document.getElementById("rentalDays");
    var returnDate = document.getElementById("returnDate");
    var availNote = document.getElementById("availNote");

    function dateStr(d) {
        var y = d.getFullYear();
        var m = ("0" + (d.getMonth() + 1)).slice(-2);
        var day = ("0" + d.getDate()).slice(-2);
        return y + "-" + m + "-" + day;
    }

    window.checkAvailability = function () {
        if (!availNote) return;
        var today = new Date();
        today.setHours(0, 0, 0, 0);
        if (!rentalStart || !rentalStart.value) {
            availNote.className = "availability-note neutral";
            availNote.innerHTML = '<i class="fa-regular fa-circle-question"></i><span>Select your rental dates to check availability.</span>';
            if (returnDate) returnDate.value = "\u2014";
            return;
        }
        var start = new Date(rentalStart.value);
        start.setHours(0, 0, 0, 0);
        if (start < today) {
            availNote.className = "availability-note no";
            availNote.innerHTML = '<i class="fa-solid fa-circle-xmark"></i><span>Start date cannot be in the past.</span>';
            return;
        }
        var days = parseInt(rentalDays && rentalDays.value ? rentalDays.value : "1", 10) || 1;
        var end = new Date(start);
        end.setDate(end.getDate() + days - 1);
        var endStr = dateStr(end);
        if (returnDate) {
            returnDate.value = end.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
        }

        var qty = parseInt(qtyInput ? qtyInput.value : "1", 10) || 1;
        var total = (typeof productQty !== "undefined") ? productQty : 0;
        var ranges = (typeof bookedRanges !== "undefined") ? bookedRanges : [];
        var booked = 0;
        ranges.forEach(function (r) {
            if (r.start <= endStr && r.end >= startISO(rentalStart.value)) {
                booked += r.qty;
            }
        });

        if (total < qty) {
            availNote.className = "availability-note no";
            availNote.innerHTML = '<i class="fa-solid fa-circle-xmark"></i><span>Not enough units available. Only ' + total + ' unit(s) in stock.</span>';
            return;
        }
        if (booked + qty > total) {
            availNote.className = "availability-note no";
            availNote.innerHTML = '<i class="fa-solid fa-circle-xmark"></i><span>Unavailable for the selected dates. Try different dates.</span>';
            return;
        }
        availNote.className = "availability-note ok";
        availNote.innerHTML = '<i class="fa-solid fa-circle-check"></i><span>Available for your selected dates. ' + qty + ' unit(s) for ' + days + ' day(s).</span>';
    };

    function startISO(v) {
        var d = new Date(v);
        d.setHours(0, 0, 0, 0);
        return dateStr(d);
    }

    if (rentalStart && rentalStart.addEventListener) {
        rentalStart.addEventListener("change", checkAvailability);
        if (rentalDays) rentalDays.addEventListener("change", checkAvailability);
        var minDate = new Date();
        minDate.setHours(0, 0, 0, 0);
        rentalStart.min = dateStr(minDate);
        checkAvailability();
    }

    /* ===== To top button ===== */
    var topBtn = document.querySelector(".to-top");
    if (!topBtn) {
        topBtn = document.createElement("button");
        topBtn.className = "to-top";
        topBtn.setAttribute("aria-label", "Back to top");
        topBtn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
        document.body.appendChild(topBtn);
        topBtn.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }
    window.addEventListener("scroll", function () {
        if (topBtn) topBtn.classList.toggle("show", window.scrollY > 600);
    }, { passive: true });
});
