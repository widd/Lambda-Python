configUrl = "/api/upload/restrictions"

page = 1
perPage = 21

numPages = 1

searchText = null

uploadDomain = "/"
noExtensionTypes = []
thumbnailTypes = []

selectedImages = []

fetchServerConfig = =>
  xmlHttp = new XMLHttpRequest()
  xmlHttp.onreadystatechange = =>
    if xmlHttp.readyState == 4 && xmlHttp.status == 200
        response = JSON.parse(xmlHttp.responseText)
        uploadDomain = response.upload_domain
        noExtensionTypes = response.no_extension_types
        thumbnailTypes = response.thumbnail_types
  xmlHttp.open("GET", configUrl, true)  # true for asynchronous
  xmlHttp.send(null)

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
          img.name = upload.name

          img.onload = (e) ->
            width = e.target.clientWidth
            height = e.target.clientHeight
            if height > width
              e.target.className = "tall"
            else
              e.target.className = "wide"

          img.onerror = (e) ->  # If the image failed to load
            if not e.target.erroredBefore
              e.target.erroredBefore = true  # Prevent endless loop of loading the replacement image if the replacement image also fails

              extension = e.target.src.split('.').pop()
              e.target.src = "/generic/by-ext/#{extension}"

          img.myLi = li
          img.oncontextmenu = (e) ->
            toggleSelection(e.target, e.target.myLi)
            return false

          if upload.has_thumb
            setThumb(img, upload.name)
          else
            if upload.extension in thumbnailTypes
              img.src = '/' + upload.name + '.' + upload.extension
            else
              img.src = "/generic/by-ext/#{upload.extension}"

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

toggleSelection = (img, li) ->
  if li.className.length == 0
    li.className = 'selected'
    selectedImages.push(img)
  else
    li.className = ''
    selectedImages.splice(selectedImages.indexOf(img), 1)

  if selectedImages.length == 0
    document.getElementById('selection-management').className = "selection-manage hidden"
  else
    document.getElementById('selection-management').className = "selection-manage"
    document.getElementById('numSelectedLabel').innerHTML = "#{selectedImages.length} items selected"

deleteSelected = =>
  toFinishCount = selectedImages.length

  for img in selectedImages
    deleteImage(img.name, =>
      toFinishCount--
      if toFinishCount == 0
        location.reload() # Refresh the page
    )

deleteImage = (name, callback) ->
  xmlHttp = new XMLHttpRequest()
  xmlHttp.onreadystatechange = callback
  xmlHttp.open("DELETE", "/file/#{name}", true)  # true for asynchronous
  xmlHttp.send(null)

