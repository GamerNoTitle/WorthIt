function changeNavigation(element) {
    elements = ['nav-my-items', 'nav-login-logout']
    for (let i = 0; i < elements.length; i++) {
        document.getElementById(elements[i]).removeAttribute('checked');
    }
    element.setAttribute('checked', 'true');
}

function openGithubRepo() {
    window.open('https://github.com/GamerNoTitle/WorthIt', '_blank');
}

function openAboutDialog() {
    const dialog = document.getElementById('nav-about-dialog');
    dialog.setAttribute('showed', 'true');
}

function openLoginLogoutDialog(element) {
    if (element.getAttribute('mode') === 'login') {
        const dialog = document.getElementById('nav-login-dialog');
        dialog.setAttribute('showed', 'true');
    } else if (element.getAttribute('mode') === 'logout') {
        const dialog = document.getElementById('nav-logout-dialog');
        dialog.setAttribute('showed', 'true');
    } else {
        console.error('Invalid mode for openLoginLogoutDialog:', element.getAttribute('mode'));
    }
}

function openLoginDialog() {
    const dialog = document.getElementById('nav-login-dialog');
    dialog.setAttribute('showed', 'true');
}

function openLogoutDialog() {
    const dialog = document.getElementById('nav-logout-dialog');
    dialog.setAttribute('showed', 'true');
}

function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    if (username && password) {
        fetch('/api/public/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        }).then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Login failed');
            }
        }).then(data => {
            if (data.success) {
                showDialog("成功", "登录成功");
                setTimeout(() => {
                    const dialog = document.getElementById('nav-login-dialog');
                    dialog.removeAttribute('showed');
                }, 2000);
                window.location.reload();
            } else {
                showDialog("错误", data.message || "登录失败，请重试");
            }
        }).catch(error => {
            console.error('Error during login:', error);
            showDialog("错误", "登录请求失败，请稍后再试");
        });
    } else {
        showDialog("错误", "用户名或密码不能为空");
    }
}

function showDialog(title, text) {
    const dialog = document.getElementById('global-dialog');
    document.getElementById('global-dialog-title').innerText = title;
    document.getElementById('global-dialog-text').innerText = text;
    dialog.setAttribute('showed', 'true');
}

function openAddItemDialog() {
    const dialog = document.getElementById("add-item-dialog");
    dialog.setAttribute('showed', 'true');
}

function checkTokenExists() {
    // 检查 cookie 中是否存在 token
    fetch("/api/admin/health", {
        method: "GET",
        credentials: "include"
    }).then(response => {
        if (response.ok) {
            const loginLogoutBtn = document.getElementById('nav-login-logout');
            loginLogoutBtn.setAttribute('mode', 'logout');
            loginLogoutBtn.innerHTML = `<svg slot="start" viewBox="0 0 1024 1024" id="icon-login-logout">
              <svg viewBox="0 -960 960 960">
                <path
                  d="M480-120v-80h280v-560H480v-80h280q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H480Zm-80-160-55-58 102-102H120v-80h327L345-622l55-58 200 200-200 200Z">
                </path>
              </svg>
            </svg>登出`;
            const addItemBtn = document.getElementById('nav-add-item');
            addItemBtn.classList.remove('hidden');
        } else {
            throw new Error("Token does not exist or is invalid");
        }
    }).catch(error => {

    })

}