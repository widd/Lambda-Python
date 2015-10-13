login = =>
  loginForm = document.getElementById("loginForm")
  fData = new FormData(loginForm)

  request = new XMLHttpRequest()
  request.open('POST', '/api/user/login', true)

  request.onload = =>
    if request.status == 200
      window.location = "/"
    else
      try
        response = JSON.parse(request.responseText)
        if response.errors.length > 0
          errorArea = document.getElementById("errorArea")
          errorArea.innerHTML = ""
          for error in response.errors
            errorArea.innerHTML += "<div class=\"form-error\">#{error}</div>"
      catch ex
        console.error(e)
        alert('Login failed for unknown reason')

      console.error(request.responseText)

  request.send(fData)
  return false
