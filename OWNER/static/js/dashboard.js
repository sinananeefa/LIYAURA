/**
 * LIYAURA OWNER / ADMIN DASHBOARD — INTERACTIVE CONTROLLER
 * Handles Tabs, Sidebar Collapse, Dark Mode, Drawers, Revenue Chart, and Gemini AI Generator
 */

document.addEventListener("DOMContentLoaded", function () {
    // ----------------------------------------------------
    // 1. Theme Management (Dark / Light Mode)
    // ----------------------------------------------------
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const currentTheme = localStorage.getItem("liyaura_owner_theme") || "light";
    document.documentElement.setAttribute("data-theme", currentTheme);
    updateThemeIcon(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", function () {
            const activeTheme = document.documentElement.getAttribute("data-theme") || "light";
            const newTheme = activeTheme === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("liyaura_owner_theme", newTheme);
            updateThemeIcon(newTheme);
            renderRevenueChart(); // Re-render chart with new palette
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        const icon = themeToggleBtn.querySelector("i");
        if (icon) {
            icon.className = theme === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
        }
    }

    // ----------------------------------------------------
    // 2. Sidebar Collapse & Mobile Navigation
    // ----------------------------------------------------
    const sidebar = document.getElementById("adminSidebar");
    const sidebarToggleBtn = document.getElementById("sidebarToggleBtn");
    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const drawerBackdrop = document.getElementById("globalDrawerBackdrop");

    // Remember collapsed preference
    const isCollapsed = localStorage.getItem("liyaura_sidebar_collapsed") === "true";
    if (isCollapsed && sidebar && window.innerWidth > 768) {
        sidebar.classList.add("collapsed");
    }

    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("collapsed");
            localStorage.setItem("liyaura_sidebar_collapsed", sidebar.classList.contains("collapsed"));
            renderRevenueChart();
        });
    }

    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener("click", function () {
            sidebar.classList.toggle("mobile-open");
            if (drawerBackdrop) drawerBackdrop.classList.toggle("show");
        });
    }

    // ----------------------------------------------------
    // 3. Tab Navigation & Deep Linking with Scroll Preservation
    // ----------------------------------------------------
    const navItems = document.querySelectorAll(".sidebar-nav .nav-item[data-tab]");
    const tabPanels = document.querySelectorAll(".tab-panel");

    function switchTab(tabId, updateHash = true) {
        if (!tabId) tabId = "dashboard";

        // If target is a product row, map to products tab
        let actualTab = tabId;
        let targetRowId = null;
        if (tabId.startsWith("product-row-")) {
            actualTab = "products";
            targetRowId = tabId;
        } else if (tabId === "products") {
            actualTab = "products";
        }
        
        navItems.forEach(item => {
            if (item.getAttribute("data-tab") === actualTab) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        tabPanels.forEach(panel => {
            if (panel.id === `tab-${actualTab}`) {
                panel.classList.add("active");
            } else {
                panel.classList.remove("active");
            }
        });

        // Close mobile drawer if open
        if (sidebar) sidebar.classList.remove("mobile-open");
        if (drawerBackdrop) drawerBackdrop.classList.remove("show");

        // If switching to dashboard, ensure chart renders
        if (actualTab === "dashboard") {
            setTimeout(renderRevenueChart, 100);
        }

        if (updateHash) {
            history.replaceState(null, null, `#${tabId}`);
        }

        // If there is a target product row, scroll smoothly to it
        if (targetRowId) {
            setTimeout(() => {
                const targetRow = document.getElementById(targetRowId);
                if (targetRow) {
                    targetRow.scrollIntoView({ behavior: "smooth", block: "center" });
                    targetRow.classList.add("row-highlight-pulse");
                    setTimeout(() => targetRow.classList.remove("row-highlight-pulse"), 3500);
                }
            }, 120);
        }
    }

    navItems.forEach(item => {
        item.addEventListener("click", function () {
            const tab = this.getAttribute("data-tab");
            switchTab(tab);
        });
    });

    // Handle Quick Action buttons linking to tabs
    document.querySelectorAll("[data-action-tab]").forEach(btn => {
        btn.addEventListener("click", function () {
            const targetTab = this.getAttribute("data-action-tab");
            switchTab(targetTab);
        });
    });

    // Check initial URL hash & saved scroll position
    const initialHash = window.location.hash.replace("#", "");
    const savedScrollPos = sessionStorage.getItem("owner_scroll_pos");
    const savedLastEditedId = sessionStorage.getItem("owner_last_edited_id");

    if (initialHash) {
        switchTab(initialHash, false);
    } else if (savedLastEditedId) {
        switchTab(`product-row-${savedLastEditedId}`, false);
        sessionStorage.removeItem("owner_last_edited_id");
    } else if (savedScrollPos) {
        switchTab("products", false);
        setTimeout(() => {
            window.scrollTo({ top: parseInt(savedScrollPos, 10), behavior: "smooth" });
            sessionStorage.removeItem("owner_scroll_pos");
        }, 100);
    } else {
        switchTab("dashboard", false);
    }

    // ----------------------------------------------------
    // 4. Staggered Stat Cards Count-Up Animation
    // ----------------------------------------------------
    const statValues = document.querySelectorAll(".stat-value[data-count]");
    statValues.forEach(el => {
        const rawCount = el.getAttribute("data-count") || "";
        const target = parseFloat(rawCount.replace(/,/g, "")) || 0;
        const prefix = el.getAttribute("data-prefix") || "";
        let current = 0;
        const duration = 1200;
        const stepTime = 25;
        const steps = duration / stepTime;
        const increment = target / steps;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            if (prefix === "₹") {
                el.innerText = `₹${Math.round(current).toLocaleString("en-IN")}`;
            } else {
                el.innerText = `${Math.round(current).toLocaleString("en-IN")}`;
            }
        }, stepTime);
    });

    // ----------------------------------------------------
    // 5. Interactive Revenue Canvas Chart
    // ----------------------------------------------------
    const chartCanvas = document.getElementById("revenueChartCanvas");
    let currentChartData = {
        labels: ["Day 1", "Day 4", "Day 7", "Day 10", "Day 13", "Day 16", "Day 19", "Day 22", "Day 25", "Day 28"],
        revenue: [22000, 34000, 48000, 41000, 58000, 72000, 64000, 89000, 95000, 112000],
        orders: [4, 6, 8, 7, 10, 12, 11, 15, 16, 19],
    };

    function renderRevenueChart() {
        if (!chartCanvas) return;
        const ctx = chartCanvas.getContext("2d");
        const width = chartCanvas.parentElement.clientWidth;
        const height = 240;
        chartCanvas.width = width * window.devicePixelRatio;
        chartCanvas.height = height * window.devicePixelRatio;
        chartCanvas.style.width = `${width}px`;
        chartCanvas.style.height = `${height}px`;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        const data = currentChartData.revenue;
        const labels = currentChartData.labels;
        const maxVal = Math.max(...data) * 1.15 || 100000;
        const padding = { top: 20, right: 20, bottom: 40, left: 20 };
        const chartW = width - padding.left - padding.right;
        const chartH = height - padding.top - padding.bottom;

        ctx.clearRect(0, 0, width, height);

        // Draw grid lines
        const isDark = document.documentElement.getAttribute("data-theme") === "dark";
        ctx.strokeStyle = isDark ? "rgba(255,255,255,0.06)" : "rgba(33,28,24,0.06)";
        ctx.lineWidth = 1;

        for (let i = 0; i <= 4; i++) {
            const y = padding.top + (chartH / 4) * i;
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(width - padding.right, y);
            ctx.stroke();
        }

        // Draw smooth line
        const points = [];
        const step = chartW / (data.length - 1 || 1);

        for (let i = 0; i < data.length; i++) {
            const x = padding.left + i * step;
            const y = padding.top + chartH - (data[i] / maxVal) * chartH;
            points.push({ x, y, val: data[i], label: labels[i] });
        }

        if (points.length > 1) {
            // Area Gradient Fill
            const grad = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartH);
            grad.addColorStop(0, isDark ? "rgba(201, 169, 106, 0.35)" : "rgba(185, 151, 91, 0.3)");
            grad.addColorStop(1, isDark ? "rgba(201, 169, 106, 0.0)" : "rgba(185, 151, 91, 0.0)");

            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 0; i < points.length - 1; i++) {
                const xc = (points[i].x + points[i + 1].x) / 2;
                const yc = (points[i].y + points[i + 1].y) / 2;
                ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc);
            }
            ctx.lineTo(points[points.length - 1].x, points[points.length - 1].y);
            ctx.lineTo(points[points.length - 1].x, padding.top + chartH);
            ctx.lineTo(points[0].x, padding.top + chartH);
            ctx.closePath();
            ctx.fillStyle = grad;
            ctx.fill();

            // Line Stroke
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 0; i < points.length - 1; i++) {
                const xc = (points[i].x + points[i + 1].x) / 2;
                const yc = (points[i].y + points[i + 1].y) / 2;
                ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc);
            }
            ctx.lineTo(points[points.length - 1].x, points[points.length - 1].y);
            ctx.strokeStyle = isDark ? "#C9A96A" : "#B9975B";
            ctx.lineWidth = 3;
            ctx.stroke();

            // Draw points
            points.forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, 4.5, 0, Math.PI * 2);
                ctx.fillStyle = isDark ? "#211C18" : "#FFFFFF";
                ctx.fill();
                ctx.strokeStyle = isDark ? "#C9A96A" : "#B9975B";
                ctx.lineWidth = 2.5;
                ctx.stroke();
            });
        }

        // Draw Labels
        ctx.fillStyle = isDark ? "#A3998C" : "#8D847A";
        ctx.font = "11px 'Plus Jakarta Sans', sans-serif";
        ctx.textAlign = "center";
        points.forEach((p, idx) => {
            if (points.length > 8 && idx % 2 !== 0) return; // Skip alternate on small widths
            ctx.fillText(p.label, p.x, height - 12);
        });
    }

    // Chart period filter clicks
    document.querySelectorAll(".period-pill").forEach(pill => {
        pill.addEventListener("click", function () {
            document.querySelectorAll(".period-pill").forEach(p => p.classList.remove("active"));
            this.classList.add("active");
            const period = this.getAttribute("data-period");

            fetch(`/owner/api/chart-data/?period=${period}`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        currentChartData = data;
                        renderRevenueChart();
                    }
                })
                .catch(() => renderRevenueChart());
        });
    });

    window.addEventListener("resize", renderRevenueChart);
    setTimeout(renderRevenueChart, 200);

    // ----------------------------------------------------
    // 6. Drawers System (Booking, Customer, Product, Notifications)
    // ----------------------------------------------------
    const bookingDrawer = document.getElementById("bookingDetailDrawer");
    const customerDrawer = document.getElementById("customerDetailDrawer");
    const productDrawer = document.getElementById("productDrawer");
    const notificationDrawer = document.getElementById("notificationDrawer");
    const geminiModal = document.getElementById("geminiGeneratorModal");

    window.closeAllDrawers = function () {
        document.querySelectorAll(".drawer").forEach(d => d.classList.remove("show"));
        if (geminiModal) geminiModal.classList.remove("show");
        if (drawerBackdrop) drawerBackdrop.classList.remove("show");
    };

    if (drawerBackdrop) {
        drawerBackdrop.addEventListener("click", window.closeAllDrawers);
    }

    document.querySelectorAll(".drawer-close-btn, [data-close-drawer]").forEach(btn => {
        btn.addEventListener("click", window.closeAllDrawers);
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") window.closeAllDrawers();
    });

    // --- Booking Drawer Trigger ---
    window.openBookingDrawer = function (bookingId) {
        if (!bookingDrawer) return;
        
        fetch(`/owner/api/booking/${bookingId}/details/`)
            .then(res => res.json())
            .then(b => {
                const elId = document.getElementById("bd_id"); if (elId) elId.innerText = `#${b.id}`;
                const elCName = document.getElementById("bd_customer_name"); if (elCName) elCName.innerText = b.customer_name;
                const elCEmail = document.getElementById("bd_customer_email"); if (elCEmail) elCEmail.innerText = b.customer_email;
                const elCPhone = document.getElementById("bd_customer_phone"); if (elCPhone) elCPhone.innerText = b.customer_phone;
                const elPName = document.getElementById("bd_product_name"); if (elPName) elPName.innerText = b.product_name;
                const elPImg = document.getElementById("bd_product_img"); if (elPImg) elPImg.src = b.product_image;
                const elCat = document.getElementById("bd_category"); if (elCat) elCat.innerText = b.category;
                const elOcc = document.getElementById("bd_occasion"); if (elOcc) elOcc.innerText = b.occasion;
                const elDates = document.getElementById("bd_dates"); if (elDates) elDates.innerText = `${b.rental_start} → ${b.rental_end} (${b.rental_days} days)`;
                const elAmt = document.getElementById("bd_amount"); if (elAmt) elAmt.innerText = `₹${parseFloat(b.amount).toLocaleString('en-IN')}`;
                const elPay = document.getElementById("bd_payment"); if (elPay) elPay.innerText = b.payment_method;
                const elAddr = document.getElementById("bd_address"); if (elAddr) elAddr.innerText = b.address;
                
                const statusSelect = document.getElementById("bd_status_select");
                if (statusSelect) {
                    statusSelect.value = b.status;
                    statusSelect.onchange = function () {
                        updateBookingStatus(b.id, this.value);
                    };
                }

                bookingDrawer.classList.add("show");
                if (drawerBackdrop) drawerBackdrop.classList.add("show");
            });
    };

    function updateBookingStatus(bookingId, newStatus) {
        const formData = new FormData();
        formData.append("status", newStatus);
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

        fetch(`/owner/api/booking/${bookingId}/update-status/`, {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken },
            body: formData,
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                // Update table row badge if visible
                const badge = document.getElementById(`booking-badge-${bookingId}`);
                if (badge) {
                    badge.className = `status-badge badge-${getStatusBadgeClass(newStatus)}`;
                    badge.innerText = data.display_status;
                }
            }
        });
    }

    function getStatusBadgeClass(status) {
        switch (status) {
            case "confirmed":
            case "completed": return "success";
            case "out_for_delivery":
            case "preparing": return "info";
            case "delivered":
            case "rented": return "gold";
            case "cancelled": return "danger";
            default: return "warning";
        }
    }

    // --- Customer Drawer Trigger ---
    window.openCustomerDrawer = function (userId) {
        if (!customerDrawer) return;
        fetch(`/owner/api/customer/${userId}/details/`)
            .then(res => res.json())
            .then(c => {
                document.getElementById("cd_name").innerText = c.username;
                document.getElementById("cd_email").innerText = c.email;
                document.getElementById("cd_phone").innerText = c.phone;
                document.getElementById("cd_bookings_count").innerText = c.total_bookings;
                document.getElementById("cd_total_spent").innerText = `₹${c.total_spent}`;
                
                const list = document.getElementById("cd_bookings_list");
                list.innerHTML = "";
                if (c.bookings && c.bookings.length > 0) {
                    c.bookings.forEach(b => {
                        list.innerHTML += `
                            <div style="display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid var(--line-border-subtle);">
                                <img src="${b.product_image}" style="width:40px; height:48px; border-radius:6px; object-fit:cover;">
                                <div style="flex:1;">
                                    <div style="font-weight:600; font-size:13px; color:var(--text-dark);">${b.product_name}</div>
                                    <div style="font-size:11.5px; color:var(--text-muted);">${b.date} &middot; ₹${b.amount}</div>
                                </div>
                                <span class="status-badge badge-${getStatusBadgeClass(b.status)}">${b.status_display}</span>
                            </div>
                        `;
                    });
                } else {
                    list.innerHTML = `<p style="color:var(--text-muted); font-size:13px;">No rental orders yet.</p>`;
                }

                customerDrawer.classList.add("show");
                if (drawerBackdrop) drawerBackdrop.classList.add("show");
            });
    };

    // --- Notification Drawer ---
    const notificationBtn = document.getElementById("notificationBtn");
    if (notificationBtn && notificationDrawer) {
        notificationBtn.addEventListener("click", function () {
            notificationDrawer.classList.add("show");
            if (drawerBackdrop) drawerBackdrop.classList.add("show");
        });
    }

    // --- Product Drawer ---
    window.openAddProductDrawer = function () {
        if (!productDrawer) return;
        document.getElementById("productForm").reset();
        document.getElementById("productDrawerTitle").innerText = "Add New Outfit";
        document.getElementById("productForm").action = "/owner/product/add/";
        document.getElementById("ai_preview_box").style.display = "none";
        productDrawer.classList.add("show");
        if (drawerBackdrop) drawerBackdrop.classList.add("show");
    };

    window.openEditProductDrawer = function (pData) {
        if (!productDrawer) return;
        sessionStorage.setItem("owner_scroll_pos", window.scrollY);
        sessionStorage.setItem("owner_last_edited_id", pData.id);
        document.getElementById("productDrawerTitle").innerText = `Edit: ${pData.name}`;
        document.getElementById("productForm").action = `/owner/product/edit/${pData.id}/`;
        document.getElementById("pf_name").value = pData.name;
        document.getElementById("pf_actual_price").value = pData.actual_price;
        document.getElementById("pf_offer_price").value = pData.offer_price;
        document.getElementById("pf_quantity").value = pData.quantity;
        document.getElementById("pf_description").value = pData.description;
        document.getElementById("pf_category_1").value = pData.category_1_id;
        document.getElementById("pf_category_2").value = pData.category_2_id;
        const sectionEl = document.getElementById("pf_section");
        if (sectionEl) sectionEl.value = pData.section_id || "";
        productDrawer.classList.add("show");
        if (drawerBackdrop) drawerBackdrop.classList.add("show");
    };

    const productForm = document.getElementById("productForm");
    if (productForm) {
        productForm.addEventListener("submit", function () {
            sessionStorage.setItem("owner_scroll_pos", window.scrollY);
        });
    }

    // --- Category Drawer ---
    const categoryEditDrawer = document.getElementById("categoryEditDrawer");
    window.openEditCategoryDrawer = function (cData) {
        if (!categoryEditDrawer) return;
        document.getElementById("catEditDrawerTitle").innerText = `Edit: ${cData.name}`;
        document.getElementById("catEditForm").action = `/owner/category-2/edit/${cData.id}/`;
        document.getElementById("cat_edit_name").value = cData.name;
        document.getElementById("cat_edit_category_1").value = cData.category_1_id;
        document.getElementById("cat_edit_gender_type").value = cData.gender_type;
        const preview = document.getElementById("cat_edit_img_preview");
        if (preview) {
            preview.src = cData.image || "/static/images/bride-vertical.png";
        }
        categoryEditDrawer.classList.add("show");
        if (drawerBackdrop) drawerBackdrop.classList.add("show");
    };

    // --- Occasion Drawer ---
    const occasionEditDrawer = document.getElementById("occasionEditDrawer");
    window.openEditOccasionDrawer = function (oData) {
        if (!occasionEditDrawer) return;
        document.getElementById("occEditDrawerTitle").innerText = `Edit: ${oData.name}`;
        document.getElementById("occEditForm").action = `/owner/category-1/edit/${oData.id}/`;
        document.getElementById("occ_edit_name").value = oData.name;
        document.getElementById("occ_edit_gender_type").value = oData.gender_type;
        const preview = document.getElementById("occ_edit_img_preview");
        if (preview) {
            preview.src = oData.image || "/static/images/hero-couple.jpg";
        }
        occasionEditDrawer.classList.add("show");
        if (drawerBackdrop) drawerBackdrop.classList.add("show");
    };

    // --- Section Drawer ---
    const sectionEditDrawer = document.getElementById("sectionEditDrawer");
    window.openEditSectionDrawer = function (sData) {
        if (!sectionEditDrawer) return;
        document.getElementById("secEditDrawerTitle").innerText = `Edit Section: ${sData.name}`;
        document.getElementById("secEditForm").action = `/owner/rack/edit/${sData.id}/`;
        document.getElementById("sec_edit_name").value = sData.name;
        document.getElementById("sec_edit_rack_no").value = sData.rack_no;
        sectionEditDrawer.classList.add("show");
        if (drawerBackdrop) drawerBackdrop.classList.add("show");
    };

    window.previewDrawerImage = function (input, previewId) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const preview = document.getElementById(previewId);
                if (preview) preview.src = e.target.result;
            };
            reader.readAsDataURL(input.files[0]);
        }
    };

    // ----------------------------------------------------
    // 7. Gemini AI Fashion Image Generation Assistant (Slots 1, 2, 3)
    // ----------------------------------------------------
    const generateGeminiBtn = document.getElementById("generateGeminiBtn");
    const apiKeyInput = document.getElementById("gemini_api_key_input");
    const apiKeySavedBadge = document.getElementById("apiKeySavedBadge");
    const aiAlertBox = document.getElementById("ai_alert_box");
    let lastGeneratedImageUrl = "";

    // Load saved API Key from localStorage
    if (apiKeyInput) {
        const savedKey = localStorage.getItem("gemini_api_key");
        if (savedKey) {
            apiKeyInput.value = savedKey;
            if (apiKeySavedBadge) apiKeySavedBadge.style.display = "inline";
        }

        apiKeyInput.addEventListener("input", function () {
            const val = this.value.trim();
            if (val) {
                localStorage.setItem("gemini_api_key", val);
                if (apiKeySavedBadge) apiKeySavedBadge.style.display = "inline";
                if (aiAlertBox) aiAlertBox.style.display = "none";
            } else {
                localStorage.removeItem("gemini_api_key");
                if (apiKeySavedBadge) apiKeySavedBadge.style.display = "none";
            }
        });
    }

    if (generateGeminiBtn) {
        generateGeminiBtn.addEventListener("click", function () {
            const name = document.getElementById("pf_name")?.value || "Bridal Outfit";
            const catSelect = document.getElementById("pf_category_2");
            const category = catSelect?.options[catSelect.selectedIndex]?.text || "Lehenga";
            const occSelect = document.getElementById("pf_category_1");
            const occasion = occSelect?.options[occSelect.selectedIndex]?.text || "Wedding";
            const color = document.getElementById("pf_color_prompt")?.value || "";
            const desc = document.getElementById("pf_description")?.value || "";
            const apiKey = apiKeyInput ? apiKeyInput.value.trim() : (localStorage.getItem("gemini_api_key") || "");

            if (!apiKey) {
                if (aiAlertBox) {
                    aiAlertBox.style.display = "block";
                    aiAlertBox.style.background = "rgba(211, 47, 47, 0.1)";
                    aiAlertBox.style.border = "1px solid rgba(211, 47, 47, 0.3)";
                    aiAlertBox.style.color = "#C62828";
                    aiAlertBox.innerHTML = `<i class="fa-solid fa-key"></i> <strong>API Key Required:</strong> Please paste your Google Gemini API Key in the field above to generate fresh AI imagery.`;
                }
                if (apiKeyInput) {
                    apiKeyInput.focus();
                    apiKeyInput.style.borderColor = "#C62828";
                }
                return;
            }

            if (aiAlertBox) {
                aiAlertBox.style.display = "none";
            }

            this.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Generating with Google Gemini...`;
            this.disabled = true;

            const formData = new FormData();
            formData.append("name", name);
            formData.append("category", category);
            formData.append("occasion", occasion);
            formData.append("color", color);
            formData.append("description", desc);
            formData.append("gemini_api_key", apiKey);
            const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";

            fetch("/owner/api/generate-gemini-image/", {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken },
                body: formData,
            })
            .then(res => res.json())
            .then(data => {
                this.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Generate with Gemini`;
                this.disabled = false;

                if (data.status === "success") {
                    lastGeneratedImageUrl = data.generated_image_url;
                    const previewBox = document.getElementById("ai_preview_box");
                    const previewImg = document.getElementById("ai_preview_img");
                    
                    if (previewBox && previewImg) {
                        const cleanUrl = data.generated_image_url.split("?")[0] + `?t=${Date.now()}`;
                        previewImg.onerror = function() {
                            this.src = data.generated_image_url;
                        };
                        previewImg.src = cleanUrl;
                        previewBox.style.display = "block";
                    }

                    if (aiAlertBox) {
                        aiAlertBox.style.display = "block";
                        aiAlertBox.style.background = "rgba(46, 125, 50, 0.1)";
                        aiAlertBox.style.border = "1px solid rgba(46, 125, 50, 0.3)";
                        aiAlertBox.style.color = "#2E7D32";
                        aiAlertBox.innerHTML = `✓ ${data.message || "Fresh AI visual generated successfully!"}`;
                    }

                    // Auto-assign to slot 1
                    assignToSlot(1, data.generated_image_url);
                } else {
                    if (aiAlertBox) {
                        aiAlertBox.style.display = "block";
                        aiAlertBox.style.background = "rgba(211, 47, 47, 0.1)";
                        aiAlertBox.style.border = "1px solid rgba(211, 47, 47, 0.3)";
                        aiAlertBox.style.color = "#C62828";
                        aiAlertBox.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> ${data.message || "Could not generate image. Please check API Key or quota."}`;
                    }
                }
            })
            .catch(err => {
                this.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Generate with Gemini`;
                this.disabled = false;
                if (aiAlertBox) {
                    aiAlertBox.style.display = "block";
                    aiAlertBox.style.background = "rgba(211, 47, 47, 0.1)";
                    aiAlertBox.style.border = "1px solid rgba(211, 47, 47, 0.3)";
                    aiAlertBox.style.color = "#C62828";
                    aiAlertBox.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> Network error generating image: ${err}`;
                }
            });
        });
    }

    function assignToSlot(slotNum, imageUrl) {
        const preview = document.getElementById(`slot${slotNum}_preview`);
        const status = document.getElementById(`slot${slotNum}_status`);
        const hiddenInput = document.getElementById(`ai_generated_image_${slotNum}_val`);

        if (preview && hiddenInput) {
            const cleanUrl = imageUrl.split("?")[0] + `?t=${Date.now()}`;
            preview.onerror = function() {
                this.src = imageUrl;
            };
            preview.src = cleanUrl;
            preview.style.opacity = "1";
            preview.style.border = "1.5px solid var(--gold-primary)";
            hiddenInput.value = imageUrl.split("?")[0];
        }
        if (status) {
            status.innerHTML = `<span style="color:#2E7D32; font-weight:700;">✓ AI Image ${slotNum} Set</span>`;
        }
    }

    document.getElementById("setSlot1Btn")?.addEventListener("click", function () {
        if (lastGeneratedImageUrl) assignToSlot(1, lastGeneratedImageUrl);
    });

    document.getElementById("setSlot2Btn")?.addEventListener("click", function () {
        if (lastGeneratedImageUrl) assignToSlot(2, lastGeneratedImageUrl);
    });

    document.getElementById("setSlot3Btn")?.addEventListener("click", function () {
        if (lastGeneratedImageUrl) assignToSlot(3, lastGeneratedImageUrl);
    });

    document.getElementById("setAllSlotsBtn")?.addEventListener("click", function () {
        if (lastGeneratedImageUrl) {
            assignToSlot(1, lastGeneratedImageUrl);
            assignToSlot(2, lastGeneratedImageUrl);
            assignToSlot(3, lastGeneratedImageUrl);
        }
    });

    // Handle Local File Upload Previews
    [1, 2, 3].forEach(slot => {
        const fileInput = document.getElementById(`file_slot${slot}`);
        const preview = document.getElementById(`slot${slot}_preview`);
        const status = document.getElementById(`slot${slot}_status`);

        if (fileInput && preview) {
            fileInput.addEventListener("change", function () {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        preview.src = e.target.result;
                        preview.style.opacity = "1";
                        preview.style.border = "1.5px solid var(--gold-primary)";
                        if (status) status.innerHTML = `<span style="color:#2E7D32; font-weight:700;">✓ Local File Attached</span>`;
                    };
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
    });

    // ----------------------------------------------------
    // 8. Global Search Filter
    // ----------------------------------------------------
    const globalSearchInput = document.getElementById("globalSearchInput");
    if (globalSearchInput) {
        globalSearchInput.addEventListener("input", function () {
            const query = this.value.toLowerCase().trim();
            document.querySelectorAll(".searchable-row, .searchable-card").forEach(el => {
                const text = el.innerText.toLowerCase();
                if (text.includes(query)) {
                    el.style.display = "";
                } else {
                    el.style.display = "none";
                }
            });
        });
    }
});