const socket = io();
const input = document.getElementById("input");
const messages = document.getElementById("messages");

// 按 Enter 送出，Shift+Enter 則換行
input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        // event.preventDefault(); // 阻止換行
        sendData();
    }
});

// 將輸入的資料餵給 handle_submit Function
function sendData() {
    const input = document.getElementById("input");
    const text = input.value.trim();
    if (text) {
        socket.emit("submit_data", { text });
        input.value = ""; // 清空輸入欄
    }
}

// 新資料到來時，新增到列表底部
socket.on("new_data", function(data) {
    const li = document.createElement("li");
    li.className = "list-group-item";
    li.textContent = data.text;
    messages.appendChild(li);
    messages.scrollTop = messages.scrollHeight; // 自動捲到底部
});
