// Universal Edit Button finder for Chromium
// Justin Forest <justin.forest@gmail.com>
// Public domain.

function findEditor()
{
  var result = document.evaluate('//link[@rel="alternate" and @type="application/x-wiki"]', document, null, 0, null);
  var editor, item;

  while (item = result.iterateNext()) {
    editor = item.href;
    break;
  }

  // Support for Google Code Wiki.
  if (!editor) {
    var re1 = new RegExp("(http://code\.google\.com/p/[^/]+/)wiki/([^?#]+)");
    var re2 = re1.exec(window.location.href);
    if (re2)
      editor = re2[1] + 'w/edit/' + re2[2];
  }

  if (editor)
    chrome.extension.connect().postMessage(editor);
}

if (window == top) {
  findEditor();
  window.addEventListener("focus", findEditor);
}
