(() => {
    const topbarInner = document.querySelector(".topbar-inner");
    const mobileNavToggle = document.getElementById("mobile-nav-toggle");
    const topbarRightGroup = document.getElementById("topbar-right-group");

    if (!topbarInner || !mobileNavToggle || !topbarRightGroup || typeof window.matchMedia !== "function") {
        return;
    }

    const mobileMediaQuery = window.matchMedia("(max-width: 640px)");

    const closeMobileMenu = () => {
        topbarInner.classList.remove("mobile-nav-open");
        mobileNavToggle.setAttribute("aria-expanded", "false");
        mobileNavToggle.textContent = "菜单";
    };

    const syncMobileMenuState = () => {
        if (mobileMediaQuery.matches) {
            topbarInner.classList.add("mobile-nav-enabled");
            closeMobileMenu();
            return;
        }

        topbarInner.classList.remove("mobile-nav-enabled", "mobile-nav-open");
        mobileNavToggle.setAttribute("aria-expanded", "false");
        mobileNavToggle.textContent = "菜单";
    };

    syncMobileMenuState();

    if (typeof mobileMediaQuery.addEventListener === "function") {
        mobileMediaQuery.addEventListener("change", syncMobileMenuState);
    } else if (typeof mobileMediaQuery.addListener === "function") {
        mobileMediaQuery.addListener(syncMobileMenuState);
    }

    mobileNavToggle.addEventListener("click", () => {
        if (!topbarInner.classList.contains("mobile-nav-enabled")) return;
        const isOpen = topbarInner.classList.toggle("mobile-nav-open");
        mobileNavToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        mobileNavToggle.textContent = isOpen ? "收起" : "菜单";
    });

    topbarRightGroup.addEventListener("click", (event) => {
        const target = event.target;
        if (!(target instanceof HTMLElement)) return;
        if (target.closest("a")) {
            closeMobileMenu();
        }
    });

    document.addEventListener("click", (event) => {
        if (!mobileMediaQuery.matches) return;
        const target = event.target;
        if (!(target instanceof Node)) return;
        if (topbarInner.contains(target)) return;
        closeMobileMenu();
    });
})();
