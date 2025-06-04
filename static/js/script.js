/**
 * 更改导航栏选中状态
 * 移除所有导航元素的'checked'属性，并设置当前点击的元素为'checked'。
 * @param {HTMLElement} element - 当前被点击的导航元素。
 * @returns {void}
 */
function changeNavigation(element) {
    // 定义需要重置'checked'属性的导航元素ID列表
    elements = ['nav-my-items', 'nav-login-logout']
    // 遍历列表，移除每个元素的'checked'属性
    for (let i = 0; i < elements.length; i++) {
        document.getElementById(elements[i]).removeAttribute('checked');
    }
    // 设置当前点击的元素为'checked'状态
    element.setAttribute('checked', 'true');
}

/**
 * 在新标签页中打开GitHub仓库链接。
 * @returns {void}
 */
function openGithubRepo() {
    window.open('https://github.com/GamerNoTitle/WorthIt', '_blank');
}

/**
 * 显示“关于”对话框。
 * 通过设置'showed'属性为'true'来显示对话框。
 * @returns {void}
 */
function openAboutDialog() {
    const dialog = document.getElementById('nav-about-dialog');
    dialog.setAttribute('showed', 'true'); // 设置属性以显示对话框
}

/**
 * 根据元素的'mode'属性显示登录或登出对话框。
 * @param {HTMLElement} element - 触发此函数的元素，其'mode'属性决定显示哪个对话框。
 * @returns {void}
 */
function openLoginLogoutDialog(element) {
    // 检查元素的'mode'属性
    if (element.getAttribute('mode') === 'login') {
        const dialog = document.getElementById('nav-login-dialog');
        dialog.setAttribute('showed', 'true'); // 显示登录对话框
    } else if (element.getAttribute('mode') === 'logout') {
        const dialog = document.getElementById('nav-logout-dialog');
        dialog.setAttribute('showed', 'true'); // 显示登出对话框
    } else {
        // 如果'mode'属性无效，则输出错误信息
        console.error('Invalid mode for openLoginLogoutDialog:', element.getAttribute('mode'));
    }
}

/**
 * 显示登录对话框。
 * @returns {void}
 */
function openLoginDialog() {
    const dialog = document.getElementById('nav-login-dialog');
    dialog.setAttribute('showed', 'true'); // 设置属性以显示登录对话框
}

/**
 * 显示登出对话框。
 * @returns {void}
 */
function openLogoutDialog() {
    const dialog = document.getElementById('nav-logout-dialog');
    dialog.setAttribute('showed', 'true'); // 设置属性以显示登出对话框
}

/**
 * 处理用户登录逻辑。
 * 获取用户名和密码，发送POST请求到后端API进行认证，并根据响应显示结果。
 * @returns {void}
 */
function login() {
    // 获取用户名和密码输入框的值
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    // 检查用户名和密码是否为空
    if (username && password) {
        // 发送登录请求到后端API
        fetch('/api/public/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' // 设置请求头为JSON格式
            },
            body: JSON.stringify({ username, password }) // 将用户名和密码作为JSON字符串发送
        }).then(response => {
            // 检查响应是否成功 (HTTP 2xx)
            if (response.ok) {
                return response.json(); // 解析JSON响应
            } else {
                // 如果响应不成功，抛出错误
                throw new Error('Login failed');
            }
        }).then(data => {
            // 处理登录成功或失败的数据
            if (data.success) {
                showDialog("成功", "登录成功，即将重新加载页面"); // 显示成功对话框
                sleep(2000); // 等待2秒
                window.location.reload(); // 重新加载页面
            } else {
                showDialog("错误", data.message || "登录失败，请重试"); // 显示错误对话框，使用后端返回的消息或默认消息
            }
        }).catch(error => {
            // 捕获fetch请求或then链中的错误
            console.error('Error during login:', error);
            showDialog("错误", "登录请求失败，请稍后再试"); // 显示网络请求失败对话框
        });
    } else {
        showDialog("错误", "用户名或密码不能为空"); // 提示用户名或密码为空
    }
}

/**
 * 显示一个全局对话框。
 * @param {string} title - 对话框的标题。
 * @param {string} text - 对话框显示的内容文本。
 * @returns {void}
 */
function showDialog(title, text) {
    const dialog = document.getElementById('global-dialog');
    document.getElementById('global-dialog-title').innerText = title; // 设置对话框标题
    document.getElementById('global-dialog-text').innerText = text; // 设置对话框文本内容
    dialog.setAttribute('showed', 'true'); // 设置属性以显示对话框
}

/**
 * 显示添加物品对话框。
 * 同时调用 `autoPaddingDatePicker` 调整日期选择器样式。
 * @returns {void}
 */
function openAddItemDialog() {
    const dialog = document.getElementById("add-item-dialog");
    autoPaddingDatePicker(); // 调整日期选择器填充
    dialog.setAttribute('showed', 'true'); // 设置属性以显示对话框
}

/**
 * 检查 cookie 中是否存在有效 token
 * 并根据结果更新导航栏 UI
 * @returns {Promise<boolean>} 如果 token 存在且有效则返回 true，否则返回 false
 */
async function checkTokenExistsAndValid() {
    try {
        // 向受保护的admin API发送健康检查请求，带上cookie
        const response = await fetch("/api/admin/health", {
            method: "GET",
            credentials: "include" // 确保请求包含cookie
        });

        // 如果响应成功（HTTP 2xx），表示token有效
        if (response.ok) {
            const loginLogoutBtn = document.getElementById('nav-login-logout');
            const addItemBtn = document.getElementById('nav-add-item');

            // 更新登录/登出按钮的UI为“登出”状态
            if (loginLogoutBtn) {
                loginLogoutBtn.setAttribute('mode', 'logout'); // 设置mode为logout
                loginLogoutBtn.innerHTML = `<svg slot="start" viewBox="0 0 1024 1024" id="icon-login-logout">
                  <svg viewBox="0 -960 960 960">
                    <path
                      d="M480-120v-80h280v-560H480v-80h280q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H480Zm-80-160-55-58 102-102H120v-80h327L345-622l55-58 200 200-200 200Z">
                    </path>
                  </svg>
                </svg>登出`; // 更新按钮文本和图标
            }
            // 显示添加物品按钮
            if (addItemBtn) {
                addItemBtn.classList.remove('hidden');
            }
            return true; // 返回true表示token有效
        } else {
            // 如果响应不成功，表示token无效或不存在
            return false;
        }
    } catch (error) {
        // 捕获网络错误或请求失败
        console.error("检查 token 有效性时出错:", error);
        return false; // 返回false
    }
}

/**
 * 执行用户登出操作
 * 发送POST请求到后端API进行登出，并根据响应显示结果。
 * @returns {Promise<void>}
 */
async function logout() {
    try {
        // 发送登出请求到后端API
        const response = await fetch('/api/public/logout', {
            method: 'POST',
            credentials: 'include' // 确保请求包含cookie
        });

        // 如果响应成功
        if (response.ok) {
            showDialog("成功", "登出成功"); // 显示成功对话框
            await sleep(2000); // 等待2秒
            window.location.reload(); // 重新加载页面
        } else {
            // 尝试解析错误响应体
            const errorData = await response.json().catch(() => ({ message: '未知错误' }));
            // 抛出带有详细错误信息的错误
            throw new Error(`登出失败: ${response.status} - ${errorData.message || response.statusText}`);
        }
    } catch (error) {
        // 捕获并处理登出请求中的错误
        console.error('登出时出错:', error);
        showDialog("错误", "登出请求失败，请稍后再试"); // 显示错误对话框
    }
}

/**
 * 刷新物品列表，根据用户登录状态显示/隐藏编辑和删除按钮
 * @param {boolean} [active=false] - 未使用的参数，但保留以便将来扩展。
 * @returns {Promise<void>}
 */
async function flushItemList(active = false) {
    // 获取DOM元素
    const itemList = document.getElementById('item-list-container');
    const loadingContainer = document.getElementById('loading-container');
    const loadingErrorContainer = document.getElementById("loading-error-container");
    const loadingText = document.getElementById('loading-text');
    const needLoginContainer = document.getElementById('need-login-container');

    // 显示加载状态，隐藏其他状态
    loadingContainer.classList.remove('hidden');
    loadingErrorContainer.classList.add('hidden');
    needLoginContainer.classList.add('hidden');
    loadingText.innerText = '正在加载物品列表，请稍候...';
    itemList.classList.add('hidden'); // 隐藏物品列表容器

    itemList.innerHTML = ''; // 清空当前物品列表
    const counter = document.getElementById('item-counter');
    counter.innerText = '0'; // 重置物品计数器

    // 检查用户登录状态
    const loggedIn = await checkTokenExistsAndValid();

    try {
        // 发送请求获取物品列表
        const response = await fetch('/api/public/items', {
            method: 'GET',
            credentials: 'include' // 确保发送cookie以处理私有页面情况
        });

        loadingContainer.classList.add('hidden'); // 隐藏加载状态

        // 如果响应不成功
        if (!response.ok) {
            const errorData = await response.json(); // 解析错误数据

            // 特定错误消息处理：页面未公开展示
            if (errorData.message === "本好物页面未公开展示，你需要登录来进行查看！") {
                console.log(errorData.message);
                needLoginContainer.classList.remove('hidden'); // 显示需要登录的提示
                counter.innerText = '0';
            } else {
                showDialog("错误", "获取物品列表失败，请稍后再试"); // 显示通用错误对话框
                console.error('获取物品列表失败:', response.status, response.statusText, errorData);
                itemList.classList.remove('hidden'); // 显示物品列表容器（即使是空的或错误状态）

                // 创建并添加错误提示元素
                const errorElement = document.createElement('s-empty');
                errorElement.style.textAlign = 'center';
                errorElement.style.display = 'block';
                errorElement.style.marginTop = '40px';
                errorElement.textContent = '加载物品列表失败，请稍后再试。';
                itemList.appendChild(errorElement);
            }
            return; // 结束函数执行
        }

        const data = await response.json(); // 解析成功的响应数据

        counter.innerText = data.items.length || 0; // 更新物品计数

        // 如果物品列表为空
        if (data.items.length === 0) {
            itemList.classList.remove('hidden'); // 显示物品列表容器
            // 创建并添加空状态提示元素
            const emptyStateElement = document.createElement('s-empty');
            emptyStateElement.style.textAlign = 'center';
            emptyStateElement.style.display = 'block';
            emptyStateElement.style.marginTop = '40px';
            emptyStateElement.textContent = '暂时还没有物品哦~';
            itemList.appendChild(emptyStateElement);
            return; // 结束函数执行
        }

        // 遍历物品数据，为每个物品创建DOM元素并添加到列表中
        data.items.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'item';

            // 计算总价值
            const totalValue = (item.properties.购买价格 || 0) + (item.properties.附加价值 || 0);

            // 创建 s-card 组件
            const sCard = document.createElement('s-card');
            sCard.setAttribute('type', 'outlined');
            sCard.style.padding = '16px';

            // 设置 headline (物品名称)
            const headlineDiv = document.createElement('div');
            headlineDiv.setAttribute('slot', 'headline');
            headlineDiv.textContent = item.properties.物品名称 || '未知物品';
            sCard.appendChild(headlineDiv);

            // 设置 subhead (备注)
            const subheadDiv = document.createElement('div');
            subheadDiv.setAttribute('slot', 'subhead');
            subheadDiv.style.marginTop = '8px';
            subheadDiv.textContent = item.properties.备注 || '';
            sCard.appendChild(subheadDiv);

            // 设置 text 部分 (物品属性)
            const textDiv = document.createElement('div');
            textDiv.setAttribute('slot', 'text');
            textDiv.style.marginTop = '8px';

            // 添加购买价格
            const purchasePriceDiv = document.createElement('div');
            purchasePriceDiv.textContent = `购买价格：${item.properties.购买价格 !== undefined ? item.properties.购买价格 + ' 元' : '未填写'}`;
            textDiv.appendChild(purchasePriceDiv);

            // 添加附加价值（如果存在）
            if (item.properties.附加价值 !== undefined) {
                const additionalValueDiv = document.createElement('div');
                additionalValueDiv.textContent = `附加价值：${item.properties.附加价值} 元`;
                textDiv.appendChild(additionalValueDiv);
            }

            // 添加总价值
            const totalValueDiv = document.createElement('div');
            totalValueDiv.textContent = `总价值：${totalValue} 元`;
            textDiv.appendChild(totalValueDiv);

            // 添加购买日期
            const entryDateDiv = document.createElement('div');
            entryDateDiv.textContent = `购买日期：${item.properties.入役日期 || '未填写'}`;
            textDiv.appendChild(entryDateDiv);

            // 添加退役日期（如果存在）
            if (item.properties.退役日期) {
                const retirementDateDiv = document.createElement('div');
                retirementDateDiv.textContent = `退役日期：${item.properties.退役日期}`;
                textDiv.appendChild(retirementDateDiv);
            }

            // 添加服役天数
            const serviceDaysDiv = document.createElement('div');
            serviceDaysDiv.textContent = `服役天数：${item.properties.服役天数 !== undefined ? item.properties.服役天数 : '计算中...'}`;
            textDiv.appendChild(serviceDaysDiv);

            // 添加日均价格
            const dailyPriceDiv = document.createElement('div');
            dailyPriceDiv.textContent = `日均价格：${item.properties.日均价格 ? item.properties.日均价格 : "是刚刚开始用嘛？明天再来看吧 (¬◡¬)✧"}`;
            textDiv.appendChild(dailyPriceDiv);

            // 创建按钮容器
            const buttonContainer = document.createElement('div');
            buttonContainer.style.marginTop = '8px';
            buttonContainer.style.display = 'flex';
            buttonContainer.style.justifyContent = 'flex-end';
            buttonContainer.style.gap = '8px';

            // 如果已登录，显示编辑按钮
            if (loggedIn) {
                const editButton = document.createElement('s-button');
                editButton.setAttribute('type', 'filled-tonal');
                editButton.textContent = '编辑';
                editButton.onclick = () => openEditItemDialog(item.id, item.properties.物品名称); // 绑定点击事件
                buttonContainer.appendChild(editButton);
            }

            // 如果已登录，显示删除按钮
            if (loggedIn) {
                const deleteButton = document.createElement('s-button');
                deleteButton.setAttribute('type', 'outlined');
                deleteButton.textContent = '删除';
                deleteButton.onclick = () => openDeleteItemDialog(item.id, item.properties.物品名称); // 绑定点击事件
                buttonContainer.appendChild(deleteButton);
            }

            textDiv.appendChild(buttonContainer); // 将按钮容器添加到 textDiv
            sCard.appendChild(textDiv); // 将 textDiv 添加到 s-card
            itemElement.appendChild(sCard); // 将 s-card 添加到 itemElement
            itemList.appendChild(itemElement); // 将 itemElement 添加到物品列表容器
        });
        itemList.classList.remove('hidden'); // 显示物品列表容器
    } catch (error) {
        // 捕获并处理获取物品列表过程中的错误
        console.error('获取物品列表时出错:', error);
        loadingContainer.classList.add('hidden'); // 隐藏加载状态
        loadingErrorContainer.classList.remove('hidden'); // 显示加载错误提示
        counter.innerText = '0'; // 重置物品计数
    }
}

/**
 * 创建一个延时Promise。
 * @param {number} time - 延时的时间，单位毫秒。
 * @returns {Promise<void>} 一个在指定时间后解析的Promise。
 */
function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

/**
 * 显示删除物品确认对话框。
 * @param {string} itemId - 要删除的物品的ID。
 * @param {string} itemName - 要删除的物品的名称。
 * @returns {void}
 */
function openDeleteItemDialog(itemId, itemName) {
    const dialog = document.getElementById('item-delete-dialog');
    const confirmButton = document.getElementById('item-delete-confirm-btn');
    const dialogText = document.getElementById('item-delete-dialog-text');
    dialogText.innerText = `您确定要删除物品 「${itemName}」 吗 (((ﾟДﾟ;)??`; // 设置对话框文本
    confirmButton.onclick = function() {
        deleteItem(itemId, itemName); // 绑定删除操作到确认按钮
    };
    dialog.setAttribute('showed', 'true'); // 显示删除确认对话框
}

/**
 * 执行删除物品操作。
 * @param {string} itemId - 要删除的物品的ID。
 * @param {string} itemName - 要删除的物品的名称。
 * @returns {void}
 */
function deleteItem(itemId, itemName) {
    // 发送DELETE请求到后端API删除物品
    fetch(`/api/admin/items/${itemId}`, {
        method: 'DELETE',
        credentials: 'include' // 确保请求包含cookie
    }).then(response => {
        // 检查响应是否成功
        if (response.ok) {
            showDialog("成功", `物品 ${itemName} 删除成功 ╰(°▽°)╯`); // 显示成功对话框
            return response.json(); // 解析JSON响应
        } else {
            // 如果响应不成功，抛出错误
            throw new Error(`删除物品 ${itemName} 失败了 ╯﹏╰`);
        }
    }).then(() => {
        flushItemList(); // 删除成功后刷新物品列表
    }).catch(error => {
        // 捕获并处理删除物品过程中的错误
        console.error('删除物品时出错:', error);
        showDialog("错误", "删除物品失败，请稍后再试 ╯﹏╰"); // 显示错误对话框
    });
}

/**
 * 显示编辑物品对话框，并加载物品的当前信息。
 * @param {string} itemId - 要编辑的物品的ID。
 * @param {string} itemName - 要编辑的物品的名称。
 * @returns {void}
 */
function openEditItemDialog(itemId, itemName) {
    // 获取对话框和输入框元素
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

    // 显示加载状态，隐藏编辑表单
    loadingContainer.classList.remove('hidden');
    loadingText.innerText = `正在加载物品「${itemName}」的信息，请稍候...`;
    itemEditContainer.classList.add('hidden');

    // 清空所有输入框的值，避免显示旧数据
    itemIdInput.value = itemId; // 设置物品ID
    itemNameInput.value = '';
    itemPriceInput.value = '';
    itemAdditionValue.value = '';
    itemEntryDateInput.value = '';
    itemRetirementDateInput.value = '';
    itemWorkingDaysInput.value = '';
    itemDailyValueInput.value = '';
    itemDescriptionInput.value = '';

    dialog.setAttribute('showed', 'true'); // 显示编辑对话框

    // 发送请求获取物品的详细信息
    fetch(`/api/admin/items/${itemId}`, {
        method: 'GET',
        credentials: 'include' // 确保请求包含cookie
    }).then(response => {
        // 检查响应是否成功
        if (response.ok) {
            return response.json(); // 解析JSON响应
        } else {
            showDialog("错误", "获取物品信息失败，请稍后再试"); // 显示错误对话框
            throw new Error(`获取物品信息失败: ${response.statusText}`);
        }
    }).then(data => {
        const item = data.item;
        // 填充输入框为物品的当前值
        itemNameInput.value = item.properties.物品名称 || '';
        itemPriceInput.value = item.properties.购买价格 || '';
        itemAdditionValue.value = item.properties.附加价值 || '';
        itemEntryDateInput.value = item.properties.入役日期 || '';
        itemRetirementDateInput.value = item.properties.退役日期 || '';
        itemWorkingDaysInput.value = item.properties.服役天数 || '';
        itemDailyValueInput.value = item.properties.日均价格 || '';
        itemDescriptionInput.value = item.properties.备注 || '';
        autoPaddingDatePicker(); // 调整日期选择器样式
        loadingContainer.classList.add('hidden'); // 隐藏加载状态
        itemEditContainer.classList.remove('hidden'); // 显示编辑表单

        // 存储原始数据，用于后续判断哪些字段被修改
        const prevData = {
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
        };
        const confirmButton = document.getElementById('edit-item-save-btn');
        // 绑定保存操作到确认按钮，并传递物品ID和原始数据
        confirmButton.onclick = function() {
            editItem(itemId, prevData);
        };

    }).catch(error => {
        // 捕获并处理获取物品信息过程中的错误
        console.error('获取物品信息时出错:', error);
        loadingText.innerText = '获取物品信息失败，请稍后再试'; // 更新加载文本为错误信息
        showDialog("错误", "获取物品信息失败，请稍后再试"); // 显示错误对话框
    });
}

/**
 * 编辑物品信息。
 * 比较当前表单值与原始数据，只发送有更改的字段到后端进行PATCH更新。
 * @param {string} itemId - 要编辑的物品的ID。
 * @param {object} prevData - 物品当前的原始数据（包含 properties 对象）。
 * @returns {Promise<void>}
 */
async function editItem(itemId, prevData) {
    // 获取所有相关输入框的当前值
    const itemNameInput = document.getElementById('edit-item-name');
    const itemPriceInput = document.getElementById('edit-item-purchase-price');
    const itemAdditionValue = document.getElementById('edit-item-additional-value');
    const itemEntryDateInput = document.getElementById('edit-item-entry-date');
    const itemRetirementDateInput = document.getElementById('edit-item-retirement-date');
    const itemDescriptionInput = document.getElementById('edit-item-description');

    let updatedProperties = {}; // 用于存储已修改的属性

    // 比较并添加修改后的属性
    if (itemNameInput.value !== prevData.properties.物品名称) {
        updatedProperties.name = itemNameInput.value;
    }

    const newPurchasePrice = parseFloat(itemPriceInput.value);
    if (!isNaN(newPurchasePrice) && newPurchasePrice !== prevData.properties.购买价格) {
        updatedProperties.purchase_price = newPurchasePrice;
    }

    const newAdditionalValue = parseFloat(itemAdditionValue.value);
    // 处理附加价值为空的情况，如果之前有值现在清空，则设置为null
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

    // 处理退役日期为空的情况，如果之前有值现在清空，则设置为null
    if (itemRetirementDateInput.value !== prevData.properties.退役日期) {
        updatedProperties.retirement_date = itemRetirementDateInput.value || null;
    }

    if (itemDescriptionInput.value !== prevData.properties.备注) {
        updatedProperties.remark = itemDescriptionInput.value;
    }

    // 如果没有检测到任何更改，则显示提示并返回
    if (Object.keys(updatedProperties).length === 0) {
        showDialog("提示", "没有检测到任何更改，无需更新。");
        return;
    }

    showDialog("正在修改", "请稍候，正在修改物品信息..."); // 显示正在修改的提示

    try {
        // 发送PATCH请求到后端API更新物品信息
        const response = await fetch(`/api/admin/items/${itemId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json' // 设置请求头为JSON格式
            },
            credentials: 'include', // 确保请求包含cookie
            body: JSON.stringify(updatedProperties) // 发送修改后的属性
        });

        // 检查响应是否成功
        if (response.ok) {
            showDialog("成功", "物品信息修改成功，物品列表将在稍后刷新"); // 显示成功对话框
            await flushItemList(); // 刷新物品列表
        } else {
            const errorText = await response.text(); // 获取错误响应文本
            let errorMessage = `修改物品信息失败: ${response.status} - ${response.statusText}`;
            try {
                const errorJson = JSON.parse(errorText); // 尝试解析JSON错误响应
                if (errorJson.message) {
                    errorMessage = errorJson.message;
                } else if (errorJson.error) {
                    errorMessage = errorJson.error;
                }
            } catch (e) {
                console.warn("无法解析错误响应为 JSON:", errorText); // 如果无法解析为JSON
            }
            throw new Error(errorMessage); // 抛出带有详细信息的错误
        }
    } catch (error) {
        // 捕获并处理修改物品信息过程中的错误
        console.error('修改物品信息时出错:', error);
        showDialog("错误", error.message || "修改物品信息失败，请稍后再试"); // 显示错误对话框
    }
}

/**
 * 当入役日期改变时，重新计算服役天数和日均价格。
 * @param {HTMLInputElement} element - 触发此事件的入役日期输入框。
 * @returns {void}
 */
function onEntryDateChange(element) {
    autoPaddingDatePicker(); // 调整日期选择器样式
    const retirementDateInput = document.getElementById('edit-item-retirement-date');
    const entryDateValue = element.value;
    // 如果退役日期未填写，则默认为当前日期
    const retirementDateValue = retirementDateInput.value || new Date().toISOString().split('T')[0];
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    // 计算服役天数，向上取整以包含当天
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
    const workingDaysInput = document.getElementById('edit-item-working-days');
    workingDaysInput.value = workingDays + ' 天'; // 更新服役天数显示

    // 获取购买价格和附加价值
    const itemPriceInput = document.getElementById('edit-item-purchase-price');
    const itemAdditionValue = document.getElementById('edit-item-additional-value');
    const itemPrice = parseFloat(itemPriceInput.value) || 0;
    const additionalValue = parseFloat(itemAdditionValue.value) || 0;
    const totalValue = itemPrice + additionalValue; // 计算总价值

    const dailyValueInput = document.getElementById('edit-item-daily-value');
    // 计算日均价格
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 保留两位小数
        dailyValueInput.value = dailyValue + ' 元'; // 更新日均价格显示
    } else {
        dailyValueInput.value = '0.00 元'; // 如果服役天数为0或负数，日均价格为0
    }
}

/**
 * 当退役日期改变时，重新计算服役天数和日均价格。
 * @param {HTMLInputElement} element - 触发此事件的退役日期输入框。
 * @returns {void}
 */
function onRetirementDateChange(element) {
    autoPaddingDatePicker(); // 调整日期选择器样式
    const entryDateInput = document.getElementById('edit-item-entry-date');
    const entryDateValue = entryDateInput.value;
    const retirementDateValue = element.value;
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    // 计算服役天数，向上取整以包含当天
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
    const workingDaysInput = document.getElementById('edit-item-working-days');
    workingDaysInput.value = workingDays + ' 天'; // 更新服役天数显示

    // 获取购买价格和附加价值
    const itemPriceInput = document.getElementById('edit-item-purchase-price');
    const itemAdditionValue = document.getElementById('edit-item-additional-value');
    const itemPrice = parseFloat(itemPriceInput.value) || 0;
    const additionalValue = parseFloat(itemAdditionValue.value) || 0;
    const totalValue = itemPrice + additionalValue; // 计算总价值

    const dailyValueInput = document.getElementById('edit-item-daily-value');
    // 计算日均价格
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 保留两位小数
        dailyValueInput.value = dailyValue + ' 元'; // 更新日均价格显示
    } else {
        dailyValueInput.value = '0.00 元'; // 如果服役天数为0或负数，日均价格为0
    }
}

/**
 * 当购买价格改变时，重新计算服役天数和日均价格。
 * @returns {void}
 */
function onPurchasePriceChange() {
    // 获取相关输入框元素
    const itemEntryDateInput = document.getElementById('edit-item-entry-date');
    const itemRetirementDateInput = document.getElementById('edit-item-retirement-date');
    const itemPurchasePriceInput = document.getElementById('edit-item-purchase-price');
    const itemAdditionValue = document.getElementById('edit-item-additional-value');
    const itemWorkingDaysInput = document.getElementById('edit-item-working-days');
    const itemDailyValueInput = document.getElementById('edit-item-daily-value');

    const entryDateValue = itemEntryDateInput.value;
    // 如果退役日期未填写，则默认为当前日期
    const retirementDateValue = itemRetirementDateInput.value || new Date().toISOString().split('T')[0];
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 计算服役天数
    itemWorkingDaysInput.value = workingDays + ' 天'; // 更新服役天数显示

    const itemPrice = parseFloat(itemPurchasePriceInput.value) || 0;
    const additionalValue = parseFloat(itemAdditionValue.value) || 0;
    const totalValue = itemPrice + additionalValue; // 计算总价值

    // 计算日均价格
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 保留两位小数
        itemDailyValueInput.value = dailyValue + ' 元'; // 更新日均价格显示
    } else {
        itemDailyValueInput.value = '0.00 元'; // 如果服役天数为0或负数，日均价格为0
    }
}

/**
 * 当附加价值改变时，重新计算服役天数和日均价格。
 * @returns {void}
 */
function onAdditionalValueChange() {
    // 获取相关输入框元素
    const itemEntryDateInput = document.getElementById('edit-item-entry-date');
    const itemRetirementDateInput = document.getElementById('edit-item-retirement-date');
    const itemPurchasePriceInput = document.getElementById('edit-item-purchase-price');
    const itemAdditionValue = document.getElementById('edit-item-additional-value');
    const itemWorkingDaysInput = document.getElementById('edit-item-working-days');
    const itemDailyValueInput = document.getElementById('edit-item-daily-value');

    const entryDateValue = itemEntryDateInput.value;
    // 如果退役日期未填写，则默认为当前日期
    const retirementDateValue = itemRetirementDateInput.value || new Date().toISOString().split('T')[0];
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 计算服役天数
    itemWorkingDaysInput.value = workingDays + ' 天'; // 更新服役天数显示

    const itemPrice = parseFloat(itemPurchasePriceInput.value) || 0;
    const additionalValue = parseFloat(itemAdditionValue.value) || 0;
    const totalValue = itemPrice + additionalValue; // 计算总价值

    // 计算日均价格
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 保留两位小数
        itemDailyValueInput.value = dailyValue + ' 元'; // 更新日均价格显示
    } else {
        itemDailyValueInput.value = '0.00 元'; // 如果服役天数为0或负数，日均价格为0
    }
}

/**
 * 当“添加物品”对话框中的入役日期改变时，重新计算服役天数和日均价格。
 * @returns {void}
 */
function onAddEntryDateChange() {
    autoPaddingDatePicker(); // 调整日期选择器样式
    const addItemEntryDateInput = document.getElementById('add-item-entry-date');
    const addItemRetirementDateInput = document.getElementById('add-item-retirement-date');
    const entryDateValue = addItemEntryDateInput.value;
    // 如果退役日期未填写，则默认为当前日期
    const retirementDateValue = addItemRetirementDateInput.value || new Date().toISOString().split('T')[0];
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 计算服役天数
    const workingDaysInput = document.getElementById('add-item-working-days');
    workingDaysInput.value = workingDays + ' 天'; // 更新服役天数显示

    const itemPriceInput = document.getElementById('add-item-purchase-price');
    const itemAdditionValue = document.getElementById('add-item-additional-value');
    const itemPrice = parseFloat(itemPriceInput.value) || 0;
    const additionalValue = parseFloat(itemAdditionValue.value) || 0;
    const totalValue = itemPrice + additionalValue; // 计算总价值

    const dailyValueInput = document.getElementById('add-item-daily-value');
    // 计算日均价格
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 保留两位小数
        dailyValueInput.value = dailyValue + ' 元'; // 更新日均价格显示
    } else {
        dailyValueInput.value = '0.00 元'; // 如果服役天数为0或负数，日均价格为0
    }
}

/**
 * 当“添加物品”对话框中的退役日期改变时，重新计算服役天数和日均价格。
 * @returns {void}
 */
function onAddRetirementDateChange() {
    autoPaddingDatePicker(); // 调整日期选择器样式
    const addItemEntryDateInput = document.getElementById('add-item-entry-date');
    const addItemRetirementDateInput = document.getElementById('add-item-retirement-date');
    const entryDateValue = addItemEntryDateInput.value;
    const retirementDateValue = addItemRetirementDateInput.value;
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 计算服役天数
    const workingDaysInput = document.getElementById('add-item-working-days');
    workingDaysInput.value = workingDays + ' 天'; // 更新服役天数显示

    const itemPriceInput = document.getElementById('add-item-purchase-price');
    const itemAdditionValue = document.getElementById('add-item-additional-value');
    const itemPrice = parseFloat(itemPriceInput.value) || 0;
    const additionalValue = parseFloat(itemAdditionValue.value) || 0;
    const totalValue = itemPrice + additionalValue; // 计算总价值

    const dailyValueInput = document.getElementById('add-item-daily-value');
    // 计算日均价格
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 保留两位小数
        dailyValueInput.value = dailyValue + ' 元'; // 更新日均价格显示
    } else {
        dailyValueInput.value = '0.00 元'; // 如果服役天数为0或负数，日均价格为0
    }
}

/**
 * 当“添加物品”对话框中的购买价格改变时，重新计算服役天数和日均价格。
 * @returns {void}
 */
function onAddPurchasePriceChange() {
    // 获取相关输入框元素
    const addItemEntryDateInput = document.getElementById('add-item-entry-date');
    const addItemRetirementDateInput = document.getElementById('add-item-retirement-date');
    const addItemPurchasePriceInput = document.getElementById('add-item-purchase-price');
    const addItemAdditionValueInput = document.getElementById('add-item-additional-value');
    const addItemWorkingDaysInput = document.getElementById('add-item-working-days');
    const addItemDailyValueInput = document.getElementById('add-item-daily-value');

    const entryDateValue = addItemEntryDateInput.value;
    // 如果退役日期未填写，则默认为当前日期
    const retirementDateValue = addItemRetirementDateInput.value || new Date().toISOString().split('T')[0];
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 计算服役天数
    addItemWorkingDaysInput.value = workingDays + ' 天'; // 更新服役天数显示

    const itemPrice = parseFloat(addItemPurchasePriceInput.value) || 0;
    const additionalValue = parseFloat(addItemAdditionValueInput.value) || 0;
    const totalValue = itemPrice + additionalValue; // 计算总价值

    // 计算日均价格
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 保留两位小数
        addItemDailyValueInput.value = dailyValue + ' 元'; // 更新日均价格显示
    } else {
        addItemDailyValueInput.value = '0.00 元'; // 如果服役天数为0或负数，日均价格为0
    }
}

/**
 * 当“添加物品”对话框中的附加价值改变时，重新计算服役天数和日均价格。
 * @returns {void}
 */
function onAddAdditionalValueChange() {
    // 获取相关输入框元素
    const addItemEntryDateInput = document.getElementById('add-item-entry-date');
    const addItemRetirementDateInput = document.getElementById('add-item-retirement-date');
    const addItemPurchasePriceInput = document.getElementById('add-item-purchase-price');
    const addItemAdditionValueInput = document.getElementById('add-item-additional-value');
    const addItemWorkingDaysInput = document.getElementById('add-item-working-days');
    const addItemDailyValueInput = document.getElementById('add-item-daily-value');

    const entryDateValue = addItemEntryDateInput.value;
    // 如果退役日期未填写，则默认为当前日期
    const retirementDateValue = addItemRetirementDateInput.value || new Date().toISOString().split('T')[0];
    const entryDate = new Date(entryDateValue);
    const retirementDate = new Date(retirementDateValue);
    const timeDiff = retirementDate - entryDate; // 计算时间差（毫秒）
    const workingDays = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)); // 计算服役天数
    addItemWorkingDaysInput.value = workingDays + ' 天'; // 更新服役天数显示

    const itemPrice = parseFloat(addItemPurchasePriceInput.value) || 0;
    const additionalValue = parseFloat(addItemAdditionValueInput.value) || 0;
    const totalValue = itemPrice + additionalValue; // 计算总价值

    // 计算日均价格
    if (workingDays > 0) {
        const dailyValue = (totalValue / workingDays).toFixed(2); // 保留两位小数
        addItemDailyValueInput.value = dailyValue + ' 元'; // 更新日均价格显示
    } else {
        addItemDailyValueInput.value = '0.00 元'; // 如果服役天数为0或负数，日均价格为0
    }
}

/**
 * 自动调整日期选择器标签的填充，以适应不同状态下文本长度的变化。
 * 这是为了解决UI显示问题，当日期输入框有值时，标签可能会变长。
 * @returns {void}
 */
function autoPaddingDatePicker() {
    // 获取编辑和添加物品对话框中的日期输入框元素
    const itemEntryDateInput = document.getElementById('edit-item-entry-date');
    const itemRetirementDateInput = document.getElementById('edit-item-retirement-date');
    const addItemEntryDateInput = document.getElementById('add-item-entry-date');
    const addItemRetirementDateInput = document.getElementById('add-item-retirement-date');

    // 根据输入框是否有值来调整其'label'属性，通过添加空格来调整填充
    if (addItemEntryDateInput.value) {
        addItemEntryDateInput.setAttribute("label", "入役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    } else {
        addItemEntryDateInput.setAttribute("label", "入役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    }
    if (addItemRetirementDateInput.value) {
        addItemRetirementDateInput.setAttribute("label", "退役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    } else {
        addItemRetirementDateInput.setAttribute("label", "退役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    }
    if (itemEntryDateInput.value) {
        itemEntryDateInput.setAttribute("label", "入役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    } else {
        itemEntryDateInput.setAttribute("label", "入役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    }
    if (itemRetirementDateInput.value) {
        itemRetirementDateInput.setAttribute("label", "退役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    } else {
        itemRetirementDateInput.setAttribute("label", "退役日期（YYYY-MM-DD）ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ")
    }
}

/**
 * 添加新物品到列表中。
 * 获取表单输入，进行验证，然后发送POST请求到后端API创建新物品。
 * @returns {void}
 */
function addItem() {
    // 获取所有相关输入框元素
    const itemNameInput = document.getElementById('add-item-name');
    const itemPriceInput = document.getElementById('add-item-purchase-price');
    const itemAdditionValue = document.getElementById('add-item-additional-value');
    const itemEntryDateInput = document.getElementById('add-item-entry-date');
    const itemRetirementDateInput = document.getElementById('add-item-retirement-date');
    const itemDescriptionInput = document.getElementById('add-item-description');

    // 客户端输入验证
    if (!itemNameInput.value || !itemPriceInput.value || !itemEntryDateInput.value) {
        showDialog("错误", "物品名称、购买价格和入役日期不能为空"); // 提示必填项
        return;
    }

    // 构建新物品数据对象
    const newItem = {
        properties: {
            name: itemNameInput.value,
            purchase_price: parseFloat(itemPriceInput.value),
            additional_value: parseFloat(itemAdditionValue.value) || 0, // 如果为空，默认为0
            entry_date: itemEntryDateInput.value,
            retirement_date: itemRetirementDateInput.value || null, // 如果为空，默认为null
            remark: itemDescriptionInput.value || '' // 如果为空，默认为空字符串
        }
    };
    showDialog("正在添加", `请稍候，正在添加物品「${itemNameInput.value}」...`); // 显示添加中提示
    // 发送POST请求到后端API添加物品
    fetch('/api/admin/items', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // 设置请求头为JSON格式
        },
        credentials: 'include', // 确保请求包含cookie
        body: JSON.stringify(newItem) // 发送新物品数据
    }).then(response => {
        // 检查响应是否成功
        if (response.ok) {
            showDialog("成功", "物品添加成功，即将刷新物品列表"); // 显示成功对话框
            return response.json(); // 解析JSON响应
        } else {
            throw new Error('添加物品失败，请稍后再试'); // 抛出错误
        }
    }).then(() => {
        flushItemList(); // 添加成功后刷新物品列表
    }).catch(error => {
        // 捕获并处理添加物品过程中的错误
        console.error('添加物品时出错:', error);
        showDialog("错误", error.message); // 显示错误对话框
    });
}

/**
 * 更改应用的主题强调色。
 * @param {string} color - 要设置的颜色值 (例如 '#RRGGBB' 或 'red')。
 * @param {boolean} [fromRecover=false] - 指示颜色是否是从本地存储恢复的，用于更新颜色选择器UI。
 * @returns {void}
 */
function changeAccentColor(color, fromRecover = false) {
    // 使用sober.theme库创建新的主题方案并应用到页面
    sober.theme.createScheme(color, { page: document.querySelector('s-page') })
    localStorage.setItem('accentColor', color); // 将选中的颜色保存到本地存储
    // 如果是从恢复操作触发的，则更新颜色选择器的值
    if (fromRecover) {
        document.getElementById('color-picker').value = color;
    }
}