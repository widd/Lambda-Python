getUploads = =>
  xmlHttp = new XMLHttpRequest()
  xmlHttp.onreadystatechange = =>
    if xmlHttp.readyState == 4 && xmlHttp.status == 200
        response = JSON.parse(xmlHttp.responseText)
        uploads = document.getElementById('uploads')
        for upload in response.files
          li = document.createElement('li')
          img = document.createElement('img')
          img.src = '/' + upload.name + '.' + upload.extension
          li.appendChild(img)
          uploads.appendChild(li)
  xmlHttp.open("GET", "/api/user/uploads?page=1&n=20", true)  # true for asynchronous
  xmlHttp.send(null);

document.addEventListener("DOMContentLoaded", =>
  getUploads()
)