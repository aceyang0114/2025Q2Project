const socket = io();
const input = document.getElementById("input");
const messages = document.getElementById("messages");

input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendData();
    }
});

function sendData() {
    const text = input.value.trim();
    if (text) {
        socket.emit("submit_data", { text });
        input.value = "";
    }
}

socket.on("new_data", function(data) {
    const li = document.createElement("li");
    li.className = "list-group-item";
    li.textContent = data.text;
    messages.appendChild(li);
    messages.scrollTop = messages.scrollHeight;
});


socket.on("clear_data", function() {
    messages.innerHTML = "";  // 清空訊息區域
});

function openLoginDialog() {
    const username = prompt("請輸入帳號：");
    const password = prompt("請輸入密碼：");
    if (username && password) {
        fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // 顯示歡迎訊息
                document.getElementById("welcome").textContent = `歡迎，${data.username}`;

                // 隱藏登入按鈕
                const loginBtn = document.querySelector("button[onclick='openLoginDialog()']");
                if (loginBtn) {
                    loginBtn.style.display = "none";
                }
            }
        })
        .catch(error => console.error("登入錯誤", error));
    }
}