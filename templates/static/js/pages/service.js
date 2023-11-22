$(document).ready(() => {
    /**
     * window load event handler
     */

    let cluster = getSelectedClusterFromCookie();
    let namespace = getSelectedNamespaceFromCookie();

    if (cluster && namespace) {
        $("#service-list tr:first-child input[type=radio]").prop('checked', true);
        refreshServiceDetail();
    } else {
        clearServiceList();
        resetServiceDetails();
    }

    initClusterAndNamespaceListUpdater();
    initServiceListUpdater();

});

let serviceListUpdateTimer;
let prevSelectedService;
let prevSelectedPod;

// initialize service list updater
// update service list (period=3s)
function initServiceListUpdater() {
    serviceListUpdateTimer = setInterval(function () {
        let cluster = getSelectedClusterFromCookie();
        let namespace = getSelectedNamespaceFromCookie();

        if(!cluster || !namespace) {
            clearServiceList();
            resetServiceDetails();
        }

        // update service list
        refreshServiceList(cluster, namespace);
        console.log('service list are updated.');
    }, 5000);
}

$(document).on('change', '#migrate-cluster-list', function () {
    let selectedClusterName = $("#migrate-cluster-list option:selected").html();
    getNodeList(selectedClusterName);
});

// when click a service in the service list,
// get service name
$(document).on('click', '#service-list tr', function () {
    if ($(this).has('.label-name').length !== 0) {
        selectRadioBtn($(this));

        let serviceName = $(this).find(".label-name").text();

        if (isEmpty(serviceName)) {
            resetServiceDetails();
            return;
        }
        selectServiceName(serviceName);
    }
});

// pod click event
$(document).on('click', '#pod-list tr', function () {
    if ($(this).has('.label-name').length !== 0) {
        selectRadioBtn($(this));

        let pod = getSelectedPod();

        prevSelectedPod = pod;

        setModal("#delete-modal-pod", pod);
        setMigrateModalPod(pod);
    }
});

// refresh service list
function refreshServiceList(cluster, namespace) {
    getServiceList(cluster, namespace);

    let service = getSelectedService();

    if (isEmpty(service)) {
        resetServiceDetails();
        return;
    }

    selectServiceName(service);
}

// refresh service detail
function refreshServiceDetail() {
    let service = getSelectedService();

    if (isEmpty(service)) {
        resetServiceDetails();
        return;
    }

    selectServiceName(service);
}

// reset service details when selected service is unavailable
function resetServiceDetails() {
    clearServiceDetail();
    clearSelectedServiceName();
    clearPodList();
    clearSelectedPodName();
    clearServicePorts();
    clearServiceExport();
}

// select service name
function selectServiceName(service) {
    let cluster = $("#selected-cluster-name").text();
    let namespace = getSelectedServiceNamespace();

    prevSelectedService = service;

    getServiceDetail(cluster, namespace, service);
    getPodList(cluster, namespace, service);

    setModal("#delete-modal-service", service);
    setModal("#export-modal-service", cluster);
    setModal("#unexport-modal-service", cluster);

    let pod = getSelectedPod();
    prevSelectedPod = pod;

    if (!pod) {
        clearSelectedPodName();
        return;
    }

    setModal("#delete-modal-pod", pod);
    setMigrateModalPod(pod);
}

function setModal(modalType, name) {
    let tag = $(`${modalType} .modal-body-emphasis`);

    tag.html("");
    tag.html(name);
}

function setMigrateModalPod(pod) {
    let tag = $("#migrate-modal-pod #recipient-name");

    tag.attr("value", "");
    tag.attr("value", pod);
}

// clear service list
function clearServiceList() {
    let serviceList = $("#service-list");
    let numberOfNullRecords = defaultNumberOfListViewRecord;
    let nullRecordHtml = `<tr><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/></tr>`;

    serviceList.html("");

    // fill null records
    for (let i = 0; i < numberOfNullRecords; i++) {
        serviceList.append(nullRecordHtml);
    }
}

// clear service detail
function clearServiceDetail() {
    let selectedService = $('#selected-service');
    selectedService.html("");
    selectedService.html(`
        <h2>Service:
            <span id="selected-service-name" class="selected-name"></span>
            <span id="selected-service-state" data-state="unknown"
                  class="label-common label-unavailable">Unavailable</span>
        </h2>
        <div class="selected-info">
            <p>Namespace: <span id="selected-service-namespace-name">None</span></p>
            <p>Type: <span id="selected-service-type">None</span></p>
            <p>Cluster IP: <span id="selected-service-cluster-ip">None</span></p>
            <p>Selector: <span id="selected-service-selector">None</span></p>
        </div>        
    `);
}

// clear selected pod name
function clearSelectedPodName() {
    setModal("#delete-modal-pod", "");
    $("#migrate-modal-pod #recipient-name").attr("value", "");
    setMigrateModalPod("");
}

function clearSelectedServiceName() {
    setModal("#delete-modal-service", "");
}

// clear pod list
function clearPodList() {
    let podList = $("#pod-list");
    let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/></tr>';
    let numberOfNullRecord = defaultNumberOfListViewRecord;

    podList.html("");

    // fill null records
    for(let i=0; i < numberOfNullRecord; i++) {
        podList.append(nullRecordHtml);
    }
}

// clear service export table
function clearServiceExport() {
    let serviceExport = $("selected-service-service-export-list");
    serviceExport.html(`
    <tr>
        <td/>
        <td><span class="label-common label-unavailable">Unavailable</span></td>
        <td/>
        <td/>
    </tr>`);
}

// clear service port table
function clearServicePorts() {
    let portList = $("#selected-service-port-list");
    let numberOfNullRecord = defaultNumberOfListViewRecord;
    let nullRecordHtml = '<tr><td/><td/><td/><td/><td/></tr>';

    portList.html("");

    // fill null records
    for (let i = 0; i < numberOfNullRecord; i++) {
        portList.append(nullRecordHtml);
    }
}

// get services from gwlink-manager server
function getServiceList(clusterName, namespaceName) {
    if(!clusterName || !namespaceName) {
        clearServiceList();
        return;
    }

    $.ajax({
        url: "/api/app/v1/clusters/" + clusterName + "/namespaces/" + namespaceName + "/services",
        type: "GET",
        async: false,
        success: function (response) {
            let serviceList = $("#service-list");
            let serviceLength = response.services.length;
            let numberOfNullRecords = defaultNumberOfListViewRecord;
            let nullRecordHtml = `<tr><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/></tr>`;

            serviceList.html("");
            numberOfNullRecords = numberOfNullRecords - serviceLength;

            if (!hasElement(response.services)) {
                clearServiceList();
                return;
            }

            if (response.services) {
                for (const service of response.services) {
                    // port
                    let portValue = "";
                    let externalIpsValue = service.external_ips.join(" ");

                    for (const port of service.ports) {
                        if (!port.node_port) {
                            portValue += port.port + '/' + port.protocol + ' ' + port.target_port + '<br>';
                        } else {
                            portValue += port.node_port + ':' + port.port + '/' + ' ' + port.target_port + '<br>';
                        }
                    }

                    if (!service.service_export.target) {
                        service.service_export.target = '';
                    }

                    if (!service.age) {
                        service.age = '';
                    }
                    let serviceExportStatus = 'Unavailable';

                    if (service.service_export.status === 'true') {
                        serviceExportStatus = 'Active';
                    }

                    if (!service.cluster_ip || service.cluster_ip === 'None') {
                        service.cluster_ip = '';
                    }

                    serviceList.append(`
                        <tr>
                            <td><input type="radio" class="form-check-input"></td>
                            <td><span class="label-common label-${service.state.toLowerCase()}">${service.state}</span></td>
                            <td width="15%"><a href="#" class="label-name service-name">${service.name}</a></td>
                            <td>${service.namespace}</td>
                            <td>${service.service_type}</td>
                            <td>${service.cluster_ip}</td>
                            <td>${externalIpsValue}</td>
                            <td>${portValue}</td>
                            <td>${service.age}</td>
                            <td>${service.service_export.target}</td>
                            <td><span class="label-common label-${serviceExportStatus.toLowerCase()}"> ${serviceExportStatus}</span></td>
                        </tr>`);
                }
                for (let i = 0; i < numberOfNullRecords; i++) {
                    serviceList.append(nullRecordHtml);
                }

                if (prevSelectedService && isExistService(prevSelectedService)) {
                    // check prevSelectedService is in update service list
                    selectServiceButton(prevSelectedService);
                    return;
                }

                $("#service-list  tr:first-child input[type=radio]").prop('checked', true);
                prevSelectedService = getSelectedService();
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function getServiceDetail(clusterName, namespaceName, serviceName) {

    $.ajax({
        url: "/api/app/v1/clusters/" + clusterName + "/namespaces/" + namespaceName + "/services/" + serviceName,
        type: "GET",
        async: false,
        success: function (response) {
            // Service Title Group
            let selectedService = $("#selected-service");
            selectedService.html("");

            if (!hasElement(response.services)) {
                clearServiceDetail();
                clearServicePorts();
                clearServiceExport();
                return;
            }

            let service = response.services[0];

            // selected service
            selectedService.html(
                `
                <h2>Service:
                    <span id="selected-service-name" class="selected-name">${service.name}</span>
                    <span id="selected-service-state" data-state="unknown"
                          class="label-common label-${service.state.toLowerCase()}">${service.state}</span>
                </h2>
                <div class="selected-info">
                    <p>Namespace: <span id="selected-service-namespace-name">${service.namespace}</span></p>
                    <p>Type: <span id="selected-service-type">${service.service_type}</span></p>
                    <p>Cluster IP: <span id="selected-service-cluster-ip">${service.cluster_ip}</span></p>
                    <p>Selector: <span id="selected-service-selector">${service.selector.join(" ")}</span></p>
                </div>                
                `
            )
            // service ports tab
            let portList = $("#selected-service-port-list");
            let portLength = service.ports.length;
            let numberOfNullRecord = defaultNumberOfListViewRecord;
            let nullRecordHtml = '<tr><td/><td/><td/><td/><td/></tr>';

            portList.html("");
            numberOfNullRecord = numberOfNullRecord - portLength;

            for (let port of service.ports) {
                portList.append(`
                <tr>
                    <td><a href="#port" class="label-name selected-service-port-name">${port.name}</a></td>
                    <td> ${port.port} </td>
                    <td> ${port.protocol} </td>
                    <td> ${port.target_port} </td>
                    <td> ${port.node_port} </td>
                </tr>
                `);
            }
            // fill null records
            for (let i = 0; i < numberOfNullRecord; i++) {
                portList.append(nullRecordHtml);
            }

            // service export tab
            let serviceExport = $("#selected-service-service-export-list");
            let serviceExportStatus = 'Unavailable';

            if (service.service_export.status === 'true') {
                serviceExportStatus = 'Active'
            }

            serviceExport.html(`
                <tr>
                    <td>${service.service_export.target}</td>
                    <td><span class="label-common label-${service.service_export.status.toLowerCase()}">${serviceExportStatus}</span></td>
                    <td>${service.service_export.reason}</td>
                    <td>${service.service_export.clusterset_ip}</td>
                    <td>${service.service_export.service_discovery}</td>                
                </tr>`);
        },
        error: function (error) {
            console.log(error);
        }
    })
}

function getPodList(clusterName, namespaceName, serviceName) {
    $.ajax({
        url: "/api/app/v1/clusters/" + clusterName + "/namespaces/" + namespaceName + "/pods?service=" + serviceName,
        type: "GET",
        async: false,
        success: function (response) {
            let podList = $("#pod-list")
            let podLength = response.pods.length;
            let numberOfNullRecord = defaultNumberOfListViewRecord;
            let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/></tr>';

            podList.html("");
            numberOfNullRecord = numberOfNullRecord - podLength;

            if (!hasElement(response.pods)) {
                clearPodList();
                return;
            }

            for (let i = 0; i < response.pods.length; i++) {
                let pod = response.pods[i];
                let namespace = "";
                let ip = "";
                let node = "";
                let age = "";

                if(pod.namespace) {
                    namespace = pod.namespace;
                }
                if(pod.node) {
                    node = pod.node;
                }
                if(pod.pod_ip) {
                    ip = pod.pod_ip;
                }
                if(pod.age) {
                    age = pod.age;
                }

                podList.append(`
                    <tr>
	                    <td><input type="radio" class="form-check-input"></td>
	                    <td><span class="label-common label-${pod.state.toLowerCase()}">${pod.state}</span></td>
	                    <td width="20%"><a href="#" id="label-name-${i}" class="label-name">${pod.name}</a></td>
	                    <td>${namespace}</td>
	                    <td>${ip}</td>
	                    <td>${node}</td>
	                    <td>${age}</td>
	                </tr>`);
            }
            // fill null records
            for (let i = 0; i < numberOfNullRecord; i++) {
                podList.append(nullRecordHtml);
            }

            if (prevSelectedPod && isExistPod(prevSelectedPod)) {
                // check prevSelectedPod is in update pod list
                selectPodButton(prevSelectedPod);
                return;
            }

            $("#pod-list  tr:first-child input[type=radio]").prop('checked', true);
            prevSelectedPod = getSelectedPod();
        },
        error: function (error) {
            console.log(error);
        }
    })
}

// reload page
function reloadPage() {
    reloadServiceList();
}

// reload service list
function reloadServiceList() {
    let cluster = getSelectedClusterFromCookie();
    let namespace = getSelectedNamespaceFromCookie();

    if (!cluster || !namespace) {
        clearServiceList();
        resetServiceDetails();
    }

    // update service list
    refreshServiceList(cluster, namespace);
}
