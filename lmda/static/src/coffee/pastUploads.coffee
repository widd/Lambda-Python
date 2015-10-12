page = 1
perPage = 21

numPages = 1

searchText = null

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
          a.href = '/' + upload.name  # TODO use link url config
                                      # TODO use extension-keeping config
          img = document.createElement('img')
          img.src = '/' + upload.name + '.' + upload.extension
          img.alt = upload.local_name
          a.appendChild(img)
          li.appendChild(a)
          uploads.appendChild(li)

  reqUrl = "/api/user/uploads?page=#{page}&n=#{perPage}"
  if searchText != null
    reqUrl += "&nameContains=" + encodeURIComponent(searchText)
  xmlHttp.open("GET", reqUrl, true)  # true for asynchronous
  xmlHttp.send(null);

document.addEventListener("DOMContentLoaded", =>
  getUploads()

  window.addEventListener('hashchange', =>
    getUploads()
  )
)

prevPage = =>
  page = parseInt(page) - 1
  window.location.hash = page

nextPage = =>
  page = parseInt(page) + 1
  window.location.hash = page