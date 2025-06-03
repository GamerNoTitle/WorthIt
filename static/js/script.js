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
                showDialog("成功", "登录成功，即将重新加载页面");
                sleep(2000);
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
    autoPaddingDatePicker();
    dialog.setAttribute('showed', 'true');
}

/**
 * 检查 cookie 中是否存在有效 token
 * 并根据结果更新导航栏 UI
 * @returns {Promise<boolean>} 如果 token 存在且有效则返回 true，否则返回 false
 */
async function checkTokenExistsAndValid() {
    try {
        const response = await fetch("/api/admin/health", {
            method: "GET",
            credentials: "include"
        });

        if (response.ok) {
            const loginLogoutBtn = document.getElementById('nav-login-logout');
            const addItemBtn = document.getElementById('nav-add-item');

            if (loginLogoutBtn) { // 总是检查元素是否存在
                loginLogoutBtn.setAttribute('mode', 'logout');
                loginLogoutBtn.innerHTML = `<svg slot="start" viewBox="0 0 1024 1024" id="icon-login-logout">
                  <svg viewBox="0 -960 960 960">
                    <path
                      d="M480-120v-80h280v-560H480v-80h280q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H480Zm-80-160-55-58 102-102H120v-80h327L345-622l55-58 200 200-200 200Z">
                    </path>
                  </svg>
                </svg>登出`;
            }
            if (addItemBtn) { // 总是检查元素是否存在
                addItemBtn.classList.remove('hidden');
            }
            return true; // Token 存在且有效
        } else {
            return false;
        }
    } catch (error) {
        console.error("检查 token 有效性时出错:", error);
        return false;
    }
}

/**
 * 执行用户登出操作
 */
async function logout() {
    try {
        const response = await fetch('/api/public/logout', {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok) {
            showDialog("成功", "登出成功");
            await sleep(2000); // 等待2秒后再刷新页面
            window.location.reload();
        } else {
            // 尝试从响应体获取错误信息
            const errorData = await response.json().catch(() => ({ message: '未知错误' }));
            throw new Error(`登出失败: ${response.status} - ${errorData.message || response.statusText}`);
        }
    } catch (error) {
        console.error('登出时出错:', error);
        showDialog("错误", "登出请求失败，请稍后再试");
    }
}

/**
 * 刷新物品列表，根据用户登录状态显示/隐藏编辑和删除按钮
 */
async function flushItemList(active = false) {
    const itemList = document.getElementById('item-list-container');
    const loadingContainer = document.getElementById('loading-container');
    const loadingErrorContainer = document.getElementById("loading-error-container");
    const loadingText = document.getElementById('loading-text');
    const needLoginContainer = document.getElementById('need-login-container');

    // 初始状态设置
    loadingContainer.classList.remove('hidden');
    loadingErrorContainer.classList.add('hidden');
    needLoginContainer.classList.add('hidden'); // 隐藏需要登录的提示
    loadingText.innerText = '正在加载物品列表，请稍候...';
    itemList.classList.add('hidden');

    // 确保在加载前清空列表
    itemList.innerHTML = '';

    const counter = document.getElementById('item-counter');
    counter.innerText = '0'; // 在加载前将计数器重置为0

    // 等待 checkTokenExistsAndValid 完成并获取登录状态
    const loggedIn = await checkTokenExistsAndValid();

    try {
        const response = await fetch('/api/public/items', {
            method: 'GET',
            credentials: 'include'
        });

        // 无论成功失败，都先隐藏加载容器
        loadingContainer.classList.add('hidden');

        if (!response.ok) {
            const errorData = await response.json();

            if (errorData.message === "本好物页面未公开展示，你需要登录来进行查看！") {
                console.log(errorData.message);
                needLoginContainer.classList.remove('hidden');
                counter.innerText = '0';
            } else {
                showDialog("错误", "获取物品列表失败，请稍后再试");
                console.error('获取物品列表失败:', response.status, response.statusText, errorData);
                itemList.classList.remove('hidden'); // 即使失败也要显示列表，可能显示错误信息
                
                // 创建错误提示元素
                const errorElement = document.createElement('s-empty');
                errorElement.style.textAlign = 'center';
                errorElement.style.display = 'block';
                errorElement.style.marginTop = '40px';
                errorElement.textContent = '加载物品列表失败，请稍后再试。';
                itemList.appendChild(errorElement);
            }
            return; // 错误情况下直接返回
        }

        // 如果响应成功
        const data = await response.json();

        counter.innerText = data.items.length || 0;

        if (data.items.length === 0) {
            itemList.classList.remove('hidden');
            // 创建空状态提示元素
            const emptyStateElement = document.createElement('s-empty');
            emptyStateElement.style.textAlign = 'center';
            emptyStateElement.style.display = 'block';
            emptyStateElement.style.marginTop = '40px';
            emptyStateElement.textContent = '暂时还没有物品哦~';
            itemList.appendChild(emptyStateElement);
            return; // 没有物品时直接返回
        }

        data.items.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'item';

            // 计算总价值
            const totalValue = (item.properties.购买价格 || 0) + (item.properties.附加价值 || 0);

            // 创建 s-card 元素
            const sCard = document.createElement('s-card');
            sCard.setAttribute('type', 'outlined');
            sCard.style.padding = '16px';

            // headline slot
            const headlineDiv = document.createElement('div');
            headlineDiv.setAttribute('slot', 'headline');
            headlineDiv.textContent = item.properties.物品名称 || '未知物品';
            sCard.appendChild(headlineDiv);

            // subhead slot
            const subheadDiv = document.createElement('div');
            subheadDiv.setAttribute('slot', 'subhead');
            subheadDiv.style.marginTop = '8px';
            subheadDiv.textContent = item.properties.备注 || '';
            sCard.appendChild(subheadDiv);

            // text slot (main content)
            const textDiv = document.createElement('div');
            textDiv.setAttribute('slot', 'text');
            textDiv.style.marginTop = '8px';

            // 购买价格
            const purchasePriceDiv = document.createElement('div');
            purchasePriceDiv.textContent = `购买价格：${item.properties.购买价格 !== undefined ? item.properties.购买价格 + ' 元' : '未填写'}`;
            textDiv.appendChild(purchasePriceDiv);

            // 附加价值 (条件显示)
            if (item.properties.附加价值 !== undefined) {
                const additionalValueDiv = document.createElement('div');
                additionalValueDiv.textContent = `附加价值：${item.properties.附加价值} 元`;
                textDiv.appendChild(additionalValueDiv);
            }

            // 总价值
            const totalValueDiv = document.createElement('div');
            totalValueDiv.textContent = `总价值：${totalValue} 元`;
            textDiv.appendChild(totalValueDiv);

            // 购买日期
            const entryDateDiv = document.createElement('div');
            entryDateDiv.textContent = `购买日期：${item.properties.入役日期 || '未填写'}`;
            textDiv.appendChild(entryDateDiv);

            // 退役日期 (条件显示)
            if (item.properties.退役日期) {
                const retirementDateDiv = document.createElement('div');
                retirementDateDiv.textContent = `退役日期：${item.properties.退役日期}`;
                textDiv.appendChild(retirementDateDiv);
            }

            // 服役天数
            const serviceDaysDiv = document.createElement('div');
            serviceDaysDiv.textContent = `服役天数：${item.properties.服役天数 !== undefined ? item.properties.服役天数 : '计算中...'}`;
            textDiv.appendChild(serviceDaysDiv);

            // 日均价格
            const dailyPriceDiv = document.createElement('div');
            dailyPriceDiv.textContent = `日均价格：${item.properties.日均价格 ? item.properties.日均价格 : "是刚刚开始用嘛？明天再来看吧 (¬◡¬)✧"}`;
            textDiv.appendChild(dailyPriceDiv);

            // 按钮容器
            const buttonContainer = document.createElement('div');
            buttonContainer.style.marginTop = '8px';
            buttonContainer.style.display = 'flex';
            buttonContainer.style.justifyContent = 'flex-end';
            buttonContainer.style.gap = '8px';

            // 编辑按钮 (条件显示)
            if (loggedIn) {
                const editButton = document.createElement('s-button');
                editButton.setAttribute('type', 'filled-tonal');
                editButton.textContent = '编辑';
                // 使用函数引用而不是字符串，避免XSS
                editButton.onclick = () => openEditItemDialog(item.id, item.properties.物品名称);
                buttonContainer.appendChild(editButton);
            }

            // 删除按钮 (条件显示)
            if (loggedIn) {
                const deleteButton = document.createElement('s-button');
                deleteButton.setAttribute('type', 'outlined');
                deleteButton.textContent = '删除';
                // 使用函数引用而不是字符串，避免XSS
                deleteButton.onclick = () => openDeleteItemDialog(item.id, item.properties.物品名称);
                buttonContainer.appendChild(deleteButton);
            }

            textDiv.appendChild(buttonContainer);
            sCard.appendChild(textDiv);
            itemElement.appendChild(sCard);
            itemList.appendChild(itemElement);
        });
        itemList.classList.remove('hidden'); // 确保列表可见
    } catch (error) {
        console.error('获取物品列表时出错:', error);
        loadingContainer.classList.add('hidden');
        loadingErrorContainer.classList.remove('hidden'); // 显示加载错误容器
        counter.innerText = '0'; // 发生异常时计数器也为0
    }
}

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function openDeleteItemDialog(itemId, itemName) {
    const dialog = document.getElementById('item-delete-dialog');
    const confirmButton = document.getElementById('item-delete-confirm-btn');
    const dialogText = document.getElementById('item-delete-dialog-text');
    dialogText.innerText = `您确定要删除物品 「${itemName}」 吗 (((ﾟДﾟ;)??`;
    confirmButton.setAttribute('onclick', `deleteItem('${itemId}', '${itemName}')`);
    dialog.setAttribute('showed', 'true');
}

function deleteItem(itemId, itemName) {
    fetch(`/api/admin/items/${itemId}`, {
        method: 'DELETE',
        credentials: 'include'
    }).then(response => {
        if (response.ok) {
            showDialog("成功", `物品 ${itemName} 删除成功 ╰(°▽°)╯`);
            return response.json();
        } else {
            throw new Error(`删除物品 ${itemName} 失败了 ╯﹏╰`);
        }
    }).then(() => {
        flushItemList();
    }).catch(error => {
        console.error('删除物品时出错:', error);
        showDialog("错误", "删除物品失败，请稍后再试 ╯﹏╰");
    });
}

function openEditItemDialog(itemId, itemName) {
    const dialog = document.getElementById('edit-item-dialog');
    const itemEditContainer = document.getElementById('edit-item-input-container');
    const itemIdInput = document.getElementById('edit-item-id');
    const itemNameInput = document.getElementById('edit-item-name');
    const itemPriceInput = document.getElementById('edit-item-purchase-price');
    const itemAdditionValue = document.getElementById('edit-item-additional-value');
    const itemEntryDateInput = document.getElementById('edit-item-entry-date');
    const itemRetirementDateInput = document.getElementById('edit-item-retirement-date');
    const itemWorkingDaysInput = document.getElementById('edit-item-working-days');
    const itemDailyValueInput = document.getElementById('edit-item-daily-value');
    const itemDescriptionInput = document.getElementById('edit-item-description');
    const loadingContainer = document.getElementById('edit-item-loading-container');
    const loadingText = document.getElementById('edit-item-loading-text');

    loadingContainer.classList.remove('hidden');
    loadingText.innerText = `正在加载物品「${itemName}」的信息，请稍候...`;
    itemEditContainer.classList.add('hidden');

    // 清空输入框
    itemIdInput.value = itemId;
    itemNameInput.value = '';
    itemPriceInput.value = '';
    itemAdditionValue.value = '';
    itemEntryDateInput.value = '';
    itemRetirementDateInput.value = '';
    itemWorkingDaysInput.value = '';
    itemDailyValueInput.value = '';
    itemDescriptionInput.value = '';


    // 显示对话框
    dialog.setAttribute('showed', 'true');

    // 获取物品信息并填充到输入框
    fetch(`/api/admin/items/${itemId}`, {
        method: 'GET',
        credentials: 'include'
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            showDialog("错误", "获取物品信息失败，请稍后再试");
            throw new Error(`获取物品信息失败: ${response.statusText}`);
        }
    }).then(data => {
        const item = data.item;
        itemNameInput.value = item.properties.物品名称 || '';
        itemPriceInput.value = item.properties.购买价格 || '';
        itemAdditionValue.value = item.properties.附加价值 || '';
        itemEntryDateInput.value = item.properties.入役日期 || '';
        itemRetirementDateInput.value = item.properties.退役日期 || '';
        itemWorkingDaysInput.value = item.properties.服役天数 || '';
        itemDailyValueInput.value = item.properties.日均价格 || '';
        itemDescriptionInput.value = item.properties.备注 || '';
        autoPaddingDatePicker();
        loadingContainer.classList.add('hidden'); // 隐藏加载容器
        itemEditContainer.classList.remove('hidden'); // 显示编辑容器
        prevData = {
            id: item.id,
            properties: {
                物品名称: item.properties.物品名称 || '',
                购买价格: item.properties.购买价格 || '',
                附加价值: item.properties.附加价值 || '',
                入役日期: item.properties.入役日期 || '',
                退役日期: item.properties.退役日期 || '',
                服役天数: item.properties.服役天数 || '',
                日均价格: item.properties.日均价格 || '',
                备注: item.properties.备注 || ''
            }
        }
        const confirmButton = document.getElementById('edit-item-save-btn');
        confirmButton.setAttribute('onclick', `editItem('${itemId}', ${JSON.stringify(prevData)})`);

    }).catch(error => {
        console.error('获取物品信息时出错:', error);
        loadingText.innerText = '获取物品信息失败，请稍后再试';
        showDialog("错误", "获取物品信息失败，请稍后再试");
    });
}

/**
 * 编辑物品信息
 * @param {string} itemId - 要编辑的物品的ID
 * @param {object} prevData - 物品当前的原始数据（包含 properties 对象）
 */
async function editItem(itemId, prevData) {
    // 获取所有相关输入框元素
    const itemIdInput = document.getElementById('edit-item-id');
    const itemNameInput = document.getElementById('edit-item-name');
    const itemPriceInput = document.getElementById('edit-item-purchase-price');
    const itemAdditionValue = document.getElementById('edit-item-additional-value');
    const itemEntryDateInput = document.getElementById('edit-item-entry-date');
    const itemRetirementDateInput = document.getElementById('edit-item-retirement-date');
    const itemDescriptionInput = document.getElementById('edit-item-description');

    let updatedProperties = {};

    if (itemNameInput.value !== prevData.properties.物品名称) {
        updatedProperties.name = itemNameInput.value;
    }

    const newPurchasePrice = parseFloat(itemPriceInput.value);
    if (!isNaN(newPurchasePrice) && newPurchasePrice !== prevData.properties.购买价格) {
        updatedProperties.purchase_price = newPurchasePrice;
    }

    const newAdditionalValue = parseFloat(itemAdditionValue.value);
    if (isNaN(newAdditionalValue)) {
        if (prevData.properties.附加价值 !== null && prevData.properties.附加价值 !== undefined) {
            updatedProperties.additional_value = null;
        }
    } else if (newAdditionalValue !== prevData.properties.附加价值) {
        updatedProperties.additional_value = newAdditionalValue;
    }

    if (itemEntryDateInput.value !== prevData.properties.入役日期) {
        updatedProperties.entry_date = itemEntryDateInput.value;
    }

    if (itemRetirementDateInput.value !== prevData.properties.退役日期) {
        updatedProperties.retirement_date = itemRetirementDateInput.value || null;
    }

    if (itemDescriptionInput.value !== prevData.properties.备注) {
        updatedProperties.remark = itemDescriptionInput.value;
    }

    // 如果没有任何属性被修改，则不发送请求，直接提示用户
    if (Object.keys(updatedProperties).length === 0) {
        showDialog("提示", "没有检测到任何更改，无需更新。");
        return;
    }

    showDialog("正在修改", "请稍候，正在修改物品信息...");

    try {
        const response = await fetch(`/api/admin/items/${itemId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(updatedProperties)
        });

        if (response.ok) {
            showDialog("成功", "物品信息修改成功，物品列表将在稍后刷新");
            await flushItemList(); // 修改成功后刷新列表，并等待其完成
        } else {
            // 尝试从服务器响应中获取具体的错误信息
            const errorText = await response.text(); // 先获取原始文本
            let errorMessage = `修改物品信息失败: ${response.status} - ${response.statusText}`;
            try {
                const errorJson = JSON.parse(errorText);
                if (errorJson.message) {
                    errorMessage = errorJson.message;
                } else if (errorJson.error) { // 某些API可能用 error 字段
                    errorMessage = errorJson.error;
                }
            } catch (e) {
                // 如果解析 JSON 失败，就用默认的错误信息
                console.warn("无法解析错误响应为 JSON:", errorText);
            }
            throw new Error(errorMessage);
        }
    } catch (error) {
        console.error('修改物品信息时出错:', error);
        showDialog("错误", error.message || "修改物品信息失败，请稍后再试");
    }
}

function onEntryDateChange(element) {
    autoPaddingDatePicker();
    const retirementDateInput = document.getElementById('edit-item-retirement-date');
    // 获取入役日期的值
    const entryDateValue = element.value;
    // 获取退役日期的值，如果不存在则以今天为准
    const retirementDateValue = retirementDateInput.value || new Date().toISOString().split('T')[0];
    // 计算服役天数
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 将毫秒转换为天数
    const workingDaysInput = document.getElementById('edit-item-working-days');
    workingDaysInput.value = workingDays + ' 天'; // 更新服役天数输入框的值
    // 计算日均价格
    const itemPriceInput = document.getElementById('edit-item-purchase-price');
    const itemAdditionValue = document.getElementById('edit-item-additional-value');
    const itemPrice = parseFloat(itemPriceInput.value) || 0; // 获取购买价格
    const additionalValue = parseFloat(itemAdditionValue.value) || 0; // 获取附加价值
    const totalValue = itemPrice + additionalValue; // 计算总价值
    const dailyValueInput = document.getElementById('edit-item-daily-value');
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 计算日均价格，保留两位小数
        dailyValueInput.value = dailyValue + ' 元'; // 更新日均价格输入框的值
    } else {
        dailyValueInput.value = '0.00 元'; // 如果服役天数为0，则设置为0
    }
}

function onRetirementDateChange(element) {
    autoPaddingDatePicker();
    const entryDateInput = document.getElementById('edit-item-entry-date');
    // 获取入役日期的值
    const entryDateValue = entryDateInput.value;
    // 获取退役日期的值
    const retirementDateValue = element.value;
    // 计算服役天数
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 将毫秒转换为天数
    const workingDaysInput = document.getElementById('edit-item-working-days');
    workingDaysInput.value = workingDays + ' 天'; // 更新服役天数输入框的值
    // 计算日均价格
    const itemPriceInput = document.getElementById('edit-item-purchase-price');
    const itemAdditionValue = document.getElementById('edit-item-additional-value');
    const itemPrice = parseFloat(itemPriceInput.value) || 0; // 获取购买价格
    const additionalValue = parseFloat(itemAdditionValue.value) || 0; // 获取附加价值
    const totalValue = itemPrice + additionalValue; // 计算总价值
    const dailyValueInput = document.getElementById('edit-item-daily-value');
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 计算日均价格，保留两位小数
        dailyValueInput.value = dailyValue + ' 元'; // 更新日均价格输入框的值
    } else {
        dailyValueInput.value = '0.00 元'; // 如果服役天数为0，则设置为0
    }
}

function onPurchasePriceChange() {
    // 当购买价格变化时，对于修改物品的情况，重新计算日均价格
    const itemEntryDateInput = document.getElementById('edit-item-entry-date');
    const itemRetirementDateInput = document.getElementById('edit-item-retirement-date');
    const itemPurchasePriceInput = document.getElementById('edit-item-purchase-price');
    const itemAdditionValue = document.getElementById('edit-item-additional-value');
    const itemWorkingDaysInput = document.getElementById('edit-item-working-days');
    const itemDailyValueInput = document.getElementById('edit-item-daily-value');
    // 获取入役日期的值
    const entryDateValue = itemEntryDateInput.value;
    // 获取退役日期的值，如果不存在则以今天为准
    const retirementDateValue = itemRetirementDateInput.value || new Date().toISOString().split('T')[0];
    // 计算服役天数
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 将毫秒转换为天数
    itemWorkingDaysInput.value = workingDays + ' 天'; // 更新服役天数输入框的值
    // 计算日均价格
    const itemPrice = parseFloat(itemPurchasePriceInput.value) || 0; // 获取购买价格
    const additionalValue = parseFloat(itemAdditionValue.value) || 0; // 获取附加价值
    const totalValue = itemPrice + additionalValue; // 计算总价值
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 计算日均价格，保留两位小数
        itemDailyValueInput.value = dailyValue + ' 元'; // 更新日均价格输入框的值
    } else {
        itemDailyValueInput.value = '0.00 元'; // 如果服役天数为0，则设置为0
    }
}

function onAdditionalValueChange() {
    // 当附加价值变化时，对于修改物品的情况，重新计算日均价格
    const itemEntryDateInput = document.getElementById('edit-item-entry-date');
    const itemRetirementDateInput = document.getElementById('edit-item-retirement-date');
    const itemPurchasePriceInput = document.getElementById('edit-item-purchase-price');
    const itemAdditionValue = document.getElementById('edit-item-additional-value');
    const itemWorkingDaysInput = document.getElementById('edit-item-working-days');
    const itemDailyValueInput = document.getElementById('edit-item-daily-value');
    // 获取入役日期的值
    const entryDateValue = itemEntryDateInput.value;
    // 获取退役日期的值，如果不存在则以今天为准
    const retirementDateValue = itemRetirementDateInput.value || new Date().toISOString().split('T')[0];
    // 计算服役天数
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 将毫秒转换为天数
    itemWorkingDaysInput.value = workingDays + ' 天'; // 更新服役天数输入框的值
    // 计算日均价格
    const itemPrice = parseFloat(itemPurchasePriceInput.value) || 0; // 获取购买价格
    const additionalValue = parseFloat(itemAdditionValue.value) || 0; // 获取附加价值
    const totalValue = itemPrice + additionalValue; // 计算总价值
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 计算日均价格，保留两位小数
        itemDailyValueInput.value = dailyValue + ' 元'; // 更新日均价格输入框的值
    } else {
        itemDailyValueInput.value = '0.00 元'; // 如果服役天数为0，则设置为0
    }
}

function onAddEntryDateChange() {
    autoPaddingDatePicker();
    const addItemEntryDateInput = document.getElementById('add-item-entry-date');
    const addItemRetirementDateInput = document.getElementById('add-item-retirement-date');
    // 获取入役日期的值
    const entryDateValue = addItemEntryDateInput.value;
    // 获取退役日期的值，如果不存在则以今天为准
    const retirementDateValue = addItemRetirementDateInput.value || new Date().toISOString().split('T')[0];
    // 计算服役天数
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 将毫秒转换为天数
    const workingDaysInput = document.getElementById('add-item-working-days');
    workingDaysInput.value = workingDays + ' 天'; // 更新服役天数输入框的值
    // 计算日均价格
    const itemPriceInput = document.getElementById('add-item-purchase-price');
    const itemAdditionValue = document.getElementById('add-item-additional-value');
    const itemPrice = parseFloat(itemPriceInput.value) || 0; // 获取购买价格
    const additionalValue = parseFloat(itemAdditionValue.value) || 0; // 获取附加价值
    const totalValue = itemPrice + additionalValue; // 计算总价值
    const dailyValueInput = document.getElementById('add-item-daily-value');
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 计算日均价格，保留两位小数
        dailyValueInput.value = dailyValue + ' 元'; // 更新日均价格输入框的值
    } else {
        dailyValueInput.value = '0.00 元'; // 如果服役天数为0，则设置为0
    }
}

function onAddRetirementDateChange() {
    autoPaddingDatePicker();
    const addItemEntryDateInput = document.getElementById('add-item-entry-date');
    const addItemRetirementDateInput = document.getElementById('add-item-retirement-date');
    // 获取入役日期的值
    const entryDateValue = addItemEntryDateInput.value;
    // 获取退役日期的值
    const retirementDateValue = addItemRetirementDateInput.value;
    // 计算服役天数
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 将毫秒转换为天数
    const workingDaysInput = document.getElementById('add-item-working-days');
    workingDaysInput.value = workingDays + ' 天'; // 更新服役天数输入框的值
    // 计算日均价格
    const itemPriceInput = document.getElementById('add-item-purchase-price');
    const itemAdditionValue = document.getElementById('add-item-additional-value');
    const itemPrice = parseFloat(itemPriceInput.value) || 0; // 获取购买价格
    const additionalValue = parseFloat(itemAdditionValue.value) || 0; // 获取附加价值
    const totalValue = itemPrice + additionalValue; // 计算总价值
    const dailyValueInput = document.getElementById('add-item-daily-value');
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 计算日均价格，保留两位小数
        dailyValueInput.value = dailyValue + ' 元'; // 更新日均价格输入框的值
    } else {
        dailyValueInput.value = '0.00 元'; // 如果服役天数为0，则设置为0
    }
}

function onAddPurchasePriceChange() {
    // 通过获取入役日期和退役日期计算日均价格
    const addItemEntryDateInput = document.getElementById('add-item-entry-date');
    const addItemRetirementDateInput = document.getElementById('add-item-retirement-date');
    const addItemPurchasePriceInput = document.getElementById('add-item-purchase-price');
    const addItemAdditionValueInput = document.getElementById('add-item-additional-value');
    const addItemWorkingDaysInput = document.getElementById('add-item-working-days');
    const addItemDailyValueInput = document.getElementById('add-item-daily-value');
    // 获取入役日期的值
    const entryDateValue = addItemEntryDateInput.value;
    // 获取退役日期的值，如果不存在则以今天为准
    const retirementDateValue = addItemRetirementDateInput.value || new Date().toISOString().split('T')[0];
    // 计算服役天数
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 将毫秒转换为天数
    addItemWorkingDaysInput.value = workingDays + ' 天'; // 更新服役天数输入框的值
    // 计算日均价格
    const itemPrice = parseFloat(addItemPurchasePriceInput.value) || 0; // 获取购买价格
    const additionalValue = parseFloat(addItemAdditionValueInput.value) || 0; // 获取附加价值
    const totalValue = itemPrice + additionalValue; // 计算总价值
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 计算日均价格，保留两位小数
        addItemDailyValueInput.value = dailyValue + ' 元'; // 更新日均价格输入框的值
    } else {
        addItemDailyValueInput.value = '0.00 元'; // 如果服役天数为0，则设置为0
    }
}

function onAddAdditionalValueChange() {
    // 通过获取入役日期和退役日期计算日均价格
    const addItemEntryDateInput = document.getElementById('add-item-entry-date');
    const addItemRetirementDateInput = document.getElementById('add-item-retirement-date');
    const addItemPurchasePriceInput = document.getElementById('add-item-purchase-price');
    const addItemAdditionValueInput = document.getElementById('add-item-additional-value');
    const addItemWorkingDaysInput = document.getElementById('add-item-working-days');
    const addItemDailyValueInput = document.getElementById('add-item-daily-value');
    // 获取入役日期的值
    const entryDateValue = addItemEntryDateInput.value;
    // 获取退役日期的值，如果不存在则以今天为准
    const retirementDateValue = addItemRetirementDateInput.value || new Date().toISOString().split('T')[0];
    // 计算服役天数
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 将毫秒转换为天数
    addItemWorkingDaysInput.value = workingDays + ' 天'; // 更新服役天数输入框的值
    // 计算日均价格
    const itemPrice = parseFloat(addItemPurchasePriceInput.value) || 0; // 获取购买价格
    const additionalValue = parseFloat(addItemAdditionValueInput.value) || 0; // 获取附加价值
    const totalValue = itemPrice + additionalValue; // 计算总价值
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 计算日均价格，保留两位小数
        addItemDailyValueInput.value = dailyValue + ' 元'; // 更新日均价格输入框的值
    } else {
        addItemDailyValueInput.value = '0.00 元'; // 如果服役天数为0，则设置为0
    }
}

function autoPaddingDatePicker() {
    const itemEntryDateInput = document.getElementById('edit-item-entry-date');
    const itemRetirementDateInput = document.getElementById('edit-item-retirement-date');
    const addItemEntryDateInput = document.getElementById('add-item-entry-date');
    const addItemRetirementDateInput = document.getElementById('add-item-retirement-date');
    if (addItemEntryDateInput.value) {
        addItemEntryDateInput.setAttribute("label", "入役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    }
    else (
        addItemEntryDateInput.setAttribute("label", "入役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    )
    if (addItemRetirementDateInput.value) {
        addItemRetirementDateInput.setAttribute("label", "退役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    } else {
        addItemRetirementDateInput.setAttribute("label", "退役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    }
    if (itemEntryDateInput.value) {
        itemEntryDateInput.setAttribute("label", "入役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    }
    else (
        itemEntryDateInput.setAttribute("label", "入役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    )
    if (itemRetirementDateInput.value) {
        itemRetirementDateInput.setAttribute("label", "退役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    } else {
        itemRetirementDateInput.setAttribute("label", "退役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    }
}

function addItem() {
    const itemNameInput = document.getElementById('add-item-name');
    const itemPriceInput = document.getElementById('add-item-purchase-price');
    const itemAdditionValue = document.getElementById('add-item-additional-value');
    const itemEntryDateInput = document.getElementById('add-item-entry-date');
    const itemRetirementDateInput = document.getElementById('add-item-retirement-date');
    const itemDescriptionInput = document.getElementById('add-item-description');

    if (!itemNameInput.value || !itemPriceInput.value || !itemEntryDateInput.value) {
        showDialog("错误", "物品名称、购买价格和入役日期不能为空");
        return;
    }

    const newItem = {
        properties: {
            name: itemNameInput.value,
            purchase_price: parseFloat(itemPriceInput.value),
            additional_value: parseFloat(itemAdditionValue.value) || 0,
            entry_date: itemEntryDateInput.value,
            retirement_date: itemRetirementDateInput.value || null,
            remark: itemDescriptionInput.value || ''
        }
    };
    showDialog("正在添加", `请稍候，正在添加物品「${itemNameInput.value}」...`);
    fetch('/api/admin/items', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(newItem)
    }).then(response => {
        if (response.ok) {
            showDialog("成功", "物品添加成功，即将刷新物品列表");
            return response.json();
        } else {
            throw new Error('添加物品失败，请稍后再试');
        }
    }).then(() => {
        flushItemList();
    }).catch(error => {
        console.error('添加物品时出错:', error);
        showDialog("错误", error.message);
    });
}

function changeAccentColor(color, fromRecover = false) {
    sober.theme.createScheme(color, { page: document.querySelector('s-page') })
    localStorage.setItem('accentColor', color);
    if (fromRecover) {
        document.getElementById('color-picker').value = color;
    }
}