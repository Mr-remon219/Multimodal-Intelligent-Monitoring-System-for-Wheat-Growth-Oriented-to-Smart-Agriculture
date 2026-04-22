(() => {
    const script = document.currentScript;
    if (!script) return;

    const apiUrl = script.dataset.apiUrl;
    const loginUrl = script.dataset.loginUrl;
    const form = document.getElementById("register-form");
    const messageEl = document.getElementById("register-message");
    const submitButton = document.getElementById("register-submit");
    const csrfInput = form?.querySelector("input[name='csrfmiddlewaretoken']");

    if (!form || !messageEl || !submitButton || !csrfInput || !apiUrl || !loginUrl) return;

    const setMessage = (text, type) => {
        messageEl.textContent = text;
        messageEl.classList.remove("error", "success", "show");
        if (type) {
            messageEl.classList.add(type, "show");
        }
    };

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = form.username.value.trim();
        const password = form.password.value;
        const confirmPassword = form.confirm_password.value;

        if (!username || !password || !confirmPassword) {
            setMessage("请完整填写用户名和密码。", "error");
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = "提交中...";
        setMessage("", "");

        try {
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfInput.value,
                },
                body: JSON.stringify({
                    username,
                    password,
                    confirm_password: confirmPassword,
                }),
            });

            const data = await response.json();
            if (!response.ok || !data.ok) {
                setMessage(data.message || "注册失败，请稍后重试。", "error");
                return;
            }

            setMessage(data.message || "注册成功，即将跳转登录页。", "success");
            setTimeout(() => {
                window.location.href = loginUrl;
            }, 900);
        } catch (error) {
            setMessage("网络异常，请稍后重试。", "error");
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = "注册";
        }
    });
})();
