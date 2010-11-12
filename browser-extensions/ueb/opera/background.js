window.addEventListener("load", function(){
	var button = opera.contexts.toolbar.createItem({
		disabled: true,
		title: "Edit this page",
		icon: "icons/UEB18.png",
		onclick: function () {
			var tab = opera.extension.tabs.getFocused();
			if (tab) {
				tab.postMessage({ 'name': 'edit' });
			}
		}
	});

	opera.contexts.toolbar.addItem(button);

	function enableButton() {
		button.disabled = true;
		var tab = opera.extension.tabs.getFocused();
		if (tab) {
			tab.postMessage({ 'name': 'check' });
		}
	}

	opera.extension.onconnect = enableButton;
	opera.extension.tabs.onfocus = enableButton;
	opera.extension.tabs.onblur = enableButton;

	opera.extension.onmessage = function (event) {
		if (event.data.name == 'enable') {
			// opera.postError('URL: ' + event.data.url);
			if (event.data.url)
				button.disabled = false;
			else
				button.disabled = true;
		}
	};
}, false);
