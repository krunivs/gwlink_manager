$(document).ready(function () {
    initClipboardJS();
    initNodeCPUChart();
    initNodeMemoryChart();
    initNodeCapacityChart();
    initNodeNetworkChart();
    initMCNLatencyChart();
    initMCNetworkChart();
    initNodeMetricUpdater();
    initMCNMetricUpdater();
    initClusterListUpdater();

    // select cluster list
    if ($("#cluster-list tr").length > 0) {
        let cluster = $('#cluster-list tr:first-child').find('.label-name').text();
        selectClusterName(cluster);

    }
});

let clusterListUpdateTimer;
let prevSelectedCluster;
let prevSelectedNode;

// initialize cluster list updater
// update cluster list (period=3s)
function initClusterListUpdater() {
    refreshClusterList();

    clusterListUpdateTimer = setInterval(function () {
        // update cluster list
        console.log('cluster list are updated.');
        refreshClusterList();
    }, 5000);
}

// when click on a cluster item on the cluster list,
// select the radio button,
// get cluster info
// get mc-network measured data and latency
$(document).on('click', '#cluster-list tr', function () {
    if ($(this).has('.label-name').length !== 0) {
        selectRadioBtn($(this));

        let cluster = getSelectedCluster();

        if(cluster) {
            selectClusterName(cluster);
        }
    }
});

// event listener for node-list 'tr' click
$(document).on('click', '#node-list tr', function () {
    if ($(this).has('.label-name').length !== 0) {
        selectRadioBtn($(this));

        let node = $(this).find(".label-name").html();

        if(node) {
            selectNodeName(node);
        }
    }
});

// event listener for node-list 'tr' click
$(document).on('click', '#migration-list tr', function () {
    if ($(this).has('.label-migration-id').length !== 0) {
        selectRadioBtn($(this));

        let migration_id = $(this).find(".label-migration-id").html();

        if(migration_id) {
            selectMigrationId(migration_id);
        }
    }
});

// event listener for Connect Modal is show
$(document).on('show.bs.modal', '#connectModal', function(e) {
    let cluster = $("#connect-cluster-name").val();
    let connectId = getSelectedClusterConnectId();

    // if cluster name is not exist or selected cluster is on connecting or connected,
    // prevent popup connectModal
    if (!cluster || connectId) {
        return e.preventDefault();
    }

    // set connecting target clusters to target dropdown box
    setConnectTargetCluster(cluster);
});

// event listener for 'OK' button click in Connect modal
$(document).on('click', '#connectModal button.btn.btn-primary.btn-blue', function () {
    $("#connectModal").modal("hide");
    let clusterName = $("#connect-cluster-name").val();
    connectMcNetwork(clusterName);
});

// event listener for Disconnect Modal is show
$(document).on('show.bs.modal', '#disconnectModal', function(e) {
    let selectedConnectId = getClusterMCNConnectID();
    let clusterName = $("#connect-cluster-name").val();

    if (!selectedConnectId || !clusterName) {
        return e.preventDefault();
    }
});

// event listener for 'Disconnect' button click in Disconnect modal
$(document).on('click', '#disconnectModal button.btn.btn-primary.btn-purple', function () {
    $("#disconnectModal").modal("hide");

    let clusterName = $("#connect-cluster-name").val();
    disconnectMcNetwork(clusterName);
});

// event listener for 'Create' button click in Import modal
$(document).on('click', '#importModal button.btn.btn-primary.btn-blue', function () {
    $("#importModal").modal("hide");

    importCluster();
});

// event listener for Delete Modal is shown
$(document).on('show.bs.modal', '#deleteModal', function(e) {
    let clusterName = getSelectedCluster();

    if (!clusterName) {
        return e.preventDefault();
    }
});

// event listener for 'Delete' button click in Delete modal
$(document).on('click', '#deleteModal button.btn.btn-primary.btn-red', function () {
    $("#deleteModal").modal("hide");
    let clusterName = getSelectedCluster();
    deleteCluster(clusterName);
    refreshClusterList();
});

// event listener for Delete Modal is shown
$(document).on('show.bs.modal', '#delete-modal-migration', function(e) {
    let cluster = getSelectedCluster();
    let migrationId = getSelectedMigrationId();

    if (!cluster || !migrationId) {
        return e.preventDefault();
    }
});

// event listener for 'Delete' button click in Delete modal
$(document).on('click', '#delete-modal-migration button.btn.btn-primary.btn-red', function () {
    $("#delete-modal-migration").modal("hide");

    let cluster = getSelectedCluster();
    let migrationId = getSelectedMigrationId();
    // alert('delete cluster=' + cluster + 'migration id=' + migrationId);
    deleteMigration(cluster, migrationId);
});


// refresh migration log list
function refreshMigrationLogList() {
    let cluster = getSelectedCluster();

    if (isEmpty(cluster)) {
        clearmigrationList();
        return;
    }

    getMigrationLogList(cluster);
}

// refresh cluster list
function refreshClusterList() {
    getClusterList();

    let cluster = getSelectedCluster();

    if (isEmpty(cluster)) {
        resetClusterDetails();
        return;
    }

    selectClusterName(cluster);
}

// reset cluster details when selected cluster is unavailable
function resetClusterDetails() {
    clearClusterDetail();
    clearNodeList();
    clearSelectedNodeName();
    clearConditions();
    clearMCNDetail();
    clearNodeMetricCharts();
}

// clear cluster list
function clearClusterList() {
    let clusterList = $("#cluster-list");
    let numberOfNullRecords = defaultNumberOfListViewRecord;
    let nullRecordHtml = `<tr><td/><td/><td/><td/><td/><td/><td/><td/></tr>`;

    clusterList.html("");

    // fill null records
    for (let i = 0; i < numberOfNullRecords; i++) {
        clusterList.append(nullRecordHtml);
    }
}

// clear cluster detail
function clearClusterDetail() {
    setCluster("", "");
    clearNodeInterface();
    setClusterState("");
    setClusterApiVersion("");
    setClusterAPINetworkAddress("");
    clearNodeMetricCharts();
    clearMCNMetricCharts();
}

// clear node list
function clearNodeList() {
    let nodeList = $("#node-list");
    let numberOfNullRecord = defaultNumberOfListViewRecord;
    let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/></tr>';

    nodeList.html("");

    for (let i = 0; i < numberOfNullRecord; i++) {
        nodeList.append(nullRecordHtml);
    }
}

// clear pod migration log list
function clearmigrationList() {
    let migrationList = $("#migration-list");
    let numberOfNullRecord = defaultNumberOfListViewRecord;
    let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/></tr>';

    migrationList.html("");

    for (let i = 0; i < numberOfNullRecord; i++) {
        migrationList.append(nullRecordHtml);
    }
}


// clear condition
function clearConditions() {
    let conditionList = $("#cluster-conditions");
    let numberOfNullRecord = defaultNumberOfListViewRecord + 5;
    let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/></tr>';

    conditionList.html("");

    for (let i = 0; i < numberOfNullRecord; i++) {
        conditionList.append(nullRecordHtml);
    }
}

// clear multi-cluster network detail
function clearMCNDetail() {
    setClusterMCNRole("");
    setClusterMCNConnectID("");
    setClusterMCNState("");
    setClusterMCNGlobalnetState("");
    setClusterMCNGlobalnetCIDR("");
    setClusterMCNCableDriver("");

    setClusterMCNLocalPublicIP("");
    setClusterMCNLocalGateway("");
    setClusterMCNLocalClusterCIDR("");
    setClusterMCNLocalServiceCIDR("");

    setClusterMCNRemotePublicIP("");
    setClusterMCNRemoteGateway("");
    setClusterMCNRemoteClusterCIDR("");
    setClusterMCNRemoteServiceCIDR("");
}

// clear node metric chart in cluster details and MCN
function clearNodeMetricCharts() {
    clearNodeCPUChart();
    clearNodeMemoryChart();
    clearNodeNetworkChart();
    clearNodePodCapacityChart();
}

// clear MCN metric chart in cluster details and MCN
function clearMCNMetricCharts() {
    clearMCNLatencyChart();
    clearMCNetworkChart();
}

// select cluster name
function selectClusterName(cluster) {
    // check cluster state
    // if cluster is unavailable, reset cluster details
    let clusterState = getSelectedClusterState();
    prevSelectedCluster = cluster;

    if (!clusterState || clusterState === "unavailable") {
        return resetClusterDetails();
    }

    getClusterDetail(cluster);
    setSelectedCluster(cluster);
    getNodeList(cluster);
    getMigrationLogList(cluster);

    let node = getSelectedNode();

    if(node) {
        selectNodeName(node);
    }

    let migrationId = getSelectedMigrationId();

    if(migrationId) {
        selectMigrationId(migrationId);
    }
}

// select node name
function selectNodeName(node) {
    prevSelectedNode = node;
    $("#selected-node-name").html(node);
}

// select migration id
function selectMigrationId(migrationId) {
    $("#selected-migration-id").html(migrationId);
}

// clear selected node name
function clearSelectedNodeName() {
    $("#selected-node-name").html("");
}

// clear node host network interface
function clearNodeInterface() {
    $("#selected-node-host-if").html("");
}
// set cluster id
function setSelectedCluster(clusterName) {
    $('#connect-cluster-name').val(clusterName);

    let clusterId = getSelectedClusterId();

    $('.selected-cluster-id').each(function () {
        $(this).html(clusterId);
    });
}

// set cluster
function setCluster(clusterId, clusterName) {
    $('.selected-cluster-id').each(function () {
        $(this).html(clusterId);
    });

    $('.selected-cluster-name').each(function () {
        if ($(this).is('input')) {
            $(this).val(clusterName);
        } else {
            $(this).html(clusterName);
        }
    });
}

// set target cluster name for multi-cluster connecting
// call after connect modal btn is clicked.
function setConnectTargetCluster(sourceCluster) {
    // iterate cluster table, parse cluster name and id
    let targetCluster = $("#target-cluster-select");

    targetCluster.html("");

    $("#cluster-list tr").each(function () {
        let clusterField = $(this).find('td:nth-child(3)');
        let connectedId = $(this).find('td:nth-child(8)').text();
        let mcnConnectState = $(this).find('td:nth-child(9)').text();
        let clusterState = $(this).find('td:nth-child(2)').text();
        let clusterId = clusterField.attr('cls-id');
        let clusterName = clusterField.text();

        if(!clusterName) {
            console.log('Not found any cluster record');
            return true;
        }
        if (!clusterId) {
            console.log('Not found cluster ID');
            return true;
        }
        if (!clusterName) {
            console.log('Not found cluster name');
            return true;
        }
        if(connectedId) {
            return true;
        }
        if(mcnConnectState !== 'Standby') {
            return true;
        }
        if (clusterName !== sourceCluster && clusterState === 'Active') {
            targetCluster.append(`
                <option value="${clusterId}">${clusterName}</option>
            `);
        }
    });
}

// set cluster state
function setClusterState(state) {
    let clusterState = $('.selected-cluster-state');

    if (!state) {
        clusterState.each(function () {
            $(this).attr('class', 'label-common label-unavailable selected-cluster-state');
            $(this).html("Unavailable");
        });
        return;
    }

    clusterState.each(function () {
        $(this).attr('class', 'label-common label-' + (state).toLowerCase() + ' selected-cluster-state');
        $(this).html(state);
    });
}

// set cluster registration cli command(run in gw-agent)
function setClusterRegistrationCliCommand(command) {
    $('#copy-text').html(command);
}

// set cluster API version
function setClusterApiVersion(version) {
    $('#selected-cluster-api-version').html(version);
}

// set cluster api network address
function setClusterAPINetworkAddress(addr) {
    $('#selected-cluster-api-address').html(addr);
}

// set cluster role in multi-cluster network(Local or Remote)
function setClusterMCNRole(role) {
    $('#selected-node-role').html(role);
}

// set MCN connect ID
function setClusterMCNConnectID(connectID) {
    $('.selected-cluster-mc-connection-id').each(function () {
        $(this).html(connectID);
    });
}

// get MCN connect ID
function getClusterMCNConnectID() {
    return $('.selected-cluster-mc-connection-id')[0].innerText;
}

// set MCN state
function setClusterMCNState(mcnState) {
    let multiClusterStatus = $('#selected-cluster-mc-status');

    if (mcnState) {
        multiClusterStatus.attr('class', 'label-common label-' + mcnState.toLowerCase());
        multiClusterStatus.html(mcnState);
        return;
    }

    multiClusterStatus.attr('class', 'label-common label-unavailable');
    multiClusterStatus.html("Unavailable");
}

// set MCN globalnet state
function setClusterMCNGlobalnetState(globalnet) {
    let multiClusterGlobalnet = $('#selected-cluster-mc-globalnet');

    if (isEmpty(globalnet)) {
        multiClusterGlobalnet.attr('class', 'label-common label-unavailable');
        multiClusterGlobalnet.html("Unavailable");
        return;
    }

    if (globalnet === true) {
        multiClusterGlobalnet.attr('class', 'label-common label-enabled');
        multiClusterGlobalnet.html("True");
        return;
    }
    multiClusterGlobalnet.attr('class', 'label-common label-disabled');
    multiClusterGlobalnet.html("False");
}

// set MCN globalnet CIDR
function setClusterMCNGlobalnetCIDR(cidr) {
    let multiClusterGlobalCidr = $('#selected-cluster-mc-global-cidr');

    multiClusterGlobalCidr.html(cidr);
}

// set MCN cable driver
function setClusterMCNCableDriver(driver) {
    let multiClusterCableDriver = $('#selected-cluster-mc-cable-driver');

    multiClusterCableDriver.html(driver);
}

// set MCN local public IP
function setClusterMCNLocalPublicIP(addr) {
    let multiClusterLocalPublicIp = $('#selected-cluster-mc-local-public');

    multiClusterLocalPublicIp.html(addr);
}

// set MCN local gateway IP
function setClusterMCNLocalGateway(addr) {
    let multiClusterLocalGatewayIp = $('#selected-cluster-mc-local-gateway');

    multiClusterLocalGatewayIp.html(addr);
}

// set MCN local service CIDR
function setClusterMCNLocalServiceCIDR(cidr) {
    let multiClusterLocalServiceCidr = $('#selected-cluster-mc-local-service-cidr');

    multiClusterLocalServiceCidr.html(cidr);
}

// set MCN local cluster CIDR
function setClusterMCNLocalClusterCIDR(cidr) {
    let multiClusterLocalClusterCidr = $('#selected-cluster-mc-local-cluster-cidr');

    multiClusterLocalClusterCidr.html(cidr);
}

// set MCN remote public IP
function setClusterMCNRemotePublicIP(addr) {
    let multiClusterRemotePublicIp = $('#selected-cluster-mc-remote-public');

    multiClusterRemotePublicIp.html(addr);
}

// set MCN remote gateway IP
function setClusterMCNRemoteGateway(addr) {
    let multiClusterRemoteGatewayIp = $('#selected-cluster-mc-remote-gateway')

    multiClusterRemoteGatewayIp.html(addr);
}

// set MCN remote service CIDR
function setClusterMCNRemoteServiceCIDR(cidr) {
    let multiClusterRemoteServiceCidr = $('#selected-cluster-mc-remote-service-cidr');

    multiClusterRemoteServiceCidr.html(cidr);
}

// set MCN remote cluster CIDR
function setClusterMCNRemoteClusterCIDR(cidr) {
    let multiClusterRemoteClusterCidr = $('#selected-cluster-mc-remote-cluster-cidr')

    multiClusterRemoteClusterCidr.html(cidr);
}

// get cluster list from gwlink-manager server
function getClusterList() {
    $.ajax({
        url: "/api/app/v1/clusters",
        type: "GET",
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let clusterList = $("#cluster-list");
            let clusterLength = response.clusters.length;
            let numberOfNullRecords = defaultNumberOfListViewRecord;
            let nullRecordHtml = `<tr><td/><td/><td/><td/><td/><td/><td/><td/><td/></tr>`;
            clusterList.html("");

            numberOfNullRecords = numberOfNullRecords - clusterLength

            if(!hasElement(response.clusters)) {
                clearClusterList();
                return;
            }

            if (response.clusters) {
                for (const cluster of response.clusters) {
                    let mcn_status = "Unavailable";
                    let connectId = "";
                    let apiVersion = "";
                    let apiAddress = "";

                    if(cluster.mc_network) {
                        mcn_status = cluster.mc_network.status;

                        if(!cluster.mc_network.status) {
                            mcn_status = "Unavailable";
                        } else {
                            mcn_status = cluster.mc_network.status;
                        }

                        if(cluster.mc_network.connect_id) {
                            connectId = cluster.mc_network.connect_id;
                        }
                    }

                    if(cluster.api_address) {
                        apiAddress = cluster.api_address;
                    }

                    if(cluster.api_version) {
                        apiVersion = cluster.api_version;
                    }

                    clusterList.append(`
                        <tr>
                            <td><input type="radio" class="form-check-input"></td>
                            <td><span class="label-common label-${cluster.state.toLowerCase()}">${cluster.state}</span></td>
                            <td cls-id="${cluster.id}"><a href="#" class="label-name">${cluster.name}</a></td>
                            <td>${apiAddress}</td>
                            <td>${apiVersion}</td>
                            <td id="registrationImg" value="${cluster.registration}">
                                <a href="#" data-bs-toggle="modal" data-bs-target="#registrationModal">
                                    <img src="static/images/ico-file.png" alt="Registration"/></a></td>
                            <td>${cluster.nodes}</td>
                            <td width="18%" class="connection-id">${connectId}</td>
                            <td><span class="label-common label-${mcn_status.toLowerCase()}">${mcn_status}</span></td>;
                        </tr>`);
                }
            }
            for (let i=0; i < numberOfNullRecords; i++)
                clusterList.append(nullRecordHtml);

            if(prevSelectedCluster && isExistCluster(prevSelectedCluster)) {
                // check prevSelectedCluster is in update cluster list
                selectClusterButton(prevSelectedCluster);
                return;
            }

            $("#cluster-list  tr:first-child input[type=radio]").prop('checked', true);
            prevSelectedCluster = getSelectedCluster();
        },
        error: function (error) {
            clearClusterList();
            resetClusterDetails();
            console.log(error);
        }
    });
}

// get node list from gwlink-manager server
function getNodeList(clusterName) {
    $.ajax({
        url: `/api/app/v1/clusters/${clusterName}/nodes`,
        type: "GET",
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let nodeList = $("#node-list");
            let nodeLength = response.nodes.length;
            let numberOfNullRecord = defaultNumberOfListViewRecord;
            let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/></tr>';

            nodeList.html("");
            numberOfNullRecord = numberOfNullRecord - nodeLength;

            if (!hasElement(response.nodes)) {
                clearNodeList();
            }

            for (const node of response.nodes) {
                if (node.host_if) {
                    $("#selected-node-host-if").html(node.host_if);
                }

                nodeList.append(`
                    <tr>
                       <td><input type="radio" class="form-check-input"></td>
                       <td><span class="label-common label-${node.state.toLowerCase()} node-state">${node.state}</span></td>
                       <td><a href="#" class="label-name">${node.name}</a></td>
                       <td class="node-role">${node.role}</td>
                       <td class="node-k8s-version">${node.k8s_version}</td>
                       <td class="node-ip">${node.ip}</td>
                       <td class="node-os">${node.os}</td>
                       <td class="node-cpus">${node.number_of_cpu}</td>
                       <td class="node-mem">${node.ram_size}</td>
                       <td>
                         <span class="node-pods">${node.pods.running_pods}/${node.pods.max_pods}</span>
                         <span class="node-pod-usages">(${node.pods.usage}%)</span>
                       </td>
                       <td class="node-age">${node.age}</td>
                    </tr>`);
            }

            if(prevSelectedNode && isExistNode(prevSelectedNode)) {
                // check prevSelectedNode is in update node list
                selectNodeButton(prevSelectedNode);
                return;
            }

            $("#node-list  tr:first-child input[type=radio]").prop('checked', true);
            prevSelectedNode = getSelectedNode();

            // fill null records
            for (let i = 0; i < numberOfNullRecord; i++) {
                nodeList.append(nullRecordHtml);
            }
        },
        error: function (error) {
            console.log(error);
            clearNodeList();
            clearNodeMetricCharts();
            clearNodeInterface();
            clearSelectedNodeName();
            clearNodeMetricCharts();
        }
    })
}

// get migration log list from gwlink-manager server
function getMigrationLogList(clusterName) {
    $.ajax({
        url: `/api/app/v1/clusters/${clusterName}/migration_logs`,
        type: "GET",
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let migrationList = $("#migration-list");
            let podMigrationLength = response.logs.length;
            let numberOfNullRecord = defaultNumberOfListViewRecord;
            let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/><td/></tr>';

            migrationList.html("");

            numberOfNullRecord = numberOfNullRecord - podMigrationLength;

            if (!hasElement(response.logs)) {
                clearmigrationList();
            }

            for (const log of response.logs) {
                let state = log.state;
                let label;

                if (state === "ERROR_EXITED") {
                    label = "label-error";
                } else {
                    label = "label-enabled";
                }
                migrationList.append(`
                    <tr>
                       <td><input type="radio" class="form-check-input"></td>
                       <td class="label-migration-id">${log.migration_id}</td>
                       <td><span class="label-common ${label}">${state}</span></td>
                       <td>${log.source_namespace}</td>
                       <td>${log.source_pod}</td>
                       <td>${log.source_cluster}</td>
                       <td>${log.target_cluster}</td>
                       <td>${log.target_node}</td>
                       <td>${log.task}</td>
                       <td>${log.retry}</td>
                       <td>${log.error}</td>
                       <td>${log.start_date}</td>
                       <td>${log.end_date}</td>                       
                    </tr>`);
            }

            $("#migration-list  tr:first-child input[type=radio]").prop('checked', true);

            // fill null records
            for (let i = 0; i < numberOfNullRecord; i++) {
                migrationList.append(nullRecordHtml);
            }
        },
        error: function (error) {
            console.log(error);
            clearmigrationList();
        }
    })
}

// get cluster detail
function getClusterDetail(clusterName) {
    $.ajax({
        url: "/api/app/v1/clusters/" + clusterName,
        type: "GET",
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            if(!hasElement(response.clusters)) {
                resetClusterDetails();
            }
            let cluster = response.clusters[0];

            // cluster detail tab
            setCluster(cluster.id, cluster.name);
            setClusterState(cluster.state);
            setClusterApiVersion(cluster.api_version);
            setClusterAPINetworkAddress(cluster.api_address);

            // multi-cluster network tab
            if (!cluster.mc_network || !cluster.mc_network.status || cluster.mc_network.status != 'Connected') {
                clearMCNDetail();
                clearMCNMetricCharts();
            }
            else {
                setClusterMCNRole(cluster.mc_network.broker_role);
                setClusterMCNConnectID(cluster.mc_network.connect_id);
                setClusterMCNState(cluster.mc_network.status);
                setClusterMCNGlobalnetState(cluster.mc_network.globalnet);
                setClusterMCNGlobalnetCIDR(cluster.mc_network.global_cidr);
                setClusterMCNCableDriver(cluster.mc_network.cable_driver);

                setClusterMCNLocalPublicIP(cluster.mc_network.local.public);
                setClusterMCNLocalGateway(cluster.mc_network.local.gateway);
                setClusterMCNLocalClusterCIDR(cluster.mc_network.local.cluster_cidr);
                setClusterMCNLocalServiceCIDR(cluster.mc_network.local.service_cidr);

                setClusterMCNRemotePublicIP(cluster.mc_network.remote.public);
                setClusterMCNRemoteGateway(cluster.mc_network.remote.gateway);
                setClusterMCNRemoteClusterCIDR(cluster.mc_network.remote.cluster_cidr);
                setClusterMCNRemoteServiceCIDR(cluster.mc_network.remote.service_cidr);
            }

            // cluster component conditions tab
            let clusterConditionList = $('#cluster-conditions');
            clusterConditionList.html("");

            if (!hasElement(cluster.conditions)) {
                clearConditions();
                return;
            }

            for (let condition of cluster.conditions) {
                let update_datetime = "";

                if (condition.updated) {
                    update_datetime = condition.updated.replace('T', ' ');
                    update_datetime = update_datetime.replace('Z', ' ');
                }

                clusterConditionList.append(`
                    <tr>
                      <td width="5%"/>
                      <td width="15%">${condition.condition}</td>
                      <td width="10%">${condition.status}</td>
                      <td width="10%">${update_datetime}</td>
                      <td width="40%" class="text-left" >${condition.message}</td>
                      <td width="20%"/>
                    </tr>`);
            }
        },
        error: function (error) {
            console.log(error);
            clearConditions();
        }
    })
}

// connect multi-cluster network
function connectMcNetwork(clusterName) {
    let targetClusterName = $("#target-cluster-select > option:selected").text();

    let formData = {
        "target": targetClusterName
    }
    $.ajax({
        url: `/api/app/v1/clusters/${clusterName}/mc/connect`,
        type: "POST",
        data: JSON.stringify(formData),
        dataType: "json",
        accept: "application/json",
        contentType: "application/json; charset=utf-8",
        headers: {
            Authorization: ""
        },
        success: function (response) {
            const message =
                `<p>Connect: ${clusterName}</p> 
                 <p class="color-green">Success!</p>`
            showMessageModal('Connect', message);
            refreshClusterList();
        },
        error: function (error) {
            const message =
                `<p>Cluster: ${clusterName}</p>
                 <p class="color-red">${error.responseJSON.error}</p>`;
            showErrorMessageModal(message);
        }
    });
}

// disconnect multi-cluster network
function disconnectMcNetwork(clusterName) {
    $.ajax({
        url: `/api/app/v1/clusters/${clusterName}/mc/disconnect`,
        type: "POST",
        headers: {
            Authorization: ""
        },
        success: function (response) {
            const message =
                `<p>Disconnect: ${clusterName}</p>
                 <p class="color-green">Success!</p>`
            showMessageModal('Disconnect', message);
            refreshClusterList();
        },
        error: function (error) {
            const message =
                `<p>Cluster: ${clusterName}</p>
                 <p class="color-red">${error.responseJSON.error}</p>`;
            showErrorMessageModal(message);
        }
    });
}

// request import cluster
function importCluster() {
    let clusterName = $("#import-cluster-name").val();
    let clusterRemark = $("#import-cluster-remark").val();
    let formData = {
        "name": clusterName,
        "description": clusterRemark
    }
    $.ajax({
        url: "/api/app/v1/clusters",
        type: "POST",
        data: JSON.stringify(formData),
        dataType: "json",
        accept: "application/json",
        contentType: "application/json; charset=utf-8",
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            const message =
                `<p>Import: ${clusterName}</p>
                 <p class="color-green">Success!</p>`
            showMessageModal('Import', message);
            refreshClusterList();
        },
        error: function (error) {
            showErrorModal(error);
        }
    });
}

// request delete cluster
function deleteCluster(clusterName) {
    $.ajax({
        url: `/api/app/v1/clusters/${clusterName}`,
        type: "DELETE",
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            const message =
                `<p>Delete: ${clusterName}</p>
                 <p class="color-green">Success!</p>`
            showMessageModal('Delete', message);
            // find cluster record from cluster table and delete it
            // if deleting cluster is selectedCluster, select the other cluster from cluster table
            refreshClusterList();
        },
        error: function (error) {
            showErrorModal(error);
        }
    });
}

// delete migration log
function deleteMigration(cluster, migrationId) {
    $.ajax({
        url: `/api/app/v1/clusters/${cluster}/migration_logs/${migrationId}`,
        type: "DELETE",
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            const message = `
                <p>Delete cluster: ${cluster}</p>
                <p>Delete migration ID: ${migrationId}</p>
                <p class="color-green">Success!</p>`;
            showMessageModal('Delete', message);
            // find cluster record from cluster table and delete it
            // if deleting cluster is selectedCluster, select the other cluster from cluster table
            refreshMigrationLogList();
        },
        error: function (error) {
            showErrorModal(error);
        }
    })
}
