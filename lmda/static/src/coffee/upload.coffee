uploadUrl = "/api/upload"
allowedTypes = ["image/png"]
sizeLimit = 20  # MB
apikey = ""


checkAndUpload = (file) ->
  if not isTypeAllowed(file)
    alert('Filetype "' + file.type + '" is not supported')
    return
  if file.size > sizeLimit*1000000
    alert('File is too large. Max size is ' + sizeLimit + ' MB.')
    return
  # Nothing failed, continue to upload
  upload(file, onUploadFinish)


upload = (file, onFinish) ->
  xhr = new XMLHttpRequest()
  fd = new FormData()
  xhr.open('PUT', uploadUrl, true)
  fd.append('apikey', apikey)
  fd.append('file', file)
  createStatusIndicator(xhr, file)
  xhr.onreadystatechange = => # on upload finish
    if xhr.readyState == 4 && xhr.status == 200
      response = JSON.parse(xhr.responseText)
      response.file = file
      onFinish(response)
  xhr.send(fd)

createStatusIndicator = (xhr, file) ->
  ongoingSection = document.getElementById("ongoing-uploads")

  uploadEl = document.createElement("li")

  if isImage(file)
    image = document.createElement("img")
    image.src = URL.createObjectURL(file)
    uploadEl.appendChild(image)

  uploadContent = document.createElement("div")

  title = document.createElement("span")
  title.innerHTML = file.name

  progress = document.createElement("progress")
  progress.value = 0

  uploadContent.appendChild(title)
  uploadContent.appendChild(progress)
  uploadEl.appendChild(uploadContent)

  ongoingSection.appendChild(uploadEl)

  xhr.upload.addEventListener('progress', (e) ->
    percent = e.loaded / e.total
    progress.value = percent

    if percent >= 1.0
      ongoingSection.removeChild(uploadEl)
  )


onUploadFinish = (response) ->
  url = response.url

  finishedSection = document.getElementById("finished-uploads")

  uploadEl = document.createElement("li")

  uploadEl.onclick = =>
    window.location = url


  if isImage(response.file)
    image = document.createElement("img")
    image.src = URL.createObjectURL(response.file)
    uploadEl.appendChild(image)

  contentArea = document.createElement("div")

  uploadLink = document.createElement("a")
  uploadLink.href = url

  uploadLink.innerHTML = response.file.name

  contentArea.appendChild(uploadLink)

  uploadEl.appendChild(contentArea)

  finishedSection.appendChild(uploadEl)


document.addEventListener("DOMContentLoaded", =>
  # On file hover
  document.body.addEventListener('dragover', (e) ->
    e.stopPropagation();
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  )

  # On file drop
  document.body.addEventListener('drop', (e) ->
    e.stopPropagation()
    e.preventDefault()  # stop the browser from redirecting
    files = e.dataTransfer.files
    for file in files
      checkAndUpload(file)
  )
)


isImage = (file) ->
  return file.type.lastIndexOf('image/', 0) == 0  # beginsWith('image/')


isTypeAllowed = (file) ->
  return file.type in allowedTypes