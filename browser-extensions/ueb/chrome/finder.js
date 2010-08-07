// Universal Edit Button finder for Chromium
// Justin Forest <justin.forest@gmail.com>
// Public domain.

function findEditor()
{
  var result = document.evaluate('//link[@rel="alternate" and (@type="application/x-wiki" or @type="application/wiki")]', document, null, 0, null);
  var editor, item;

  while (item = result.iterateNext()) {
    editor = item.href;
    break;
  }

  // Support for Google Code Wiki.
  if (!editor) {
    var m = /^(http:\/\/code\.google\.com\/p\/[^\/]+\/)wiki\/([^?#]+)/.exec(window.location.href||"");
    if (m)
      editor = m[1] + 'w/edit/' + m[2];
  }

  if (editor)
    chrome.extension.connect().postMessage(editor);
}

if (window == top) {
  findEditor();
  window.addEventListener("focus", findEditor);
}
