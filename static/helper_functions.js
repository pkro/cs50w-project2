function qs(selector) {
    return document.querySelector(selector);
}

function qsa(selector) {
    return document.querySelectorAll(selector);
}

function onPageLoad(func) {
    document.addEventListener('DOMContentLoaded', func);
}