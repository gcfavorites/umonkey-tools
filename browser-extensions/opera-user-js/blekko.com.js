// ==UserScript==
// @include https://blekko.com/ws/*
// ==/UserScript==
//
// Displays links to Google and Yandex on search result pages.
//
// code.umonkey.net

(function () {
	function make_link(text, href) {
		var a = document.createElement("a");
		a.appendChild(document.createTextNode(text));
		a.setAttribute("href", href);
		a.setAttribute("target", "_blank");

		var arrow = document.createElement("span");
		arrow.setAttribute("class", "arrow");

		var li = document.createElement("li");
		li.appendChild(arrow);
		li.appendChild(a);

		return li;
	}

	function on_load() {
		var sb = document.getElementById("searchBox");
		var menu = document.getElementById("blekko-menu");
		if (!sb || !menu)
			return;

		var qs = encodeURIComponent(sb.value);

		menu.appendChild(make_link("search with google", "https://encrypted.google.com/search?q=" + qs));
		menu.appendChild(make_link("search with yandex", "https://yandex.ru/yandsearch?text=" + qs));
	}

	window.addEventListener("load", on_load, false)
})();
