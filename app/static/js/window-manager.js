// Window Management
let highestZIndex = 2000;

function bringToFront(modalIdOrElement) {
    let modal;
    if (typeof modalIdOrElement === 'string') {
        modal = document.getElementById(modalIdOrElement);
    } else if (modalIdOrElement instanceof HTMLElement) {
        modal = modalIdOrElement.closest('.modal');
    }

    if (!modal) return;

    highestZIndex++;
    modal.style.zIndex = highestZIndex;

    document.querySelectorAll('.modal-content').forEach(el => {
        el.classList.remove('active');
    });

    const content = modal.querySelector('.modal-content');
    if (content) {
        content.classList.add('active');
    }
}

function toggleMaximize(target) {
    let modal;
    let icon;

    if (typeof target === 'string') {
        modal = document.getElementById(target);
        if (modal) {
            icon = modal.querySelector('.maximize i');
        }
    } else if (target instanceof HTMLElement) {
        modal = target.closest('.modal');
        icon = target.querySelector('i');
    }

    if (!modal) return;

    const content = modal.querySelector('.modal-content');
    if (!content) return;

    if (content.classList.contains('maximized')) {
        // Restore
        content.classList.remove('maximized');
        if (icon) {
            icon.classList.remove('fa-window-restore');
            icon.classList.add('fa-square');
            icon.classList.add('fa-regular');
            icon.classList.remove('fa-solid');
        }
    } else {
        // Maximize
        content.classList.remove('minimized');
        content.classList.add('maximized');
        if (icon) {
            icon.classList.remove('fa-square');
            icon.classList.remove('fa-regular');
            icon.classList.add('fa-window-restore');
            icon.classList.add('fa-solid');
        }
    }
    bringToFront(modal);
}

function toggleMinimize(target) {
    let modal;
    if (typeof target === 'string') {
        modal = document.getElementById(target);
    } else if (target instanceof HTMLElement) {
        modal = target.closest('.modal');
    }

    if (!modal) return;

    const content = modal.querySelector('.modal-content');
    if (!content) return;

    if (content.classList.contains('minimized')) {
        // Restore
        content.classList.remove('minimized');
        bringToFront(modal);
    } else {
        // Minimize
        content.classList.remove('maximized');
        content.classList.add('minimized');
    }
}

// Initialize z-index behavior for all modals
document.addEventListener('DOMContentLoaded', () => {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        const content = modal.querySelector('.modal-content');
        if (content) {
            content.addEventListener('mousedown', () => {
                bringToFront(modal);
            });
        }
    });
});
