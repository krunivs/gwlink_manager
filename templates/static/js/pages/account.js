$(document).ready(() => {
  getUserList();
})

// $("#errorModal").on('hidden.bs.modal', () => {
//   document.location.reload();
// })
//
// $("#messageModal").on('hidden.bs.modal', () => {
//   document.location.reload();
// })

$(document).on('click', '#accountCreateModalBtn', function () {
  $("div.error-message").addClass("invisible");
  let inputs = $("#createModal input");
  inputs.removeClass("field-error")
    .each((i, info) => {
      info.value = "";
    })
})

$(document).on('click', '#accountEditModalBtn', function () {
  $("div.error-message").addClass("invisible");
  let selectedUser = $("#user-list input:checked[type=radio]").parent().parent().children();
  let inputs = $("#editModal input");
  inputs.removeClass("field-error");
  updateEditModal(selectedUser);
})

$(document).on('click', '#user-list tr', function () {
  selectRadioBtn($(this));
  let selectedUser = $(this).children();
  updateEditModal(selectedUser);
});

$(document).on('click', '#createModal button.btn.btn-primary.btn-blue', function () {
  $("#createModal input").removeClass("field-error");
  $("#createModal div.error-message").addClass("invisible");
  createUser();
})

$(document).on('click', '#editModal button.btn.btn-primary.btn-purple', function () {
  // $("#editModal").modal('hide');
  editUser();
})

$(document).on('click', '#deleteUserModal button.btn.btn-primary.btn-red', function () {
  $("#deleteUserModal").modal('hide');
  let username = $("#user-list input:checked[type=radio]").parent().next().html();
  deleteUser(username);
})

function updateEditModal(selectedUser) {
  $("div[name='edit-modal-body'] input").each((i, input) => {
    input.value = selectedUser[i + 1].innerText;
  })
}

function getUserList() {
  $.ajax({
    url: "/api/app/v1/users",
    type: "GET",
    headers: {
      Authorization: getBearerAccessTokenHeaderFromCookie(),
    },
    success: function (response) {
      $("#user-list").empty();
      $.each(response.users, function (i, user) {
        $("#user-list").append(`
          <tr>
            <td><input type="radio" class="form-check-input" value="` + user.username + `"></td>
            <td>` + user.username + `</td>
            <td>` + user.email + `</td>
            <td>` + user.name + `</td>
            <td>` + user.tel + `</td>
            <td>` + user.department + `</td>
            <td>` + user.organization + `</td>
          </tr>
        `)
        if (i === 0) {
          $("#edit-username").val(user.username);
          $("#edit-name").val(user.name);
          $("#edit-email").val(user.email);
          $("#edit-tel").val(user.tel);
          $("#edit-department").val(user.department);
          $("#edit-organization").val(user.organization);
        }
      })
      $("tbody tr:first-child input[type=radio]").prop('checked', true);
    },
    error: function (error) {
      showErrorModal(error);
    }
  });
}

function createUser() {
  let formData = {
    username: $("#createModal #username").val(),
    name: $("#createModal #name").val(),
    email: $("#createModal #email").val(),
    tel: $("#createModal #tel").val(),
    department: $("#createModal #department").val(),
    organization: $("#createModal #organization").val(),
    password: $("#createModal #password").val(),
    password2: $("#createModal #password2").val()
  }
  $.ajax({
    url: `/api/app/v1/users`,
    type: "POST",
    headers: {
      Authorization: getBearerAccessTokenHeaderFromCookie()
    },
    data: JSON.stringify(formData),
    dataType: 'json',
    accept: 'application/json',
    contentType: 'application/json; charset=utf-8',
    success: function (response) {
      $("#createModal").modal('hide');
      getUserList();
    },
    error: function (error) {
      let errors = error.responseJSON['error'];
      let keys = Object.keys(errors);
      keys.forEach((key, index) => {
        $("input#" + key).addClass("field-error");
        let errorMessageSpan = $("span")
        $("div#" + key + "-error").removeClass("invisible").html(errors[key]);
      })


      // const message = `
      // <p>Create: ${error.statusText} (${error.status})</p>
      // <p class="color-red">${error.responseJSON.error}</p>
      // `
      // showErrorModal(message);
    }
  })
}

function editUser() {
  let formData = {
    username: $("#editModal #edit-username").val(),
    name: $("#editModal #edit-name").val(),
    email: $("#editModal #edit-email").val(),
    tel: $("#editModal #edit-tel").val(),
    department: $("#editModal #edit-department").val(),
    organization: $("#editModal #edit-organization").val(),
  }
  $.ajax({
    url: `/api/app/v1/${formData.username}`,
    type: "PUT",
    headers: {
      Authorization: getBearerAccessTokenHeaderFromCookie()
    },
    data: JSON.stringify(formData),
    dataType: 'json',
    accept: 'application/json',
    contentType: 'application/json; charset=utf-8',
    success: function (response) {
      $("#editModal").modal('hide');
      getUserList();
      document.location.reload();
    },
    error: function (error) {
      let errors = error.responseJSON['error'];
      let keys = Object.keys(errors);
      keys.forEach((key, index) => {
        $("input#edit-" + key).addClass("field-error");
        $("#editModal div#edit-" + key + "-error").removeClass("invisible")
          .html(errors[key]);
      })
      // const message = `
      // <p>Edit: ${error.statusText} (${error.status})</p>
      // <p class="color-red">${error.responseJSON.error}</p>
      // `
      // showErrorModal(message);
    }
  })
}

function deleteUser(username) {
  $.ajax({
    url: `/api/app/v1/users/${username}`,
    type: "DELETE",
    headers: {
      Authorization: getBearerAccessTokenHeaderFromCookie()
    },
    success: function (response) {
      const message = `
      <p>Delete: ${username}</p>
      <p class="color-green">Success!</p>
      `;
      showMessageModal('Delete', message);
    },
    error: function (error) {
      showErrorMessageModal(message);
    }
  })
}