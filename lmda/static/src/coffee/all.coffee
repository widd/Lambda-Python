userDropdownDown = false
username = null
uploadRestrictions = null

getSessionInfo = (onSuccess, onFail) ->
  request = new XMLHttpRequest()
  request.open('GET', '/api/session', true)

  request.onload = =>
    if request.status == 200
      try
        onSuccess(JSON.parse(request.responseText))
      catch ex  # wasn't json. That shouldn't happen...
        console.error(ex)
        onFail()
    else
      try
        response = JSON.parse(request.responseText)
        if response.errors
          console.log(response.errors)
      catch ex
        console.error(ex)
        console.error("Something went wrong, and the server didn't send json")
        console.error("Response code: " + request.status)
        console.error("Response text:")
        console.error(request.responseText)
      finally
        onFail()

  request.onerror = onFail

  request.send()

setTopbarAuth = =>
  getSessionInfo(
    ((userInfo) ->
      topbarAccountArea = document.getElementById("topbar-account")
      topbarAccountArea.innerHTML = userInfo.username
      username = userInfo.username
      topbarAccountArea.href = "#"
      topbarAccountArea.onclick = toggleUserDropdown
    ),
    (=>
      topbarAccountArea = document.getElementById("topbar-account")
      topbarAccountArea.innerHTML = "Not Signed In"
      topbarAccountArea.href = "/login"
      topbarAccountArea.onclick = null
      username = null

      if userDropdownDown
        toggleUserDropdown()
    )
  )

toggleUserDropdown = =>
  userDropdown = document.getElementById("user-dropdown")
  if not userDropdownDown
    userDropdown.className = "user-dropdown"
    userDropdown.style.right = (document.documentElement.clientWidth - document.getElementById("topbar-account").getBoundingClientRect().right) + "px"
    console.log(document.getElementById("topbar-account").getBoundingClientRect().right)
  else
    userDropdown.className = "user-dropdown hidden"

  userDropdownDown = !userDropdownDown

document.addEventListener("DOMContentLoaded",
  (event) ->
    setTopbarAuth()
)

signOut = () ->
  request = new XMLHttpRequest()
  request.open('DELETE', '/api/session', true)

  request.onload = =>
    if request.status == 200
      setTopbarAuth()
    else
      console.error(request.responseText)

  request.send()

fetchServerConfig = =>
  xmlHttp = new XMLHttpRequest()
  xmlHttp.onreadystatechange = =>
    if xmlHttp.readyState == 4 && xmlHttp.status == 200
        uploadRestrictions = JSON.parse(xmlHttp.responseText)
  xmlHttp.open("GET", "/api/upload/restrictions", true)  # true for asynchronous
  xmlHttp.send(null);

entityMap =
  "&": "&amp;"
  "<": "&lt;"
  ">": "&gt;"
  '"': '&quot;'
  "'": '&#39;'
  "/": '&#x2F;'

escapeHtml = (string) ->
  return String(string).replace(/[&<>"'\/]/g,
    (s) ->
      return entityMap[s])

fetchServerConfig()