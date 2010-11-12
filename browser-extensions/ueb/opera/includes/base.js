window.addEventListener('load', function (event) {
	opera.extension.onmessage = function (event) {
		var url = find_url();
		switch (event.data.name) {
		case 'check':
			event.source.postMessage({ 'name': 'enable', 'url': url });
			break;
		case 'edit':
			window.location.href = url;
			break;
		}
	};
}, false);

function find_url()
{
	var result = document.evaluate('//link[(@rel="alternate" and (@type="application/x-wiki" or @type="application/wiki")) or @rel="edit"]', document, null, 0, null);
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

	return editor;
}
