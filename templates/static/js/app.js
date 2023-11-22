let defaultNumberOfListViewRecord = 5;

document.body.style.zoom = 0.9;

let allClusterNamespaces = [];

// Cluster related functions
function getAllClusterNamespaceList() {
    $.ajax({
        url: "/api/app/v1/clusters/_all_/namespaces",
        async: false,
        type: "GET",
        success: function (response) {
            let clusterList = $("#cluster-list");
            let importClusterList = $("#import-yaml-cluster-list");

            importClusterList.html("");
            clusterList.html("");

            if (!hasElement(response.namespaces)) {
                allClusterNamespaces = [];
                return;
            }

            // update cluster dropbox and yaml apply tool
            allClusterNamespaces = response.namespaces;

            for(const item of response.namespaces) {
                clusterList.append(`<li><a class="cluster-item">${item.name}</a></li>`);
                importClusterList.append(`<li><a class="import-yaml-cluster-item" href="#">${item.name}</a></li>`);
            }
            // select cluster for yaml apply tool
            if(!selectedYMLImportCluster) {
                selectedYMLImportCluster = $(".import-yaml-cluster-item").first().html();
                $("#selected-import-yaml-cluster-name").html(selectedYMLImportCluster);
            }
        },
        error: function (error) {
            allClusterNamespaces = [];
            console.log(error);
        }
    });
}

// Namespace related functions
function getNamespaceList(cluster) {
    if(allClusterNamespaces.length <= 0) {
        return;
    }

    let namespaceList = $("#namespace-list");
    let importNamespaceList = $("#import-yaml-namespace-list");

    namespaceList.html("");
    importNamespaceList.html("");

    for(const item of allClusterNamespaces) {
        if (item.name === cluster) {
            if (item.namespaces.length <= 0) {
                return;
            }
            for (const namespace of item.namespaces) {
                namespaceList.append(`<li><a class="namespace-item">${namespace}</a></li>`);
                if(namespace !== '_all_') {
                    importNamespaceList.append(`<li><a class="import-yaml-namespace-item" href="#">${namespace}</a></li>`);
                }
            }
        }
    }
}

function getYAMLImportNamespaceList(cluster) {
    if(allClusterNamespaces.length <= 0) {
        return;
    }

    let importNamespaceList = $("#import-yaml-namespace-list");
    importNamespaceList.html("");

    for(const item of allClusterNamespaces) {
        if (item.name === cluster) {
            if (item.namespaces.length <= 0) {
                return;
            }
            for (const namespace of item.namespaces) {
                if(namespace === '_all_') continue;
                importNamespaceList.append(`<li><a class="import-yaml-namespace-item" href="#">${namespace}</a></li>`);
            }
        }
    }

    // select namespace for yaml apply tool
    let selectedNamespace = $(".import-yaml-namespace-item").first().html();
    $("#selected-import-yaml-namespace-name").html(selectedNamespace);
}

let updateClusterAndNamespaceListTimer;

function initClusterAndNamespaceListUpdater() {
    /**
     * updater for cluster and namespace list
     * */
    updateClusterAndNamespaceListTimer = setInterval(function() {
        // get active cluster list and update cluster dropbox
        getAllClusterNamespaceList();

        let cluster = getSelectedClusterFromCookie();
        let namespace = getSelectedNamespaceFromCookie();
        let clusterChanged = false;

        if(!isExistInActiveClusterList(cluster)) {
            let clusterItemList = $(".cluster-item");

            cluster = clusterItemList.first().html();
            setSelectedClusterToCookie(cluster);
            clusterChanged = true;

            // not found any cluster in .cluster-item
            if(!cluster) {
                setSelectedClusterToCookie("");
                setSelectedNamespaceToCookie("");
                return;
            }
        }

        // select cluster in #cluster-list
        $("#selected-cluster-name").html(cluster);

        // get active namespace list and update namespace dropbox
        getNamespaceList(cluster);

        if(!isExistInNamespaceList(namespace)) {

            let namespaceItemList = $(".namespace-item");

            namespace = namespaceItemList.first().html();

            // not found any namespace in .namespace-item
            if(!namespace) {
                setSelectedNamespaceToCookie("");
                return;
            }
        }

        if(clusterChanged) {
            namespace = '_all_';
            $("#selected-namespace-name").html('_all_');

            setSelectedNamespaceToCookie(namespace);
        }
        else {
            $("#selected-namespace-name").html(namespace);
        }
        console.log("cluster list and namespace list is updated");

    }, 1000);
}

// cluster list
$(document).on('click', '.cluster-item', function () {
    /**
     * cluster dropbox click event handler
     */
    selectClusterDropBox(this);

    // refresh pod list
    reloadPage();
});

$(document).on('click', '.namespace-item', function () {
    /**
     * namespace dropbox click event handler
     */
    selectNamespaceDropBox(this);

    // refresh pod list
    reloadPage();
});


// is exist cluster name in cluster-item list
function isExistInActiveClusterList(cluster) {
    let found = false;

    $(".cluster-item").each(function() {
        let val = $(this).html();

        if(val === cluster) {
            found = true;
            return false;
        }
    });
    return found;
}

// is exist namespace name in namespace-item list
function isExistInNamespaceList(namespace) {
    let found = false;

    $(".namespace-item").each(function () {
        let val = $(this).html();

        if(val === namespace) {
            found = true;
            return false;
        }
    });
    return found;
}

function selectClusterDropBox(obj) {
    /**
     * select cluster drop box and set to cookie
     * @type {*|jQuery}
     */
    let selectedClusterFromDropBox = $(obj).html();
    let selectedClusterFromFromCookies = getSelectedClusterFromCookie();

    if (isEmpty(selectedClusterFromDropBox)) {
        setSelectedClusterToCookie(null);
        setSelectedNamespaceToCookie(null);
        return;
    }

    // select cluster dropbox
    $("#selected-cluster-name").html(selectedClusterFromDropBox);

    // set cookies
    setSelectedClusterToCookie(selectedClusterFromDropBox);

    // If cluster selection is changed,
    let selectedNamespace = getSelectedNamespaceFromCookie();

    if (selectedClusterFromFromCookies !== selectedClusterFromDropBox) {
        selectedNamespace = '_all_'
        $("#selected-namespace-name").html(selectedNamespace);
        setSelectedNamespaceToCookie(selectedNamespace);
    }
}

function selectNamespaceDropBox(obj) {
    /**
     * select namespace dropbox and set to cookie
     */
    let selectedNamespaceFromDropBox = $(obj).html();  // selected namespace from dropbox

    if (isEmpty(selectedNamespaceFromDropBox)) {
        return;
    }

    // select namespace dropbox item
    $("#selected-namespace-name").html(selectedNamespaceFromDropBox);

    // set namespace to cookie
    setSelectedNamespaceToCookie(selectedNamespaceFromDropBox);
}

function hasElement(val) {
    if (val.length === undefined) {
        return false
    }
    return val.length > 0;
}

function isEmpty(val) {
    return val === undefined || val === null || val === '';
}

function getSelectedClusterFromCookie() {
    return Cookies.get('selectedCluster');
}

function setSelectedClusterToCookie(clusterName) {
    Cookies.set('selectedCluster', clusterName);
}

function clearClusterSelectBox()  {
    $("#selected-cluster-name").html('');
    setSelectedClusterToCookie('');
}

function clearNamespaceSelectBox() {
    $("#selected-namespace-name").html('');
    setSelectedNamespaceToCookie('');
}

function getSelectedNamespaceFromCookie() {
    return Cookies.get('selectedNamespace');
}

function setSelectedNamespaceToCookie(namespace) {
    Cookies.set('selectedNamespace', namespace);
}

function getBearerAccessTokenHeaderFromCookie() {
    return "Bearer " + Cookies.get("token");
}

function setAccessTokenToCookie(token) {
    Cookies.set('token', token);
}

function printText(text) {
    alert(text)
}


// when click on 'tr' tag, the radio button is selected
function selectRadioBtn(selectedElement) {
    selectedElement.parent().find('input[type=radio]').prop('checked', false);
    selectedElement.find('input[type=radio]').prop('checked', true);
}

// Import YAML - insert value in textarea
document.getElementById("importYaml").addEventListener("change", () => {
    let inputFile = document.getElementById("importYaml").files[0];
    let readTextArea = document.getElementById("readYamlArea");
    let fileReader = new FileReader();
    fileReader.readAsText(inputFile);
    fileReader.onload = function (e) {
        let content = e.target.result;
        readTextArea.value += content;
    };
});


/*** Pod Management functions ***/
$(document).on('show.bs.modal', '#delete-modal-pod', function(e) {
    let cluster = $("#selected-cluster-name").html();
    let namespace = getSelectedPodNamespace();
    let pod = getSelectedPod();

    if(!cluster || !namespace || !pod) {
        e.preventDefault();
    }
});

$(document).on('click', '#delete-modal-pod .modal-footer .btn.btn-red', function () {
    /**
     * delete pod
     * */
    let clusterName = $("#selected-cluster-name").html();
    let namespaceName = getSelectedPodNamespace();
    let podName = $(this).parent().parent().find('.modal-body-emphasis').text();

    $("#delete-modal-pod").modal("toggle");

    deletePod(clusterName, namespaceName, podName);

    reloadPage();
});

let migrationClusters = {}

$(document).on('show.bs.modal', '#migrate-modal-pod', function(e) {
    let cluster = $("#selected-cluster-name").text();
    let namespace = getSelectedPodNamespace();
    let pod = $("#migrate-modal-pod #recipient-name").attr('value');

    if(!cluster || !namespace || !pod) {
        e.preventDefault();
    }
});

$(document).on('click', '#registrationImg', function() {
    setClusterRegistrationCliCommand($(this).attr('value'));
});


$(document).on('click', '#migrateBtn', function () {
    /***
     * "Migrate" Button(#migrateBtn) event listener
     * @type {*|jQuery}
     */
    let pod = $("#migrate-modal-pod #recipient-name").attr('value');
    let namespace = getSelectedPodNamespace();
    let cluster = $("#selected-cluster-name").text();

    $.ajax({
        type: "GET",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/pods/${pod}/migrate`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            // validate migration target clusters
            if (!hasElement(response.clusters)) {
                $('#migrate-modal-pod').modal('toggle');
                let error = {
                    statusText: 'Cluster',
                    status: 'Error',
                    responseJSON: {
                        error: 'Not found migration target cluster'
                    }
                };
                showErrorModal(error);
                return;
            }
            let foundMigrationNode = false;

            // validate migration target nodes
            for (let cluster of response.clusters) {
                for (let node of cluster.nodes) {
                    foundMigrationNode = true;
                    break;
                }
            }
            if (!foundMigrationNode) {
                $('#migrate-modal-pod').modal('toggle');
                let error = {
                    statusText: 'Node',
                    status: 'Error',
                    responseJSON: {
                        error: 'Not found any migration target node'
                    }
                };
                showErrorModal(error);
                return;
            }

            let migrateClusterList = $("#migrate-cluster-list");
            let migrateNodeList = $("#migrate-node-list");

            migrateClusterList.html("");
            migrateNodeList.html("");

            migrationClusters = response.clusters;

            for (let cluster of response.clusters) {
                migrateClusterList.append(`<option value="${cluster.name}">${cluster.name}</option>`);
            }
            for (let node of response.clusters[0].nodes) {
                migrateNodeList.append(`<option value="${node}">${node}</option>`);
            }
        },
        error: function (error) {
            $('#migrate-modal-pod').modal('toggle');
            showErrorModal(error);
        }
    });
});

$(document).on('change', '#migrate-cluster-list', function () {
    /***
     * select box(#migrate-cluster-list) "change" event listener
     * @type {*|jQuery}
     */

    let selectedClusterName = $("#migrate-cluster-list option:selected").val();
    let migrateNodeList = $("#migrate-node-list");

    if (!hasElement(migrationClusters)) return;

    migrateNodeList.html("");

    for (let cluster of migrationClusters) {
        if (cluster.name === selectedClusterName) {
            for (let node of cluster.nodes) {
                migrateNodeList.append(`<option value="${node}">${node}</option>`);
            }
        }
    }
});


$(document).on('click', '#migrate-modal-pod button.btn.btn-blue', function () {
    /**
     * Migration submit button click event listener
     * */
    let sourceClusterName = $("#selected-cluster-name").text();
    let sourceNamespace = getSelectedPodNamespace();
    let sourcePodName = $("#migrate-modal-pod #recipient-name").attr('value');
    let targetClusterName = $("#migrate-cluster-list option:selected").val();
    let targetNodeName = $("#migrate-node-list option:selected").val();
    let deleteOrigin = $('#flexCheckDefault').prop('checked');

    $("#migrate-modal-pod").modal("toggle");

    if (!sourceClusterName) {
        let error = {
            statusText: 'Cluster',
            status: 'Error',
            responseJSON: {
                error: 'Source cluster name is null'
            }
        };
        showErrorModal(error);
        return;
    }
    if (!sourceNamespace) {
        let error = {
            statusText: 'Namespace',
            status: 'Error',
            responseJSON: {
                error: 'Source namespace is null'
            }
        };
        showErrorModal(error);
        return;
    }
    if (!sourcePodName) {
        let error = {
            statusText: 'Pod',
            status: 'Error',
            responseJSON: {
                error: 'Source pod name is null'
            }
        };

        showErrorModal(error);
        return;
    }
    if (!targetClusterName) {
        let error = {
            statusText: 'Cluster',
            status: 'Error',
            responseJSON: {
                error: 'Target cluster name is null'
            }
        };

        showErrorModal(error);
        return;
    }
    if (!targetNodeName) {
        let error = {
            statusText: 'Node',
            status: 'Error',
            responseJSON: {
                error: 'Target node name is null'
            }
        };

        showErrorModal(error);
        return;
    }

    migratePod(sourceClusterName, sourceNamespace, sourcePodName, targetClusterName, targetNodeName, deleteOrigin);
});

/*** Service Management functions ***/
// delete service
$(document).on('show.bs.modal', '#delete-modal-service', function(e) {
    let cluster = $("#selected-cluster-name").html();
    let namespace = getSelectedServiceNamespace();
    let service = $(this).parent().parent().find('.modal-body-emphasis').text();

    if(!cluster || !namespace || !service) {
        e.preventDefault();
    }
});

$(document).on('click', '#delete-modal-service .modal-footer .btn.btn-red', function () {
    $('#delete-modal-service').modal('hide');
    let cluster = $("#selected-cluster-name").html();
    let namespace = getSelectedServiceNamespace();
    let service = $(this).parent().parent().find('.modal-body-emphasis').text();

    $("#delete-modal-service").modal("toggle");

    deleteService(cluster, namespace, service);
});

/**
 * get selected resource
 * */
// get selected cluster's state
function getSelectedClusterState() {
    return $("#cluster-list input[type=radio]:checked").parent().parent().find("td:nth-child(2)>span").html().toLowerCase();
}

// check whether cluster is exist in cluster list
function isExistCluster(cluster) {
    let found = false;

    $("#cluster-list .label-name").each(function() {
        let val = $(this).text();
        if (val === cluster) {
            found = true;
            return false;
        }
    });
    return found;
}

// check whether node is exist in node list
function isExistNode(node) {
    let found = false;

    $("#node-list .label-name").each(function() {
        let val = $(this).text();
        if (val === node) {
            found = true;
            return false;
        }
    });
    return found;
}

// check whether pod is exist in pod list
function isExistPod(pod) {
    let found = false;

    $("#pod-list .label-name").each(function() {
        let val = $(this).text();
        if (val === pod) {
            found = true;
            return false;
        }
    });
    return found;
}

// check whether deployment is exist in deployment list
function isExistDeployment(deployment) {
    let found = false;

    $("#deployment-list .label-name").each(function() {
        let val = $(this).text();
        if (val === deployment) {
            found = true;
            return false;
        }
    });
    return found;
}

// check whether daemonset is exist in daemonset list
function isExistDaemonSet(daemonset) {
    let found = false;

    $("#daemonset-list .label-name").each(function() {
        let val = $(this).text();
        if (val === daemonset) {
            found = true;
            return false;
        }
    });
    return found;
}

// check whether service is exist in service list
function isExistService(service) {
    let found = false;

    $("#service-list .label-name").each(function() {
        let val = $(this).text();
        if (val === service) {
            found = true;
            return false;
        }
    });
    return found;
}

// select cluster button
function selectClusterButton(cluster) {
    $("#cluster-list .label-name").each(function() {
        let val = $(this).text();
        if (val === cluster) {
            $(this).parent().parent().find("input[type=radio]").prop('checked', true);
            return false;
        }
    });
}

// select node button
function selectNodeButton(node) {
    $("#node-list .label-name").each(function() {
        let val = $(this).text();
        if (val === node) {
            $(this).parent().parent().find("input[type=radio]").prop('checked', true);
            return false;
        }
    });
}

// select pod button
function selectPodButton(pod) {
    $("#pod-list .label-name").each(function() {
        let val = $(this).text();
        if (val === pod) {
            $(this).parent().parent().find("input[type=radio]").prop("checked", true);
            return false;
        }
    });
}

// select deployment button
function selectDeploymentButton(deployment) {
    $("#deployment-list .label-name").each(function() {
        let val = $(this).text();
        if (val === deployment) {
            $(this).parent().parent().find("input[type=radio]").prop("checked", true);
            return false;
        }
    });
}

// select daemonset button
function selectDaemonSetButton(daemonset) {
    $("#daemonset-list .label-name").each(function() {
        let val = $(this).text();
        if (val === daemonset) {
            $(this).parent().parent().find("input[type=radio]").prop("checked", true);
            return false;
        }
    });
}

// select service button
function selectServiceButton(service) {
    $("#service-list .label-name").each(function() {
        let val = $(this).text();
        if (val === service) {
            $(this).parent().parent().find("input[type=radio]").prop("checked", true);
            return false;
        }
    });
}

// select service button
function selectServiceButton2(service) {
    $("#service-list .label-name").each(function() {
        let val = $(this).text();
        if (val === service) {
            $(this).parent().find("input[type=radio]").prop("checked", true);
            return false;
        }
    });
}

// get endpoint cluster's name for selected cluster
function getSelectedClusterEndpoint() {
    let selectedCluster = getSelectedCluster();
    let selectedConnectionId = getSelectedClusterConnectId();
    let endpoint = "";

    $(".connection-id").each(function () {
        let connectionId = $(this).text();
        let cluster = $(this).parent().find("td:nth-child(3)").text();

        if (selectedCluster !== cluster && selectedConnectionId === connectionId) {
            endpoint = cluster;
            return false;
        }
    });

    return endpoint;
}

// get selected cluster's mc connection id
function getSelectedClusterConnectId() {
    return $("#cluster-list input[type=radio]:checked").parent().parent().find("td:nth-child(8)").text();
}

// get selected cluster's name
function getSelectedCluster() {
    return $("#cluster-list input[type=radio]:checked").parent().parent().find("td:nth-child(3)").text();
}

// get selected cluster's ID
function getSelectedClusterId() {
    return $("#cluster-list input[type=radio]:checked").parent().parent().find("td:nth-child(3)").attr('cls-id');
}

// get selected cluster's MC network connection ID
function getSelectedClusterConnectId() {
    return $("#cluster-list input[type=radio]:checked").parent().parent().find("td:nth-child(8)").text();
}

// get selected cluster's MCN status
function getSelectedClusterMCNStatus() {
    return $("#cluster-list input[type=radio]:checked").parent().parent().find("td:nth-child(9)").text();
}

// get selected node's name
function getSelectedNode() {
    return $("#node-list input[type=radio]:checked").parent().parent().find("td:nth-child(3)").text();
}

// get selected migration id
function getSelectedMigrationId() {
    return $("#migration-list input[type=radio]:checked").parent().parent().find("td:nth-child(2)").text();
}

// get selected pod's name
function getSelectedPod() {
    return $("#pod-list .form-check-input:checked[type=radio]").parent().parent().find(".label-name").text();
}

// get selected pod's namespace
function getSelectedPodNamespace() {
    return $("#pod-list input[type=radio]:checked").parent().parent().find("td:nth-child(4)").text();
}

// get selected service's name
function getSelectedService() {
    return $("#service-list input:checked[type=radio]").parent().parent().find('.label-name').text();
}

// get selected service's namespace
function getSelectedServiceNamespace() {
    return $("#service-list input:checked[type=radio]").parent().parent().find(":nth-child(4)").text();
}

// get selected deployment's name
function getSelectedDeployment() {
    return $("#deployment-list input:checked[type=radio]").parent().parent().find('.label-name').text();
}

// get selected deployment's namespace
function getSelectedDeploymentNamespace() {
return $("#deployment-list input[type=radio]:checked").parent().parent().find("td:nth-child(4)").text();
}

// get selected daemonset's name
function getSelectedDaemonSet() {
    return $("#daemonset-list input:checked[type=radio]").parent().parent().find('.label-name').text();
}

// get selected daemonset's namespace
function getSelectedDaemonSetNamespace() {
    return $("#daemonset-list input[type=radio]:checked").parent().parent().find("td:nth-child(4)").text();
}

$(document).on('show.bs.modal', '#export-modal-service', function(e) {
    let cluster = $("#selected-cluster-name").html();
    let namespace = getSelectedServiceNamespace();
    let service = getSelectedService();

    if(!cluster || !namespace || !service) {
        e.preventDefault();
    }
});

$(document).on('click', '#export-modal-service button.btn.btn-blue', function () {
    let cluster = $("#selected-cluster-name").html();
    let namespace = getSelectedServiceNamespace();
    let service = getSelectedService();

    $("#export-modal-service").modal("hide");

    exportService(cluster, namespace, service);
    reloadPage();
});

$(document).on('show.bs.modal', '#unexport-modal-service', function(e) {
    let cluster = $("#selected-cluster-name").html();
    let namespace = getSelectedServiceNamespace();
    let service = getSelectedService();

    if(!cluster || !namespace || !service) {
        e.preventDefault();
    }
});

$(document).on('click', '#unexport-modal-service button.btn.btn-purple', function () {
    let cluster = $("#selected-cluster-name").html();
    let namespace = getSelectedServiceNamespace();
    let service = getSelectedService();

    $("#unexport-modal-service").modal("hide");

    unexportService(cluster, namespace, service);
    reloadPage();
})


/*** Deployment Management functions ***/

$(document).on('show.bs.modal', '#delete-modal-deployment', function(e) {
    let cluster = $("#selected-cluster-name").html();
    let namespace = $("#selected-namespace-name").html();
    let deployment = $(this).parent().parent().find('.modal-body-emphasis').text();

    if(!cluster || !namespace || !deployment) {
        e.preventDefault();
    }
});

$(document).on('click', '#delete-modal-deployment .modal-footer .btn.btn-red', function () {
    /**
     * Delete deployment button click event listener
     * */
    let cluster = $("#selected-cluster-name").html();
    let namespace = $("#selected-namespace-name").html();
    let deployment = $(this).parent().parent().find('.modal-body-emphasis').text();

    $("#delete-modal-deployment").modal("hide");

    deleteDeployment(cluster, namespace, deployment);
    reloadPage();
});

$(document).on('show.bs.modal', '#delete-modal-daemonset', function(e) {
    let cluster = $("#selected-cluster-name").html();
    let namespace = $("#selected-namespace-name").html();
    let deployment = $(this).parent().parent().find('.modal-body-emphasis').text();

    if(!cluster || !namespace || !deployment) {
        e.preventDefault();
    }
});

/*** Daemonset Management functions ***/
$(document).on('click', '#delete-modal-daemonset .modal-footer .btn.btn-red', function () {
    /**
     * Delete daemonset button click event listener
     * */
    $('#delete-modal-daemonset').modal('hide');
    let cluster = $("#selected-cluster-name").html();
    let namespace = $("#selected-namespace-name").html();
    let deployment = $(this).parent().parent().find('.modal-body-emphasis').text();

    $("#delete-modal-daemonset").modal("hide");

    deleteDaemonset(cluster, namespace, deployment);
    reloadPage();
});


// logout
$(document).on("click", "#logout", function () {
    /**
     * Logout button click event listener
     * */
    $.ajax({
        type: "POST",
        url: "/api/app/v1/logout",
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie(),
        },
        success: function () {
            Cookies.remove("token");
            location.reload();
        },
        error: function (error) {
            showErrorModal(error);
        },
    });
});

// menu active
let title = document.querySelector(".content-title-group>h2").innerText;
if (title === "Cluster") {
    title = "home";
}

let menu = document.getElementById(title.toLowerCase());
menu.className += "menu-active";

function initClipboardJS() {
    let clipboard = new ClipboardJS('#copy-clipboard-btn');
    clipboard.on('success', function (e) {
        console.info('Action:', e.action);
        console.info('Text:', e.text);
        console.info('Trigger:', e.trigger);
        e.clearSelection();
    });

    clipboard.on('error', function (e) {
        console.error('Action:', e.action);
        console.error('Trigger:', e.trigger);
    });
}

// custom select box
function dropdownSelected(num) {
    const label = document.querySelector('.dropdown-select-value-' + num);
    const options = document.querySelectorAll('.dropdown-item-' + num);

    const handleSelect = (item) => {
        label.innerHTML = item.textContent;
    }

    options.forEach(option => {
        option.addEventListener('click', () => handleSelect(option));
    });

}

// popup toggle
const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

// Import YAML - Append Line Numbers
function LNPrefix(ta) {
    var p = ta.parentElement,
        lineCount = ta.value.split(/\r?\n/).length;

    p.classList.add("LN_area");

    function appendLineNum(sb, line) {
        var n = document.createElement("div");
        n.innerText = line;
        n.classList.add("LN_n");
        n.style.cssText = "text-align:right;";
        sb.appendChild(n);
    }

    var toDelete = document.getElementsByClassName("LN_sb")[0];
    if (toDelete)
        p.removeChild(toDelete);

    // var currentLineCount = ;
    // if (lineCount > currentLineCount);

    var sidebar = document.createElement("div");
    sidebar.classList.add("LN_sb");
    sidebar.style.cssText = "padding-top:.375rem;display:inline-block;float:left;width:auto;";
    p.insertBefore(sidebar, ta);

    for (var l = 0; l < lineCount; l++)
        appendLineNum(document.getElementsByClassName("LN_sb")[0], l + 1);


    input.addEventListener("scroll", function (e) {
        var style = this.parentElement.children[0].style,
            o = style.margin - this.scrollTop;
        style.marginTop = String(o) + "px";
        this.parentElement.style.overflow = "hidden";
    });
}


// IMport YAML
const input = document.getElementById("readYamlArea");
LNPrefix(input);
input.addEventListener("input", LNPrefix.bind(this, input));


// Import YAML - insert value in textarea
document.getElementById("importYaml").addEventListener("change", () => {
    let file_to_read = document.getElementById("importYaml").files[0];
    let file_name = file_to_read.name.toLowerCase();
    if (file_name.endsWith('.yaml') || file_name.endsWith('.yml')) {
        let read_box = document.getElementById("readYamlArea");
        let error_box = document.getElementById("YamlError");
        let fileread = new FileReader();
        fileread.readAsText(file_to_read);
        read_box.value = "loading...";
        error_box.value = "";
        fileread.onload = function (e) {
            let content = e.target.result;
            read_box.value = content;
            LNPrefix(input);
            input.addEventListener("input", LNPrefix.bind(this, input));
        };
        fileread.onerror = function (e) {
            error_box.value = e.target.result;
        };
    } else {
        alert("The file type is not allowed to upload.");
    }
});

// Import YAML - clear value in textarea
function cancelImportYaml() {
    let read_box = document.getElementById("readYamlArea");
    let error_box = document.getElementById("YamlError");
    read_box.value = "";
    error_box.value = "";
}

function getPodMigrationInfo(cluster, namespace, pod) {
    return $.ajax({
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/pods/${pod}/migrate`,
        type: "GET",
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
        },
        error: function (error) {
            showErrorModal(error);
        }
    })
}

function updateMigrateNodeList(clusterName, namespaceName, podName) {
    getPodMigrationInfo(clusterName, namespaceName, podName).then((response) => {
        $("#migrate-node-list").html(`
            <option value="None" selected disabled hidden>Open this select menu</option>`);

        $.each(response.clusters, (i, cluster) => {
            if (cluster.name === $("#migrate-cluster-list").val()) {
                $.each(cluster.nodes, (j, node) => {
                    $("#migrate-node-list").append(`<option value="${node}">${node}</option>`);
                })
            }
        })
    })
}

function migratePod(sourceCluster, sourceNamespace, sourcePod, targetCluster, targetNode, deleteOrigin) {
    /**
     * Migrate source cluster's namespaced pod to target cluster's node
     * */

    let deleteOriginValue;

    if (deleteOrigin) deleteOriginValue = "True";
    else deleteOriginValue = "False";

    let body = {
        "target_cluster": targetCluster,
        "target_node": targetNode,
        "delete_origin": deleteOriginValue
    };

    $.ajax({
        url: `/api/app/v1/clusters/${sourceCluster}/namespaces/${sourceNamespace}/pods/${sourcePod}/migrate`,
        type: "POST",
        data: body,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },

        success: function (response) {
            const message = `
                <p> Migration request </p>
                <p> [Source] cluster: ${sourceCluster}, pod: ${sourcePod}, namespace: ${sourceNamespace} </p>
                <p> [Target] cluster: ${targetCluster}, node: ${targetNode} </p> 
                <p class="color-green"> Success!</p>`;

            showMessageModal("Migrate", message);
        },
        error: function (error) {
            showErrorModal(error);
        }
    })
}

function deletePod(cluster, namespace, pod_name) {
    $.ajax({
        type: "DELETE",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/pods/${pod_name}`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            const message = `
                <p>Pod: ${pod_name}</p>
                <p>Cluster: ${response.name}</p>
                <p>Cluster ID: ${response.id}</p>`;

            showMessageModal("Delete Complete", message);
        },
        error: function (error) {
            showErrorModal(error);
        },
    });
}

function exportService(cluster, namespace, service) {
    $.ajax({
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/services/${service}/export`,
        type: "POST",
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            const message = `
                <p>Export: ${service}</p>
                <p class="color-green">Success!</p>`;

            showMessageModal("Export", message);
            // refreshServiceList();
        },
        error: function (error) {
            showErrorModal(error);
        }
    })
}

function unexportService(cluster, namespace, service) {
    $.ajax({
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/services/${service}/unexport`,
        type: "POST",
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            const message = `
                <p>Unexport: ${service}</p>
                <p class="color-green">Success!</p>`;

            showMessageModal("Unexport", message);
        },
        error: function (error) {
            showErrorModal(error);
        }
    })
}

function deleteService(cluster, namespace, service_name) {
    $.ajax({
        type: "DELETE",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/services/${service_name}`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            const message = `
                <p>Service: ${service_name}</p>
                <p>Cluster: ${response.name}</p>
                <p>Cluster ID: ${response.id}</p>`;

            showMessageModal("Delete Complete", message);
        },
        error: function (error) {
            const message = `
                <p>Service: ${service_name}</p>
                <p class="color-red">${error.responseJSON.error}</p>`;

            showErrorMessageModal(message);
        },
    });
}

function deleteDeployment(cluster, namespace, deployment_name) {
    $.ajax({
        type: "DELETE",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/deployments/${deployment_name}`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            const message = `
                <p>Deployment: ${deployment_name}</p>
                <p>Cluster: ${response.name}</p>
                <p>Cluster ID: ${response.id}</p>`;
            showMessageModal("Delete Complete", message);
        },
        error: function (error) {
            const message = `
                <p>Deployment: ${deployment_name}</p>
                <p class="color-red">${error.responseJSON.error}</p>`;
            showErrorMessageModal(message);
        },
    });
}

function deleteDaemonset(cluster, namespace, daemonset_name) {
    $.ajax({
        type: "DELETE",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/daemonsets/${daemonset_name}`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            const message = `
                <p>Daemonset: ${daemonset_name}</p>
                <p>Cluster: ${response.name}</p>
                <p>Cluster ID: ${response.id}</p>`;

            showMessageModal("Delete Complete", message);
        },
        error: function (error) {
            const message = `
                <p>Daemonset: ${daemonset_name}</p>
                <p class="color-red">${error.responseJSON.error}</p>`;

            showErrorMessageModal(message);
        },
    });
}

