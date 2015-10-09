code = false
showTopbar = false

toggleCode = =>
  code = !code
  codeLabel = document.getElementById("codeLabel")
  if code
    if codeLabel
      codeLabel.innerHTML = "CODE: YES"
      codeLabel.className = "enabled"
    myCodeMirror = CodeMirror.fromTextArea(document.getElementById('paste-area'), {
      lineNumbers: true,
      theme: 'zenburn'
    })
  else
    if codeLabel
      codeLabel.innerHTML = "CODE: NO"
      codeLabel.className = ""
    codeMirror = document.getElementsByClassName("CodeMirror")[0]
    codeMirror.style.display = "none"
    pasteArea = document.getElementById("paste-area")
    pasteArea.style.display = "inline"
    pasteArea.value = codeMirror.CodeMirror.getValue()

toggleTopbar = =>
  header = document.querySelector("header")
  timeRemaining = document.getElementById("time-remaining")
  if showTopbar
    header.className = "hidden"
    timeRemaining.className = "time-remaining"
  else
    header.className = "regular"
    timeRemaining.className = "hidden"

  showTopbar = !showTopbar

genEncKey = (length=8) ->
  id = ""
  id += Math.random().toString(36).substr(2) while id.length < length
  id.substr 0, length

encrypt = (text, key) ->
  sjcl.encrypt(key, text)

decrypt = (text, key) ->
  sjcl.decrypt(key, text)

submitPaste = =>
  paste_plaintext = document.getElementById("paste-area").value
  encryption_key = genEncKey()
  paste_encrypted = encrypt(paste_plaintext, encryption_key)
  paste_enc_obj = JSON.parse(paste_encrypted)
  paste_enc_obj.is_code = code
  paste_encrypted = JSON.stringify(paste_enc_obj)

  putPaste(paste_encrypted, (url) ->
    window.location = "/#{url}##{encryption_key}"
  )

putPaste = (paste_encrypted, onfinish) ->
  request = new XMLHttpRequest()
  request.open('POST', '/api/paste', true)

  request.onload = =>
    if request.status == 200
      try
        response = JSON.parse(request.responseText)
        if response.errors.length == 0
          onfinish(response.url)
        else
          console.error(response.errors)
          alert('An unexpected error occurred')
      catch ex
        console.error(ex)
        alert('An unexpected error occurred')

  data = new FormData();
  data.append('paste', paste_encrypted);
  data.append('is_code', code);

  request.send(data)

getPaste = (name) ->
  request = new XMLHttpRequest()
  request.open('GET', "/api/paste?name=#{name}", true)

  request.onload = =>
    if request.status == 200
      try
        decryptPasteView(request.response)
      catch ex
        console.error(ex)
        alert('An unexpected error occurred')

  data = new FormData();
  data.append('name', name);

  request.send(data)

decryptPasteView = (encPaste) ->
  key = window.location.hash.substr(1)
  json = JSON.parse(encPaste)

  json_plain = JSON.parse(encPaste)
  delete json_plain.is_code
  json_plain = JSON.stringify(json_plain)

  document.getElementById("paste-area").value = decrypt(json_plain, key)
  if json.is_code
    toggleCode()

document.addEventListener("DOMContentLoaded",
  if window.location.hash.length > 0
    pasteName = window.location.pathname.split('#')[0].split('/')[1]
    getPaste(pasteName)
)