setInfo = =>
  getSessionInfo(
    ((userInfo) ->
      apiKeyArea = document.getElementById("apiKey")
      apiKeyArea.innerHTML = userInfo.api_key
    ),
    (=>
      window.location.href = "/login"
    )
  )

document.addEventListener("DOMContentLoaded",
  (event) ->
    setInfo()
)