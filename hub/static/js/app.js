(function () {
    'use strict';

    function ready(fn) {
        if (document.readyState !== 'loading') {
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    }

    ready(function () {
        const flash = document.querySelector('[data-flash]');

        function setFlash(message, level = 'info') {
            if (!flash) {
                return;
            }
            flash.textContent = message;
            flash.classList.remove('error', 'success');
            if (level === 'error') {
                flash.classList.add('error');
            } else if (level === 'success') {
                flash.classList.add('success');
            }
            flash.style.display = message ? 'block' : 'none';
        }

        async function submitApiForm(event) {
            event.preventDefault();
            const form = event.currentTarget;
            const endpoint = form.dataset.api;
            if (!endpoint) {
                setFlash('Missing API endpoint.', 'error');
                return;
            }

            const method = (form.dataset.method || form.method || 'post').toUpperCase();
            const booleanFields = extractCsv(form.dataset.booleans);
            const jsonFields = extractCsv(form.dataset.jsonFields);
            const wrapKey = form.dataset.wrap || null;

            const formData = new FormData(form);
            const payload = {};

            formData.forEach((value, key) => {
                if (value === null || value === undefined || value === '') {
                    return;
                }
                if (jsonFields.includes(key)) {
                    try {
                        payload[key] = value ? JSON.parse(value) : {};
                    } catch (_error) {
                        setFlash(`Invalid JSON provided for ${key}.`, 'error');
                        payload[key] = {};
                    }
                    return;
                }
                if (booleanFields.includes(key)) {
                    payload[key] = value === 'true' || value === 'on' || value === '1';
                    return;
                }
                payload[key] = value;
            });

            booleanFields.forEach((field) => {
                if (!(field in payload)) {
                    payload[field] = false;
                }
            });

            const body = wrapKey ? { [wrapKey]: payload } : payload;

            try {
                const response = await fetch(endpoint, {
                    method,
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: method === 'GET' ? undefined : JSON.stringify(body)
                });

                if (!response.ok) {
                    const text = await response.text();
                    setFlash(text || 'Request failed.', 'error');
                    return;
                }

                const contentType = response.headers.get('content-type') || '';
                if (contentType.includes('application/json')) {
                    const data = await response.json();
                    setFlash('Request completed.', 'success');
                    if (form.dataset.refresh === 'true') {
                        window.location.reload();
                    } else if (form.dataset.clear === 'true') {
                        form.reset();
                    }
                    if (form.dataset.messageField && data[form.dataset.messageField]) {
                        setFlash(String(data[form.dataset.messageField]), 'success');
                    }
                } else {
                    setFlash('Request completed.', 'success');
                }
            } catch (error) {
                setFlash('Network error while contacting the hub.', 'error');
                // eslint-disable-next-line no-console
                console.error(error);
            }
        }

        function extractCsv(value) {
            if (!value) {
                return [];
            }
            return value
                .split(',')
                .map((item) => item.trim())
                .filter(Boolean);
        }

        document.querySelectorAll('form[data-api]').forEach((form) => {
            form.addEventListener('submit', submitApiForm);
        });

        document.querySelectorAll('button[data-reboot]').forEach((button) => {
            button.addEventListener('click', () => {
                const nodeId = button.dataset.reboot;
                setFlash(`Reboot command queued for ${nodeId} (placeholder).`, 'success');
            });
        });
    });
})();
