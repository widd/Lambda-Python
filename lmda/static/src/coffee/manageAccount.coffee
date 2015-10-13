setInfo = =>
  getSessionInfo(
    ((userInfo) ->
      apiKeyArea = document.getElementById("apiKey")
      apiKeyArea.innerHTML = userInfo.api_key
    ),
    (=>
    )
  )

document.addEventListener("DOMContentLoaded",
  (event) ->
    setInfo()
)