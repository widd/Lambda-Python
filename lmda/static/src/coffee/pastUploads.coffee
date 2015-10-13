configUrl = "/api/upload/restrictions"

page = 1
perPage = 21

numPages = 1

searchText = null

uploadDomain = "/"
noExtensionTypes = []

fetchServerConfig = =>
  xmlHttp = new XMLHttpRequest()
  xmlHttp.onreadystatechange = =>
    if xmlHttp.readyState == 4 && xmlHttp.status == 200
        response = JSON.parse(xmlHttp.responseText)
        uploadDomain = response.upload_domain
        noExtensionTypes = response.no_extension_types
  xmlHttp.open("GET", configUrl, true)  # true for asynchronous
  xmlHttp.send(null);

getUploads = =>
  specified_page = window.location.hash.substr(1)
  if specified_page.length > 0
    page = specified_page

  uploads = document.getElementById('uploads')
  uploads.innerHTML = ""

  xmlHttp = new XMLHttpRequest()
  xmlHttp.onreadystatechange = =>
    if xmlHttp.readyState == 4 && xmlHttp.status == 200
        response = JSON.parse(xmlHttp.responseText)

        numPages = response.number_pages
        pageNum = document.getElementById("pageNum")
        pageNum.innerHTML = "Page #{page} of #{numPages}"

        goBackBtn = document.getElementById("goBack")
        if page > 1
          goBackBtn.className = "navButton"
        else
          goBackBtn.className = "navButton hidden"

        goFwdBtn = document.getElementById("goNext")
        if page < numPages
          goFwdBtn.className = "navButton"
        else
          goFwdBtn.className = "navButton hidden"

        for upload in response.files
          li = document.createElement('li')
          li.title = upload.local_name
          a = document.createElement('a')
          a.href = uploadDomain + upload.name
          if upload.extension not in noExtensionTypes
            a.href += '.' + upload.extension
          img = document.createElement('img')

          img.onerror = (e) ->  # If the image failed to load
            if not e.target.erroredBefore
              e.target.erroredBefore = true  # Prevent endless loop of loading the replacement image if the replacement image also fails

              extension = e.target.src.split('.').pop()
              e.target.src = "/generic/by-ext/#{extension}"

          if upload.has_thumb
            setThumb(img, upload.name)
          else
            img.src = '/' + upload.name + '.' + upload.extension

          img.alt = upload.local_name
          a.appendChild(img)
          li.appendChild(a)
          uploads.appendChild(li)
    else if xmlHttp.readyState == 4  # an error occurred
      response = JSON.parse(xmlHttp.responseText)
      for error in response.errors
        if error == "Not signed in"
          window.location.href = "/login"

  reqUrl = "/api/user/uploads?page=#{page}&n=#{perPage}"
  if searchText != null
    reqUrl += "&nameContains=" + encodeURIComponent(searchText)
  xmlHttp.open("GET", reqUrl, true)  # true for asynchronous
  xmlHttp.send(null);

document.addEventListener("DOMContentLoaded", =>
  fetchServerConfig()

  getUploads()

  window.addEventListener('hashchange', =>
    getUploads()
  )
)

setThumb = (img, name) ->
  thumbReq = new XMLHttpRequest()
  thumbReq.onreadystatechange = =>
    if thumbReq.readyState == 4 && thumbReq.status == 200
      response = JSON.parse(thumbReq.responseText)
      img.src = response.thumbnails[0].url

  thumbReq.open("GET", "/api/file/thumbnails/#{name}", true)
  thumbReq.send(null)

prevPage = =>
  page = parseInt(page) - 1
  window.location.hash = page

nextPage = =>
  page = parseInt(page) + 1
  window.location.hash = page