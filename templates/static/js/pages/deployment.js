// window load event
$(document).ready(() => {
    /**
     * window load event handler
     */
    let cluster = getSelectedClusterFromCookie();
    let namespace = getSelectedNamespaceFromCookie();

    if (cluster && namespace) {
        $("#deployment-list tr:first-child input[type=radio]").prop('checked', true);
        refreshDeploymentDetail();
    } else {
        clearDeploymentList();
        resetDeploymentDetails();
    }

    initClusterAndNamespaceListUpdater();
    initDeploymentListUpdater();
});

let deploymentListUpdateTimer;
let prevSelectedDeployment;
let prevSelectedPod;

// initialize deployment list updater
// update deployment list (period=3s)
function initDeploymentListUpdater() {
    deploymentListUpdateTimer = setInterval(function () {
        let cluster = getSelectedClusterFromCookie();
        let namespace = getSelectedNamespaceFromCookie();

        if (!cluster || !namespace) {
            clearDeploymentList();
            resetDeploymentDetails();
            return;
        }

        // update deployment list
        refreshDeploymentList(cluster, namespace);
        console.log('deployment list are updated.');
    }, 5000);
}

// reset deployment details
function resetDeploymentDetails() {
    clearDeploymentDetail();
    clearSelectedDeploymentName();
    clearPodList();
    clearSelectedPodName();
}

// deployment click event
$(document).on('click', '#deployment-list tr', function () {
    if ($(this).has('.label-name').length !== 0) {
        selectRadioBtn($(this));

        let deployment = getSelectedDeployment();

        if (isEmpty(deployment)) {
            resetDeploymentDetails();
            return;
        }

        selectDeploymentName(deployment);
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

// refresh deployment list view
function refreshDeploymentList(cluster, namespace) {
    getDeploymentList(cluster, namespace);

    let deployment = getSelectedDeployment();

    if (isEmpty(deployment)) {
        resetDeploymentDetails();
        return;
    }

    selectDeploymentName(deployment);
}

// refresh deployment detail
function refreshDeploymentDetail() {
    let deployment = getSelectedDeployment();

    if (isEmpty(deployment)) {
        resetDeploymentDetails();
        return;
    }

    selectDeploymentName(deployment);
}

// select deployment name
function selectDeploymentName(deployment) {
    let cluster = $("#selected-cluster-name").text();
    let pod = getSelectedPod();
    let namespace = getSelectedDeploymentNamespace();

    prevSelectedDeployment = deployment;

    getDeploymentDetail(cluster, namespace, deployment);
    getPodList(cluster, namespace, deployment);

    prevSelectedPod = getSelectedPod();

    setModal("#delete-modal-deployment", deployment);
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

// get deployment list from gslink-manager server
function getDeploymentList(cluster, namespace) {
    $.ajax({
        type: "GET",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/deployments`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let deploymentList = $("#deployment-list")
            let numberOfNullRecords = defaultNumberOfListViewRecord;
            let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/></tr>';

            deploymentList.html("");
            numberOfNullRecords -= response.deployments.length;

            for (let i = 0; i < response.deployments.length; i++) {
                let deployment = response.deployments[i];
                deploymentList.append(`
                    <tr>
                        <td><input type="radio" class="form-check-input"></td>
                        <td><span class="label-common label-${deployment.state.toLowerCase()}">${deployment.state}</span></td>
                        <td><a href="#node" class="label-name">${deployment.name}</a></td>
                        <td>${deployment.namespace}</td>
                        <td width="20%">${deployment.images.join(" / ")}</td>
                        <td>${deployment.ready_replicas}</td>
                        <td>${deployment.restart}</td>
                        <td>${deployment.age}</td>
                    </tr>`);
            }
            for (let i = 0; i < numberOfNullRecords; i++) {
                deploymentList.append(nullRecordHtml);
            }

            if (prevSelectedDeployment && isExistDeployment(prevSelectedDeployment)) {
                // check prevSelectedDeployment is in update deployment list
                selectDeploymentButton(prevSelectedDeployment);
                return;
            }

            // check first child
            $("#deployment-list tr:first-child input[type=radio]").prop("checked", true);
            prevSelectedDeployment = getSelectedDeployment();
        },
        error: function (error) {
            console.log(error);
        },
    });
}

// clear deployment list
function clearDeploymentList() {
    let deploymentList = $("#deployment-list")
    let numberOfNullRecords = defaultNumberOfListViewRecord;
    let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/></tr>';

    deploymentList.html("");
    for (let i = 0; i < numberOfNullRecords; i++) {
        deploymentList.append(nullRecordHtml);
    }
}

// clear deployment detail view
function clearDeploymentDetail() {
    let selectedDeployment = $('#selected-deployment');

    selectedDeployment.html("");
    selectedDeployment.html(`
        <h2>Deployment:
          <span class="selected-name"></span>
          <span class="label-common label-unavailable">Unavailable</span>
        </h2>
        <div class="selected-info">
          <p>Namespace: <span>None</span></p>
          <p>Image: <span>None</span></p>
          <p>Ready: <span>None</span></p>
          <p>Selector: <span>None</span></p>
        </div>`);
}

// clear pod list in deployment detail view
function clearPodList() {
    let podList = $("#pod-list");
    let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/></tr>';
    let numberOfNullRecord = defaultNumberOfListViewRecord;

    podList.html("");

    // fill null records
    for (let i = 0; i < numberOfNullRecord; i++) {
        podList.append(nullRecordHtml);
    }
}

// clear selected deployment name
function clearSelectedDeploymentName() {
    setModal("#delete-modal-deployment", "");
}

// clear selected pod name
function clearSelectedPodName() {
    setModal("#delete-modal-pod", "");
    $("#migrate-modal-pod #recipient-name").attr("value", "");
}

// get deployment details from gslink-manager server
function getDeploymentDetail(cluster, namespace, deployment_name) {
    $.ajax({
        type: "GET",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/deployments/${deployment_name}`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let selectedDeployment = $("#selected-deployment");
            selectedDeployment.html("");

            if (!hasElement(response.deployments)) {
                clearDeploymentDetail();
                return;
            }

            let deployment = response.deployments[0];

            selectedDeployment.html(`
                <h2>Deployment:
				    <span class="selected-name">${deployment.name}</span>
				    <span class="label-common label-${deployment.state.toLowerCase()}">${deployment.state}</span>
			    </h2>
			    <div class="selected-info">
				    <p>Namespace: <span>${deployment.namespace}</span></p>
				    <p>Image: <span>${deployment.images.join(" / ")}</span></p>
				    <p>Ready: <span>${deployment.ready_replicas}</span></p>
				    <p>Selector: <span>${deployment.selector.join(" ")}</span></p>
			    </div>
                `);
        },
        error: function (error) {
            console.log(error);
        }
    });
}

// get pod list from gslink-manager server
function getPodList(cluster, namespace, deployment_name) {
    $.ajax({
        type: "GET",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/pods?deployment=${deployment_name}`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let podList = $("#pod-list");
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
    });
}

// reload page
function reloadPage() {
    reloadDeploymentList();
}

// reload deployment list
function reloadDeploymentList() {
    let cluster = getSelectedClusterFromCookie();
    let namespace = getSelectedNamespaceFromCookie();

    if (!cluster || !namespace) {
        clearDeploymentList();
        resetDeploymentDetails();
        return;
    }

    // update deployment list
    refreshDeploymentList(cluster, namespace);
}
