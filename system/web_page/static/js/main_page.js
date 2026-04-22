(() => {
    const script = document.querySelector("script[data-predict-simple-url]");
    const simplePredictUrl = script?.dataset.predictSimpleUrl;
    const batchPredictUrl = script?.dataset.predictBatchUrl;
    if (!simplePredictUrl) return;

    const openBtn = document.getElementById("open-simple-modal");
    const closeBtn = document.getElementById("close-simple-modal");
    const cancelBtn = document.getElementById("cancel-simple-submit");
    const modal = document.getElementById("simple-modal");
    const form = document.getElementById("simple-form");
    const resultPanel = document.getElementById("simple-result");
    const formMessage = document.getElementById("simple-form-message");
    const submitBtn = document.getElementById("submit-simple-form");
    const requestPreview = document.getElementById("request-preview");
    const batchInput = document.getElementById("batch-csv-input");
    const batchSubmitBtn = document.getElementById("submit-batch");
    const batchSummary = document.getElementById("batch-summary");
    const batchErrorBox = document.getElementById("batch-error-box");
    const batchTableWrapper = document.getElementById("batch-table-wrapper");
    const batchTableBody = document.getElementById("batch-table-body");

    if (
        !openBtn ||
        !closeBtn ||
        !cancelBtn ||
        !modal ||
        !form ||
        !resultPanel ||
        !formMessage ||
        !submitBtn ||
        !requestPreview ||
        !batchInput ||
        !batchSubmitBtn ||
        !batchSummary ||
        !batchErrorBox ||
        !batchTableWrapper ||
        !batchTableBody
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

    const setBatchSummary = (text, state) => {
        batchSummary.textContent = text;
        batchSummary.classList.remove("ok", "warn", "neutral", "error");
        batchSummary.classList.add(state);
    };

    const setBatchErrors = (errors) => {
        if (!Array.isArray(errors) || errors.length === 0) {
            batchErrorBox.classList.remove("show");
            batchErrorBox.textContent = "";
            return;
        }

        const previewErrors = errors.slice(0, 10);
        const text = previewErrors
            .map((item) => `第 ${item.row} 行：${item.message}`)
            .join("\n");
        const more = errors.length > previewErrors.length ? `\n... 另外 ${errors.length - previewErrors.length} 条错误` : "";
        batchErrorBox.textContent = `${text}${more}`;
        batchErrorBox.classList.add("show");
    };

    const escapeHtml = (value) =>
        String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");

    const renderBatchTable = (rows) => {
        if (!Array.isArray(rows) || rows.length === 0) {
            batchTableBody.innerHTML = "";
            batchTableWrapper.classList.add("hidden");
            return;
        }

        const maxRenderRows = 500;
        const renderRows = rows.slice(0, maxRenderRows);
        const html = renderRows
            .map((item) => {
                const tagClass = item.result === 1 ? "warn" : "ok";
                return `
                    <tr>
                        <td>${escapeHtml(item.row)}</td>
                        <td>${escapeHtml(item.soil_type)}</td>
                        <td>${escapeHtml(item.seedling_stage)}</td>
                        <td>${escapeHtml(item.MOI)}</td>
                        <td>${escapeHtml(item.temp)}</td>
                        <td>${escapeHtml(item.humidity)}</td>
                        <td><span class="result-tag ${tagClass}">${escapeHtml(item.result_text)}</span></td>
                    </tr>
                `;
            })
            .join("");

        batchTableBody.innerHTML = html;
        batchTableWrapper.classList.remove("hidden");
        if (rows.length > maxRenderRows) {
            batchErrorBox.textContent = `结果行较多，仅展示前 ${maxRenderRows} 条，完整统计已在汇总中给出。`;
            batchErrorBox.classList.add("show");
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
            const response = await fetch(simplePredictUrl, {
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

    if (batchPredictUrl) {
        batchSubmitBtn.addEventListener("click", async () => {
            const file = batchInput.files?.[0];
            if (!file) {
                setBatchSummary("请先选择 CSV 文件。", "error");
                return;
            }

            setBatchErrors([]);
            renderBatchTable([]);
            batchSubmitBtn.disabled = true;
            batchSubmitBtn.textContent = "处理中...";

            try {
                const formData = new FormData();
                formData.append("csv_file", file);

                const response = await fetch(batchPredictUrl, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: formData,
                });

                let data = {};
                try {
                    data = await response.json();
                } catch (error) {
                    data = {};
                }

                if (!response.ok || !data.ok) {
                    setBatchSummary(data.message || "批量预测失败，请稍后重试。", "error");
                    setBatchErrors(data.errors || []);
                    return;
                }

                const summary = data.summary || {};
                const summaryText =
                    `批量预测完成：总计 ${summary.total_rows ?? "-"} 行，` +
                    `有效 ${summary.valid_rows ?? "-"} 行，` +
                    `错误 ${summary.error_rows ?? "-"} 行，` +
                    `需要灌溉 ${summary.need_irrigation ?? "-"} 行，` +
                    `一切正常 ${summary.normal ?? "-"} 行。`;
                setBatchSummary(summaryText, "ok");
                setBatchErrors(data.errors || []);
                renderBatchTable(data.results || []);
            } catch (error) {
                setBatchSummary("网络异常，请稍后重试。", "error");
            } finally {
                batchSubmitBtn.disabled = false;
                batchSubmitBtn.textContent = "上传并预测";
            }
        });
    }
})();
