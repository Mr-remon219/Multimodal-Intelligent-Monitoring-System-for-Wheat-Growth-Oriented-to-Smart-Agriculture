(() => {
    const script = document.querySelector("script[data-predict-url]");
    const predictUrl = script?.dataset.predictUrl;
    if (!predictUrl) return;

    const openBtn = document.getElementById("open-simple-modal");
    const closeBtn = document.getElementById("close-simple-modal");
    const cancelBtn = document.getElementById("cancel-simple-submit");
    const modal = document.getElementById("simple-modal");
    const form = document.getElementById("simple-form");
    const resultPanel = document.getElementById("simple-result");
    const formMessage = document.getElementById("simple-form-message");
    const submitBtn = document.getElementById("submit-simple-form");
    const requestPreview = document.getElementById("request-preview");

    if (
        !openBtn ||
        !closeBtn ||
        !cancelBtn ||
        !modal ||
        !form ||
        !resultPanel ||
        !formMessage ||
        !submitBtn ||
        !requestPreview
    ) {
        return;
    }

    const setResult = (text, state) => {
        resultPanel.textContent = text;
        resultPanel.classList.remove("ok", "warn", "neutral", "error");
        resultPanel.classList.add(state);
    };

    const setFormMessage = (text, state) => {
        formMessage.textContent = text || "";
        formMessage.classList.remove("show", "error");
        if (text) {
            formMessage.classList.add("show");
            if (state === "error") {
                formMessage.classList.add("error");
            }
        }
    };

    const openModal = () => {
        modal.classList.remove("hidden");
        modal.setAttribute("aria-hidden", "false");
    };

    const closeModal = () => {
        modal.classList.add("hidden");
        modal.setAttribute("aria-hidden", "true");
        setFormMessage("", "");
    };

    const getCookie = (name) => {
        const cookies = document.cookie ? document.cookie.split(";") : [];
        for (const cookieRaw of cookies) {
            const cookie = cookieRaw.trim();
            if (cookie.startsWith(`${name}=`)) {
                return decodeURIComponent(cookie.slice(name.length + 1));
            }
        }
        return "";
    };

    const getCsrfToken = () => {
        const tokenFromCookie = getCookie("csrftoken");
        if (tokenFromCookie) return tokenFromCookie;
        const tokenFromMeta = document.querySelector("meta[name='csrf-token']")?.getAttribute("content");
        return tokenFromMeta || "";
    };

    const parseStrictFloat = (value) => {
        if (typeof value !== "string" || value.trim() === "") return null;
        const num = Number(value);
        if (!Number.isFinite(num)) return null;
        return num;
    };

    openBtn.addEventListener("click", openModal);
    closeBtn.addEventListener("click", closeModal);
    cancelBtn.addEventListener("click", closeModal);

    modal.addEventListener("click", (event) => {
        const target = event.target;
        if (target instanceof HTMLElement && target.dataset.closeModal === "true") {
            closeModal();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !modal.classList.contains("hidden")) {
            closeModal();
        }
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        setFormMessage("", "");

        const formData = new FormData(form);
        const payload = {
            soil_type: String(formData.get("soil_type") || "").trim(),
            seedling_stage: String(formData.get("seedling_stage") || "").trim(),
            MOI: parseStrictFloat(String(formData.get("MOI") || "")),
            temp: parseStrictFloat(String(formData.get("temp") || "")),
            humidity: parseStrictFloat(String(formData.get("humidity") || "")),
        };

        if (!payload.soil_type || !payload.seedling_stage) {
            setFormMessage("请选择土壤和生长周期。", "error");
            return;
        }

        if (payload.MOI === null || payload.temp === null || payload.humidity === null) {
            setFormMessage("MOI、temp、humidity 必须是 float 数值。", "error");
            return;
        }

        requestPreview.textContent = JSON.stringify(payload, null, 2);

        submitBtn.disabled = true;
        submitBtn.textContent = "预测中...";

        try {
            const response = await fetch(predictUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            if (!response.ok || !data.ok) {
                setFormMessage(data.message || "预测失败，请稍后重试。", "error");
                setResult("预测失败，请检查参数或稍后重试。", "error");
                return;
            }

            if (data.result === 1) {
                setResult("预测结果：需要灌溉", "warn");
            } else {
                setResult("预测结果：一切正常", "ok");
            }

            closeModal();
            form.reset();
        } catch (error) {
            setFormMessage("网络异常，请稍后重试。", "error");
            setResult("请求失败，请检查网络连接。", "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "提交预测";
        }
    });
})();
