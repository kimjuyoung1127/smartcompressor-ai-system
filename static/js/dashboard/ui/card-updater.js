// static/js/dashboard/ui/card-updater.js
class CardUpdater {
    constructor() {
        // 초기화
    }
    updateOverviewCards(summary) {
        if (summary.overview) {
            const totalStoresEl = document.getElementById('totalStores');
            const onlineDevicesEl = document.getElementById('onlineDevices');
            const warningAlertsEl = document.getElementById('warningAlerts');
            const energyCostEl = document.getElementById('energyCost');

            if (totalStoresEl) totalStoresEl.textContent = summary.overview.total_stores || 0;
            if (onlineDevicesEl) onlineDevicesEl.textContent = summary.overview.online_compressors || 0;
            if (warningAlertsEl) warningAlertsEl.textContent = summary.overview.warning_alerts || 0;
            if (energyCostEl) energyCostEl.textContent = `₩${(summary.overview.total_energy_cost || 0).toLocaleString()}`;
        }
    }
}

// Export for ES modules
export { CardUpdater };