(() => {
    const script = document.querySelector("script[data-predict-simple-url]");
    const simplePredictUrl = script?.dataset.predictSimpleUrl;
    const batchPredictUrl = script?.dataset.predictBatchUrl;
    const sensorLatestUrl = script?.dataset.sensorLatestUrl;
    const sensorStreamUrl = script?.dataset.sensorStreamUrl;
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
    const batchPagination = document.getElementById("batch-pagination");
    const batchPrevPageBtn = document.getElementById("batch-prev-page");
    const batchNextPageBtn = document.getElementById("batch-next-page");
    const batchPageInfo = document.getElementById("batch-page-info");
    const sensorLiveEmpty = document.getElementById("sensor-live-empty");
    const sensorLiveContent = document.getElementById("sensor-live-content");
    const sensorLiveDataList = document.getElementById("sensor-live-data-list");
    const sensorLiveResult = document.getElementById("sensor-live-result");
    const sensorLiveTime = document.getElementById("sensor-live-time");

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
        !batchTableBody ||
        !batchPagination ||
        !batchPrevPageBtn ||
        !batchNextPageBtn ||
        !batchPageInfo
    ) {
        return;
    }

    const BATCH_PAGE_SIZE = 10;
    let batchResults = [];
    let batchCurrentPage = 1;

    const hasSensorModule =
        !!sensorLatestUrl &&
        !!sensorStreamUrl &&
        !!sensorLiveEmpty &&
        !!sensorLiveContent &&
        !!sensorLiveDataList &&
        !!sensorLiveResult &&
        !!sensorLiveTime;
    let lastSensorRecordId = null;

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

    const setSensorNoData = (text = "暂无数据上传") => {
        if (!hasSensorModule) return;
        sensorLiveDataList.innerHTML = "";
        sensorLiveResult.textContent = "等待分析";
        sensorLiveResult.classList.remove("ok", "warn", "error", "neutral");
        sensorLiveResult.classList.add("neutral");
        sensorLiveTime.textContent = "";
        sensorLiveContent.classList.add("hidden");
        sensorLiveEmpty.classList.remove("hidden");
        sensorLiveEmpty.classList.remove("compact");
        sensorLiveEmpty.textContent = text;
    };

    const renderSensorExample = (payload) => {
        if (!hasSensorModule) return;
        const displayData = payload.display_data || {};
        sensorLiveDataList.innerHTML = "";
        for (const [key, value] of Object.entries(displayData)) {
            const li = document.createElement("li");
            li.textContent = `${key}：${value}`;
            sensorLiveDataList.appendChild(li);
        }

        sensorLiveResult.classList.remove("ok", "warn", "error", "neutral");
        sensorLiveResult.classList.add("neutral");
        sensorLiveResult.textContent = payload.analysis_text || "示例数据";
        sensorLiveTime.textContent = "";

        sensorLiveEmpty.classList.remove("hidden");
        sensorLiveEmpty.classList.add("compact");
        sensorLiveEmpty.textContent = payload.message || "示例：";
        sensorLiveContent.classList.remove("hidden");
    };

    const renderSensorLive = (payload) => {
        if (!hasSensorModule) return;

        const displayData = payload.display_data || {};
        sensorLiveDataList.innerHTML = "";
        for (const [key, value] of Object.entries(displayData)) {
            const li = document.createElement("li");
            li.textContent = `${key}：${value}`;
            sensorLiveDataList.appendChild(li);
        }

        sensorLiveResult.classList.remove("ok", "warn", "error", "neutral");
        if (payload.analysis_result === 1) {
            sensorLiveResult.classList.add("warn");
        } else if (payload.analysis_result === 0) {
            sensorLiveResult.classList.add("ok");
        } else {
            sensorLiveResult.classList.add("neutral");
        }
        sensorLiveResult.textContent = payload.analysis_text || "暂无分析结果";
        sensorLiveTime.textContent = payload.uploaded_at ? `上传时间：${payload.uploaded_at}` : "";

        sensorLiveEmpty.classList.add("hidden");
        sensorLiveContent.classList.remove("hidden");
    };

    const refreshSensorLiveOnce = async (force = false) => {
        if (!hasSensorModule) return;

        try {
            const response = await fetch(sensorLatestUrl, { method: "GET" });
            const data = await response.json();
            if (!response.ok || !data.ok) {
                return;
            }

            if (!data.has_data) {
                lastSensorRecordId = null;
                renderSensorExample(data);
                return;
            }

            const recordId = Number(data.record_id);
            if (force || recordId !== lastSensorRecordId) {
                lastSensorRecordId = recordId;
                renderSensorLive(data);
            }
        } catch (error) {
            if (lastSensorRecordId === null) {
                setSensorNoData("暂无数据上传");
            }
        }
    };

    const connectSensorStream = () => {
        if (!hasSensorModule) return null;
        if (typeof EventSource === "undefined") return null;

        const source = new EventSource(sensorStreamUrl);

        source.addEventListener("sensor_update", (event) => {
            try {
                const payload = JSON.parse(event.data);
                if (!payload.ok) return;

                if (!payload.has_data) {
                    lastSensorRecordId = null;
                    renderSensorExample(payload);
                    return;
                }

                const currentId = Number(payload.record_id);
                if (!Number.isFinite(currentId)) return;
                if (lastSensorRecordId === null || currentId > lastSensorRecordId) {
                    lastSensorRecordId = currentId;
                    renderSensorLive(payload);
                }
            } catch (error) {
                // ignore malformed event
            }
        });

        source.addEventListener("error", () => {
            // Let EventSource auto-reconnect; no manual timer refresh.
        });

        return source;
    };

    const escapeHtml = (value) =>
        String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");

    const getBatchTotalPages = () => {
        return Math.max(1, Math.ceil(batchResults.length / BATCH_PAGE_SIZE));
    };

    const updateBatchPagination = () => {
        if (batchResults.length === 0) {
            batchPagination.classList.add("hidden");
            return;
        }

        const totalPages = getBatchTotalPages();
        batchPageInfo.textContent = `第 ${batchCurrentPage} / ${totalPages} 页（每页 ${BATCH_PAGE_SIZE} 条）`;
        batchPrevPageBtn.disabled = batchCurrentPage <= 1;
        batchNextPageBtn.disabled = batchCurrentPage >= totalPages;
        batchPagination.classList.remove("hidden");
    };

    const renderBatchTablePage = () => {
        if (batchResults.length === 0) {
            batchTableBody.innerHTML = "";
            batchTableWrapper.classList.add("hidden");
            batchPagination.classList.add("hidden");
            return;
        }

        const totalPages = getBatchTotalPages();
        if (batchCurrentPage > totalPages) {
            batchCurrentPage = totalPages;
        }

        const start = (batchCurrentPage - 1) * BATCH_PAGE_SIZE;
        const end = start + BATCH_PAGE_SIZE;
        const renderRows = batchResults.slice(start, end);
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
        updateBatchPagination();
    };

    const renderBatchTable = (rows) => {
        batchResults = Array.isArray(rows) ? rows : [];
        batchCurrentPage = 1;
        renderBatchTablePage();
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

    batchPrevPageBtn.addEventListener("click", () => {
        if (batchCurrentPage <= 1) return;
        batchCurrentPage -= 1;
        renderBatchTablePage();
    });

    batchNextPageBtn.addEventListener("click", () => {
        const totalPages = getBatchTotalPages();
        if (batchCurrentPage >= totalPages) return;
        batchCurrentPage += 1;
        renderBatchTablePage();
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

    if (hasSensorModule) {
        setSensorNoData("示例：");
        refreshSensorLiveOnce(true);
        connectSensorStream();
    }
})();
