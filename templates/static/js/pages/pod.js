// window load event
$(document).ready(() => {
    /**
     * window load event handler
     */
    let cluster = getSelectedClusterFromCookie();
    let namespace = getSelectedNamespaceFromCookie();

    if (cluster && namespace) {
        $("#pod-list tr:first-child input[type=radio]").prop('checked', true);
        refreshPodDetail();
    } else{
        clearPodList();
        resetPodDetails();
    }

    initClusterAndNamespaceListUpdater();
    initPodListUpdater();
});

let podListUpdateTimer;
let prevSelectedPod;
let prevSelectedService;

// initialize pod list updater
// update pod list (period=5s)
function initPodListUpdater() {
    podListUpdateTimer = setInterval(function () {
        let cluster = getSelectedClusterFromCookie();
        let namespace = getSelectedNamespaceFromCookie();

        if(!cluster || !namespace) {
            clearPodList();
            resetPodDetails();
            return;
        }

        // update pod list
        refreshPodList(cluster, namespace);
        console.log('pod list are updated.');
    }, 5000);
}

// service-list click event
$(document).on('click', '#service-list tr', function () {
    if ($(this).has('.label-name').length !== 0) {
        selectRadioBtn($(this));

        let cluster = $("#selected-cluster-name").text();
        let service = getSelectedService();

        prevSelectedService = service;

        setModal("#delete-modal-service", service);
        setModal("#export-modal-service", cluster);
        setModal("#unexport-modal-service", cluster);
    }
});

// pod-list click event
$(document).on('click', '#pod-list tr', function () {
    if ($(this).has('.label-name').length !== 0) {
        selectRadioBtn($(this));

        let pod = getSelectedPod();
        prevSelectedPod = pod;

        if (isEmpty(pod)) {
            resetPodDetails();
            prevSelectedPod = "";
            return;
        }

        selectPodName(pod);
    }
});

function resetPodDetails() {
    clearPodDetail();
    clearSelectedPodName();
    clearServiceList();
    clearSelectedServiceName();
    clearDeploymentList();
    clearSelectedDeploymentName();
    clearDaemonSetList();
    clearSelectedDaemonSetName();
}

// refresh pod list
function refreshPodList(cluster, namespace) {
    // get pod list from server
    getPodList(cluster, namespace);

    // select first pod
    let pod = getSelectedPod();

    if (isEmpty(pod)) {
        resetPodDetails();
        return;
    }

    selectPodName(pod);
}

// refresh pod detail
function refreshPodDetail() {
    let pod = getSelectedPod();

    if (isEmpty(pod)) {
        resetPodDetails();
        return;
    }

    selectPodName(pod);
}

// if pod is clicked in table,
function selectPodName(pod) {
    let cluster = $("#selected-cluster-name").text();
    let namespace = getSelectedPodNamespace();
    prevSelectedPod = pod;

    getPodDetail(cluster, namespace, pod);
    getServiceList(cluster, namespace, pod);

    let service = getSelectedService();
    prevSelectedService = service;

    getDeploymentList(cluster, namespace, pod);
    getDaemonsetList(cluster, namespace, pod);

    setMigrateModalPod(pod);
    setModal("#delete-modal-pod", pod);
    setModal("#delete-modal-service", service);
    setModal("#export-modal-service", cluster);
    $('#export-service').innerText = service;
    setModal("#export-service", cluster);
    setModal("#unexport-modal-service", cluster);
}

function setModal(modalType, name) {
    let model = $(`${modalType} .modal-body-emphasis`);
    model.html("");
    model.html(name);
}

function setMigrateModalPod(pod_name) {
    let migrateModelPod = $("#migrate-modal-pod #recipient-name");
    migrateModelPod.attr("value", "");
    migrateModelPod.attr("value", pod_name);
}

// Pod related functions
function getPodList(cluster, namespace) {
    $.ajax({
        type: "GET",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/pods`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let podList = $("#pod-list");
            let podLength = response.pods.length;
            let numberOfNullRecords = defaultNumberOfListViewRecord;
            let nullRecordHtml = `<tr><td/><td/><td/><td/><td/><td/><td/><td/></tr>`;

            podList.html("");
            numberOfNullRecords = numberOfNullRecords - podLength;

            if (response.pods) {
                for (const pod of response.pods) {
                    let namespace = "";
                    let ip = "";
                    let node = "";
                    let age = "";

                    if (pod.namespace) {
                        namespace = pod.namespace;
                    }
                    if (pod.node) {
                        node = pod.node;
                    }
                    if (pod.pod_ip) {
                        ip = pod.pod_ip;
                    }
                    if (pod.age) {
                        age = pod.age;
                    }
                    podList.append(`
                        <tr>
                           <td><input type="radio" class="form-check-input"></td>
                           <td><span class="label-common label-${pod.state.toLowerCase()}">${pod.state}</span></td>
                           <td width="30%">
                            <a href="#" class="label-name">${pod.name}</a>
                           </td>
                           <td>${namespace}</td>
                           <td>${ip}</td>
                           <td>${node}</td>
                           <td>${age}</td>
                           <td/>
                        </tr>
                        `
                    );
                }
            }
            for (let i = 0; i < numberOfNullRecords; i++) {
                podList.append(nullRecordHtml);
            }
            if (prevSelectedPod && isExistPod(prevSelectedPod)) {
                // check prevSelectedPod is in update pod list
                selectPodButton(prevSelectedPod);
                return;
            }

            $("#pod-list tr:first-child input[type=radio]").prop('checked', true);
            prevSelectedPod = getSelectedPod();
        },
        error: function (error) {
            // showErrorModal(error);
            console.log(error);
        }
    });
}

// clear pod list
function clearPodList() {
    let podList = $("#pod-list");
    let numberOfNullRecords = defaultNumberOfListViewRecord;
    let nullRecordHtml = `<tr><td/><td/><td/><td/><td/><td/><td/><td/></tr>`;
    podList.html("");

    for (let i = 0; i < numberOfNullRecords; i++) {
        podList.append(nullRecordHtml);
    }
}

function clearPodDetail() {
    let selectedPod = $("#selected-pod");
    selectedPod.html("");
    selectedPod.html(
        `
                <h2> Pod:
                    <span class="selected-name"></span>
                    <span class="label-common label-unavailable">unavailable</span>
                </h2>
        
                <div class="selected-info">
                    <p>Namespace: <span id="selected-pod-namespace">None</span></p>
                    <p>Pod IP: <span id="selected-pod-ip">None</span></p>
                    <p>Labels: <span id="selected-pod-label">None</span></p>
                </div>`
    );
    clearPodConditions();
}

function clearServiceList() {
    let serviceList = $("#service-list");
    let numberOfNullRecord = defaultNumberOfListViewRecord;

    serviceList.html("");
    let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/></tr>';

    // fill null records
    for(let i=0; i < numberOfNullRecord; i++) {
        serviceList.append(nullRecordHtml);
    }
}

function clearSelectedPodName() {
    setModal("#delete-modal-pod", "");
    $("#migrate-modal-pod #recipient-name").attr("value", "");
}

function clearSelectedServiceName() {
    setModal("#delete-modal-service", "");
    setModal("#export-modal-service", "");
    $('#export-service').innerText = "";
    setModal("#unexport-modal-service", "");
}

// clear selected deployment name
function clearSelectedDeploymentName() {
    setModal("#delete-modal-deployment", "");
}

// clear selected daemonset name
function clearSelectedDaemonSetName() {
    setModal("#delete-modal-daemonset", "");
}

function clearDeploymentList() {
    let deploymentList = $("#deployment-list");
    let selectedDeployName = $("#selected-deployment-name");
    selectedDeployName.text("None");

    deploymentList.html(`
              <tr>
                <td>
                  <span class="label-common label-unavailable">Unavailable</span>
                </td>
                <td/><td/><td/><td/><td/>
              </tr>`);
}

function clearDaemonSetList() {
    let daemonsetList = $('#daemonset-list');
    daemonsetList.html(`
              <tr>
                <td>
                  <span class="label-common label-unavailable">Unavailable</span>
                </td>
                <td/><td/><td/>
              </tr>`);
}

function clearPodConditions() {
    let podConditions = $("#pod-conditions");
    let numberOfNullRecords = defaultNumberOfListViewRecord;
    let nullRecordHtml = '<tr><td width="2%"/><td width="20%"/><td/><td/><td/></tr>';
    podConditions.html("");

    for (let i = 0; i < numberOfNullRecords; i++) {
        podConditions.append(nullRecordHtml);
    }
}

function getPodDetail(cluster, namespace, pod_name) {
    $.ajax({
        type: "GET",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/pods/${pod_name}`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let selectedPod = $("#selected-pod")
            selectedPod.html("");

            if (!hasElement(response.pods)) {
                clearPodDetail();
                return;
            }

            let pod = response.pods[0];
            selectedPod.html(
                `
                <h2>Pod:
                    <span class="selected-name">${pod.name || ""}</span>
                    <span class="label-common label-${pod.state.toLowerCase() || ""}">${pod.state || ""}</span>
                </h2>
                <div class="selected-info">
                    <p>Namespace: <span>${pod.namespace || ""}</span></p>
                    <p>Pod IP: <span>${pod.pod_ip || ""}</span></p>
                    <p>Labels: <span>${pod.labels || ""}</span></p>
                </div>
                `
            );

            let podConditions = $("#pod-conditions");
            let podConditionLength = pod.conditions.length;
            let numberOfNullRecords = defaultNumberOfListViewRecord;
            let nullRecordHtml = '<tr><td width="2%"/><td width="20%"/><td/><td/><td/></tr>';
            numberOfNullRecords = numberOfNullRecords - podConditionLength;

            podConditions.html("");

            for (const condition of pod.conditions) {
                podConditions.append(
                    `
                    <tr>
                        <td width="2%"></td>
	                    <td width="10%">${condition.condition}</td>
	                    <td>${condition.status}</td>
	                    <td>${condition.updated}</td>
	                    <td>${condition.message}</td>
	                </tr>
                    `
                );
            }
            for (let i = 0; i < numberOfNullRecords; i++) {
                podConditions.append(nullRecordHtml);
            }
        },
        error: function (error) {
            console.log(error);
        },
    });
}

// Service related functions
function getServiceList(cluster, namespace, pod_name) {
    $.ajax({
        type: "GET",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/services?pod=${pod_name}`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let serviceList = $("#service-list");
            let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/></tr>';
            let numberOfNullRecord = defaultNumberOfListViewRecord;
            numberOfNullRecord = numberOfNullRecord - response.services.length;

            serviceList.html("");

            if (!hasElement(response.services)) {
                clearServiceList();
                return;
            }

            for (let i = 0; i < response.services.length; i++) {
                let service = response.services[i];
                let portContents = '';

                $.each(service.ports, (i, port) => {
                    if (isEmpty(port.node_port)) {
                        portContents +=
                            port.port + '/' + port.protocol + ' ' + port.target_port + '<br>';
                    } else {
                        portContents +=
                            port.node_port + ':' + port.port + '/' + port.protocol + ' ' + port.target_port + '<br>';
                    }
                });

                if (isEmpty(service.age)) {
                    service.age = "";
                }

                if (isEmpty(service.service_export.target)) {
                    service.service_export.target = "";
                }

                let serviceExportStatus = 'Unavailable';

                if (service.service_export.status === 'true') {
                    serviceExportStatus = 'Active'
                }

                serviceList.append(`
                    <tr>
                        <td width="1%"><input type="radio" class="form-check-input"></td>
                        <td width="5%"><span class="label-common label-${service.state.toLowerCase()}">${service.state}</span></td>
                        <td width="15%" class="label-name service-name">${service.name}</td>
                        <td>${service.namespace}</td>
                        <td>${service.service_type}</td>
                        <td>${service.cluster_ip}</td>
                        <td>${service.external_ips.join(" ")}</td>
                        <td>${portContents}</td>
                        <td>${service.age}</td>
                        <td>${service.service_export.target}</td>
                        <td><span class="label-common label-${serviceExportStatus.toLowerCase()}">${serviceExportStatus}</span></td>
                    </tr>`);
            }

            // fill null records
            for (let i = 0; i < numberOfNullRecord; i++) {
                serviceList.append(nullRecordHtml);
            }

            if (prevSelectedService && isExistService(prevSelectedService)) {
                // check prevSelectedService is in update service list
                selectServiceButton2(prevSelectedService);
                return;
            }

            $("#service-list tr:first-child input[type=radio]").prop('checked', true);
            prevSelectedService = getSelectedService();
        },
        error: function (error) {
            console.log(error);
        },
    });
}

// Deployment related functions
function getDeploymentList(cluster, namespace, pod_name) {
    $.ajax({
        type: "GET",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/deployments?pod=${pod_name}`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let deploymentList = $("#deployment-list");
            deploymentList.html("");
            if (!hasElement(response.deployments)) {
                clearDeploymentList();
                return;
            }

            for (let deployment of response.deployments) {
                $("#selected-deployment-name").text(deployment.name);
                deploymentList.append(
                    `
                <tr>
                    <td>
                        <span class="label-common label-${deployment.state.toLowerCase()}">${deployment.state}</span>
                    </td>
                    <td>${deployment.name}</td>
                    <td>${deployment.namespace}</td>
                    <td>${deployment.ready_replicas}</td>
                    <td>${deployment.restart}</td>
                    <td>${deployment.age}</td>
                </tr>
                `);
                setModal("#delete-modal-deployment", deployment.name);
            }
        },
        error: function (error) {
            console.log(error);
        },
    });
}


function getDaemonsetList(cluster, namespace, pod_name) {
    $.ajax({
        type: "GET",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/daemonsets?pod=${pod_name}`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let daemonsetList = $("#daemonset-list");

            daemonsetList.html("");

            if (!hasElement(response.daemonsets)) {
                clearDaemonSetList();
                return;
            }

            for (let daemonset of response.daemonsets) {
                daemonsetList.append(
                    `
                    <tr>
                        <td>
                            <span class="label-common label-${daemonset.state.toLowerCase()}">${daemonset.state}</span>
                        </td>
                        <td>${daemonset.name}</td>
                        <td>${daemonset.namespace}</td>
                        <td>${daemonset.images.length}</td>
                    </tr>
                    `
                );
                setModal("#delete-modal-daemonset", daemonset.name);
            }
        },
        error: function (error) {
            console.log(error);
        },
    });
}


// reload page
function reloadPage() {
    reloadPodList();
}

// reload pod list
function reloadPodList() {
    let cluster = getSelectedClusterFromCookie();
    let namespace = getSelectedNamespaceFromCookie();

    if (!cluster || !namespace) {
        clearPodList();
        resetPodDetails();
        return;
    }

    // update pod list
    refreshPodList(cluster, namespace);
}

