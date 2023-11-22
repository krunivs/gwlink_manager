$(document).ready(function () {
  $("#loginForm").on("submit", function (event) {
    event.preventDefault();
    let email = $("#id_email").val();
    let password = $("#id_password").val();
    $.ajax({
      type: "POST",
      url: "/api/app/v1/login",
      data: {
        email: email,
        password: password
      },
      success: function (response) {
        let token = response['access_token'];
        setAccessTokenToCookie(token);
        // Cookies.set("token", token);
        location.reload();
      },
      error: function () {
        alert("Login Failed. Please check if your email and password are correct.");
      }
    })
    return false;
  })
});

function getBearerAccessTokenHeaderFromCookie() {
  return "Bearer " + Cookies.get("token");
}
function setAccessTokenToCookie(token) {
  Cookies.set('token', token);
}
