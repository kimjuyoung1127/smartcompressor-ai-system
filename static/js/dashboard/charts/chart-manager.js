// static/js/dashboard/charts/chart-manager.js
import { EnergyChart } from './energy-chart.js';
import { DeviceStatusChart } from './device-status-chart.js';
import { TemperatureChart } from './temperature-chart.js';
import { VibrationChart } from './vibration-chart.js';
import { PowerChart } from './power-chart.js';
import { AnomalyChart } from './anomaly-chart.js';

class ChartManager {
    constructor() {
        this.charts = {};
    }

    initializeAllCharts() {
        this.charts.energy = new EnergyChart('energyChart');
        this.charts.deviceStatus = new DeviceStatusChart('deviceStatusChart');
        this.charts.temperature = new TemperatureChart('temperatureChart');
        this.charts.vibration = new VibrationChart('vibrationChart');
        this.charts.power = new PowerChart('powerChart');
        this.charts.anomaly = new AnomalyChart('anomalyChart');
    }
}

export { ChartManager };