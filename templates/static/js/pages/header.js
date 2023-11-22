let selectedYMLImportCluster;

$(document).on('click', '.import-yaml-cluster-item', function () {
  selectedYMLImportCluster = $(this).html();
  // getYAMLImportNamespaceList(selectedClusterName);
  // let selectedNamespaceName = $(".import-yaml-namespace-item").first().html();
  $("#selected-import-yaml-cluster-name").html(selectedYMLImportCluster);
  // $("#selected-import-yaml-namespace-name").html(selectedNamespaceName);
});

$(document).on('click', '.import-yaml-namespace-item', function () {
  let selectedNamespaceName = $(this).html();
  $("#selected-import-yaml-namespace-name").html(selectedNamespaceName);
});

$(document).on('click', '#import-yaml', function () {
  let cluster = $("#selected-import-yaml-cluster-name").text();
  let yamlData = $("#readYamlArea").val();
  let body = {
    "manifest": yamlData
  }

  $.ajax({
    url: `/api/app/v1/clusters/${cluster}/manifest/apply`,
    type: "POST",
    headers: {
      Authorization: getBearerAccessTokenHeaderFromCookie()
    },
    dataType: "json",
    data: body,
    success: function (response) {
      const message = `
      <p>Cluster: ${response.name}</p>
      <p>Cluster uuid: ${response.id}</p>
      <p class="color-green">Success!</p>
      `
      showMessageModal("Import YAML", message);
    },
    error: function (error) {
      $('#YamlError').val(JSON.parse(error.responseText).error)
    }
  })
})

function showMessageModal(title, message) {
  $("#messageModal").modal('show');
  $("#messageModalLabel").html(title);
  $("#message-message").html(message);
}

function showErrorModal(error) {
  const message = `<p>${error.statusText} (${error.status})</p>
						<p class="color-red">${error.responseJSON.error}</p>`;
  $("#error-message").empty();
  $("#errorModal").modal('show');
  $("#error-message").html(message);
}

function showErrorMessageModal(message) {
  $("#error-message").empty();
  $("#errorModal").modal('show');
  $("#error-message").html(message);
}