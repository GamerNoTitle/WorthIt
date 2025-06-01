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