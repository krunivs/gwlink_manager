$(document).ready(() => {
    /**
     * window load event handler
     */

    let cluster = getSelectedClusterFromCookie();
    let namespace = getSelectedNamespaceFromCookie();

    if (cluster && namespace) {
        $("#daemonset-list tr:first-child input[type=radio]").prop('checked', true);
        refreshDaemonsetDetail();
    } else {
        clearDaemonsetList();
        resetDaemonsetDetails();
    }

    initClusterAndNamespaceListUpdater();
    initDaemonSetListUpdater();
});

let daemonSetListUpdateTimer;
let prevSelectedDaemonSet;
let prevSelectedPod;

// initialize daemonset list updater
// update daemonset list (period=3s)
function initDaemonSetListUpdater() {
    daemonSetListUpdateTimer = setInterval(function () {
        let cluster = getSelectedClusterFromCookie();
        let namespace = getSelectedNamespaceFromCookie();

        if (!cluster || !namespace) {
            clearDaemonsetList();
            resetDaemonsetDetails();
        }

        // update daemonSet list
        refreshDaemonsetList(cluster, namespace);
        console.log('daemonset list are updated.');
    }, 5000);
}

// daemonset click event
$(document).on('click', '#daemonset-list tr', function () {
    if ($(this).has('.label-name').length !== 0) {
        selectRadioBtn($(this));

        let daemonset = getSelectedDaemonSet();

        if (isEmpty(daemonset)) {
            resetDaemonsetDetails();
            return;
        }

        selectDaemonsetName(daemonset);
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

// refresh daemonset list
function refreshDaemonsetList(cluster, namespace) {
    getDaemonsetList(cluster, namespace);
    let daemonset = getSelectedDaemonSet();

    if (isEmpty(daemonset)) {
        resetDaemonsetDetails();
        return;
    }
    selectDaemonsetName(daemonset);
}

// refresh daemonset detail
function refreshDaemonsetDetail() {
    let daemonset = getSelectedDaemonSet();

    if (isEmpty(daemonset)) {
        resetDaemonsetDetails();
        return;
    }
    selectDaemonsetName(daemonset);
}

// reset daemonset details
function resetDaemonsetDetails() {
    clearDaemonSetDetails();
    clearSelectedDaemonSetName();
    clearPodList();
    clearSelectedPodName();
}

// clear daemonset list
function clearDaemonsetList() {
    let daemonsetList = $("#daemonset-list");
    let numberOfNullRecords = defaultNumberOfListViewRecord;
    let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/><td/><td/></tr>';

    daemonsetList.html("");
    for (let i = 0; i < numberOfNullRecords; i++) {
        daemonsetList.append(nullRecordHtml);
    }
}

// clear daemonset details
function clearDaemonSetDetails() {
    let selectedDaemonSet = $("#selected-daemonset");

    selectedDaemonSet.html("");
    selectedDaemonSet.html(`
        <h2>DaemonSet:
          <span class="selected-name"></span>
          <span class="label-common label-unavailable">Unavailable</span>
        </h2>
        <div class="selected-info">
          <p>Namespace: <span>None</span></p>
          <p>Image: <span>None</span></p>
          <p>Ready: <span>None</span></p>
        </div>        
    `);
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

// clear selected daemonset name
function clearSelectedDaemonSetName() {
    setModal("#delete-modal-daemonset", "");
}

// clear selected pod name
function clearSelectedPodName() {
    setModal("#delete-modal-pod", "");
    $("#migrate-modal-pod #recipient-name").attr("value", "");
}

function selectDaemonsetName(daemonset) {
    let cluster = $("#selected-cluster-name").text();
    let namespace = getSelectedDaemonSetNamespace();

    prevSelectedDaemonSet = daemonset;

    getDaemonsetDetail(cluster, namespace, daemonset);
    getPodList(cluster, namespace, daemonset);

    let pod = getSelectedPod();

    if (!pod) {
        clearSelectedPodName();
        return;
    }

    prevSelectedPod = pod;

    setModal("#delete-modal-daemonset", daemonset);
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

$(document).on('change', '#migrate-cluster-list', function () {
    let cluster = $("#migrate-cluster-list option:selected").html();
    getNodeList(cluster);
});

function getDaemonsetList(cluster, namespace) {
    $.ajax({
        type: "GET",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/daemonsets`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie(),
        },
        success: function (response) {
            let daemonsetList = $("#daemonset-list");
            let numberOfNullRecords = defaultNumberOfListViewRecord;
            let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/><td/><td/></tr>';

            daemonsetList.html("");
            numberOfNullRecords -= response.daemonsets.length;

            for (let i = 0; i < response.daemonsets.length; i++) {
                let daemonset = response.daemonsets[i];
                daemonsetList.append(`
					<tr>
            			<td><input type="radio" class="form-check-input"></td>
            			<td><span class="label-common label-${daemonset.state.toLowerCase()}">${daemonset.state}</span></td>
            			<td class="text-left"><a href="#node" class="label-name">${daemonset.name}</a></td>
            			<td>${daemonset.namespace}</td>
            			<td>${daemonset.images.join(" / ")}</td>
            			<td>${daemonset.desired}</td>
            			<td>${daemonset.current}</td>
            			<td>${daemonset.ready}</td>
            			<td>${daemonset.age}</td>
          			</tr>`);
			}
            for(let i=0; i < numberOfNullRecords; i++) {
                daemonsetList.append(nullRecordHtml);
            }

            if (prevSelectedDaemonSet && isExistDaemonSet(prevSelectedDaemonSet)) {
                // check prevSelectedDaemonSet is in update daemonset list
                selectDaemonSetButton(prevSelectedDaemonSet);
                return;
            }

            // check first child
            $("#daemonset-list tr:first-child input[type=radio]").prop("checked", true);
            prevSelectedDaemonSet = getSelectedDaemonSet();
		},
		error: function (error) {
			console.log(error);
		},
	});
}

// get daemonset details
function getDaemonsetDetail(cluster, namespace, daemonsetName) {
	$.ajax({
		type: "GET",
		url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/daemonsets/${daemonsetName}`,
		headers: {
			Authorization: "",
		},
		success: function (response) {
		    let selectedDaemonset = $("#selected-daemonset");
			selectedDaemonset.html("");

            if (!hasElement(response.daemonsets)) {
                clearDaemonSetDetails();
                return;
            }

			let daemonset = response.daemonsets[0];

			selectedDaemonset.html(`
				<h2>DaemonSet:
            		<span class="selected-name">${daemonset.name}</span>
            		<span class="label-common label-${daemonset.state.toLowerCase()}">${daemonset.state}</span>
          		</h2>
          		<div class="selected-info">
            		<p>Namespace: <span>${daemonset.namespace}</span></p>
            		<p>Image: <span>${daemonset.images.join(" / ")}</span></p>
            		<p>Ready: <span>${daemonset.ready}</span></p>
          		</div>`);
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function getPodList(cluster, namespace, daemonsetName) {
    $.ajax({
        type: "GET",
        url: `/api/app/v1/clusters/${cluster}/namespaces/${namespace}/pods?daemonset=${daemonsetName}`,
        async: false,
        headers: {
            Authorization: getBearerAccessTokenHeaderFromCookie()
        },
        success: function (response) {
            let podList = $("#pod-list")
            let podLength = response.pods.length;
            let numberOfNullRecord = defaultNumberOfListViewRecord;
            let nullRecordHtml = '<tr><td/><td/><td/><td/><td/><td/><td/></tr>'

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
            for(let i=0; i < numberOfNullRecord; i++) {
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

// get node list
function getNodeList(clusterName) {
    $.ajax({
        url: "api/app/v1/clusters/" + clusterName + "/nodes",
        type: "GET",
        success: function (response) {
            let nodeList = $("#migrate-node-list").html(
                `
                <select class="form-select" id="migrate-node-list" aria-label="Floating label select example">
                <option value="none" selected disabled hidden>Open this select menu</option>
                `
            );
            $.each(response.nodes, (i, node) => {
                nodeList.append(`
                    <option value="` + node.name + `">` + node.name + `</option>`);
            })
        },
        error: function (error) {
            console.log(error);
        }
    });
}

// reload page
function reloadPage() {
    reloadDaemonsetList();
}

// reload daemonset list
function reloadDaemonsetList() {
    let cluster = getSelectedClusterFromCookie();
    let namespace = getSelectedNamespaceFromCookie();

    if (!cluster || !namespace) {
        clearDaemonsetList();
        resetDaemonsetDetails();
        return;
    }

    // update deployment list
    refreshDaemonsetList(cluster, namespace);
}
