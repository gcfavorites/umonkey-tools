// ==UserScript==
// @include https://blekko.com/ws/*
// ==/UserScript==
//
// Displays links to Google and Yandex on search result pages.
//
// Since blekko.com uses https, you must enable user.js on secure pages in
// Opera (you'll still get a confirmation every time a script changes):
//
// http://www.opera.com/docs/userjs/using/#securepages

(function () {
	function make_link(text, href) {
		var a = document.createElement("a");
		a.appendChild(document.createTextNode(text));
		a.setAttribute("href", href);

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
