/**
 * Radial bar chart
 **/

let metricUpdateTimeout = 1000;

// initialize radial bar chart(configure, render)
function initRadialBarChart(selector, usages) {
    let radialBarChartOption = {
        chart: {
            id: selector,
            height: 260,
            type: "radialBar",
        },
        series: usages,
        colors: ["#20E647"],
        plotOptions: {
            radialBar: {
                startAngle: -135,
                endAngle: 135,
                track: {
                    background: '#252a30',
                    startAngle: -135,
                    endAngle: 135,
                },
                dataLabels: {
                    name: {
                        show: false,
                    },
                    value: {
                        fontSize: "30px",
                        show: true,
                        color: '#fff',
                    }
                }
            }
        },
        fill: {
            colors: [function ({value, seriesIndex, w}) {
                if (value < 55) {
                    return '#00E396';
                } else if (value >= 55 && value < 80) {
                    return '#FF8833';
                } else {
                    return '#FF443B';
                }
            }]
        },
        stroke: {
            lineCap: "butt"
        },
        labels: ["Progress"]
    };

    return new ApexCharts(document.querySelector(selector), radialBarChartOption);
}

// update radial bar chart
function updateRadialBarChart(selector, usages) {
    ApexCharts.exec(selector, 'updateSeries', usages);
}

/**
 * Area chart
 **/

// initialize area bar chart(configure, render)
function initAreaChart(selector, usages) {
    let areaChartOption = {
        chart: {
            id: selector,
            type: 'area',
            height: 200,
            toolbar: {
                show: false
            },
            animations: {
                enabled: false,
            }
        },
        colors: ['#008FFB', '#00E396', '#CED4DC'],
        dataLabels: {
            enabled: false
        },
        stroke: {
            width: 1.5,
            curve: 'smooth'
        },
        fill: {
            type: 'gradient',
            gradient: {
                opacityFrom: 0.6,
                opacityTo: 0.8,
            },
        },
        legend: {
            position: 'bottom',
            horizontalAlign: 'center',
            onItemClick: {
                toggleDataSeries: false,
            },
            onItemHover: {
                highlightDataSeries: false,
            }
        },
        xaxis: {
            type: 'datetime',
            labels: {
                show: true,
                datetimeUTC: false,
            },
        },
        yaxis: {
            show: true,
            tickAmount: 5,
            labels: {
                show: true,
                style: {
                    colors: '#fff',
                }
            }
        },
        tooltip: {
            enabled: false,
        },
    };

    // update init data
    $.each(usages, (i, usage_item) => {
        if (usage_item.length === 0) {
            areaChartOption['noData'] = {
                text: 'Loading...'
            }
        } else {
            areaChartOption['series'] = [
                {
                    name: `TX: 0 Kbps`,
                    data: net_usages['net_tx_usage']
                },
                {
                    name: `RX: 0 Kbps`,
                    data: net_usages['net_rx_usage']
                }
            ]
        }
    });

    return new ApexCharts(document.querySelector(selector), areaChartOption);
}

function initAreaMCNetworkChart(selector, usages) {
    let areaChartOption = {
        chart: {
            id: selector,
            type: 'area',
            height: 230,
            toolbar: {
                show: false
            },
            animations: {
                enabled: false,
            }
        },
        colors: ['#008FFB', '#00E396', '#CED4DC'],
        dataLabels: {
            enabled: false
        },
        stroke: {
            width: 1.5,
            curve: 'smooth'
        },
        fill: {
            type: 'gradient',
            gradient: {
                opacityFrom: 0.6,
                opacityTo: 0.8,
            },
        },
        legend: {
            position: 'bottom',
            horizontalAlign: 'center',
            onItemClick: {
                toggleDataSeries: false,
            },
            onItemHover: {
                highlightDataSeries: false,
            }
        },
        xaxis: {
            type: 'datetime',
            labels: {
                datetimeUTC: false,
            }
        },
        yaxis: {
            show: true,
            tickAmount: 5,
            labels: {
                show: true,
                style: {
                    colors: '#fff',
                }
            }
        },
        tooltip: {
            enabled: false,
        },
    };

    // update init data
    $.each(usages, (i, usage_item) => {
        if (usage_item.length === 0) {
            areaChartOption['noData'] = {
                text: 'Loading...'
            }
        } else {
            areaChartOption['series'] = [
                {
                    name: `TX: 0 Kbps`,
                    data: net_usages['net_tx_usage']
                },
                {
                    name: `RX: 0 Kbps`,
                    data: net_usages['net_rx_usage']
                }
            ]
        }
    });

    return new ApexCharts(document.querySelector(selector), areaChartOption);
}

// update area chart label & data
function updateAreaChart(selector, usages) {
    ApexCharts.exec(selector, 'updateSeries', [
        {
            name: `TX: ${(usages['net_tx_usage'][usages['net_tx_usage'].length - 1][1])} Kbps`,
            data: usages['net_tx_usage']
        },
        {
            name: `RX: ${(usages['net_rx_usage'][usages['net_rx_usage'].length - 1][1])} Kbps`,
            data: usages['net_rx_usage']
        }
    ]);
}

// init area latency chart
function initAreaLatencyChart(selector, latencies) {
    let areaChart2Option = {
        chart: {
            id: selector,
            type: 'area',
            height: 230,
            toolbar: {
                show: false
            },
            animations: {
                enabled: false,
            },
        },
        colors: ['#008FFB', '#00E396', '#CED4DC'],
        dataLabels: {
            enabled: false
        },
        stroke: {
            width: 1.5,
            curve: 'smooth'
        },
        fill: {
            type: 'gradient',
            gradient: {
                opacityFrom: 0.6,
                opacityTo: 0.8,
            },
        },
        legend: {
            position: 'bottom',
            horizontalAlign: 'center',
            onItemClick: {
                toggleDataSeries: false,
            },
            onItemHover: {
                highlightDataSeries: false,
            }
        },
        xaxis: {
            type: 'datetime',
            labels: {
                datetimeUTC: false,
            }
        },
        yaxis: {
            show: true,
            tickAmount: 5,
            labels: {
                show: true,
                style: {
                    colors: '#fff',
                }
            }
        },
        tooltip: {
            enabled: false,
        },
    };

    // update init data
    if (latencies.length === 0) {
        areaChart2Option['noData'] = {
            text: 'Loading...'
        };
    } else {
        areaChart2Option['series'] = [
            {
                name: `Latency: 0 ms`,
                data: latencies
            },
        ];
    }

    return new ApexCharts(document.querySelector(selector), areaChart2Option);
}

// update area chart label & data
function updateAreaLatencyChart(selector, latencies) {
    ApexCharts.exec(selector, 'updateSeries', [
        {
            name: `Latency: ${latencies[latencies.length-1][1]} ms`,
            data: latencies
        },
    ]);
}

/**
 * Data structure for node metric charts
 **/
let _init_data = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0], [8, 0], [9, 0], [10, 0], [11, 0]];
let cpu_usages = [];
let mem_usages = [];
let pod_caps = [];
let net_usages = {
    'net_tx_usage': [],
    'net_rx_usage': []
};

/**
 * Node CPU usage chart(#chart1)
 **/

// initialize node cpu chart
function initNodeCPUChart() {
    let cpuChart;
    clearNodeCPUMetric();
    cpuChart = initRadialBarChart("#chart1", cpu_usages);
    cpuChart.render();
}

// clear node cpu metric data
function clearNodeCPUMetric() {
    cpu_usages = [0];
}

// clear node CPU usage chart
function clearNodeCPUChart() {
    clearNodeCPUMetric();
    updateRadialBarChart("#chart1", cpu_usages);
}

/**
 * Node Memory usage chart(#chart2)
 **/

// initialize memory usage chart
function initNodeMemoryChart() {
    let memChart;
    clearNodeMemoryMetric();
    memChart = initRadialBarChart("#chart2", mem_usages);
    memChart.render();
}

// clear node memory usage metric
function clearNodeMemoryMetric() {
    mem_usages = [0];
}

// clear node memory usage chart
function clearNodeMemoryChart() {
    clearNodeMemoryMetric();
    updateRadialBarChart("#chart2", mem_usages);
}

/**
 * Node Pod capacity chart(#chart2-1)
 **/

// initialize memory usage chart
function initNodeCapacityChart() {
    let memChart;
    clearNodePodCapacityMetric();
    memChart = initRadialBarChart("#chart2-1", pod_caps);
    memChart.render();
}

// clear node memory usage metric
function clearNodePodCapacityMetric() {
    pod_caps = [0];
}

// clear node memory usage chart
function clearNodePodCapacityChart() {
    clearNodePodCapacityMetric();
    updateRadialBarChart("#chart2-1", pod_caps);
}
/**
 * Node Network usage chart(#chart3)
 **/
// initialize node network chart
function initNodeNetworkChart() {
    let netChart;
    clearNodeNetworkMetric();
    netChart = initAreaChart("#chart3", net_usages);
    netChart.render();
}

// clear node network metric
function clearNodeNetworkMetric() {
    net_usages['net_tx_usage'] = _init_data;
    net_usages['net_rx_usage'] = _init_data;
}

// clear node network usage chart
function clearNodeNetworkChart() {
    clearNodeNetworkMetric();
    updateAreaChart("#chart3", net_usages);
}

/**
 * update timer for node metric
 **/
function getNodeMetrics(cluster, node) {
    return $.ajax({
        url: `/api/app/v1/clusters/${cluster}/nodes/${node}/metrics`,
        type: "GET",
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            getNodeMetricsOk = true;
        },
        error: function (error) {
            getNodeMetricsOk = false;
            console.log(error);
        }
    });
}

// update node metric charts
let nodeMetricTimer;
let getNodeMetricsOk = false;

function nodeMetricUpdater() {
    let cluster = getSelectedCluster();
    let node = getSelectedNode();

    if (!cluster || !node) return;

    // update node metric charts
    getNodeMetrics(cluster, node).then((response) => {
        let node = response['nodes'][0];

        if(!node) return;

        let value;

        value = node['cpu_usages'][node['cpu_usages'].length - 1][1];
        cpu_usages = [parseFloat(value.toFixed(2))];
        value = node['mem_usages'][node['mem_usages'].length - 1][1];
        mem_usages = [parseFloat(value.toFixed(2))];
        pod_caps = [node['pods']['usage']];

        let val = [];

        // calculate kbps for net_tx_usage
        for (let i = 0; i < node['net_tx_bytes'].length; i++) {
            if (i === 0) continue;
            let elapsed = node['net_tx_bytes'][i][0] - node['net_tx_bytes'][i - 1][0];
            let bits = (node['net_tx_bytes'][i][1] - node['net_tx_bytes'][i - 1][1]) * 8;
            let kbps = bits / elapsed / 1000;

            val.push([node['net_tx_bytes'][i][0], kbps.toFixed(3)]);
        }

        net_usages['net_tx_usage'] = val;

        val = [];

        // calculate kbps for net_rx_usage
        for (let i = 0; i < node['net_rx_bytes'].length; i++) {
            if (i === 0) continue;
            let elapsed = node['net_rx_bytes'][i][0] - node['net_rx_bytes'][i - 1][0];
            let bits = (node['net_rx_bytes'][i][1] - node['net_rx_bytes'][i - 1][1]) * 8;
            let kbps = bits / elapsed / 1000;

            val.push([node['net_rx_bytes'][i][0], kbps.toFixed(3)]);
        }

        net_usages['net_rx_usage'] = val;
    });

    if (getNodeMetricsOk) {
        // update CPU usage chart for selected node
        updateRadialBarChart("#chart1", cpu_usages);

        // update memory usage chart for selected node
        updateRadialBarChart("#chart2", mem_usages);

        // update pod capacity chart for selected node
        updateRadialBarChart("#chart2-1", pod_caps);

        // update network usage chart for selected node
        updateAreaChart("#chart3", net_usages);
    }
}

function initNodeMetricUpdater() {
    nodeMetricUpdater();

    nodeMetricTimer = setInterval(function () {
        nodeMetricUpdater();
    }, metricUpdateTimeout);
}

/**
 * multi-cluster network metric charts
 **/

/**
 * Data structure for multi-cluster network metric charts
 **/
let mcn_latencies = [];
let mcn_net_usages = {
    'net_tx_usage': [],
    'net_rx_usage': []
};

let mcn_latencies_init = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0], [8, 0], [9, 0], [10, 0], [11, 0]];

/**
 * Multi-cluster Network latency chart(#chart4)
 **/

// initialize mc network latency chart
function initMCNLatencyChart() {
    let mcLatencyChart;

    clearMCNLatencyMetric();
    mcLatencyChart = initAreaLatencyChart("#chart4", mcn_latencies);
    mcLatencyChart.render();
}

// clear mc network latency chart
function clearMCNLatencyMetric() {
    mcn_latencies = mcn_latencies_init;
}

// clear node network usage chart
function clearMCNLatencyChart() {
    clearMCNLatencyMetric();
    updateAreaLatencyChart("#chart4", mcn_latencies);
}

/**
 * Multi-cluster Network Usage chart(#chart5)
 **/
function initMCNetworkChart() {
    let mcNetChart;
    clearMCNetworkMetric();
    mcNetChart = initAreaMCNetworkChart("#chart5", mcn_net_usages);
    mcNetChart.render();
}

// clear mc network latency chart
function clearMCNetworkMetric() {
    mcn_net_usages['net_tx_usage'] = _init_data;
    mcn_net_usages['net_rx_usage'] = _init_data;
}

// clear node network usage chart
function clearMCNetworkChart() {
    clearMCNetworkMetric();
    updateAreaChart("#chart5", mcn_net_usages);
}

// get multi-cluster network latency metric
function getMCNMetrics(cluster, endpoint) {
    return $.ajax({
        url: `/api/app/v1/clusters/${cluster}/mc/${endpoint}/metrics`,
        type: "GET",
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
        },
        error: function (error) {
            console.log(error);
        }
    });
}

let mcnMetricTimer;

function MCNMetricUpdater() {
    let cluster = getSelectedCluster();
    let endpoint = getSelectedClusterEndpoint();
    let mcnStatus = getSelectedClusterMCNStatus();

    if (!cluster || !endpoint || mcnStatus !== 'Connected') return;

    getMCNMetrics(cluster, endpoint).then((response) => {
        // console.log(response);
        let val = [];
        let update = true;

        if (!response['tx_bytes']) update = false;
        else {
            // calculate kbps for net_tx_usages
            for (let i = 0; i < response['tx_bytes'].length; i++) {
                if (i === 0) continue;
                let elapsed = response['tx_bytes'][i][0] - response['tx_bytes'][i - 1][0];
                let bits = (response['tx_bytes'][i][1] - response['tx_bytes'][i - 1][1]) * 8;
                let kbps = bits / elapsed / 1000;
                if (kbps < 0) {
                    kbps *= -1;
                }

                val.push([response['tx_bytes'][i][0], kbps.toFixed(3)]);
            }
            mcn_net_usages['net_tx_usage'] = val;
        }

        val = [];

        if (!response['tx_bytes']) update = false;
        else {
            // calculate kbps for net_tx_usages
            for (let i = 0; i < response['rx_bytes'].length; i++) {
                if (i === 0) continue;
                let elapsed = response['rx_bytes'][i][0] - response['rx_bytes'][i - 1][0];
                let bits = (response['rx_bytes'][i][1] - response['rx_bytes'][i - 1][1]) * 8;
                let kbps = bits / elapsed / 1000;
                if (kbps < 0) {
                    kbps *= -1;
                }

                val.push([response['rx_bytes'][i][0], kbps.toFixed(3)]);
            }
            mcn_net_usages['net_rx_usage'] = val;
        }

        if (update)
            // update MCN network usage chart
            updateAreaChart("#chart5", mcn_net_usages);

        val = [];
        if (response['latencies']) {
            for (let i = 0; i < response['latencies'].length; i++) {
                val.push([response['latencies'][i][0], response['latencies'][i][1].toFixed(3)]);
            }
            mcn_latencies = val;
            updateAreaLatencyChart("#chart4", mcn_latencies);

        }
    });
}
function initMCNMetricUpdater() {
    MCNMetricUpdater();

    mcnMetricTimer = setInterval(function () {
        MCNMetricUpdater();
    }, metricUpdateTimeout);
}
